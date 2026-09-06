"""Extract stage structure from an OBO developmental-stage ontology."""
import sys, json
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from collections import defaultdict

OBO = "http://purl.obolibrary.org/obo/"
PART_OF   = URIRef(OBO+"BFO_0000050")
IMM_PREC  = URIRef(OBO+"RO_0002087")   # immediately_preceded_by
PREC      = URIRef(OBO+"BFO_0000062")  # preceded_by

def load(path):
    g = Graph().parse(path)
    label, dep = {}, set()
    for s,_,o in g.triples((None, RDFS.label, None)):
        if str(s).startswith(OBO): label[str(s)] = str(o)
    for s in g.subjects(OWL.deprecated, None): dep.add(str(s))
    rels = defaultdict(list)   # (prop) -> list[(sub,obj)]
    for c in set(g.subjects(RDF.type, OWL.Class)):
        if not str(c).startswith(OBO): continue
        for sup in g.objects(c, RDFS.subClassOf):
            if (sup, RDF.type, OWL.Restriction) in g:
                p = next(g.objects(sup, OWL.onProperty), None)
                v = next(g.objects(sup, OWL.someValuesFrom), None)
                if p is not None and v is not None and str(v).startswith(OBO):
                    rels[str(p)].append((str(c), str(v)))
            elif str(sup).startswith(OBO):
                rels["is_a"].append((str(c), str(sup)))
    return dict(labels=label, deprecated=dep, rels=rels)

if __name__ == "__main__":
    for name in ["hsapdv","mmusdv"]:
        d = load(f"sources/{name}.owl")
        R = d["rels"]
        live = {k for k in d["labels"] if k not in d["deprecated"]}
        print(f"=== {name} ===  live classes: {len(live)}")
        for p,pairs in R.items():
            pn = {"is_a":"is_a", str(PART_OF):"part_of", str(IMM_PREC):"imm_preceded_by",
                  str(PREC):"preceded_by"}.get(p, p)
            print(f"   {pn:18} {len(pairs)}")
        # the immediately-precedes chain = the backbone
        prec = {a:b for a,b in R.get(str(IMM_PREC),[])}
        succ = defaultdict(list)
        for a,b in prec.items(): succ[b].append(a)
        heads = [x for x in prec.values() if x not in prec]
        forks = {k:v for k,v in succ.items() if len(v)>1}
        print(f"   backbone edges: {len(prec)}  chain-heads: {len(set(heads))}  branch points: {len(forks)}")
        json.dump({k:(list(v) if isinstance(v,set) else v) for k,v in d.items() if k!="rels"} |
                  {"rels":{k:v for k,v in R.items()}}, open(f"out/{name}.json","w"))
        print()
