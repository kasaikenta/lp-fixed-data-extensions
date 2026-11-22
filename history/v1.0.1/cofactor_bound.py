"""Explicit <=17 logicals for every specialization of the2x5 polynomial seed."""
import copy,itertools,json,random
from pathlib import Path
import build_codes as b
from cssdist.algebra import support,permute
R=b.ROOT
def poly(terms,p):
 v=0
 for exponent,coefficient in terms:
    if coefficient&1:v ^= 1<<(exponent%p)
 return v
def multiply(a,c,p):
 out=0;mask=(1<<p)-1
 for i in support(a):out ^= ((c<<i)&mask)|(c>>(p-i) if i else 0)
 return out
records=[]
for spec in b.read(R/'data/manifest.json')['specs']:
 if spec['parent']!='LS-P31-2X5':continue
 p=spec['p'];A=copy.deepcopy(b.parent(spec['parent'])['A']);rng=random.Random(spec['seed'])
 if spec['rule']:
    for row in A:
        for terms in row:
            for term in terms:term[0] += 31*rng.choice([-1,0,1])
 arr=[[poly(v,p) for v in row] for row in A]
 code=b.make(spec);best=None
 for columns in itertools.combinations(range(5),3):
    vector=[0]*5
    for index,j in enumerate(columns):
        k,l=[v for v in columns if v!=j]
        vector[j]=multiply(arr[0][k],arr[1][l],p)^multiply(arr[0][l],arr[1][k],p)
    # Embed in tensor stripe b=2. This placement has an explicit parity detector.
    v=sum(value<<((a*5+2)*p) for a,value in enumerate(vector))
    if v and code.is_logical(v,'Z') and (best is None or v.bit_count()<best.bit_count()):best=v
 assert best is not None and best.bit_count()<=17
 xv=permute(best,code.exchange);assert code.is_logical(xv,'X')
 records.append({'id':spec['id'],'p':p,'rule':spec['rule'],'n':code.n,'k':code.k,'upper':best.bit_count(),
                 'X_support':support(xv),'Z_support':support(best),'code_sha256':code.fingerprint})
b.write(R/'cofactor_witnesses.json',{'proved_uniform_upper':17,'verified_assignments':len(records),'records':records})
print(json.dumps({'assignments':len(records),'upper_histogram':b.hist(d['upper'] for d in records),'uniform_bound':17}))
