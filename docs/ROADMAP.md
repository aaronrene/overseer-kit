# Overseer Kit v1 roadmap

**Fresh combined suite: 225 passed (248.14s). Git-only: 117 passed on Python
3.14.4 (56.89s) and 117 on Python 3.11.15 (50.44s). No failures/errors/skips.**

2026-10-08 — Local Muse artifact readiness is implemented and validated. The
complete product and held release remain unfinished. A reproducible rc5 recovery
source archive and wheel now exist locally with exact reviewed digests and honest
provenance. Artifact hosting and hosted CI still require authorization and evidence;
Muse-first product publication remains a separate later gate. No session ceiling
applies. The [scope decision](decisions/V1-SCOPE-RESET.md) retains two permanent choices:

- **Git/GitHub only:** no Muse installation, account, network check or migration.
- **MuseHub with a GitHub mirror:** explicit adoption and controlled one-way
  distribution, with separate delivery approval.

| Milestone | State |
| --- | --- |
| Original edits/Muse refs and held release | Preserved; release remains on hold |
| Closed Git-core reviews and authorized DINERO pilot | Unchanged; not repeated |
| R1 authority/adoption and R2 mirror/retry | Retained; full combined suite passes |
| R3 source reconciliation and changed-integration review | Retained; new delta carried into the same isolated Muse feature branch |
| R3 current/previous rollback | Prior 24-check evidence retained; runtime unchanged |
| Reproducible local rc5 distribution | Closed locally: 388 input files; identical builds on Python 3.11/3.14 |
| Fresh independent installation | Verified recovery wheel, separate kit/Muse venvs, dependency checks and full suite pass |
| Supported CI contract | Exact recovery artifact/source pins; both Git versions and combined runner pass locally |
| Artifact hosting and hosted Linux CI | Await separately scoped authorization; no URL configured or hosted run claimed |
| Muse-first publication | Separate later gate; live Hub/rights, legacy mirror and real delivery remain unvalidated |

The original checksum-pinned Muse archive still returns 404; it was not recovered.
The recovery wheel keeps **0.2.1rc5**, adds build tag `1overseerrecovery` and embeds
provenance saying it is **not an upstream release**. All 384 Python files and
package data are unchanged. Three builds from the installed payload/source ZIP
produce identical artifacts. The [recipe and contract](../tools/ci/MUSE-RC5-RECOVERY.md)
record what is recovered and what remains unavailable. Third-party dependency
versions are constrained; their binary artifacts/platform availability are not a
fully reproducible offline supply chain.

CI now requires `MUSE_RC5_RECOVERY_WHEEL_URL`, verifies the exact wheel before pip,
and checks the installed rc5 source digest. The former original-archive variable
is superseded explicitly. Missing URL or altered bytes fail without fallback.
Artifacts exist only under `../RECOVERY-RUNS/20261008-muse-artifact-readiness/`.
No artifact publication, remote write, consumer access, hook activation, production
trust reset, OCI or complete-product claim occurred.

The existing `feat/overseer-v1-restoration-r3` isolated Muse branch receives only
the reviewed Git delta. All **854** source paths, bytes, ten executable modes and
exclusions are checked again in its snapshot, working tree and disposable mirror.
Staging main remains unchanged. Final identities are in the new evidence directory's
`source-latest.json` and `projection-latest.json`.

Exact results, author artifact review, installation provenance, preservation and
remaining limits are in the [artifact readiness validation](validation/V1-RECOVERY.md#muse-artifact-and-ci-readiness--2026-10-08).
This work does not claim a new independent peer review or hosted Linux execution.
The runtime digest remains `d5b692b52c152f006b71414f8b10fd20811b66ad1d90d61bdd9808881b31f3bb`.
Canonical `docs/NEXT.md`, published with `next-write` and verified from disk, is the
only executable next action; this file is a milestone summary.
