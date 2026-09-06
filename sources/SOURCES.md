# Source ontologies

The files in this directory are **not tracked in git** (see `.gitignore`) — together they are
~365 MB, and `go.owl` alone exceeds GitHub's 100 MB hard limit. Run `./sources/fetch.sh` to
retrieve them.

This file records exactly which releases the results in [../README.md](../README.md) and
[../USER_STORIES.md](../USER_STORIES.md) were computed against.

## Versions used

| File | Version IRI / source | Released | Bytes | sha256 (first 16) |
|---|---|---|---|---|
| `go.owl` | `obo/go/releases/2026-07-26/go.owl` | 2026-07-26 | 129,926,009 | `653ce47cd7b02304` |
| `hp.owl` | `obo/hp/releases/2026-09-01/hp.owl` | 2026-09-01 | 76,854,086 | `8da35ec3b4cb4943` |
| `mp.owl` | `obo/mp/releases/2026-08-25/mp.owl` | 2026-08-25 | 101,214,866 | `583b0b28a731f0a9` |
| `uberon.owl` | `obo/uberon/releases/2026-06-19/uberon-base.owl` | 2026-06-19 | 57,164,204 | `50aae4e64fdf97ef` |
| `ro.owl` | `obo/ro/releases/2025-12-17/ro.owl` | 2025-12-17 | 1,215,616 | `a9f644d4a865747e` |
| `hsapdv.owl` | `obo/life-stages/releases/2025-01-23/components/hsapdv.owl` | 2025-01-23 | 528,600 | `bc310742b68d398f` |
| `mmusdv.owl` | `obo/life-stages/releases/2025-01-23/components/mmusdv.owl` | 2025-01-23 | 367,557 | `1b2db363f8fe6644` |
| `life-stages-full.owl` | `obo/life-stages/releases/2025-01-23/life-stages-full.owl` | 2025-01-23 | 3,140,364 | `c6fa9cd539f6347e` |
| `life-stages.sssom.tsv` | `developmental-stage-ontologies@master:src/mappings/` | — | 29,051 | `251ecdbc15a9acf4` |
| `make-bridge-axioms.pl` | `developmental-stage-ontologies@master:src/util/` | — | 1,164 | `3407712adc4cb08c` |
| `owl-time.ttl` | `http://www.w3.org/2006/time#2016` (W3C REC 2017-10-19) | 2016 | 101,486 | `251bd6970b0d7a5e` |

`uberon.owl` here is **uberon-base**, not full Uberon.

## Two caveats on reproducibility

**Version IRIs are mostly not dereferenceable.** Of the four tested, only RO's resolved:

```
200  obo/ro/releases/2025-12-17/ro.owl
404  obo/go/releases/2026-07-26/go.owl
404  obo/uberon/releases/2026-06-19/uberon-base.owl
404  obo/life-stages/releases/2025-01-23/components/hsapdv.owl
```

A `versionIRI` is an identifier, not a promise of a retrievable copy. `fetch.sh` therefore
pulls the **current** release from the unversioned PURL and verifies the checksum, warning if
it differs. A mismatch means the ontology has been re-released, not that anything is broken —
but the counts in the write-ups may then drift.

**`owl-time.ttl` needs a workaround.** `w3.org` returns 403 to scripted clients (Cloudflare
interstitial). `fetch.sh` routes it through `r.jina.ai` and strips the wrapper. If that proxy
is unavailable, download it manually in a browser from
<https://www.w3.org/2006/time.ttl>.

## Which files each result depends on

| Result | Needs |
|---|---|
| RO axiom audit (`src/audit_ro.py`) | `ro.owl` |
| 29-relation algebra, templates (`src/generate.py`) | none — derived from first principles |
| HsapDv anchoring / propagation | `hsapdv.owl` |
| Uberon existence cases (`tests/uberon_cases.py`) | `uberon.owl` |
| Mouse lethality chain (`tests/full_chain.py`) | `mp.owl`, `mmusdv.owl`, `uberon.owl`, `life-stages.sssom.tsv` |
| Escalation rate (`tests/escalation_rate.py`) | `hsapdv.owl`, `uberon.owl` |

`go.owl` and `hp.owl` were used only for the survey in `USER_STORIES.md` §1 and are not needed
to reproduce any computed result. They are the two largest files after `mp.owl`; skip them with
`./sources/fetch.sh --minimal`.
