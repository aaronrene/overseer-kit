# Phase K9a — L1 Checkpoint Plugin + L2 Honesty Module (Frozen Thinking Contract)

Status: **Frozen — K9a-r9 → `pass`. Cleared for K9b (L1 Auto) and K10 (L2 Auto).**  
No implementation in this Thinking close-out. No domain verify scripts shipped. No VideoFactory
gate names hardcoded in kit core. No MuseHub-required baseline. No media-model QC as authority.

**Downstream:** K9b builds Leg A (L1) only. K10 builds Leg B (L2) against this same contract.
K11 (API/CI provider) and K12 (Track N) are out of scope here except as named seams.

```yaml
phase: K9a
outputs:
  - id: k9a-l1-l2-module-freeze
    path: docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md
    frozen: true
frozen_inputs:
  - id: kit-spec
    path: docs/OVERSEER-KIT-SPEC.md
  - id: layered-honesty-vision
    path: docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md
  - id: k4-cli-contract
    path: docs/PHASE-K4-VENDORING-CLI-CONTRACT.md
  - id: k5-freeze-reviewer-contract
    path: docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
  - id: k8-multi-lane-contract
    path: docs/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md
  - id: vf-option-b-prompt
    path: docs/consumers/videofactory/CHECKPOINT-BUILD-PROMPT.md
  - id: vf-track-h-reference
    path: VideoFactory/docs/thinking/VF-OVERSEER-HONEST-FACTORY-SPEC-20260709.md
    note: reference only — not vendored; L2 source material for portable primitives
  - id: test-tiers
    path: policy/test-tiers.yaml
```

**Review record:**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (7 MAJOR + 4 MINOR) | **M1–M7 + N1–N4** recorded below; fixed in-tree same session. CLI `review --freeze` unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r2**. |
| 1-fix (2026-07-11) | Author fix revision (M1–M7 + N1–N4) | — | Dual-enable precedence; extensions warn-only v1; placeholder/overrides delivery; `--json` schema; artifact SHA; ledger canonical hash; usage/`--through`/governance/SPEC DoD notes. Awaiting **K9a-r2**. |
| 2 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (3 MAJOR + 1 MINOR) | **M1–M7 + N1–N4 confirmed RESOLVED** (citations in r2 ledger). New **R2-M1–M3 + R2-N1** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r3**. |
| 2-fix (2026-07-12) | Author fix revision (R2-M1–M3 + R2-N1) | — | Per-step manifest persist + `current_step` advance; missing manifest → `2`; session inequality via optional `--producer-session`; match requires `actor_role=verifier`; overrides cross-ref → §K9.5 steps 3–4c. Awaiting **K9a-r3**. |
| 3 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (3 MAJOR + 3 MINOR) | **M1–M7 + N1–N4 + R2-M1–M3 + R2-N1 confirmed RESOLVED** (citations in r3 ledgers). New **R3-M1–M3 + R3-N1–N3** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r4**. |
| 3-fix (2026-07-12) | Author fix revision (R3-M1–M3 + R3-N1–N3) | — | Ledger chain bootstrap + envelope fields; missing ledger file semantics; `--json` always emit; `--through current` empty → `0`; multi-verdict last-match. Awaiting **K9a-r4**. |
| 4 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (2 MAJOR + 3 MINOR) | **M1–M7 + N1–N4 + R2-M1–M3 + R2-N1 + R3-M1–M3 + R3-N1–N3 confirmed RESOLVED** (citations in r4 ledgers). New **R4-M1–M2 + R4-N1–N3** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r5**. |
| 4-fix (2026-07-12) | Author fix revision (R4-M1–M2 + R4-N1–N3) | — | `--step` must be in template else `2`; unknown `template_id` → `2`; policy file missing → `4`; ledger `--kind` authoritative vs JSON; `--file`/`--stdin` at most one; unknown `--hook` → `1`. Awaiting **K9a-r5**. |
| 5 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (2 MAJOR + 3 MINOR) | **M1–M7 + N1–N4 + R2-M1–M3 + R2-N1 + R3-M1–M3 + R3-N1–N3 + R4-M1–M2 + R4-N1–N3 confirmed RESOLVED** (citations in r5 ledgers). New **R5-M1–M2 + R5-N1–N3** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r6**. |
| 5-fix (2026-07-12) | Author fix revision (R5-M1–M2 + R5-N1–N3) | — | Manifest `current_step` ∈ T + every T id in `steps` else `2`; child argv always passes `--policy`; policy/manifest version `1` else `2`; `approval_recorded` role=`owner`; JSONL LF-terminated lines. Awaiting **K9a-r6**. |
| 6 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (2 MAJOR + 3 MINOR) | **M1–M7 + N1–N4 + R2-* + R3-* + R4-* + R5-M1–M2 + R5-N1–N3 confirmed RESOLVED** (citations in r6 ledgers). New **R6-M1–M2 + R6-N1–N3** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r7**. |
| 6-fix (2026-07-12) | Author fix revision (R6-M1–M2 + R6-N1–N3) | — | Module-disabled short-circuit before path load; template ids ∈ `policy.steps` + non-empty `verify_script` else `2`; `ledger show` empty/missing → `0`; `ARTIFACT_SHA256` line parse after trailing-NL strip; step/template id regex → `2`. Awaiting **K9a-r7**. |
| 7 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (3 MAJOR + 3 MINOR) | **M1–M7 + N1–N4 + R2-* + R3-* + R4-* + R5-* + R6-M1–M2 + R6-N1–N3 confirmed RESOLVED** (citations in r7 ledgers). New **R7-M1–M3 + R7-N1–N3** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r8**. |
| 7-fix (2026-07-12) | Author fix revision (R7-M1–M3 + R7-N1–N3) | — | `--dry-run` normative algorithm; resolve-`T` template id wording; consumer `orchestrator` timing + missing → `4`; overrides cross-ref → §K9.5 steps 3 + 6c; genesis actors refuse `2`; `require_l1_evidence` prefix match. Awaiting **K9a-r8**. |
| 8 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `findings` (2 MAJOR + 2 MINOR) | **M1–M7 + N1–N4 + R2-* + R3-* + R4-* + R5-* + R6-* + R7-M1–M3 + R7-N1–N3 confirmed RESOLVED** (citations in r8 ledgers). New **R8-M1–M2 + R8-N1–N2** recorded below; fixed in-tree same session. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Not cleared for K9b.** Awaiting **K9a-r9**. |
| 8-fix (2026-07-12) | Author fix revision (R8-M1–M2 + R8-N1–N2) | — | `require_verdict_on` allowlist + hook-not-enabled → `4`; `roles_file` v1 path-check + warn/ignore (enum-only); `--json` `dry_run` echoes CLI flag on every exit; L1 manifest/progress IO → `5`. Awaiting **K9a-r9**. |
| 9 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from r8; file+line citations | **`pass`** | **M1–M7 + N1–N4 + R2-* + R3-* + R4-* + R5-* + R6-* + R7-* + R8-M1–M2 + R8-N1–N2 confirmed RESOLVED** (citations in r9 ledger). Full regress §K9.0–§K9.19: no new contradictions; non-goals hold; K9b≠L2 split explicit; consumer hygiene paths on disk. CLI `review --freeze` still unavailable (muse `ReadError` / missing `.muse/HEAD`) — semantic review per `/freeze-review` skill. **Cleared for K9b.** No human escalation. |

### Freeze-review findings ledger (K9a-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| M1 | MAJOR | consistency | `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md:146-175`, `:275` | Dual enable: `modules.*.enabled` and `checkpoints.enabled` / `honesty.enabled` with no precedence — Auto cannot choose the operational gate. |
| M2 | MAJOR | consistency | `:153-154`, `:185-186` | Escape hatch: comment says “unknown ids warn; known schemaVersion loads”; parse rule only mentions `schema_version`; no v1 registered-id set. |
| M3 | MAJOR | completeness | `:203`, `:277-293` | `placeholder_tokens` claimed as banned in artifact paths but §K9.5 algorithm never enforces or exports them. |
| M4 | MAJOR | consistency | `:214-216`, `:284-287` | `overrides` “passed via env/file” but orchestrator argv/env list omits any overrides delivery. |
| M5 | MAJOR | completeness | `:256-271` | `--json` accepted with “one JSON object” but no frozen key schema for K9b e2e asserts. |
| M6 | MAJOR | completeness | `:373-374` | `honesty-status --artifact PATH` “matching passing verdict” — no frozen SHA algorithm for PATH. |
| M7 | MAJOR | completeness | `:321-357` | Ledger genesis string hashing + canonical JSON omit/null rules underspecified for deterministic `entry_hash`. |
| N1 | MINOR | consistency | `:421-422` | verify-step precedence omits usage `1` short-circuit (K4/K5 style). |
| N2 | MINOR | completeness | `:541-547` | DoD / build split does not require SPEC §5 command-table update when K9b/K10 land CLI. |
| N3 | MINOR | completeness | `:259`, `:267` | `--through current` shown; other `--through` values not refused explicitly. |
| N4 | MINOR | completeness | `:147-148` | `modules.governance.enabled: false` not fail-closed (L0 cannot be disabled). |

**Checks that passed in round 1 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes `10`–`11`/`20`–`24` additive vs K4/K5; role enum + co-requirement hook names domain-neutral; seven-tier matrices present for K9b and K10; consumer hygiene paths exist under `docs/consumers/videofactory/`; K9b≠L2 split explicit; Track H reference-only.

### Freeze-review findings ledger (K9a-r2)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R2-M1 | MAJOR | completeness | `:280-286`, `:322-338` | State machine says `current_step` advances when prior is verified, but orchestrator algorithm never updates `current_step`; end-of-run-only manifest write discards earlier successes if a later `--through`/`--all` step fails (`10`). |
| R2-M2 | MAJOR | completeness | `:301-302`, `:317` | `--manifest` / `active_manifest` “required effective path” with no frozen exit when both absent/null. |
| R2-M3 | MAJOR | consistency | `:381-383`, `:460-461` | §K9.6 co-requirement demands session inequality “when known,” but §K9.8 match rule is SHA-only and CLI has no producer-session seam; Auto cannot implement deterministically. |
| R2-N1 | MINOR | consistency | `:261` | Overrides delivery cross-ref says “§K9.5 step 3c”; env delivery lives at algorithm step **4c**. |

**K9a-r1 resolution confirmation (r2):**

| ID | Verdict | Evidence (post-1-fix) |
| --- | --- | --- |
| M1 | RESOLVED | `:196-205` operational gates + mirror MUST-equal; `:198` authoritative section flags |
| M2 | RESOLVED | `:172-173`, `:215-218` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:258-260`, `:329` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:319-332` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:344-368` verify-step `--json`; `:503-519` honesty-status `--json` |
| M6 | RESOLVED | `:457-458` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:392-411` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:537-538` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:647-649` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:310-311` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:203-204`, `:166` governance `enabled: false` → `2` |

