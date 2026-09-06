"""Parse numeric bounds out of HsapDv definitions -> interval endpoints in days post-birth."""
import re, json
from rdflib import Graph, RDFS, URIRef

OBO="http://purl.obolibrary.org/obo/"
IAO=URIRef(OBO+"IAO_0000115")
UNIT={"hour":1/24,"day":1.0,"week":7.0,"month":30.4375,"year":365.25}

# "over X and under Y <unit>s old"  /  "over X <unit>s and under Y <unit>s old"
P1=re.compile(r'over\s+([\d.]+)\s*(hour|day|week|month|year)?s?\s+and\s+under\s+([\d.]+)\s*(hour|day|week|month|year)s?\s+old', re.I)

def parse(defn):
    m=P1.search(defn)
    if not m: return None
    lo,u1,hi,u2=m.groups()
    u1=u1 or u2
    return float(lo)*UNIT[u1.lower()], float(hi)*UNIT[u2.lower()]

g=Graph().parse("sources/hsapdv.owl")
labs={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
defs={}
for s,_,o in g.triples((None,IAO,None)): defs.setdefault(str(s),[]).append(str(o))

iv={}; multi=[]
for k,ds in defs.items():
    got=[parse(d) for d in ds]; got=[x for x in got if x]
    if not got: continue
    if len({tuple(round(v,2) for v in x) for x in got})>1: multi.append((labs.get(k,k),got))
    iv[k]=got[0]

print(f"parsed numeric intervals: {len(iv)} terms")
print(f"terms with CONFLICTING numeric definitions: {len(multi)}")
for l,got in multi[:6]:
    print(f"   ! {l:30} {[(round(a,2),round(b,2)) for a,b in got]}  (days)")
json.dump({k:list(v) for k,v in iv.items()}, open("out/hsapdv_intervals.json","w"))
print("\nsample (days post-birth):")
for k in sorted(iv, key=lambda k: iv[k][0])[:8]:
    a,b=iv[k]; print(f"   {labs.get(k,''):32} [{a:9.2f}, {b:9.2f})")
