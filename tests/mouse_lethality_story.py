"""USER STORY: 'Gene X knockout is embryonic lethal between E4.5 and E8.
   What structures/processes were forming in that window?'

Chain:  MP lethality interval (E-days)
     -> Theiler stages overlapping it   [ends DERIVED by propagation: 27 starts + 'meets']
     -> Uberon structures existing then  [via existence_* assertions]
"""
import json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
from rdflib import Graph, RDFS, RDF, OWL, URIRef
import fast_allen as A

OBO="http://purl.obolibrary.org/obo/"
IMM=URIRef(OBO+"RO_0002087")   # immediately_preceded_by  (Allen: metBy)

g=Graph().parse("sources/mmusdv.owl")
lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
start={}
for s,p,o in g:
    if str(p).endswith("start_dpc"): start[str(s)]=float(o)
prec={}
for c in set(g.subjects(RDF.type,OWL.Class)):
    for sup in g.objects(c,RDFS.subClassOf):
        if next(g.objects(sup,OWL.onProperty),None)==IMM:
            v=next(g.objects(sup,OWL.someValuesFrom),None)
            if v is not None: prec[str(c)]=str(v)      # c metBy v  =>  end(v)=start(c)

# ---- derive end_dpc: end(v) = start(c) whenever c immediately_preceded_by v
end={}
for c,v in prec.items():
    if c in start: end[v]=start[c]
stages=sorted([(lab.get(k,''),start[k],end.get(k)) for k in start if k in start],
              key=lambda t:t[1])
done=[(l,s,e) for l,s,e in stages if e is not None]
print(f"Theiler stages with asserted start_dpc : {len(start)}")
print(f"           with asserted end_dpc       : 0")
print(f"           with end DERIVED by 'meets'  : {len(done)}   <- propagation, not curation\n")

# ---- MP lethality intervals -> overlapping stages
mp=[m for m in json.load(open("out/mp_lethality_intervals.json"))
    if 'complete' not in m['label'] and 'incomplete' not in m['label']]
print("="*92); print("MP lethality window  ->  Theiler stages it overlaps (Allen: not p and not P)")
print("="*92)
hits={}
for m in sorted(mp,key=lambda m:(m['lo'],m['hi'])):
    ov=[l for l,s,e in done if not (e<=m['lo'] or s>=m['hi'])]
    if not ov: continue
    hits[m['label']]=ov
    print(f"\n  {m['label'][:60]}")
    print(f"     E{m['lo']}-E{m['hi']}  ->  {len(ov)} stages: {', '.join(x.replace('Theiler stage ','TS') for x in ov)}")
print(f"\n  {len(hits)} MP terms mapped onto the Theiler backbone with no manual curation.")
