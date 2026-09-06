"""Cross-check asserted DV structure against parsed numeric intervals."""
import json
from rdflib import Graph, RDFS, RDF, OWL, URIRef
OBO="http://purl.obolibrary.org/obo/"
PO=URIRef(OBO+"BFO_0000050"); IMM=URIRef(OBO+"RO_0002087")

g=Graph().parse("sources/hsapdv.owl")
labs={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
dep={str(s) for s in g.subjects(OWL.deprecated,None)}
iv={k:tuple(v) for k,v in json.load(open("out/hsapdv_intervals.json")).items()}
rel={str(PO):[], str(IMM):[]}
for c in set(g.subjects(RDF.type, OWL.Class)):
    for sup in g.objects(c, RDFS.subClassOf):
        p=next(g.objects(sup,OWL.onProperty),None); v=next(g.objects(sup,OWL.someValuesFrom),None)
        if p is not None and str(p) in rel and v is not None: rel[str(p)].append((str(c),str(v)))
L=lambda x: labs.get(x,x.split('/')[-1])

print(f"terms with intervals: {len(iv)}   (deprecated among them: {len(set(iv)&dep)})\n")

# 1. part_of  =>  child interval must be contained in parent interval
po=[(a,b) for a,b in rel[str(PO)] if a in iv and b in iv]
bad_po=[(a,b) for a,b in po if not (iv[b][0]-1e-6 <= iv[a][0] and iv[a][1] <= iv[b][1]+1e-6)]
print(f"part_of pairs with both endpoints known : {len(po)}")
print(f"  containment VIOLATIONS               : {len(bad_po)}")
for a,b in bad_po[:10]:
    print(f"    {L(a):30} {tuple(round(x,1) for x in iv[a])}  NOT within  {L(b):26} {tuple(round(x,1) for x in iv[b])}")

# 2. immediately_preceded_by => a.start == b.end  (Allen: a metBy b)
im=[(a,b) for a,b in rel[str(IMM)] if a in iv and b in iv]
bad_im=[(a,b) for a,b in im if abs(iv[a][0]-iv[b][1])>1e-6]
print(f"\nimmediately_preceded_by pairs known    : {len(im)}")
print(f"  'meets' VIOLATIONS (gap/overlap)     : {len(bad_im)}")
for a,b in bad_im[:10]:
    gap=iv[a][0]-iv[b][1]
    print(f"    {L(b):30} ends {iv[b][1]:9.2f}  ->  {L(a):26} starts {iv[a][0]:9.2f}   gap={gap:+.2f}d")
