# Findings and proposed changes for RO

Results from a mechanical audit of RO's temporal relations against Allen's Interval Calculus,
plus an attempt to give Uberon's developmental relations temporal semantics.

Audited against **RO 2025-12-17** and **Uberon-base 2026-06-19**
(see [sources/SOURCES.md](sources/SOURCES.md)). Every claim below is reproducible with the
scripts named at the end.

---

## Action items

| # | Item | Effort | Impact |
|---|---|---|---|
| **1** | Add `starts_after`, the missing converse of `starts_before` | 1 term | Unblocks #2 |
| **2** | Bridge developmental relations to the temporal hierarchy | 3 axioms | **1,558 Uberon assertions** gain temporal semantics |
| **3** | Decide whether `developmentally_induced_by` belongs under `developmentally_preceded_by` | discussion | Semantics of a widely-used branch |
| **4** | Repair 2 property chains referencing obsolete properties | 2 edits | Correctness |
| **5** | *(Optional, larger)* Add relations for the exact results of temporal composition | 21 terms | Removes information loss in 4 of 6 temporal chains |

Items 1, 2 and 4 are small and independent. Item 3 is a modelling question. Item 5 is a
separate proposal, summarised here only because it explains a limitation you may already know
about.

---

## 1. `starts_before` has no converse

RO has `starts before` (RO:0002089), whose Allen semantics is the disjunction `pmoFD`
(`start(X) < start(Y)`). It has **no declared inverse**, and no relation anywhere in RO has the
converse semantics `dfOMP` (`start(X) > start(Y)`):

```
labels matching "starts after"                    : NONE
inverse declared on starts before (RO:0002089)    : NONE
```

This matters because `start(X) > start(Y)` is the correct — and weakest safe — temporal reading
of "X arises from Y" (§2). Without it that axiom cannot be written at all.

**Proposed**: add `starts after`, inverse of `starts before`, defined as
`X starts after Y iff start(X) > start(Y)`.

*Naming note.* We reached this via a systematic treatment of the 29 Allen relations closed under
composition, converse and intersection, and found that RO's existing compound names already
follow a consistent principle — **each names the endpoint invariant shared by all its
disjuncts**. `starts during` = `dfO` = "start(X) is strictly inside Y"; `starts before` =
`pmoFD` = "start(X) < start(Y)". `starts after` fits that scheme exactly.

---

## 2. No path from developmental relations to temporal ones

```
develops from → has developmental contribution from → developmentally preceded by
              → developmentally related to → (dead end)
```

The developmental branch never reaches `temporally related to` or any of its descendants. So
over 1,500 Uberon assertions that one structure arises from another are **invisible to temporal
reasoning**, even though each plainly implies one.

The right axiom is *not* `⊑ preceded_by`: where X arises from Y, Y need not cease when X appears
— X may bud from a persisting Y. The weakest safe claim is that Y begins first.

**Proposed** (`out/ro_temporal_patch.ofn` in this repo):

```
has developmental contribution from  ⊑  starts after
developmentally replaces             ⊑  starts after
developmentally contributes to       ⊑  starts before
```

Measured effect on Uberon:

| | |
|---|---|
| RO relations inheriting `starts after` | **7** |
| Uberon assertions gaining temporal semantics | **1,558** |
| Structures drawn into the resulting DAG | 2,019 |
| Ordered pairs after transitive closure | **3,029** (1,471 derived beyond asserted) |
| Longest developmental chain | 9 structures |
| Cycles | **none** |

The 7 relations are `develops from` (1,331 assertions), `has developmental contribution from`
(95), `immediate transformation of` (71), `transformation of` (47), `developmentally replaces`
(8), `develops from part of` (5), `directly develops from` (1).

---

## 3. `developmentally_preceded_by` does not entail precedence

The natural home for the axiom above is the top of the branch —
`developmentally preceded by ⊑ starts after` — one line covering everything. **This is wrong**,
and it fails immediately against real data.

`developmentally induced by` (RO:0002256) sits directly beneath `developmentally preceded by`.
Its own definition describes the two entities as "**interacting participants**" in a
developmental induction process. Interaction implies coexistence, not precedence.

Uberon contains reciprocal induction, correctly asserted in both directions:

