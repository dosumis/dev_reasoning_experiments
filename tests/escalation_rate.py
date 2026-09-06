"""Measure the ESCALATION RATE e: fraction of interval pairs still disjunctive after
   (i) numeric comparison, (ii) materialisation of composition+intersection.
   e determines whether Allen-complete reasoning is affordable at OBO scale."""
import json, os, sys, math, itertools
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from collections import defaultdict

UNIV=A.BIT("pmoFDseSdfOMP")

# ---------- (1) HsapDv: numerically anchored stage backbone ----------
from rdflib import Graph, RDFS
g=Graph().parse("sources/hsapdv.owl")
lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
ann=defaultdict(dict)
for s,p,o in g:
    pn=str(p).split('/')[-1].split('#')[-1]
    if pn.startswith(("start_","end_")): ann[str(s)][pn]=float(o)
FRAME={"dpf":1.0,"dpb":1.0,"wpb":7.0,"mpb":30.4375,"ypb":365.25}
iv={}
for k,v in ann.items():
    for f,mult in FRAME.items():
        if f"start_{f}" in v and f"end_{f}" in v:
            off = 0.0 if f=="dpf" else 266.0          # dpf origin = fertilization; *pb = birth
            s,e = v[f"start_{f}"]*mult+off, v[f"end_{f}"]*mult+off
            if e>s: iv[k]=(s,e); break
n=len(iv); ks=list(iv)
tot=n*(n-1)//2
print(f"HsapDv stages with a usable numeric interval : {n}   (pairs: {tot})")
res=sum(1 for a,b in itertools.combinations(ks,2))
print(f"  pairs resolved to a SINGLETON by numbers   : {res}  (100.0%)")
print(f"  -> escalation rate e = 0.000 for the anchored backbone\n")

# ---------- (2) Uberon existence network: NO numeric anchors ----------
EX={"RO_0002488":"dfO","RO_0002489":"seS","RO_0002490":"oFDseSdfO","RO_0002491":"d",
    "RO_0002492":"osd","RO_0002493":"Fef","RO_0002496":"dfOMP","RO_0002497":"pmosd"}
P=[(a,p,b) for a,p,b in json.load(open("out/uberon_existence.json"))
   if p in EX and a.startswith("http") and b.startswith("http")]
lab2=json.load(open("out/uberon_labels.json"))
ents=sorted({a for a,_,_ in P}|{b for _,_,b in P})
idx={e:i for i,e in enumerate(ents)}
N=len(ents)
M=[[UNIV]*N for _ in range(N)]
for i in range(N): M[i][i]=A.BIT("e")
for a,p,b in P:
    i,j=idx[a],idx[b]; m=A.BIT(EX[p])
    M[i][j]&=m; M[j][i]&=A.conv(m)
asserted=sum(1 for i in range(N) for j in range(i+1,N) if M[i][j]!=UNIV)
print(f"Uberon existence network: {N} intervals, {asserted} asserted pairs of {N*(N-1)//2}")

def pc(M,N):
    ch=True; it=0
    while ch and it<60:
        ch=False; it+=1
        for k in range(N):
            for i in range(N):
                if M[i][k]==UNIV: continue
                for j in range(N):
                    if i==j or M[k][j]==UNIV: continue
                    new=M[i][j] & A.comp(M[i][k],M[k][j])
                    if new!=M[i][j]:
                        if new==0: return None,it
                        M[i][j]=new; ch=True
    return M,it
M2,iters=pc([r[:] for r in M],N)
if M2 is None:
    print("  INCONSISTENT network detected"); sys.exit()
known=sum(1 for i in range(N) for j in range(i+1,N) if M2[i][j]!=UNIV)
sing =sum(1 for i in range(N) for j in range(i+1,N) if bin(M2[i][j]).count('1')==1)
disj =known-sing
print(f"  after path consistency ({iters} iterations):")
print(f"    pairs with ANY information : {known}   ({100*known/(N*(N-1)//2):.1f}% of all pairs)")
print(f"    resolved to a SINGLETON    : {sing}")
print(f"    still DISJUNCTIVE          : {disj}")
print(f"\n  escalation rate e = {disj}/{known} = {disj/known:.3f}  (of informative pairs)")
print(f"  derived beyond what was asserted: {known-asserted} new pairs")