**Checks that passed in round 2 (no finding):** C1 ground-truth edge; non-goals; L0/L1/L2 table; exits additive; hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2; Track H reference-only; seven-tier matrices present; Muse-not-required; no media QC as authority.

### Freeze-review findings ledger (K9a-r3)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R3-M1 | MAJOR | completeness | `:437-456`, `:556-557` | Genesis “may” + chain rule only ties `prev_hash` to prior `entry_hash`; empty/missing ledger bootstrap for first append and `ledger verify` on empty file not frozen — K10 Auto cannot implement deterministically. |
| R3-M2 | MAJOR | completeness | `:425-426`, `:458-484`, `:556-557` | Example entries include `v`/`ts`/`actor_session_id`, “each entry carries” session fields, but required-fields table omits envelope for most kinds; server fill only frozen for hashes — deterministic `entry_hash` underspecified. |
| R3-M3 | MAJOR | completeness | `:506-514`, `:552-557` | Missing ledger file: `honesty-status` match vs refuse (`20` vs `4`) and `ledger append` create-or-fail not frozen. |
| R3-N1 | MINOR | completeness | `:346`, `:388-412`, `:559-577` | `--json` “one object” does not state emission on non-zero exits (K5 always-emits pattern). |
| R3-N2 | MINOR | completeness | `:342`, `:348-349` | `--through current` when no unverified steps (all done) — empty selection exit not frozen. |
| R3-N3 | MINOR | consistency | `:509-514`, `:575-576` | Multiple matching verdicts → which `matched_verdict_hash` is undefined. |

**K9a-r1 + r2 resolution confirmation (r3):**

