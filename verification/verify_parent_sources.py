"""Match the original Mitten code to the pinned public QEDist catalogue."""
from pathlib import Path
import hashlib,json,urllib.request
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def inverse(p):
 assert sorted(p)==list(range(len(p)))
 result=[0]*len(p)
 for i,j in enumerate(p):result[j]=i
 return result
for r in read(R/'data/parent_provenance.json'):
 raw=urllib.request.urlopen(r['url'],timeout=60).read()
 assert hashlib.sha256(raw).hexdigest()==r['sha256']
 public=json.loads(raw);local=read(R/'data/selected'/f'{r["id"]}.json')
 if r['id']=='Mitten-975':
  yarn=read(R/'data/selected/mitten_yarn_coordinate_permutation.json')
  qedist=read(R/'data/selected/mitten_qedist_coordinate_permutation.json')
  columns=inverse(yarn['columns'])
  for field,sector in [('hx','X'),('hz','Z')]:
   rows=inverse(qedist['rows_'+sector])
   transformed=[sorted(columns[qedist['columns'][j]] for j in public[field][rows[i]]) for i in yarn['rows']]
   assert transformed==local[field]
 else:
  assert public['hx']==local['hx'] and public['hz']==local['hz']
 print(r['id'],'public fixed-version matrix match',flush=True)
