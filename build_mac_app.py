"""Build a user-local launcher around existing Mac Python. Installs no packages.

Does not pin/restart Dock, install system hooks, copy keys or run model calls.
"""
import os,pathlib,plistlib,shutil,sys,uuid

PYTHON='/Library/Frameworks/Python.framework/Versions/3.13/bin/python3'
def build(source,home=None,*,check=True):
    source=pathlib.Path(source).resolve();home=pathlib.Path(home or pathlib.Path.home())
    if check:
        if sys.platform!='darwin':raise PermissionError('Mac required')
        import AppKit,dotenv
        if not pathlib.Path(PYTHON).is_file():raise PermissionError('Existing standalone Python missing')
    apps=home/'Applications';apps.mkdir(exist_ok=True)
    target=apps/'MuseSwarm.app'
    if target.exists():raise FileExistsError('MuseSwarm.app already exists; not overwritten')
    stage=apps/('.MuseSwarm-build-'+uuid.uuid4().hex);contents=stage/'Contents';mac=contents/'MacOS';resources=contents/'Resources';mac.mkdir(parents=True);resources.mkdir()
    try:
        # Carry repo source/assets, never .env, local state or symlinks.
        dest=resources/'app';dest.mkdir()
        for p in source.rglob('*'):
            rel=p.relative_to(source)
            if any(x.startswith('.') or x=='__pycache__' for x in rel.parts) or p.is_symlink():continue
            if p.is_file() and p.suffix in ('.py','.png','.md','.json','.icns'):
                d=dest/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
        icon=source/'assets'/'brand'/'museswarm-app.icns'
        if icon.is_file():shutil.copyfile(icon,resources/'MuseSwarm.icns')
        plist={'CFBundleName':'MuseSwarm','CFBundleDisplayName':'MuseSwarm','CFBundleIdentifier':'com.arbonomous.museswarm','CFBundleVersion':'1','CFBundleShortVersionString':'0.1','CFBundlePackageType':'APPL','CFBundleExecutable':'MuseSwarm','LSUIElement':False,'CFBundleIconFile':'MuseSwarm.icns','NSHighResolutionCapable':True}
        (contents/'Info.plist').write_bytes(plistlib.dumps(plist))
        entry=mac/'MuseSwarm';entry.write_text('''#!/bin/zsh
set -eu
HERE="${0:A:h:h}/Resources/app"
export MUSESWARM_DOCK=1
cd "$HERE"
exec /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 "$HERE/menubar.py"
''');entry.chmod(0o755)
        stage.rename(target);return target
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True);raise

if __name__=='__main__':
    app=build(pathlib.Path(__file__).resolve().parent)
    print('Created '+str(app)+'. No model requests made. Open it from Applications; keep its icon in Dock with Options > Keep in Dock.')
