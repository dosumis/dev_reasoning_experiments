# What can we actually compute? User stories and a capability matrix

All counts measured against current releases of HsapDv, MmusDv, Uberon (base), GO, HP, MP.

---

## 0. Two corrections to earlier findings in this repo

**Numeric bounds are NOT locked in prose.** Both DV ontologies carry dedicated
machine-readable endpoint annotation properties. An earlier pass here regex-scraped 156
intervals out of HsapDv *definitions*; the annotations are more complete and authoritative:

| | HsapDv | MmusDv |
|---|---|---|
| terms with **both** a start and an end | **215** | **122** |
| terms with any numeric endpoint | 248 | 156 |
| properties used | `start_dpf`/`end_dpf`, `start_mpb`/`end_mpb`, `start_ypb`/`end_ypb` | `start_dpc`, `start_dpb`/`end_dpb`, `start_wpb`/`end_wpb`, `start_mpb`/`end_mpb` |

**The reference-frame problem is largely already solved.** The frame is encoded in the
property name — `dpf` (days post fertilization), `dpc` (post coitum), `dpb`/`wpb`/`mpb`/`ypb`
(post birth). Converting between them needs one constant per species, not an OWL-Time `TRS`
modelling exercise. That earlier recommendation was overbuilt.

---

## 1. What temporal content actually exists

| Ontology | Native temporal content | Numeric anchoring |
|---|---|---|
| **HsapDv** | 220 `immediately_preceded_by`, 237 `part_of` | **215/255 fully anchored** |
| **MmusDv** | 122 `immediately_preceded_by`, 132 `part_of` | 122 anchored postnatally; **27 Theiler stages have `start_dpc`, ZERO have `end_dpc`** |
| **Uberon** | 80 `existence_*` → stage; **1,434 `develops_from`**; 332 `has potential to develop into` | n/a |
| **MP** | **36 lethality terms with explicit E-day intervals** | in prose only (`"Mus: E4.5 to less than E8"`) |
| **HP** | 55 onset terms forming an interval hierarchy; 11 with numeric prose bounds | none machine-readable |
| **GO** | ~24 `happens_during`, 2 `starts_during`, 4 `ends_during` | none |

**GO is essentially empty of explicit temporal relations.** Its process `part_of` hierarchy
carries implicit temporal containment, but nothing is asserted. Do not plan around GO.

---

## 2. The two structural gaps

### Gap A — `develops_from` has no temporal semantics

```
develops from → has developmental contribution from → developmentally preceded by
              → developmentally related to → (dead end)
```

There is **no path from the developmental relation hierarchy to the temporal one**. 1,434
Uberon assertions state that one structure arises from another, and none of it is visible to
temporal reasoning.

The correct axiom is *not* `develops_from ⊑ preceded_by`. Where X develops from Y, Y need not
cease when X appears (X may bud from a persisting Y). The safe claim is only that Y begins
first:

> `develops_from ⊑ starts_after`  — i.e. `start(X) > start(Y)`, Allen label **`dfOMP`**

**RO cannot express this.** RO has `starts_before` (`pmoFD`, RO:0002089) but not its converse
`starts_after` (`dfOMP`). So the single highest-value temporal axiom available — one line,
unlocking 1,434 assertions — requires a relation the 29-relation extension supplies and
current RO does not.

### ~~Gap B — the species-stage ↔ generic-stage bridge is missing~~ — RESOLVED

**This is not a gap.** The bridges exist, in
`developmental-stage-ontologies/src/mappings/life-stages.sssom.tsv`: **269
`semapv:crossSpeciesExactMatch` mappings** from 23 species DV ontologies to UBERON generic
life-cycle stages (19 each for HsapDv and MmusDv). They are simply not present in the
standalone `hsapdv.owl` / `mmusdv.owl` artifacts, which is why the earlier check missed them.
The repo also ships `src/util/make-bridge-axioms.pl` and a merged `life-stages-full.owl`.

Coverage against the stages Uberon's `existence_*` assertions actually use: **17 of 21 (81%)**,
12 of them with both mouse and human mappings. The four uncovered are `larval stage`,
`pupal stage`, `2/4/8 cell stage` — irrelevant to mammals or too fine-grained.

**The full chain runs end-to-end** (`tests/full_chain.py`), with no manual curation:

