"""UNRELEASED, inert helper/controller protocol prototype.

No socket, OS authentication, Santa calls, processes, provider calls or host effects.
HMAC authenticates a caller holding an injected key, NOT a macOS audit token or
user approval. Never connect this prototype to a privileged service as-is.
"""
import hashlib
import hmac
import json
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

VERSION = 1
MAX_WIRE_BYTES = 65536
MAX_TTL = 60


class Refused(PermissionError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _hex(value, length):
    return (type(value) is str and len(value) == length and
            all(c in '0123456789abcdef' for c in value))


def compile_deny_policy(rules):
    """Narrow schema only. Output is data, not an installed Santa rule set.

    Paths, certificates, allow rules and deletes deliberately have no encoding.
    This blocks no process until a separately qualified OS adapter exists.
    """
    if type(rules) is not list or not 1 <= len(rules) <= 64:
        raise Refused('One to 64 explicit binary deny rules required')
    hashes = []
    for rule in rules:
        if (type(rule) is not dict or set(rule) != {'binary_sha256', 'decision'} or
                rule['decision'] != 'deny' or not _hex(rule['binary_sha256'], 64)):
            raise Refused('Only exact SHA256 binary deny rules are supported')
        hashes.append(rule['binary_sha256'])
    if len(set(hashes)) != len(hashes):
        raise Refused('Duplicate binary rule')
    return {'schema': VERSION, 'rules': [
        {'binary_sha256': sha, 'decision': 'deny'} for sha in sorted(hashes)]}


def seal(key, *, epoch, seq, expires, operation, body):
    """Controller-side wire encoder. A MAC is not user authorization."""
    if type(key) is not bytes or len(key) < 32:
        raise ValueError('Injected session key must contain at least 32 bytes')
    message = dict(version=VERSION, epoch=epoch, seq=seq, expires=expires,
                   operation=operation, body=body)
    tag = hmac.new(key, canonical(message), hashlib.sha256).hexdigest()
    wire = canonical({'message': message, 'mac': tag})
    if len(wire) > MAX_WIRE_BYTES:
        raise Refused('Oversized wire message')
    return wire


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refused('Duplicate JSON key')
        result[key] = value
    return result


class InertController:
    """Durable, fenced state machine exercised only by explicit simulation.

    Caller must supply a private disposable directory and a fresh injected key.
    Persistence provides replay/crash tests, NOT protection against same-user
    writes or a compromised root account. There is no production adapter.
    """
    def __init__(self, directory, key, *, clock=time.time):
        if type(key) is not bytes or len(key) < 32:
            raise ValueError('Injected session key must contain at least 32 bytes')
        directory = Path(directory)
        if not directory.is_dir() or directory.is_symlink():
            raise Refused('Existing private disposable directory required')
        if directory.stat().st_mode & 0o077:
            raise Refused('Disposable directory must be owner-only')
        self.path = directory / 'inert-controller.sqlite3'
        if self.path.is_symlink():
            raise Refused('Symlink database refused')
        # This is not a privileged-file opening boundary. The enclosing private
        # test directory is a prerequisite, not a substitute for secure OS IPC.
        self.key, self.clock = key, clock
        self.lock = threading.RLock()
        self.epoch = secrets.token_hex(16)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS session (singleton INTEGER PRIMARY KEY CHECK(singleton=1), epoch TEXT NOT NULL, seq INTEGER NOT NULL, last_time INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS policy (id TEXT PRIMARY KEY, digest TEXT NOT NULL, state TEXT NOT NULL, expires INTEGER NOT NULL)')
            db.execute("UPDATE policy SET state=CASE WHEN state IN ('simulating','simulated_applied') THEN 'unknown' ELSE 'invalidated' END WHERE state IN ('staged','simulating','simulated_applied')")
            db.execute('INSERT OR REPLACE INTO session VALUES(1,?,?,?)',
                       (self.epoch, 0, int(clock())))
        self.path.chmod(0o600)

    @contextmanager
    def _db(self):
        with self.lock:
            db = sqlite3.connect(self.path, timeout=5)
            try:
                db.execute('PRAGMA synchronous=FULL')
                db.execute('BEGIN IMMEDIATE')
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                db.close()

    def _decode(self, wire):
        if type(wire) is not bytes or len(wire) > MAX_WIRE_BYTES:
            raise Refused('Bounded bytes required')
        try:
            envelope = json.loads(wire, object_pairs_hook=_unique)
            if type(envelope) is not dict or set(envelope) != {'message', 'mac'}:
                raise Refused('Invalid envelope')
            m, tag = envelope['message'], envelope['mac']
            if (type(m) is not dict or set(m) !=
                    {'version', 'epoch', 'seq', 'expires', 'operation', 'body'} or
                    type(m['version']) is not int or m['version'] != VERSION or
                    not _hex(m['epoch'], 32) or type(m['seq']) is not int or
                    not 1 <= m['seq'] <= 2**53 or type(m['expires']) is not int or
                    type(m['operation']) is not str or type(m['body']) is not dict or
                    not _hex(tag, 64)):
                raise Refused('Invalid message schema')
            expected = hmac.new(self.key, canonical(m), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(tag, expected):
                raise Refused('Unauthenticated message')
            return m
        except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
            raise Refused('Malformed wire message') from exc

    def receive(self, wire):
        """Consume one authenticated command, recording simulation intent only.

        A valid but semantically refused command also consumes its sequence.
        Crashes at intent leave 'simulating', never an applied claim.
        """
        m = self._decode(wire)
        refusal, result = None, None
        with self._db() as db:
            epoch, seq, last = db.execute('SELECT epoch,seq,last_time FROM session WHERE singleton=1').fetchone()
            now = int(self.clock())
            if (epoch != self.epoch or m['epoch'] != epoch or m['seq'] <= seq or
                    now < last or not now < m['expires'] <= now + MAX_TTL):
                raise Refused('Stale, replayed, expired or unfenced command')
            db.execute('UPDATE session SET seq=?,last_time=? WHERE singleton=1', (m['seq'], now))
            try:
                result = self._transition(db, m, now)
            except Refused as exc:
                refusal = exc
        if refusal:
            raise refusal
        return result

    def _transition(self, db, m, now):
        body, op = m['body'], m['operation']
        if op == 'stage':
            if set(body) != {'rules'}:
                raise Refused('Exact stage schema required')
            policy = compile_deny_policy(body['rules'])
            if db.execute("SELECT 1 FROM policy WHERE state IN ('staged','simulating','simulated_applied','unknown')").fetchone():
                raise Refused('Resolve the existing policy first')
            pid, digest = secrets.token_hex(16), fingerprint(policy)
            db.execute('INSERT INTO policy VALUES(?,?,?,?)', (pid, digest, 'staged', m['expires']))
            return {'id': pid, 'digest': digest, 'state': 'staged', 'host_effects': False}
        if set(body) != {'id', 'digest'} or not _hex(body.get('id'), 32) or not _hex(body.get('digest'), 64):
            raise Refused('Exact policy identity required')
        row = db.execute('SELECT digest,state,expires FROM policy WHERE id=?', (body['id'],)).fetchone()
        if row is None or row[0] != body['digest']:
            raise Refused('Policy identity mismatch')
        _, state, expires = row
        if op == 'begin_simulation' and state == 'staged' and now < expires:
            target = 'simulating'
        elif op == 'ack_simulation' and state == 'simulating' and now < expires:
            target = 'simulated_applied'
        elif op == 'cancel' and state == 'staged':
            target = 'cancelled'
        elif op == 'rollback_simulation' and state in ('simulating', 'simulated_applied', 'unknown'):
            target = 'simulated_rolled_back'
        else:
            raise Refused('Invalid state transition or expired stage')
        db.execute('UPDATE policy SET state=? WHERE id=?', (target, body['id']))
        return {**body, 'state': target, 'host_effects': False}

    def inspect(self):
        with self._db() as db:
            return [dict(zip(('id', 'digest', 'state', 'expires'), row))
                    for row in db.execute('SELECT id,digest,state,expires FROM policy ORDER BY rowid')]
