# Idealised individuals, and promoting instance-level conclusions

A proposal for representing countable anatomical parts as **individuals of an idealised
organism** — one canonical specimen per species, as a standard atlas depicts it — and asserting
timing relations between those individuals rather than between classes.

The payoff is not the representation itself. It is that **conclusions reached at instance level
can be promoted back to sound class-level axioms**, including exact relations that cannot
currently be asserted at all.

Measured against EHDAA2 2024-01-11 and HsapDv 2025-01-23. Reproduce with
`tests/individuation.py`; the per-somite offsets in §9 come from
`tests/ehdaa2_consistency.py`.

---

## 1. The proposal in brief

Anatomy ontologies are read as describing an idealised individual. Where a part occurs once per
organism — or as a bilateral pair developing in sync — it is modelled as an **individual**, not
a class. Timing relations between those individuals are ordinary object property assertions:

```
myotome-08  immediately_preceded_by  dermomyotome-08
```

Non-countable parts keep the class-level representation. Most structure-to-cell-type relations
fall here: cells are not countable per organism, so `CL` linkage stays as it is. The result is a
**declared hybrid**, with the individual layer generated and scoped to an enumerated subset.

---

## 2. Two problems this addresses

### (a) The type/token problem

Three independent instances in this project, all of the same shape — a type-level relation that
is cyclic or temporally contradictory because the type recurs while the tokens do not:

| | |
|---|---|
| Uberon | `metanephric mesenchyme` ⇄ `ureteric bud`, reciprocal induction ([RO_REPORT.md](RO_REPORT.md) §3) |
| dismech | 46 pathographs with causal cycles ([DISMECH_REPORT.md](DISMECH_REPORT.md) §3) |
| EHDAA2 | `blood` starts CS06a yet `develops_from` spleen (CS13) ([EHDAA2_REPORT.md](EHDAA2_REPORT.md) §4b) |

Individuals force the disambiguation at assertion time instead of producing contradictions at
reasoning time. There is one `blood-of-the-idealised-embryo`, and the question "which blood?"
has to be answered before the assertion can be written.

### (b) Class-level assertions are irreducibly lossy

A class axiom must hold of every instance, so where instances differ it can only state what they
have in common. Measured in EHDAA2:

| family | start stages spanned |
|---|---|
| `somite` | CS09 – CS13 (5 stages) |
| `dermomyotome`, `sclerotome`, `dermatome`, `myotome` | CS10 – CS13 (4 stages) |

"Somite starts during X" is unstatable as a point claim. The instances carry information the
class cannot represent, and no amount of care at class level recovers it.

---

## 3. EHDAA2 already does this for a fifth of its terms

This is not hypothetical. Of 2,459 EHDAA2 terms, **469 (19%) are individuated in all but name**:

```
label ends in an index    262    dermomyotome 01 … dermomyotome 39
label carries an ordinal   58    1st arch, 1st arch artery, 1st arch pouch endoderm
label carries laterality  153    4th arch artery left, precardinal vein right
```

The indexed ones collapse into 23 families — somite, sclerotome, dermomyotome at 39 members
each, dermatome and myotome at 35, ribs at 12. Counting ordinals and laterality gives **349
members across 65 families**, against 2,110 singletons.

The convention is stable, legible and already curated. What is missing is any machinery that
treats these as what they are.

---

## 4. The promotion rule

```
promote   C ⊑ R some D    iff    ∀c ∈ inst(C)  ∃d ∈ inst(D) :  c R d
```

All-some is exactly what an OWL class axiom already means, so the promotion target is native —
no new machinery on the receiving end, and the result is an ordinary Uberon axiom.

### What licenses it: the idealisation creates a closed world

There are exactly 39 somites, not an unknown number. Checking a universal over instances is only
sound if the instance set is complete, and **the idealised individual is what makes it
complete**. Against real-world instances OWL's open world would always admit the case you had
not seen, and no union or universal could ever be taken safely.

So the closed world is not a convenience bolted on afterwards. It is the thing that makes
promotion legitimate, and it comes directly from the idealisation.

