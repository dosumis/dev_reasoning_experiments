# Toy examples: bridging continuants to temporal relations

> **Read 08 first** if you want the answer. 01 and 02 record *failed* attempts and are kept
> because they prove why the obvious routes do not work. [archive/](archive/) holds a route that
> works but costs more than it needs to.
>
> | | |
> |---|---|
> | **08** | **the design that works** — three typed families + property chains |
> | 08a | DOS's original, before the chains were added |
> | 09 | error checking via class-level disjointness |
> | 10–12 | the same with individuals; 12 adds closed-world promotion |
> | 01, 02 | why subsuming continuant relations under occurrent ones fails |
> | 03 | `ObjectHasSelf` as a class gate — orthogonal capability |
> | 04, 05 | composition, and why the whole table matters |

Seven small runnable ontologies working through one problem — **`develops_from` relates
continuants, Allen relations relate occurrents, and BFO declares the two disjoint.**

The first two record failed attempts, because both are instructive and the second one was mine.

---

## 01-broken.ofn — the obvious attempt

```
preceded by (BFO:0000062)                  domain/range = occurrent
immediate transformation of (RO:0002495)   domain/range = independent continuant

SubObjectPropertyOf( RO:0002495  BFO:0000062 )
```

```
ERROR  There are 1 unsatisfiable classes: http://ex.org/Liver
```

Fatal, not stylistic. Anything participating in a transformation collapses to `owl:Nothing`.

## 02-also-broken.ofn — the `existence_*` family does **not** rescue it

`existence starts at end of` (RO:0002583) is defined *"iff α(x) = ω(y)"* — Allen **M** — and
declares no domain or range of its own. That looks like a continuant-to-continuant bridge.

**It is not.** The whole family inherits from
`relation between physical entity and a process or stage` (RO:0002581):

```
domain = independent continuant        range = OCCURRENT
```

So `RO:0002495 ⊑ RO:0002583` forces the *range* — a continuant — to be an occurrent. Same error,
one level further out:

```
ERROR  There are 1 unsatisfiable classes: http://ex.org/Liver
```

**Check inherited domain/range, not just declared.** The family is correctly
continuant→(process or stage) — which is exactly how EHDAA2 uses it, structure → Carnegie
stage. It is not a bridge between two structures.

## 03-self-gate.ofn — `ObjectHasSelf` as a class gate

OWL chains cannot be qualified by class. The Self marker simulates it:

```
HumanScoped ⊑ ∃isHuman.Self
isHuman ∘ develops_from ⊑ human_starts_after
```

```
ObjectPropertyAssertion( human_starts_after  liver_h  hd_h )   ← human-scoped: fires
                                                                ← liver_m:      does not
```

In OWL 2 EL. **Not** usable on the temporal relations themselves: `ObjectHasSelf` requires a
*simple* property, and 18 of the 29 are transitive while all are chain-implied. Both rejected
from DL with *"Use of non-simple property in ObjectHasSelf restriction"*.

This does **not** solve the continuant/occurrent problem — it is an orthogonal capability.

## 04-chain.ofn / 05-class-level.ofn — composition, and why the table matters

> `:starts_at_end_of` here is a **locally declared** property. RO:0002583 cannot play this role
> (see 02). The point being made is about composition, not about which relation to use.

`M ∘ M = P`: if x starts when y ends and y starts when z ends, x starts strictly after z ends.

**Individual level (04)** — derived, never asserted:

```
liver         starts_strictly_after  hepatic_plate
gall_bladder  starts_strictly_after  hepatic_diverticulum
```

**Class level (05)** — stated all-some, the way Uberon states things:

```
HepaticDiverticulum ⊑ ∃ starts_at_end_of . HepaticPlate
Liver               ⊑ ∃ starts_at_end_of . HepaticDiverticulum
GallBladder         ⊑ ∃ starts_at_end_of . Liver

StartsAfterHepaticPlate ≡ ∃ starts_strictly_after . HepaticPlate
```

```sh
robot reason --reasoner ELK --input 05-class-level.ofn --output 05-reasoned.owl
robot query --input 05-reasoned.owl --query queries/starts-after.rq /dev/stdout
#   Liver
#   GallBladder
```

With only `M ∘ M ⊑ P` asserted, `Liver` classifies and `GallBladder` does not — **one table
entry buys one hop**. Adding `P ∘ M ⊑ P` brings it in. That is why the 169-entry table matters
rather than a few hand-picked chains.

`robot explain` prints the full derivation, which curators will want.

---

## 08-develops-from-timing.ofn — **the right answer**

Due to DOS. No reification, no new primitive, no category error: keep **three families, each
internally type-consistent**, and let property chains do the crossing.

```
C:C   exists_after, exists_immediately_after              continuant → continuant
O:O   preceded_by, immediately_preceded_by                occurrent  → occurrent   (the stage series)
C:O   existence_starts_during, ..._during_or_after        continuant → occurrent   (already in RO)
```

A developmental relation carries the **C:C** timing relation as a superproperty — both sides
continuant, so nothing breaks:

```
transformation_of  ⊑  develops_directly_from
transformation_of  ⊑  exists_immediately_after
```

