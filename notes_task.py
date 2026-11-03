"""Review-bound notes-to-draft controller. No host tools or automatic exports."""
import json
from pathlib import Path
from types import SimpleNamespace
from native_task_flow import prepare,SingleArtifactSession
from defense_council import DefenseCouncil,ROLES
from managed_guard import Guard
from isolation_check import VERIFIED_IMAGE
from provider_bridge import ProviderBridge

SCOPE='Only this owned task is guarded. Other agents and the rest of your Mac are not protected.'

def notes_plan(notes,goal):
    if not isinstance(notes,str) or not notes.strip():raise ValueError('Paste non-sensitive notes first')
    return prepare({'notes.txt':notes.encode('utf-8')},goal)

def preview(p):
    return ('READY FOR YOUR REVIEW\n\nGoal\n'+p.goal+'\n\nNotes\n'+p.source['notes.txt'].decode()+
            '\n\nMeta receives these notes, goal and proposed draft for the task and both defenders. Use only public or non-sensitive text. Limited secret checks are not a privacy guarantee.'+
            '\n\nOne run: up to3requests and4800completion tokens, including reasoning; input is billed too. No retries. Active promo credit must cover this key. These limits are not a dollar cap; no card-overage authority.'+
            '\n\nBoth defenders must approve before the draft is released. Nothing changes in your project. Save Copy is separate, after cleanup verifies.\n\n'+SCOPE)


class NotesSession:
    def __init__(self,gate):self.gate=gate;self.pending=None;self.used=False;self.result=None
    def invalidate(self):self.gate.cancel();self.pending=None;self.result=None
    def review(self,notes,goal):
        self.invalidate();p=notes_plan(notes,goal);self.pending=p;self.used=False;return preview(p)
    def start(self,notes,goal,*,explicit_start=False,client_factory=None,on_progress=None):
        p=notes_plan(notes,goal)
        if explicit_start is not True or self.used or self.pending is None or p.manifest!=self.pending.manifest:
            self.invalidate();raise PermissionError('Review these exact notes/goal, then use separate Start once')
        if client_factory is None:raise PermissionError('No scoped transport')
        self.used=True;self.pending=None;self.result=None
        ticket=self.gate.review(p.manifest);self.gate.decide_dry(ticket,p.manifest,explicit_start=True)
        def operation(claim):
            transport=None
            def create(**kwargs):
                nonlocal transport
                if transport is None:transport=client_factory()
                return transport.chat.completions.create(**kwargs)
            bridge=ProviderBridge.for_notes_task(self.gate,claim,p,client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
            council=DefenseCouncil(p.goal,{r:bridge.defender(r) for r in ROLES},reserve=lambda role,size:None,timeout=12)
            model=SingleArtifactSession(bridge,p)
            def event(e):
                if on_progress:
                    try:on_progress({'boundary_verified':'Boundary checked.','started':'Owned worker started.','proposal_received':'Reviewing proposed work.','allowed':'Both defenders allowed the output.','denied':'Work blocked; stopping worker.','stopped':'Worker stop verified.','removed':'Worker removal checked.'}.get(e['kind'],'Task and cleanup in progress.'))
                    except Exception:pass
            r=Guard(VERIFIED_IMAGE).run(dict(p.source),list(p.manifest.command),seconds=45,model_session=model,defense_council=council,on_event=event)
            r.update(model_finished=model.finished,defense_reviews=council.events,provider_diagnostics=bridge.diagnostics,all_role_usage=bridge.usage)
            r['export_permitted']=bool(r.get('stopped') is True and r.get('removed') is True and model.finished and not r.get('denied') and not r.get('failure') and len(r.get('artifacts',{}))==1)
            if not r['export_permitted']:r['artifacts']={}
            return r
        self.result=self.gate.dispatch_dry(ticket,p.manifest,operation);return self.result
    def draft(self):
        r=self.result
        if not r or not r.get('export_permitted'):raise PermissionError('No verified draft to save')
        name,data=next(iter(r['artifacts'].items()));return name,bytes(data)

def result_text(r):
    clean=r.get('stopped') is True and r.get('removed') is True
    if r.get('export_permitted'):
        lines=['DRAFT READY','Both defenders approved. Worker stopped and removed.','Read the draft before using it. Save Copy writes only to the location you choose.']
        for n,b in r.get('artifacts',{}).items():lines+=['\n'+n,b.decode()]
    elif not clean:
        lines=['CLEANUP NEEDS ATTENTION','No draft released. Keep the app open and ask for help. Do not run this task again.']
    elif r.get('denied') and any(e.get('failure_category')=='grounded_deny' for e in r.get('defense_reviews',[])):
        lines=['TASK BLOCKED','A defender rejected the proposed work before output. The worker stopped and was removed.','No draft was released. Review the goal and source before choosing a new task.']
    else:
        lines=['TASK STOPPED','No draft released. The worker stopped and was removed. Do not repeat automatically.','Open Details for the technical reason. A failed request may still use credits.']
    return '\n\n'.join(lines)

def details_text(r):
    lines=[SCOPE,'No output is released unless both defenders allow and cleanup verifies.']
    if r.get('failure'):lines+=['Stop reason: '+str(r['failure'])]
    for e in r.get('events',[]):
        if e.get('kind')=='denied':lines+=['Refusal: '+str(e.get('reason','unknown'))]
    for d in r.get('provider_diagnostics',[]):
        if d.get('stage')=='failed':lines+=['Provider: '+str(d.get('category'))+' '+str(d.get('error_type'))+(' HTTP '+str(d['http_status']) if 'http_status' in d else '')]
    return '\n\n'.join(lines)
