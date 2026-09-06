from allen import compose, REL
from itertools import product

# --- 1. how much of the 13x13 table is OWL-expressible as a property chain? ---
tab={}
for a in REL:
    for b in REL: tab[(a,b)]=compose(a,b)
sing=[(a,b,c) for (a,b),c in tab.items() if len(c)==1]
print("="*88)
print("1. Allen composition table: what fits in an OWL property chain?")
print("="*88)
print(f"  entries total              : {len(tab)}")
print(f"  SINGLETON (chain-able)     : {len(sing)}  ({100*len(sing)/len(tab):.0f}%)")
print(f"  disjunctive (NOT chain-able): {len(tab)-len(sing)}")
sizes={}
for c in tab.values(): sizes[len(c)]=sizes.get(len(c),0)+1
print(f"  result-size distribution   : {dict(sorted(sizes.items()))}")
print(f"  distinct labels appearing  : {len(set(tab.values()))}")

# --- 2. the HsapDv backbone case: composing immediately_preceded_by ---
print("\n"+"="*88)
print("2. HsapDv backbone: what RO can and cannot conclude walking back the chain")
print("="*88)
cur="M"
for step in range(2,6):
    cur=compose(cur,"M")
    print(f"  {step} steps back (M^{step})   true Allen = {cur:6}   RO can only say 'preceded_by' = PM")

# --- 3. can RO be extended to a closed set of named relations? ---
print("\n"+"="*88)
print("3. Closure: start from 13 singletons, close under composition (+converse, +intersection)")
print("="*88)
def comp_lbl(A,B):
    out=set()
    for a in A:
        for b in B: out|=set(tab[(a,b)])
    return "".join(r for r in REL if r in out)
# converse: use the verified implementation in fast_allen (an inline table here was WRONG:
# it mapped s->e, e->S, M->M. Never transcribe these tables - derive or import them.)
import fast_allen as _fa
def conv(A): return _fa.STR(_fa.conv(_fa.BIT(A)))

for mode in ["composition only","composition + converse", "composition + converse + intersection"]:
    S={r for r in REL}
    for it in range(60):
        new=set()
        for A in S:
            for B in S:
                c=comp_lbl(A,B)
                if c: new.add(c)
        if "converse" in mode: new|={conv(A) for A in S}
        if "intersection" in mode:
            for A in list(S):
                for B in list(S):
                    i="".join(r for r in REL if r in set(A)&set(B))
                    if i: new.add(i)
        if new<=S: break
        S|=new
        if len(S)>9000: break
    print(f"  {mode:38} -> {len(S):5} distinct relations after {it+1} iterations")
print(f"\n  (full Allen algebra = 2^13 - 1 = {2**13-1} non-empty labels)")
