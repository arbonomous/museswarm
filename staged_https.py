"""Single-request stdlib HTTPS transport for the fixed staged task.

No SDK dependency, proxy routing, redirect following, retry or body diagnostics.
The same ProviderBridge still owns model/tools/context/token reservations.
"""
import json
import ssl
import urllib.request
import urllib.error
from types import SimpleNamespace
from meta_agent import BASE_URL

class Usage(dict):
    def model_dump(self):return dict(self)

def _object(value):
    if isinstance(value,dict):return SimpleNamespace(**{k:_object(v) for k,v in value.items()})
    if isinstance(value,list):return [_object(v) for v in value]
    return value

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise PermissionError('Provider redirect refused; no retry')

class StagedHTTPS:
    def __init__(self,key,*,opener=None):
        if not isinstance(key,str) or not key or '\r' in key or '\n' in key:raise PermissionError('Invalid host-local key')
        if BASE_URL!='https://api.meta.ai/v1':raise PermissionError('Unexpected provider endpoint')
        self._key=key
        self._opener=opener or urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        self.chat=SimpleNamespace(completions=SimpleNamespace(create=self.create))
    def create(self,**kwargs):
        timeout=kwargs.pop('timeout',10)
        if timeout!=10:raise PermissionError('Unexpected provider timeout')
        payload=json.dumps(kwargs,separators=(',',':')).encode('utf-8')
        request=urllib.request.Request(BASE_URL+'/chat/completions',data=payload,headers={'Authorization':'Bearer '+self._key,'Content-Type':'application/json','Accept':'application/json'},method='POST')
        try:
            with self._opener.open(request,timeout=10) as response:
                if response.geturl()!=request.full_url:raise PermissionError('Provider endpoint changed')
                if response.status!=200:raise PermissionError('Unexpected provider status')
                data=response.read(1024*1024+1)
        except urllib.error.HTTPError as exc:
            # Never retain/print response bodies, headers or the key.
            error=RuntimeError('Provider HTTP failure; no retry');error.status_code=exc.code
            exc.close();raise error from None
        if len(data)>1024*1024:raise PermissionError('Provider response limit exceeded')
        result=json.loads(data)
        if not isinstance(result,dict) or not isinstance(result.get('choices'),list):raise PermissionError('Invalid provider response')
        out=_object(result)
        out.usage=Usage(result['usage']) if isinstance(result.get('usage'),dict) else None
        for choice in out.choices:
            if not hasattr(choice,'message'):raise PermissionError('Missing provider message')
            if not hasattr(choice.message,'tool_calls'):choice.message.tool_calls=None
        return out
