"""Generate ROBOT template + composition chains for the 29-relation Allen extension to RO."""
import csv, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import fast_allen as A, itertools

# ---------------------------------------------------------------- the subalgebra
def subalgebra():
    S=set(1<<i for i in range(13))
    while True:
        n=len(S); L=list(S)
        S|={A.conv(m) for m in L}
        S|={a&b for a in L for b in L if a&b}
        S|={c for a in L for b in L if (c:=A.comp(a,b))}
        if len(S)==n: return S

# ---------------------------------------------------------------- endpoint invariants
PAIR=[("start(X)","start(Y)"),("start(X)","end(Y)"),("end(X)","start(Y)"),("end(X)","end(Y)")]
def _sig(r):
    for a,b,c,d in itertools.product(range(6),repeat=4):
        if a<b and c<d and A._rel(a,b,c,d)==r:
            s=lambda x,y:'<' if x<y else ('=' if x==y else '>')
            return (s(a,c),s(a,d),s(b,c),s(b,d))
SIG={r:_sig(r) for r in A.REL}
def invariant(lbl):
    vs=[SIG[r] for r in lbl]
    return " and ".join(f"{PAIR[i][0]} {vs[0][i]} {PAIR[i][1]}"
                        for i in range(4) if len({v[i] for v in vs})==1)

# ---------------------------------------------------------------- naming
# (RO id, label, status)  status: existing | new | COLLISION-CHECK
N={
 # --- already in RO, verified against ro.owl ---
 "m":            ("RO:0002090","immediately precedes","existing"),
 "M":            ("RO:0002087","immediately preceded by","existing"),
 "d":            ("RO:0002092","happens during","existing"),
 "D":            ("RO:0002085","encompasses","existing"),
 "dfO":          ("RO:0002091","starts during","existing"),
 "osd":          ("RO:0002093","ends during","existing"),
 "oFD":          ("RO:0002088","during which starts","existing"),
 "DSO":          ("RO:0002084","during which ends","existing"),
 "DSOMP":        ("RO:0002086","ends after","existing"),
 "pmoFD":        ("RO:0002089","starts before","existing"),
 "pmoFDseSdfOMP":("RO:0002222","temporally related to","existing"),
 # --- new atoms ---
 "p":  ("AIC:0000001","strictly precedes","new"),
 "P":  ("AIC:0000002","strictly preceded by","new"),
 "o":  ("AIC:0000003","starts before and ends during","new"),
 "O":  ("AIC:0000004","starts during and ends after","new"),
 "s":  ("AIC:0000005","starts with and ends before","new"),
 "S":  ("AIC:0000006","starts with and ends after","new"),
 "f":  ("AIC:0000007","ends with and starts after","new"),
 "F":  ("AIC:0000008","ends with and starts before","new"),
 "e":  ("AIC:0000009","temporally coincides with","COLLISION-CHECK: RO:0002082 simultaneous with / RO:0002008 coincident with"),
 # --- new disjunctions ---
 "seS":         ("AIC:0000010","starts with","COLLISION-CHECK: RO:0002224 starts with may be mereological (Fe not seS)"),
 "Fef":         ("AIC:0000011","ends with","COLLISION-CHECK: RO:0002230 ends with may be mereological (fe not Fef)"),
 "pmo":         ("AIC:0000012","earlier than","new"),
 "OMP":         ("AIC:0000013","later than","new"),
 "dfOMP":       ("AIC:0000014","starts during or after","new (precedent: RO:0002496 existence starts during or after)"),
 "pmosd":       ("AIC:0000015","ends during or before","new (precedent: RO:0002497 existence ends during or before)"),
 "oFDseSdfO":   ("AIC:0000016","temporally overlaps","COLLISION-CHECK: RO:0002131 'overlaps' is mereological - do NOT reuse"),
 "oFDseSdfOMP": ("AIC:0000017","ends after start of","new"),
 "pmoFDseSdfO": ("AIC:0000018","starts before end of","new"),
}