```
MP lethality (E-days) ──► Theiler stage ──► generic MmusDv stage ──► UBERON stage ──► structures
   [dpc + Allen 'meets']    [part_of closure]        [SSSOM]           [existence_*]
```

**But precision is poor, and the reason matters.** The mappings are at gross granularity, as
expected. Every query window pulls in `embryo stage`, so coarse structures (`embryo`,
`conceptus`, `entire extraembryonic component`) dominate every answer. Two fixes, both cheap:
rank results by stage specificity, and drop stages that properly contain the query window
rather than overlapping it — an Allen `D`/`contains` filter, exactly the kind of distinction
the relation set is for.

The real bottleneck is now **volume**: only 80 `existence_*` assertions exist across all of
Uberon. Which makes Gap A the priority — it would multiply the available structure data by 18×.

---

## 3. User stories

Each story names a role, a query that role would plausibly issue, and an outcome that role
plausibly cares about. An LLM layer sits at both ends: turning the natural-language ask into a
formal interval query, and turning the returned relations back into something the role can act
on. The role never sees an Allen label.

---

### US1 — Candidate mechanisms for an embryonic-lethal knockout ★ strongest case

> **As a** mouse developmental geneticist who has just phenotyped a knockout line as embryonic
> lethal between E4.5 and E8,
> **I want** the anatomical structures and processes whose existence window overlaps that
> lethality window,
> **so that** I can shortlist candidate mechanisms before committing to targeted histology or
> expression work.

- **Query**: `interval_overlaps([E4.5, E8])` over structure existence intervals, via the
  Theiler backbone.
