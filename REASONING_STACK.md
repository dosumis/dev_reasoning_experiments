# Compound reasoning: which engine does what

Measured answers to "what should actually run this?" — because no single engine does all of it,
and the obvious choices are not the right ones.

---

## 1. The measurements

### ABox property-chain materialisation

The individual-level design ([examples/10-individuals.ofn](examples/10-individuals.ofn)) needs
property chains applied to **individuals**. Not all EL reasoners do this.

| engine | derived on the toy | 500 individuals | 5,000 |
|---|---|---|---|
| **ELK** | **3** — i.e. nothing | — | — |
| **Whelk** | **9** ✓ | 3.46 s | **245 s** |
| **HermiT** | **9** ✓ | 1.17 s | **5.46 s** |

**The limitation was ELK, not the EL profile.** EL supports ABox chains; ELK is a TBox
classifier and does not implement them. Whelk does.

But Whelk scales badly on this workload — **45× slower than HermiT at 5,000**, which is the
reverse of the usual EL-vs-DL story and worth knowing before building on it.

### Closing a class is what actually costs

```
500 individuals, chains only            0.59 s
500 individuals + ObjectOneOf closure  10.67 s
```

Not `DifferentIndividuals` (10.10 s vs 9.66 s without it) — the enumeration itself, in a tableau.

### Profiles

| | EL | RL | DL |
|---|---|---|---|
| class-level axioms (08, 09) | ✓ | **✗** | ✓ |
| **individual-level facts (10)** | ✓ | **✓** | ✓ |
| closed class (12) | ✗ | ✗ | ✓ |

RL rejects the class-level ones for a structural reason: **`∃R.C` is banned in superclass
position**, which is exactly how OBO states everything (`C ⊑ ∃R.D`). RL can never carry the
Uberon pattern.

The **ABox layer is RL-clean**, which is the opening for rule engines.

`ObjectOneOf` in EL is permitted with **exactly one** individual. `ObjectOneOf(:a)` ✓,
`ObjectOneOf(:a :b :c)` ✗ — and EL has no union, so a closed class cannot be built from
singletons either.

---

## 2. OWL + SPARQL

The loop, which [`Uberon_HDCA_stage_axioms`][repo] already runs in miniature with `expand.ru`:

```
  ┌─ reason (ELK / relation-graph)  → materialise the class-level closure
  │
  ├─ SPARQL UPDATE over the artefact → derive what OWL cannot
  │     · closed-world universals (the promotion check)
  │     · arithmetic over stage bounds
  │     · narrowing a label from two sources
  │
  └─ feed the result back, re-reason ─┘   until fixpoint
```

The key precedent from that repo is that the update runs **over the artefact**, not as another
output of the generator — because it has to work on GCIs nobody here wrote.

**Where it fits best: the promotion check.** "Does every member of this closed set satisfy P?"
is a closed-world universal — the one thing DL does worst, needing nominals to simulate closure
and then paying tableau costs for them. In SPARQL it is one negated subgraph:

```sparql
ASK { FILTER NOT EXISTS {
        ?s a :Somite .
        FILTER NOT EXISTS { ?s :existence_starts_during_or_after :CS09 } } }
```

10 s in HermiT at 500 individuals; a single pass here.

**Limitation**: SPARQL has no recursion beyond property paths, so iterated CONSTRUCT to a
fixpoint has to be driven externally. Fine for a build step, awkward as a reasoner.

[repo]: https://github.com/dosumis/Uberon_HDCA_stage_axioms

---

## 3. OWL + Datalog (Soufflé)

This is where the comparison becomes lopsided. [datalog/allen.dl](datalog/allen.dl).

### The composition table becomes *data*

```
.decl comp(R1:symbol, R2:symbol, R3:symbol)      // the 169-entry table, loaded as facts
.decl rel(X:symbol, Y:symbol, R:symbol)

rel(X, Z, R3) :- rel(X, Y, R1), rel(Y, Z, R2), comp(R1, R2, R3).
```

| | |
|---|---|
| OWL property chains for the same | **842** |
| of which rejected by OWL 2 regularity | **132** |
| Datalog rules | **1** (+1 for converse) |

The regularity wall simply does not exist — Datalog has no acyclicity condition on rules, so
the cyclic entries that OWL rejects are ordinary facts here.

Verified on the liver chain: three asserted `M` relations, fixpoint derives three more including
`gall_bladder P hepatic_plate` — which OWL needed *two separately chosen* chain axioms to reach,
and which falls out here with none.

### Narrowing, which OWL cannot do at all

No object-property intersection exists in OWL, so two paths yielding `dfO` and `osd` can never
be combined to `d`. Datalog is monotonic, so you encode the *complement*:

```
impossible(X,Z,R) :- rel(X,Y,_), rel(Y,Z,_), allen(R), !pathAllows(X,Y,Z,R).
possible(X,Y,R)   :- rel(X,Y,R), !impossible(X,Y,R).
inconsistent(X,Y) :- rel(X,Y,_), !anyPossible(X,Y).
```

Stratified negation, which Soufflé supports. The empty label — an inconsistency — becomes a
derived fact you can *query for* rather than a global failure that stops all reasoning.

**Honest limit**: this is one round of narrowing, not full path consistency. Path consistency
iterates narrowing to a fixpoint, and because each round depends on the previous round's
*negation*, the strata do not simply stack. Expressible with care; ASP (clingo) handles the
non-monotonicity more naturally.

### Closed-world promotion is native

```
counterexample(C,S) :- member(C,I), stage(S), !rel(I,S,"sdoa").
promote(C,S)        :- stage(S), member(C,_), !counterexample(C,S).
```

No nominals, no enumeration cost. This is the §4 promotion rule of
[IDEALISED_INDIVIDUALS.md](IDEALISED_INDIVIDUALS.md) stated directly.

---

## 4. Proposed division of labour

| layer | engine | why |
|---|---|---|
| class-level closure, materialisation, Uberon integration | **ELK / relation-graph** | EL only; the `C ⊑ ∃R.D` pattern lives here and RL cannot hold it |
| individual-level chains | **Soufflé** (or HermiT if staying in OWL) | the ABox layer is RL-clean; Whelk works but scales poorly |
| composition, narrowing, inconsistency detection | **Soufflé / ASP** | 1 rule vs 842 chains; no regularity wall; negation available |
| closed-world promotion | **SPARQL or Soufflé** | a universal over a closed set — DL's worst case, their native case |
| emitting promoted axioms back to OWL | ROBOT template | so the result re-enters Uberon as ordinary class axioms |

Two reasoner passes, not one, and the heavy lifting outside OWL.

---

## 5. What this does not settle

**Whelk and RL.** Whelk is documented as an OWL **EL** reasoner and I found no evidence it
covers RL. My attempts to test it empirically were inconclusive — I built test ontologies that
did not actually carry the entailment, so all three engines returned nothing and the test
measured my test, not the reasoners. The solid finding is the ABox-chain one above.

**Soufflé is not installed here**, so the `.dl` is written and its logic validated by simulating
the fixpoint in Python against the verified composition table — not by running Soufflé itself.

**Konclude** was not tried and is the obvious missing data point: it is substantially faster than
HermiT on OWL 2 DL and would be the right test before concluding that closed-world promotion is
too expensive to do in OWL.
