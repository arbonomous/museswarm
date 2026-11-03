import unittest,tempfile,json,ast
from pathlib import Path
from unittest.mock import Mock,patch
from types import SimpleNamespace as S
from execution_gate import Coordinator
from notes_task import NotesSession,notes_plan,result_text
from managed_guard import Broker
class NotesTests(unittest.TestCase):
    def test_intake_limits_changed_review_and_no_implicit_start(self):
        with tempfile.TemporaryDirectory() as t:
            s=NotesSession(Coordinator(Path(t)/'audit'));factory=Mock();s.review('My public notes','Make a checklist')
            with self.assertRaises(PermissionError):s.start('changed','Make a checklist',explicit_start=True,client_factory=factory)
            factory.assert_not_called()
            with self.assertRaises(PermissionError):s.draft()
        for n,g in [('x'*1025,'goal'),('notes','g'*513),('','goal')]:
            with self.assertRaises(ValueError):notes_plan(n,g)
    def test_useful_output_two_reviews_save_only_after_cleanup(self):
        with tempfile.TemporaryDirectory() as t:
            s=NotesSession(Coordinator(Path(t)/'audit'));c=Mock()
            def respond(**kw):
                if 'tools' in kw:return S(usage=None,choices=[S(finish_reason='tool_calls',message=S(tool_calls=[S(function=S(name='write_artifact',arguments=json.dumps({'path':'draft.md','text':'My useful draft'})))]))])
                p=json.loads(kw['messages'][1]['content']);ctx=p['untrusted_context'];return S(usage=None,choices=[S(finish_reason='stop',message=S(tool_calls=[],content=json.dumps(dict(role=p['reviewer_role'],action_hash=ctx['action_hash'],decision='allow',reason='Matches notes',evidence='public notes'))))])
            c.chat.completions.create.side_effect=respond
            def guard(_self,source,command,**kw):
                b=Broker(source,defense_council=kw['defense_council']);m=kw['model_session'];action=m.request({'id':0,'tool':'model_next','arguments':{}},b);m.request(action,b);m.request({'id':0,'tool':'model_next','arguments':{}},b)
                return dict(stopped=True,removed=True,denied=False,failure=None,events=[],artifacts=b.artifacts)
            s.review('public notes','Draft a note')
            with patch('managed_guard.Guard.run',new=guard):r=s.start('public notes','Draft a note',explicit_start=True,client_factory=lambda:c)
            self.assertTrue(r['export_permitted']);self.assertEqual(s.draft(),('draft.md',b'My useful draft'));self.assertEqual(c.chat.completions.create.call_count,3)
            with self.assertRaises(PermissionError):s.start('public notes','Draft a note',explicit_start=True,client_factory=lambda:c)
    def test_boundary_failure_no_key_and_no_save(self):
        with tempfile.TemporaryDirectory() as t:
            s=NotesSession(Coordinator(Path(t)/'audit'));s.review('public notes','draft');f=Mock()
            with patch('managed_guard.Guard.run',return_value=dict(stopped=True,removed=True,denied=False,failure='refused',events=[],artifacts={})):
                r=s.start('public notes','draft',explicit_start=True,client_factory=f)
            f.assert_not_called();self.assertFalse(r['export_permitted'])
            with self.assertRaises(PermissionError):s.draft()
    def test_ui_selector_arities_and_legacy_gates(self):
        import notes_task_mac,native_task_flow,native_model_task,provider_bridge
        self.assertFalse(native_task_flow.NATIVE_LIVE_RELEASED);self.assertFalse(native_model_task.PAID_EXECUTION_ENABLED);self.assertFalse(provider_bridge.LIVE_PROVIDER_ENABLED)
        tree=ast.parse(Path(notes_task_mac.__file__).read_text());cls=next(n for n in ast.walk(tree) if isinstance(n,ast.ClassDef) and n.name=='Controller')
        for m in cls.body:
            if isinstance(m,ast.FunctionDef):self.assertEqual(m.name.count('_'),len(m.args.args)-1,m.name)
    def test_bundle_no_secrets_or_symlinks_no_overwrite(self):
        from build_mac_app import build
        import plistlib
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);src=root/'src';src.mkdir();(src/'menubar.py').write_text('def main() -> None:\n    pass\n');(src/'.env').write_text('fake-secret');(src/'link.py').symlink_to(src/'.env')
            import shutil
            shutil.copytree(Path('vendor'),src/'vendor')
            home=root/'home';home.mkdir();app=build(src,home,check=False)
            self.assertFalse((app/'Contents/Resources/app/.env').exists());self.assertFalse((app/'Contents/Resources/app/link.py').exists());self.assertFalse(plistlib.loads((app/'Contents/Info.plist').read_bytes())['LSUIElement']);self.assertEqual((app/'Contents/MacOS/MuseSwarm').read_bytes()[:4],bytes.fromhex('cafebabe'))
            with self.assertRaises(FileExistsError):build(src,home,check=False)

    def test_clean_failure_and_cleanup_failure_are_plain_distinct_states(self):
        self.assertIn('CLEANUP NEEDS ATTENTION',result_text(dict(stopped=False,removed=False,export_permitted=False)))
        self.assertIn('TASK STOPPED',result_text(dict(stopped=True,removed=True,export_permitted=False)))
        self.assertIn('TASK BLOCKED',result_text(dict(stopped=True,removed=True,export_permitted=False,denied=True,defense_reviews=[dict(failure_category='grounded_deny')])))
    def test_menu_has_both_routes_and_busy_quit_guard(self):
        text=Path('menubar.py').read_text()
        self.assertIn('callback=self._on_task',text);self.assertIn('"openGuardedTask:"',text)
        self.assertGreaterEqual(text.count('if guarded_task_busy():'),3)
        self.assertIn('applicationShouldHandleReopen_hasVisibleWindows_',text)
