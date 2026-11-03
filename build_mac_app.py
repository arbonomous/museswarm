"""Build a user-local launcher around existing Mac Python. Installs no packages.

Does not pin/restart Dock, install system hooks, copy keys or run model calls.
"""
import os,pathlib,plistlib,shutil,sys,uuid,hashlib

PYTHON='/Library/Frameworks/Python.framework/Versions/3.13/bin/python3'
def build(source,home=None,*,check=True,replace_known=False):
    source=pathlib.Path(source).resolve();home=pathlib.Path(home or pathlib.Path.home())
    if check:
        if sys.platform!='darwin':raise PermissionError('Mac required')
        import AppKit,dotenv
        if not pathlib.Path(PYTHON).is_file():raise PermissionError('Existing standalone Python missing')
    apps=home/'Applications';apps.mkdir(exist_ok=True)
    target=apps/'MuseSwarm.app'
    if target.exists():
        if not replace_known:raise FileExistsError('MuseSwarm.app already exists; not overwritten')
        info=plistlib.loads((target/'Contents/Info.plist').read_bytes())
        if info.get('CFBundleIdentifier')!='com.arbonomous.museswarm' or info.get('CFBundleVersion')!='1':raise PermissionError('Not the known first launcher; no replacement')
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
        plist.update(CFBundleVersion='2',NSPrincipalClass='NSApplication',PyMainFileNames=['__boot__'],PyRuntimeLocations=['/Library/Frameworks/Python.framework/Versions/3.13/Python'],PyExecutableName='python',PyOptions={'use_pythonpath':False})
        (contents/'Info.plist').write_bytes(plistlib.dumps(plist))
        native=source/'vendor'/'py2app'/'MuseSwarm'
        if not native.is_file():raise PermissionError('Native launcher missing')
        shutil.copyfile(native,mac/'MuseSwarm');(mac/'MuseSwarm').chmod(0o755)
        shutil.copyfile(source/'vendor'/'py2app'/'LICENSE.txt',resources/'py2app-LICENSE.txt')
        (mac/'python').symlink_to(PYTHON)
        (resources/'__boot__.py').write_text("""import os,sys,pathlib
os.environ['MUSESWARM_DOCK']='1'
os.environ['PATH']='/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'
root=pathlib.Path(os.environ['RESOURCEPATH'])/'app'
sys.path.insert(0,str(root))
os.chdir(root)
import menubar
try:
    menubar.main()
except Exception as error:
    from AppKit import NSAlert
    alert=NSAlert.alloc().init()
    alert.setMessageText_('MuseSwarm could not start')
    alert.setInformativeText_(type(error).__name__+': '+str(error)[:240])
    alert.runModal()
    raise
""")
        if target.exists():
            backup=apps/('MuseSwarm-launcher-backup-'+uuid.uuid4().hex[:8]+'.app')
            target.rename(backup)
            try:stage.rename(target)
            except BaseException:backup.rename(target);raise
            return target
        stage.rename(target);return target
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True);raise

if __name__=='__main__':
    app=build(pathlib.Path(__file__).resolve().parent)
    print('Created '+str(app)+'. No model requests made. Open it from Applications; keep its icon in Dock with Options > Keep in Dock.')
