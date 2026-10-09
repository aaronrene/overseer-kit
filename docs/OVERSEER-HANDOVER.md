# Overseer Kit v1 handover

2026-10-09 — **The Git credential compatibility defect is repaired and validated
locally. Publication of the resulting candidate requires new owner authorization.**
The helper accepts repeated `capability[]` and `wwwauth[]` challenge metadata while
keeping the destination exact and scalar fields unique. It ignores the metadata
without negotiating state or a different credential type. Unknown fields, malformed
UTF-8, control characters and oversized requests still fail before token lookup.
The 16,384-byte bound, ephemeral credentials, no-op store/erase, disabled redirects
and strict mirror ownership, drift, correspondence and retry checks remain intact.

The new tests reproduce the observed protocol mismatch with fake credentials:
**33 passed, 6 failed** on the old helper; **39 passed** after repair. The 25 added
cases include real Git credential-fill negotiation, repeated metadata and refusals
that prove no token-provider invocation for invalid scope or malformed input.
No real credential or remote service was used in this repair.

| Required local matrix | Actual result | Pytest duration |
| --- | --- | --- |
| Git-only, Python 3.11.15 | **156 passed** | 53.10s |
| Git-only, Python 3.14.4 | **156 passed** | 59.10s |
| Combined Muse, Python 3.14.4 | **289 passed** | 368.81s |

All final runs have zero failures/errors/skips. Counts are 150 v1 + 6 retained
+ 133 Muse/mirror = 289 combined. The exact recovery Muse package-source digest
was checked by the supported driver; the Python 3.11 source fixture used retained
dependencies offline. No unchanged closed review or installation milestone was
repeated. The full matrix preceded the local feature commit; afterward only
validation/decision/summary documentation was finalized before committing.

The new exact Git candidate, isolated Muse revision/parent/snapshot and disposable
two-parent projection are frozen together in
[candidate.json](../../RECOVERY-RUNS/20261009-credential-compatibility/candidate.json).
Source/projection records retain all 861 paths/bytes/modes, ten executable paths,
the reviewed incremental delta and full GitHub delta (52 additions, 32 modifications,
32 removals). The projection preserves legacy mirror
`3e21496f7c4eab64b6d9ab3f868c5cdcaf8cfcde` as first parent and GitHub main
`d47291d5d9030de5ebef713da95efa978c4d8c6e` as second parent. It is a disposable
fixture; no real delivery commit is computed or approved.

The [publication decision](decisions/V1-MUSE-PUBLICATION.md) preserves the earlier
failed attempt and its owner scope. That authorization applies only to Git
`eef4901d76658c74bf1c56799a514c1cd756d28f`, Muse
`sha256:b310c0197a35b47c201cb055c211f0132efb902f86ecc76fd343302e8f2ed4cc`
and snapshot
`sha256:f0d48dd3f6b8d7cbc661e7f3ce07c7dfe3fb38efbe30332b43768ebd412658f1`.
It does not transfer to the repaired candidate. The prior attempt changed no remote
ref and created no hosted run. Its readbacks are retained observations, not current
remote-state assertions. Live authentication, push rights, staging acceptance and
mirror delivery remain unvalidated. No complete-product readiness claim is made.

Prior evidence and all three pending documentation edits were retained before
this repair. The isolated feature alone advances by a source-exact local commit;
its main stays at the retained staging base. Original refs/edits, identity/trust/
configuration and clean held release `06f988e5a078ede81c9dc664520833980a9a19a3`
remain protected. The actual delivery `source` and `mirror.git` paths remain absent.

Recovery wheel/source pins and the Actions URL are unchanged. Git-only operation
is permanently supported without Muse installation/login, and Muse adoption stays
explicit. The local runtime digest is
`e15e5f9a7567f18dd79181627eb040b876ada83a4c9334a70451eb419b9b53ed`;
`sync` refreshed the local binding without hooks. No remote read/write, hosted
job, MuseHub publication, shared-main change, PR, tag/release, consumer access,
production trust reset, automatic hook or OCI operation occurred in this repair.

The [validation closeout](validation/V1-RECOVERY.md#local-credential-compatibility-repair--2026-10-09)
and repair evidence retain actual results. Both summaries were refreshed together;
only `next-write` publishes the remaining owner authorization decision for the
resulting candidate. Any authorized delivery must record its real projection SHA
before pushing and preserve the approved source and ordered Git parents.
