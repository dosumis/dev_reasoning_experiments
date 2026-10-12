# Idealised individuals, and promoting instance-level conclusions

A proposal for representing countable anatomical parts as **individuals of an idealised
organism** — one canonical specimen per species, as a standard atlas depicts it — and asserting
timing relations between those individuals rather than between classes.

The payoff is not the representation itself. It is that **conclusions reached at instance level
can be promoted back to sound class-level axioms**, including exact relations that cannot
currently be asserted at all.

Measured against EHDAA2 2024-01-11, HsapDv 2025-01-23, and the curated axiom table in
[`Uberon_HDCA_stage_axioms`][repo]. Reproduce with `tests/individuation.py` (§3, §4, §6),
`tests/pharyngeal_arches.py` (§5), `tests/singleton_chains.py` (§6) and
`tests/ehdaa2_consistency.py` (§11).

[repo]: https://github.com/dosumis/Uberon_HDCA_stage_axioms

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

## 2. The problem: class-level assertions are irreducibly lossy

A class axiom must hold of every instance, so where instances differ it can only state what they
have in common. The information in the instances is not merely unrecorded — it is **unstatable**
at class level, and no amount of care recovers it.

Measured in EHDAA2, the start stages spanned by a single class:

| family | start stages spanned |
|---|---|
| `somite` | CS09 – CS13 (5 stages) |
| `dermomyotome`, `sclerotome`, `dermatome`, `myotome` | CS10 – CS13 (4 stages) |

"Somite starts during X" cannot be said as a point claim. §5 shows the same thing on curated
data with *both* endpoints, where the loss is sharper still.

A secondary motivation is the type/token problem — type-level relations that go cyclic or
contradictory because the type recurs while its tokens do not. Individuation forces the
disambiguation at assertion time. But the clear cases there are collective masses and
signalling relations that sit outside the countable core this proposal addresses, and some are
better fixed by restructuring RO (see [RO_REPORT.md](RO_REPORT.md) §3). It is a reason to
expect this to help, not the argument for it.

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

This is the part worth the effort.

**The assertion is a developmental relation, not a bare Allen one.** An OPA between individuals
uses the BFO/RO relation that fits the biology; the Allen relation follows as an *entailment*
from the subproperty axioms in
[DEVELOPMENTAL_RELATIONS.md](DEVELOPMENTAL_RELATIONS.md) §4:

```
asserted   myotome-08  immediate_transformation_of  dermomyotome-08
entails    myotome-08  immediately_preceded_by      dermomyotome-08     Allen M, a singleton
```

Nothing new is asserted about time. The timing is what the developmental relation *means*, made
computable.

At class level `myotome M dermomyotome` is plainly **false**: somite 8's myotome does not meet
somite 26's dermomyotome. But the all-some form

```
myotome ⊑ immediate_transformation_of some dermomyotome
myotome ⊑ immediately_preceded_by      some dermomyotome
```

**is true**, because each myotome is met by *its own* dermomyotome. Index-matching supplies the
per-instance witness that the existential needs.

So promotion does not merely recover the weak class-level claim. It can yield **exact
class-level relations that are not otherwise assertable** — a 1-of-13 relation where the current
representation forces a disjunction.

### What does not promote

- **Instance-level errors.** The 16 bad somite pairs in [EHDAA2_REPORT.md](EHDAA2_REPORT.md) §4a
  are data bugs. There is no class-level fact to lift.
- **Point timings.** The family spread washes them out. What promotes is an envelope,
  `[min start, max end]` over the members.

---

## 5. Worked example: the pharyngeal arch series

The clearest demonstration comes from curated data in
[`Uberon_HDCA_stage_axioms`][repo] — `src/axioms.tsv`, sourced from O'Rahilly & Müller — where
both endpoints are stated against HsapDv Carnegie stages.

### The existence axioms

```
pharyngeal arch 1          starts_during CS10   ends_during CS17     [22.0, 44.0) dpf
pharyngeal arch 2          starts_during CS10   ends_during CS17     [22.0, 44.0)
pharyngeal arch 3          starts_during CS11   ends_during CS17     [23.0, 44.0)
pharyngeal arch 4          starts_during CS12   ends_during CS17     [26.0, 44.0)
pharyngeal arch 6          starts_during CS12   ends_during CS17     [26.0, 44.0)

pharyngeal arch artery 1   starts_during CS10   ends_during CS12     [22.0, 28.0)
pharyngeal arch artery 2   starts_during CS10   ends_during CS13     [22.0, 31.0)
```

Nothing here is new curation. These are the existence axioms as written, resolved through the
Carnegie backbone's numeric bounds.

### What falls out at instance level

Each artery is `part_of` its own arch. `part_of` alone entails only temporal containment — the
label `dfse`, four possibilities. But with both endpoints known, the relation is **exact**:

```
artery 1  vs  arch 1   ->  s      (starts: same onset, artery ends first)
artery 2  vs  arch 2   ->  s
```