| ID | Verdict | Evidence (post-2-fix / pre-3-fix at review; holds post-3-fix) |
| --- | --- | --- |
| M1 | RESOLVED | `:260-269` operational gates + mirror MUST-equal; `:240`/`:248` authoritative section flags |
| M2 | RESOLVED | `:236-237`, `:279-282` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:322-324`, `:411` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:401-413` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:433-457` verify-step `--json`; `:649-668` honesty-status `--json` |
| M6 | RESOLVED | `:581` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:484-534` genesis constant + canonical JSON omit/null + hash rule (envelope extended in 3-fix) |
| N1 | RESOLVED | `:686` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:796-798` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:384` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:267-268`, `:283` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:353-359` advance rule; `:416-421` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:392-393`, `:399` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:468-475`, `:571-592` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:325` overrides cross-ref §K9.5 steps 3–4c |

**Checks that passed in round 3 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present; consumer hygiene paths on disk; K9b≠L2 split; Track H reference-only; dual-enable / extensions / placeholder / overrides / artifact SHA / L1 state machine from prior fixes hold.

### Freeze-review findings ledger (K9a-r4)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R4-M1 | MAJOR | completeness | `:376`, `:399-405` | `--step ID` selection never refuses an ID absent from the template step list; Auto can invent out-of-template verifies (or diverge on exit). Unknown `template_id` also lack a frozen exit. |
| R4-M2 | MAJOR | completeness | `:623`, `:632-634` | `ledger append --kind KIND` plus JSON body may both carry `kind` with no precedence — K10 Auto cannot implement deterministically. |
| R4-N1 | MINOR | completeness | `:562-574` | `--hook` required but not restricted to the frozen hook enum (`board_done`/`handoff`/`register`). |
| R4-N2 | MINOR | completeness | `:623` | `--file` and `--stdin` both present → cardinality/refuse not frozen. |
| R4-N3 | MINOR | consistency | `:399` vs `:392-393` | Effective policy path missing/unreadable file exit not frozen (manifest file → `4` is). |

**K9a-r1 + r2 + r3 resolution confirmation (r4):**

| ID | Verdict | Evidence (post-3-fix / pre-4-fix at review) |
| --- | --- | --- |
| M1 | RESOLVED | `:260-269` operational gates + mirror MUST-equal; `:240`/`:248` authoritative section flags |
| M2 | RESOLVED | `:236-237`, `:279-282` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:322-324`, `:411` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:401-413` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:433-457` verify-step `--json`; `:649-668` honesty-status `--json` |
| M6 | RESOLVED | `:581` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:484-534` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:686` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:796-798` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:384` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:267-268`, `:283` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:353-359` advance rule; `:416-421` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:392-393`, `:399` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:468-475`, `:571-592` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:325` overrides cross-ref §K9.5 steps 3–4c |
| R3-M1 | RESOLVED | `:487-496` chain bootstrap (missing/empty verify `0`; first append genesis/auto-genesis; genesis on non-empty → `2`) |
| R3-M2 | RESOLVED | `:500-512` envelope `v`/`ts`/actors; genesis omits actors; server-fill hashes |
| R3-M3 | RESOLVED | `:576-578` missing/empty ledger → status `20`; `:637` append creates then bootstraps |
| R3-N1 | RESOLVED | `:424-426`, `:646-647` `--json` emits on every exit path |
| R3-N2 | RESOLVED | `:386-388` `--through current` all-verified → `0` empty selection |
| R3-N3 | RESOLVED | `:589-590`, `:665-667` last matching verdict wins `matched_verdict_hash` |

**Checks that passed in round 4 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present; consumer hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2 split; Track H reference-only; dual-enable / extensions / placeholder / overrides / artifact SHA / L1 state machine / ledger bootstrap / envelope / `--json` always-emit / empty `--through` / last-match from prior fixes hold.

### Freeze-review findings ledger (K9a-r5)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R5-M1 | MAJOR | completeness | `:375`, `:426-430`, `:445-453` | Schema comment says `current_step` must be in the template list, and `--through current` indexes by it, but the orchestrator never refuses when `current_step ∉ T` or when a template step is missing from `manifest.steps` — Auto cannot implement load/`--through` deterministically. |
| R5-M2 | MAJOR | completeness | `:462-463` | Child verify argv shows optional `[--policy …]`; kit does not freeze whether the effective policy path is always passed — argv-builder / e2e asserts diverge. |
| R5-N1 | MINOR | completeness | `:339`, `:372` | Policy `version` “unknown → fail closed” and manifest `schema_version: 1` lack frozen exit codes. |
| R5-N2 | MINOR | consistency | `:602` | `approval_recorded` allows `actor_role` “(human/owner)” but §K9.6 enum has no `human`. |
| R5-N3 | MINOR | completeness | `:548` | “LF between records” underspecifies trailing LF / empty final segment on verify (JSONL line discipline). |

**K9a-r1 + r2 + r3 + r4 resolution confirmation (r5):**

| ID | Verdict | Evidence (post-4-fix / pre-5-fix at review) |
| --- | --- | --- |
| M1 | RESOLVED | `:302-309` operational gates + mirror MUST-equal; `:280`/`:288` authoritative section flags |
| M2 | RESOLVED | `:276-277`, `:319-322` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:362-364`, `:461` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:447-461` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:483-507` verify-step `--json`; `:711-730` honesty-status `--json` |
| M6 | RESOLVED | `:631-632` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:533-576` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:748-749` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:858-860` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:423-424` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:307-308`, `:323` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:393-399` advance rule; `:466-471` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:432-433` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:520-524`, `:634-644` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:365` overrides cross-ref §K9.5 steps 3–4c |
| R3-M1 | RESOLVED | `:537-546` chain bootstrap (missing/empty verify `0`; first append genesis/auto-genesis; genesis on non-empty → `2`) |
| R3-M2 | RESOLVED | `:550-562` envelope `v`/`ts`/actors; genesis omits actors; server-fill hashes |
| R3-M3 | RESOLVED | `:627-629` missing/empty ledger → status `20`; `:699` append creates then bootstraps |
| R3-N1 | RESOLVED | `:474-476`, `:708-709` `--json` emits on every exit path |
| R3-N2 | RESOLVED | `:426-428` `--through current` all-verified → `0` empty selection |
| R3-N3 | RESOLVED | `:640-641`, `:727-729` last matching verdict wins `matched_verdict_hash` |
| R4-M1 | RESOLVED | `:445-446` unknown `template_id` → `2`; `:450-451` `--step` not in `T` → `2` |
| R4-M2 | RESOLVED | `:685-691` CLI `--kind` authoritative vs body `kind` |
| R4-N1 | RESOLVED | `:623-624` unknown `--hook` → `1` |
| R4-N2 | RESOLVED | `:686` `--file`/`--stdin` at most one → else `1` |
| R4-N3 | RESOLVED | `:435-437` policy path escape / missing/unreadable → `4` |

**Checks that passed in round 5 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present; consumer hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2 split; Track H reference-only; dual-enable / extensions / placeholder / overrides / artifact SHA / L1 state machine / ledger bootstrap / envelope / `--json` always-emit / empty `--through` / last-match / `--step`∈T / `--kind` authority / hook enum / file|stdin cardinality / policy file → `4` from prior fixes hold.

### Freeze-review findings ledger (K9a-r6)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R6-M1 | MAJOR | consistency | `:491`, `:484-489`, `:495-497`, `:804` | `checkpoints.enabled: false` → `4`, but effective manifest/policy missing → `2` and algorithm step 1 always loads them — Auto diverges on disabled+null-manifest (`2` vs `4`); K5 freezes enabled short-circuit before other work. Honesty table has the same ordering gap vs ledger/artifact resolution. |
| R6-M2 | MAJOR | completeness | `:394`, `:509` | Template comment “each id MUST exist under steps” has no exit; orchestrator only refuses `4` when `verify_script` file is missing — id absent from `policy.steps` or empty `verify_script` key → Auto invents `2` vs `4`. |
| R6-N1 | MINOR | completeness | `:762` | `ledger show` freezes `N` only — missing/empty ledger exit/output not frozen (verify is vacuous `0`). |
| R6-N2 | MINOR | completeness | `:522-523` | `ARTIFACT_SHA256` on “last stdout line” underspecifies trailing NL / empty final segment (matrix requires sha line parse). |
| R6-N3 | MINOR | completeness | `:403` | `step_id` / `template_id` regex “only” with no frozen exit on violation. |

**K9a-r1 + r2 + r3 + r4 + r5 resolution confirmation (r6):**

| ID | Verdict | Evidence (post-5-fix / pre-6-fix at review) |
| --- | --- | --- |
| M1 | RESOLVED | `:345-354` operational gates + mirror MUST-equal; `:325`/`:333` authoritative section flags |
| M2 | RESOLVED | `:321-322`, `:364-367` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:407-409`, `:514` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:500-518` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:528-561` verify-step `--json`; `:764-786` honesty-status `--json` |
| M6 | RESOLVED | `:687-688` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:587-632` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:804-805` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:914-916` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:475-476` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:352-353`, `:368` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:445-451` advance rule; `:520-525` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:484-485` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:574-578`, `:690-700` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:410` overrides cross-ref §K9.5 steps 3–4c |
| R3-M1 | RESOLVED | `:591-600` chain bootstrap (missing/empty verify `0`; first append genesis/auto-genesis; genesis on non-empty → `2`) |
| R3-M2 | RESOLVED | `:606-618` envelope `v`/`ts`/actors; genesis omits actors; server-fill hashes |
| R3-M3 | RESOLVED | `:683-685` missing/empty ledger → status `20`; `:754-755` append creates then bootstraps |
| R3-N1 | RESOLVED | `:528-530`, `:764-765` `--json` emits on every exit path |
| R3-N2 | RESOLVED | `:478-480` `--through current` all-verified → `0` empty selection |
| R3-N3 | RESOLVED | `:696-697`, `:783-785` last matching verdict wins `matched_verdict_hash` |
| R4-M1 | RESOLVED | `:498-499` unknown `template_id` → `2`; `:503-504` `--step` not in `T` → `2` |
| R4-M2 | RESOLVED | `:745-747` CLI `--kind` authoritative vs body `kind` |
| R4-N1 | RESOLVED | `:679-680` unknown `--hook` → `1` |
| R4-N2 | RESOLVED | `:742` `--file`/`--stdin` at most one → else `1` |
| R4-N3 | RESOLVED | `:487-489` policy path escape / missing/unreadable → `4` |
| R5-M1 | RESOLVED | `:438-443` `current_step` ∈ T + every T id in `manifest.steps` else `2`; `:498-499` applied after resolve `T` |
| R5-M2 | RESOLVED | `:515-517` child argv **always** passes `--policy` (effective path) |
| R5-N1 | RESOLVED | `:384`, `:417`, `:496-497` policy/manifest version MUST be `1` else `2` |
| R5-N2 | RESOLVED | `:658` `approval_recorded` requires `actor_role=owner` |
| R5-N3 | RESOLVED | `:602-604` every JSONL record LF-terminated; ignore final empty segment |

**Checks that passed in round 6 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present; consumer hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2 split; Track H reference-only; dual-enable / extensions / placeholder / overrides / artifact SHA / L1 state machine / ledger bootstrap / envelope / `--json` always-emit / empty `--through` / last-match / `--step`∈T / `--kind` authority / hook enum / file|stdin cardinality / policy file → `4` / manifest consistency / always `--policy` / version exits / `approval_recorded` owner / JSONL LF from prior fixes hold.

### Freeze-review findings ledger (K9a-r7)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R7-M1 | MAJOR | completeness | `:525`, `:550-586`, `:964` | `--dry-run` accepted and required by the K9b matrix (“writes nothing”), and `--json` has `dry_run`, but the normative orchestrator algorithm never branches on dry-run — Auto invents plan/order/script-check/exit behavior. |
| R7-M2 | MAJOR | consistency | `:444`, `:455-456`, `:556-558` | Policy rule says every id under `templates.*.steps` must exist, while the algorithm only validates resolved `T` — Auto can fail-closed on unused templates or silently accept them. |
| R7-M3 | MAJOR | completeness | `:379`, `:599-602` | Non-null `checkpoints.orchestrator` replaces the built-in path, but timing vs module gate/load, missing/unexecutable exit, and which env vars the kit sets are unfrozen — Auto diverges on `2`/`4`/`5` and whether built-in still runs. |
| R7-N1 | MINOR | consistency | `:463` | Overrides delivery cross-ref still says “§K9.5 steps 3–4c”; after algorithm renumbering, env delivery is step **6c** (merge remains step 3). |
| R7-N2 | MINOR | completeness | `:685` | Genesis “MUST NOT carry” actors has no refuse exit when `actor_role` / `actor_session_id` are present. |
| R7-N3 | MINOR | completeness | `:777` | `require_l1_evidence` “matching `verify-step:*`” does not freeze prefix vs glob semantics. |

**K9a-r1 + r2 + r3 + r4 + r5 + r6 resolution confirmation (r7):**

| ID | Verdict | Evidence (post-6-fix / pre-7-fix at review) |
| --- | --- | --- |
| M1 | RESOLVED | `:397-404` operational gates + mirror MUST-equal; `:375`/`:383` authoritative section flags |
| M2 | RESOLVED | `:371-372`, `:414-417` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:460-462`, `:575` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:560-575` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:604-629` verify-step `--json`; `:836-858` honesty-status `--json` |
| M6 | RESOLVED | `:757-758` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:654-699` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:877` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:986-988` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:528-529` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:402-403`, `:418` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:498-504` advance rule; `:583-585` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:542-544` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:641-645`, `:760-767` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:463` intended cross-ref (stale “3–4c” → **R7-N1**; merge@3 + env@6c after 7-fix) |
| R3-M1 | RESOLVED | `:658-667` chain bootstrap (missing/empty verify `0`; first append genesis/auto-genesis; genesis on non-empty → `2`) |
| R3-M2 | RESOLVED | `:673-685` envelope `v`/`ts`/actors; genesis omits actors; server-fill hashes |
| R3-M3 | RESOLVED | `:753-755` missing/empty ledger → status `20`; `:824-825` append creates then bootstraps |
| R3-N1 | RESOLVED | `:595-597`, `:836-837` `--json` emits on every exit path |
| R3-N2 | RESOLVED | `:536-538` `--through current` all-verified → `0` empty selection |
| R3-N3 | RESOLVED | `:766-767`, `:855-857` last matching verdict wins `matched_verdict_hash` |
| R4-M1 | RESOLVED | `:556-557` unknown `template_id` → `2`; `:564` `--step` not in `T` → `2` |
| R4-M2 | RESOLVED | `:815-817` CLI `--kind` authoritative vs body `kind` |
| R4-N1 | RESOLVED | `:747` unknown `--hook` → `1` |
| R4-N2 | RESOLVED | `:812` `--file`/`--stdin` at most one → else `1` |
| R4-N3 | RESOLVED | `:546-548` policy path escape / missing/unreadable → `4` |
| R5-M1 | RESOLVED | `:491-496` `current_step` ∈ T + every T id in `manifest.steps` else `2`; applied after resolve `T` |
| R5-M2 | RESOLVED | `:576-578` child argv **always** passes `--policy` (effective path) |
| R5-N1 | RESOLVED | `:434`, `:470`, `:554-555` policy/manifest version MUST be `1` else `2` |
| R5-N2 | RESOLVED | `:725` `approval_recorded` requires `actor_role=owner` |
| R5-N3 | RESOLVED | `:669-671` every JSONL record LF-terminated; ignore final empty segment |
| R6-M1 | RESOLVED | `:531-534`, `:552-553` L1 module gate before path load; `:750-751`, `:805-807` L2 same |
| R6-M2 | RESOLVED | `:455-456`, `:556-558` every id in `T` ∈ `policy.steps` + non-empty `verify_script` else `2` |
| R6-N1 | RESOLVED | `:832-833` `ledger show` missing/empty → `0` no entry lines |
| R6-N2 | RESOLVED | `:588-593` `ARTIFACT_SHA256` after trailing-NL strip; last line segment |
| R6-N3 | RESOLVED | `:453-454`, `:555` step/template id regex → `2` |

**Checks that passed in round 7 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present; consumer hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2 split; Track H reference-only; dual-enable / extensions / placeholder / overrides / artifact SHA / L1 state machine / ledger bootstrap / envelope / `--json` always-emit / empty `--through` / last-match / `--step`∈T / `--kind` authority / hook enum / file|stdin cardinality / policy file → `4` / manifest consistency / always `--policy` / version exits / `approval_recorded` owner / JSONL LF / module-disabled short-circuit / template step∃+verify_script / ledger show empty / ARTIFACT_SHA256 NL / id regex from prior fixes hold.

### Freeze-review findings ledger (K9a-r8)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R8-M1 | MAJOR | completeness | `:442-445`, `:820-857` | `require_verdict_on` lists co-requirement hooks in config but honesty-status never consults it — Auto invents allowlist vs ignore vs must-equal-full-enum. |
| R8-M2 | MAJOR | completeness | `:441`, `:717-722` | `roles_file: null → enum-only` implies non-null changes behavior, but no load/enforce/ignore/exit rules — K10 Auto invents roster gates. |
| R8-N1 | MINOR | completeness | `:609-613`, `:642-646`, `:675-678`, `:699-704` | `--json` `dry_run` is shown in the schema and success dry-run path, but empty `--through` early exit and non-zero dry-run exits do not freeze whether `dry_run` echoes the CLI flag. |
| R8-N2 | MINOR | completeness | `:663-665`, `:675-677`, `:903-905` | verify-step `--json` emission lists exit `5` and L2 freezes append IO → `5`, but the L1 algorithm never maps manifest/progress write failure → `5`. |

**K9a-r1 + r2 + r3 + r4 + r5 + r6 + r7 resolution confirmation (r8):**

| ID | Verdict | Evidence (post-7-fix / pre-8-fix at review; holds post-8-fix) |
| --- | --- | --- |
| M1 | RESOLVED | `:453-460` operational gates + mirror MUST-equal; `:431`/`:439` authoritative section flags |
| M2 | RESOLVED | `:427-428`, `:470-473` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:518-520`, `:655` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:635-637`, `:651-655` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:675-704` verify-step `--json`; `:913-935` honesty-status `--json` |
| M6 | RESOLVED | `:834-835` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:730-776` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:953-954` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:1063-1065` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:586-587` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:458-459`, `:474` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:556-562` advance rule; `:663-665` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:615-617` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:825`, `:837-847` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:521` overrides cross-ref §K9.5 steps 3 + 6c |
| R3-M1 | RESOLVED | `:734-743` chain bootstrap (missing/empty verify `0`; first append genesis/auto-genesis; genesis on non-empty → `2`) |
| R3-M2 | RESOLVED | `:749-762` envelope `v`/`ts`/actors; genesis omits actors; server-fill hashes |
| R3-M3 | RESOLVED | `:830-832` missing/empty ledger → status `20`; `:902-903` append creates then bootstraps |
| R3-N1 | RESOLVED | `:675-678`, `:913-914` `--json` emits on every exit path |
| R3-N2 | RESOLVED | `:609-613` `--through current` all-verified → `0` empty selection |
| R3-N3 | RESOLVED | `:843-844`, `:932-934` last matching verdict wins `matched_verdict_hash` |
| R4-M1 | RESOLVED | `:631-632` unknown `template_id` → `2`; `:639` `--step` not in `T` → `2` |
| R4-M2 | RESOLVED | `:892-894` CLI `--kind` authoritative vs body `kind` |
| R4-N1 | RESOLVED | `:823-824` unknown `--hook` → `1` |
| R4-N2 | RESOLVED | `:889` `--file`/`--stdin` at most one → else `1` |
| R4-N3 | RESOLVED | `:619-622` policy path escape / missing/unreadable → `4` |
| R5-M1 | RESOLVED | `:549-554` `current_step` ∈ T + every T id in `manifest.steps` else `2`; applied after resolve `T` |
| R5-M2 | RESOLVED | `:656-658` child argv **always** passes `--policy` (effective path) |
| R5-N1 | RESOLVED | `:490`, `:528`, `:629-630` policy/manifest version MUST be `1` else `2` |
| R5-N2 | RESOLVED | `:802` `approval_recorded` requires `actor_role=owner` |
| R5-N3 | RESOLVED | `:745-747` every JSONL record LF-terminated; ignore final empty segment |
| R6-M1 | RESOLVED | `:589-592`, `:626-627` L1 module gate before path load; `:827-828`, `:882-884` L2 same |
| R6-M2 | RESOLVED | `:511-514`, `:631-633` every id in `T` ∈ `policy.steps` + non-empty `verify_script` else `2` |
| R6-N1 | RESOLVED | `:909-910` `ledger show` missing/empty → `0` no entry lines |
| R6-N2 | RESOLVED | `:668-673` `ARTIFACT_SHA256` after trailing-NL strip; last line segment |
| R6-N3 | RESOLVED | `:509-510`, `:630` step/template id regex → `2` |
| R7-M1 | RESOLVED | `:583`, `:642-646` `--dry-run` normative branch (order/script-path checks; no invoke/writes) |
| R7-M2 | RESOLVED | `:511-514` only **resolved** `T` validated; unused templates not until selected |
| R7-M3 | RESOLVED | `:594-607` consumer `orchestrator` after module gate; missing/unexecutable → `4`; no built-in run |
| R7-N1 | RESOLVED | `:521` overrides cross-ref steps 3 + 6c |
| R7-N2 | RESOLVED | `:761-762` genesis with actors → `2` |
| R7-N3 | RESOLVED | `:849-855` `require_l1_evidence` literal prefix `verify-step:` |

**Checks that passed in round 8 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present; consumer hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2 split; Track H reference-only; dual-enable / extensions / placeholder / overrides / artifact SHA / L1 state machine / ledger bootstrap / envelope / `--json` always-emit / empty `--through` / last-match / `--step`∈T / `--kind` authority / hook enum / file|stdin cardinality / policy file → `4` / manifest consistency / always `--policy` / version exits / `approval_recorded` owner / JSONL LF / module-disabled short-circuit / template step∃+verify_script / ledger show empty / ARTIFACT_SHA256 NL / id regex / `--dry-run` algorithm / resolve-`T` only / consumer orchestrator / overrides 3+6c / genesis actors / L1 evidence prefix from prior fixes hold.

### Freeze-review findings ledger (K9a-r9)

No new findings. Verdict: **`pass`**.

**K9a-r1 + r2 + r3 + r4 + r5 + r6 + r7 + r8 resolution confirmation (r9):**

| ID | Verdict | Evidence (post-8-fix) |
| --- | --- | --- |
| M1 | RESOLVED | `:571-578` operational gates + mirror MUST-equal |
| M2 | RESOLVED | `:545-546`, `:588-591` v1 registry empty; well-formed → warn-only; malformed → `2` |
| M3 | RESOLVED | `:647-649`, `:785` env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS`; kit transports only |
| M4 | RESOLVED | `:765-767`, `:781-785` merge + `OVERSEER_CHECKPOINT_OVERRIDES_PATH` temp file |
| M5 | RESOLVED | `:815-840` verify-step `--json`; `:1059-1078` honesty-status `--json` |
| M6 | RESOLVED | `:974-975` `sha256(raw file bytes)` lowercase hex |
| M7 | RESOLVED | `:867-868`, `:900-912` genesis constant + canonical JSON omit/null + hash rule |
| N1 | RESOLVED | `:1096` usage `1` short-circuit before precedence |
| N2 | RESOLVED | `:1206`, `:1208` SPEC §5 command-table update in K9b/K10 build split |
| N3 | RESOLVED | `:716` `--through` only literal `current` else `1` |
| N4 | RESOLVED | `:576-577`, `:592` governance `enabled: false` → `2` |
| R2-M1 | RESOLVED | `:685-691` advance rule; `:793-797` per-step persist + advance; mid-fail keeps prior writes |
| R2-M2 | RESOLVED | `:745-747` missing/null/empty effective manifest → `2` |
| R2-M3 | RESOLVED | `:961`, `:977-981` `--producer-session` + match requires `actor_role=verifier` |
| R2-N1 | RESOLVED | `:650` overrides cross-ref §K9.5 steps 3 + 6c |
| R3-M1 | RESOLVED | `:870-879` chain bootstrap (missing/empty verify `0`; first append genesis/auto-genesis; genesis on non-empty → `2`) |
| R3-M2 | RESOLVED | `:885-898` envelope `v`/`ts`/actors; genesis omits actors; server-fill hashes |
| R3-M3 | RESOLVED | `:970-972` missing/empty ledger → status `20`; `:1044-1045` append creates then bootstraps |
| R3-N1 | RESOLVED | `:807-810`, `:1056-1057` `--json` emits on every exit path |
| R3-N2 | RESOLVED | `:738-740` `--through current` all-verified → `0` empty selection |
| R3-N3 | RESOLVED | `:983-984`, `:1076-1077` last matching verdict wins `matched_verdict_hash` |
| R4-M1 | RESOLVED | `:761-762` unknown `template_id` → `2`; `:769` `--step` not in `T` → `2` |
| R4-M2 | RESOLVED | `:1035-1037` CLI `--kind` authoritative vs body `kind` |
| R4-N1 | RESOLVED | `:960` unknown `--hook` → `1` |
| R4-N2 | RESOLVED | `:1032` `--file`/`--stdin` at most one → else `1` |
| R4-N3 | RESOLVED | `:749-752` policy path escape / missing/unreadable → `4` |
| R5-M1 | RESOLVED | `:678-683` `current_step` ∈ T + every T id in `manifest.steps` else `2` |
| R5-M2 | RESOLVED | `:786-789` child argv **always** passes `--policy` (effective path) |
| R5-N1 | RESOLVED | `:619`, `:657`, `:759-760` policy/manifest version MUST be `1` else `2` |
| R5-N2 | RESOLVED | `:938` `approval_recorded` requires `actor_role=owner` |
| R5-N3 | RESOLVED | `:881-883` every JSONL record LF-terminated; ignore final empty segment |
| R6-M1 | RESOLVED | `:718-721`, `:756-758` L1 module gate before path load; `:963-964`, `:1024` L2 same |
| R6-M2 | RESOLVED | `:640-643`, `:761-763` every id in `T` ∈ `policy.steps` + non-empty `verify_script` else `2` |
| R6-N1 | RESOLVED | `:1052-1053` `ledger show` missing/empty → `0` no entry lines |
| R6-N2 | RESOLVED | `:800-805` `ARTIFACT_SHA256` after trailing-NL strip; last line segment |
| R6-N3 | RESOLVED | `:638-639`, `:760` step/template id regex → `2` |
| R7-M1 | RESOLVED | `:712`, `:772-776` `--dry-run` normative branch (order/script-path checks; no invoke/writes) |
| R7-M2 | RESOLVED | `:640-643` only **resolved** `T` validated; unused templates not until selected |
| R7-M3 | RESOLVED | `:723-736` consumer `orchestrator` after module gate; missing/unexecutable → `4`; no built-in run |
| R7-N1 | RESOLVED | `:650` overrides cross-ref steps 3 + 6c |
| R7-N2 | RESOLVED | `:897-898` genesis with actors → `2` |
| R7-N3 | RESOLVED | `:994` `require_l1_evidence` literal prefix `verify-step:` |
| R8-M1 | RESOLVED | `:593-597` `require_verdict_on` allowlist parse; `:966-968` hook not in set → `4` |
| R8-M2 | RESOLVED | `:598-603` `roles_file` v1 path-check + warn/ignore; `:963-964`, `:1026-1027` applied |
| R8-N1 | RESOLVED | `:740`, `:811-813`, `:837` `--json` `dry_run` echoes CLI flag on every exit |
| R8-N2 | RESOLVED | `:796-797` L1 manifest/progress write IO → `5` |

