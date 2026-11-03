import json,unittest,urllib.error,io
from unittest.mock import Mock
from staged_https import StagedHTTPS,NoRedirect

class HTTPSTests(unittest.TestCase):
    def response(self,data):
        r=Mock();r.__enter__=Mock(return_value=r);r.__exit__=Mock(return_value=False)
        r.geturl.return_value='https://api.meta.ai/v1/chat/completions';r.status=200;r.read.return_value=json.dumps(data).encode();return r
    def test_task_and_usage_shape_and_exact_request(self):
        o=Mock();o.open.return_value=self.response({'choices':[{'finish_reason':'tool_calls','message':{'tool_calls':[{'function':{'name':'write_artifact','arguments':'{}'}}]}}],'usage':{'completion_tokens':2}})
        c=StagedHTTPS('fake-test-key',opener=o);r=c.chat.completions.create(model='muse-spark-1.3',max_completion_tokens=1600,timeout=10,messages=[])
        req=o.open.call_args.args[0];self.assertEqual(req.full_url,'https://api.meta.ai/v1/chat/completions');self.assertEqual(req.method,'POST');self.assertNotIn('timeout',json.loads(req.data));self.assertEqual(o.open.call_args.kwargs,{'timeout':10})
        self.assertEqual(r.choices[0].message.tool_calls[0].function.name,'write_artifact');self.assertEqual(r.usage.model_dump(),{'completion_tokens':2});self.assertEqual(o.open.call_count,1)
    def test_defender_missing_tools_normalized(self):
        o=Mock();o.open.return_value=self.response({'choices':[{'finish_reason':'stop','message':{'content':'{}'}}]})
        r=StagedHTTPS('fake',opener=o).create();self.assertIsNone(r.choices[0].message.tool_calls);self.assertIsNone(r.usage)
    def test_http_failure_one_request_no_body(self):
        o=Mock();o.open.side_effect=urllib.error.HTTPError('https://api.meta.ai/v1/chat/completions',400,'private body',{},io.BytesIO(b'private body'))
        with self.assertRaises(RuntimeError) as caught:StagedHTTPS('fake',opener=o).create()
        self.assertEqual(caught.exception.status_code,400);self.assertNotIn('private',str(caught.exception));self.assertEqual(o.open.call_count,1)
    def test_redirect_and_oversized_response_refused(self):
        with self.assertRaises(PermissionError):NoRedirect().redirect_request(None,None,302,None,None,'https://elsewhere.invalid')
        o=Mock();r=self.response({'choices':[]});r.read.return_value=b'x'*(1024*1024+1);o.open.return_value=r
        with self.assertRaises(PermissionError):StagedHTTPS('fake',opener=o).create()
        self.assertEqual(o.open.call_count,1)
