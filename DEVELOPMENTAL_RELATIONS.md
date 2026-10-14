# Timing relations for developmental transitions

A proposal for giving `develops_from` and its relatives temporal semantics: **two new object
properties and four axioms**, most of the targets already in RO.

Companion to [`docs/end-bound-convention.md`][ebc] in
[dosumis/Uberon_HDCA_stage_axioms][repo], which reaches the same distinction from the curation
side. That repo is the delivery vehicle — sourced axioms, evidence standards, drafted NTRs.
This document supplies the formal justification and the measurement.

[repo]: https://github.com/dosumis/Uberon_HDCA_stage_axioms
[ebc]: https://github.com/dosumis/Uberon_HDCA_stage_axioms/blob/evidence-pipeline/docs/end-bound-convention.md
[mono]: https://github.com/dosumis/Uberon_HDCA_stage_axioms/blob/evidence-pipeline/sparql/checks/monotonicity.rq

---

> ## ⚠ Correction in progress
>
> The axioms proposed in §4 subsume continuant relations under BFO's **occurrent** temporal
> relations. BFO declares continuant and occurrent disjoint, so as written they make every
> structure involved **unsatisfiable** — verified in [examples/01-broken.ofn](examples/01-broken.ofn).
>
> The `existence_*` family does not rescue it either: it inherits `range = occurrent` from
> RO:0002581 ([examples/02-also-broken.ofn](examples/02-also-broken.ofn)).
>
> The route that works keeps **three typed families** — C:C timing, O:O timing, and RO's
> existing C:O `existence_*` bridge — with developmental relations carrying the **C:C** relation
> as a superproperty, and property chains crossing between families:
>
> ```
> transformation_of       ⊑ exists_immediately_after                    (both C:C)
> exists_after ∘ existence_starts_during ⊑ existence_starts_during_or_after
> existence_starts_during ∘ preceded_by  ⊑ existence_starts_during_or_after
> ```
>
> No new primitive, no reification, OWL 2 EL. See
> [examples/08-develops-from-timing.ofn](examples/08-develops-from-timing.ofn). This document has
> not yet been rewritten around it.

## 1. The problem

`develops_from` has no path to the temporal relation hierarchy
([RO_REPORT.md](RO_REPORT.md) §2), so ~3,500 assertions across Uberon and EHDAA2 are invisible
to temporal reasoning. The obvious fix is an axiom. The question is *which*.

RO's own definition of `directly develops from` (RO:0002207) is unexpectedly strong:

> *"…and a substantial portion of the matter of x comes from y, and **the start of x is
> coincident with or after the end of y**."*

That is `start(X) ≥ end(Y)` — Allen `PM`, which is exactly RO's `preceded_by` (BFO:0000062).

**The data contradicts it.** Measured across EHDAA2's 2,125 `develops_from` assertions
(`tests/develops_from_strength.py`):

| candidate axiom | testable pairs | provably violated |
|---|---|---|
| `preceded_by` (`PM`) — *precursor has ended* | 1,538 | **417 (27.1%)** |
| `starts_after` (`dfOMP`) — *precursor has started* | 2,125 | 50 (2.4%) |

Over a quarter of real usage has the precursor demonstrably still present when the product
appears — `Rathkes pouch epithelium` from `buccopharyngeal membrane ectoderm`, `myotome 26`
from `dermomyotome 26`, `dorsal pancreas parenchyma` from `dorsal pancreas duct`.

[`end-bound-convention.md`][ebc] reaches the same conclusion independently from n=16:

> *"`develops_from` does not mean replaced by. A precursor routinely persists while its
> derivative appears — the neural plate carries on existing after the neural crest delaminates
> from it."*

So RO's definition quietly assumes transformation; curators use the relation for both.

---

## 2. The decomposition is exact

```
starts_after (dfOMP)  =  preceded_by (PM)  ⊎  starts_during (dfO)

   union is exact · intersection is empty · verified in tests/develops_from_strength.py
```

Those are the **only two ways** a successor-relative bound can sit. Either the precursor has
ended when the product starts (`PM`), or it is still going (`dfO`). Nothing else is possible and
the two cannot overlap.

