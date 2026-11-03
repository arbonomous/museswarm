import unittest,tempfile,json
from pathlib import Path
from types import SimpleNamespace as S
from unittest.mock import Mock,patch
from execution_gate import Coordinator
from staged_product import ProductSession,plan,run_case,result_text
from managed_guard import Broker

class StagedTests(unittest.TestCase):
    def test_complete_useful_and_real_reviewed_veto_protocol(self):
        from staged_https import StagedHTTPS
        with tempfile.TemporaryDirectory() as tmp:
            gate=Coordinator(Path(tmp)/'audit.db');f=ProductSession(gate);made=[];calls=[]
            def factory():
                made.append(1);c=Mock()
                def respond(**kw):
                    calls.append(kw)
                    if 'tools' in kw:return {'choices':[{'finish_reason':'tool_calls','message':{'tool_calls':[{'function':{'name':'write_artifact','arguments':json.dumps({'path':'checklist.md','text':'- Check download link\n- Review release notes\n- Publish status update'})}}]}}]}
                    p=json.loads(kw['messages'][1]['content']);ctx=p['untrusted_context'];deny='collector.invalid' in json.dumps(ctx)
                    return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'role':p['reviewer_role'],'action_hash':ctx['action_hash'],'decision':'deny' if deny else 'allow','reason':'Reject harmful proposal' if deny else 'Matches launch note','evidence':'send your project files' if deny else 'Check download link'})}}]}
                def open_response(req,timeout):
                    wire=respond(**json.loads(req.data));r=Mock();r.__enter__=Mock(return_value=r);r.__exit__=Mock(return_value=False);r.status=200;r.geturl.return_value=req.full_url;r.read.return_value=json.dumps(wire).encode();return r
                c.open.side_effect=open_response;return StagedHTTPS('fake-test-key',opener=c)
            def guard(_self,source,command,**kw):
                broker=Broker(source,defense_council=kw['defense_council']);session=kw['model_session'];denied=False
                if session:
                    action=session.request({'id':0,'tool':'model_next','arguments':{}},broker);self.assertFalse(broker.artifacts)
                else:
                    from validate_cooperation import VETO_ACTION
                    action=VETO_ACTION
                try:
                    if session:session.request(action,broker);session.request({'id':0,'tool':'model_next','arguments':{}},broker)
                    else:broker.request(action)
                except PermissionError:denied=True
                return dict(artifacts=broker.artifacts,denied=denied,stopped=True,removed=True,failure='denied' if denied else None,events=[])
            with patch('managed_guard.Guard.run',new=guard):
                f.review();self.assertFalse(made);result=f.start(explicit_start=True,client_factory=factory)
                self.assertTrue(result['complete']);self.assertEqual(len(calls),4);self.assertIn('Check download link',result_text(result));self.assertIn('blocked before output',result_text(result))
                with self.assertRaises(PermissionError):f.start(explicit_start=True,client_factory=factory)
    def test_failure_result_shows_reason_and_no_counterpart_claim(self):
        text=result_text({'complete':False,'scope':'fixed','cases':[dict(case='useful task',cleanup_verified=True,useful_output=False,blocked_counterpart=False,failure='PermissionError: Managed tool request denied',diagnostics=[dict(role='task',stage='failed',category='transport_error',error_type='BadRequestError',http_status=400)],events=[dict(kind='denied',reason='Incomplete single artifact proposal; no retry')],reviews=[])]})
        self.assertIn('HTTP 400',text)
        self.assertIn('Incomplete single artifact proposal',text)
        self.assertIn('counterpart was not started',text)
    def test_cancel_and_no_start_never_call(self):
        with tempfile.TemporaryDirectory() as t:
            f=ProductSession(Coordinator(Path(t)/'audit.db'));factory=Mock();f.review();f.cancel()
            with self.assertRaises(PermissionError):f.start(explicit_start=True,client_factory=factory)
            f.review()
            with self.assertRaises(PermissionError):f.start(client_factory=factory)
            factory.assert_not_called()
    def test_boundary_failure_before_key_access_stops_pair(self):
        with tempfile.TemporaryDirectory() as t:
            f=ProductSession(Coordinator(Path(t)/'audit.db'));f.review();factory=Mock()
            with patch('managed_guard.Guard.run',return_value=dict(artifacts={},denied=False,stopped=True,removed=True,failure='boundary refused',events=[])) as guard:
                r=f.start(explicit_start=True,client_factory=factory)
            factory.assert_not_called();self.assertFalse(r['complete']);self.assertEqual(guard.call_count,1)
    def test_fixed_manifest_and_wrong_path_rejected(self):
        from provider_bridge import ProviderBridge
        from staged_product import ChecklistSession
        bad=plan().manifest.__class__(**{**plan().manifest.__dict__,'model':'other'})
        with self.assertRaises(PermissionError):ProviderBridge.for_staged_product(None,None,bad,client=Mock())
        bridge=Mock();bridge.request.return_value=S(choices=[S(finish_reason='tool_calls',message=S(tool_calls=[S(function=S(name='write_artifact',arguments='{"path":"wrong.txt","text":"x"}'))]))])
        with self.assertRaises(PermissionError):ChecklistSession(bridge,plan()).request({'id':0,'tool':'model_next','arguments':{}},Broker(dict(plan().source)))
    def test_legacy_gates_stay_closed_and_mac_import_inert(self):
        import native_task_flow,native_model_task,provider_bridge,staged_product_mac
        self.assertFalse(native_task_flow.NATIVE_LIVE_RELEASED);self.assertFalse(native_model_task.PAID_EXECUTION_ENABLED);self.assertFalse(provider_bridge.LIVE_PROVIDER_ENABLED)
        import ast
        tree=ast.parse(Path(staged_product_mac.__file__).read_text());cls=next(n for n in ast.walk(tree) if isinstance(n,ast.ClassDef) and n.name=='Controller')
        for m in cls.body:
            if isinstance(m,ast.FunctionDef):self.assertEqual(m.name.count('_'),len(m.args.args)-1,m.name)
