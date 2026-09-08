# Proposal: axiomatising the HP onset vocabulary as intervals

HP's onset terms already carry logical definitions against HsapDv. This proposal shows that
those definitions resolve to a **perfect interval partition of the human lifespan**, and that
adding a small number of axioms would make that structure available to reasoners — enabling
contradiction detection over onset annotations in HPO, dismech and anywhere else the vocabulary
is used.

Measured against **HP 2026-09-01** and **HsapDv 2025-01-23**. Reproduce with
`tests/hp_onset_intervals.py`.

---

## 1. The alignment already exists

Ten HP onset terms are defined by an equivalence axiom against HsapDv:

```
Infantile onset  ≡  Onset  and  (existence starts during some HsapDv:0000261 "infant stage")
```

The relation is `existence starts during` (RO:0002488), whose Allen semantics is `dfO` —
*start(X) lies strictly inside Y*. So each onset term is already an interval constraint; it has
simply never been treated as one.

| HP term | | HsapDv target |
|---|---|---|
| Embryonal onset | HP:0011460 | embryonic stage |
| Fetal onset | HP:0011461 | fetal stage |
| Antenatal onset | HP:0030674 | prenatal stage |
| Neonatal onset | HP:0003623 | newborn stage (0–28 days) |
| Infantile onset | HP:0003593 | infant stage |
| Childhood onset | HP:0011463 | child stage (1–4 yo) |
| Young adult onset | HP:0011462 | young adult stage |
| Adult onset | HP:0003581 | adult stage |
| Middle age onset | HP:0003596 | middle aged stage |
| Late onset | HP:0003584 | late adult stage |

**Not defined against HsapDv**: `Juvenile onset` (HP:0003621), `Pediatric onset` (HP:0410280),
`Congenital onset` (HP:0003577).

## 2. Following the definitions yields numeric intervals

HsapDv carries machine-readable endpoint annotations (`start_dpf`/`end_dpf`,
`start_ypb`/`end_ypb`, …), so each onset term resolves to a numeric window. Normalising to days
post-fertilization (birth = 266 dpf):

| Onset term | Interval (days post-fert.) | |
|---|---|---|
| Embryonal | [0, 56) | |
| Fetal | [56, 266) | |
| Antenatal | [0, 266) | = Embryonal ∪ Fetal |
| Neonatal | [266, 294) | |
| Infantile | [294, 631) | |
| Childhood | [631, 2092) | |
| *Juvenile* | *[2092, 5745)* | from prose only |
| Young adult | [5745, 14876) | |
| Middle age | [14876, 22181) | |
| Late | [22181, ∞) | open — HsapDv gives no end |
| Adult | [5745, ∞) | open |

**8 of 10 resolve to fully bounded intervals.** `Adult onset` and `Late onset` are open-ended
because `adult stage` and `late adult stage` have a `start_ypb` but no end — defensible, since
the end is death.

## 3. The series is a perfect partition — verified

Consecutive terms stand in Allen `m` (**meets**) — each ends exactly where the next begins, with
no gap and no overlap:

```
Antenatal   m  Neonatal   m  Infantile   m  Childhood
            m  Juvenile   m  Young adult m  Middle age  m  Late
```

All seven checks pass. The coarser terms nest exactly, giving a second granularity level:

```
Embryonal    s (starts)    Antenatal
Fetal        f (finishes)  Antenatal     →  Embryonal m Fetal, together spanning Antenatal
Young adult  s (starts)    Adult
Middle age   d (during)    Adult
```

(`Pediatric onset` is omitted: it has no HsapDv definition, so its interval cannot be derived —
see §4a.)

This is the same two-level structure HsapDv itself has, and it is **entirely derivable from data
already published**. Nothing here is new curation — it is existing content made computable.

---

## 4. What is missing

### (a) Three terms lack HsapDv definitions

