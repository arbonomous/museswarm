import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from helper_protocol import InertController, Refused, compile_deny_policy, seal, canonical


class HelperProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.key = b'synthetic-inert-test-key-not-a-real-secret'
        self.now, self.seq = 1000, 0
        self.c = InertController(self.tmp.name, self.key, clock=lambda: self.now)
        self.rules = [{'binary_sha256': 'a' * 64, 'decision': 'deny'}]

    def wire(self, op, body, **changes):
        self.seq += 1
        fields = dict(epoch=self.c.epoch, seq=self.seq, expires=self.now+30,
                      operation=op, body=body)
        fields.update(changes)
        return seal(self.key, **fields)

    def stage(self):
        r = self.c.receive(self.wire('stage', {'rules': self.rules}))
        return {k:r[k] for k in ('id', 'digest')}

    def test_compiler_exact_sorted_deny_only(self):
        rules = self.rules + [{'binary_sha256': 'b'*64, 'decision': 'deny'}]
        self.assertEqual(compile_deny_policy(rules), compile_deny_policy(rules[::-1]))
        for bad in ([], self.rules*2, [{'binary_sha256':'A'*64,'decision':'deny'}],
                    [{'binary_sha256':'a'*64,'decision':'allow'}],
                    [{'path':'/fake', 'decision':'deny'}], self.rules*65):
            with self.assertRaises(Refused): compile_deny_policy(bad)

    def test_full_simulated_lifecycle_never_claims_os_enforcement(self):
        identity = self.stage()
        for op,state in [('begin_simulation','simulating'),('ack_simulation','simulated_applied'),
                         ('rollback_simulation','simulated_rolled_back')]:
            result = self.c.receive(self.wire(op, identity))
            self.assertEqual(result['state'], state)
            self.assertIs(result['host_effects'], False)
        self.stage()

    def test_replay_and_concurrent_duplicate_have_one_winner(self):
        wire = self.wire('stage', {'rules':self.rules})
        def attempt(_):
            try: self.c.receive(wire); return 1
            except Refused: return 0
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(attempt, range(8))), 1)

    def test_auth_tamper_wrong_key_and_all_bound_fields(self):
        wire = self.wire('stage', {'rules':self.rules})
        original = json.loads(wire)
        for field,value in [('operation','cancel'),('seq',99),('expires',1050),
                            ('epoch','b'*32),('version',2),('body',{})]:
            env = json.loads(wire); env['message'][field] = value
            with self.assertRaises(Refused): self.c.receive(canonical(env))
        other = InertController.__new__(InertController)
        other.key = b'other-inert-synthetic-key-00000000'
        with self.assertRaises(Refused): other._decode(wire)
        self.assertEqual(self.c.receive(wire)['state'], 'staged')

    def test_expiry_long_ttl_clock_regression_and_bool(self):
        for kw in ({'expires':1000},{'expires':1061},{'seq':True}, {'expires':True}):
            with self.assertRaises(Refused): self.c.receive(self.wire('stage',{'rules':self.rules},**kw))
        self.now = 999
        with self.assertRaises(Refused): self.stage()

    def test_schema_duplicate_keys_size_and_malformed(self):
        for wire in (b'{}', b'null', b'[]', b'\xff', b'{"a":1,"a":2}', b'x'*65537,
                     'not bytes', b'{', b'['*1500):
            with self.assertRaises(Refused): self.c.receive(wire)
        env = json.loads(self.wire('stage',{'rules':self.rules}))
        env['extra'] = 1
        with self.assertRaises(Refused): self.c.receive(canonical(env))

    def test_ack_cannot_skip_intent_or_replace_digest(self):
        identity = self.stage()
        with self.assertRaises(Refused): self.c.receive(self.wire('ack_simulation', identity))
        with self.assertRaises(Refused): self.c.receive(self.wire('begin_simulation', {**identity,'digest':'b'*64}))
        self.c.receive(self.wire('begin_simulation',identity))
        self.now += 31
        with self.assertRaises(Refused): self.c.receive(self.wire('ack_simulation',identity))
        self.c.receive(self.wire('rollback_simulation',identity))

    def test_semantic_refusal_consumes_sequence(self):
        wire = self.wire('not-an-operation', {'id':'a'*32,'digest':'b'*64})
        with self.assertRaisesRegex(Refused,'identity mismatch'): self.c.receive(wire)
        with self.assertRaisesRegex(Refused,'replayed'): self.c.receive(wire)

    def test_restart_invalidates_stage_and_fences_old_instance(self):
        identity = self.stage()
        old = self.c
        self.c = InertController(self.tmp.name, self.key, clock=lambda:self.now)
        self.assertEqual(self.c.inspect()[0]['state'],'invalidated')
        with self.assertRaises(Refused): old.receive(self.wire('cancel',identity,epoch=old.epoch))
        with self.assertRaises(Refused): self.c.receive(self.wire('begin_simulation',identity))
        self.stage()

    def test_restart_after_intent_is_unknown_not_success_and_requires_rollback(self):
        identity = self.stage()
        self.c.receive(self.wire('begin_simulation', identity))
        self.c = InertController(self.tmp.name, self.key, clock=lambda:self.now)
        self.assertEqual(self.c.inspect()[0]['state'],'unknown')
        with self.assertRaises(Refused): self.stage()
        with self.assertRaises(Refused): self.c.receive(self.wire('ack_simulation',identity))
        self.c.receive(self.wire('rollback_simulation',identity))
        self.stage()

    def test_restart_after_simulated_apply_also_requires_resolution(self):
        identity = self.stage()
        self.c.receive(self.wire('begin_simulation', identity))
        self.c.receive(self.wire('ack_simulation', identity))
        self.c = InertController(self.tmp.name, self.key, clock=lambda:self.now)
        self.assertEqual(self.c.inspect()[0]['state'], 'unknown')
        with self.assertRaises(Refused): self.stage()
        self.c.receive(self.wire('rollback_simulation', identity))

    def test_active_policy_not_silently_replaced_or_double_acked(self):
        identity = self.stage()
        with self.assertRaises(Refused): self.stage()
        self.c.receive(self.wire('begin_simulation',identity))
        self.c.receive(self.wire('ack_simulation',identity))
        with self.assertRaises(Refused): self.c.receive(self.wire('ack_simulation',identity))
        with self.assertRaises(Refused): self.c.receive(self.wire('cancel',identity))

    def test_failed_persistence_does_not_transition(self):
        identity = self.stage()
        with patch.object(self.c, '_db', side_effect=OSError('inert disk failure')):
            with self.assertRaises(OSError): self.c.receive(self.wire('begin_simulation',identity))
        self.assertEqual(self.c.inspect()[0]['state'], 'staged')

    def test_expired_stage_can_cancel_but_not_begin(self):
        identity = self.stage(); self.now += 31
        with self.assertRaises(Refused): self.c.receive(self.wire('begin_simulation',identity))
        self.c.receive(self.wire('cancel',identity)); self.stage()

    def test_private_directory_and_symlink_preconditions(self):
        with self.assertRaises(ValueError): InertController(self.tmp.name,b'short')
        public=Path(self.tmp.name)/'public';public.mkdir(mode=0o755)
        with self.assertRaises(Refused): InertController(public,self.key)
        link=Path(self.tmp.name)/'link';link.symlink_to(self.c.path)
        other=Path(self.tmp.name)/'other';other.mkdir(mode=0o700)
        (other/'inert-controller.sqlite3').symlink_to(link)
        with self.assertRaises(Refused): InertController(other,self.key)


if __name__ == '__main__': unittest.main()
