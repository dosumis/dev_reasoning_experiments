# EHDAA2: consistency of existence assertions

Testing [EHDAA2](http://purl.obolibrary.org/obo/ehdaa2.owl) (human developmental anatomy,
abstract v2) against the HsapDv Carnegie-stage backbone. EHDAA2 2024-01-11, HsapDv 2025-01-23,
Uberon-base 2026-06-19. Reproduce with `tests/ehdaa2_consistency.py` and `tests/dv_selfcheck.py`.

**Headline: EHDAA2 is in very good shape.** Its `develops_from` graph is acyclic over 1,958
structures, all 2,922 testable `part_of` containments hold, and all 1,058 start/end pairs are
coherent. The findings below are 50 ordering conflicts (2.4% of `develops_from`), a relation
choice that weakens every existence assertion, and four defects in the HsapDv backbone it
depends on.

---

## 1. What EHDAA2 contains

| | |
|---|---|
| live classes | 2,456 |
| `part_of` | 2,983 |
| `starts_at` (RO:0002496) | **2,445** |
| `develops_from` | 2,125 |
| `ends_at` (RO:0002497) | **1,058** |
| `located_in` / `develops_in` / other | 202 |
| distinct Carnegie stages referenced | 23 (CS01–CS20, plus CS05a/b/c, CS06a/b) |

**3,503 stage assertions** — by a wide margin the densest anatomy↔stage linkage available.
Uberon has 80.

| existence coverage | |
|---|---|
| structures with a start | 2,445 |
| structures with **both** start and end | 1,058 |
| start only, end unconstrained | 1,387 |

---

## 2. The relation choice weakens every assertion

EHDAA2 declares its own labels for two RO properties, and they do not match RO's semantics:

| IRI | EHDAA2 label | RO label | Meaning |
|---|---|---|---|
| RO:0002496 | `starts_at` | existence starts during **or after** | `start(X) ≥ start(S)` |
| RO:0002497 | `ends_at` | existence ends during **or before** | `end(X) ≤ end(S)` |

`starts_at` reads as exact; RO:0002496 is a **one-sided lower bound**. The two-sided relations
— RO:0002488 `existence starts during` and RO:0002492 `existence ends during` — are almost
certainly what was meant.

This is not cosmetic. **Under the semantics as asserted, EHDAA2's existence assertions cannot
contradict anything**, because a one-sided bound lets a structure start arbitrarily late:

| Check | As asserted (one-sided) | As intended (two-sided) |
|---|---|---|
| structure starts before it ends | 0 | 0 |
| `part_of` containment (2,922 pairs) | 0 | 0 |
| `develops_from` ordering (2,125 pairs) | **0 — undetectable** | **50** |

Every violation found below is invisible under the literal reading. Switching to RO:0002488 /
RO:0002492 would make 3,503 assertions genuinely constraining at a stroke, and is the single
highest-value change available here.

> **Partial correction.** For an indexed *family* whose members start at different stages, a
> one-sided bound is the correct class-level summary — `starts_during some CS09` would be false
> of somite 39. But that covers at most **17 of 65 families**; the other 48 have all members at
> one stage, and 2,095 of the 2,445 assertions are singletons where the one-sided predicate is
> simply weak. See [IDEALISED_INDIVIDUALS.md](IDEALISED_INDIVIDUALS.md) §5.

*(Caveat: an earlier version of this test reported the 50 under both readings. That was a bug —
it computed the two-sided upper bound and never used it. The distinction above is the whole
point of the section, so it is worth stating that it was nearly missed.)*

---

## 3. What checks out

Worth stating plainly before the problems.

- **`develops_from` is acyclic** across 1,958 structures and 2,125 edges. No cycles at all —
  unlike dismech's causal graph (46 cyclic pathographs) or the trap in Uberon's
  `developmentally_preceded_by` branch.
- **All 2,922 testable `part_of` containments hold.** No part starts before its whole or ends
  after it.
- **All 1,058 start/end pairs are coherent.** No structure is asserted to start after it ends.
- **Exactly one stage assertion per structure** — no term carries conflicting `starts_at` or
  `ends_at` assertions.

For an ontology of this size with no formal consistency checking in its pipeline, that is a
good result.

---

## 4. The 50 `develops_from` ordering conflicts

Read with the intended two-sided semantics, 50 of 2,125 `develops_from` assertions (2.4%) place
a product's existence **provably before** its precursor's.

```
gap between product's start-stage and precursor's:
   1 stage    36  ████████████████████████████████████
   2 stages    5  █████
   3 stages    3  ███
   4 stages    1  █
   5 stages    2  ██
   7 stages    1  █
   8 stages    2  ██
```