**Checks that passed in round 9 (no finding):** C1 ground-truth edge to K9b/K10; non-goals (no VF domain, no Muse-required, no media QC, no unbounded plugins, no Tier-3); L0/L1/L2 layer table; exit codes additive vs K4/K5; role enum domain-neutral; seven-tier matrices present and aligned with algorithm; consumer hygiene paths on disk under `docs/consumers/videofactory/`; K9b≠L2 split; Track H reference-only; all r1–r8 resolutions hold under §K9.0–§K9.19 regress.

---

## Simple summary (no jargon)

Overseer Kit already keeps roadmaps and handovers honest. That is not enough when agents mark
work done without proof, or when the same agent that did the work also stamps “approved.”

This contract freezes two optional add-ons any repo can turn on in `.overseer/config.yaml`:

1. **Checkpoints (L1)** — after each work step, a script must exit clean before the next step.
2. **Honesty (L2)** — a boss / worker / independent checker pattern plus a tamper-evident log so
   nobody can certify their own homework.

The kit owns the **socket** (config, CLI, orchestrator, ledger format). Each product repo owns the
**domain pack** (what to check for video, research, accounting, etc.). MuseHub can deepen storage
and identity later; it is never required for these features to work on plain GitHub.

## Technical summary

K9a freezes additive `.overseer/config.yaml` modules `checkpoints:` (L1) and `honesty:` (L2),
CLI commands `overseer verify-step`, `overseer honesty-status`, `overseer ledger`, shared exit
taxonomy extensions (`10`–`11` L1; `20`–`24` L2), manifest + policy schemas, hash-chained JSONL
ledger entry kinds, role enum, co-requirement hook points, consumer vs kit ownership rules,
explicit non-goals, and seven-tier matrices for **K9b** and **K10**.

---

## §K9.0 — Scope / non-goals / ownership

### In scope (this freeze)

| Item | Owner after build |
| --- | --- |
| `checkpoints:` / `honesty:` / `modules:` / `extensions[]` config schema | Kit parse + validate |
| Generic L1 orchestrator contract + policy/manifest shapes | Kit (`tools/checkpoints/`) |
| Generic L2 ledger + role + co-requirement primitives | Kit (`tools/honesty/`) |
| CLI: `verify-step`, `honesty-status`, `ledger {append,verify,show}` | Kit CLI |
| Exit codes `10`–`11`, `20`–`24` | Kit shared taxonomy |
| Fixture domain pack under `tests/fixtures/checkpoints/` | Kit tests only |
| Consumer adapter pattern doc | Kit `docs/CONSUMER-ADAPTER-PATTERN.md` |

### Explicit non-goals (frozen)

1. **No VideoFactory domain logic in kit core** — no `vf_verify_*`, no SIN-*, no BOR-*, no
   `videos/_active` hardcoded paths, no narration/avatar/CTA checks.
