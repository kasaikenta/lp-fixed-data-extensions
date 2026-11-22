"""Frozen integer-support specializations of compact LP presentations."""
from pathlib import Path
import collections, copy, hashlib, json, math, random, sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor/QEDist'))
from cssdist.code import CSSCode
from cssdist.constructors import cyclic_lp
from cssdist.algebra import support

def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')

def group_lp(p,m,rho,ring,order='ji'):
    assert math.gcd(rho,p)==1 and pow(rho,m,p)==1
    q=p*m
    pairs=[(i,j) for j in range(m) for i in range(p)] if order=='ji' else [(i,j) for i in range(p) for j in range(m)]
    index={v:i for i,v in enumerate(pairs)}
    def block(terms,right):
        rows=[0]*q
        for col,(u,t) in enumerate(pairs):
            for i,j in terms:
                dest=((u+pow(rho,t,p)*i)%p,(t+j)%m) if right else ((i+pow(rho,j,p)*u)%p,(j+t)%m)
                rows[index[dest]] ^= 1<<col
        assert all(v.bit_count()==3 for v in rows),'colliding terms'
        return rows
    def transpose(rows):
        out=[0]*q
        for r,v in enumerate(rows):
            for c in support(v):out[c] ^= 1<<r
        return out
    a0,a1=block(ring['a0'],False),block(ring['a1'],False)
    b0,b1=block(ring['b0'],True),block(ring['b1'],True)
    at0,at1,bt0,bt1=map(transpose,(a0,a1,b0,b1))
    hx=[a0[r]^(a1[r]<<(2*q))^(bt0[r]<<(4*q)) for r in range(q)]
    hx += [(a0[r]<<q)^(a1[r]<<(3*q))^(bt1[r]<<(4*q)) for r in range(q)]
    hz=[b0[r]^(b1[r]<<q)^(at0[r]<<(4*q)) for r in range(q)]
    hz += [(b0[r]<<(2*q))^(b1[r]<<(3*q))^(at1[r]<<(4*q)) for r in range(q)]
    generators=[]
    # Central x^(p/gcd(rho-1,p)) and w^ord(rho); both preserve each block.
    t=next(k for k in range(1,m+1) if pow(rho,k,p)==1)
    dx=p//math.gcd(rho-1,p)
    for step_i,step_j in [(dx,0),(0,t)]:
        if step_i%p==0 and step_j%m==0:continue
        generators.append([b*q+index[((i+step_i)%p,(j+step_j)%m)] for b in range(5) for i,j in pairs])
    code=CSSCode.from_sparse(5*q,list(map(support,hx)),list(map(support,hz)),
         lp_layout={'A_shape':[1,2],'C_shape':[1,2],'block_size':q},
         symmetry_generators=generators,cyclic_period=1)
    return code

def parent(name):
    if name=='Mitten-975':
        d=read(ROOT/'reference/mitten_parameters.json')
        # Stored mitten b terms use right inverse multiplication.
        # Convert the fixed terms to right-positive normal coordinates.
        # The symbolic inversion, not its original modular residue, is retained below.
        return {'kind':'group','p0':13,'m':15,'rho0':9,'ring':d['ring'],'inverse_right':True,'order':'ij','distance':24,'rate':.2,'weight':9}
    doc=read(ROOT/'reference'/f'{name}.json');c=doc['construction']
    if name.startswith('Hong'):
        p,m,rho=c['group']
        return {'kind':'group','p0':p,'m':m,'rho0':rho,'ring':dict(zip(['a0','a1','b0','b1'],[c['polynomials'][k] for k in 'abcd'])),'order':'ji','distance':16 if p==26 else 18,'rate':.2,'weight':9}
    return {'kind':'cyclic','p0':31,'A':c['A'],'distance':8,'rate':279/899,'weight':13}

def rule_ring(base,rule,seed):
    ring=copy.deepcopy(base)
    rng=random.Random(seed)
    if rule:
        for key,terms in ring.items():
            for pair in terms:
                if pair != [0,0]:pair[0] += rule['p0']*rng.choice([-1,0,1])
    return ring