### Measured: all five indexed `develops_from` families promote

```
sclerotome   ⊑ develops_from some somite               ✓  39/39 index-matched, complete
dermomyotome ⊑ develops_from some somite               ✓  39/39
myotome      ⊑ develops_from some dermomyotome         ✓  35/35
dermatome    ⊑ develops_from some dermomyotome         ✓  35/35
rhombomere   ⊑ develops_from some early rhombomere     ✓   8/8
```

Every family is 100% index-matched with no unpaired members, so the universal holds and all five
promote soundly.

### Exact relations survive promotion

This is the part worth the effort. Suppose instance-level evidence establishes

```
myotome-08  metBy  dermomyotome-08          Allen M — a singleton
```

At class level `myotome M dermomyotome` is plainly **false**: somite 8's myotome does not meet
somite 26's dermomyotome. But the all-some form

```
myotome ⊑ metBy some dermomyotome
```

**is true**, because each myotome is met by *its own* dermomyotome. Index-matching supplies the
per-instance witness that the existential needs.

So promotion does not merely recover the weak class-level claim. It can yield **exact class-level
relations that are not otherwise assertable** — a 1-of-13 relation where the current
representation forces a 5-of-13 disjunction or a one-sided bound.

(To be clear about what is and is not shown: the *structural* precondition is measured — all
five families are complete and index-matched. Whether EHDAA2's current data supports `metBy`
specifically is a separate question, and at Carnegie-stage granularity it does not — see §9.)

### What does not promote

- **Instance-level errors.** The 16 bad somite pairs in [EHDAA2_REPORT.md](EHDAA2_REPORT.md) §4a
  are data bugs. There is no class-level fact to lift.
- **Point timings.** The family spread washes them out. What promotes is an envelope,
  `[min start, max end]` over the members.

---

## 5. A correction this forces to EHDAA2_REPORT §2

[EHDAA2_REPORT.md](EHDAA2_REPORT.md) §2 criticises EHDAA2's blanket use of the one-sided
RO:0002496 / RO:0002497. The envelope case above partly vindicates it: for a *family*,
`existence_starts_during_or_after CS09` is the correct class-level summary, because a two-sided
`starts_during some CS09` would be false of somite 39.

But the carve-out is small:

| | |
|---|---|
| terms with a `starts_at` assertion | 2,445 |
| **singletons** — one-sided needlessly weak | **2,095** |
| family members | 349, in 65 families |
| families whose members all start at the **same** stage — one-sided needlessly weak | **48 of 65** |
| families whose members **spread** — one-sided defensible | **17 of 65** |

So the criticism stands for the overwhelming majority, and the one-sided predicate is defensible
for at most 17 families. Even there it is not forced: `starts_during some (CS09 or CS10 or CS11
or CS12 or CS13)` is both two-sided and exact, and OWL expresses it without difficulty.
One-sided is easier, not necessary.

---

## 6. Scope: what becomes an individual

| | |
|---|---|
| **Individual** | occurs once per organism (heart, notochord); or a bilateral pair developing in sync (kidney, optic vesicle); or an indexed series member (somite 08, 3rd arch) |
| **Stays a class** | non-countable masses (mesenchyme), unenumerated repeats (capillaries, hair follicles), and essentially all cell types |

**Bilateral pairs are not a problem.** Where the pair develops in sync, one individual is correct
for timing purposes and simpler than two. The laterality question is a different use case, served
by the class-level representation that remains.

The one exception class is genuinely **asymmetric** development — heart looping, gut rotation,
situs determination. Those need the pair split, which is an exception list rather than a
different model.

---

## 7. Where the reasoning happens: outside OWL

Individuals *inside* OWL buy little. Punning keeps the class and individual views semantically
separate, so no inference flows between them; ABox reasoning does not scale in EL, where the
profile's value is class-level inheritance of bounds; and OWL still cannot do the interval
reasoning regardless — no object-property intersection, no elimination, and the regularity wall
on property chains ([README.md](README.md) §5).

