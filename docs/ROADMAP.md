# Overseer Kit v1 roadmap

**Combined suite: 213 passed (275.37s); Git-only: 105 passed (60.88s); manual lifecycle: 24 checks passed.**

2026-10-08 — R3 local source reconciliation and combined operation are implemented.
The complete intended product is unfinished; the existing release worktree remains
on hold. The next readiness gap is a reproducible reviewed Muse rc5 installation
artifact. Hosted CI and publication still need their own evidence and authorization.
There is no session ceiling. The [scope decision](decisions/V1-SCOPE-RESET.md)
preserves two permanent choices:

- **Git/GitHub only:** local handoffs without Muse, an account, network checks or
  forced migration.
- **MuseHub with a GitHub mirror:** explicit Muse authority and controlled one-way
  snapshot distribution, with offline preparation and separate delivery approval.

| Milestone | State |
| --- | --- |
| Original working edits, Muse refs and held release | Preserved; staging evidence rehashed and reread |
| Git-core architecture/build review and authorized DINERO pilot | Closed; unchanged reviews and consumer work not repeated |
| R1 optional Muse authority and explicit adoption | Retained and covered by combined validation |
| R2 controlled mirror and retry | Retained; R3 independent review corrected one malformed-PR observation issue |
| R3 isolated source reconciliation | Native feature branch based on verified staging; every source path/byte/mode and explicit exclusion checked |
| R3 installation, migration and rollback | 24 manual no-hooks fixture checks passed; fresh local rc5 install used reconstructed verified package bytes |
| Supported CI | Workflow and local runner implemented; Git and combined local results in validation; hosted execution not evidenced |
| Reproducible upstream Muse dependency | Open: rc5 archive returned 404; moving installer selects unsupported rc11 |
| Muse-first publication and bounded consumer validation | Separate later gate; no remote write or consumer access in R3 |

The isolated feature source starts from staging
`sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`,
using only the enumerated recovery delta from Git
`d47291d5d9030de5ebef713da95efa978c4d8c6e`. Original histories and the isolated
store's main remain unchanged. Source/mirror manifests retain exact final Git/Muse
IDs under `../RECOVERY-RUNS/20261008-muse-restoration-r3/`. The new workflow survives
native snapshot and mirror projection; rc5 requires explicit staging of new
dot-directory files. Ten executable paths use the reviewed Git mode policy.

One independent changed-integration review found and rechecked a P2: malformed PR
observations could trigger creation. Only an exact empty list now allows creation;
invalid rows, heads, boolean fields or URLs refuse first. This review did not
reopen the unchanged Git-core milestones. Exact suite counts, earlier failures,
installation provenance and final review evidence are in the
[R3 validation record](validation/V1-RECOVERY.md#r3-isolated-source-and-combined-validation--2026-10-08).

Fresh kit and Muse venvs use separate dependencies. Fixed-path source replacement
between current/R2, explicit Muse environment selection, schema-1 rollback to the
held Git-only version and restoration with Muse unavailable were exercised.
Repository identity, summaries, binary bytes, executable modes and owner edits
survived. No lifecycle hooks were activated. Moving kit installations is still an
explicitly refused rebind, not a supported rollback shortcut.

The Muse CI job fails unless `MUSE_RC5_URL` supplies the original checksum-pinned
archive. The locally reconstructed wheel is labelled as such and does not close
upstream distribution readiness. Linux/Python 3.11 hosted execution, live staging
refs negotiation, credentials/rights, the real push/PR lifecycle, legacy remote
mirror reconciliation and production fingerprint trust remain unverified. There
is no version fallback, trust reset, main merge, release, OCI or final-product claim.

Canonical `docs/NEXT.md`, published by `next-write` and read back from disk, is the
only executable next action. This roadmap is a milestone summary.