2. **No MuseHub required** for L1 or L2 baseline on `git-only`.
3. **No media-model / LLM-as-QC as authority** for measurable artifacts (L1 scripts decide;
   humans decide taste).
4. **No unbounded plugin marketplace / DLL loader** in v1 — typed modules + thin `extensions[]`
   that warn on unknown `schema_version`.
5. **No per-work-unit ROADMAP/HANDOVER** — L1 uses manifest + optional generated PROGRESS;
   L0 lanes stay for durable concerns (K8).
6. **No full agent mesh OS / workflow engine** — only decision-boundary honesty.
7. **No K11 API provider implementation** — Seam C remains a named future; L2 may *declare*
   a CI re-executor hook shape only.
8. **No Track H VF-specific org chart / worktree portals** — portable roles only;
   VF maps portals in its consumer pack.
9. **No Tier-3 automation enablement** without owner authorization.

### Kit vs consumer (every artifact type)

| Artifact | Kit | Consumer |
| --- | --- | --- |
| Config schema + CLI | Owns | Fills values |
| Generic orchestrator / ledger engine | Owns | Invokes |
| `policy/checkpoints.yaml` (domain steps) | Ships **fixture only** | Owns production policy |
| Domain verify scripts | No | Owns |
| Always-on Cursor rule for domain steps | Template stub optional | Owns domain rule |
| Episode / product boards (JSON grids) | No | Owns (VF production board) |
| L0 handover/roadmap/lanes | Owns machinery | Owns content |
| Track H SIN gates / video DoD | No | Owns (may call kit L2) |
| Consumer setup runbooks | `docs/consumers/<name>/` | Canonical copy may live in consumer repo |

**Hygiene decision (frozen):** kit `docs/` root stays **kit-neutral**. Consumer-specific
runbooks live under `docs/consumers/<name>/` (or only in the consumer repo). Root files
`VIDEOFACTORY-*.md` move to `docs/consumers/videofactory/` in the same Thinking close-out
that lands this contract (paths updated in ROADMAP/HANDOVER/vision).

---

## §K9.1 — Layer vocabulary (normative for K9b/K10)

| Layer | Name | Required? | Kit phase |
| --- | --- | --- | --- |
| **L0** | Governance | Always (shipped K1–K8) | — |
| **L1** | Domain checkpoints | Opt-in | K9b |
| **L2** | Honesty / roles | Opt-in | K10 |
| **L3** | MuseHub substrate | Opt-in deepen via existing VCS regime | already available; not gated by K9 |

**Dependency guidance (not hard refuse):**

- L2 **may** enable without L1, but CLI/status **must warn**:
  `honesty_without_checkpoints: true` — certification without mid-pipeline checks repeats remakes.
- L1 does **not** require L2.
- L3 never gates L0–L2 (K7 guardrail unchanged).

---

## §K9.2 — Config schema (additive, `overseer_config_version: 1`)

All new keys are **optional**. Absent → modules off; existing configs unchanged (backward compatible).

```yaml
# Additive — illustrative values, not defaults to assume
modules:
  governance: { enabled: true }     # L0; optional mirror; cannot be false (see parse rules)
  checkpoints: { enabled: false }   # optional mirror of checkpoints.enabled
  honesty: { enabled: false }       # optional mirror of honesty.enabled
  # muse_substrate is NOT a separate flag — regime already encodes L3
  # api_review remains freeze_contract.reviewer.provider (K5/K11)

# Escape hatch (K9a v1): every well-formed entry warns and is ignored (registry empty)
extensions: []   # [{ id: string, schema_version: int, config_path: repo-relative }]

checkpoints:
  enabled: false                   # AUTHORITATIVE L1 gate
  policy: policy/checkpoints.yaml  # consumer-owned; required when enabled
  active_manifest: null            # repo-relative; required when verify-step runs
  progress: null                   # optional generated human drill-down path
  orchestrator: null               # null → kit built-in; else consumer override script
  allow_hand_verified: false       # forever forbidden; refuse if true

honesty:
  enabled: false                   # AUTHORITATIVE L2 gate
  ledger: .overseer/honesty/VERDICT-LEDGER.jsonl   # repo-relative
  roles_file: null                 # optional roster path; v1 warn/ignore (see parse rules)
  require_verdict_on:              # allowlist of hooks that enforce co-requirement (see below)
    - board_done                   # L0 roadmap/board row → DONE
    - handoff                      # consumer handoff writers call kit check
    - register                     # consumer register writers call kit check
  require_l1_evidence: warn        # off | warn | require
  allow_signed_approval: false     # Tier-2 optional; off by default (zero-setup first)
  ci_reexecutor: null              # optional workflow path string for docs/status only
```

### Enable / modules precedence (frozen — resolves dual-flag ambiguity)

1. **Operational gates** are only `checkpoints.enabled` and `honesty.enabled`.
2. `modules` is optional. When absent, implied mirrors equal the section flags (governance
   treated as on).
3. When `modules.checkpoints` is present, `modules.checkpoints.enabled` **MUST equal**
   `checkpoints.enabled` → else `2`. Same for `modules.honesty` ↔ `honesty.enabled`.
4. When `modules.governance` is present, `modules.governance.enabled` **MUST be true**
   (or omitted with default true) → `false` → `2`. L0 cannot be disabled.
5. CLI/status may print `modules` as a derived view; writers always set the section flags.

### Parse rules (fail-closed → exit `2` unless noted)

1. Unknown keys under `checkpoints` / `honesty` / `modules.*` / each `extensions[]` object → `2`.
2. `checkpoints.enabled: true` without non-empty `policy` path → `2`.
3. `honesty.enabled: true` without non-empty `ledger` path → `2`.
4. `allow_hand_verified: true` → `2` (forbidden; only orchestrator may set verified).
5. `require_l1_evidence` not in `{off, warn, require}` → `2`.
6. Path fields that escape repo root → `4` (REFUSED), same as K5 path discipline.
7. **`extensions[]` (v1 registry empty):** every well-formed entry → **warn on stderr**, do not
   load, do not fail. Malformed entry (missing/non-string `id`, missing/non-int
   `schema_version`, missing/non-string `config_path`, or path escape) → `2`.
   Future kit versions may register `(id, schema_version)` pairs; until then **nothing loads**.
8. `modules` mirror mismatch / governance disabled → `2` (rules above).
9. **`require_verdict_on` (frozen):**
   - Absent or `null` → effective set = `{board_done, handoff, register}`.
   - Present → MUST be a list; empty list → `2`; every element MUST be one of
     `board_done` \| `handoff` \| `register` → else `2`; duplicates collapsed (set semantics).
   - Effective set is the allowlist of hooks that enforce co-requirement (§K9.8).
10. **`roles_file` (frozen — v1):**
    - Absent or `null` → enum-only (§K9.6); no roster file.
    - Non-null → repo-relative path (escape → `4` per rule 6). On every honesty/ledger command
      after the module gate: missing/unreadable → `4`; if readable → **warn on stderr** that v1
      does **not** load roster content for enforcement (role gates remain enum-only §K9.6);
      do not parse custom roles; do not fail closed on content.

### Token / footprint note

L1/L2 engines live in the kit **runtime** (`tools/checkpoints/`, `tools/honesty/`), not in the
vendored consumer footprint by default. Consumers call `overseer` from the kit pin (same as today).
Optional stub Cursor rule/skill templates may be added to footprint in K9b/K10 under
`cursor/rules/` / `cursor/skills/` with **domain-neutral** wording only.

---

## §K9.3 — L1 policy schema (`policy/checkpoints.yaml`)

Consumer-owned. Kit validates shape; does not invent domain steps.

```yaml
version: 1                    # integer MUST be 1; else → 2 (missing/non-int/unknown)
placeholder_tokens: []        # optional strings; exported to scripts (see below)

steps:                        # map step_id → definition
  <step_id>:
    verify_script: scripts/verify/verify_<step_id>.py   # repo-relative
    description: string       # optional human text

templates:                    # map template_id → ordered step list
  <template_id>:
    steps: [<step_id>, ...]   # ids in resolved T MUST exist under steps: with non-empty verify_script → else 2

overrides:                    # optional
  default: {}                 # free-form map — merged then delivered per §K9.5
  <template_id>: {}
```

**Rules:**

- `step_id` / `template_id`: `[a-z][a-z0-9_-]{0,63}` only → else `2` (policy load / manifest
  `template_id` / any step id key).
- Every id in the **resolved** template list `T` (`templates[manifest.template_id].steps`) **MUST**
  exist under `policy.steps` with a non-empty string `verify_script` → else `2` (checked when
  resolving `T`, before selection). Other templates in the same policy file are **not** validated
  until their `template_id` is selected.
- Kit **never** requires a fixed step vocabulary (`brief`/`export`/…). Domains choose names.
- Verify scripts are **opaque executables** to the kit: invoked with frozen argv; exit `0` = pass,
  any non-zero = fail (kit maps to exit `10`).
- **`placeholder_tokens`:** kit does **not** scan artifact paths. Before each invoke, kit sets
  env `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS` to a JSON array (UTF-8) of those strings (or `[]`).
  Domain scripts **must** enforce bans; kit only transports the list.
- **`overrides` delivery:** see §K9.5 step 3 (merge) and step 6c (env path to temp JSON).

---

## §K9.4 — L1 manifest schema (active work-unit state)

```yaml
schema_version: 1             # integer MUST be 1; else → 2 (missing/non-int/unknown)
template_id: <string>         # must exist in policy.templates
slug: <string>
current_step: <step_id>       # must be in template step list (load refuses else → 2)
meta: {}                      # optional free-form (branch, worktree, …) — kit ignores
steps:
  <step_id>:
    verified: false           # ONLY orchestrator may set true
    verified_at: null         # ISO-8601 UTC Z or null
    artifact_sha256: null     # optional; set when script reports a primary artifact hash
```

**State machine (frozen):**

1. On create, every template step present with `verified: false`; `current_step` = first template step.
2. `current_step` is the tip of verified progress: it may advance **only** via the orchestrator after a
   successful verify (rule below) — never by hand-edit trust.
3. Hand-editing `verified: true` is a policy violation; K9b orchestrator **re-runs** the script and
   overwrites — never trusts pre-set true without a successful run in the same invocation.
4. `--all` requires every step in the template list `verified: true` after successful verifies.

**Manifest consistency vs template `T` (frozen — after resolve `T`):**

1. `manifest.schema_version` MUST be integer `1` → else `2`.
2. `manifest.current_step` MUST be a member of `T` → else `2`.
3. Every id in `T` MUST exist under `manifest.steps` → else `2`.
4. Extra keys under `manifest.steps` not in `T` are **ignored** (not an error).

**`current_step` advance (frozen — after each successful verify of step `S`):**

