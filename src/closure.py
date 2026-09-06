import fast_allen as A
from functools import lru_cache
@lru_cache(maxsize=None)
def comp(m1,m2): return A.comp(m1,m2)
BASE=tuple(1<<i for i in range(13))

def close(use_conv,use_inter,cap=8191):
    S=set(BASE); frontier=set(BASE)
    while frontier:
        new=set()
        for m1 in frontier:
            for m2 in S:
                for c in (comp(m1,m2),comp(m2,m1)):
                    if c and c not in S: new.add(c)
        if use_conv: new|={A.conv(m) for m in frontier if A.conv(m) not in S}
        if use_inter:
            for m1 in frontier:
                for m2 in S:
                    i=m1&m2
                    if i and i not in S: new.add(i)
        new-=S; S|=new; frontier=new
        if len(S)>=cap: break
    return S
for lbl,uc,ui in [("composition only",0,0),("+ converse",1,0),("+ converse + intersection",1,1)]:
    S=close(uc,ui)
    print(f"  {lbl:30} -> {len(S):5} distinct relations", flush=True)
print(f"\n  full Allen algebra (2^13 - 1)   = {2**13-1}")
