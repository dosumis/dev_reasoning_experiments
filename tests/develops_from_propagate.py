"""Propagating QC: derive start-order constraints through the develops_from DAG and test them
   against the stage ordering asserted in Uberon.

   develops_from  starts_after  (Allen dfOMP)  =>  start(X) > start(Y), transitively.
   If X's existence begins in a stage that STRICTLY PRECEDES Y's, that is a contradiction.
"""
import json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A
from collections import defaultdict, deque

D=json.load(open("out/uberon_dev.json")); DF=[tuple(e) for e in D["df"]]; L=dict(D["labels"])
S=json.load(open("out/uberon_stage_rels.json")); L.update(S["labels"])
lab=lambda x: L.get(x,x.split('/')[-1])

# ---------- stage strict-precedence closure ----------
after=defaultdict(set)      # after[a] = stages a comes strictly after
part=defaultdict(set)
for a,r,b in S["rels"]:
    if r in ("preceded_by","imm_preceded_by"): after[a].add(b)
    elif r in ("precedes","imm_precedes"):     after[b].add(a)
    elif r=="part_of":                          part[a].add(b)
# inherit precedence through part_of, then transitively close
for _ in range(6):
    for a in list(part):
        for p in part[a]: after[a] |= after[p]
    ch=True
    while ch:
        ch=False
        for a in list(after):
            add=set()
            for b in after[a]: add |= after[b]
            if not add <= after[a]: after[a] |= add; ch=True
strictly_after=lambda x,y: y in after[x]
print(f"stage precedence pairs after closure: {sum(len(v) for v in after.values())}")

# ---------- earliest possible start stage per structure ----------
EX_STARTS={"RO_0002488","RO_0002489","RO_0002491","RO_0002496"}   # constrain the START
EX_ALL={"RO_0002488","RO_0002489","RO_0002490","RO_0002491","RO_0002492","RO_0002493",
        "RO_0002496","RO_0002497"}
startstage=defaultdict(set); anystage=defaultdict(set)
for a,p,b in json.load(open("out/uberon_existence.json")):
    if not a.startswith("http") or p not in EX_ALL: continue
    anystage[a].add(b)
    if p in EX_STARTS: startstage[a].add(b)
print(f"structures with a START-constraining existence assertion: {len(startstage)}")

# ---------- propagate through develops_from ----------
succ=defaultdict(list); pred=defaultdict(list)
for x,y in DF: succ[y].append(x); pred[x].append(y)   # y -> x  (x develops_from y)
nodes={n for e in DF for n in e}
print(f"develops_from DAG: {len(nodes)} structures, {len(DF)} edges")

# derived: X cannot start before any stage constraining an ancestor Y
derived=defaultdict(set); q=deque(n for n in nodes if n in startstage)
for n in q: derived[n]|=startstage[n]
seen=0
order=[]; indeg={n:len(pred[n]) for n in nodes}
dq=deque([n for n in nodes if indeg[n]==0])
while dq:
    n=dq.popleft(); order.append(n)
    for m in succ[n]:
        indeg[m]-=1
        if indeg[m]==0: dq.append(m)
for n in order:
    for m in succ[n]:
        derived[m] |= derived[n]          # m develops_from n => m starts at/after n's constraints
        seen+=1
print(f"structures with a DERIVED start constraint: {sum(1 for n in derived if derived[n])}"
      f"   (vs {len(startstage)} asserted)  -> {sum(1 for n in derived if derived[n])-len(startstage)} gained by propagation")

# ---------- contradictions ----------
print("\n"+"="*92); print("CONTRADICTIONS"); print("="*92)
viol=[]
for x,y in DF:
    for sx in startstage.get(x,()):
        for sy in derived.get(y,()) | startstage.get(y,set()):
            if strictly_after(sy,sx):     # y's start stage is strictly AFTER x's => impossible
                viol.append((x,y,sx,sy))
seenp=set(); n=0
for x,y,sx,sy in viol:
    if (x,y) in seenp: continue
    seenp.add((x,y)); n+=1
    print(f"  {lab(x)[:34]:36} develops_from  {lab(y)[:32]}")
    print(f"      {lab(x)[:20]:22} starts in '{lab(sx)}'  but {lab(y)[:18]} starts in '{lab(sy)}', which is later")
print(f"\n  {n} contradicting develops_from assertions")