### (a) The somite series — 16 edges, one decision

```
 8×  myotome NN    develops_from  dermomyotome NN     (CS10 vs CS11)
 8×  dermatome NN  develops_from  dermomyotome NN     (CS10 vs CS11)
```

Both derivatives are assigned CS10 while their precursor is assigned CS11. Repeated identically
across all eight somites, so this is one curation decision rather than sixteen slips — most
likely the dermomyotome's `starts_at` is a stage too late, since myotome and dermatome cannot
precede it.

### (b) Blood and the later haematopoietic sites — the type/token problem again

```
blood        (CS06a)  develops_from  spleen                (CS13)   8 stages
blood cells  (CS06a)  develops_from  liver haemangioblasts (CS13)   8 stages
blood        (CS06a)  develops_from  liver                 (CS12)   7 stages
```

These are not errors of fact. Blood first appears in the yolk sac at CS06a; later waves of
haematopoiesis arise in liver and spleen. The conflict comes from asserting both about **blood
as a type**: the type starts at CS06a, but *some instances* of it develop from the liver much
later.

This is the third independent appearance of the same pattern in this project — after reciprocal
induction in Uberon and vicious cycles in dismech ([USER_STORIES.md](USER_STORIES.md) §4).
Type-level relations cannot carry start-order semantics where the type recurs.

The fix here is representational, not a correction: either the later waves need their own terms
(`liver-derived blood cell`), or the relation should be `develops_in` — which EHDAA2 already
uses, 33 times.

All five of EHDAA2's indexed `develops_from` families are 100% index-matched and complete, so
they promote soundly to class level — see [IDEALISED_INDIVIDUALS.md](IDEALISED_INDIVIDUALS.md) §4.

