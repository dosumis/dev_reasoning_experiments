# A composition-closed Allen extension for RO

Infrastructure for temporal reasoning over developmental stages, anatomical existence
windows, and process timing — grounded in Allen's Interval Calculus (AIC) and aligned
with the OBO Relation Ontology.

Everything here is **derived and machine-verified**, never transcribed. The composition
table is computed by enumerating endpoint orderings; the converse function is checked
against interval semantics rather than copied from a published table.

> ### 📄 [USER_STORIES.md](USER_STORIES.md) — what this is *for*
>
> A survey of the temporal content actually present in HsapDv, MmusDv, Uberon, GO, HP and MP;
> where it falls short; and seven user stories worked against it — each recording what
> machinery it genuinely requires. Read that first if you want to know which parts of this
> infrastructure earn their keep.
>
> Headline findings: **where stage endpoints are numerically anchored, no qualitative reasoning
> is needed at all** — the Allen relation follows from comparing four numbers. AIC is
> irreplaceable in three of the seven stories, all curation- or integration-facing. And three
> axioms turning on `starts_after` — a relation current RO cannot express, but the extension
> below supplies — give **1,558 Uberon assertions** temporal semantics they currently lack.

**[RO_REPORT.md](RO_REPORT.md)** collects the findings that are actionable for RO maintainers:
a missing converse relation, three axioms that would give 1,558 Uberon assertions temporal
semantics, a misplaced relation in the developmental branch, and two chains referencing
obsolete properties.

Two further reports: **[DISMECH_REPORT.md](DISMECH_REPORT.md)** surveys dismech's 2,480 disease
pathographs — ~33,500 causal edges needing the same axiom, and 46 causal cycles that turn out to
be real vicious cycles. **[HP_ONSET_PROPOSAL.md](HP_ONSET_PROPOSAL.md)** shows that HP's onset
vocabulary already resolves to a perfect interval partition of the human lifespan, and proposes
the axioms that would make it computable.

Provenance for every source ontology — version IRIs, release dates, checksums, and which
results depend on which files — is in [sources/SOURCES.md](sources/SOURCES.md).

---

## 1. The 13 Allen relations

Every pair of proper intervals stands in exactly one of thirteen relations. Reading
`X R Y`, with `X` drawn above `Y`:

```
  p   X precedes Y                 XXXXX                    e(X) < s(Y)
      (strictly, with a gap)                 YYYYY

  m   X meets Y                    XXXXX                    e(X) = s(Y)
                                        YYYYY

  o   X overlaps Y                 XXXXX                    s(X)<s(Y)<e(X)<e(Y)
                                      YYYYY

  F   X finished-by Y              XXXXXXXXX                s(X)<s(Y), e(X)=e(Y)
                                       YYYY

  D   X contains Y                 XXXXXXXXX                s(X)<s(Y), e(Y)<e(X)
                                     YYYY

  s   X starts Y                   XXXX                     s(X)=s(Y), e(X)<e(Y)
                                   YYYYYYYYY

  e   X equals Y                   XXXXXXXXX                s(X)=s(Y), e(X)=e(Y)
                                   YYYYYYYYY

  S   X started-by Y               XXXXXXXXX                s(X)=s(Y), e(Y)<e(X)
                                   YYYY

  d   X during Y                     XXXX                   s(Y)<s(X), e(X)<e(Y)
                                   YYYYYYYYY

  f   X finishes Y                      XXXX                s(Y)<s(X), e(X)=e(Y)
                                   YYYYYYYYY

  O   X overlapped-by Y                XXXXX                s(Y)<s(X)<e(Y)<e(X)
                                   YYYYY

  M   X met-by Y                        XXXXX               s(X) = e(Y)
                                   YYYYY

  P   X preceded-by Y                        XXXXX          s(X) > e(Y)
                                   YYYYY
```

Six converse pairs (`p/P`, `m/M`, `o/O`, `F/f`, `D/d`, `s/S`) plus self-converse `e`.

A **label** is any set of these atoms, written as a string: `dfO` means "during, finishes,
or overlapped-by" — i.e. the relation is one of those three, but which is not yet known.
Labels are how partial knowledge is represented.