And the arches against each other:

```
       arch1 arch2 arch3 arch4 arch6
arch1    e     e     F     F     F
arch2    e     e     F     F     F
arch3    f     f     e     F     F
arch4    f     f     f     e     e
arch6    f     f     f     e     e
```

Three relations, `{F, e, f}` — which is the label **`Fef`**, one of the 29
([README.md](README.md) §4), and it means exactly *"ends with"*. **All pharyngeal arches end at
the same time; their onsets stagger.** That is a real, non-obvious fact about the series,
derivable only from the instances.

### Why class level cannot say it

Cross-index, the artery relation is different:

```
artery 1  vs  arch 3   ->  o
artery 1  vs  arch 4   ->  o
artery 2  vs  arch 4   ->  o
```

So `pharyngeal arch artery` stands in `{s, o}` to `pharyngeal arch` taken as classes. A
class-level relation would have to be that disjunction — or, as EHDAA2 does, a one-sided bound
that constrains almost nothing.

### What promotion returns

```
pharyngeal arch artery  ⊑  part_of some pharyngeal arch        ← already assertable
pharyngeal arch artery  ⊑  starts  some pharyngeal arch        ← NEW, exact, Allen s
pharyngeal arch         ⊑  ends_with some pharyngeal arch      ← NEW, exact, Allen Fef
```

The second and third are sound by the §4 rule — every artery starts *its own* arch, every arch
ends with *some* arch — and neither is statable today. The first is what Uberon already has.

**This is the whole proposal in one case**: existence axioms against a stage ontology, resolved
to numeric intervals, read at instance level to give exact Allen relations, promoted back as
class axioms that Uberon cannot currently express.

---

## 6. The singleton chains — available immediately

The arch series above needs index-matching and a family declaration. **A large part of the gain
needs neither**, because most developmentally interesting structures occur once per organism:
liver, notochord, ureteric bud, heart tube, hepatic diverticulum.

For those, the "family" has exactly one member, so the all-some witness is automatic and
promotion is trivially sound. No tagging, no index matching, no idealised-individual bookkeeping.

In EHDAA2, restricted to singleton terms with **both** endpoints bounded:

| | |
|---|---|
| structures | **520** |
| `develops_from` edges | 481 |

### Two chains

```
ureteric bud                                        liver
  zygote                   [ 0.0,  2.5)               inner cell mass        [ 4.5,  7.0)
  morula               M   [ 2.5,  4.5)               epiblast           M   [ 7.0, 13.0)
  inner cell mass      M   [ 4.5,  7.0)               definitive endoderm M  [13.0, 15.0)
  epiblast             M   [ 7.0, 13.0)               endoderm           S   [13.0, 26.0)
  mesoderm             M   [13.0, 31.0)               early foregut end. d   [19.0, 22.0)
  intermediate mesoderm d  [19.0, 28.0)               foregut-midgut j.  S   [19.0, 23.0)
  nephric cord         O   [22.0, 31.0)               hepatic plate      f   [22.0, 23.0)
  nephric duct         O   [23.0, 37.0)               hepatic diverticulum M [23.0, 26.0)
  ureteric bud         d   [28.0, 35.0)               liver              M   [26.0,   ?  )
```

Every step carries an **exact** relation. `hepatic plate` **meets** `hepatic diverticulum`
**meets** `liver` is three consecutive singletons — a textbook transformation chain, and
precisely the case `immediate transformation of ⊑ immediately_preceded_by`
([DEVELOPMENTAL_RELATIONS.md](DEVELOPMENTAL_RELATIONS.md) §4) is for.

### What composition derives

Composing along the chains over the whole singleton graph:

| | |
|---|---|
| pairs related after closure | 1,993 |
| of which asserted | 481 |
| **derived** | **1,512 — 3.1× the asserted** |
| of those derived, **exact** (a singleton label, not a disjunction) | **1,216 (80%)** |
| soundness — composed label contains the true relation | **1,993 / 1,993** |

So four out of five derived relations are exact. Composition does not degrade into
uninformative disjunctions along these chains, because the asserted steps are themselves mostly
singletons: `M`, `d`, `s`, `f`, `e` compose tightly, and only the genuinely ambiguous steps
widen.

Worked end to end: `ureteric bud` versus `zygote`, composed through all eight steps, gives
**`P`** — a singleton — and the directly computed relation is `P`. Complete, not merely sound.

### The honest qualification

**The singleton case does not actually need the idealised-individual framing.** It needs two
things: the `develops_from` subproperties carrying Allen axioms, and endpoints on both
structures. `liver ⊑ immediately_preceded_by some hepatic diverticulum` is true of the world,
not of an idealisation, and would be sound to assert today if the vocabulary existed.

That makes it the **cheapest available win and the one to attempt first** — 520 structures and
1,512 derivable relations in EHDAA2 alone, independent of whether the metamodelling proposal
goes anywhere.