1. Let `T` = template step list in order.
2. If every step in `T` strictly before `S` has `verified: true` (after this success), set
   `current_step` to the next step after `S` in `T`, or leave `current_step = S` when `S` is last.
3. Re-verifying an already-verified earlier step does not move `current_step` backward.
4. Out-of-order requests still refuse with `11` before any write.

**Optional PROGRESS.md:** if `checkpoints.progress` is set, orchestrator regenerates it from
manifest after each successful per-step write (deterministic renderer). Not an L0 lane doc.

---

## §K9.5 — L1 CLI: `overseer verify-step`

```text
overseer verify-step [--manifest PATH] [--step ID | --through current | --all]
                     [--policy PATH] [--dry-run] [--json]
```

| Arg | Default | Behavior |
| --- | --- | --- |
| `--manifest` | `checkpoints.active_manifest` | Required effective path |
| `--step ID` | — | Verify one step; on pass update manifest |
| `--through current` | — | Verify from first unverified through `current_step` inclusive |
| `--all` | — | Verify full template order |
| `--policy` | config `checkpoints.policy` | Override |
| `--dry-run` | off | Plan only: same load/select/order/script-path checks; **no** script invoke; **no** manifest/progress writes |
| `--json` | off | Exactly one JSON object on stdout for **every** exit (incl. non-zero); schema below |

**Mutual exclusion:** exactly one of `--step` / `--through` / `--all` required → else `1`.
`--through` accepts **only** the literal token `current`; any other value → `1`.

**Module gate (frozen — after usage `1`, before path resolution):**  
If `checkpoints.enabled` is `false` → refuse `4` with a message to enable the module. Do **not**
require or load effective manifest/policy paths when disabled (same short-circuit pattern as K5
`freeze_contract.enabled: false`).

**Consumer override (frozen — after usage `1` + module gate, before built-in load):**  
If `checkpoints.orchestrator` is non-null:

1. Resolve the path as repo-relative; path escape / missing / unreadable / not executable → `4`.
2. Invoke with argv list only (no `shell=True`): the same CLI argv this `verify-step` received
   (including `--dry-run` / `--json` when set). cwd = repo root. Set env
   `OVERSEER_REPO_ROOT` = absolute repo root only (per-step overrides/placeholder env is the
   override script’s responsibility).
3. Treat the script’s exit code as the command exit (must honor `10`/`11` meanings when using kit
   taxonomy). Do **not** run the built-in orchestrator algorithm below.
4. When `--json` is set, the override **MUST** emit exactly one schema object on stdout for every
   exit path (kit does not wrap/replace that object).
5. Override **MUST** honor per-step persist + `current_step` advance and `--dry-run` writes-nothing
   semantics (§K9.4 / dry-run rule below).

**`--through current` selection (frozen):** let `U` = first template step with `verified: false`
(template order). If no such step (all verified), selection is **empty** → exit `0` (no-op; JSON
`steps: []`; when `--json` is set, `dry_run` still echoes whether `--dry-run` was on the CLI).
Else select contiguous steps from `U` through `current_step` inclusive. If `U`
sorts **after** `current_step` in the template (inconsistent hand-edited tip), refuse `11`
(do not invent a repair).

**Effective manifest path** (only when module enabled **and** built-in orchestrator): `--manifest`
if given, else `checkpoints.active_manifest`.  
If the effective path is missing/null/empty → exit `2`. Path escape / missing/unreadable file → `4`.

**Effective policy path** (only when module enabled **and** built-in orchestrator): `--policy` if
given, else `checkpoints.policy`.  
If the effective path is missing/null/empty when `checkpoints.enabled: true` → exit `2` (same as parse
rule). Path escape / missing/unreadable file → `4`.

**Orchestrator algorithm (normative — built-in only):**

1. Load **config only**. After usage `1` already enforced: if `checkpoints.enabled: false` → `4`
   (module gate above). If `checkpoints.orchestrator` is non-null → consumer override path above
   (return its exit). Then load policy + manifest (fail-closed; missing effective manifest → `2`;
   policy/manifest path escape or missing/unreadable file → `4` as above). Policy `version` MUST be
   integer `1` → else `2`. Validate `step_id` / `template_id` keys against the regex (§K9.3) → else `2`.
2. Resolve ordered step list `T` from `templates[manifest.template_id]`. If `template_id` is absent
   from `policy.templates` → exit `2`. Every id in `T` MUST exist under `policy.steps` with a
   non-empty string `verify_script` → else `2`. Apply **manifest consistency vs `T`** (§K9.4) →
   else `2`.
3. Build **merged overrides** = shallow merge of `policy.overrides.default` overlaid by
   `policy.overrides[manifest.template_id]` when present (template keys win). Missing
   `overrides` → `{}`.
4. **Select steps** (after mutual exclusion already enforced):
   - `--step ID`: if `ID` is not in `T` → exit `2`. Selection = `[ID]`.
   - `--through current`: selection per rule above (may be empty → exit `0` before this loop).
   - `--all`: selection = full `T`.
5. **If `--dry-run`:** for each selected step in order, apply the same order refuse (`11`) and
   `verify_script` path refuse (`4`) as steps 6a–6b. Do **not** invoke scripts; do **not** write
   manifest/progress; do **not** create overrides temp files. Exit `0` (JSON `dry_run: true`;
   `steps` = planned selection in template order with pre-run `verified` / `artifact_sha256` from
   the loaded manifest — no simulated post-verify flips).
6. For each selected step in order:
   a. Refuse (`11`) if a previous template step is not verified (except when verifying that previous step in the same `--through`/`--all` walk).
   b. Resolve `verify_script` path from `policy.steps[id]`; refuse (`4`) if the script file is
      missing/unexecutable/path-escape (schema absence already refused at step 2 with `2`).
   c. Write merged overrides as canonical JSON (UTF-8, sorted keys, no insignificant whitespace)
      to a temp file (OS temp OK); set env (absolute paths allowed in env only):
      - `OVERSEER_REPO_ROOT` = absolute repo root
      - `OVERSEER_CHECKPOINT_OVERRIDES_PATH` = absolute path to that temp file
      - `OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS` = JSON array string of `placeholder_tokens`
      Invoke with argv list only (no `shell=True`):  
      `verify_script --manifest <repo-relative> --step <id> --policy <repo-relative>`  
      where `--policy` is **always** the effective policy path (repo-relative).  
      cwd = repo root. Delete temp overrides file after the invoke returns (best-effort).
      Stdout/stderr reports stay repo-relative (K4 path discipline).
   d. Non-zero → exit `10`; stderr from script passed through; **no further steps**; prior
      successful writes from this invocation **remain** on disk.
   e. Exit 0 → set `steps[id].verified=true`, `verified_at=now()`, optional sha from
      **`ARTIFACT_SHA256` parse** (below) — otherwise leave null; apply **`current_step` advance**
      rule (§K9.4); **write manifest atomically** now (temp + rename); regenerate progress if
      configured. Manifest or progress write IO failure → exit `5` (prior successful step writes
      from this invocation **remain** on disk).
7. Exit `0`.

**`ARTIFACT_SHA256` parse (frozen):** decode child stdout as UTF-8 (decode failure → leave
`artifact_sha256` null, still treat script exit `0` as verify pass). Strip all trailing `\n` and
`\r` from the decoded string. If empty after strip → null. Else take the substring after the final
`\n` (the whole string if no `\n` remains). If that line matches
`ARTIFACT_SHA256=<hex>` where `<hex>` is 1+ hexadecimal digits (`[0-9a-fA-F]+`) → set
`artifact_sha256` to the lowercase hex form; else leave null (malformed line does not fail verify).

**`--json` emission (frozen — built-in path):** when `--json` is set, print exactly one schema object
to stdout on **every** exit path (including `1`/`2`/`4`/`10`/`11`/`5`), with `ok`, `exit_code`, and
`error` populated; human diagnostics stay on stderr. Without `--json`, do not print the schema
object. (Consumer override `--json` duty: see override rule 4.)
**`dry_run` field (frozen):** on every `--json` exit path, `dry_run` MUST be `true` iff `--dry-run`
was present on the CLI, else `false` (including usage `1`, empty `--through` no-op, dry-run
order/script refuses, and non-dry-run verify exits).

### `--json` schema (frozen for verify-step)

One object, UTF-8, repo-relative paths only:

```json
{
  "ok": true,
  "exit_code": 0,
  "command": "verify-step",
  "mode": "step",
  "dry_run": false,
  "manifest": "path/to/manifest.yaml",
  "steps": [
    {"id": "export", "verified": true, "artifact_sha256": null}
  ],
  "error": null
}
```

| Field | Rule |
| --- | --- |
| `mode` | `step` \| `through` \| `all` |
| `dry_run` | `true` iff `--dry-run` was on the CLI; else `false` (every exit path) |
| `steps` | Selected steps in template order after this invocation (planned-only when `dry_run`) |
| `error` | `null` on success; else short machine token (`usage`\|`config`\|`refused`\|`step_order`\|`verify_fail`\|`io`) |
| `ok` | `true` iff `exit_code == 0` |

---

## §K9.6 — L2 roles (portable enum)

| Role | Powers | Forbidden |
| --- | --- | --- |
| `owner` | Human final approver; Tier-3 | — |
| `overseer` | Read; assign one scoped task; adjudicate; append `overseer_ruling` / `task_assigned` | Produce domain artifacts; write `verdict` as if verifier; self-approve |
| `producer` | Execute one assignment; write artifacts + advisory reports | Mark board DONE; write approvals; append `verdict`; advance co-required hooks |
| `verifier` | Re-execute L1/domain gates; append `verdict` bound to artifact SHA | Edit production artifacts; trust producer self-report as evidence |

**Session identity (frozen minimum):** each **non-genesis** ledger entry carries `actor_role` +
`actor_session_id` (opaque non-empty string; consumer/CI supplies). Append of `kind=verdict`
requires `actor_role == verifier` (else `23`). Session inequality vs the producer is **not**
inferred by the kit: consumers that know the producer session pass `--producer-session` to
`honesty-status` (see §K9.8). K10 does **not** require cryptographic identity on `git-only`;
L3 may deepen later.

---

## §K9.7 — L2 ledger format

**Path:** `honesty.ledger` (JSONL, append-only).

**Genesis constant (frozen):**  
`GENESIS_PREV = lowercase_hex(sha256(UTF-8 bytes of the ASCII string `overseer-kit-honesty-ledger-v1`))`  
(no BOM, no trailing newline in the hashed bytes).

**Chain bootstrap (frozen):**

1. **Missing ledger file** (path resolves inside repo, parents OK to create): treat as empty.
2. **Empty ledger** (zero bytes or file absent): `ledger verify` → exit `0` (vacuous chain).
3. **First append to an empty ledger:**
   - If `--kind genesis`: write exactly one genesis entry (`prev_hash = GENESIS_PREV`).
   - If any other kind: server **first** writes a genesis entry, then writes the requested entry
     with `prev_hash = genesis.entry_hash` (two lines in one atomic append transaction).
