# Toy examples

Three tiny ontologies. Run each with `robot`; each is ~15 lines.

## 01-broken.ofn — why `develops_from ⊑ preceded_by` fails

```
preceded by (BFO:0000062)            domain/range = occurrent
immediate transformation of (RO:0002495)  domain/range = independent continuant
BFO:                                 continuant and occurrent are DISJOINT

SubObjectPropertyOf( RO:0002495  BFO:0000062 )      <- the proposal
```

```sh
robot reason --reasoner HermiT --input 01-broken.ofn --output /dev/null
# ERROR  There are 1 unsatisfiable classes in the ontology.
# ERROR      unsatisfiable: http://ex.org/Liver
```

Not a stylistic objection — anything participating in a transformation becomes unsatisfiable.

## 02-fixed.ofn — the continuant-side relation

RO already has the bridge. `existence starts at end of` (RO:0002583) is defined
`iff α(x) = ω(y)` — Allen **M**, between continuants, and it declares no domain or range
that forces occurrents.

```
SubObjectPropertyOf( RO:0002495  RO:0002583 )
ObjectPropertyAssertion( RO:0002495  liver  hepatic_diverticulum )
```

```sh
robot reason --reasoner HermiT --axiom-generators PropertyAssertion \
  --input 02-fixed.ofn --output -
# ObjectPropertyAssertion(RO:0002583 liver hepatic_diverticulum)
```

Satisfiable, entails the timing, and in **both OWL 2 DL and EL**.

## 03-self-gate.ofn — class-gated property chains

OWL chains cannot be qualified by class: there is no way to say *"R ∘ S ⊑ T, but only when
the middle is a C"*. `ObjectHasSelf` simulates it.

```
HumanScoped ⊑ ∃isHuman.Self
isHuman ∘ develops_from ⊑ human_starts_after
```

```sh
robot reason --reasoner HermiT --axiom-generators PropertyAssertion \
  --input 03-self-gate.ofn --output -
# ObjectPropertyAssertion(human_starts_after liver_h hd_h)     <- human-scoped: fires
#                                                              <- liver_m: does not
```

In OWL 2 EL. **Not** usable on the temporal relations themselves — `ObjectHasSelf` requires a
*simple* property, and 18 of the 29 are transitive while all are chain-implied. Both are
rejected from DL with "Use of non-simple property in ObjectHasSelf restriction".

Untested: whether `relation-graph` implements `ObjectHasSelf`. If it ignores it, the pattern
materialises as nothing — the same failure mode as the GCI-invisibility problem.

## 04-chain.ofn / 05-class-level.ofn — temporal inference you can actually query

`existence starts at end of` is Allen **M**. Composition gives `M ∘ M = P` — if x starts when y
ends and y starts when z ends, x starts *strictly after* z ends. Asserted as a property chain,
that is a real temporal inference an OWL reasoner performs.

### At individual level (04)

```
asserted:  hepatic_diverticulum  M  hepatic_plate
           liver                 M  hepatic_diverticulum
           gall_bladder          M  liver

derived:   liver         starts_strictly_after  hepatic_plate
           gall_bladder  starts_strictly_after  hepatic_diverticulum
```

### At class level (05) — **this is the one that matters**

The same, stated all-some the way Uberon states things:

```
HepaticDiverticulum ⊑ ∃ RO:0002583 . HepaticPlate
Liver               ⊑ ∃ RO:0002583 . HepaticDiverticulum
GallBladder         ⊑ ∃ RO:0002583 . Liver
```

Define the query as a class and let the reasoner classify into it:

```
StartsAfterHepaticPlate  ≡  ∃ starts_strictly_after . HepaticPlate
```

```sh
robot reason --reasoner ELK --input 05-class-level.ofn --output 05-reasoned.owl
robot query --input 05-reasoned.owl --query queries/starts-after.rq /dev/stdout
#   Liver
#   GallBladder
```

**In OWL 2 EL.** So ELK does it, and relation-graph will materialise it.

### Why you need the whole table

With only `M ∘ M ⊑ P` asserted, `Liver` classifies and `GallBladder` does not — one table entry
buys one hop. Adding `P ∘ M ⊑ P` brings `GallBladder` in. The 169-entry composition table is
what makes the closure complete, which is the point of
[templates/aic_chains.tsv](../templates/aic_chains.tsv).

### Asking why

```sh
robot explain --input 05-class-level.ofn --reasoner ELK \
  --prefix "ex: http://ex.org/" \
  --axiom "ex:GallBladder SubClassOf ex:StartsAfterHepaticPlate" --explanation /dev/stdout
```

prints the full derivation — the three asserted restrictions, both chain axioms, and the
defined class.

### What these queries cannot do

- **Narrow a relation from two sources.** No object-property intersection, so two paths giving
  `dfO` and `osd` cannot be combined to `d`.
- **Reason over stage numbers.** EL has no arithmetic; "what existed at day 26" is not a DL query.
- **Conclude by elimination** — "it must be `M`, because everything else is inconsistent".
- **Carry the full table.** 132 of the 638 chains are cyclic and rejected from OWL 2 DL
  ([../README.md](../README.md) §5).

Those are the constraint-solver's job. What DL gives you is the materialised forward closure,
which is a large part of the value and the part that integrates with Uberon.
