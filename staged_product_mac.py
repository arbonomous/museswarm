"""Separate staged Mac panel. No provider/worker work before explicit Start.

Launch only for coordinated current-credit qualification. Does not enable the
legacy native task/demo buttons or install any host enforcement.
"""
from pathlib import Path
import threading,json,sys

def main():
    if sys.platform!='darwin':raise SystemExit('This panel needs macOS. Nothing started.')
    import objc
    from AppKit import (NSApplication,NSWindow,NSWindowStyleMaskTitled,NSWindowStyleMaskClosable,NSBackingStoreBuffered,NSMakeRect,NSButton,NSScrollView,NSTextView,NSTextField,NSApplicationActivationPolicyRegular)
    from Foundation import NSObject
    from staged_product import ProductSession,result_text
    from execution_gate import Coordinator
    app=NSApplication.sharedApplication();app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    class Controller(NSObject):
        def init(self):
            self=objc.super(Controller,self).init()
            self.busy=False;self.session=ProductSession(Coordinator(Path.home()/'Library'/'Application Support'/'SwarmGuard'/'staged-product.sqlite3'))
            self.window=NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(NSMakeRect(0,0,700,640),NSWindowStyleMaskTitled|NSWindowStyleMaskClosable,NSBackingStoreBuffered,False);self.window.setTitle_('MuseSwarm - staged working task');self.window.setReleasedWhenClosed_(False);self.window.setDelegate_(self)
            c=self.window.contentView();self.label=NSTextField.labelWithString_('Review exact public task. Nothing has started.');self.label.setFrame_(NSMakeRect(18,596,664,26));c.addSubview_(self.label)
            scroll=NSScrollView.alloc().initWithFrame_(NSMakeRect(18,94,664,490));scroll.setHasVerticalScroller_(True)
            self.text=NSTextView.alloc().initWithFrame_(NSMakeRect(0,0,644,490));self.text.setEditable_(False);self.text.setSelectable_(True);self.text.setVerticallyResizable_(True);self.text.setHorizontallyResizable_(False);self.text.textContainer().setWidthTracksTextView_(True);scroll.setDocumentView_(self.text);c.addSubview_(scroll)
            self.start=NSButton.alloc().initWithFrame_(NSMakeRect(18,48,430,32));self.start.setTitle_('Start once - current promo credit verified');self.start.setTarget_(self);self.start.setAction_('startClicked:');c.addSubview_(self.start)
            close=NSButton.alloc().initWithFrame_(NSMakeRect(470,48,212,32));close.setTitle_('Close - no new task');close.setTarget_(self);close.setAction_('closeClicked:');c.addSubview_(close)
            foot=NSTextField.labelWithString_('Fixed public task only. No host-wide protection. No automatic retries.');foot.setFrame_(NSMakeRect(18,12,664,26));c.addSubview_(foot)
            self.text.setString_(self.session.review());self.window.center();self.window.makeKeyAndOrderFront_(None);app.activateIgnoringOtherApps_(True);return self
        def startClicked_(self,sender):
            if self.busy:return
            self.busy=True;self.start.setEnabled_(False);self.label.setStringValue_('Running reviewed task. Keep this panel open for cleanup.');self.text.setString_('Useful task running through two defenders. A result is not verified until cleanup finishes.')
            def work():
                try:
                    def factory():
                        import os
                        from dotenv import load_dotenv
                        from openai import OpenAI
                        from meta_agent import BASE_URL
                        load_dotenv(Path(__file__).resolve().parent/'.env',override=False)
                        key=os.environ.get('MODEL_API_KEY') or os.environ.get('META_API_KEY')
                        if not key:raise PermissionError('Existing host-local model key missing')
                        return OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=10)
                    result=self.session.start(explicit_start=True,client_factory=factory,on_progress=lambda t:self.performSelectorOnMainThread_withObject_waitUntilDone_('progress:',t,False))
                    message=result_text(result)
                    # Only fixed-public fixture results are saved, never credentials.
                    folder=Path.home()/'Library'/'Application Support'/'SwarmGuard';folder.mkdir(parents=True,exist_ok=True)
                    import datetime
                    out=folder/('staged-result-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
                    with out.open('x') as f:json.dump(result,f,indent=2)
                    out.chmod(0o600);message+='\n\nEvidence saved locally: '+str(out)
                except Exception as e:message='Run stopped ('+type(e).__name__+'). Do not repeat. Credits may have been used; cleanup needs checking. No output released.'
                self.performSelectorOnMainThread_withObject_waitUntilDone_('finished:',message,False)
            threading.Thread(target=work,daemon=True).start()
        def progress_(self,text):
            self.label.setStringValue_(str(text))
            self.text.setString_(str(self.text.string())+'\n'+str(text))
        def finished_(self,text):self.text.setString_(str(text));self.label.setStringValue_('Result ready. Review the output and blocked counterpart.');self.busy=False
        def closeClicked_(self,sender):
            if self.busy:self.label.setStringValue_('Wait for owned-worker cleanup before closing.');return
            self.session.cancel();app.terminate_(None)
        def windowShouldClose_(self,sender):
            if self.busy:self.label.setStringValue_('Wait for owned-worker cleanup before closing.');return False
            self.session.cancel();app.terminate_(None);return True
    controller=Controller.alloc().init();app.run()
if __name__=='__main__':main()