4. **Append `genesis` to a non-empty ledger** → refuse `2`.
5. Every subsequent line: `prev_hash` MUST equal the previous line’s `entry_hash`; else `22` on verify.

**Each line:** one JSON object, UTF-8, no pretty-print. **Line discipline (frozen):** every record
is terminated by a single LF (`\n`), including the last record (standard JSONL). On read/verify,
split on LF and **ignore** a final empty segment when the file ends with a trailing LF.

**Envelope fields (frozen — every entry):**

| Field | Rule |
| --- | --- |
| `v` | MUST be integer `1` (all kinds, including genesis) |
| `ts` | ISO-8601 UTC with `Z`. Client may supply; if omitted/empty, server sets `now()` before hash |
| `kind` | Frozen enum below |
| `prev_hash` | Server-filled only; client-supplied → `2` |
| `entry_hash` | Server-filled only; client-supplied → `2` |
| `actor_role` | Required on every **non-genesis** kind (enum §K9.6) |
| `actor_session_id` | Required on every **non-genesis** kind; opaque non-empty string |

Genesis entries **MUST NOT** carry `actor_role` / `actor_session_id` (omit keys). If either key is
present on a genesis append → refuse `2`.

**Canonical JSON for hashing (frozen):**

1. UTF-8 encoding.
2. At every object level, keys sorted lexicographically by Unicode code point.
3. No insignificant whitespace (no spaces after `:`/`,`; no newlines inside a record).
4. Arrays preserve element order.
5. Keys present with JSON `null` are included as `null`; **absent optional keys are omitted**
   (callers must not send `entry_hash`/`prev_hash` on append — server fills them).
6. Integers/booleans/strings as standard JSON; strings are JSON-escaped per RFC 8259.

**Hash rule:** let `body` = entry object with the `entry_hash` key removed (if present).  
`entry_hash = lowercase_hex(sha256(canonical_json(body)))`.  
Next line `prev_hash` MUST equal previous `entry_hash`.

```json
{
  "v": 1,
  "kind": "verdict",
  "ts": "2026-07-11T00:00:00Z",
  "actor_role": "verifier",
  "actor_session_id": "sess-…",
  "artifact_sha256": "hex…",
  "passed": true,
  "evidence": { "reexecuted": ["verify-step:export"], "notes": "…" },
  "prev_hash": "hex…",
  "entry_hash": "hex…"
}
```

**Entry kinds (frozen enum):**

| kind | Required fields (plus envelope above) |
| --- | --- |
| `genesis` | `v`, `ts`, `prev_hash`, `entry_hash` only (no actors) |
| `task_assigned` | `actor_role=overseer`, `actor_session_id`, `assignment` object |
| `verdict` | `actor_role=verifier`, `actor_session_id`, `artifact_sha256`, `passed`, `evidence` |
| `dispute_opened` | `actor_role`, `actor_session_id`, `subject` |
| `overseer_ruling` | `actor_role=overseer`, `actor_session_id`, `ruling` |
| `approval_recorded` | `actor_role=owner`, `actor_session_id`, `artifact_sha256`, `bound_verdict_hash` |
| `board_advance` | `actor_role`, `actor_session_id`, `artifact_sha256`, `bound_verdict_hash` |
| `hook_check` | `actor_role`, `actor_session_id`, `hook` name, `ok`, optional `reason` |

**Tamper:** `overseer ledger verify` walks the chain; break → exit `22`.

---

## §K9.8 — L2 co-requirement hooks

Generic hook names (no VF gate names):

| Hook | When | Requirement |
| --- | --- | --- |
| `board_done` | Consumer/L0 attempts to mark a work row DONE | Passing `verdict` for artifact SHA |
| `handoff` | Consumer handoff writer | Same |
| `register` | Consumer register writer | Same |

**Check API (K10):**  
`overseer honesty-status --hook HOOK --artifact PATH [--producer-session ID] [--json]`

`--hook` and `--artifact` are **required** together → else `1`.  
`--hook` MUST be one of the frozen names `board_done` | `handoff` | `register` → else `1`.  
`--producer-session` is optional (opaque string).

**Module gate:** after usage `1`, if `honesty.enabled: false` → `4` before resolving ledger or
artifact paths. Then apply **`roles_file` v1 path rule** (§K9.2 parse rule 10).

**Hook allowlist gate:** after module gate (+ roles_file rule), if `--hook` is not in the effective
`require_verdict_on` set (§K9.2 parse rule 9) → refuse `4` (hook not enabled for co-requirement)
before resolving ledger or artifact paths.

**Ledger file for status (frozen):** resolve `honesty.ledger`. Path escape → `4`.  
Missing or empty ledger file → no verdict match → exit `20` (not `4`; absence ≡ empty chain).  
Unreadable existing file → `4`.

**Artifact digest (frozen):** `PATH` is repo-relative; escape or missing/unreadable → `4`.  
`artifact_sha256 = lowercase_hex(sha256(raw file bytes of PATH))` (full file, not filtered).

**Match rule:** scan ledger in file order; collect every `kind=verdict` entry with all of:
- `passed: true`
- `actor_role: verifier`
- `artifact_sha256` equal to that digest
- if `--producer-session ID` was supplied: `actor_session_id != ID`  

If the collection is empty → `20`. Else success candidate = the **last** matching entry in file
order (newest append wins for `matched_verdict_hash`).

When `--producer-session` is omitted, session inequality is **not** checked (append still
enforced `actor_role=verifier`).

**`require_l1_evidence` (applied on successful match):**

| Mode | Behavior |
| --- | --- |
| `off` | No further check |
| `warn` | If `evidence.reexecuted` has no string entry with literal prefix `verify-step:` (Unicode), warn on stderr; still `0` |
| `require` | Same missing L1 evidence → `20` |

→ exit `0` when match (+ require rule) holds.

**Optional approval binding:** when recording `approval_recorded`, require
`bound_verdict_hash` → matching passing verdict on same `artifact_sha256`; else `21`.
If `allow_signed_approval: true`, additional signed-commit check is consumer/CI-defined;
kit exposes the flag and a verify callback seam only (signature deferred to K10 implementation
notes; not required for git-only baseline).

**Evidence-free verdict refuse:** `evidence.reexecuted` must be a non-empty list; else append
rejected with `24` (verifier tool enforces).

**Role violation:** producer appending `verdict` or overseer writing production paths via kit
helpers → `23`.

---

## §K9.9 — L2 CLI

```text
overseer honesty-status --hook HOOK --artifact PATH [--producer-session ID] [--json]
overseer ledger append --kind KIND [--file JSON_PATH | --stdin]
overseer ledger verify
overseer ledger show [--last N]
```

| Command | `honesty.enabled: false` |
| --- | --- |
| All above | After usage `1`, refuse `4` **before** ledger/artifact path resolution (do not require those paths when disabled). Then apply `roles_file` v1 path rule when enabled. |

**`ledger append` / `verify` / `show` (enabled path):** after module gate, apply **`roles_file` v1
path rule** (§K9.2 parse rule 10) before ledger IO.

**`ledger append` input (frozen):**

1. `--kind KIND` is **required** → else `1`. `KIND` must be a frozen entry-kind enum value → else `2`.
2. **At most one** of `--file` / `--stdin` → both present → `1`. Neither present → body is empty object `{}`.
3. `--file JSON_PATH`: repo-relative; path escape / missing/unreadable → `4`. Parse as one JSON object.
4. `--stdin`: read one JSON object from stdin (fail closed → `2` on malformed JSON).
5. **`kind` authority:** CLI `--kind` is authoritative. If the JSON body contains `kind` and it
   differs from `--kind` → exit `2`. If the body omits `kind`, server sets `kind` from `--kind`
   before validation/hash. Client must not supply `entry_hash` / `prev_hash` (→ `2`).

**`ledger append` (frozen):**

1. Apply input rules above; validate envelope + kind schema + role rules (§K9.7); refuse
   `2`/`23`/`24` as applicable.
2. Never accept client-supplied `entry_hash` / `prev_hash` (server-side fill) → else `2`.
3. If ledger path’s parent dirs are missing: create them under repo root only (path escape → `4`).
4. If ledger file is missing: create empty file, then apply chain bootstrap (§K9.7).
5. Append atomically (temp + rename or single append syscall with full line(s)); dual-write
   genesis+entry on first non-genesis append is one transaction — on failure leave prior bytes
   unchanged (`5` on IO failure).

`ledger verify`: missing/empty → `0`; otherwise walk chain (§K9.7) → break `22`.

`ledger show [--last N]`: default `N=20` when flag absent; `N < 1` → `1`. Missing or empty
ledger file → exit `0` and emit no entry lines (vacuous show; same empty-chain reading as verify).
Otherwise print the last `N` records (file order; oldest of the window first) as JSONL to stdout.

**`--json` emission (honesty-status):** same as verify-step — exactly one schema object on stdout
for **every** exit path when `--json` is set.

### `--json` schema (frozen for honesty-status)

```json
{
  "ok": true,
  "exit_code": 0,
  "command": "honesty-status",
  "hook": "board_done",
  "artifact": "path/to/artifact",
  "artifact_sha256": "hex…",
  "producer_session": null,
  "matched_verdict_hash": "hex…",
  "error": null
}
```

`producer_session` echoes `--producer-session` or `null` when omitted.  
`matched_verdict_hash` is the `entry_hash` of the **last** matching passing verdict (or `null`
when none).  
`error` tokens: `usage`\|`config`\|`refused`\|`missing_verdict`\|`io`.

---

## §K9.10 — Exit-code taxonomy (extensions)

Inherits K4 `0`–`6` and K5 `7`–`8`. New codes:

| Code | Name | Layer | Meaning |
| --- | --- | --- | --- |
| `10` | VERIFY_FAIL | L1 | Domain verify script non-zero |
| `11` | STEP_ORDER | L1 | Step requested out of order / prior unverified |
| `20` | MISSING_VERDICT | L2 | Co-requirement failed (no matching independent verdict) |
| `21` | APPROVAL_INTEGRITY | L2 | Approval without bound passing verdict (or signed tier fail) |
| `22` | LEDGER_BROKEN | L2 | Hash chain invalid / mutated history |
| `23` | ROLE_VIOLATION | L2 | Actor role not permitted for action |
| `24` | EVIDENCE_FREE | L2 | Verdict lacked re-executed evidence |

**Precedence for verify-step:** after usage `1` short-circuit, `2 > 4 > 11 > 10 > 5 > 0`  
**Precedence for honesty/ledger:** after usage `1` short-circuit, `2 > 4 > 22 > 23 > 24 > 21 > 20 > 5 > 0`

**Mapping note (non-normative):** VideoFactory Track H SIN-35..39 / exits 60–64 map onto
kit `20`–`24` at the consumer boundary; kit core does not emit SIN ids.

