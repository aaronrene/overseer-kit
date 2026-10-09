# Overseer Kit v1 handover

**Fresh combined: 225 passed (248.14s); Git-only 3.14.4: 117 passed (56.89s);
Git-only 3.11.15: 117 passed (50.44s); artifact regressions: 12 passed (0.89s).**
Zero failures, errors or skips in these runs. The product and held release are
unfinished; hosted CI and Muse-first publication remain separate gates.

2026-10-08 — Artifact readiness started clean at Git
`92026da78b9861a7278d8a3df8c58f9aa576a1fe`, branch `feat/overseer-v1-recovery`, physical
root `overseer-kit-v1-recovery`, name `overseer-kit`, UUID
`6dba88a5-029c-4136-9277-c3a0c81f31a6`. The recovery remains Git-bound. Permanent
Git-only operation and explicit Muse adoption are unchanged; no consumer was accessed.

The original rc5 archive again returned HTTP 404. Its recorded download path and
88 pip cache files contained no matching original archive. R3's timestamp-dependent
reconstructed wheel remains preserved as evidence; it is not the new artifact.
The new deterministic recovery source ZIP and wheel use all 388 reviewed original
payload files. All 384 Python sources, data, metadata and license are accounted for.
The wheel changes WHEEL packaging metadata, adds `OVERSEER_RECOVERY.json`, and
regenerates RECORD (390 entries total); it keeps version `0.2.1rc5` and build tag
`1overseerrecovery`. It explicitly disclaims being an upstream release.

| Reviewed item | SHA-256 |
| --- | --- |
| Recovery wheel | `6b596288fd61f1d0373ead76eff90f82b14291984bff2dbecf9e51cf0694eb4d` |
| Recovery source ZIP | `28f5fefacf5860b600edbb83e3cdd35485b983a900ab229a2a1ea673776ae3f0` |
| Original Python sources | `7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92` |
| 388-file input manifest | `3a30de887720d3019ad8a40b300960f97693fc13b91da8814784dabe897115ff` |

The [recovery recipe](../tools/ci/MUSE-RC5-RECOVERY.md) rebuilds from the saved source
ZIP without Muse import, network or build backend. Original installed payload,
source ZIP/Python 3.14.4 and source ZIP/Python 3.11.15 produce identical bytes.
Author review used a separate ZIP/RECORD inspector and compared all entries against
R3. This is not a new independent review or proof of upstream release authenticity.
The closed Git-core and R3 independent reviews were not reopened.

Fresh conventional kit and separate Muse venvs were created and installed with
PyPI dependencies constrained to tested versions. Both pass `pip check`; kit cannot
import Muse. All 387 unchanged installed payload files match, and installed rc5's
source digest passes before the full 225-test run. The new 12 regressions cover
reproducibility and changed source/data/metadata, extra files, links, manifest/source
pin drift, duplicate entries and substituted artifacts. Native snapshot/mirror
coverage now carries the complete CI artifact contract. Python 3.11's separate
fresh kit install also passed the full Git-only matrix; all runs were local macOS.

`.github/workflows/supported-v1.yml` now requires `MUSE_RC5_RECOVERY_WHEEL_URL` for
the exact recovery wheel and verifies it before installation. It retains the
independent installed-source pin. Unset URL and wrong bytes fail; no fallback to
rc11, the moving installer or PyPI Muse exists. No URL or hosted CI run was created.
Third-party wheels/toolchains/platforms are not fully pinned by artifact hash.

The reviewed source delta is reconciled into the **existing** isolated
`feat/overseer-v1-restoration-r3` branch, still under
`../RECOVERY-RUNS/20261008-muse-restoration-r3/isolated-muse-source`.
New evidence is under `../RECOVERY-RUNS/20261008-muse-artifact-readiness/`.
`source-latest.json` and `projection-latest.json` bind final Git/Muse identities,
all **854** paths, bytes, ten executable modes, exclusions and mirror no-change
retry. Only a disposable projection copy moves its own main. The isolated store's
main remains staging `sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`.
No original refs, working edits or retained staging files are changed.

Kit runtime stays unpublished `1.0.0`, digest
`d5b692b52c152f006b71414f8b10fd20811b66ad1d90d61bdd9808881b31f3bb`;
R3's 24-check current/previous rollback evidence remains applicable and was not
repeated against unchanged runtime. The held release remains clean at
`06f988e5a078ede81c9dc664520833980a9a19a3`, branch `release/overseer-v1.0.0`.
No remote write, artifact publication, production trust reset, automatic hook or
OCI occurred. Hosted Linux/3.11/3.14 execution, live Hub protocol/rights, legacy
mirror reconciliation, real push/PR lifecycle, production trust and previously
unsupported platform/filesystem behaviors remain outside passing evidence.

The [validation entry](validation/V1-RECOVERY.md#muse-artifact-and-ci-readiness--2026-10-08)
records exact commands, counts and limits. Artifact hosting/hosted CI authorization
is the next gate, separately from Muse-first product publication. Canonical NEXT
is published with actual HEAD/prior digest and checked through direct and bound
launchers; this summary contains no competing executable prompt.
