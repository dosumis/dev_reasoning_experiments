# A lineage-resolved fate map as a temporal knowledge graph

Assessment of Colgan, Koblan et al., *Comprehensive Lineage Tracing Maps the Landscape of Cell
Fate Decisions in Mouse Embryogenesis* (bioRxiv 2026.05.07.722278v2) as a substrate for the
interval-reasoning architecture in this repo.

**Verdict: the best fit encountered in this project**, for a reason that is structural rather
than incidental — it is the first dataset here whose temporal assertions are *measured* and
*token-level*.

---

## 1. What the dataset provides

PEtracer prime-editing lineage recording across **>1.5M cells from 16 mouse embryos**, sampled
at **half-day intervals E7.5–E10.0**, resolving **~75% of cell divisions**, paired with
scRNA-seq so every cell has both a lineage history and a transcriptional state.

Four kinds of temporal assertion fall out of it:

| | Temporal form | Allen |
|---|---|---|
| **Fate restriction times** — per clade/cell type, numeric, in embryonic days | interval endpoint with uncertainty | bounded start |
| **Gene program activation order** — 70 Hotspot programs, "activated in defined temporal sequences" | measured ordering | `precedes` / `meets` |
| **Lineage trees** — mother → daughter, ~75% of divisions | division is instantaneous | `meets` (`m`) |
| **Fate bias** — e.g. "23.1% of clades bipotent" | weighted edge | *not expressible in OWL* |

Concrete measured orderings from the paper:

```
myotome:   P47 somite signal modulation   precedes   P41 actomyosin contractility
cardiac:   P33 cardiomyocyte contractility   FHF first, then SHF derivatives
notochord: fate restriction before E7.5, concurrent with initial mesodermal specification
```

These are exactly Allen relations, derived from data rather than curated from literature.

---

## 2. Why it fits the architecture unusually well

### It is token-level, so the type/token problem does not arise

Twice in this project a naive start-order axiom broke on real biology — Uberon's reciprocal
induction and dismech's 46 vicious cycles ([USER_STORIES.md](USER_STORIES.md) §2). Both failed
because the assertions are over **types**, which can recur, while Allen applies to
**occurrences**, which cannot.

Lineage trees are over actual cells. **A cell divides once.** The graph is acyclic by
construction, start-order is guaranteed, and `develops_from ⊑ starts_after` needs no narrowing
or exception. This is the first dataset here where the axiom simply works.

Better still, cell division makes the relation exact: a mother cell's existence interval
**meets** each daughter's — Allen `m`, a singleton, not a disjunction. Dense, exact, measured
constraints are the ideal input to a constraint network.

### The sampling design already aligns to the Theiler backbone

Checked against MmusDv `start_dpc` annotations:

| Timepoint | Theiler | | Stage | Interval |
|---|---|---|---|---|
| E7.5 | TS11 | | TS11 | [E7.5, E8.0) |
| E8.0 | TS12 | | TS12 | [E8.0, E8.5) |
| E8.5 | TS13 | | TS13 | [E8.5, E9.0) |
| E9.0 | TS14 | | TS14 | [E9.0, E9.5) |
| E9.5 | TS15 | | TS15 | [E9.5, E10.0) |
| E10.0 | TS16 | | | |

**One timepoint per stage, five complete stages tiling the window exactly.** No alignment work
is needed — the dataset lands on the existing backbone as-is.

### It composes with what is already built

The E7.5–E10.0 window overlaps five MP lethality intervals:

```
E4.5–E8.0   between implantation and somite formation
E4.5–E9.0   between implantation and placentation
E8.0–E9.0   between somite formation and embryo turning
E9.0–E9.5   prior to organogenesis
E9.0–E14.0  during organogenesis
```

So the chain already demonstrated in `tests/full_chain.py` extends straight through:

```
MP lethality (E-days) → Theiler stage → [fate restrictions + gene programs in that window]
```

which yields a query nobody can currently run — see US11 below.

---

## 3. What would need building

### Raw data, or at least `obs`

The preprint gives figures and prose; the quantities needed are per-cell and per-node:

