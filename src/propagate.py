"""Bounds propagation (STP-style) over DV structure: sparse numeric anchors -> bounded endpoints for all."""
import json, math
from rdflib import Graph, RDFS, RDF, OWL, URIRef
OBO="http://purl.obolibrary.org/obo/"
PO=URIRef(OBO+"BFO_0000050"); IMM=URIRef(OBO+"RO_0002087"); PREC=URIRef(OBO+"BFO_0000062")
INF=float('inf')

g=Graph().parse("sources/hsapdv.owl")
labs={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
dep={str(s) for s in g.subjects(OWL.deprecated,None)}
anchor={k:tuple(v) for k,v in json.load(open("out/hsapdv_intervals.json")).items()}
rel={PO:[],IMM:[],PREC:[]}
terms=set()
for c in set(g.subjects(RDF.type,OWL.Class)):
    if not str(c).startswith(OBO) or str(c) in dep: continue
    terms.add(str(c))
    for sup in g.objects(c,RDFS.subClassOf):
        p=next(g.objects(sup,OWL.onProperty),None); v=next(g.objects(sup,OWL.someValuesFrom),None)
        if p in rel and v is not None and str(v) not in dep: rel[p].append((str(c),str(v)))
L=lambda x: labs.get(x,x.split('/')[-1])

# bounds: term -> [s_lo,s_hi,e_lo,e_hi]
B={t:[-INF,INF,-INF,INF] for t in terms}
for t,(a,b) in anchor.items():
    if t in B: B[t]=[a,a,b,b]

def tighten(t,i,val,op):
    old=B[t][i]
    new=max(old,val) if op=='lo' else min(old,val)
    if new!=old and not (math.isinf(new) and math.isinf(old)):
        B[t][i]=new; return True
    return False

for it in range(200):
    ch=False
    for a,b in rel[PO]:                    # a during b : b.s <= a.s , a.e <= b.e
        if a in B and b in B:
            ch|=tighten(a,0,B[b][0],'lo'); ch|=tighten(b,1,B[a][1],'hi')
            ch|=tighten(a,3,B[b][3],'hi'); ch|=tighten(b,2,B[a][2],'lo')
    for a,b in rel[IMM]:                   # a metBy b : a.s == b.e
        if a in B and b in B:
            ch|=tighten(a,0,B[b][2],'lo'); ch|=tighten(a,1,B[b][3],'hi')
            ch|=tighten(b,2,B[a][0],'lo'); ch|=tighten(b,3,B[a][1],'hi')
    for a,b in rel[PREC]:                  # a after b : a.s >= b.e
        if a in B and b in B: ch|=tighten(a,0,B[b][2],'lo')
    for t in terms:                        # s <= e
        ch|=tighten(t,2,B[t][0],'lo'); ch|=tighten(t,1,B[t][3],'hi')
    if not ch: break
print(f"converged after {it+1} iterations\n")

anch=set(anchor)&terms
def bounded(t): return all(not math.isinf(x) for x in B[t])
def partly(t): return any(not math.isinf(x) for x in B[t])
newly=[t for t in terms if t not in anch and bounded(t)]
partial=[t for t in terms if t not in anch and partly(t) and not bounded(t)]
print(f"live terms                     : {len(terms)}")
print(f"  numerically anchored (input) : {len(anch)}")
print(f"  FULLY bounded by propagation : {len(newly)}")
print(f"  partially bounded            : {len(partial)}")
print(f"  still unbounded              : {len(terms)-len(anch)-len(newly)-len(partial)}")
print("\nExamples of terms dated purely by propagation (days post-birth):")
for t in sorted(newly,key=lambda t:B[t][0])[:12]:
    s_lo,s_hi,e_lo,e_hi=B[t]
    print(f"  {L(t):34} start∈[{s_lo:9.1f},{s_hi:9.1f}]  end∈[{e_lo:9.1f},{e_hi:9.1f}]")
json.dump({t:B[t] for t in terms}, open("out/hsapdv_bounds.json","w"))
