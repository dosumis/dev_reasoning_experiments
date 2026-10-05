"""Extract EHDAA2 structure + a numeric Carnegie-stage backbone from HsapDv.

Backbone: CS01..CS23 carry start_dpf; ends come from the immediately_preceded_by chain
(end(N) = start(N+1)), exactly as for Theiler stages. The five sub-stages CS05a/b/c and
CS06a/b carry no bounds, so each inherits its parent's interval as a *bound* -- honest about
the fact that their internal boundaries are not stated.
"""
import json, os
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from collections import defaultdict

OBO="http://purl.obolibrary.org/obo/"
IMM=URIRef(OBO+"RO_0002087"); PO=URIRef(OBO+"BFO_0000050")
REL={"RO_0002496":"starts_at","RO_0002497":"ends_at","RO_0002202":"develops_from",
     "BFO_0000050":"part_of","RO_0002226":"develops_in","RO_0001025":"located_in"}

def backbone():
    h=Graph().parse("sources/hsapdv.owl")
    lab={str(s):str(o) for s,_,o in h.triples((None,RDFS.label,None))}
    start={str(s):float(o) for s,p,o in h if str(p).endswith("start_dpf")}
    prec={}; part=defaultdict(set)
    for c in set(h.subjects(RDF.type,OWL.Class)):
        for sup in h.objects(c,RDFS.subClassOf):
            p=next(h.objects(sup,OWL.onProperty),None); v=next(h.objects(sup,OWL.someValuesFrom),None)
            if v is None: continue
            if p==IMM: prec[str(c)]=str(v)
            elif p==PO: part[str(c)].add(str(v))
    # Build intervals by SORTING on start_dpf rather than walking the precedence chain:
    # the chain is broken by the CS05a defect (CS05's "successor" is CS05a, which has no
    # bounds), which silently robbed CS05 of an end. See tests/dv_selfcheck.py.
    carn={c:v for c,v in start.items() if lab.get(c,"").startswith("Carnegie stage")}
    seq=sorted(carn, key=lambda c: carn[c])
    iv={}
    for a,b in zip(seq,seq[1:]): iv[a]=(carn[a],carn[b])
    iv[seq[-1]]=(carn[seq[-1]], 60.0)      # CS23 -> end of the Carnegie series
    # sub-stages: inherit the parent's interval as a bound
    for c in list(part):
        if c in iv: continue
        for p in part[c]:
            if p in iv: iv[c]=iv[p]; break
    return {c:dict(label=lab.get(c,''),lo=v[0],hi=v[1],
                   exact=(c in carn)) for c,v in iv.items()}

def ehdaa2():
    g=Graph().parse("sources/ehdaa2.owl")
    lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
    dep={str(s) for s in g.subjects(OWL.deprecated,None)}
    rel=defaultdict(list)
    for c in set(g.subjects(RDF.type,OWL.Class)):
        cs=str(c)
        if not cs.startswith("http") or cs in dep: continue
        for sup in g.objects(c,RDFS.subClassOf):
            if str(sup).startswith("http"):
                if str(sup) not in dep: rel["is_a"].append((cs,str(sup)))
                continue
            p=next(g.objects(sup,OWL.onProperty),None)
            v=next(g.objects(sup,OWL.someValuesFrom),None)
            if p is None or v is None or str(v) in dep: continue
            pid=str(p).split('/')[-1]
            if pid in REL: rel[REL[pid]].append((cs,str(v)))
    return dict(rel), lab

if __name__=="__main__":
    bb=backbone(); rel,lab=ehdaa2()
    print(f"Carnegie backbone: {len(bb)} stages with intervals "
          f"({sum(1 for v in bb.values() if v['exact'])} exact, "
          f"{sum(1 for v in bb.values() if not v['exact'])} inherited from parent)")
    for c,v in sorted(bb.items(), key=lambda kv:(kv[1]['lo'],kv[1]['label']))[:6]:
        print(f"    {v['label']:20} [{v['lo']:5.1f}, {v['hi']:5.1f}) dpf  {'exact' if v['exact'] else 'bound'}")
    print("  ...")
    print("\nEHDAA2 relations:")
    for k,v in sorted(rel.items(), key=lambda kv:-len(kv[1])): print(f"  {len(v):6}  {k}")
    os.makedirs("out",exist_ok=True)
    json.dump({"backbone":bb,"rel":rel,"labels":lab}, open("out/ehdaa2.json","w"))
    print("\nsaved -> out/ehdaa2.json")
