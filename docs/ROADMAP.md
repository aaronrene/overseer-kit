# Overseer Kit v1 roadmap

2026-10-09 — **Recovery artifact hosting and the first hosted Linux validation
are complete.** The [supported-v1 run](https://github.com/aaronrene/overseer-kit/actions/runs/37946983229)
passed on Git candidate `25f319fb5505f86a36933bb7d7ebbb94b626899f`:

| Environment | Result | Pytest duration |
| --- | --- | --- |
| Ubuntu 24.04.5, Git-only Python 3.11.17 | **117 passed** | 36.12s |
| Ubuntu 24.04.5, Git-only Python 3.14.8 | **117 passed** | 45.66s |
| Ubuntu 24.04.5, combined Muse Python 3.14.8 | **225 passed** | 352.64s |
| Local macOS, combined Python 3.14.4 | **225 passed** | 262.75s |

All runs have zero failures/errors/skips. No code, workflow or dependency-pin fix
was needed. The closeout changes only documentation; its final Git/Muse/projection
identities and hosted readback are retained in the execution evidence directory.
The held release and complete product remain unfinished.

The exact recovery commit `bff17390675358b764d43f31f71233ed11a673b0` is hosted on
the public `aaronrene/overseer-kit` branch `ci/muse-rc5-recovery1-artifacts`. Both
HTTPS downloads matched the reviewed hashes/sizes before the exact
`MUSE_RC5_RECOVERY_WHEEL_URL` repository variable was set and read back. The
[decision record](decisions/V1-HOSTED-CI-AUTHORIZATION.md) records owner authority,
destinations and scope. The original upstream archive is still unavailable;
this reproducible dependency recovery is **not an upstream release**. Third-party
dependency artifacts/toolchains are not a fully locked offline supply chain.

Git-only remains permanent without Muse installation/login/migration; Muse
adoption is explicit. The existing isolated `feat/overseer-v1-restoration-r3`
branch receives only the reviewed source delta. All **855** paths and bytes,
ten executable modes, exclusions and disposable mirror no-change retry are
verified. Staging main, original Muse refs/config/Git edits and the clean held
release at `06f988e5a078ede81c9dc664520833980a9a19a3` remain preserved.
The unpublished runtime digest remains
`d5b692b52c152f006b71414f8b10fd20811b66ad1d90d61bdd9808881b31f3bb`;
closed unchanged reviews and current/previous rollback evidence are retained.

**Remaining product gates:** Muse-first publication with verified live Hub
protocol/rights, explicit legacy GitHub mirror reconciliation, actual delivery,
and any separately authorized consumer access. The existing mirror is not ready
to overwrite. Hosted CI does not authorize main merge/push, PR, tag/release,
MuseHub publication, real mirror delivery, consumer access, production trust reset,
automatic hooks or OCI. No complete-product or new independent-review claim is made.

The [execution validation](validation/V1-RECOVERY.md#hosted-ci-execution--2026-10-09)
records commands, counts and limits. Raw evidence is under
`../RECOVERY-RUNS/20261009-hosted-ci/`. Both summaries were updated together.
Canonical `docs/NEXT.md`, published only through `next-write`, carries the sole
executable remaining action.
