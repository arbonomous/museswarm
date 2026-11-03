"""One-time local app setup. No install dependencies, model call or Dock rewrite."""
import hashlib,pathlib,sys,tempfile,urllib.request,zipfile,subprocess
import AppKit,dotenv
root=pathlib.Path(tempfile.mkdtemp(prefix='museswarm-app-source-'))
data=urllib.request.urlopen('https://github.com/arbonomous/museswarm/archive/0add06286604d7603e8b288e29a1ce893a8ac156.zip',timeout=30).read()
if hashlib.sha256(data).hexdigest()!='e6abd4dc9cfb3332395d61ce69f9634b09a1c8ffc309325a9e4131d45bae154f':raise SystemExit('Source verification failed. Nothing installed.')
import io
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    for item in archive.infolist():
        parts=pathlib.PurePosixPath(item.filename).parts
        if len(parts)<2 or any(p in ('.','..') or p.startswith('.') for p in parts[1:]):continue
        if ((item.external_attr>>16)&0o170000)==0o120000:continue
        if item.is_dir():continue
        out=root.joinpath(*parts[1:]);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(archive.read(item))
sys.path.insert(0,str(root))
from build_mac_app import build
app=build(root)
print('Created '+str(app)+'. No model request made. Opening the app.')
subprocess.run(['/usr/bin/open',str(app)],check=True)
