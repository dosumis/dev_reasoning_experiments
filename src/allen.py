"""Allen composition derived from first principles: enumerate consistent endpoint orderings.
Interval A = (sA,eA) with sA<eA.  Relation letters (Allen/Nebel convention):
 p precedes  m meets  o overlaps  F finishedBy  D contains  s starts
 e equals    S startedBy  d during  f finishes  O overlappedBy  M metBy  P precededBy
"""
from itertools import product
REL="pmoFDseSdfOMP"
def holds(r,s1,e1,s2,e2):
    return {
     'p': e1<s2, 'm': e1==s2, 'o': s1<s2<e1<e2, 'F': s1<s2 and e1==e2,
     'D': s1<s2 and e2<e1, 's': s1==s2 and e1<e2, 'e': s1==s2 and e1==e2,
     'S': s1==s2 and e2<e1, 'd': s2<s1 and e1<e2, 'f': s2<s1 and e1==e2,
     'O': s2<s1<e2<e1, 'M': s1==e2, 'P': e2<s1,
    }[r]
def rel_of(s1,e1,s2,e2):
    hits=[r for r in REL if holds(r,s1,e1,s2,e2)]
    assert len(hits)==1,(s1,e1,s2,e2,hits)
    return hits[0]

# brute force over small integer endpoint assignments (6 points, values 0..5)
def compose(R1,R2):
    out=set()
    V=range(6)
    for sA,eA,sB,eB,sC,eC in product(V,repeat=6):
        if not(sA<eA and sB<eB and sC<eC): continue
        if rel_of(sA,eA,sB,eB) not in R1: continue
        if rel_of(sB,eB,sC,eC) not in R2: continue
        out.add(rel_of(sA,eA,sC,eC))
    return "".join(r for r in REL if r in out)

if __name__=="__main__":
    # sanity: known entries
    for a,b,exp in [("p","p","p"),("d","d","d"),("e","o","o"),("m","m","p")]:
        got=compose(a,b); print(f"  check {a}o{b} = {got:15} (expect {exp})  {'OK' if got==exp else 'FAIL'}")
    print()
    RO={"precedes":"pm","preceded_by":"PM","immediately_precedes":"m","immediately_preceded_by":"M",
        "happens_during":"d","encompasses":"D","starts_during":"dfO","ends_during":"osd",
        "ends_after":"DSOMP","starts_before":"pmoFD"}
    inv={v:k for k,v in RO.items()}
    print(f"{'chain':52} {'true Allen composition':24} {'RO asserts':16} verdict")
    print("-"*112)
    chains=[("happens_during","precedes","precedes"),
            ("ends_during","precedes","precedes"),
            ("happens_during","preceded_by","preceded_by"),
            ("starts_during","preceded_by","preceded_by"),
            ("ends_during","preceded_by","ends_after"),
            ("starts_during","precedes","starts_before")]
    for p1,p2,asserted in chains:
        c=compose(RO[p1],RO[p2]); a=RO[asserted]
        exact = set(c)==set(a)
        sound = set(c)<=set(a)
        v = "EXACT" if exact else ("sound but LOSSY  (true ⊂ asserted)" if sound else "*** UNSOUND ***")
        print(f"{p1+' o '+p2+' -> '+asserted:52} {c+' ('+(inv.get(c,'no RO term')+')'):24} {a:16} {v}")
