"""One-time local app setup. No install dependencies, model call or Dock rewrite."""
import hashlib,pathlib,sys,tempfile,urllib.request,zipfile,subprocess
import AppKit,dotenv
root=pathlib.Path(tempfile.mkdtemp(prefix='museswarm-app-source-'))
data=urllib.request.urlopen('https://github.com/arbonomous/museswarm/archive/b25540db383f39dc8e37c1f5a76e6bb88165bdfc.zip',timeout=30).read()
if hashlib.sha256(data).hexdigest()!='688edb1381a4ccf310b4f6ca2f39de6a161bfd7d63654834840b9a2fe2d84368':raise SystemExit('Source verification failed. Nothing installed.')
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
app=build(root,replace_known=True)
print('Created '+str(app)+'. No model request made. Opening the app.')
subprocess.run(['/usr/bin/open',str(app)],check=True)