| Needed | Where |
|---|---|
| cell → timepoint, cell type, embryo, clone | `obs` |
| lineage tree topology (mother/daughter node ids) | tree files |
| fate restriction time per clade | derived; may be supplementary |
| gene program scores per cell and per ancestral node | `obsm` / program matrices |
| fate bias distributions per ancestral node | derived |

A GEO accession is referenced. The KG cannot be built from the PDF.

### Grounding the cell types

Cell types were annotated by **label transfer from Pijuan-Sala 2019 and Qiu 2024, then manual
curation** — free-text labels, not CL terms. Mapping them to CL is the prerequisite for joining
to anything else, and is the standard LLM-normalisation-with-solver-validation job
([USER_STORIES.md](USER_STORIES.md) US7).

Uberon/MmusDv grounding for tissues would follow the same route.

### Weighted edges: a real limitation

Fate bias is inherently probabilistic — "the probability of a clade containing either DRG or
autonomic outputs decreased with later restriction time". **OWL has no notion of edge weight.**
Three options, in increasing order of honesty:

1. **Threshold** into qualitative relations (`has_fate_bias_toward` above some cutoff). Lossy,
   arbitrary, but immediately usable in the OWL/materialisation layer.
2. **Axiom annotations** carrying the probability. Preserves the number, invisible to the
   reasoner, usable by the query layer.
3. **Keep weights out of the ontology entirely** — OWL layer for the qualitative skeleton,
   weights in the accompanying data. The reasoner answers *possible/entailed*; the weights rank
   the answers.

(3) is the right split and matches the two-layer architecture already argued for: symbolic layer
for what is entailed, numeric layer for what is likely.

---

## 4. Proposed KG shape

```
Cell (token)             --develops_from-->  Cell            [Allen m, exact]
Clade                    --has_member-->     Cell
Clade                    --restricted_to-->  CellType        [weight: fate bias]
Clade                    restriction_time    interval [lo, hi]     <- measured
CellType                 --existence_starts_during-->  Theiler stage
GeneProgram              --active_during-->  interval, per CellType
GeneProgram P47          --precedes-->       GeneProgram P41  [in myotome]  <- measured
```

RO relations that apply directly: `develops_from` / `develops_into`, `existence_starts_during`,
`existence_starts_and_ends_during`, `precedes` / `immediately_precedes`, `part_of`. Plus
`starts_after` from [RO_REPORT.md](RO_REPORT.md), which the lineage edges need.

The gradual-mapping route the data invites: ground cell types in CL first (largest payoff,
enables every join), then tissues in Uberon, then attach the measured intervals. Programs can be
left as local identifiers indefinitely — their value is in their *relations*, not their labels.

---

## 5. The query this unlocks

> **As a** mouse developmental geneticist whose knockout is embryonic lethal between E8.0 and
> E9.0,
> **I want** the cell fate restriction events and gene program activations that occur inside
> that window, ranked by how specific they are to it,
> **so that** I can shortlist which fate decision the knockout disrupts, rather than which
> anatomical structure was merely present.

This is US1 with the resolution turned up. US1 currently answers with coarse structures
(`embryo`, `conceptus`) because Uberon has only 80 `existence_*` assertions at gross stage
granularity. This dataset would answer with **specific fate restriction events and named gene
programs**, at half-day resolution, from measurement rather than curation.

That is the single largest available improvement to the strongest user story in the project.

---

## 6. Caveats

**The trees extend beyond the sampling window by inference.** Fate bias is reported as first
emerging "~E4.0" — well before the E7.5 earliest sample. Those are *imputed ancestral* times,
not observations. Any interval derived from them carries model uncertainty that must be
propagated, not silently dropped. This is precisely the bounded-but-unknown-endpoint case the
constraint layer exists to handle, and it should be represented as such rather than as a point
estimate.

**Chimeric embryos.** Embryos were seeded by 2–6 donor mESCs, not derived from a single zygote.
The authors flag that earliest fate decisions should be read in that engineered context.

**Cell type boundaries are not discrete.** The authors' own limitation: "rare or transitional
states may be under-resolved, and boundaries between closely related cell types may not reflect
discrete biological categories." Interval endpoints inherited from such boundaries are softer
than the numbers suggest.

**Nothing here has been run.** This is an assessment from the preprint text. The composition
with Theiler stages and MP intervals is computed and verified; everything about the KG is
proposal.
