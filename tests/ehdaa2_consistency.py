"""Consistency of EHDAA2's existence assertions against the HsapDv Carnegie backbone.

EHDAA2 asserts starts_at / ends_at against Carnegie stages. The IRIs it uses matter:

    starts_at = RO:0002496 "existence starts during OR AFTER"   =>  start(X) >= start(S)
    ends_at   = RO:0002497 "existence ends during OR BEFORE"    =>  end(X)   <= end(S)

Those are ONE-SIDED bounds. EHDAA2's own labels ("starts_at"/"ends_at") read as exact, so the
curatorial intent was almost certainly the two-sided RO:0002488 / RO:0002492.

The difference is not cosmetic. A violation is only detectable when the constraints make the
required ordering IMPOSSIBLE -- and a one-sided bound almost never does, because the structure
can always start arbitrarily late. Both readings are therefore tested separately.
"""
import json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
from collections import defaultdict, deque
INF=float('inf')

D=json.load(open("out/ehdaa2.json"))
BB=D["backbone"]; REL=D["rel"]; LAB=D["labels"]
L=lambda x: LAB.get(x,x.split('/')[-1])
SL=lambda s: BB[s]["label"] if s in BB else s.split('/')[-1]

starts={}; ends={}
for a,b in REL.get("starts_at",[]):
    if b in BB: starts[a]=b
for a,b in REL.get("ends_at",[]):
    if b in BB: ends[a]=b

def bounds(x, strict):
    """(start_lo, start_hi, end_lo, end_hi) for structure x."""
    slo,shi,elo,ehi=-INF,INF,-INF,INF
    if x in starts:
        s=BB[starts[x]]; slo=s["lo"]
        if strict: shi=s["hi"]
    if x in ends:
        e=BB[ends[x]]; ehi=e["hi"]
        if strict: elo=e["lo"]
    return slo,shi,elo,ehi

print("="*94); print("  COVERAGE"); print("="*94)
print(f"  structures with starts_at      : {len(starts)}")
print(f"  structures with ends_at        : {len(ends)}")
print(f"  with BOTH                      : {len(set(starts)&set(ends))}")
print(f"  start only (end unconstrained) : {len(set(starts)-set(ends))}")

for strict in (False,True):
    tag=("INTENDED — two-sided (RO:0002488/0002492, 'starts during'/'ends during')" if strict
         else "AS ASSERTED — one-sided (RO:0002496/0002497, 'during or after'/'during or before')")
    print("\n"+"="*94); print(f"  READING: {tag}"); print("="*94)

    # 1. a structure must be able to start before it ends
    bad=[]
    for x in set(starts)|set(ends):
        slo,shi,elo,ehi=bounds(x,strict)
        if slo>=ehi: bad.append((x,slo,ehi))
    print(f"\n1. can each structure start before it ends?   IMPOSSIBLE for: {len(bad)}")
    for x,a,b in bad[:8]:
        print(f"     ✗ {L(x)[:46]:48} starts_at {SL(starts.get(x,''))} (>= {a}) but ends_at "
              f"{SL(ends.get(x,''))} (<= {b})")

    # 2. part_of  =>  start(A) >= start(B)  and  end(A) <= end(B)
    po=[(a,b) for a,b in REL.get("part_of",[]) if (a in starts or a in ends) and (b in starts or b in ends)]
    bs=[]; be=[]
    for a,b in po:
        a_slo,a_shi,a_elo,a_ehi=bounds(a,strict); b_slo,b_shi,b_elo,b_ehi=bounds(b,strict)
        if a_shi<=b_slo and a_shi<INF: bs.append((a,b,a_shi,b_slo))      # A must start before B
        if a_elo>=b_ehi and a_elo>-INF: be.append((a,b,a_elo,b_ehi))     # A must end after B
    print(f"\n2. part_of containment   ({len(po)} testable pairs)")
    print(f"     part must start before its whole : {len(bs)}")
    for a,b,x,y in bs[:8]:
        print(f"       ✗ {L(a)[:34]:36} starts by {x:5} < {L(b)[:26]:28} starts from {y}")
    print(f"     part must end after its whole    : {len(be)}")
    for a,b,x,y in be[:8]:
        print(f"       ✗ {L(a)[:34]:36} ends from {x:5} > {L(b)[:26]:28} ends by {y}")

    # 3. develops_from  =>  start(A) >= start(B)
    df=[(a,b) for a,b in REL.get("develops_from",[]) if a in starts and b in starts]
    bad=[(a,b,bounds(a,strict)[1],bounds(b,strict)[0]) for a,b in df
         if bounds(a,strict)[1] <= bounds(b,strict)[0] and bounds(a,strict)[1] < INF]
    print(f"\n3. develops_from start ordering   ({len(df)} testable pairs)")
    print(f"     product provably starts BEFORE its precursor : {len(bad)}")
    for a,b,x,y in bad[:10]:
        print(f"       ✗ {L(a)[:36]:38} starts_at {SL(starts[a]):6} (by {x:4})  "
              f"develops_from  {L(b)[:24]:26} starts_at {SL(starts[b])} (from {y})")

print("\n"+"="*94); print("4. develops_from acyclicity (reading-independent)"); print("="*94)
adj=defaultdict(list)
for a,b in REL.get("develops_from",[]): adj[b].append(a)
nodes={n for e in REL.get("develops_from",[]) for n in e}
ind=defaultdict(int)
for b in adj:
    for a in adj[b]: ind[a]+=1
dq=deque([n for n in nodes if ind[n]==0]); seen=0; c=dict(ind)
while dq:
    n=dq.popleft(); seen+=1
    for m in adj[n]:
        c[m]=c.get(m,0)-1
        if c[m]==0: dq.append(m)
print(f"   {len(nodes)} structures, {len(REL.get('develops_from',[]))} edges  -> "
      f"{'ACYCLIC' if seen==len(nodes) else f'{len(nodes)-seen} NODES IN CYCLES'}")
