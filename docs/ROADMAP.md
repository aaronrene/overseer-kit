# Overseer Kit v1 roadmap

2026-10-09 — Explicit owner authorization is recorded in the
[hosting/CI decision](decisions/V1-HOSTED-CI-AUTHORIZATION.md). The exact recovery
artifact commit `bff17390675358b764d43f31f71233ed11a673b0` has been published to the
public `aaronrene/overseer-kit` branch `ci/muse-rc5-recovery1-artifacts` by normal
push. Both HTTPS downloads match their exact hashes/sizes, and the approved
repository URL variable is configured and verified. Hosted Linux results remain pending; local evidence
remains **225 combined**, **117 Git-only on Python 3.11**, and **117 Git-only on
Python 3.14**, with zero failures/errors/skips.

Git-only remains a permanent option without Muse, and Muse adoption is explicit.
The original upstream archive remains unavailable; the exact recovery wheel and
source ZIP retain their reviewed hashes and recovery provenance. This dependency
hosting is not an upstream release or an Overseer product release.

The authorized scope includes non-force `feat/overseer-v1-recovery` pushes and
supported-v1 Git Linux 3.11/3.14 and combined Muse 3.14 jobs, with scoped fixes and
retries preserving artifact/source pins. New recovery candidates are reconciled
into the existing isolated `feat/overseer-v1-restoration-r3` Muse branch and checked
against a disposable mirror. Original refs/edits, staging main and the held release
remain preserved. Closed unchanged reviews and runtime rollback stay closed.

Muse-first product publication, live Hub protocol/rights, legacy mirror
reconciliation, actual delivery and consumer access remain separate gates. No
main push/merge, PR, tag/release, production trust reset, automatic hooks, OCI or
complete-product claim is authorized. Hosted execution does not prove those gates.

Current evidence is under `../RECOVERY-RUNS/20261009-hosted-ci/`; prior artifact
readiness evidence remains under `../RECOVERY-RUNS/20261008-muse-artifact-readiness/`.
The [validation record](validation/V1-RECOVERY.md#hosted-ci-execution--2026-10-09)
records the actual operations and results. Canonical `docs/NEXT.md`, published only
through `next-write`, is the sole executable next action.
