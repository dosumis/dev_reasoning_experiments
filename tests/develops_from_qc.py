"""QC over Uberon's developmental relations, enabled by the proposed RO patch
   (out/ro_temporal_patch.ofn):  has_developmental_contribution_from  starts_after (Allen dfOMP).

X arises from Y entails start(X) > start(Y). That is a strict partial order on interval start
points, so the induced graph must be ACYCLIC and must agree with the existence_* assertions.
"""
import json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from rdflib import Graph, RDFS, RDF, OWL, URIRef
from collections import defaultdict, deque, Counter

OBO="http://purl.obolibrary.org/obo/"
SA=OBO+"AIC_0000014"; SB=OBO+"RO_0002089"

rp=Graph().parse("out/ro_patched.owl")
rlab={str(s):str(o) for s,_,o in rp.triples((None,RDFS.label,None))}
up=defaultdict(set)
for s,_,o in rp.triples((None,RDFS.subPropertyOf,None)):
    if str(s).startswith("http") and str(o).startswith("http"): up[str(s)].add(str(o))
up=dict(up)
def anc(x):
    seen=set(); dq=deque([x])
    while dq:
        for p in up.get(dq.popleft(),()):
            if p not in seen: seen.add(p); dq.append(p)
    return seen
after={k for k in list(up) if SA in anc(k)}; before={k for k in list(up) if SB in anc(k)}
print(f"RO relations entailing starts_after : {len(after)}")
print(f"                     starts_before  : {len(before)}")

g=Graph().parse("sources/uberon.owl")
lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
dep={str(s) for s in g.subjects(OWL.deprecated,None)}
edges=[]; used=Counter()
for c in set(g.subjects(RDF.type,OWL.Class)):
    if not str(c).startswith(OBO) or str(c) in dep: continue
    for sup in g.objects(c,RDFS.subClassOf):
        p=next(g.objects(sup,OWL.onProperty),None); v=next(g.objects(sup,OWL.someValuesFrom),None)
        if p is None or v is None or not str(v).startswith(OBO) or str(v) in dep: continue
        ps=str(p)
        if ps in after:    edges.append((str(c),str(v))); used[rlab.get(ps,ps)]+=1
        elif ps in before: edges.append((str(v),str(c))); used[rlab.get(ps,ps)+" [inv]"]+=1
L=lambda x: lab.get(x,x.split('/')[-1])
print(f"\n=== Uberon assertions gaining temporal semantics ===")
for r,n in used.most_common(): print(f"   {n:6}  {r}")
print(f"   {sum(used.values()):6}  TOTAL")

nodes={n for e in edges for n in e}; succ=defaultdict(set)
for x,y in edges: succ[y].add(x)
indeg=Counter()
for y in succ:
    for x in succ[y]: indeg[x]+=1
ind=dict(indeg); dq=deque([n for n in nodes if indeg[n]==0]); order=[]
while dq:
    n=dq.popleft(); order.append(n)
    for m in succ[n]:
        ind[m]=ind.get(m,0)-1
        if ind[m]==0: dq.append(m)

print(f"\n=== CHECK 1 — acyclicity (start(X)>start(X) is unsatisfiable) ===")
if len(order)<len(nodes):
    print(f"   *** {len(nodes)-len(order)} structures in cycles — CONTRADICTION ***")
else:
    print(f"   acyclic: {len(nodes)} structures, {len(edges)} edges — consistent with a strict start order")
    reach=defaultdict(set)
    for n in reversed(order):
        for m in succ[n]: reach[n].add(m); reach[n]|=reach[m]
    pairs=sum(len(v) for v in reach.values())
    print(f"   transitive closure: {pairs} ordered pairs ({pairs-len(edges)} derived beyond asserted)")
    depth={}
    for n in reversed(order): depth[n]=1+max([depth.get(m,0) for m in succ[n]],default=0)
    print(f"   longest developmental chain: {max(depth.values())} structures")

print(f"\n=== CHECK 2 — agreement with existence_* stage assertions ===")
EX={"RO_0002488":"dfO","RO_0002489":"seS","RO_0002490":"oFDseSdfO","RO_0002491":"d",
    "RO_0002492":"osd","RO_0002493":"Fef","RO_0002496":"dfOMP","RO_0002497":"pmosd"}
exist=defaultdict(dict)
for a,p,b in json.load(open("out/uberon_existence.json")):
    if p in EX and a.startswith("http"): exist[a][b]=A.BIT(EX[p])
STARTS_AFTER=A.BIT("dfOMP"); both=[(x,y) for x,y in edges if x in exist and y in exist]
viol=0
for x,y in both:
    for st in set(exist[x])&set(exist[y]):
        m=A.comp(exist[x][st],A.conv(exist[y][st]))
        if m and not (m & STARTS_AFTER):
            viol+=1
            print(f"   CONFLICT: {L(x)[:32]} arises from {L(y)[:32]}; via '{L(st)}' only {A.STR(m)} possible")
print(f"   pairs testable (both have existence assertions): {len(both)}   conflicts: {viol}")
print(f"   coverage of the DAG by existence data: {len(nodes & set(exist))}/{len(nodes)} "
      f"({100*len(nodes & set(exist))/len(nodes):.1f}%)")