```
metanephric mesenchyme  --developmentally induced by-->  ureteric bud
ureteric bud            --developmentally induced by-->  metanephric mesenchyme
```

This is the textbook reciprocal induction of kidney development. Under a start-order axiom on
the parent branch it entails `start(X) > start(X)` — unsatisfiable — and the Uberon
developmental graph acquires a cycle. Narrowing the axiom to the two branches in §2 leaves
induction untouched, and the graph is then acyclic across all 2,019 structures.

**The question for RO**: a relation named *developmentally preceded by* does not, given what
sits beneath it, entail that anything precedes anything. Either

- the name oversells the semantics and should be documented as not implying temporal order, or
- `developmentally induced by` is misplaced and belongs under `developmentally related to`
  alongside its siblings rather than under the *preceded by* branch.

We have no strong view on which; we only note that the current arrangement blocks the one-line
version of the §2 axiom, and that the blocking case is real biology rather than a curation error.

---

## 4. Two property chains reference obsolete properties

```
starts during o obsolete preceded by            -> starts before
    obsolete: BFO:0000060 "obsolete preceded by"

causally upstream of o obsolete has direct output -> obsolete has indirect output
    obsolete: RO:0002402 "obsolete has direct output"
```

The first is the substantive one: an **active** property (`starts before`) carries a chain whose
middle term is deprecated. `BFO:0000060` is the superseded BFO `preceded by`; the live
replacement is `BFO:0000062`. Presumably the chain was not updated when the obsoletion happened.

The second sits entirely within obsolete territory (both the chain member and the head are
deprecated) and is harmless, but is probably also worth removing.

---

## 5. Four of six temporal chains lose information

*Informational — no fix is possible without new relations, so this is context for item 5 in the
table rather than a defect report.*

RO's temporal axioms are **sound**. A mechanical check against Allen composition, derived from
endpoint enumeration rather than transcribed from a table, found:

- **10 of 10** transitivity declarations correct, including the four non-obvious negatives
  (`starts during`, `ends during`, `immediately precedes`, `immediately preceded by` are
  correctly *not* transitive)
- all subproperty axioms valid
- no unsound property chains

But four of six chains conclude something weaker than what is entailed:

```
happens_during o precedes    true result: p    RO must assert: pm
ends_during    o precedes    true result: p    RO must assert: pm
happens_during o preceded_by true result: P    RO must assert: PM
starts_during  o preceded_by true result: P    RO must assert: PM
```

The cause is a vocabulary gap: RO has `precedes` = `pm` and `immediately precedes` = `m`, but no
term for `p` alone — "precedes and does not meet". OWL has no property subtraction, so the exact
result is inexpressible and must be weakened every time.

The loss compounds. Walking two or more stages back along an HsapDv `immediately_preceded_by`
chain, the true relation is `P` (strictly preceded by) — meeting is impossible after two hops —
but RO can only conclude `PM`.

More strikingly, `precedes` (`pm`) and `preceded_by` (`PM`) **are not members of the
29-relation subalgebra** generated by the 13 Allen atoms under composition, converse and
intersection. They never arise as the result of any inference. Every conclusion drawn through
them is necessarily weaker than what was derivable.

Closing this fully needs 21 new object properties (the 29-relation set minus the 11 RO already
has). That is a much larger proposal than items 1–4 and is not urgent; item 1 alone unblocks the
high-value change.

---

## What checks out

Worth saying explicitly, since the above is a list of problems: **RO's temporal axiomatisation is
in good shape.** Every transitivity declaration is correct, including four where the correct
answer is counter-intuitive; every subproperty axiom holds; no chain is unsound. The issues found
are gaps and one misplacement, not errors.

---

## Reproducing

```sh
./sources/fetch.sh --minimal          # ro.owl, uberon.owl, DV ontologies
python src/audit_ro.py                # §4, §5 — axiom audit vs Allen composition
python src/generate.py                # emits out/ro_temporal_patch.ofn
python tests/develops_from_qc.py      # §2, §3 — 1,558 assertions, acyclicity, conflicts
```

The Allen composition table is derived by enumerating endpoint orderings
(`src/fast_allen.py`), and the converse function is checked against interval semantics rather
than transcribed. Background and the full 29-relation treatment: [README.md](README.md).
Context on which user-facing queries this enables: [USER_STORIES.md](USER_STORIES.md).
