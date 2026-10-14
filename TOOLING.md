# Generating OWL: which library, and why it matters

> **Caveat.** This repo has moved fast and explored several directions, some of which were
> abandoned mid-stream. Measurements here were taken on 2026-10-14 against the versions then
> installed. Some context from the exploration that produced these questions is not written
> down anywhere, and a few conclusions elsewhere in the repo have been superseded without every
> cross-reference being chased down. Treat numbers as reproducible and narrative as provisional.

---

## 1. The problem: string emission is the wrong abstraction

Three bugs from generating OWL in this repo, and where each surfaced:

| bug | caught |
|---|---|
| `csv.writer` excel dialect emitted `\r\n`, leaving a stray `\r` on every last field | by accident |
| missing `Declaration()` | at ROBOT parse |
| ROBOT template `AI owl:inverseOf` emits an **annotation**, not an axiom | **never** |

The third is the one that matters. It validates, it reasons, and it is silently wrong. No
amount of care with strings catches that class of error — the representation has to make it
unrepresentable.

---

## 2. Four options, measured

### owlready2 — objects, but no safety

```python
A.equivalent_to = [P.some("not-a-class")]     # a string where a class is required
onto.save(...)                                 # saves without complaint
```

```xml
<owl:someValuesFrom rdf:datatype="...#string">not-a-class</owl:someValuesFrom>
```

**Silent garbage** — the same failure mode as string emission, with extra steps. Convenience,
not correctness.

### Tawny-OWL — correctness, at the cost of Clojure

[phillord/tawny-owl](https://github.com/phillord/tawny-owl). Sits on the OWL API, whose factory
methods are typed, so a malformed expression fails at construction rather than serialising.
Plus real Lisp macros, so a generation pattern becomes an actual abstraction rather than a
template with holes — which matters here, because index-matching and the promotion rule are
*computations* and expressing computations as TSV is what makes them awkward.

Its distinctive advantage is **in-process reason-and-assert**: generate → reason → assert the
*entailment* → iterate, without serialising. That is what would have caught the `inverseOf` bug,
because the test would have been "does this entail X?" rather than "does this serialise?".

Against it: one maintainer; no native fit with ROBOT/ODK pipelines; gaps mean Java interop; and
the Clojure barrier.

*(Not tested here — no Clojure toolchain installed. Claims about typed construction are read off
the OWL API's signatures.)*

### horned-owl — correctness without the Clojure

[phillord/horned-owl](https://github.com/phillord/horned-owl), Rust, with Python bindings as
`py-horned-owl`. Same author as Tawny.

```python
ObjectSomeValuesFrom(P, "not-a-class")
→ TypeError: Object cannot be converted to ClassExpression
```

**Rejected at construction, from Python.** The Rust type system is enforced across the binding
boundary, so you get OWL API-grade correctness with no JVM and no Lisp.

And it is fast:

| parsing Uberon (57 MB) | |
|---|---|
| **horned-owl** | **1.24 s** — 225,056 axioms |
| rdflib | 13.45 s |

109 model constructors. Both things ROBOT templates got silently wrong are first-class:

```python
InverseObjectProperties(P, Q)       ✓
SubObjectPropertyOf([P, Q], P)      ✓    # chain as a plain list
```

Two gaps. **No reasoner** — none exposed, so reasoning stays in ELK/Whelk/HermiT/Soufflé. Fine
for this architecture, since reasoning was never going to live in the generator. And **no
auto-declaration** — output failed DL validation purely on `Use of undeclared class`, the same
bug class as the hand-rolled generator, but a few lines in the emitter rather than anything
inherent.

### ROBOT templates — fine for what they are

Good for flat term tables that curators edit. Cannot express inverses or property chains, and
**fails silently** when asked to, which is how bug 3 happened.

---

## 3. Scorecard

| | malformed input | parse speed | reasoner | language |
|---|---|---|---|---|
| Python string emission | not caught | — | external | Python |
| ROBOT template | **silently wrong** | — | external | TSV |
| owlready2 | **silent garbage** | slow | bundled HermiT | Python |
| Tawny-OWL | rejected at construction | OWL API | **integrated** | Clojure |
| **horned-owl** | **rejected at construction** | **11× rdflib** | none | Python |

---

## 4. Recommendation

**horned-owl for the generation layer**, reasoning stays where
[REASONING_STACK.md](REASONING_STACK.md) puts it.

It gets the elegance the question was after — real types, real abstraction, generation as code —
without the barrier that prompted "would need an agent layer for most mortals". And that worry
is worth addressing directly: **the barrier was never writing the code.** An LLM writes Clojure
fine. The barrier is *reviewing and debugging* it, and generated Clojure nobody on the team can
read is a worse maintenance position than generated Python everyone can — especially when the
motivating problem is errors getting through unnoticed. Adding a layer that makes output harder
to eyeball cuts against the goal.

Where an agent genuinely helps is the other direction: writing the **tests** — "assert this
module entails X and does not entail Y" — in whatever language the team reads.

### Cheapest first

1. **Validate generated artifacts in CI** — `robot validate-profile`, `reason`, and `explain`
   assertions on known entailments. Catches bugs 2 and 3 for near-zero cost, language-agnostic,
   and worth doing whatever else changes.
2. **Test entailments, not serialisations.** The real lesson from bug 3.
3. **Then** consider the generation library. horned-owl if the answer is "change it".

Tawny keeps one advantage horned-owl does not have — reason-and-assert in process. If the
ontology-as-program model is wanted for its own sake rather than just for correctness, that is
the argument for it, and the Clojure cost is a team-composition question rather than a technical
one.

---

## 5. Not settled

- **Tawny-OWL untested here.** No Clojure toolchain; claims are from the OWL API's signatures,
  not measurement.
- **horned-owl's reasoner story** — there may be work on bindings to EL reasoners that was not
  checked.
- **funowl** and other Python OWL libraries were not compared.
- Whether `py-horned-owl` keeps full type safety across *every* constructor, or only the ones
  tested here.
