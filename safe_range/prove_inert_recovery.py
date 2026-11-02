#!/usr/bin/env python3
"""Offline simulation evidence only. No worker, network, OS policy or host effects."""
import json
from pathlib import Path
import secrets
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helper_protocol import InertController, Refused, seal


def main():
    with tempfile.TemporaryDirectory(prefix='museswarm-inert-proof-') as directory:
        key = secrets.token_bytes(32)
        now = 1000
        receiver = InertController(directory, key, clock=lambda: now)
        seq = 0

        def command(operation, body):
            nonlocal seq
            seq += 1
            return seal(key, epoch=receiver.epoch, seq=seq, expires=now+30,
                        operation=operation, body=body)

        staged = receiver.receive(command('stage', {'rules': [
            {'binary_sha256': 'a'*64, 'decision': 'deny'}]}))
        identity = {field: staged[field] for field in ('id', 'digest')}
        wire = command('begin_simulation', identity)
        receiver.receive(wire)
        try:
            receiver.receive(wire)
            raise AssertionError('Replay was accepted')
        except Refused:
            replay_refused = True
        receiver = InertController(directory, key, clock=lambda: now)
        assert receiver.inspect()[0]['state'] == 'unknown'
        seq = 0
        try:
            receiver.receive(command('stage', {'rules': [
                {'binary_sha256': 'b'*64, 'decision': 'deny'}]}))
            raise AssertionError('Unknown intent silently replaced')
        except Refused:
            replacement_refused = True
        receiver.receive(command('rollback_simulation', identity))
        history = receiver.history()
        assert all(row['host_effects'] is False for row in history)
        print(json.dumps({
            'scope': 'Inert simulation only, not OS recovery or protection',
            'replay_refused': replay_refused,
            'restart_state': 'unknown',
            'replacement_refused_until_resolution': replacement_refused,
            'final_state': receiver.inspect()[0]['state'],
            'host_effects': False,
            'transitions': [row['state'] for row in history if row['state'] is not None],
            'refusals': sum(row['outcome'] == 'refused' for row in history),
            'limits': ['Injected key is not OS identity or user approval',
                       'Rollback changes a test database, not installed rules',
                       'Journal has no independent tamper anchor']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
