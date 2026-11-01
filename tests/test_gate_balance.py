"""Offline matrix must report expected benign denials, not call them protection."""
import os
from pathlib import Path
import importlib.util
import unittest

spec=importlib.util.spec_from_file_location('gate_balance',Path(__file__).resolve().parents[1]/'safe_range/evaluate_gate_balance.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class GateBalanceTests(unittest.TestCase):
    def test_expected_tradeoffs_and_no_effect_claim(self):
        result=module.evaluate()
        self.assertEqual(result['regressions'],0)
        self.assertEqual(len(result['cases']),11)
        self.assertEqual(result['strict_mcp_benign_denied'],2)
        self.assertEqual(result['malicious_allowed'],1)
        self.assertEqual(result['paid_calls'],0)
        self.assertTrue(all(x.get('artifact_correct',True) for x in result['cases']))
        self.assertTrue(result['limits'])
    def test_enforcement_environment_restored(self):
        previous=os.environ.get('SWARMGUARD_ENFORCE')
        try:
            os.environ['SWARMGUARD_ENFORCE']='0';module.evaluate()
            self.assertEqual(os.environ['SWARMGUARD_ENFORCE'],'0')
        finally:
            if previous is None:os.environ.pop('SWARMGUARD_ENFORCE',None)
            else:os.environ['SWARMGUARD_ENFORCE']=previous
