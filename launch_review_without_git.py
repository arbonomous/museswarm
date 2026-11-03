import hashlib, pathlib, runpy, subprocess, sys, tempfile, zipfile
old = pathlib.Path('/Users/illfaded2022/Desktop/Workspace/swarmguard-zero')
import AppKit, dotenv, openai
root = pathlib.Path(tempfile.mkdtemp(prefix='museswarm-review-'))
z = root / 'source.zip'
subprocess.run(['/usr/bin/curl', '-fLsS', '--connect-timeout', '15', '--max-time', '90', 'https://github.com/arbonomous/museswarm/archive/4faf6e70e5870ccbb9f0f9f61bfb0c09cf083a50.zip', '-o', str(z)], check=True)
if hashlib.sha256(z.read_bytes()).hexdigest() != 'dac5196a41cc183b5b6f1bc590567e11afafb05763dbfa52dea6f6ed4f04842e':
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