**The somite cases in (a) are a different problem with a known shape.** Myotome and dermatome
delaminate from a dermomyotome that persists — the precursor does not cease. Tested directly,
**417 of 1,538 (27.1%)** of EHDAA2's `develops_from` assertions are of this kind. That is the
`differentiation` category of [`end-bound-convention.md`](https://github.com/dosumis/Uberon_HDCA_stage_axioms/blob/evidence-pipeline/docs/end-bound-convention.md)
and the missing `⊑ starts_during` subproperty of
**[DEVELOPMENTAL_RELATIONS.md](DEVELOPMENTAL_RELATIONS.md)**.

### (c) Individually plausible errors

```
5 stages  pleuroperitoneal membranes      (CS11)  <-  diaphragm body wall component (CS16)
5 stages  1st arch maxillary ectoderm     (CS10)  <-  frontonasal process epithelium (CS15)
4 stages  facial VII nerve                (CS13)  <-  facial VII ganglion            (CS17)
3 stages  pulmonary artery                (CS14)  <-  outflow tract pulmonary artery (CS17)
3 stages  coecum mesentery                (CS14)  <-  appendix associated mesenchyme (CS17)
3 stages  inferior vena cava post-hepatic (CS15)  <-  supracardinal vein left        (CS18)
```

Each needs a curator's eye. The facial VII case is the most suspect — a nerve asserted to exist
four stages before its ganglion.

The 36 one-stage gaps are a different matter: they may be genuine, or an artifact of stage
assignment being coarser than the biology. They are worth a sweep but not individually alarming.

---

## 5. Four defects in the HsapDv backbone

Found while building the Carnegie backbone. These affect anything that depends on HsapDv, not
just EHDAA2. `tests/dv_selfcheck.py`.

### (a) `Carnegie stage 05a` is both inside and after `Carnegie stage 05`

```
Carnegie stage 05a  part_of                  Carnegie stage 05
Carnegie stage 05a  immediately_preceded_by  Carnegie stage 05
```

`part_of` on stages is temporal containment (Allen `d`); `immediately_preceded_by` is Allen `M`.
**`d ∩ M = ∅`** — a term cannot be inside another and also begin exactly where it ends.

CS05a is the first sub-stage of CS05, so the correct assertion is
`immediately_preceded_by Carnegie stage 04` — which is the pattern CS06a already follows
(`immediately_preceded_by Carnegie stage 05c`, not its own parent CS06).

This bug has teeth: it silently broke the first version of my backbone, because CS05's
"successor" in the precedence chain became CS05a, which carries no bounds, so CS05 lost its end.

### (b) `centenarian stage` spans one year

`centenarian stage` = `[100, 101)` ypb, yet these are asserted `part_of` it:

```
eleventh decade stage  [100, 110)
110-year-old stage     [110, 111)
111 / 112 / 113 / 114-year-old stages
```

Six containment violations. Either `centenarian stage` should be open-ended from 100 ypb, or
those terms belong elsewhere.

### (c) `juvenile stage` (MmusDv) spans one day

`juvenile stage` = `[23, 24)` dpb, with 24-, 25-, 26-, 27-day and 4-, 5-week stages asserted
`part_of` it. Six violations. Mouse juvenile stage is conventionally ~3 weeks to sexual
maturity.

### (d) `25-day-old stage` (MmusDv) has the wrong number

```
25-day-old stage   start_dpb = 21.0   end_dpb = 22.0
```

A copy of `21-day-old stage`. All 16 other mouse day-stages match their labels exactly.
Unambiguous, one-line fix.

### A methodological note

An earlier run of this check reported **21** containment violations. Most were my own artifact:
I compared intervals across reference frames, and `dpf` vs `dpc` differ by ~0.5 day while the
week and month post-birth series do not tile identically. `17-week-old` is correctly inside
`4-month-old` when both are read in `dpb`; it looks wrong if one is converted from `mpb`.

The check now compares only within a frame both terms share, which costs coverage — 45 of 237
HsapDv pairs and 67 of 132 MmusDv pairs become untestable — but every surviving violation is
real. **Frame discipline is not optional when ontologies carry several parallel series.**

---

## 6. Uberon integration

EHDAA2 itself carries **no outgoing xrefs at all**. The mapping is held entirely on the Uberon
side:

| | |
|---|---|
| Uberon classes xreffing EHDAA2 | 1,781 |
| distinct EHDAA2 terms referenced | 1,468 |
| of EHDAA2's 2,456 live classes | **1,361 (55%)** |

So just over half of EHDAA2 is reachable from Uberon, one-directionally. This is the same shape
as the cross-species stage bridges, which live in `developmental-stage-ontologies` rather than
in the DV ontologies themselves — easy to miss if you look only at the artifact you are working
with.

**What this unlocks.** Uberon has 80 `existence_*` assertions at gross stage granularity
([USER_STORIES.md](USER_STORIES.md) §4), and US1/US2 answer coarsely because of it. EHDAA2 has
3,503 at Carnegie-stage granularity for 55%-mapped structures. Routing through those xrefs is
the most direct available fix for the precision problem in the strongest user story —
**a ~44× increase in stage-anchored assertions for the human embryonic window.**

---

## 7. Action items

| # | Item | Owner | Impact |
|---|---|---|---|
| 1 | Switch `starts_at`/`ends_at` to RO:0002488/RO:0002492 | EHDAA2 | Makes 3,503 assertions constraining instead of vacuous |
| 2 | Review the 16 somite edges — dermomyotome's stage looks one too late | EHDAA2 | One decision, 16 edges |
| 3 | Re-model blood/haematopoiesis: separate terms per wave, or `develops_in` | EHDAA2 | Removes the 3 largest conflicts |
| 4 | Curator review of the 6 mid-sized gaps, esp. facial VII nerve/ganglion | EHDAA2 | |
| 5 | Fix `Carnegie stage 05a`'s `immediately_preceded_by` → CS04 | HsapDv | Breaks downstream chain-walking |
| 6 | Fix `centenarian stage` bounds | HsapDv | 6 containment violations |
| 7 | Fix `juvenile stage` bounds | MmusDv | 6 containment violations |
| 8 | Fix `25-day-old stage` → `start_dpb` 25.0 | MmusDv | Typo |
| 9 | Route Uberon's 80 existence assertions through EHDAA2 xrefs | Uberon / this repo | US1 precision |

Items 5–8 are small and independent of everything else.

---

## 8. Caveats

**The 23 Carnegie stages have `start_dpf` but no `end_dpf`.** Ends are derived as the next
stage's start — the same propagation used for Theiler stages. Sound, but it means CS23's end
(taken as 60 dpf) is an assumption, not data.

**CS05a/b/c and CS06a/b carry no bounds at all** and inherit their parent's interval. Any
assertion resting on them is bounded, not exact — which is why the blood cases (`CS06a`) should
be read as "somewhere in [13, 15) dpf".

**`part_of` on anatomical structures is read here as temporal containment of existence.** That
is right for stages and reasonable for structures, but it is an assumption EHDAA2 does not
state. Zero violations may partly reflect a test that is weaker than it looks.

**Nothing was run through an OWL reasoner.** These are interval checks over extracted
assertions, not DL consistency. EHDAA2 is not axiomatised for the latter — which was the
premise of the exercise.
