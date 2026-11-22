"""Recheck recorded exclusions; never launch or trust an unfinished search."""
from pathlib import Path
import argparse,json,sqlite3,sys,tempfile,hashlib
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'vendor/QEDist'))
from cssdist.code import CSSCode,digest
from cssdist.audit import check_receipt
from nested_audit import audit_stage,header,coverage

def read(p):return json.loads(p.read_text())
def flat(root,cutoff,code):
 campaigns={int(p.name[1:]):header(p,code) for p in (root/'campaigns').glob('w*')}
 exclusions={};attempts=0
 with sqlite3.connect(f'file:{root}/evidence.sqlite?mode=ro',uri=True) as db, tempfile.TemporaryDirectory() as td:
  assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
  scratch=Path(td)
  for w,side,shard,receipt,stdout,stderr in db.execute('SELECT w,side,shard,receipt,stdout,stderr FROM attempts'):
   campaign,problems=campaigns[w]
   for name,data in [('receipt.json',receipt),('stdout.jsonl',stdout),('stderr.txt',stderr)]:
    (scratch/name).write_bytes(data)
   checked=check_receipt(scratch/'receipt.json',scratch,campaign,code,side,shard,problems[side]);attempts+=1
   if checked['status']=='excluded':
    key=(w,side,shard);assert key not in exclusions
    exclusions[key]=(checked['terminal'],digest(receipt))
 tasks={tuple(t[:3]):t[3] for t in read(root/f'tasks_w{cutoff}.json')}
 cover=coverage(tasks,{w:c for w,(c,_) in campaigns.items()},exclusions,{})[cutoff]
 assert all(x['complete'] for x in cover.values())
 if not any(k.startswith('Z-') for k in cover):assert code.exchange is not None
 return dict(complete=True,cutoff=cutoff,coverage=cover,attempts=attempts,
             nodes=sum(t[0]['nodes'] for t in exclusions.values()),code_sha256=code.fingerprint)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--id');args=parser.parse_args()
 records={r['id']:r for r in read(R/'data/selected/records.json')}
 results=[];out=R/'verification_results';out.mkdir(exist_ok=True)
 for a in read(R/'data/receipt_archives.json'):
  if args.id and args.id!=a['id']:continue
  root=R/'receipts'/a['id'];r=records[a['id']]
  for name,want in read(root/'SHA256.json').items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==want,name
  code=CSSCode.load(root/'code.json');assert code.fingerprint==r['code_sha256']==a['code_sha256']
  assert a['cutoff']+1==r['lower']
  result=audit_stage(root,a['cutoff']) if a['mode']=='nested' else flat(root,a['cutoff'],code)
  assert result['complete'] and result['attempts']==a['attempts']
  # Upper bounds in the table use the physical supports stored with that row.
  for sector in ['X','Z']:
   v=sum(1<<i for i in r['supports'][sector])
   assert code.is_logical(v,sector) and v.bit_count()==r['upper'][sector]
   assert r['lower']<=v.bit_count()
  if r['exact_distance'] is not None:assert r['lower']==min(r['upper'].values())==r['exact_distance']
  result.update(id=a['id'],lower=r['lower'],upper=r['upper'],exact_distance=r['exact_distance'])
  (out/f'{a["id"]}.json').write_text(json.dumps(result,indent=2)+'\n')
  results.append(result);print(a['id'],result['attempts'],'attempts: complete',flush=True)
 assert results,'No selected archive'
 (out/'receipt_summary.json').write_text(json.dumps(results,indent=2)+'\n')
