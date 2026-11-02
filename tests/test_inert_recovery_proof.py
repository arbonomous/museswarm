import json
from pathlib import Path
import subprocess
import sys
import unittest


class RecoveryProofTests(unittest.TestCase):
    def test_offline_proof_is_bounded_honest_and_leaves_no_repo_state(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root/'safe_range/prove_inert_recovery.py')],
                                cwd=root, capture_output=True, text=True, timeout=10, check=True)
        data = json.loads(result.stdout)
        self.assertFalse(data['host_effects'])
        self.assertTrue(data['replay_refused'])
        self.assertTrue(data['replacement_refused_until_resolution'])
        self.assertEqual(data['restart_state'], 'unknown')
        self.assertEqual(data['final_state'], 'simulated_rolled_back')
        self.assertEqual(data['transitions'], ['staged','simulating','unknown','simulated_rolled_back'])
        self.assertEqual(data['refusals'], 1)
        self.assertIn('not OS recovery', data['scope'])
        self.assertNotIn('key', set(data))


if __name__ == '__main__': unittest.main()
