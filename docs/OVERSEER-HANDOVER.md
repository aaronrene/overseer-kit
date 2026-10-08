# Overseer Kit v1 handover

2026-10-08 — Audit completed; owner authorized local restoration with no session
ceiling. The complete intended product is still in progress. Users choose per
repository between standalone Git/GitHub-only operation and MuseHub authority
with a GitHub mirror. Git-only remains fully supported without Muse installed or
an obligation to migrate. The kit project's own publication flow remains
Muse-first. OCI stays excluded. Historical Git validation remains valid for the
behavior actually tested; it does not establish the pending Muse integration.

Recovery: `overseer-kit-v1-recovery`, branch `feat/overseer-v1-recovery`, repository
name `overseer-kit`, UUID `6dba88a5-029c-4136-9277-c3a0c81f31a6`. This audit started
from clean HEAD `3b8d7b4bc73830ff447b847d8d8dfef18f301502`. It changes documentation
and canonical local NEXT only. Runtime `1.0.0` and digest
`3643f0c9e6c5be2cc2e4d3aa7ed13eea34eb9fb213ea221d16d3faf6f3a1b623` are unchanged.
The clean release worktree remains at `06f988e5a078ede81c9dc664520833980a9a19a3`
on `release/overseer-v1.0.0`; do not publish that Git-only candidate.

Original Muse HEAD/refs/config/repository identity/bridge records and Git working
edits were compared before/after and preserved. The original mixed checkout and
`../RECOVERY-SNAPSHOTS/20261008T122430Z-v1-recovery` remain intact (prior verified
snapshot: 21,213 entries and 153 bundle refs). No consumer, including DINERO, was
accessed; no hooks, real-project mirror, original Muse refs or remote state changed.

Read the [scope correction](decisions/V1-SCOPE-RESET.md) and
[full audit](validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08).
They include evidence classes, diagrams, prioritized findings, feature disposition,
restoration milestones, rollback policy, acceptance tests and exact commands.
Local audit scripts/logs and retained fixtures are indexed under
`../RECOVERY-RUNS/20261008-muse-restoration-audit/`. An exploratory comparison used
the wrong hash representation; only `remote-comparison-corrected.json` is the final
byte-comparison result. Raw observations are preserved rather than rewritten.

Verified read-only remote state:

- Staging MuseHub repository ID:
  `sha256:f5863e477e2f2caf510df731720976d3d91fdd821fd5657ec8da6b57c89a3bea`.
- Staging `main` and AFF branch:
  `sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`.
- GitHub `main`: `d47291d5d9030de5ebef713da95efa978c4d8c6e`; all 841 tracked files
  match staging bytes. Five extra Muse paths are local/generated historical files.
- GitHub `muse-mirror`: `3e21496f7c4eab64b6d9ab3f868c5cdcaf8cfcde`; its existence
  does not prove current tree parity. Candidate branch and v1.0.0 tag are absent.
- GitHub reads work with approved network access; earlier sandbox output did not
  establish invalid credentials. Write authorization/capability was not tested.
- Production Muse CLI refuses a hub-fingerprint mismatch. Cause and production
  repository state are unknown. Keep staging; never reset trust merely to pass.

Native Muse `0.2.1rc5` in its separate Python environment successfully imported Git,
exported local snapshots and analyzed Python symbols/callers. Existing bridge
components are reusable, but current publication handling is unsafe to reactivate.
Key reproduced gaps: Git NEXT remains valid after a Muse commit; the deploy script
uses implicit HEAD and pushes before postchecks; path aliases evade its root guard;
failed push/no-change retry can leave the remote behind; no-change export clears
its Git mapping; dirty/stale target files can enter the mirror; machine-bound NEXT
is exported; executable metadata is not generally preserved; PR failure can be
hidden. These require integration work, not OCI or automatic two-way sync.

There were 40 diagnostics: 39 confirmed their named observation, one corrected
hypothesis. Reproduced defects are not passing product tests. The unchanged full
supported suite passed **77 tests, zero failures or skips in 41.80s** for the
documentation commit; limits are recorded at the end of validation. Earlier
evidence remains closed: session 3 had
two fresh installations and six rollback stages; session 4 had 77 supported tests
and 32 authorized manual DINERO pilot checks. The clean release branch later passed
77 tests twice (42.15s and 43.07s). No historical mega-suite or closed Git review was
repeated, and none of these results validates the missing Muse integration.

Recommended implementation order is R1, narrow Muse-aware status/NEXT and explicit
adoption; R2, controlled mirror preparation/verification/publication; R3, isolated
Muse source reconciliation plus integration review and combined installation/
rollback. Start a future Muse restoration branch from verified staging main and
apply the reviewed recovery delta; never copy the dirty original checkout. Keep
local bindings ignored, preserve UUID/documents through explicit migration, and
publish receiving-checkout NEXT through `next-write` rather than copying it.
Local coding can work offline; remote state remains unknown until explicitly
checked. GitHub edits require explicit review/import into Muse before authority.

The owner has removed the earlier five-to-eight-session ceiling; the audit's
budget stop is resolved. No replacement session limit or extension approval is
required. R1–R3 local restoration can proceed, beginning with Muse-aware local
status/NEXT and explicit adoption. R1 must also prove that Git-only operation
works without the Muse executable or credentials and that mixed checkouts select
their authority explicitly. Acceptance criteria, preservation requirements and
separate remote/consumer/hook authorization still apply.

Canonical NEXT advances through `next-write` to
`OVERSEER-V1-MUSE-RESTORATION-R1`, kind `implement`, model `GPT-6 Astra` with Extra
High reasoning requested in the task. It must not remain at the completed audit
or resolved budget stop. `docs/NEXT.md` is the only runnable handoff; this document
supplies context, not an alternate prompt. The current clarification changes
documentation and NEXT only; it does not claim R1 is already implemented.

Clarification closeout started from clean recovery HEAD
`3665a89fd3541f6c6fe3f8002221a9795d387e5b`. The unchanged supported suite passed
**77 tests, zero failures, errors or skips in 44.24s**. The runtime pin is unchanged.
After the local documentation commit, NEXT is bound to that new HEAD through
`next-write`; direct and bound launcher readback are checked before handoff.