- **LLM layer**: *in* — "my knockout dies around gastrulation" → the right MP term → its E-day
  interval. *out* — a ranked structure list with a plain-English reason per hit ("the blastoderm
  begins forming in the blastula stage, which falls inside your window").
- **Machinery**: numeric anchors + `part_of` closure + SSSOM. **No AIC reasoning required.**
- **Status**: runs end-to-end (`tests/full_chain.py`). Precision poor — see §2.
- **Why the role cares**: MGI annotates thousands of genes with staged lethality terms. Nobody
  can run this query today.

### US2 — Focusing surveillance after a teratogen exposure

> **As a** teratology information specialist advising on a pregnancy exposed to a drug during
> weeks 6–9 post-fertilization,
> **I want** the structures undergoing formation during that window,
> **so that** I can focus counselling and targeted ultrasound on the organ systems actually at
> risk, rather than reciting a generic risk list.

- **Query**: same shape as US1, on the human backbone (215/255 stages anchored).
- **LLM layer**: *in* — a free-text exposure history with dates → a `dpf` interval, handling
  the LMP-vs-fertilization conversion silently. *out* — organ systems grouped by system, with
  the developmental event that makes each vulnerable.
- **Machinery**: numeric anchors alone.
- **Status**: unblocked; not yet built. Public-health framing the NIH challenge explicitly names.

### US3 — Catching impossible onset annotations

> **As an** HPO curator reviewing disease–phenotype annotations before a release,
> **I want** annotations flagged where the asserted onset window cannot overlap the existence
> window of the affected structure,
> **so that** I can correct curation errors rather than ship contradictions.

- **Query**: for each annotation, test whether `onset ∩ existence = ∅` — i.e. whether the two
  intervals are necessarily disjoint (`p` or `P`).
- **LLM layer**: mostly unnecessary — this is a batch QC report, not an interactive query. The
  LLM's job is writing the human-readable explanation attached to each flag.
- **Machinery**: **needs AIC.** Contradiction detection requires disjointness, which is what
  forces SWRL over plain OWL (§4).
- **Status**: blocked on HP-onset ↔ HsapDv alignment, which does not exist. HPO's onset
  hierarchy parallels HsapDv but is unlinked to it.

### US4 — Retrieving samples annotated at the wrong granularity

> **As a** bioinformatician analysing a single-cell atlas whose samples are stage-annotated
> inconsistently — some to "Carnegie stage 13", some just to "embryonic stage",
> **I want** a query for "structures developing during organogenesis" expanded to every
> stage-annotated term whose interval falls in that window,
> **so that** I retrieve all relevant samples regardless of the granularity each was curated at.

- **Query**: interval containment plus `part_of` closure over the stage backbone.
- **LLM layer**: *in* — free-text stage description → interval. *out* — nothing needed; the
  result is a term list feeding a data query.
- **Machinery**: numeric anchors + property chains. Cheapest story here.
- **Status**: unblocked. This was the original motivating use case, and it needs the least.

### US5 — Finding temporally impossible developmental assertions

> **As an** Uberon curator,
> **I want** `develops_from` assertions flagged where the two structures' existence windows make
> the relationship temporally impossible,
> **so that** I can fix incorrect developmental relationships at source.

- **Query**: for each `X develops_from Y`, test whether the asserted existence intervals are
  consistent with `start(Y) < start(X)`.
- **LLM layer**: report generation only.
- **Machinery**: **needs AIC**, and needs Gap A closed first. Also needs composition, since
  `develops_from` is transitive and lineage chains compound.
- **Status**: blocked on Gap A. 1,434 assertions to check — the largest QC surface available.

### US6 — Translating a mouse phenotype to a human window

> **As a** comparative developmental biologist studying a mouse mutant,
> **I want** the human gestational window corresponding to the mouse stage at which the defect
> arises,
> **so that** I can judge which human congenital conditions are plausible counterparts.

- **Query**: mouse stage → shared UBERON generic stage → human stage range.
- **LLM layer**: *out* — must be explicit that the answer is coarse, or the user will over-read
  it. This is a case where hiding complexity would be actively harmful.
- **Machinery**: SSSOM traversal. Numeric anchors do **not** help: `dpc` and `dpf` are not
  commensurable across species.
- **Status**: partly solvable now, at gross granularity only (TS17 → `organogenesis stage` → all
  human organogenesis stages). Fine-grained Carnegie↔Theiler remains uncurated.

### US7 — Comparing trajectories across atlases with no shared pseudotime

> **As a** computational biologist integrating two developmental single-cell atlases,
> **I want** each dataset's cell states placed on a shared stage backbone using their
> tissue-stage sample metadata,
> **so that** I can compare trajectories between datasets that have no common pseudotime axis.

- **Query**: project each trajectory segment's constituent samples onto stage intervals, then
  relate segments across datasets through the backbone.
- **LLM layer**: *in* — normalising messy free-text stage metadata ("E9.5", "8–9 pcw", "CS13",
  blank) into stage IRIs. This is the highest-value LLM contribution in the whole set, and the
  constraint solver acts as its guardrail by catching normalisations that produce contradictions.
- **Machinery**: **needs AIC.** Sampled presence gives bounded-but-unknown endpoints, which is
  exactly the disjunctive case; and cross-dataset relations must be inferred, not asserted.
- **Status**: not started. The stage backbone is the interlingua — pseudotime does not compose
  across datasets, stage intervals do.

---

## 4. Capability matrix

| Story | Numeric anchors alone | + property chains (OWL EL, relation-graph) | + full AIC (SWRL/RL) | Real blocker |
|---|---|---|---|---|
| US1 hop 1 | ✅ **done** | – | – | – |
| US1 hop 2 | ✅ **done** | ✅ | – | precision (gross mappings, 80 assertions) |
| US2 | ✅ | ✅ | – | – (SSSOM covers HsapDv too) |
| US3 | partial | ✗ | ✅ **required** (disjointness) | HP↔HsapDv alignment |
| US4 | ✅ | ✅ | – | – |
| US5 | ✗ | partial | ✅ **required** | **Gap A — one axiom + `starts_after`** |
| US6 | partial | ✗ | ✗ | SSSOM gives gross-level alignment only |
| US7 | ✗ | ✗ | ✅ **required** | stage metadata normalisation (LLM) |

**Revised headline: the bridges exist and the chain runs.** What limits US1/US2 now is not
reasoning power and not alignment — it is the *volume and granularity* of the underlying
assertions: 80 `existence_*` links, mapped at gross stage level. Where numeric anchors exist,
plain comparison suffices; the reasoning layer's job is to improve precision (ranking by stage
specificity, `contains` vs `overlaps` filtering) rather than to make the query possible.

AIC genuinely earns its place in exactly three: **US5** (needs `starts_after`, absent from RO,
plus composition through transitive `develops_from`), **US3** (disjointness-based contradiction
detection), and **US7** (bounded-but-unknown endpoints from sampled presence — the only story
where the disjunctive case is intrinsic rather than incidental).

Note the pattern: the three AIC-requiring stories are all **curation-, QC- or integration-facing**,
addressed to ontology and data professionals. The three that need only numeric comparison
(US1, US2, US4) are the ones addressed to bench and clinical users. That split is worth keeping
in view when deciding what to build first and who to demo it to.

