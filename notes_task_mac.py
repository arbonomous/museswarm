"""Native own-notes review, separate Start, and explicit Save Copy."""
from pathlib import Path
import threading,sys

_CONTROLLER=None

def is_busy():return bool(_CONTROLLER is not None and _CONTROLLER.busy)

def open_panel():
    global _CONTROLLER
    if _CONTROLLER is not None:
        _CONTROLLER.window.makeKeyAndOrderFront_(None)
        from AppKit import NSApplication
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        return _CONTROLLER
    if sys.platform!='darwin':raise SystemExit('Mac required. Nothing started.')
    import objc
    from AppKit import NSApplication,NSWindow,NSWindowStyleMaskTitled,NSWindowStyleMaskClosable,NSBackingStoreBuffered,NSMakeRect,NSButton,NSScrollView,NSTextView,NSTextField,NSApplicationActivationPolicyRegular,NSSavePanel,NSModalResponseOK
    from Foundation import NSObject
    from notes_task import NotesSession,result_text,details_text
    from execution_gate import Coordinator
    app=NSApplication.sharedApplication()
    class Controller(NSObject):
        def init(self):
            self=objc.super(Controller,self).init();self.busy=False
            self.session=NotesSession(Coordinator(Path.home()/'Library'/'Application Support'/'SwarmGuard'/'notes-task.sqlite3'))
            self.window=NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(0,0,760,760),NSWindowStyleMaskTitled|NSWindowStyleMaskClosable,NSBackingStoreBuffered,False);self.window.setTitle_('MuseSwarm - guarded notes to draft');self.window.setReleasedWhenClosed_(False);self.window.setDelegate_(self);c=self.window.contentView()
            def label(text,frame):
                l=NSTextField.labelWithString_(text);l.setFrame_(NSMakeRect(*frame));c.addSubview_(l);return l
            label('Paste your own public/non-sensitive notes (max1KiB). No files or other apps are watched.',(18,716,724,26))
            self.notes=NSTextView.alloc().initWithFrame_(NSMakeRect(0,0,700,134));self.notes.setRichText_(False)
            ns=NSScrollView.alloc().initWithFrame_(NSMakeRect(18,572,724,136));ns.setHasVerticalScroller_(True);ns.setDocumentView_(self.notes);c.addSubview_(ns)
            label('What draft do you want? (max512bytes)',(18,540,724,24))
            self.goal=NSTextField.alloc().initWithFrame_(NSMakeRect(18,506,724,30));self.goal.setPlaceholderString_('Example: Turn my notes into a short launch checklist.');c.addSubview_(self.goal)
            def button(title,x,width,selector):
                b=NSButton.alloc().initWithFrame_(NSMakeRect(x,458,width,32));b.setTitle_(title);b.setTarget_(self);b.setAction_(selector);c.addSubview_(b);return b
            self.review=button('Review exact task',18,205,'reviewClicked:');self.start=button('Start once - approve Meta use',231,300,'startClicked:');self.start.setEnabled_(False)
            self.save=button('Save Copy',539,120,'saveClicked:');self.save.setEnabled_(False)
            self.details=button('Details',665,77,'detailsClicked:');self.details.setEnabled_(False)
            self.status=label('Nothing started. Enter notes and goal, then Review.',(18,416,724,30))
            scroll=NSScrollView.alloc().initWithFrame_(NSMakeRect(18,56,724,354));scroll.setHasVerticalScroller_(True)
            self.output=NSTextView.alloc().initWithFrame_(NSMakeRect(0,0,704,354));self.output.setEditable_(False);self.output.setSelectable_(True);self.output.setVerticallyResizable_(True);self.output.setHorizontallyResizable_(False);self.output.textContainer().setWidthTracksTextView_(True);scroll.setDocumentView_(self.output);c.addSubview_(scroll)
            label('Scoped managed task only. Review outputs. No project edits, host-wide protection or automatic retries.',(18,16,724,28))
            self.output.setString_('Start with your notes and a goal.\n\nMuseSwarm asks a model to propose one draft, then two defenders check it before release. Nothing changes in your files.\n\nUse public or non-sensitive notes only. Meta receives the exact text shown at Review. Current setup uses your existing Mac, OrbStack and Meta key.\n\nThis app guards only the task you launch here. Other apps and agents are not covered.');self.window.center();self.window.makeKeyAndOrderFront_(None);app.activateIgnoringOtherApps_(True);return self
        def reviewClicked_(self,sender):
            if self.busy:return
            self.save.setEnabled_(False);self.details.setEnabled_(False);self.start.setEnabled_(False)
            try:self.output.setString_(self.session.review(str(self.notes.string()),str(self.goal.stringValue())));self.start.setEnabled_(True);self.status.setStringValue_('Review exact text and billing. Start only with active promo credit.')
            except Exception as e:self.output.setString_('Review refused: '+str(e));self.status.setStringValue_('Nothing started. Check the notes and goal limits.')
        def startClicked_(self,sender):
            if self.busy:return
            notes,goal=str(self.notes.string()),str(self.goal.stringValue())
            # Changed input is rejected before any worker/key/provider access.
            try:
                from notes_task import notes_plan
                if self.session.pending is None or notes_plan(notes,goal).manifest!=self.session.pending.manifest:raise PermissionError('Text changed. Review again before Start.')
            except Exception as e:self.session.invalidate();self.start.setEnabled_(False);self.status.setStringValue_(str(e));return
            self.busy=True;self.start.setEnabled_(False);self.review.setEnabled_(False);self.save.setEnabled_(False);self.notes.setEditable_(False);self.goal.setEditable_(False);self.output.setString_('Checking your task...\n\nThe proposed draft stays withheld until both defenders approve it. The owned worker will stop and be removed before you can save.')
            def work():
                try:
                    def factory():
                        import os
                        from dotenv import load_dotenv
                        from staged_https import StagedHTTPS
                        load_dotenv(Path.home()/'Desktop'/'Workspace'/'swarmguard-zero'/'.env',override=False)
                        return StagedHTTPS(os.environ.get('MODEL_API_KEY') or os.environ.get('META_API_KEY'))
                    r=self.session.start(notes,goal,explicit_start=True,client_factory=factory,on_progress=lambda t:self.performSelectorOnMainThread_withObject_waitUntilDone_('progress:',t,False));message=result_text(r)
                except Exception as e:message='Stopped ('+type(e).__name__+'). Do not repeat. Cleanup and credit use may need checking.'
                self.performSelectorOnMainThread_withObject_waitUntilDone_('finished:',message,False)
            threading.Thread(target=work,daemon=True).start()
        def progress_(self,text):self.status.setStringValue_(str(text))
        def finished_(self,text):
            self.output.setString_(str(text));self.status.setStringValue_('Draft ready' if self.session.result and self.session.result.get('export_permitted') else 'Task finished. Read the result below.');self.busy=False;self.details.setEnabled_(bool(self.session.result))
            # Keep task spent. New review is an explicit new task, never retry.
            self.notes.setEditable_(True);self.goal.setEditable_(True);self.review.setEnabled_(True);self.save.setEnabled_(bool(self.session.result and self.session.result.get('export_permitted')))
        def detailsClicked_(self,sender):
            if self.session.result:self.output.setString_(result_text(self.session.result)+'\n\nDETAILS\n\n'+details_text(self.session.result))
        def saveClicked_(self,sender):
            if self.busy:return
            try:
                name,data=self.session.draft();panel=NSSavePanel.savePanel();panel.setNameFieldStringValue_(name);panel.setCanCreateDirectories_(True)
                if panel.runModal()!=NSModalResponseOK:return
                path=Path(str(panel.URL().path()))
                # Never overwrite existing data silently. User chooses another name.
                with path.open('xb') as f:f.write(data)
                self.status.setStringValue_('Draft copy saved to your selected location.')
            except FileExistsError:self.status.setStringValue_('File exists. Choose a new filename; nothing overwritten.')
            except Exception as e:self.status.setStringValue_('Save refused ('+type(e).__name__+').')
        def windowShouldClose_(self,sender):
            if self.busy:self.status.setStringValue_('Wait for worker cleanup before closing.');return False
            self.session.invalidate();self.start.setEnabled_(False);self.save.setEnabled_(False);return True
    _CONTROLLER=Controller.alloc().init();return _CONTROLLER

def main():
    from AppKit import NSApplication,NSApplicationActivationPolicyRegular
    app=NSApplication.sharedApplication();app.setActivationPolicy_(NSApplicationActivationPolicyRegular);open_panel();app.run()
if __name__=='__main__':main()
