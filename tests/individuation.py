"""Measurements behind IDEALISED_INDIVIDUALS.md.

  1. how much of EHDAA2 is already individuated in all but name
  2. which families' members start at different stages (class-level lossiness)
  3. whether indexed develops_from families are complete and index-matched
     -- the precondition for sound all-some promotion
  4. singletons vs families, for the one-sided-predicate carve-out
"""
import json, re, os, sys
from collections import defaultdict, Counter

D=json.load(open("out/ehdaa2.json")); LAB=D["labels"]; BB=D["backbone"]; REL=D["rel"]
L=lambda x: LAB.get(x,"")
live={k:v for k,v in LAB.items() if "EHDAA2_" in k}
starts={a:b for a,b in REL["starts_at"] if b in BB}

def family_of(v):
    for pat,grp in ((r'^(.*?)\s+(\d+)$',1), (r'^(\d+(?:st|nd|rd|th))\s+(.*)$',2),
                    (r'^(.*?)\s+(left|right)$',1)):
        m=re.match(pat,v,re.I)
        if m: return m.group(grp)
    return None

fam=defaultdict(list)
for k,v in live.items():
    f=family_of(v)
    if f: fam[f].append(k)
members={k for ks in fam.values() for k in ks}

print("="*88); print("1. how much of EHDAA2 is already individuated"); print("="*88)
print(f"   terms                : {len(live)}")
print(f"   family members       : {len(members)} ({100*len(members)/len(live):.0f}%) in {len(fam)} families")
print(f"   singletons           : {len(live)-len(members)}")

print("\n"+"="*88); print("2. families whose members start at DIFFERENT stages"); print("="*88)
spread={}
for f,ks in fam.items():
    st={BB[starts[k]]["label"] for k in ks if k in starts}
    if len(st)>1: spread[f]=sorted(st)
for f,st in sorted(spread.items(), key=lambda kv:-len(kv[1]))[:6]:
    print(f"   {f:26} spans {len(st)}: {st[0]} … {st[-1]}")
print(f"   {len(spread)} of {sum(1 for f,ks in fam.items() if any(k in starts for k in ks))} "
      f"families with data have a spread")

print("\n"+"="*88); print("3. all-some promotion precondition: complete + index-matched"); print("="*88)
idx=defaultdict(set)
for a,b in REL["develops_from"]:
    ma=re.match(r'^([a-z ]+?) (\d+)$',L(a)); mb=re.match(r'^([a-z ]+?) (\d+)$',L(b))
    if ma and mb: idx[(ma.group(1),mb.group(1))].add((int(ma.group(2)),int(mb.group(2))))
allok=True
for (p,q),pairs in sorted(idx.items(), key=lambda kv:-len(kv[1])):
    have={i for i,j in pairs if i==j}
    allp={int(re.match(r'^.*?(\d+)$',live[k]).group(1)) for k in fam.get(p,[]) if k in live}
    missing=sorted(allp-have); allok &= not missing
    print(f"   {p:14} ⊑ develops_from some {q:16} "
          f"{'✓ SOUND' if not missing else '✗ unpaired: '+str(missing[:6])}  ({len(have)}/{len(allp)})")
print(f"\n   all families promote soundly: {allok}")

print("\n"+"="*88); print("4. one-sided predicate: where is it actually justified?"); print("="*88)
ws=set(starts); singles=set(live)-members
same=sum(1 for f,ks in fam.items()
         if len({starts[k] for k in ks if k in starts})==1)
print(f"   terms with starts_at                       : {len(ws)}")
print(f"     singletons (one-sided needlessly weak)   : {len(ws & singles)}")
print(f"     family members                           : {len(ws & members)}")
print(f"   families all-same-stage (weak)             : {same}")
print(f"   families with a spread (one-sided correct) : {len(spread)}")
