"""Individual-level chains among SINGLETON structures -- the case where no class/family
   ambiguity arises at all, so individuation is available immediately.

Measures: chain depth, how many pairs composition derives beyond what is asserted, and how
often the derived relation is EXACT (a singleton Allen label rather than a disjunction).
"""
import json, re, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from collections import defaultdict, Counter

D=json.load(open("out/ehdaa2.json")); LAB=D["labels"]; BB=D["backbone"]; REL=D["rel"]
L=lambda x: LAB.get(x,"")
starts={a:b for a,b in REL["starts_at"] if b in BB}
ends  ={a:b for a,b in REL["ends_at"]   if b in BB}
def iv(n):
    if n not in starts or n not in ends: return None
    return (BB[starts[n]]["lo"], BB[ends[n]]["hi"])
isfam=lambda v: bool(re.match(r'^.*?\s+\d+$',v) or re.match(r'^\d+(st|nd|rd|th)\s',v)
                     or re.search(r'\s(left|right)$',v,re.I))

# singleton develops_from edges where BOTH ends have a full interval
edges=[(a,b) for a,b in REL["develops_from"]
       if not isfam(L(a)) and not isfam(L(b)) and iv(a) and iv(b)]
par=defaultdict(list)
for a,b in edges: par[a].append(b)
nodes={n for e in edges for n in e}

print("="*90); print("Singleton develops_from graph with both endpoints bounded"); print("="*90)
print(f"   structures : {len(nodes)}")
print(f"   edges      : {len(edges)}")

# transitive closure, carrying the composed label
anc={}
def ancestors(n, stack=frozenset()):
    if n in anc: return anc[n]
    if n in stack: return {}
    out={}
    for p in par.get(n,[]):
        r=A.BIT(A._rel(*iv(n), *iv(p)))
        out[p]=out.get(p,0)|r
        for g,lab in ancestors(p, stack|{n}).items():
            out[g]=out.get(g,0)|A.comp(r,lab)
    anc[n]=out; return out
for n in nodes: ancestors(n)

asserted={(a,b) for a,b in edges}
pairs=[(n,p,lab) for n in nodes for p,lab in anc[n].items()]
derived=[(n,p,lab) for n,p,lab in pairs if (n,p) not in asserted]
exact=[t for t in derived if bin(t[2]).count('1')==1]
sound=sum(1 for n,p,lab in pairs if A._rel(*iv(n), *iv(p)) in A.STR(lab))
print(f"\n   pairs related after closure : {len(pairs)}")
print(f"     asserted                  : {len(pairs)-len(derived)}")
print(f"     DERIVED                   : {len(derived)}  ({len(derived)/max(1,len(pairs)-len(derived)):.1f}x the asserted)")
print(f"     of those, EXACT           : {len(exact)} ({100*len(exact)/max(1,len(derived)):.0f}%)")
print(f"   soundness check (composed label contains the true relation): {sound}/{len(pairs)}")
print(f"\n   derived label sizes: {dict(sorted(Counter(bin(l).count('1') for _,_,l in derived).items()))}")

print("\n"+"="*90); print("Named chains"); print("="*90)
rev=defaultdict(list)
for a,b in REL["develops_from"]: rev[a].append(b)
byname={v:k for k,v in LAB.items()}
for tgt in ["ureteric bud","liver","gall bladder","outflow tract pulmonary artery"]:
    n=byname.get(tgt); ch=[]
    while n and len(ch)<10:
        ch.append(n); n=rev[n][0] if rev.get(n) else None
    ch=[x for x in reversed(ch) if iv(x)]
    if len(ch)<3: continue
    rels=[A._rel(*iv(ch[i+1]), *iv(ch[i])) for i in range(len(ch)-1)]
    print(f"\n   {tgt}  ({len(ch)} steps)")
    for i,x in enumerate(ch):
        a,b=iv(x)
        print(f"     {L(x)[:40]:42} [{a:5.1f}, {b:5.1f})" + (f"   <- {rels[i-1]}" if i else ""))