---

## §K9.11 — Track H → kit L2 porting rules

| Track H concept | Kit L2 |
| --- | --- |
| Overseer / Producer / Verifier | Same enum (+ `owner`) |
| `VERDICT-LEDGER.jsonl` | `honesty.ledger` format §K9.7 |
| Verdict co-requirement | Hooks §K9.8 |
| CI re-executor | Declared path / consumer workflow; K11 may deepen |
| SIN-35..39 | Consumer policy; call kit exits |
| VF portals / worktrees | Consumer only |
| `DEFINITION-OF-DONE.json` | Consumer domain pack |
| `CustodyLedgerProvider` | Future L3 provider interface — **same ledger bytes** on git-only file backend first |

Track H remains **L2 source material**, not the kit master plan. H-0.5 threat model may proceed
in parallel; kit K10 implements portable primitives regardless of VF SIN numbering.

---

## §K9.12 — Consumer doc hygiene (frozen)

1. Add `docs/CONSUMER-ADAPTER-PATTERN.md` — how to wire L0 lanes + L1 pack + L2 hooks.
2. Move:
   - `docs/VIDEOFACTORY-CHECKPOINT-BUILD-PROMPT.md` → `docs/consumers/videofactory/CHECKPOINT-BUILD-PROMPT.md`
   - `docs/VIDEOFACTORY-OVERSEER-SETUP.md` → `docs/consumers/videofactory/OVERSEER-SETUP.md`
3. Future MuseHub / Scooling / Knowtation adapter notes → `docs/consumers/<name>/`.
4. Kit root `docs/` retains SPEC, ROADMAP, HANDOVER, PHASE-*, vision, Track N marketing only.

---

## §K9.13 — Track N seed (marketing only — not architecture)

Landing sections (K12 build later): Problem → L0 → L1 → L2 → optional L3 → Modularity → Personas →
Quickstart → MuseHub upgrade → Public roadmap.

Scenario gallery personas: A video studio, B research, C accounting, D classroom, E multi-org OSS.

LICENSE posture: choose OSI license at K12; security disclosure file at K12; no license change in K9.

Graphics brief: layer cake, Scenario A sequence, GitHub→Muse funnel, org chart, lanes vs rows vs repos.

---

## §K9.14 — MuseHub collaboration answers (§6.9 vision)

| # | Question | K9a answer |
| --- | --- | --- |
| 1 | Minimal Muse objects for an Overseer verdict? | Same JSONL entry bytes as §K9.7, content-addressed as a Muse blob/tree; kit API stays file-path ledger on git-only |
| 2 | Map Tier-3 to Muse capabilities 1:1? | **Not in K9** — keep kit Tier-3 table; Muse capability mapping is a later L3 provider ADR |
| 3 | Provenance badge from mirror? | Track N / K12 marketing; technical = mirror branch SHA |
| 4 | Classroom UX without scaring GitHub-only? | L0 default; L3 behind explicit regime flip (existing K7 story) |
| 5 | `CustodyLedgerProvider` == kit L2? | **Yes intent** — file backend first; Muse backend later behind one interface |

Open (remain open): exact Muse schema types — for MuseHub collaborators, not blocking K9b.

---

## §K9.15 — Lane guidance (soft limits)

Already N-ary (K8). Soft guidance:

| Count | Guidance |
| --- | --- |
| 1–3 | Normal |
| 4 | Warn in docs / status note |
| >4 | Prefer rows/manifests or split repos |

Rule: **lanes = few durable concerns; manifests = many instances; repos = trust/regime split.**

---

## §K9.16 — Seven-tier test matrix

### K9b (L1 Auto) — required before DONE

| Tier | Cases |
| --- | --- |
| unit | Config parse; policy/manifest schema; step-id validation (regex → `2`); argv builder (**always** includes `--policy`); `ARTIFACT_SHA256` parse (trailing-NL strip); `current_step` advance; `--step` not-in-template → `2`; `current_step` ∉ T → `2`; template step missing from `manifest.steps` → `2`; template id missing from `policy.steps` / empty `verify_script` → `2`; unused other templates with bad refs do **not** fail until selected; policy/manifest version ≠ `1` → `2`; `checkpoints.enabled: false` → `4` without requiring manifest; `--dry-run` applies order/script-path checks then exits `0` with no writes; `--json` `dry_run` echoes CLI flag on every exit (incl. empty `--through`); non-null `orchestrator` missing/unexecutable → `4`; manifest/progress write IO → `5` |
| integration | Built-in orchestrator + fixture verify scripts + manifest atomic write (temp + rename) |
| e2e | Fixture repo: `--step` pass → manifest; fail → `10` no write; `--all` happy path; `--through current` when all verified → `0` empty; `--dry-run` leaves manifest bytes unchanged |
| stress | 100-step template; large overrides map; no OOM |
| data-integrity | Idempotent re-verify; crash mid-write leaves prior manifest; dry-run writes nothing; mid-`--through` fail keeps earlier step writes |
| performance | 20-step `--all` bounded time on fixture |
| security | Path escape on manifest/policy/script/orchestrator → `4`; no absolute paths in `--json`; script cannot escalate via unchecked shell (argv list only, no `shell=True`); `--json` emits on non-zero exits |

### K10 (L2 Auto) — required before DONE

| Tier | Cases |
| --- | --- |
| unit | Canonical JSON; hash chain; envelope (`v`/`ts`/actors); role enum; hook check; genesis bootstrap; genesis with actors → `2`; `--kind` vs body `kind` mismatch → `2`; JSONL trailing-LF empty segment ignored; `approval_recorded` requires `actor_role=owner`; `honesty.enabled: false` → `4` before ledger/artifact load; `require_l1_evidence` prefix `verify-step:`; `require_verdict_on` empty/unknown → `2`; hook not in allowlist → `4`; `roles_file` missing → `4`; readable `roles_file` warns and stays enum-only |
| integration | append + verify; co-requirement pass/fail; missing ledger → status `20`; first append auto-genesis; unknown `--hook` → `1`; `ledger show` on missing/empty → `0` |
| e2e | Producer cannot append verdict (`23`); missing verdict on hook (`20`); tampered line (`22`); empty evidence (`24`); `--producer-session` rejects same-session verdict (`20`); two verdicts → last `matched_verdict_hash`; subset `require_verdict_on` refuses disabled hook with `4` |
| stress | 10k ledger lines verify |
| data-integrity | Append atomicity (incl. dual genesis+entry); verify idempotent; concurrent append refuse or serialize safely; verify empty → `0` |
| performance | verify 10k lines bounded |
| security | Path escape; no secrets in ledger show; injection in `evidence.notes` does not execute; `roles_file` content cannot inject custom roles in v1 |

---

## §K9.17 — Build split (after freeze `pass`)

| Phase | Model | Builds |
| --- | --- | --- |
| **K9b** | Auto | L1 only: config parse, `verify-step`, fixture pack, tests, neutral cursor stub; update SPEC §5 command table for `verify-step`; consumer doc move already done in K9a |
| **K10a** | Thinking (short) | Only if freeze review demands L2 splits; else skip |
| **K10b** | Auto | L2 ledger + honesty-status + role gates + tests; update SPEC §5 for `honesty-status` / `ledger` |
| **K11** | Auto | API freeze provider (unchanged queue) |
| **K12** | Thinking → Auto | Track N landing |

**Default:** one freeze doc covers both legs; Auto does **not** implement L2 in K9b.

---

## §K9.18 — Definition of Done (K9a Thinking)

- [x] This contract drafted with schemas, CLI, exits, tests, non-goals, ownership
- [x] Independent freeze review → `pass` (K9a-r1…r8 findings + fixes; **K9a-r9 → `pass`**; CLI `review --freeze` blocked by muse `ReadError` — semantic review per `/freeze-review` skill)
- [x] Vision doc expanded + hygiene decision recorded
- [x] ROADMAP + HANDOVER updated (▶ NEXT = K9b Auto)
- [x] No Auto implementation until freeze `pass` (K9b starts only after this stamp)

---

## §K9.19 — Change log

| Date | Note |
| --- | --- |
| 2026-07-11 | K9a Thinking draft from master prompt + layered vision + VF Option B + Track H primitives |
| 2026-07-11 | K9a-r1 `findings` (M1–M7, N1–N4) + 1-fix: enable precedence, extensions v1 warn-only, placeholder/overrides env delivery, `--json` schema, artifact SHA, ledger canonical hash, usage/`--through`/governance/SPEC notes |
| 2026-07-12 | K9a-r2 `findings` (R2-M1–M3, R2-N1) + 2-fix: per-step manifest persist + `current_step` advance; missing manifest → `2`; `--producer-session` + match requires `verifier`; overrides cross-ref 3–4c |
| 2026-07-12 | K9a-r3 `findings` (R3-M1–M3, R3-N1–N3) + 3-fix: ledger chain bootstrap + envelope fields; missing ledger → status `20` / append create+auto-genesis; `--json` always emit; `--through` empty → `0`; multi-verdict last-match |
| 2026-07-12 | K9a-r4 `findings` (R4-M1–M2, R4-N1–N3) + 4-fix: `--step` must be in template else `2`; unknown `template_id` → `2`; policy file missing → `4`; ledger `--kind` authoritative vs JSON; `--file`/`--stdin` at most one; unknown `--hook` → `1` |
| 2026-07-12 | K9a-r5 `findings` (R5-M1–M2, R5-N1–N3) + 5-fix: manifest `current_step` ∈ T + every T id in `steps` else `2`; child argv always `--policy`; policy/manifest version `1` else `2`; `approval_recorded` `actor_role=owner`; JSONL LF-terminated lines |
| 2026-07-12 | K9a-r6 `findings` (R6-M1–M2, R6-N1–N3) + 6-fix: module-disabled short-circuit before path load; template ids ∈ `policy.steps` + non-empty `verify_script` else `2`; `ledger show` empty/missing → `0`; `ARTIFACT_SHA256` trailing-NL parse; step/template id regex → `2` |
| 2026-07-12 | K9a-r7 `findings` (R7-M1–M3, R7-N1–N3) + 7-fix: `--dry-run` normative algorithm; resolve-`T` template wording; consumer `orchestrator` timing + missing → `4`; overrides cross-ref steps 3 + 6c; genesis actors → `2`; `require_l1_evidence` literal prefix `verify-step:` |
| 2026-07-12 | K9a-r8 `findings` (R8-M1–M2, R8-N1–N2) + 8-fix: `require_verdict_on` allowlist + hook-not-enabled → `4`; `roles_file` v1 path-check + warn/ignore (enum-only); `--json` `dry_run` echoes CLI flag; L1 manifest/progress IO → `5` |
| 2026-07-12 | **K9a-r9 → `pass`**. All prior findings confirmed RESOLVED; full §K9.0–§K9.19 regress clean. Cleared for **K9b** (L1 only). |