def make(spec):
    par=parent(spec['parent']);p=spec['p'];rid=spec['rule'];seed=spec['seed']
    if par['kind']=='group':
        ring=rule_ring(par['ring'],{'p0':par['p0']} if rid else None,seed)
        if par.get('inverse_right'):
            # (x^i w^j)^-1=x^(-rho^-j i) w^-j, evaluated at EACH target.
            for key in ['b0','b1']:
                ring[key]=[[(-pow(spec['rho'],(-j)%par['m'],p)*i)%p,(-j)%par['m']] for i,j in ring[key]]
        code=group_lp(p,par['m'],spec['rho'],ring,par['order'])
    else:
        A=copy.deepcopy(par['A']);rng=random.Random(seed)
        if rid:
            for row in A:
                for terms in row:
                    for term in terms:term[0] += 31*rng.choice([-1,0,1])
        code=cyclic_lp(A,period=p,name=spec['id'])
    code.document['name']=spec['id']
    code.document['provenance']={'frozen_spec':spec,'parent_distance':par['distance'],'method':'fixed integer support and group-action specialization'}
    return code

def hist(values):return dict(sorted(collections.Counter(values).items()))
def describe(code):
    cols=[]
    for rows in [code.hx,code.hz]:
        v=[0]*code.n
        for r in rows:
            for j in support(r):v[j]+=1
        cols.append(hist(v))
    return {'n':code.n,'k':code.k,'rate':code.k/code.n,'ranks':[len(code.bx),len(code.bz)],'css_ok':True,
            'row_weights':[hist(r.bit_count() for r in rows) for rows in [code.hx,code.hz]],'column_weights':cols,
            'matrix_sha256':{k:hashlib.sha256(json.dumps([support(v) for v in rows]).encode()).hexdigest() for k,rows in [('hx',code.hx),('hz',code.hz)]}}

def parents_check():
    records=[]
    for name in ['Mitten-975','Hong-550']:
        par=parent(name)
        spec={'id':name,'parent':name,'p':par['p0'],'rho':par.get('rho0'),'rule':0,'seed':0}
        code=make(spec);old=CSSCode.load(ROOT/'reference'/f'{name}.json')
        assert code.hx==old.hx and code.hz==old.hz,name
        for rid in range(1,16):
            trial=make({**spec,'rule':rid,'seed':2026112200+rid})
            assert trial.hx==code.hx and trial.hz==code.hz,(name,rid)
        records.append({'parent':name,**describe(code),'all_16_rules_reproduce_entrywise':True})
    out=ROOT/'verification_results';out.mkdir(exist_ok=True)
    write(out/'parent_generation.json',records);print(json.dumps(records))

def manifest():
    specs=[]
    for name in ['Mitten-975','Hong-550']:
        par=parent(name)
        sizes={'Mitten-975':list(range(14,27)),'Hong-390':[31,37,43,49,61],'Hong-550':[31,41,61,71],'LS-P31-2X5':[37,41,43,47,53,61]}[name]
        for rid in range(16):
            for p in sizes:
                rhos=[None] if par['kind']=='cyclic' else sorted({(par['rho0']+par['p0']*t)%p for t in range(64) if math.gcd((par['rho0']+par['p0']*t)%p,p)==1 and pow((par['rho0']+par['p0']*t)%p,par['m'],p)==1})
                for rho in rhos:
                    ident=f'{name}_p{p}_r{rho}_v{rid}'
                    specs.append({'id':ident,'parent':name,'p':p,'rho':rho,'rule':rid,'seed':2026112200+rid,
                                  'cutoffs':list(range(par['distance'],{'Mitten-975':30,'Hong-390':20,'Hong-550':22,'LS-P31-2X5':16}[name])),
                                  'max_n':2000,'min_rate':par['rate'],'max_check_weight':par['weight']})
    # Breadth first: unmodified representatives for every parent, then alternatives.
    specs.sort(key=lambda d:(d['rule'],d['p'],d['parent'],d['rho'] or 0))
    write(ROOT/'manifest.json',{'frozen_before_distance_evaluation':True,'rules':16,'specs':specs,
          'one_hour_epoch':True,'automatic_resubmission':False,'methods':'group regular LP and cyclic polynomial LP; not full single-APM algorithms'})
    print(json.dumps({'candidates':len(specs),'parents':hist(s['parent'] for s in specs)}))

if __name__=='__main__':
    if sys.argv[1]=='check':parents_check()
    elif sys.argv[1]=='manifest':manifest()
