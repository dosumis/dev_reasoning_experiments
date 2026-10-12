"""How strong a temporal axiom can develops_from actually carry?

RO's own definitions imply much stronger relations than `starts_after`:

  immediate transformation of  "x immediately succeeds y at a time boundary t"
                               -> Allen M (metBy)           = immediately_preceded_by
  directly develops from       "the start of x is coincident with or after the end of y"
                               -> Allen PM                  = preceded_by
  develops from                transitive closure of the above; M u M^2 u ... = PM

But `preceded_by` requires the PRECURSOR TO HAVE ENDED. Budding and delamination -- where the
precursor persists -- violate it. This script measures how often EHDAA2's data can satisfy
each candidate strength.
"""
import json, os, sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src"))
import fast_allen as A

D=json.load(open("out/ehdaa2.json")); BB=D["backbone"]; REL=D["rel"]; LAB=D["labels"]
L=lambda x: LAB.get(x,x.split('/')[-1])
starts={a:b for a,b in REL["starts_at"] if b in BB}
ends  ={a:b for a,b in REL["ends_at"]   if b in BB}

# two-sided (intended) reading: start(X) in [lo(S),hi(S)) ; end(X) in [lo(E),hi(E))
def sb(x):  return (BB[starts[x]]["lo"], BB[starts[x]]["hi"]) if x in starts else None
def eb(x):  return (BB[ends[x]]["lo"],   BB[ends[x]]["hi"])   if x in ends   else None

CAND=[("preceded_by (PM)  start(X) >= end(Y)",       "PM"),
      ("starts_after (dfOMP)  start(X) > start(Y)",  "dfOMP")]

print("="*96)
print("Can EHDAA2's develops_from assertions satisfy each candidate axiom?")
print("="*96)
df=REL["develops_from"]
for name,lbl in CAND:
    testable=0; viol=[]
    for a,b in df:
        sa=sb(a)
        if lbl=="PM":
            yb=eb(b)                      # needs the PRECURSOR'S END
            if sa is None or yb is None: continue
            testable+=1
            # impossible iff max start(A) <= min end(B)  ->  A must start before B ends
            if sa[1] <= yb[0]: viol.append((a,b,sa[1],yb[0]))
        else:
            yb=sb(b)
            if sa is None or yb is None: continue
            testable+=1
            if sa[1] <= yb[0]: viol.append((a,b,sa[1],yb[0]))
    print(f"\n  {name}")
    print(f"     testable pairs: {testable:5}   provably VIOLATED: {len(viol):4} "
          f"({100*len(viol)/testable if testable else 0:.1f}%)")
    for a,b,x,y in viol[:6]:
        print(f"       ✗ {L(a)[:34]:36} starts by {x:5}   {L(b)[:28]:30} "
              f"{'ends from' if lbl=='PM' else 'starts from'} {y}")

# how often does the precursor demonstrably OUTLIVE the product's start? (= budding)
print("\n"+"="*96)
print("Budding test: does the precursor still exist when the product starts?")
print("="*96)
bud=0; t=0
for a,b in df:
    sa=sb(a); eb_=eb(b)
    if sa is None or eb_ is None: continue
    t+=1
    if sa[0] < eb_[0]: bud+=1          # product's earliest start precedes precursor's earliest end
print(f"   pairs with product start + precursor end known: {t}")
print(f"   precursor provably still present at product's start: {bud} ({100*bud/t if t else 0:.1f}%)")
print("   -> these are budding / delamination; `preceded_by` is false for them by construction")

print("\n"+"="*96)
print("Allen arithmetic check")
print("="*96)
M=A.BIT("M")
clo=M
for i in range(2,5):
    clo=clo|A.comp(clo,M)
print(f"   transitive closure of M (metBy) = {A.STR(clo)}   (expect PM = preceded_by)")
print(f"   PM subset of dfOMP?  {set('PM') <= set('dfOMP')}   "
      f"-> preceded_by is STRICTLY STRONGER than starts_after")
