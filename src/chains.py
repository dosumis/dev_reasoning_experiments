import json, sys
from collections import defaultdict
OBO="http://purl.obolibrary.org/obo/"
IMM=OBO+"RO_0002087"; PO=OBO+"BFO_0000050"

name=sys.argv[1]
d=json.load(open(f"out/{name}.json"))
L=d["labels"]; R=d["rels"]; dep=set(d["deprecated"])
prec={a:b for a,b in R[IMM]}                 # a immediately_preceded_by b  => b then a
nxt=defaultdict(list)
for a,b in prec.items(): nxt[b].append(a)
parents=defaultdict(list)
for a,b in R[PO]: parents[a].append(b)

def lab(x): return L.get(x,x.split('/')[-1])

# walk each chain from its head
heads=sorted({b for b in prec.values() if b not in prec})
chains=[]
for h in heads:
    ch=[h]; cur=h
    while nxt.get(cur):
        cur=sorted(nxt[cur])[0]; ch.append(cur)
        if len(ch)>400: break
    chains.append(ch)
chains.sort(key=len, reverse=True)
print(f"### {name}: {len(chains)} chains\n")
for ch in chains:
    ps={lab(p) for x in ch for p in parents.get(x,[])}
    print(f"[{len(ch):3} stages]  parents: {sorted(ps)[:3]}")
    print(f"     {lab(ch[0])}  ->  {lab(ch[1]) if len(ch)>1 else ''}  ...  {lab(ch[-1])}")
