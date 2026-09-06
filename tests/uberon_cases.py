"""Real reasoning cases from Uberon existence_* assertions.
Shows conclusions reachable by label INTERSECTION - the operation OWL property chains cannot do.
"""
import json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from collections import defaultdict

EX={"RO_0002488":("existence starts during","dfO"),
    "RO_0002489":("existence starts with","seS"),
    "RO_0002490":("existence overlaps","oFDseSdfO"),
    "RO_0002491":("existence starts and ends during","d"),
    "RO_0002492":("existence ends during","osd"),
    "RO_0002493":("existence ends with","Fef"),
    "RO_0002496":("existence starts during or after","dfOMP"),
    "RO_0002497":("existence ends during or before","pmosd")}
NAME={"e":"temporally coincides with","d":"happens during","dfO":"starts during",
      "osd":"ends during","seS":"starts with","Fef":"ends with","o":"starts before and ends during",
      "oFDseSdfO":"temporally overlaps","dfOMP":"starts during or after","pmosd":"ends during or before"}

L=json.load(open("out/uberon_labels.json")); P=json.load(open("out/uberon_existence.json"))
lab=lambda x: L.get(x,x.split('/')[-1])
by=defaultdict(list)
for a,p,b in P:
    if p in EX: by[(a,b)].append(p)

print("="*94)
print("CASE SET 1  -  two assertions about the SAME (structure, stage) pair, narrowed by intersection")
print("="*94)
n=0
for (a,b),ps in sorted(by.items(), key=lambda kv: lab(kv[0][0])):
    if len(ps)<2: continue
    m=A.BIT(EX[ps[0]][1])
    for p in ps[1:]: m&=A.BIT(EX[p][1])
    res=A.STR(m); n+=1
    print(f"\n  {lab(a)}  vs  {lab(b)}")
    for p in ps: print(f"      asserted : {EX[p][0]:34} (Allen {EX[p][1]})")
    print(f"      DERIVED  : {NAME.get(res,'?'):34} (Allen {res})"
          f"{'   <- strictly tighter than either input' if res not in [EX[p][1] for p in ps] else ''}")
print(f"\n  {n} structures narrowed by intersection.")
print("  None of these conclusions is reachable by OWL property chains:")
print("  chains compose (R1 o R2), they cannot intersect two labels on the SAME pair.")

print("\n"+"="*94)
print("CASE SET 2  -  two structures related THROUGH a shared stage, by composition")
print("="*94)
struct=defaultdict(dict)
for a,p,b in P:
    if p in EX and a.startswith('http') and b.startswith('http'):
        struct[a][b]=A.BIT(EX[p][1])
pairs=[]
for x in struct:
    for y in struct:
        if x>=y: continue
        shared=set(struct[x])&set(struct[y])
        for st in shared:
            # X R st, st conv(S) Y  ->  X (R o conv(S)) Y
            m=A.comp(struct[x][st], A.conv(struct[y][st]))
            if m and bin(m).count('1')<13: pairs.append((x,y,st,m))
pairs.sort(key=lambda t: bin(t[3]).count('1'))
for x,y,st,m in pairs[:8]:
    res=A.STR(m)
    print(f"\n  {lab(x)}  vs  {lab(y)}      (via '{lab(st)}')")
    print(f"      DERIVED : {NAME.get(res,res):40} ({bin(m).count('1')} of 13 relations remain)")
print(f"\n  {len(pairs)} structure-pairs related purely by inference (nothing asserted between them).")