Then two chains, whose type arithmetic works out on its own:

```
exists_after            ∘ existence_starts_during  ⊑  existence_starts_during_or_after
   C:C                      C:O                   =   C:O

existence_starts_during ∘ preceded_by              ⊑  existence_starts_during_or_after
   C:O                      O:O                   =   C:O
```

### What it derives

Asserted about `liver`: **only** `liver transformation_of liver_bud`. Nothing about stages.

ELK derives `liver ⊑ existence_starts_during_or_after some CS11`, via:

```
liver              ⊑ transformation_of some liver_bud
  transformation_of ⊑ exists_immediately_after ⊑ exists_after  (transitive)
liver_bud          ⊑ transformation_of some liver_diverticulum
liver_diverticulum ⊑ existence_starts_during some CS11
exists_after ∘ existence_starts_during ⊑ existence_starts_during_or_after
```

The timing reaches `liver` from a stage anchor **two developmental steps away**.

It also derives the general fact `AfterLiverDiverticulum ⊑ StartsDuringOrAfterCS11` — anything
existing after the liver diverticulum starts during or after CS11.

**In OWL 2 EL.** Ablation confirms both chains do distinct work: drop the C:C one and `liver`
stops classifying; `liver_bud` still reaches CS11 through the C:O ∘ O:O route.

### Why this beats everything above

| | |
|---|---|
| 01 | subsume C:C under O:O → unsatisfiable |
| 02 | subsume C:C under the C:O family → unsatisfiable (inherited range) |
| 06/07 | reify the temporal extent → works, but needs a new primitive relation |
| **08** | **three typed families + chains → works, needs no new primitive** |

The mistake in 01/02 was trying to make one relation span both categories. The mistake in 06/07
was reaching for a new entity to span them. Neither is necessary: keep the families separate and
let composition cross between them.

---

## archive/06-reified.ofn, archive/07-reified-class.ofn — a workable but heavier alternative

*Moved to [archive/](archive/) — superseded by 08.*

Relate each continuant to its **temporal region**, and do the temporal reasoning there.
`temporal region ⊑ occurrent` in BFO, so BFO's own `preceded_by` applies between regions with
no category error at all.

```
has_temporal_extent   domain = continuant    range = temporal region     ← ONE new relation
extent_of             domain = temporal region  range = continuant

has_temporal_extent ∘ BFO:preceded_by ∘ extent_of  ⊑  starts_after_c
```

**06 (individuals)** — consistent alone and when merged with BFO plus RO's `BFO:0000062`
domain/range axioms.

**07 (classes)** — `Liver ⊑ ∃has_temporal_extent.TE_Liver`, `TE_Liver ⊑ ∃preceded_by.TE_HD`,
`TE_HD ⊑ ∃extent_of.HepaticDiverticulum`, and ELK classifies:

```
Liver  ⊑  StartsAfterHD
```

**In OWL 2 EL** — so relation-graph can materialise it.

One detail that matters: declaring `extent_of` as `InverseObjectProperties` of
`has_temporal_extent` pushes the ontology out of EL (EL has no inverses). Asserting `extent_of`
directly instead keeps it in EL with the same entailment. Confirmed identical under HermiT.

### What this costs

Neither BFO nor RO provides a continuant→temporal-region relation — checked both; zero
properties with a temporal-region range. So this needs **one genuinely new property**, plus its
converse asserted rather than declared, plus the bridging chain per temporal relation wanted.

**Superseded by 08**, which needs no new primitive. Kept because the reification is a real option
if you ever want Allen relations stated directly between temporal regions rather than carried as
superproperties of developmental relations.

---

## What none of this can do

- **Narrow a relation from two sources** — no object-property intersection, so `dfO` and `osd`
  on the same pair cannot combine to `d`.
- **Arithmetic over stages** — "what existed at day 26" is not a DL query.
- **Conclude by elimination.**
- **Carry the full table** — 132 of 638 chains are cyclic and rejected from OWL 2 DL
  ([../README.md](../README.md) §5).

Those remain the constraint solver's job.

---

## 09-error-checking.ofn — catching errors as OWL inconsistencies

### What you cannot do

Property-level constraints all require a **simple** property, and transitivity makes a property
non-simple. All three are rejected from OWL 2 DL:

```
DisjointObjectProperties(exists_after exists_before)   REJECTED  "non-simple property in an axiom"
AsymmetricObjectProperty(exists_after)                 REJECTED  "non-simple property in asymmetric..."
IrreflexiveObjectProperty(exists_after)                REJECTED  "non-simple property in irreflexive..."
```

So you cannot say "nothing exists both before and after the same thing" directly.

### What you can do

Move the constraint to **classes**, where there is no simplicity requirement:

```
During_CS11    ≡ ∃ existence_starts_during          . CS11
AtOrAfter_CS13 ≡ ∃ existence_starts_during_or_after . CS13
DisjointClasses( During_CS11, AtOrAfter_CS13 )
```

Combined with the §08 chains, this catches a product asserted to start before its own precursor:

```
bad_product ⊑ ∃transformation_of some precursor      ⊑ exists_after
precursor   ⊑ ∃existence_starts_during some CS13
  → chain → bad_product ⊑ ∃existence_starts_during_or_after some CS13   ⊑ AtOrAfter_CS13
bad_product ⊑ ∃existence_starts_during some CS11                        ⊑ During_CS11
  → DisjointClasses → ⊥
```

```
unsatisfiable: bad_product
```

**Caught by ELK, in OWL 2 EL.** This is the `monotonicity.rq` check done declaratively, as
classification rather than a query.

### It generates, and it is small

`src/gen_stage_disjointness.py` emits the module for a real stage series. For the 23 Carnegie
stages:

| | |
|---|---|
| defined classes | 46 (two per stage) |
| disjointness axioms | **253** (one per ordered pair) |
| profile | OWL 2 **EL** |
| ELK reasoning time | 0.6 s |

C(N,2) growth, so a 50-stage series would be ~1,200 axioms — still trivial.

### A second, narrower check

A *functional* relation to the finest-granularity stage, plus pairwise-disjoint stages, catches
double assignment:

```
FunctionalObjectProperty(starts_at_carnegie_stage)
DisjointClasses(CS11 CS12 CS13)
LiverBud ⊑ ∃starts_at_carnegie_stage.CS11  and  ⊑ ∃starts_at_carnegie_stage.CS13   →  ⊥
```

Works, and a property may be functional while appearing in a chain **body** — only the chain
*head* becomes non-simple. But `FunctionalObjectProperty` is **not in EL**, so this one needs
HermiT. Fine for a QC pass, which is a separate build step from materialisation.

Note functionality is only true at a single granularity: a structure starts during CS11 *and*
during the embryonic stage, which are not disjoint. Reserve it for one designated stage series.

---

## 10 / 11 / 12 — the idealised-individual versions

### 10-individuals.ofn — same design, stages *and* structures as individuals

Identical property hierarchy and chains to 08; `CS11`…`CS13` and `liver`…`liver_diverticulum`
become `NamedIndividual`s and the assertions become OPAs. **In OWL 2 EL.**

It derives *more* than the class version:

```
liver_bud  existence_starts_during_or_after  CS11, CS12, CS13
liver      existence_starts_during_or_after  CS11,       CS13
liver      exists_after                      liver_bud, liver_diverticulum
```

Individuals let the `C:O ∘ O:O` chain walk the whole stage series, so `liver_bud` reaches every
earlier stage rather than only the ones a class axiom happened to mention.

**A gap this exposes**: `liver` misses CS12. The chain starts from `existence_starts_during`
(strict), so *derived* `..._during_or_after` facts do not feed back into it. Adding
`existence_starts_during_or_after ∘ preceded_by ⊑ existence_starts_during_or_after` closes it —
another instance of needing the composition table rather than a few chains.

### 11-individual-errors.ofn — error checking degrades

Same disjointness as 09, over individuals. The error is caught, but:

```
09 (classes)      unsatisfiable: bad_product        ← named, localised, other reasoning continues
11 (individuals)  The ontology is inconsistent      ← global, nothing else can be inferred
```

**This is a real regression.** An unsatisfiable class names the culprit and leaves the rest of
the ontology usable; an inconsistent ABox stops everything and needs explanation tooling to find
the cause. Keep the error checking at class level even when the inference runs over individuals.

### 12-closed-somites.ofn — closed sets, and promotion as *entailment*

The point of the idealisation is that the instance set is **complete**. Say so with an
enumerated class:

```
Somite ≡ ObjectOneOf( somite_01 somite_02 somite_03 )
DifferentIndividuals( somite_01 somite_02 somite_03 )

somite_01 existence_starts_during CS09
somite_02 existence_starts_during CS10
somite_03 existence_starts_during CS11
```

Each somite carries its own timing — the thing a class axiom cannot represent. Then ask whether
a class-level axiom holds of all of them:

```
StartsAtOrAfterCS09 ≡ ∃ existence_starts_during_or_after . {CS09}

HermiT:   Somite ⊑ StartsAtOrAfterCS09      ENTAILED ✓
```

**This is the promotion rule of [IDEALISED_INDIVIDUALS.md](../IDEALISED_INDIVIDUALS.md) §4 done as
entailment** rather than by enumerating in code. The reasoner checks the universal for you,
because `ObjectOneOf` tells it the membership is closed.

**Negative control**: move `somite_01` to CS08 and the promotion is correctly **withheld**. The
closed class blocks an unjustified generalisation rather than rubber-stamping it.

### The cost of closing

| | |
|---|---|
| OWL 2 DL | ✓ |
| OWL 2 EL | ✗ — *"Use of ObjectOneOf with multiple individuals"* |
| 39 somites × 23 stages, HermiT | **0.57 s** |

So closed-world promotion is a **DL-only, HermiT-only** step. It will not run in ELK and
relation-graph will not materialise it. That is tolerable — it is a build-time check that emits
axioms, not something in the query path — but it means the pipeline has two reasoner passes:
ELK for materialisation, HermiT for promotion and QC.

Scale is not the problem. `ObjectOneOf` over 39 individuals costs nothing.