### But individuals still buy something here: the chain becomes traversable

Promotion yields all-some axioms, and those are **one-directional**. This is a property of the
quantifier, not an oversight:

```
A ⊑ ∃R.B        does NOT entail        B ⊑ ∃R⁻.A
```

Countermodel: `A = {a}`, `B = {b, b′}`, `R = {(a,b)}`. Every A has an R-successor in B, but `b′`
has no R⁻-successor in A. Concretely: every liver is immediately preceded by some hepatic
diverticulum, but it does **not** follow that every hepatic diverticulum is immediately followed
by a liver — one might fail to form one.

So at class level the two directions are **independent claims and both must be asserted**. An
eight-edge chain needs sixteen axioms to be walkable in both directions, and each reverse axiom
is a separate thing to get right.

At individual level, with the inverse declared, one assertion gives both:

```
immediately_preceded_by(liver, hepatic-diverticulum)
   ⊨  immediately_precedes(hepatic-diverticulum, liver)
```

Eight OPAs, sixteen directions, no extra claims. **Querying "what does the hepatic diverticulum
become?" works without anyone having asserted the reverse.**

RO already declares the inverses this needs — `immediately_preceded_by`/`immediately_precedes`,
`preceded_by`/`precedes`, `starts_during`/`during_which_starts`,
`ends_during`/`during_which_ends`, `develops_from`/`develops_into`. It does **not** declare them
for `starts_before`, `ends_after`, the two transformation relations, or
`existence_starts_during`/`existence_ends_during`. Those gaps matter for exactly this reason and
belong on the list in [RO_REPORT.md](RO_REPORT.md).

### And the graph becomes homogeneous

The second advantage is uniformity with the stage series, which is already individual-shaped —
`Carnegie stage 09` is one thing, not a population.

Today a stage link mixes levels: `heart tube ⊑ ∃ existence_starts_during . CS09` relates two
*classes* through an existential. With structures as individuals it is a plain edge,
`starts_during(heart-tube, CS-09)`, of the same kind as `starts_during(heart-tube, foregut)`.
Structure-to-stage and structure-to-structure stop being different sorts of assertion, and the
whole thing is one graph a constraint solver can consume directly — which it has to be anyway,
since path consistency operates over nodes and edges and classes are neither.

So: the singleton case does not *need* individuation to produce sound axioms, but it needs it to
be **queryable in both directions and uniform with the stage backbone**. The idealisation earns
its keep separately on the families, where the all-some witness has to be supplied by
index-matching rather than coming for free.

---

## 7. A correction this forces to EHDAA2_REPORT §2

[EHDAA2_REPORT.md](EHDAA2_REPORT.md) §2 criticises EHDAA2's blanket use of the one-sided
RO:0002496 / RO:0002497. The envelope case above partly vindicates it, and the reason is clearest
written with the quantifiers made explicit. A class axiom is universally quantified over
instances, so for the 39 somites:

```
somite ⊑ ∃ starts_during . CS09
   "EVERY somite starts during CS09"                    FALSE — somite 39 starts at CS13

somite ⊑ ∃ starts_during_or_after . CS09
   "EVERY somite starts during or after CS09"           TRUE — but constrains almost nothing

somite ⊑ ∃ starts_during . (CS09 ⊔ CS10 ⊔ CS11 ⊔ CS12 ⊔ CS13)
   "EVERY somite starts during one of these"            TRUE and exact
```

**The universal over instances is what forces the weakening**, not the predicate. The one-sided
relation is one way to survive it; a disjunctive filler is another, and keeps both bounds.

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

## 8. Scope: what becomes an individual

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

## 9. Where the reasoning happens: outside OWL

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

## 10. Implementation

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

---

## 11. Caveats

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

## 12. A proposed trial

[`Uberon_HDCA_stage_axioms`][repo], on an experimental branch, is the natural test-bed — the
generation machinery is there and the taxon-scoping problem is already solved properly.

Two experiments, in order of cost.

**First, the singletons (§6) — no new machinery.** 520 structures, 481 asserted edges, 1,512
derivable relations of which 80% are exact. Needs only the `develops_from` subproperties with
Allen axioms and the endpoints both already present. Emit the composed relations, check them
against the directly computed ones, and promote. If this does not produce useful axioms, nothing
further will.

**Then the families (§5) — the machinery test.**

1. Generate individuals for the indexed families, starting with the pharyngeal arch series,
   where both endpoints are curated and the gain is already visible.
2. Run the promotion rule and emit the class-level axioms.
3. Compare against what Uberon asserts today: does promotion yield anything both new and exact?

Step 3 is the test. The arch series says it should — `pharyngeal arch artery ⊑ starts some
pharyngeal arch` and `pharyngeal arch ⊑ ends_with some pharyngeal arch` are neither of them
statable now. For the somite series, use **somite count as the clock** rather than Carnegie
stages (§11), or the result will be 119 pairs of "same stage" and nothing learned.
