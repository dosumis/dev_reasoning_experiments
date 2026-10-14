"""Generate the error-checking module: per ordered stage pair, you cannot start DURING an
earlier stage and also start DURING-OR-AFTER a later one.

For N stages this is N defined classes of each kind plus C(N,2) disjointness axioms."""
import json, sys
S="http://purl.obolibrary.org/obo/scratch/"
BB=json.load(open("out/ehdaa2.json"))["backbone"]
carn=sorted([(v["lo"],v["label"],c) for c,v in BB.items() if v["exact"]])
ids=[(lab.replace(" ","_"), c) for _,lab,c in carn]
L=[]
L.append('Prefix(:=<%s>)' % S)
L.append('Prefix(obo:=<http://purl.obolibrary.org/obo/>)')
L.append('Ontology(<%sstage-disjointness>' % S)
L.append('  Declaration(ObjectProperty(obo:RO_0002488))')   # existence starts during
L.append('  Declaration(ObjectProperty(obo:RO_0002496))')   # existence starts during or after
L.append('  SubObjectPropertyOf(obo:RO_0002488 obo:RO_0002496)')
for nm,c in ids:
    L.append(f'  Declaration(Class(<{c}>))')
    L.append(f'  Declaration(Class(:During_{nm}))')
    L.append(f'  Declaration(Class(:AtOrAfter_{nm}))')
    L.append(f'  EquivalentClasses(:During_{nm}   ObjectSomeValuesFrom(obo:RO_0002488 <{c}>))')
    L.append(f'  EquivalentClasses(:AtOrAfter_{nm} ObjectSomeValuesFrom(obo:RO_0002496 <{c}>))')
L.append('  DisjointClasses(' + ' '.join(f'<{c}>' for _,c in ids) + ')')
n=0
for i,(ni,_) in enumerate(ids):
    for nj,_ in ids[i+1:]:
        L.append(f'  DisjointClasses(:During_{ni} :AtOrAfter_{nj})'); n+=1
L.append(')')
open("out/stage-disjointness.ofn","w").write("\n".join(L)+"\n")
print(f"  stages: {len(ids)}   disjointness axioms: {n}   total lines: {len(L)}")