Which means the split is not a modelling convenience — it is forced by the algebra. It also maps
one-to-one onto the curation categories in [`end-bound-convention.md`][ebc]:

| `offset_type` | Allen | |
|---|---|---|
| `transformation` — consumed; nothing persists under the old name | `M` | precursor ceases |
| `differentiation` — persists while derivatives appear | `dfO` | precursor continues |

---

## 3. The asymmetry in RO today

RO names the transformation case **twice** and has **nothing** for the other:

| | |
|---|---|
| `transformation of` (RO:0002494) | "x is the immediate transformation of y, or linked through a chain" |
| `immediate transformation of` (RO:0002495) | "x **immediately succeeds y temporally at a time boundary t**, and all of the matter present in x at t is present in y at t…" |
| — | *nothing for budding / delamination / segregation* |

Checked across the whole developmental branch: `develops from part of` is mereological,
`develops in` is spatial, `developmentally replaces` is about site occupancy. The persisting
case is unnamed.

RO:0002495's definition is Allen `M` verbatim — a **singleton**, the most informative relation
available. It is currently entailing nothing stronger than `developmentally preceded by`.

---

## 4. Proposal

| case | relation | status | Allen | axiom |
|---|---|---|---|---|
| precursor ceases, instantaneous | `immediate transformation of` RO:0002495 | **exists** | `M` | `⊑ immediately_preceded_by` (RO:0002087) |
| precursor ceases, chained | `transformation of` RO:0002494 | **exists** | `PM` | `⊑ preceded_by` (BFO:0000062) |
| **precursor persists** | **— missing —** | **NEW** | `dfO` | `⊑ starts_during` (RO:0002091) |
| mode not stated | `develops from` RO:0002202 | exists | `dfOMP` | `⊑ starts_after` |

**Two new object properties**: the persisting relation, and `starts_after` itself — RO's
missing converse of `starts_before` ([RO_REPORT.md](RO_REPORT.md) §1). **Four axioms.** Every
other target already exists.

Converse work is symmetric: RO has `develops into`, `developmentally contributes to` and
`part of developmental precursor of`, so each forward axiom implies an inverse one.

---

## 5. What does *not* need a new property

> **An object property earns its place when it carries an entailment its parent does not.**

Budding, delamination, ingression, evagination and splitting differ in **mechanism**, not in
temporal entailment. All are "precursor persists, product's start strictly inside the
precursor's existence" — all `dfO`, all receiving the same axiom. None earns an OP on temporal
grounds.

If they are wanted for morphogenetic reasons that is a separate and legitimate argument, but
then they belong as *children* of the one persisting relation, inheriting its axiom, not as
siblings each re-deriving it.

The same test is why transformation keeps both its terms: `M` and `PM` are genuinely different
entailments.

---

## 6. Why object properties rather than annotations

The alternative is the `onset_type`/`offset_type` column approach already used in
[`src/axioms.tsv`][repo]. For this particular distinction, properties win:

1. **Annotations are invisible to reasoners.** The purpose is inference and materialisation. An
   `offset_type: transformation` column cannot produce
   `optic cup immediately_preceded_by optic vesicle`; a subproperty can, and relation-graph
   will materialise it.
2. **Properties make the cases checkable.** `PM ∩ dfO = ∅`, so asserting both between the same
   pair becomes an inconsistency — free QC that a metadata column cannot provide.
3. **Migration is incremental.** The parent keeps the weak axiom; specialising an individual
   assertion strengthens it. No flag day for the existing ~3,500 assertions, and nothing breaks
   where a curator does not know the mode.

### What stays as curation metadata

`regression` and `event` endings are **not successor-relative at all** — a structure that
regresses, or that a named event terminates, has no `develops_from` partner carrying the
information. They cannot be `develops_from` subproperties and should not be forced into one.

**This proposal covers only the successor-relative axis.** The four-way `offset_type` scheme in
[`end-bound-convention.md`][ebc] remains the more complete account of endings, and this is a
refinement of two of its four categories, not a replacement for it.

---

## 7. Naming — open

The consistently hard part. Flagged for the curator call rather than asserted here.

