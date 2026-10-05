"""Internal consistency of HsapDv / MmusDv.

Two checks:
  1. part_of (Allen 'd') vs immediately_preceded_by (Allen 'M') on the same pair -- d ∩ M = ∅
  2. numeric containment of part_of, compared ONLY within a shared reference frame

Frame discipline matters: dpf (post fertilization) and dpc (post coitum) differ by ~0.5 day,
and the week/month post-birth series do not tile identically. Comparing across frames invents
violations that are not there -- an earlier version of this script did exactly that.
"""
import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from collections import defaultdict

OBO="http://purl.obolibrary.org/obo/"
IMM=URIRef(OBO+"RO_0002087"); PO=URIRef(OBO+"BFO_0000050")
FRAMES=["dpf","dpc","dpb","wpb","mpb","ypb"]

def load(onto):
    g=Graph().parse(f"sources/{onto}.owl")
    lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
    dep={str(s) for s in g.subjects(OWL.deprecated,None)}
    ann=defaultdict(dict)
    for s,p,o in g:
        pn=str(p).split('/')[-1].split('#')[-1]
        if pn.startswith(("start_","end_")):
            try: ann[str(s)][pn]=float(o)
            except Exception: pass
    imm=defaultdict(set); part=defaultdict(set)
    for c in set(g.subjects(RDF.type,OWL.Class)):
        if str(c) in dep: continue
        for sup in g.objects(c,RDFS.subClassOf):
            p=next(g.objects(sup,OWL.onProperty),None); v=next(g.objects(sup,OWL.someValuesFrom),None)
            if v is None or str(v) in dep: continue
            if p==IMM: imm[str(c)].add(str(v))
            elif p==PO: part[str(c)].add(str(v))
    return lab,dep,dict(ann),imm,part

def shared_interval(ann,a,b):
    """(iv_a, iv_b, frame) in the first frame where BOTH have start and end; else None."""
    for f in FRAMES:
        ka,kb=ann.get(a,{}),ann.get(b,{})
        if all(f"{w}_{f}" in ka for w in ("start","end")) and \
           all(f"{w}_{f}" in kb for w in ("start","end")):
            return (ka[f"start_{f}"],ka[f"end_{f}"]),(kb[f"start_{f}"],kb[f"end_{f}"]),f
    return None

for onto in ["hsapdv","mmusdv"]:
    lab,dep,ann,imm,part=load(onto)
    L=lambda x: lab.get(x,x.split('/')[-1])
    print("="*94); print(f"  {onto.upper()}"); print("="*94)

    clash=[(c,t) for c in imm for t in imm[c]&part.get(c,set())]
    print(f"\n1. part_of AND immediately_preceded_by on the same pair  (Allen d ∩ M = "
          f"{A.STR(A.BIT('d') & A.BIT('M')) or 'EMPTY'})")
    print(f"   violations: {len(clash)}")
    for c,t in clash:
        print(f"     ✗ {L(c)}  is part_of  {L(t)}  AND  immediately_preceded_by  {L(t)}")
        print(f"       (cannot be both inside it and start exactly where it ends)")

    print(f"\n2. numeric containment of part_of, within a shared reference frame")
    pairs=[(c,p) for c in part for p in part[c]]
    cmp=[(c,p)+ (shared_interval(ann,c,p),) for c,p in pairs]
    testable=[(c,p,x) for c,p,x in cmp if x]
    bad=[(c,p,x) for c,p,x in testable
         if not (x[1][0]-1e-9 <= x[0][0] and x[0][1] <= x[1][1]+1e-9)]
    print(f"   part_of pairs: {len(pairs)}   testable in a shared frame: {len(testable)}"
          f"   violations: {len(bad)}")
    for c,p,(a,b,f) in bad:
        print(f"     ✗ {L(c):26} [{a[0]:8.2f},{a[1]:8.2f}) {f}   NOT within   "
              f"{L(p):22} [{b[0]:8.2f},{b[1]:8.2f})")
    skipped=len(pairs)-len(testable)
    print(f"   ({skipped} pairs not testable: no frame with both endpoints on both terms)")
    print()
