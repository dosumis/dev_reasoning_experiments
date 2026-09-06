from allen import compose, REL
RO={"precedes":"pm","preceded_by":"PM","immediately_precedes":"m","immediately_preceded_by":"M",
    "happens_during":"d","encompasses":"D","starts_during":"dfO","ends_during":"osd",
    "ends_after":"DSOMP","starts_before":"pmoFD"}
inv={v:k for k,v in RO.items()}
name=lambda c: inv.get("".join(r for r in REL if r in c), "no RO term")

print("="*104); print("1. TRANSITIVITY declared in RO"); print("="*104)
declared={"precedes","preceded_by","happens_during","encompasses","ends_after","starts_before"}
for p in sorted(RO):
    c=compose(RO[p],RO[p]); trans=set(c)<=set(RO[p]); d=p in declared
    flag = "OK" if trans==d else ("*** RO declares transitive but ISN'T ***" if d else "-> transitive but NOT declared (missed inference)")
    print(f"  {p:26} {RO[p]:6} o {RO[p]:6} = {c:8}  Allen-transitive={str(trans):5} RO-declares={str(d):5}  {flag}")

print("\n"+"="*104); print("2. subPropertyOf declared in RO  (R1 sub R2 valid iff label(R1) subset-of label(R2))"); print("="*104)
subs=[("happens_during","starts_during"),("happens_during","ends_during"),("preceded_by","ends_after"),
      ("immediately_preceded_by","preceded_by"),("immediately_precedes","precedes"),("encompasses","precedes")]
for a,b in subs:
    ok=set(RO[a])<=set(RO[b])
    print(f"  {a:26} ⊑ {b:22} {RO[a]:6} ⊆ {RO[b]:8}  {'OK' if ok else '*** INVALID ***'}")

print("\n"+"="*104); print("3. PROPERTY CHAINS asserted in RO"); print("="*104)
chains=[("happens_during","precedes","precedes"),("happens_during","preceded_by","preceded_by"),
        ("starts_during","preceded_by","preceded_by"),("ends_during","preceded_by","ends_after"),
        ("starts_during","precedes","starts_before"),("ends_during","precedes","precedes")]
loss=0
for p1,p2,got in chains:
    c=compose(RO[p1],RO[p2]); a=RO[got]
    if set(c)==set(a): v="EXACT"
    elif set(c)<=set(a): v=f"LOSSY  — true result is '{c}' ({name(c)}); RO must weaken to '{a}'"; loss+=1
    else: v="*** UNSOUND ***"
    print(f"  {p1} o {p2} -> {got}")
    print(f"      true={c:8} asserted={a:8}  {v}")
print(f"\n  {loss}/{len(chains)} chains lose information because RO has no term for the exact result.")
