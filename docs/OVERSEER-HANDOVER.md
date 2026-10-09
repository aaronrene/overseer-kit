# Overseer Kit v1 handover

**Combined suite: 213 passed (275.37s); Git-only: 105 passed (60.88s); manual lifecycle: 24 checks passed.**

2026-10-08 — R3 isolated Muse source reconciliation and combined local validation
are implemented. The complete product and held release remain unfinished. Resolve
the reviewed Muse rc5 artifact availability before claiming reproducible new-host
installation or a runnable hosted Muse CI gate. Publication remains separate.
Git-only operation is permanent and needs no Muse installation or account; adoption
of Muse authority is explicit. No session ceiling applies.

Recovery root: `overseer-kit-v1-recovery`; branch `feat/overseer-v1-recovery`; name
`overseer-kit`; UUID `6dba88a5-029c-4136-9277-c3a0c81f31a6`. R3 started clean at
Git `c389d748c8fc75e23f492e096298db8b83fab054`. The recovery stays Git-bound.
The new native Muse branch `feat/overseer-v1-restoration-r3` has its own copied
store under `../RECOVERY-RUNS/20261008-muse-restoration-r3/isolated-muse-source`.
It starts from verified staging
`sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`.
The 846-path staging snapshot was revalidated against all 841 Git base files at
`d47291d5d9030de5ebef713da95efa978c4d8c6e`. Five previously dispositioned generated/
local paths are explicitly excluded; all other changes come from the enumerated
recovery delta. Original refs, edits and retained staging bytes/modes are preserved.

`source-latest.json` records the final committed Git source, native Muse parent/
head/snapshot, per-file hashes/modes, full delta, 10 executable paths and exclusions.
`projection-latest.json` records full-source disposable mirror prepare/verify/retry.
The actual isolated source retains staging main; only a disposable projection copy
moves its own main to the candidate. No real Hub or GitHub destination is contacted.
New dot-directory files need explicit `muse code add PATH` in rc5; recursive add
omitted the new workflow in the first probe, and the committed-manifest regression
now verifies its inclusion and exact mirror bytes.

One independent review of the changed integration found one P2: malformed PR-list
responses could trigger creation. The correction validates the full observation
before any creation; only `[]` means absent. Eleven no-create cases plus the prior
malformed URL regression pass independently. Closed Git-core reviews were not
repeated. Runtime remains unpublished `1.0.0`; its existing manifest covers the
changed mirror module. Digest changes from R2
`90e179326877edc25263f0f1e1597c6b4067c09e64d03565e0b828d07640ccc6` to
`d5b692b52c152f006b71414f8b10fd20811b66ad1d90d61bdd9808881b31f3bb`.
Runtime-change refusal, read-only sync preview, explicit sync and status/NEXT
readback passed, preserving repository authority, UUID and documents.

Fresh independent kit/Muse environments passed dependency checks. Muse rc5 was
installed from a locally reconstructed wheel after checking 388 installed RECORD
hashes and the unchanged R1 package-source digest. The original staging rc5 archive
returned 404; current install.sh selects rc11. The reconstructed wheel is retained
as local evidence, not an upstream release. CI pins the original archive checksum
and package-source digest, requires `MUSE_RC5_URL` and fails without it. Git-only CI
does not consult that dependency. Hosted Linux/3.11/3.14 runs remain unobserved.

The manual fixture lifecycle passed 24 checks: initial legacy schema-1 Git source,
explicit current upgrade/adoption, Muse commit staleness, current/R2 fixed-path
rollback and resume, previous/fresh Muse environment selection, missing-Muse refusal
and explicit Git restoration, schema-1 restoration before old Git-only runtime,
and offline mirror prepare/verify/retry. Identity, living prose, bytes, modes and
owner edits survived; no hooks were activated. Unapproved physical kit relocation
still refuses. The unavailable-runtime probe accidentally overlapped the first
combined test run and caused eight setup errors; the failure is retained and the
full suite was rerun after restoring the interpreter, without concurrent mutations.

Exact counts, timings, earlier corrections, independent review and remaining limits
are in the [R3 validation entry](validation/V1-RECOVERY.md#r3-isolated-source-and-combined-validation--2026-10-08).
Logs, scripts, XML, manifests, installation provenance, preservation and canonical
NEXT readbacks live in `../RECOVERY-RUNS/20261008-muse-restoration-r3/`.

The held release stays clean at `06f988e5a078ede81c9dc664520833980a9a19a3` on
`release/overseer-v1.0.0`. No consumer, remote write, production trust reset,
automatic hook or OCI operation occurred. Live Hub refs/authentication, real delivery,
legacy mirror migration, linked Muse mutations, full filesystem fidelity and
new-host upstream installation are still outside passing evidence. R3 does not
authorize publication or establish final-product completion.

Canonical NEXT is published through `next-write` with actual HEAD and prior digest,
then validated through direct and bound launchers. Read it from disk; this summary
contains no competing executable prompt.