def main():
    S=subalgebra(); labels=sorted((A.STR(m) for m in S), key=lambda x:(len(x),x))
    assert len(labels)==29 and all(l in N for l in labels)
    os.makedirs("templates",exist_ok=True)

    # -------- 1. relations template
    with open("templates/aic_relations.tsv","w",newline="") as fh:
        w=csv.writer(fh,delimiter="\t",lineterminator="\n")
        w.writerow(["ID","Label","Type","Definition","Comment"])
        w.writerow(["ID","LABEL","TYPE","A IAO:0000115","A rdfs:comment"])
        for l in labels:
            iri,lbl,st=N[l]
            cv=A.STR(A.conv(A.BIT(l)))
            trans = set(A.STR(A.comp(A.BIT(l),A.BIT(l))))<=set(l)
            w.writerow([iri,lbl,"owl:ObjectProperty",
                        f"X {lbl} Y if and only if {invariant(l)}.",
                        f"Allen label: {l}. Status: {st}."])

    # -------- 2. composition chains (only those whose result is in the 29 = all of them)
    rows=[]
    for a in labels:
        for b in labels:
            c=A.STR(A.comp(A.BIT(a),A.BIT(b)))
            if c: rows.append((N[a][1],N[b][1],N[c][1],a,b,c))
    with open("templates/aic_chains.tsv","w",newline="") as fh:
        w=csv.writer(fh,delimiter="\t",lineterminator="\n")
        w.writerow(["property 1","property 2","implies","allen 1","allen 2","allen result"])
        for r in rows: w.writerow(r)

    # -------- 3. logical axioms (ROBOT templates cannot express inverses or property chains)
    IRI=lambda l: ("http://purl.obolibrary.org/obo/"+N[l][0].replace(":","_"))
    ax=[]
    for l in labels:
        ax.append(f"Declaration(ObjectProperty(<{IRI(l)}>))")
    for l in labels:
        cv=A.STR(A.conv(A.BIT(l)))
        if cv!=l and l<cv: ax.append(f"InverseObjectProperties(<{IRI(l)}> <{IRI(cv)}>)")
        if set(A.STR(A.comp(A.BIT(l),A.BIT(l))))<=set(l):
            ax.append(f"TransitiveObjectProperty(<{IRI(l)}>)")
    nchain=0
    for a in labels:
        for b in labels:
            c=A.STR(A.comp(A.BIT(a),A.BIT(b)))
            if not c or c=="pmoFDseSdfOMP": continue   # universal result carries no information
            ax.append(f"SubObjectPropertyOf(ObjectPropertyChain(<{IRI(a)}> <{IRI(b)}>) <{IRI(c)}>)")
            nchain+=1
    with open("out/aic_axioms.ofn","w") as fh:
        fh.write("Prefix(owl:=<http://www.w3.org/2002/07/owl#>)\n")
        fh.write("Ontology(<http://purl.obolibrary.org/obo/ro/aic.owl>\n")
        fh.write("\n".join("  "+a for a in ax))
        fh.write("\n)\n")
    with open("out/aic_axioms.ofn","a") as fh: pass
    print(f"out/aic_axioms.ofn          : {len(ax)} axioms ({nchain} property chains)")

    # -------- 4. proposed RO patch: bridge developmental relations to the temporal hierarchy
    #
    # NOT asserted on developmentally_preceded_by (RO_0002258), even though the name invites it:
    # developmentally_induced_by (RO_0002256) sits directly beneath it, and induction relates
    # "interacting participants" (its own definition) -- coexisting entities, not ordered ones.
    # Reciprocal induction is real: Uberon asserts metanephric mesenchyme and ureteric bud each
    # developmentally_induced_by the other, which a start-order axiom would render unsatisfiable.
    # So the axiom goes on the two branches where one entity genuinely arises from another.
    RO="http://purl.obolibrary.org/obo/"
    SA=IRI("dfOMP"); SB=RO+"RO_0002089"
    FWD=[("RO_0002254","has developmental contribution from"),
         ("RO_0002285","developmentally replaces")]
    INV=[("RO_0002255","developmentally contributes to")]
    with open("out/ro_temporal_patch.ofn","w") as fh:
        fh.write("Prefix(owl:=<http://www.w3.org/2002/07/owl#>)\n")
        fh.write("Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)\n")
        fh.write("Ontology(<http://purl.obolibrary.org/obo/ro/temporal-patch.owl>\n")
        fh.write(f"  Declaration(ObjectProperty(<{SA}>))\n")
        fh.write(f"  Declaration(ObjectProperty(<{SB}>))\n")
        fh.write(f"  InverseObjectProperties(<{SA}> <{SB}>)\n")
        for rid,rlab in FWD:
            fh.write(f"  Declaration(ObjectProperty(<{RO}{rid}>))\n")
            fh.write(f"  SubObjectPropertyOf(<{RO}{rid}> <{SA}>)\n")
            fh.write(f'  AnnotationAssertion(rdfs:comment <{RO}{rid}> "Y must already exist when X '
                     'arises, so start(X) > start(Y). Allen dfOMP (starts_after) -- NOT preceded_by, '
                     'since Y need not cease when X appears."@en)\n')
        for rid,rlab in INV:
            fh.write(f"  Declaration(ObjectProperty(<{RO}{rid}>))\n")
            fh.write(f"  SubObjectPropertyOf(<{RO}{rid}> <{SB}>)\n")
        fh.write(")\n")
    print(f"out/ro_temporal_patch.ofn   : {len(FWD)+len(INV)} axioms "
          f"(deliberately NOT on developmentally_preceded_by -- see comment)")

    base=[l for l in labels if len(l)==1]
    bb=[(a,b) for a in base for b in base]
    print(f"templates/aic_relations.tsv : {len(labels)} relations "
          f"({sum(1 for l in labels if N[l][2]=='existing')} existing, "
          f"{sum(1 for l in labels if N[l][2]!='existing')} new)")
    print(f"templates/aic_chains.tsv    : {len(rows)} composition entries")
    print(f"  of which base 13x13       : {len(bb)}  "
          f"({sum(1 for a,b in bb if len(A.STR(A.comp(A.BIT(a),A.BIT(b))))==1)} singleton)")
    print(f"  transitive properties     : {sum(1 for l in labels if set(A.STR(A.comp(A.BIT(l),A.BIT(l))))<=set(l))}")
    print(f"  needing collision review  : {sum(1 for l in labels if 'COLLISION' in N[l][2])}")

if __name__=="__main__": main()