| Term | | Proposed |
|---|---|---|
| `Juvenile onset` | HP:0003621 | `existence starts during some HsapDv:0000271` (juvenile stage 5–14 yo) — its prose already says "between the age of 5 and 15 years", which tiles exactly between Childhood and Young adult |
| `Pediatric onset` | HP:0410280 | a union or a `part_of`-style grouping over Neonatal…Juvenile; prose says "before the age of 16 years" |
| `Congenital onset` | HP:0003577 | **not an interval** — "present at birth" is an instant. Model with `time:Instant` at 266 dpf, or as `existence starts during` the newborn stage if the intent is a window |

`Juvenile onset` is the important one: without it there is a hole in an otherwise perfect
partition, and it is the fifth most-used category in dismech (23 uses).

### (b) No relations between the onset terms

The partition is real but **entirely implicit**. HP asserts nothing relating one onset term to
another — checked: zero `disjointWith` among them, no `precedes`/`preceded_by`.

Proposed, following the structure verified in §3:

```
Neonatal onset     immediately_preceded_by  Antenatal onset
Infantile onset    immediately_preceded_by  Neonatal onset
Childhood onset    immediately_preceded_by  Infantile onset
Juvenile onset     immediately_preceded_by  Childhood onset
Young adult onset  immediately_preceded_by  Juvenile onset
Middle age onset   immediately_preceded_by  Young adult onset
Late onset         immediately_preceded_by  Middle age onset

Fetal onset        immediately_preceded_by  Embryonal onset
```

`immediately_preceded_by` (RO:0002087) is exactly Allen `metBy`, which is what §3 verified.

### (c) No disjointness — so no contradiction is detectable

This is the axiom that does the work. Without it, "congenital onset" and "adult onset" on the
same annotation is not an error, merely two facts.

```
AllDisjointClasses(
   Antenatal onset, Neonatal onset, Infantile onset, Childhood onset,
   Juvenile onset, Young adult onset, Middle age onset, Late onset )

AllDisjointClasses( Embryonal onset, Fetal onset )
```

Declared **only within a granularity level**. `Antenatal` and `Fetal` are *not* disjoint —
Fetal is part of Antenatal — and asserting otherwise would make the ontology inconsistent.

### (d) Two HsapDv stages have no end bound

`adult stage` and `late adult stage` carry `start_ypb` but no `end_ypb`. Optional, and arguably
correct as-is; if a closed interval is wanted, an explicit upper bound (say 122 ypb, the maximum
recorded human lifespan) would make every onset term fully bounded.

---

## 5. Why this is worth doing

Three user stories in [USER_STORIES.md](USER_STORIES.md) turn on it — **US3** (catching
impossible onset annotations in HPO), **US9** and **US10** (the dismech causal stories, see
[DISMECH_REPORT.md](DISMECH_REPORT.md)). dismech alone uses this vocabulary 425 times across 10
categories.

More concretely, (b) and (c) together make these queries answerable:

- *Is this annotation self-consistent?* — an annotation asserting both congenital and adult
  onset becomes an OWL inconsistency rather than a silent contradiction.
- *Does the onset of this phenotype precede the onset of its causal antecedent?* — inverted
  causality, detectable because the onset terms are ordered.
- *Which onset categories are compatible with "first seen at 3 years"?* — interval containment,
  answerable numerically once the bounds are followed.

None of that needs new curation. §3's structure is already implied by the existing equivalence
axioms; the proposal is to **assert what the data already entails** so that reasoners can use it.

---

## 6. Caveats

**The disjointness axioms in (c) will surface existing annotation conflicts.** That is the
point, but it means the change should land with a QC pass rather than silently — some
annotations will turn out to assert two incompatible onsets, and those need triage, not an
automatic fix.

**One granularity mismatch to check.** `Childhood onset` is defined against `child stage
(1–4 yo)`, giving [631, 2092) — ages 1–5. HP's own prose for the sibling `Juvenile onset` says
"between the age of 5 and 15", which tiles correctly, but users reading "childhood" may expect
it to extend further. The interval is what the axiom says; the label may mislead. Worth a
definition clarification alongside the axioms.

**`Congenital onset` is an instant, not an interval**, and does not belong in the partition.
Placing it there would be wrong; leaving it out means annotations using it are not covered by
the disjointness axioms. It needs its own treatment.