Individuals **outside** OWL buy the whole thing. Instance-level intervals with endpoints are a
Simple Temporal Problem: polynomial, and measured at roughly **two to three orders of magnitude**
more throughput than the OWL/SWRL route — ~100–500 intervals there against ~10⁴ relations in
under ten seconds for a dedicated constraint solver.

So the architecture is the two-layer one already argued for, with individuals living only in the
second layer:

| layer | holds | role |
|---|---|---|
| Uberon classes + GCIs | the source of truth, hand-curated | interoperability, inheritance, materialisation |
| generated individuals | a build artifact | exact interval reasoning, consistency checking |
| promoted axioms | generated, fed back | exact class-level relations for layer one |

Nothing is punned, humans curate only what they curate today, and the promoted axioms re-enter
layer one as ordinary all-some class axioms.

---

## 8. Implementation

[`Uberon_HDCA_stage_axioms`][repo] already has the generation pattern: `expand.ru` names the
left-hand side of a GCI so that relation-graph has something to attach an edge to, run as a
SPARQL update **over the artefact** rather than as another output of the table generator. The
same shape extends to generating individuals for a declared subset and deriving OPAs from
selected Uberon `SubClassOf` axioms.

**One non-obvious requirement: pair by index, not cross-product.** A class-level
`myotome develops_from dermomyotome` expands to 35 OPAs if index-matched and 35 × 35 = 1,225
spurious ones if not. EHDAA2 already holds them index-matched, so there the generator can lift
directly; for Uberon's class-level assertions the family correspondence has to be declared.

That is a **small tagging surface** — one declaration per family pair, not per member. 23 indexed
families, 65 counting ordinals and laterality.

[repo]: https://github.com/dosumis/Uberon_HDCA_stage_axioms

---

## 9. Caveats

**The timing vocabulary has to be fine enough to exploit the individuation.** This is the
sharpest limit. Across all 148 per-somite `develops_from` pairs with both start stages known:

```
product starts EARLIER than precursor :  16/148
product starts in the SAME stage      : 119/148
product starts later                  :  13/148
```

Carnegie stages run 2–5 days; human somites form roughly one pair every six hours. **The stages
cannot resolve what individuation exposes.** Against stage granularity alone, individuating the
somite series gains almost nothing.

There is a natural resolution: **somite number is itself a clock.** Embryologists stage by somite
count, so `somite 12 exists` is already a finer temporal statement than any Carnegie stage.
Individuation and the timing backbone converge rather than compete — but the gain is conditional
on exploiting that, and it should be part of any trial rather than an afterthought.

**It does not fix bad data.** The 16 violations above are errors at the individual level too.
What individuation buys is *localisation* — currently the class-level view cannot say which
somites are wrong.

**It only reaches anatomy.** Of the stories needing full interval reasoning
([USER_STORIES.md](USER_STORIES.md) §2), US5 benefits substantially; US7 is already token-level
(cells); US3 and US9 concern phenotype onset and disease mechanisms, which are not parts of an
organism and are untouched by this.

**Cross-organism variation is erased by construction.** Fine for "what was forming at E9", wrong
for "is this specimen normal". Note the idealisation handles *within*-organism variation (somite
08 vs somite 26) well, and discards *between*-organism variation entirely.

**Which atlas, versioned how.** One canonical reference per species, kept in step with Uberon's
class churn. An ongoing commitment, not a one-off.

---

## 10. A proposed trial

[`Uberon_HDCA_stage_axioms`][repo], on an experimental branch, is the natural test-bed — the
generation machinery is there and the taxon-scoping problem is already solved properly.

Smallest experiment that would settle whether this is worth pursuing:

1. Generate individuals for the five indexed `develops_from` families (156 members).
2. Assert instance-level timing, **using somite count as the clock** rather than Carnegie stages.
3. Run the promotion rule and emit the class-level axioms.
4. Compare against what EHDAA2 asserts today: does promotion yield anything that is both new and
   exact?

Step 4 is the test. If promotion returns only the one-sided bounds already present, the
individuation has bought localisation and nothing more — useful, but not worth the machinery. If
it returns exact all-some relations, it has produced axioms Uberon cannot currently state at all.
