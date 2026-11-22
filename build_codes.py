"""Generate the fixed-constituent Mitten LP code; only p and rho vary."""
from pathlib import Path
import argparse,collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor/QEDist'))
sys.path.insert(0,str(ROOT/'verification'))
from cssdist.code import CSSCode
from cssdist.algebra import support
from verify_constructions import MITTEN,evaluate
import math

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


def make(p,rho):
    fixed=evaluate(MITTEN,(p,15,rho),'ij')
    return group_lp(p,15,rho,fixed['ring'],'ij')

if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('check')
    generate=sub.add_parser('generate');generate.add_argument('--p',type=int,required=True);generate.add_argument('--rho',type=int,required=True);generate.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='generate':
        code=make(args.p,args.rho);args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(code.document,indent=2)+'\n');print(json.dumps(describe(code)))
    else:
        result=[]
        for ident,p,rho in [('Mitten-975',13,9),('Mitten-975_p22_r3_v0',22,3)]:
            code=make(p,rho);stored=CSSCode.load(ROOT/'data/selected'/f'{ident}.json')
            assert code.hx==stored.hx and code.hz==stored.hz
            result.append({'id':ident,**describe(code),'fixed_expressions':True})
        out=ROOT/'verification_results';out.mkdir(exist_ok=True)
        (out/'fixed_generation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
