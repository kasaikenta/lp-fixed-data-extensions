"""Download the fixed release assets, check SHA-256, and safely unpack."""
from pathlib import Path
import hashlib,json,tarfile,urllib.request,tempfile
R=Path(__file__).resolve().parents[1]
BASE='https://github.com/kasaikenta/lp-fixed-data-extensions/releases/download/v1.2.0/'
for a in json.loads((R/'data/receipt_archives.json').read_text()):
 with tempfile.TemporaryDirectory() as td:
  dest=Path(td)/a['asset'];urllib.request.urlretrieve(BASE+a['asset'],dest)
  assert dest.stat().st_size==a['bytes']
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==a['sha256']
  with tarfile.open(dest,'r:gz') as tf:
   for m in tf.getmembers():
    target=(R/m.name).resolve()
    assert target.is_relative_to(R) and not m.issym() and not m.islnk()
   tf.extractall(R,filter='data')
 print('Verified and extracted',a['asset'],flush=True)