Lead candidate for the persisting relation: **`segregates_from`** — covers budding,
delamination, ingression and splitting, and implies the source continues. Note that RO's
existing `transformation of` is named for mechanism/outcome rather than for its endpoint
invariant, so the counterpart should probably match that style rather than echoing
`starts_during`.

`starts_after` has its own naming note in [RO_REPORT.md](RO_REPORT.md) §1: RO's compound
relations are already named by the endpoint invariant shared across their disjuncts
(`starts_during` = `dfO` = "start inside Y"), and `starts_after` fits that scheme.

---

## 8. Caveats

**The strong axioms rest on RO's definitions, not on measurement.** RO:0002495's wording *is*
Allen `M`, but of Uberon's 72 `immediate transformation of` assertions, **exactly one** has
existence data on both ends. 0 of 47 for `transformation of`. The data to validate these
empirically does not exist yet — which is itself an argument for EHDAA2's 3,503 stage
assertions ([EHDAA2_REPORT.md](EHDAA2_REPORT.md) §6).

**Is "the precursor persists" objective?** [`end-bound-convention.md`][ebc] warns that when a
pharyngeal arch stops being an arch is a vocabulary decision, not an observation. If persistence
is partly a naming artifact, the property choice inherits the arbitrariness.

It is on firmer ground on the *start* side than the end side: "does Y still exist when X
appears?" requires Y to be nameable only at the instant X appears — which it is by construction,
since the `develops_from` assertion presupposes it. Whereas "when does Y stop being Y?" requires
pinning Y's end, which is the genuinely arbitrary part. **The subproperty distinction is sounder
than the end-bound convention it supports**, which is a reason to land it first.

**Species neutrality.** [`monotonicity.rq`][mono] notes that Uberon's `develops_from` edges are
species-neutral and some hold only in certain taxa, so a violation may mean the edge does not
apply in that taxon rather than that a bound is wrong. The 27.1% above is from EHDAA2, which is
human-only, so it is largely insulated — but the same caveat applies to any Uberon-wide run.

---

## 9. Relation to the idealised-individual proposal

[IDEALISED_INDIVIDUALS.md](IDEALISED_INDIVIDUALS.md) attacks the same lossiness from the other
end: rather than finding the tightest *class-level* relation, represent countable parts as
individuals, assert exact relations between them, and promote back.

The two interlock. The subproperties here are what an instance-level assertion would *use* —
`myotome-08 immediately_preceded_by dermomyotome-08` needs the transformation relation to carry
Allen `M` before the assertion means anything. And promotion is what returns the result to
Uberon as an ordinary class axiom. Neither requires the other, but together they give exact
class-level relations that are not otherwise assertable.

## 10. How the two repos divide

| | |
|---|---|
| **[Uberon_HDCA_stage_axioms][repo]** | taxon-scoped GCIs, evidence standards, sourced axioms, drafted NTRs, the contribution package |
| **this repo** | the interval algebra, what OWL can and cannot carry, what the data violates |

Two findings from that side that correct work here:

- **Taxon scoping.** `heart tube SubClassOf existence_starts_during some CS09` is an all-some
  claim that is false the moment a second species is considered. All the existence reasoning in
  this repo is species-neutral and inherits that unsoundness.
- **GCI invisibility.** A GCI has no named subject, so relation-graph materialises nothing from
  it — a concrete fact about the toolchain this repo recommends, and one it does not mention.

And two from this side worth pulling across:

- **Predicate discipline.** That repo's 176 rows are 155 two-sided / 21 one-sided, chosen
  deliberately. EHDAA2 uses the one-sided relations for all 3,503 assertions, and the
  consequence is measurable: as asserted, **no violation is detectable at all**
  ([EHDAA2_REPORT.md](EHDAA2_REPORT.md) §2).
- **A backbone bug.** HsapDv asserts `Carnegie stage 05a` both `part_of` and
  `immediately_preceded_by` `Carnegie stage 05` — Allen `d ∩ M = ∅`. Anything walking the
  `immediately_preceded_by` chain is exposed ([EHDAA2_REPORT.md](EHDAA2_REPORT.md) §5a).
