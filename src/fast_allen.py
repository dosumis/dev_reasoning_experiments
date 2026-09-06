"""Bitmask Allen algebra. Base 13x13 table derived once by endpoint enumeration, then cached."""
import json, os
from itertools import product
REL="pmoFDseSdfOMP"; IDX={r:i for i,r in enumerate(REL)}
BIT=lambda s: sum(1<<IDX[r] for r in s)
STR=lambda m: "".join(r for r in REL if m>>IDX[r] & 1)
CACHE="allen_table.json"

def _holds(r,s1,e1,s2,e2):
    return {'p':e1<s2,'m':e1==s2,'o':s1<s2<e1<e2,'F':s1<s2 and e1==e2,'D':s1<s2 and e2<e1,
            's':s1==s2 and e1<e2,'e':s1==s2 and e1==e2,'S':s1==s2 and e2<e1,'d':s2<s1 and e1<e2,
            'f':s2<s1 and e1==e2,'O':s2<s1<e2<e1,'M':s1==e2,'P':e2<s1}[r]
def _rel(s1,e1,s2,e2):
    h=[r for r in REL if _holds(r,s1,e1,s2,e2)]; assert len(h)==1; return h[0]

def base_table():
    if os.path.exists(CACHE): return {tuple(k.split('|')):v for k,v in json.load(open(CACHE)).items()}
    T={}
    V=range(6)
    for sA,eA,sB,eB,sC,eC in product(V,repeat=6):
        if not(sA<eA and sB<eB and sC<eC): continue
        a=_rel(sA,eA,sB,eB); b=_rel(sB,eB,sC,eC); c=_rel(sA,eA,sC,eC)
        T[(a,b)]=T.get((a,b),0)|(1<<IDX[c])
    json.dump({f"{a}|{b}":v for (a,b),v in T.items()}, open(CACHE,"w"))
    return T
T=base_table()
TB=[[T.get((a,b),0) for b in REL] for a in REL]
def comp(m1,m2):
    out=0
    for i in range(13):
        if m1>>i&1:
            row=TB[i]
            for j in range(13):
                if m2>>j&1: out|=row[j]
    return out
CONV=str.maketrans("pmoFDseSdfOMP","PMOfdSesDFomp")
def conv(m): return BIT(STR(m).translate(CONV))
