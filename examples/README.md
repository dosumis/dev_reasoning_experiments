# Toy examples: bridging continuants to temporal relations

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

## 06-reified.ofn / 07-reified-class.ofn — the route that actually works

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

---

## What none of this can do

- **Narrow a relation from two sources** — no object-property intersection, so `dfO` and `osd`
  on the same pair cannot combine to `d`.
- **Arithmetic over stages** — "what existed at day 26" is not a DL query.
- **Conclude by elimination.**
- **Carry the full table** — 132 of 638 chains are cyclic and rejected from OWL 2 DL
  ([../README.md](../README.md) §5).

Those remain the constraint solver's job.