---

## 2. Composition

If `X R₁ Y` and `Y R₂ Z`, then `X (R₁ ∘ R₂) Z`. Composition is generally **disjunctive**:

```
  d ∘ p  =  p           X during Y, Y before Z    ->  X strictly before Z
  m ∘ m  =  p           X meets Y, Y meets Z      ->  X strictly before Z
  M ∘ M  =  P           two steps back a stage chain -> strictly preceded by
  o ∘ o  =  pmo         three possibilities remain
  p ∘ P  =  (all 13)    no information
```

Measured over the 13×13 table:

| | |
|---|---|
| entries total | 169 |
| **singleton results** (expressible as an OWL property chain) | **97 (57%)** |
| disjunctive results | 72 |
| distinct result labels | 27 |

Result-size distribution: `{1: 97, 3: 42, 5: 24, 9: 3, 13: 3}`

---

## 3. The 29-relation subalgebra

> **Prior art.** This set is **not novel** — it is the published result of Batsakis,
> Petrakis, Tachmazidis & Antoniou, *Temporal Representation and Reasoning in OWL 2*,
> Semantic Web Journal (2016), which derives the same 29 by the same closure method and
> reports 983 OWL axioms + SWRL rules to implement it. Code:
> [github.com/sbatsakis/TemporalRepresentations](https://github.com/sbatsakis/TemporalRepresentations).
> The computation below independently reproduces and verifies it. What appears to be new
> here is the mechanical audit of RO's existing temporal axioms (§4) and the RO alignment.
>
> Note also that 29 is the **minimal** tractable set containing the basic relations. The
> *maximal* one is ORD-Horn (868 relations, Nebel & Bürckert), impractical to implement
> as rules. Full Allen satisfiability is NP-complete; ORD-Horn is the maximal tractable
> subclass on which path consistency decides satisfiability in cubic time.

Close the 13 atoms under **composition, converse and intersection**. The result does not
blow up:

| Closure under | Distinct relations |
|---|---|
| composition only | **29** |
| + converse | **29** |
| + converse + intersection | **29** |

Verified exhaustively: zero violations across all 29×29 pairs. The 29-element set is a
genuine subalgebra of Allen's algebra.

What escapes it is **union** — and union never arises from inference. It enters only when
someone *asserts* an arbitrary disjunction (`{p,P}`: "disjoint, but order unknown"). So a
vocabulary of 29 named relations is closed under every operation the reasoner performs.

Every one of the 29 is exactly characterised by a conjunction of endpoint constraints,
which is what makes the whole thing implementable — and, as it turns out, is already RO's
implicit naming principle (§5).

```
  13 atoms
  16 disjunctions:  DSO  Fef  OMP  dfO  oFD  osd  pmo  seS
                    DSOMP  dfOMP  pmoFD  pmosd
                    oFDseSdfO   oFDseSdfOMP   pmoFDseSdfO   pmoFDseSdfOMP
```

**RO already has 11 of the 29.** This repo supplies the other 18.

---

## 4. What OWL can and cannot do

This is the boundary that determines the architecture, and it is about **operations, not
vocabulary size**:

| Operation | Needed for | In OWL? |
|---|---|---|
| composition | forward chaining | ⚠️ property chains — but see regularity, below |
| converse | symmetry | ✅ `owl:inverseOf` |
| **intersection** | narrowing a label from two sources | ❌ no object-property intersection constructor |
| **elimination** | concluding `X` because alternatives are inconsistent | ❌ not DL inference |

### The regularity wall (measured)

Naming all 29 relations makes every composition result *nameable*, so the whole table can be
written down as 638 property chains. **But the result is not valid OWL 2** — and not for
disjunction reasons:

```
robot validate-profile --profile DL   ->  NOT in profile, 132 violations
robot validate-profile --profile RL   ->  NOT in profile, 132 violations
robot validate-profile --profile EL   ->  NOT in profile, 132 violations
                                          all of them "use of property in chain causes cycle"
```

OWL 2 DL imposes a **regularity condition**: there must be a strict partial order `≺` on
object properties such that every chain `R₁ ∘ R₂ ⊑ R₃` has `R₁ ≺ R₃` and `R₂ ≺ R₃` (modulo
the permitted `R ∘ S ⊑ R` forms). Allen composition does not admit such an order — the
precedence graph induced by the full table contains **20 cycles** (e.g. `Fef → M → Fef`),
so 108 distinct chains are irreparably cyclic.

This is a stronger limit than the well-known disjunction problem, and it holds *however many
relations you name*. It cannot be engineered around: it is a consequence of Allen composition
being genuinely circular, and of OWL 2's decidability requirements.

**Consequence for the design.** The OWL layer can carry a large *regular subset* of the table
(~506 of 638 chains) plus all inverses and the 18 transitivity axioms — enough to be genuinely
useful for materialisation — but it can never be complete even for forward chaining.

### A second, independent wall: transitivity + disjointness

Consistency checking works by declaring the basic relations **pairwise disjoint**: if
propagation derives two disjoint relations for the same pair, the ontology is inconsistent.
But OWL 2 forbids combining transitivity with disjointness (or asymmetry) on a property —
the combination can lead to undecidability. This artifact declares **18 transitive
properties**, so materialisation and inconsistency detection cannot coexist in OWL 2 DL,
*regardless of regularity*.

Underneath both walls: path consistency requires composition **+ intersection + role
complement**, and that combination is provably undecidable.

### Does SWRL escape this? Yes — at a cost

**DL-safe rules** (Motik, Sattler & Studer) bind every variable to named individuals in the
ABox. Rules are then not role inclusion axioms, so regularity does not apply and cyclic
composition is fine; decidability comes from the finite domain. Since our intervals are
named individuals anyway, this costs nothing semantically.

It costs a great deal in performance. Measured by Batsakis et al. (HermiT/Pellet, 2.4 GHz):

| Approach | Scale | Time |
|---|---|---|
| Allen intervals + SWRL (HermiT) | 100 intervals | 2.0 s |
| " | 500 intervals | 149 s |
| Qualitative points + SWRL (HermiT) | 500 points | 279 s |
| **OWL role inclusion axioms only** (no SWRL) + Pellet | **100,000 points** | **< 3 s** |
| **CHRONOS** standalone path-consistency reasoner | **10,000 Allen relations** | **< 10 s** |

Path consistency is O(n⁵) worst case, sound and complete. Dropping SWRL and consistency
checking buys roughly three orders of magnitude.

### Deployment

| Layer | Engine | Scale | Gives |
|---|---|---|---|
| Bulk materialisation | relation-graph, regular subset | 10⁵+ | pre-reasoned graph; no consistency checking |
| Query-time reasoning | dedicated path-consistency solver | 10⁴ relations < 10 s | completeness, inconsistency detection, entailed-vs-possible |
| Optional interchange | SWRL/OWL, 983 axioms | ~100–500 intervals | standards compliance, Protégé, OBO tooling |

SWRL sits in the worst spot — slower than a dedicated solver, far less scalable than plain
OWL axioms. **Datalog engines (RDFox, Soufflé)** occupy the same expressivity class as
DL-safe rules but are engineered for materialisation at scale, and are the obvious
substitute.

**Where none of this is needed:** for intervals with known numeric endpoints, all relations
between them are computed directly from the endpoints, guaranteed consistent, no reasoning
required. That covers 154 of HsapDv's 255 stages. Point algebra needs 20 axioms against 983
for intervals. The heavy apparatus is earned only where endpoints are genuinely unknown —
Uberon existence windows, atlas-derived intervals, disease progression.

So the design is two layers sharing one vocabulary:

- **OWL/RO layer** — the 29 relations, 169 composition chains, materialised by
  [relation-graph](https://github.com/INCATools/relation-graph). Complete for forward
  chaining. Produces the pre-reasoned graph.
- **Constraint solver** — live, per-query, does intersection and elimination. Distinguishes
  *entailed* (only one label survives) from *possible* (label is among the survivors).

Because the 29 are closed under all three operations, the two layers translate between each
other losslessly.

### Why RO's current relations lose information

RO's `precedes` (`pm`) and `preceded_by` (`PM`) **are not in the 29** — they lie outside the
entire subalgebra the atoms generate. They can never be the tightest conclusion of any
inference, so every step through them discards information:

```
  happens_during o precedes    true: p    RO must assert: pm
  ends_during    o precedes    true: p    RO must assert: pm
  happens_during o preceded_by true: P    RO must assert: PM
  starts_during  o preceded_by true: P    RO must assert: PM
```

Four of RO's six temporal chains are lossy this way — sound, but weaker than derivable.
RO has `pm` (`precedes`) and `m` (`immediately_precedes`) but no term for `p` alone, and
OWL has no property subtraction. Concretely, walking two or more stages back along an
HsapDv `immediately_preceded_by` chain gives `P` (strictly preceded by), but RO can only
conclude `PM`.

RO's axioms are otherwise sound: all 10 transitivity declarations match Allen exactly,
including the four non-obvious negatives.

---

## 5. Naming

The hard part. Allen's own names are wrong for biology, and RO's existing names encode a
decade of curator judgement that shouldn't be discarded.

### The principle RO already uses

RO's compound relations name **the endpoint invariant shared by all disjuncts**:

| RO relation | Allen | invariant |
|---|---|---|
| `starts during` | `dfO` | `start(X)` strictly inside Y |
| `ends during` | `osd` | `end(X)` strictly inside Y |
| `starts before` | `pmoFD` | `start(X) < start(Y)` |
| `ends after` | `DSOMP` | `end(X) > end(Y)` |

That principle generalises to all 29, so naming is systematic rather than ad hoc. Each
generated definition states the invariant explicitly.

### Three rules

1. **Never reuse an RO label with different semantics.** `precedes` is taken (`= pm`), so
   the atom `p` becomes `strictly precedes`.
2. **Prefer endpoint language over Allen jargon where jargon misleads.** Allen's `overlaps`
   is *asymmetric*; colloquial "overlaps" is symmetric. Never use the bare word. Likewise
   `starts`/`finishes` read as causal to biologists — hence
   `starts with and ends before` rather than `starts`.
3. **Follow existing RO precedent for disjunctions.** `dfOMP` and `pmosd` are named
   `starts during or after` / `ends during or before`, matching RO's `existence_*` family
   (RO:0002496 / RO:0002497).

### Four collisions needing curator review

Flagged in the template `Status` column — these are genuine judgement calls, not oversights:

| Allen | proposed | conflict |
|---|---|---|
| `e` | `temporally coincides with` | RO:0002082 `simultaneous with`, RO:0002008 `coincident with` — reuse one? |
| `seS` | `starts with` | RO:0002224 `starts with` may be **mereological** (`Fe`, not `seS`) |
| `Fef` | `ends with` | RO:0002230 `ends with` — same question |
| `oFDseSdfO` | `temporally overlaps` | RO:0002131 `overlaps` is mereological — must **not** reuse |

The mereological/temporal distinction is the crux: "Y is the final part of X" and "X and Y
end at the same time" are different claims that English collapses.

---

## 6. Test cases from real data

`tests/uberon_cases.py` runs against Uberon's 80 `existence_*` assertions linking
anatomical structures to life-cycle stages.

**Case set 1 — intersection.** Six structures carry two assertions about the same
(structure, stage) pair. Intersecting the labels yields a strictly tighter relation:

```
  conceptus vs embryo stage
      asserted : existence starts with        (seS)
      asserted : existence ends with          (Fef)
      DERIVED  : temporally coincides with    (e)     <- seS ∩ Fef = {e}

  morula vs cleavage stage
      asserted : existence starts during      (dfO)
      asserted : existence ends during        (osd)
      DERIVED  : happens during               (d)     <- dfO ∩ osd = {d}
```

The `morula` case is the sharpest: RO *has* a relation meaning exactly this
(`existence starts and ends during`, RO:0002491), yet cannot derive it from the two
assertions that entail it. **No OWL reasoner reaches any of these conclusions** — property
chains compose across a middle term, they cannot intersect two labels on the same pair.

**Case set 2 — composition.** 17 structure-pairs acquire a derived relation through a
shared stage, with nothing asserted between them.

---

## 7. Layout

```
sources/     owl-time.ttl, ro.owl, uberon.owl, hsapdv.owl, mmusdv.owl
src/
  fast_allen.py    bitmask algebra; base table derived by endpoint enumeration, cached
  allen.py         readable reference implementation
  audit_ro.py      mechanical audit of RO's temporal axioms
  generate.py      emits the ROBOT templates
  extract.py       stage structure from a DV ontology
  endpoints.py     numeric bounds parsed from HsapDv definitions
  propagate.py     STP-style bounds propagation
  check.py         numbers vs asserted structure
templates/
  aic_relations.tsv   ROBOT template: 29 relations, labels + textual definitions
  aic_chains.tsv      841 composition entries, human-readable (169 over the base 13)
out/
  aic_axioms.ofn      697 logical axioms: inverses, transitivity, 638 property chains
tests/
  uberon_cases.py     reasoning cases from Uberon existence_* assertions
```

Regenerate: `python src/generate.py` · Audit RO: `python src/audit_ro.py` ·
Test: `python tests/uberon_cases.py`

Build the OWL artifact:

```sh
robot template --template templates/aic_relations.tsv \
      --prefix "AIC: http://purl.obolibrary.org/obo/AIC_" --output out/aic_terms.owl
robot merge --input out/aic_terms.owl --input out/aic_axioms.ofn --output out/aic.owl
```

Note that ROBOT templates cannot express inverse properties or property chains — the `AI`
keyword emits an *annotation*, and `P` emits a `SubObjectPropertyOf`. Both are wrong. Hence
the separate functional-syntax file for logical axioms.

---

## 8. Status and open questions

Validated against HsapDv: the RO→Allen mapping holds on **263/263 asserted relations**
(122 `part_of` containments, 141 `immediately_preceded_by` exact meetings), zero violations.

Open:

- The four naming collisions in §5.
- IRI allocation — `AIC:000000n` is a placeholder pending RO ID range assignment.
- `starts_during o obsolete preceded_by -> starts_before` in current RO references a
  **deprecated** property. Probably a casualty of an obsoletion that missed the chain;
  needs confirmation before reporting as a defect.
- HsapDv's precedence structure is 14 chains with 3 branch points, not one line —
  separate sequences per granularity (Carnegie, week, LMP month, year, decade) linked by
  `part_of`. Multi-granularity handling is not yet in the propagation code.
- HsapDv mixes reference frames (post-fertilization, LMP, post-birth). OWL-Time's
  `time:TRS` is the intended fix; not yet modelled.
- **Bug:** `propagate.py` can produce degenerate intervals with `start == end`. Allen is
  undefined on these (they are not *proper* intervals), and `fast_allen._rel` correctly
  asserts. Needs a guard plus a decision on what a zero-width stage means.
- Whether to ship the regular subset as the RO contribution (valid OWL 2, materialises,
  incomplete by a documented margin), the full table as the solver specification, or both.

---

## 9. References

1. Allen, J.F. (1983). Maintaining Knowledge about Temporal Intervals. *CACM* 26(11):832–843.
   The composition table is Fig. 4.
2. Batsakis, S., Petrakis, E.G.M., Tachmazidis, I., Antoniou, G. (2016). Temporal
   Representation and Reasoning in OWL 2. *Semantic Web Journal*. — derives the same 29
   relations; 983 axioms/rules; the scaling measurements quoted in §4.
   Code: <https://github.com/sbatsakis/TemporalRepresentations>
3. Nebel, B., Bürckert, H.-J. (1995). Reasoning about Temporal Relations: A Maximal
   Tractable Subclass of Allen's Interval Algebra. *JACM* 42(1). — ORD-Horn, 868 relations.
4. Krokhin, A., Jeavons, P., Jonsson, P. (2003). Reasoning about Temporal Relations: The
   Tractable Subalgebras of Allen's Interval Algebra. *JACM* 50(5). — exactly 18 maximal
   tractable subalgebras.
5. Motik, B., Sattler, U., Studer, R. (2005). Query Answering for OWL-DL with Rules.
   *J. Web Semantics* 3(1). — DL-safe rules.
6. W3C OWL-Time: <https://www.w3.org/TR/owl-time/> — note it declares no property chains,
   for the reasons in §4.