---

## 5. Scaling

| Approach | Practical scale | Complexity | Gives |
|---|---|---|---|
| Numeric endpoint comparison | 10⁶+ | O(n log n) with an interval tree | everything in US1/2/4 |
| Property chains, regular subset (relation-graph) | 10⁵+ points, < 3 s | closure to fixpoint | materialisation, query expansion |
| Full AIC via SWRL | **100–500 intervals** | path consistency O(n⁵) | completeness + inconsistency detection |
| Dedicated PC solver (CHRONOS-class) | 10⁴ relations < 10 s | O(n⁵) worst case | same, ~100× faster |

SWRL is the binding constraint whenever consistency checking is required — and consistency
checking is precisely what OWL 2 cannot give you alongside transitivity.

---

## 6. Are hybrids viable? Yes — and here is the theoretical basis

The hybrid is a **qualitative + metric temporal constraint network** (Meiri 1996). The property
that makes it work:

> **Metric constraints prune qualitative labels.** An interval with known numeric endpoints
> stands in exactly one of the 13 relations to any other such interval — the label collapses
> to a singleton and never enters the disjunctive search.

With 215 of 255 HsapDv stages numerically anchored, the ground backbone is dense. Any floating
interval anchored to even one backbone stage inherits bounds, so the genuinely disjunctive part
of the network stays small. That is the theoretical reason the hybrid should scale, and it
yields a **measurable quantity**:

> **escalation rate** *e* = fraction of interval pairs whose label is still disjunctive after
> (i) numeric comparison where both endpoints are known, and (ii) materialisation of the
> regular property-chain subset.

Cost is then roughly `O(n log n) + O(materialisation) + O((e·n)⁵)`. Since path consistency is
quintic, *e* dominates everything. If *e* is small on real OBO data, Allen-complete reasoning
is affordable at OBO scale; if not, it never will be.

### Measured (`tests/escalation_rate.py`)

| Network | intervals | informative pairs | singletons | still disjunctive | **e** |
|---|---|---|---|---|---|
| HsapDv anchored backbone | 215 | 23,005 (100%) | 23,005 | 0 | **0.000** |
| Uberon `existence_*` network | 84 | 96 (**2.8%**) | 24 | 72 | **0.750** |

The contrast is the whole answer:

- **Where numeric anchors exist, `e = 0`.** All 23,005 HsapDv stage pairs resolve to a single
  Allen relation by comparing four numbers. No qualitative reasoning is needed *at all*, and it
  scales to 10⁶ with an interval tree.
- **Where they don't, `e = 0.75`** — three-quarters of informative pairs stay disjunctive even
  after path consistency. This is where AIC is genuinely irreplaceable.
- **But that network is 97.2% empty.** Only 96 of 3,486 pairs carry any information. The
  quintic cost applies to the informative subnetwork, not to *n*, and sparsity is what makes it
  affordable.

Path consistency also derived **27 new pairs beyond the 69 asserted (+39%)** — the quantified
value-add of the reasoning layer over the raw assertions.

*Caveat: e = 0.75 is measured on a small network (84 intervals). It establishes the shape of the
answer, not its value at scale. Re-measuring once Gaps A and B are closed — which would bring
1,434 `develops_from` assertions into the same network — is experiment #2 in §7.*

---

## 7. Proposed programme (for Jim)

Three pieces, in dependency order, each with a theoretical basis and a measurable outcome:

1. **Ship `starts_after` + the `develops_from` axiom.** Smallest change, largest unlock:
   1,434 assertions become temporally visible. Immediately testable via US5 as a QC run over
   Uberon — real defects or a clean bill, either is a result.

2. **Measure the escalation rate *e*.** Over HsapDv + MmusDv + Uberon existence + `develops_from`.
   This single number determines whether the whole enterprise is affordable, and it is cheap to
   compute with what is already in this repo.

3. **Metric-grounded label pruning in relation-graph.** Extend it to carry numeric endpoint
   annotations and collapse labels to singletons before materialising. Theory says this converts
   most of an Allen network into an STP (Floyd–Warshall, O(n³)) and confines the quintic
   path-consistency step to the *e* fraction. Novel, well-founded, and exactly the kind of
   engine work relation-graph is positioned for.

The curation gaps (A and B) are prerequisites for 1 and 2 and should be raised with Uberon/MmusDv
maintainers independently — they are small, and they block more than this project.
