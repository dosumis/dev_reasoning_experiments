"""Worked example behind IDEALISED_INDIVIDUALS.md §5.

Takes the curated existence axioms for the pharyngeal arch series from
Uberon_HDCA_stage_axioms/src/axioms.tsv, resolves them through the Carnegie backbone, and
computes the Allen relations that follow -- index-matched and cross-index.
"""
import csv, re, json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A

TSV=os.environ.get("HDCA_AXIOMS",
    "/Users/do12/Documents/GitHub/taxon-stage-axioms/src/axioms.tsv")
if not os.path.exists(TSV):
    sys.exit(f"needs Uberon_HDCA_stage_axioms checked out; set HDCA_AXIOMS= (looked in {TSV})")

BB=json.load(open("out/ehdaa2.json"))["backbone"]
stage={v["label"]:(v["lo"],v["hi"]) for v in BB.values()}
iv={}
for r in csv.DictReader(open(TSV),delimiter="\t"):
    m=re.match(r'^(pharyngeal (?:arch|arch artery|pouch)) (\d+)$', r['uberon_label'])
    if not m or r['stage_label'] not in stage: continue
    k=(m.group(1),int(m.group(2))); lo,hi=stage[r['stage_label']]
    d=iv.setdefault(k,{})
    if r['predicate']=="RO:0002488": d['lo']=lo        # existence starts during
    if r['predicate']=="RO:0002492": d['hi']=hi        # existence ends during
full={k:(d['lo'],d['hi']) for k,d in iv.items() if 'lo' in d and 'hi' in d}

print("=== curated intervals (days post-fertilization) ===")
for k,(a,b) in sorted(full.items()): print(f"  {k[0]} {k[1]:<2} [{a:5.1f}, {b:5.1f})")

print("\n=== artery N vs arch N (index-matched) -> exact ===")
for n in sorted({k[1] for k in full}):
    a=full.get(("pharyngeal arch artery",n)); b=full.get(("pharyngeal arch",n))
    if a and b: print(f"  artery {n} vs arch {n}  ->  {A._rel(a[0],a[1],b[0],b[1])}")

print("\n=== artery N vs arch M, cross-index -> different relation ===")
rel=set()
for n in sorted({k[1] for k in full}):
    for m in sorted({k[1] for k in full}):
        a=full.get(("pharyngeal arch artery",n)); b=full.get(("pharyngeal arch",m))
        if a and b and n!=m:
            r=A._rel(a[0],a[1],b[0],b[1]); rel.add(r)
            print(f"  artery {n} vs arch {m}  ->  {r}")
print(f"  -> class-level label would be {''.join(sorted(rel|{'s'}, key=A.REL.index))}")

print("\n=== arch N vs arch M ===")
ns=sorted({k[1] for k in full if k[0]=="pharyngeal arch"})
print("      "+"".join(f"{m:>6}" for m in ns))
rr=set()
for n in ns:
    row=f"  {n:2}  "
    for m in ns:
        a,b=full[("pharyngeal arch",n)],full[("pharyngeal arch",m)]
        r=A._rel(a[0],a[1],b[0],b[1]); rr.add(r); row+=f"{r:>6}"
    print(row)
lbl="".join(sorted(rr, key=A.REL.index))
print(f"\n  within-series label: {lbl}   ({'ends with' if lbl=='Fef' else '?'})")
print("\n=== promotion ===")
print("  pharyngeal arch artery ⊑ starts    some pharyngeal arch   (Allen s)")
print(f"  pharyngeal arch        ⊑ ends_with some pharyngeal arch   (Allen {lbl})")
