"""Resolve HP onset terms to numeric intervals via their HsapDv equivalence axioms,
   and verify that the series forms a perfect partition (consecutive Allen 'meets').
   Backs the claims in HP_ONSET_PROPOSAL.md."""
import re, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from rdflib import Graph, RDFS

OBO="http://purl.obolibrary.org/obo/"; BIRTH=266.0
FR={"dpf":(1.0,0.0),"dpb":(1.0,BIRTH),"mpb":(30.4375,BIRTH),"ypb":(365.25,BIRTH)}

# --- HP: onset terms and their HsapDv equivalence targets -------------------
# split on class-comment markers: a naive <owl:Class>...</owl:Class> regex breaks on the
# nested </owl:Class> inside owl:equivalentClass, silently dropping exactly these terms.
raw=open("sources/hp.owl",encoding="utf8",errors="replace").read()
parts=re.split(r'<!-- (http://purl\.obolibrary\.org/obo/HP_\d+) -->', raw)
strip=lambda t: re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t)).strip()
onset={}
for i in range(1,len(parts),2):
    iri, body = parts[i], parts[i+1]
    m=re.search(r'<rdfs:label[^>]*>(.*?)</rdfs:label>',body,re.S)
    if not m: continue
    l=strip(m.group(1))
    dv=re.findall(r'someValuesFrom rdf:resource="http://purl\.obolibrary\.org/obo/(HsapDv_\d+)"',body)
    if 'onset' in l.lower() and dv: onset[l]=dv[0]

# --- HsapDv: numeric endpoints ---------------------------------------------
g=Graph().parse("sources/hsapdv.owl")
lab={str(s):str(o) for s,_,o in g.triples((None,RDFS.label,None))}
ann={}
for s,p,o in g:
    pn=str(p).split('/')[-1].split('#')[-1]
    if pn.startswith(("start_","end_")): ann.setdefault(str(s),{})[pn]=float(o)
def interval(dvid):
    a=ann.get(OBO+dvid,{})
    for f,(mult,off) in FR.items():
        if f"start_{f}" in a and f"end_{f}" in a:
            return (a[f"start_{f}"]*mult+off, a[f"end_{f}"]*mult+off)
    for f,(mult,off) in FR.items():
        if f"start_{f}" in a: return (a[f"start_{f}"]*mult+off, float('inf'))
    return None

print(f"HP onset terms logically defined against HsapDv: {len(onset)}\n")
iv={}
for l,dv in sorted(onset.items()):
    v=interval(dv); iv[l]=v
    end = "inf" if (v and v[1]==float('inf')) else (f"{v[1]:.0f}" if v else "?")
    print(f"  {l:22} -> {lab.get(OBO+dv,dv)[:28]:30} "
          f"{'['+format(v[0],'.0f')+', '+end+')' if v else '-- no bounds --'}")
print(f"\n  fully bounded: {sum(1 for v in iv.values() if v and v[1]!=float('inf'))}/{len(iv)}")

# Juvenile onset has no HsapDv axiom; HsapDv:0000271 'juvenile stage (5-14 yo)' fits its prose
iv["Juvenile onset*"]=interval("HsapDv_0000271")
print(f"  Juvenile onset* (proposed HsapDv:0000271): "
      f"[{iv['Juvenile onset*'][0]:.0f}, {iv['Juvenile onset*'][1]:.0f})")

SERIES=["Antenatal onset","Neonatal onset","Infantile onset","Childhood onset",
        "Juvenile onset*","Young adult onset","Middle age onset","Late onset"]
print("\n=== is the series a perfect partition? (consecutive Allen 'm' = meets) ===")
CAP=1e12; ok=True
for a,b in zip(SERIES,SERIES[1:]):
    x,y=iv[a],iv[b]
    r=A._rel(x[0],min(x[1],CAP),y[0],min(y[1],CAP))
    ok &= (r=="m")
    print(f"   {a:20} -> {b:20} {'meets' if r=='m' else '*** '+r+' ***'}")
print(f"\n  perfect partition: {ok}")

print("\n=== nesting of the coarser terms ===")
for a,b in [("Embryonal onset","Antenatal onset"),("Fetal onset","Antenatal onset"),
            ("Young adult onset","Adult onset"),("Middle age onset","Adult onset")]:
    if a in iv and b in iv and iv[a] and iv[b]:
        x,y=iv[a],iv[b]
        print(f"   {a:20} {A._rel(x[0],min(x[1],CAP),y[0],min(y[1],CAP)):3} {b}")
