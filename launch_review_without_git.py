import hashlib, pathlib, runpy, subprocess, sys, tempfile, zipfile
old = pathlib.Path('/Users/illfaded2022/Desktop/Workspace/swarmguard-zero')
import AppKit, dotenv
root = pathlib.Path(tempfile.mkdtemp(prefix='museswarm-review-'))
z = root / 'source.zip'
subprocess.run(['/usr/bin/curl', '-fLsS', '--connect-timeout', '15', '--max-time', '90', 'https://github.com/arbonomous/museswarm/archive/c32fbeb8c21f26865ac59e284334b81389681925.zip', '-o', str(z)], check=True)
if hashlib.sha256(z.read_bytes()).hexdigest() != '6b68747dd7a21feb3935f3246f35f6de663793b37482a84ee5ae49f6add6e32f':
    raise SystemExit('Source verification failed. Nothing started.')
with zipfile.ZipFile(z) as archive:
    for item in archive.infolist():
        parts = pathlib.PurePosixPath(item.filename).parts
        if len(parts) == 2 and parts[1].endswith('.py'):
            (root / parts[1]).write_bytes(archive.read(item))
z.unlink()
dotenv.load_dotenv(old / '.env', override=False)
sys.path.insert(0, str(root))
runpy.run_path(str(root / 'staged_product_mac.py'), run_name='__main__')
