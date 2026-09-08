# Temporal reasoning over dismech: findings

A survey of [dismech](https://github.com/dosumis/dismech) as a substrate for temporal
reasoning — what it contains, what temporal structure is implicit in it, and what would be
needed to make that structure usable.

Surveyed at commit state of 2026-09-04. Companion to [USER_STORIES.md](USER_STORIES.md)
(stories US8–US10) and [HP_ONSET_PROPOSAL.md](HP_ONSET_PROPOSAL.md).

---

## Summary

| | |
|---|---|
| Pathographs | 2,480 (one per MONDO disease) |
| Nodes / edges | 41,730 / 43,539 |
| **Causal edges** | **~33,500** |
| Cycles in the causal subgraph | **46 pathographs, 168 nodes** |
| Disorders with onset data | 296; **291 have both a pathograph and onset** |
| Phenotype nodes grounded in HP | ~33% of all nodes |

**The headline**: dismech is the largest body of temporally-ordered biomedical assertions
surveyed in this project — an order of magnitude more than Uberon's developmental relations —
and none of it is currently visible to temporal reasoning. It needs the same single axiom.

---

## 1. Structure

Pathographs are causal DAGs. Nodes are typed:

| node_type | count |
|---|---|
| phenotype | 15,549 |
| pathophysiology | 15,158 |
| treatment | 4,682 |
| genetic | 3,602 |
| biochemical | 896 |
| environmental | 700 |
| animal_model / experimental_model / computational_model | 1,548 |

Edges carry a `predicate` and, for causal ones, a `causal_link_type`:

| predicate | count | | `causal_link_type` | count |
|---|---|---|---|---|
| **causes** | **29,343** | | DIRECT | 11,711 |
| targets | 3,732 | | INDIRECT_UNKNOWN_INTERMEDIATES | 5,300 |
| **contributes_to** | **3,235** | | INDIRECT_KNOWN_INTERMEDIATES | 4,348 |
| treats | 2,691 | | UNKNOWN | 434 |
| readout | 1,168 | | *(none — non-causal predicate)* | 21,746 |
| models / partially_models / fails_to_model | 1,305 | | | |
| variant_of | 852 | | | |
| **triggers** | **376** | | | |
| **leads_to** | **243** | | | |
| **predisposes_to** | **230** | | | |
| **exacerbates** | **102** | | | |
| measures, perturbs, modulates, rescues, protects_against | 262 | | | |

Bolded predicates are the temporally-ordering ones: **33,529 edges**.

Phenotype nodes carry HP CURIEs; pathophysiology nodes are free-text titles with prose
descriptions. That asymmetry matters — the phenotype half is already grounded and queryable,
the mechanism half is not.

---

## 2. Causation entails temporal order

If A causes B, A begins before B. That is Allen `pmoFD` — `starts_before` — the *exact same
relation* that Uberon's `develops_from` needs, and which RO does not have
(see [RO_REPORT.md](RO_REPORT.md) §1).

```
causes  ⊑  starts_before
```

One relation therefore unlocks two independent bodies of data:

| | assertions |
|---|---|
| Uberon developmental relations | 1,558 |
| dismech causal edges | ~33,500 |
| **total** | **~35,000** |

This substantially strengthens the case for adding `starts_after`/`starts_before` to RO: it is
not a developmental-biology convenience, it is the missing piece for causal-mechanism graphs
generally.

---

## 3. The cycles, and what they mean

**46 of 2,480 pathographs contain a cycle in the causal subgraph** (168 nodes). Nearly all are
biologically genuine *vicious cycles*:

```
MONDO:0001441  pica
  iron deficiency / CNS dopaminergic dysregulation
    --causes--> non-nutritive substance ingestion
    --causes--> gut luminal iron sequestration
    --causes--> iron deficiency ...

MONDO:0002687  superior mesenteric artery syndrome
  mesenteric fat pad depletion --causes--> aortomesenteric narrowing
    --causes--> duodenal obstruction --causes--> reduced oral intake
    --causes--> weight loss --causes--> mesenteric fat pad depletion

MONDO:0000409  chorioamnionitis
  microbial invasion --causes--> PRR activation --causes--> cytokine production
    --causes--> MMP-mediated matrix degradation --causes--> membrane rupture
    --causes--> microbial invasion
```

These are correct. Naively asserting `causes ⊑ starts_before` over them yields
`start(X) < start(X)` — unsatisfiable.

### The modelling principle

> **Causation is cyclic at the type level and acyclic at the token level.** "Iron deficiency
> causes pica causes iron deficiency" means *an instance* of iron deficiency causes *a later
> instance* of pica, which causes *a still later instance* of iron deficiency. The types repeat;
> the occurrences are strictly ordered.

Allen's calculus applies to **occurrences**. dismech, Uberon and GO all assert over *types*. Any
type-level causal or developmental relation given a start-order axiom will hit this, and the
failure looks like an inconsistency in perfectly good data.

This project has now hit it twice independently:

| | |
|---|---|
| Uberon | `metanephric mesenchyme` ⇄ `ureteric bud`, reciprocal induction |
| dismech | 46 vicious cycles |

Both are correct biology. In the Uberon case the fix was to narrow the axiom so it does not
cover `developmentally_induced_by` ([RO_REPORT.md](RO_REPORT.md) §3). For dismech the equivalent
is to recognise cycles as loops rather than errors — which means they must first be told apart
from actual errors.

### At least one looks like a genuine error

```
MONDO:0003672
  posterior myocardial ischaemic cell death  --causes--> posterior ECG injury pattern
  posterior ECG injury pattern               --causes--> posterior myocardial ischaemic cell death
```

An ECG injury pattern is a **readout** of myocardial cell death, not a cause of it. The second
edge looks like a mis-specified predicate, and dismech already has a `readout` predicate (1,168
uses) that fits. This is US8: separating real loops from inverted edges is the prerequisite for
any temporal use of the causal graph.

---

## 4. Temporal metadata

`kb/disorders` holds 2,565 disorder records. Temporal fields, by frequency:

| field | count | form |
|---|---|---|
| `age_range` | 886 | **free text** — "Birth to first years of life", "Infancy through adulthood" |
| `clinical_course` | 839 | HP-mapped enum |
| `progression` | 827 | structured: `phase` + `age_range` + notes |
| `temporality` | 685 | HP-mapped enum (ACUTE, CHRONIC, RECURRENT, TRANSIENT, …) |
| `onset_category` | 425 | **HP onset vocabulary** |
| `onset` | 405 | |
| `duration` | 100 | |
| `stages` | 33 | disease stages (cancer staging, Long COVID phases) |
| `mean_age_years` / `max_age_years` | 43 | **numeric** |
| `life_cycle_stage_term` | 19 | OPL parasite stages, grounded |

`onset_category` uses the HP onset hierarchy verbatim:

```
CONGENITAL 126   INFANTILE 98   CHILDHOOD 78   NEONATAL 32   YOUNG_ADULT 29
JUVENILE 23      ANTENATAL 17   ADULT 14       MIDDLE_AGE 6   LATE 2
```

**This is the bridge to the stage work.** Those HP terms are logically defined against HsapDv
and resolve to a perfect interval partition of the human lifespan — see
[HP_ONSET_PROPOSAL.md](HP_ONSET_PROPOSAL.md). So dismech's onset categories are already
interval-anchored; the anchoring has simply never been followed through.

HsapDv itself appears only in dismech's schema, never in its data.

---

## 5. The blocker: onset is per-disease, not per-node

This is the single thing standing between dismech and useful temporal reasoning.

`onset_category` is a property of a **disorder record**. The causal graph is over **nodes** —
individual pathophysiology steps and phenotypes. To ask whether a causal edge is temporally
possible, you need onsets on both endpoints, and there is currently no per-node onset anywhere.

291 disorders have both a pathograph and onset data, so the intersection is real — it is the
granularity that is wrong, not the coverage.

Two routes, neither large:

1. **Per-node onset**, where evidence supports it. Phenotype nodes are HP-grounded, and HPOA
   already records onset per disease–phenotype pair — so for the phenotype half this is a join,
   not new curation.
2. **Propagate** the disease-level onset as a lower bound on every node in the graph, then
   tighten from evidence. Weaker, but free, and enough to catch gross inversions.

---

## 6. Action items

| # | Item | Owner | Impact |
|---|---|---|---|
| 1 | Classify the 46 causal cycles: real feedback loop vs inverted edge | dismech | Unblocks all temporal use; US8 |
| 2 | Consider an explicit `feedback_loop` annotation for confirmed cycles | dismech | Lets reasoners skip them rather than choke |
| 3 | Add per-node onset for HP-grounded phenotype nodes via HPOA join | dismech | Unblocks US9, US10 |
| 4 | Fix `MONDO:0003672` — ECG pattern is a `readout`, not a cause | dismech | One edge; example of the class |
| 5 | Add `starts_before`/`starts_after` and `causes ⊑ starts_before` | RO + dismech | ~33,500 edges gain temporal semantics |
| 6 | Axiomatise the HP onset partition | HPO | Unblocks contradiction detection; see [HP_ONSET_PROPOSAL.md](HP_ONSET_PROPOSAL.md) |

Items 1, 2 and 4 are dismech-internal and independent of everything else. Item 3 is the one
that turns the causal graph into a temporal one.

---

## 7. Caveats

**The cycle classification in §3 is a spot check, not an audit.** I inspected five of the 46 and
judged four to be genuine vicious cycles and one to be an error. The remaining 41 are
unclassified, and the ratio may not hold.

**`causes ⊑ starts_before` is the weakest safe reading**, and it may be too weak to be useful in
places. For `DIRECT` causal links a stronger claim might hold — possibly `meets`, if the effect
begins as the cause completes — but `causal_link_type` distinguishes directness of *evidence*,
not temporal contiguity, so nothing stronger is currently derivable from the data.

**Nothing here has been run against dismech as a reasoning artifact.** The counts and cycles are
measured; the proposed axioms have not been applied to dismech and tested, as they were for
Uberon. That is the obvious next step and would likely surface more of the §3 pattern.
