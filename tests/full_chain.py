"""COMPLETE CHAIN — the US1 user story, all four hops.

MP lethality (E-days) -> Theiler stage -> generic MmusDv stage -> UBERON stage -> structures
                      [dpc + meets]    [part_of closure]    [SSSOM]      [existence_*]
"""
import json, csv, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
from rdflib import Graph, RDFS, RDF, OWL, URIRef
from collections import defaultdict

OBO="http://purl.obolibrary.org/obo/"
IMM=URIRef(OBO+"RO_0002087"); PO=URIRef(OBO+"BFO_0000050")

# ---------- hop 1: MP interval -> Theiler stage ----------
g=Graph().parse("sources/mmusdv.owl")
lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
start={str(s):float(o) for s,p,o in g if str(p).endswith("start_dpc")}
prec={}; parent=defaultdict(list)
for c in set(g.subjects(RDF.type,OWL.Class)):
    for sup in g.objects(c,RDFS.subClassOf):
        p=next(g.objects(sup,OWL.onProperty),None); v=next(g.objects(sup,OWL.someValuesFrom),None)
        if v is None: continue
        if p==IMM: prec[str(c)]=str(v)
        elif p==PO: parent[str(c)].append(str(v))
end={v:start[c] for c,v in prec.items() if c in start}
iv={k:(start[k],end[k]) for k in start if k in end}

# part_of closure upward
def anc(x,seen=None):
    seen=seen or set()
    for p in parent.get(x,[]):
        if p not in seen: seen.add(p); anc(p,seen)
    return seen

# ---------- hop 3: SSSOM MmusDv -> UBERON ----------
sssom=defaultdict(list)
with open("sources/life-stages.sssom.tsv") as fh:
    for r in csv.DictReader([l for l in fh if not l.startswith("#")],delimiter="\t"):
        if r['subject_id'].startswith("MmusDv"):
            sssom[OBO+r['subject_id'].replace(':','_')].append(OBO+r['object_id'].replace(':','_'))

# ---------- hop 4: UBERON stage -> structures ----------
EX={"RO_0002488":"starts during","RO_0002489":"starts with","RO_0002490":"overlaps",
    "RO_0002491":"starts and ends during","RO_0002492":"ends during","RO_0002493":"ends with",
    "RO_0002496":"starts during or after","RO_0002497":"ends during or before"}
UL=json.load(open("out/uberon_labels.json"))
struct=defaultdict(list)
for a,p,b in json.load(open("out/uberon_existence.json")):
    if p in EX and a.startswith("http"): struct[b].append((a,EX[p]))

# ---------- run ----------
mp=[m for m in json.load(open("out/mp_lethality_intervals.json"))
    if 'penetrance' not in m['label']]
print("="*94)
for m in sorted(mp,key=lambda m:(m['lo'],m['hi'])):
    ts=[k for k,(s,e) in iv.items() if not (e<=m['lo'] or s>=m['hi'])]
    if not ts: continue
    ub=set()
    for t in ts:
        for a in {t}|anc(t):
            ub.update(sssom.get(a,[]))
    res=[]
    for u in ub: res += [(UL.get(s,s.split('/')[-1]),r,UL.get(u,'')) for s,r in struct.get(u,[])]
    if not res: continue
    print(f"\n{m['label'][:66]}   (E{m['lo']}-E{m['hi']})")
    print(f"  Theiler: {', '.join(sorted(lab.get(t,'') for t in ts)).replace('Theiler stage ','TS')[:76]}")
    print(f"  -> {len(res)} structures via {len(ub)} UBERON stages:")
    for s,r,us in sorted(set(res))[:7]:
        print(f"       {s[:38]:40} {r:24} {us}")
print("\n"+"="*94)
