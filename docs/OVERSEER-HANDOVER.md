# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

<!-- overseer:next role=primary lane=product status=live -->
<!-- overseer:anchor:next-session -->
## NEXT SESSION — FRV-b Freeze-review verdict integrity build

**Date:** 2026-09-12  
**Current position:** **FRV-a DONE** (freeze `pass`, FRV-r5) → **FRV-b** (Auto, one build)  
**Model:** Auto

### What just landed

| Slice | Deliverable |
| --- | --- |
| **FRV-a** | `docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md` → `pass` (FRV-r5), mechanical stamp `sha256:c113efa3…`. F1–F7 frozen as **one** Auto build. Spec-only. |

### THE ONE NEXT STEP — **Model: Auto**

Build FRV-b exactly to the frozen artifact, as **ONE** build. F1–F7 share the same functions
(`tools/freeze_reviewer/stamp.py:27-101`, `tools/governance_hygiene/next_regen.py:395-524`), so
splitting them would land a tree where the stamp is relabelled but still authorizing, or where
authorization moved but a prose fallback still bypasses it.

**What the freeze fixes, in one line:** a verdict record must not live inside the artifact it
judges. Today a four-regex keyword scan writes a hardcoded `verdict: pass` into the document it
graded, signs a `reviewer_model` that never ran, erases a human downgrade on the next run, and
that field authorizes a mechanical build session.

Three things in the freeze that are easy to miss and are load-bearing:

1. **§FRV.6.5.1 — the gate must cover plain `Auto`, not just `Thinking → Auto`.** FRV-r4 caught
   this as BLOCKER-class: only **4** of **103** live roadmap rows carry the split label (all long
   DONE) against **43** plain `Auto`, so a gate wired to the split label alone is dead code here.
2. **§FRV.6.4.1 — one `phase_id` derivation for both readers.** `governance_gates/scan.py:121`
   uses display strings while `next_regen.py:512` uses `compact_step_id`; left alone they would
   query the ledger under different keys and assert opposite things about one slice.
3. **§FRV.6.6 — `mechanical_only` is an `advisory`, never a `reason`.** Any non-`None` `reason`
   short-circuits `plan_next_regen` to ambiguity (`next_regen.py:556-557`), which would suppress
   NEXT regeneration instead of emitting Thinking.

**Live dogfood irony to preserve, not fix:** the stamp now on the freeze artifact reads
`verdict: pass`, `reviewer_model: thinking-high`, `reviewer_provider: local` — the exact false
claim the artifact indicts (P6/P9). Leave it. FRV-b's own first `ok review --freeze` run will
rewrite it to the fourteen-key shape **once**, and that single rewrite is the per-document
migration (§FRV.9.3 step 2). It must **not** change `artifact_digest`.

| | |
| --- | --- |
| **ID** | **FRV-b** |
| **Branch** | `feat/freeze-review-verdict-integrity` |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md`; `docs/ROADMAP.md`; `docs/OVERSEER-HANDOVER.md` |
| **Hard stops** | No merge to `main` without Tier 3 · no secrets · no live posture flips · do not split F1–F7 · do not rewrite archived phase docs · do not renumber exit codes · do not break the v1 ledger chain · do not change honesty Mode A–D · no config knob for the prose fallback or the legacy window · not DONE on green tests alone |
<!-- /overseer:anchor:next-session -->

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — FRV-b

```text
FRV-b — Freeze-review verdict integrity build (overseer-kit).

Model: Auto
Repo: overseer-kit
Branch: feat/freeze-review-verdict-integrity
Step: FRV-b
Authority: authoritative

Read first: docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md (frozen,
FRV-r5 pass); docs/ROADMAP.md (FRV-a + FRV-b rows); docs/OVERSEER-HANDOVER.md.

Build exactly to the frozen artifact as ONE build. Do not redesign. Do not re-derive
§FRV.1 — every problem claim is already verified with a file+line citation. Do not split
F1-F7: they touch the same functions (tools/freeze_reviewer/stamp.py:27-101,
tools/governance_hygiene/next_regen.py:395-524), so a partial landing leaves the stamp
relabelled but still authorizing, or authorization moved while a prose fallback bypasses it.

Deliverables:
- F1 (§FRV.3) Fourteen-key stamp: `gate: mechanical` + `mechanical_verdict`; `verdict`
  reserved and never written. §FRV.3.4 legacy resolver (six branches,
  ACCEPT_LEGACY_VERDICT_STAMP) implemented ONCE in the new shared module and used by all
  three readers. Serializer key-order contract (serializer.py:10-31) untouched.
- F2 (§FRV.4) produced_by / provider_kind / checklist_ids / checklist_source /
  findings_count. New producer_identity() on the ReviewProvider Protocol, called AFTER
  provider.review() returns; a provider double lacking it resolves ("unknown",
  "rule_engine"). reviewer_model MUST be null whenever provider_kind is rule_engine.
- F3 (§FRV.5) Merge unknown keys instead of replacing; refuse to escalate a non-pass
  record; flag --override-non-pass-stamp; EXIT_STAMP_ESCALATION_REFUSED = 39 in
  tools/freeze_reviewer/engine.py; reason name stamp_escalation_refused; precedence
  2 > 4 > 5 > 39 > 8 > 7 > 0; no 39 under --dry-run / --no-stamp; four-condition true
  no-op. Pass the flag through cli/commands/check_ok.py:82-92.
- F4 (§FRV.6) Additive ENTRY_KINDS value freeze_review + validate_append_body branch +
  genesis forbid-list + find_matching_freeze_review beside the existing three. New module
  tools/freeze_authorization/ as the single reader shared by next_regen and
  governance_gates/scan. Gate BOTH `Thinking → Auto` and plain `Auto`; exclude
  `Operator + Auto`; add REASON_FREEZE_NOT_SUBSTANTIVE. mechanical_only travels as an
  `advisory` field, never as `reason`.
- F5 (§FRV.7) Delete BOTH prose fallbacks: next_regen.py:415-436 (remove _freeze_pass_state
  entirely) and governance_gates/scan.py:236-241 (_narrative_freeze_pass). No opt-in knob.
- F6 (§FRV.8) Honor auto_may_start: false as a real block, including the malformed
  fail-closed case. The CLI never writes, removes, or normalizes it.
- F7 (§FRV.9) Reconciliation only. No archived phase doc is rewritten.
- Seven-tier §FRV.12, test file prefix test_frv_.
- Update tests/unit/test_gs_paste_next_regen.py:78 and :94 to the new
  decide_split_emission signature (4-tuple, keyword-only config).
- Doc touchpoints: docs/CHECK-OK.md, tools/freeze_reviewer/README.md, SPEC §6 pointer.

Three easy-to-miss, load-bearing items:
1. §FRV.6.5.1 — plain `Auto` must gate. Only 4 of 103 live roadmap rows use
   `Thinking → Auto` (all DONE) vs 43 plain `Auto`; split-label-only is dead code here.
2. §FRV.6.4.1 — one phase_id derivation (compact_step_id) for BOTH readers, or the gate
   scan and the emission path query the ledger under different keys.
3. §FRV.6.6 — any non-None `reason` suppresses NEXT regeneration (next_regen.py:556-557).

Do NOT: rewrite archived phase docs; renumber any exit code; break the v1 ledger chain;
change honesty Mode A/B/C/D; add a config knob for the prose fallback or the legacy
window; dispatch a review model; change consumer defaults; roll out to consumers.

Hard stops: No merge to main without Tier 3 · no secrets · no live posture flips ·
 not DONE on green tests alone — /build-verification-review must pass FROM A SECOND CHAT
 with an independent_second_review ledger entry appended first (require per
 .overseer/config.yaml:57).

Governance sync: update roadmap + handover together on completion.
```
<!-- /overseer:anchor:paste-ready-prompt -->

---

## Shared context (canonical — prepend only when paste fence omits it)

| | |
| --- | --- |
| **Project** | 🆗 Overseer Kit — repo-agnostic governance vendoring CLI |
| **Read** | `docs/OVERSEER-KIT-SPEC.md`; target phase in `docs/ROADMAP.md`; this handover |
| **Guardrails** | No secrets; fail-closed VCS reads; no MuseHub-only baseline features; no Tier-3 automation |
| **Tests** | Seven tiers per `policy/test-tiers.yaml` before DONE |
| **Close** | Update ROADMAP + this handover together; feature branch → PR (no commit/push without consent) |
| **Governance gates** | §KH1.9 **live** — `ok status` + `governance-sync` pending-gate reminders |
| **Muse dev tree** | `ok status --exit-code` must show `substrate.ok: true`, `muse_sync.ok: true`, **and** `footprint_self_integrity.ok: true` before phase DONE. Hollow substrate → `muse init --force .`; Muse behind Git (`muse_sync: pending`) → `muse code add -A && muse commit -m "…"`; declared-but-absent kit file (`footprint_self_integrity: missing`) → `ok sync` (all Tier 1) |
| **Handover shape (KH1)** | Every NEXT must include valid **`Model:`** from `policy/model-labels.yaml` **and** a `### Paste-ready prompt` fenced block (H7/H8). Never use `Operator choice` as a Model label. |

---

<!-- overseer:anchor:verified-snapshot -->
## Verified snapshot

| Area | State |
| --- | --- |
| **VCS regime** | `muse+git-mirror` |
| **GitHub main** | `8358f968155a66b2e45bf68237bb324fb2de7601` |
| **Canonical anchor** | `sha256:1742cd1969fb4061a1b5b4521b3bca9c6a5aa969a848c496716ad2fe4bfac2e2` |
| **Canonical main** | `sha256:1742cd1969fb4061a1b5b4521b3bca9c6a5aa969a848c496716ad2fe4bfac2e2` |
| **Branch** | `main` |
| **Dirty** | `no` |
| **Drift** | D1=drifted, D2=aligned, D3=aligned |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-09-05)

| Item | Value |
| --- | --- |
| Branch | `main` |
| GitHub `main` | `8358f968155a66b2e45bf68237bb324fb2de7601` |
| Canonical anchor | `sha256:1742cd1969fb4061a1b5b4521b3bca9c6a5aa969a848c496716ad2fe4bfac2e2` (.muse/git-bridge.toml:last_export.muse_commit_id) |
| Muse `main` | `sha256:1742cd1969fb4061a1b5b4521b3bca9c6a5aa969a848c496716ad2fe4bfac2e2` |
| Dirty | no |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
- **2026-09-12** — **FRV-a DONE (Thinking freeze).** `docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md` → `pass` (FRV-r5), mechanical stamp `sha256:c113efa3…`. Froze the repair of the freeze gate itself. Verified by source inspection, not assumed: the default reviewer is a four-regex keyword scan (`tools/freeze_reviewer/providers/base.py:15-19`, `:51-125`) that accepts a `reviewer` argument and never reads it (`:145-160`); its result is written as the hardcoded string `pass` (`tools/freeze_reviewer/stamp.py:33-42`) under the **same** key and vocabulary a substantive review uses (`tools/freeze_reviewer/types.py:18`, `:82-91`), asserting a `reviewer_model` with no causal role — **all 31** stamped archive docs carry that identical false claim. Because `pre_stamp_canonical_bytes` excises `review_stamp` before hashing (`tools/freeze_reviewer/artifact.py:119-147`) and the no-op guard requires an existing `pass` (`tools/freeze_reviewer/stamp.py:45-52`), a human downgrade **fails** the guard and the write proceeds as a wholesale replacement (`:55-58`) — sticky when pass, self-healing back to pass when a human objects. That field authorizes a mechanical build session (`tools/governance_hygiene/next_regen.py:517-524`), and with no stamp a bold `**pass**` in a prose table suffices (`:415-436`). Two readers and two prose fallbacks found, not one: `tools/governance_gates/scan.py:133` + `:236-241` were unenumerated in the brief and are now in scope; the reader set is **closed at three modules**. Root cause frozen: *a verdict record must not live inside the artifact it judges* — reusing the ISR ledger machinery rather than inventing a parallel mechanism. F1 vocabulary split (fourteen-key stamp, legacy window, all 31 digests provably stable since the stamp is excised pre-hash); F2 self-describing stamp with `reviewer_model` **null** under a rule engine; F3 merge-not-replace + escalation refusal + `--override-non-pass-stamp` + exit `39`; F4 additive hash-chained `freeze_review` kind matched on `phase_id` + `frozen_spec` + `artifact_digest`; F5 **both** prose fallbacks deleted, no opt-in; F6 `auto_may_start: false` honored, its locus outside `review_stamp` chosen so flipping it invalidates any bound entry; F7 reconciliation over the enumerated archive (40 docs: 31 mechanical, 5 prose-only, 4 already inert) with no bulk rewrite and no retro-failed DONE row. Narrowly revisits the `PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:182` rejection for the freeze gate only — ledger record required, session independence **not** imported. Five rounds; **FRV-r4 caught a BLOCKER-class reachability defect**: the gate was wired only to `Thinking → Auto`, which is **4** of **103** live roadmap rows (all long DONE) against **43** plain `Auto`, so it would have been dead code under this repo's own two-row convention → §FRV.6.5.1 extends it via the existing §GSP.4.3 ambiguity channel. FRV-r3 also caught a fourteen-vs-thirteen key-count error and a `phase_id` divergence between the two readers (§FRV.6.4.1). Seven-tier §FRV.12, prefix `test_frv_`. **No FRV-b Auto code, no test file, no CLI edit this session.** NEXT → **FRV-b** (Auto, one build) on `feat/freeze-review-verdict-integrity`.

- **2026-09-05** — **NXP → main DONE (land-b).** GitHub PR [#78](https://github.com/aaronrene/overseer-kit/pull/78) merged @ `c921bf1` (NXP-a freeze + NXP-b build). Muse FF `sha256:c07f2f34…` → muse-bridge → squash. Post-merge sync; N5 backlog unblocked (§NXP.7). NEXT → **queue-idle**.

- **2026-09-04** — **NXP-b DONE** — **BV-r2 `pass` + ISR `pass`** from independent verifier `2869c11a…` (≠ producer `3a3eda52…`, who was BV-r1 verifier then NXP-b-FIX producer). V1–V8 over `940c3b4..HEAD`, covering both the build commit `410ddc1` and the test fix `6c35b72`. BV-r1's findings were **re-derived by mutation rather than trusted**: 12 targeted mutations run against the NXP tiers, 10 killed. The rewritten §NXP.8 e2e row fails (`2 ≠ 0`) when N4 is folded into `--exit-code` while the pre-fix `410ddc1` row *passes* under the identical mutation; the rewritten data-integrity row fails on a **newline-only** fence-body change while the pre-fix row *passes* (content-byte changes are caught by both) — BV1 and BV2 confirmed real, and confirmed genuinely closed. Verified live: twelve-step layout with heading byte-exact on line 1, four ` · ` U+00B7 separators, stdout minus provenance+blank reproducing pre-NXP nine-step bytes exactly, `check-next` unconfigured at exit `0` naming bare basename **and** compliant target, board-naming advisory printing while `ok status --exit-code` returns `0`. Exit precedence `2 > 6 > 35 > 3 > 0`, `CURRENT_NEXT_HEADING`, and `extract_paste_fence_body` untouched. §NXP.8 **54** green; suite **1343** pass / **16** pre-existing, failure set identical to parent `940c3b4` in matched worktree environments. Ledger: `verification_evidence` `bv_verdict: pass` round 2 (`test_output` sha256:`d4c5e0ae…`) + `independent_second_review` `isr_verdict: pass` (`8e5e49d9…`); `ok ledger verify` → `0`; Mode B and Mode D → `0`. Two non-blocking observations recorded in NEXT (unasserted `check-next --json` payload fields; unreachable `is_absolute()` guard) plus a frozen-spec factual slip in §NXP.1 V6. **No merge to `main`** — NEXT → **NXP-land-a** (Tier 3).

- **2026-09-04** — **NXP-b-FIX applied** @ `6c35b72` (producer `3a3eda52…` — same session as BV-r1, so **it cannot verify this**). Made the two vacuous §NXP.8 rows real: BV1 e2e now uses an initialized fixture that exits `0` on all pre-existing conditions and asserts the N4 advisory fires **and** exit stays `0`; BV2 reconstructs pre-NXP nine-step stdout and asserts byte-for-byte equality after removing exactly the provenance line + blank. BV4 adds §NXP.3.6 refusal (exit `2`, reason token, message, empty stdout), the `absolute_repo_root` failure predicate, and §NXP.4 failure-shape keys; dropped the discarded first `read_at_now()`; restored `tools/workspace/__init__.py` trailing newline. **No N1–N4 behavior change.** All three original mutations now fail the correct tier. Suite **1343** pass / **16** pre-existing. NEXT → **NXP-b-BV-r2** in a fresh chat (ISR `producer_session_id: 3a3eda52…`).

- **2026-09-04** — **NXP-b-BV-r1 → `findings`** (second chat, verifier `3a3eda52…`; **no ISR appended**). V1–V8 against frozen `PHASE-NXP-NEXT-PROVENANCE.md` §NXP.3–§NXP.6: implementation **correct** — verified live, not just green (twelve-step bytes + U+00B7 separators, N2 keys on both JSON shapes, N3 exit `0`, N4 advisory present while `ok status --exit-code` → `0`, no secrets/env/subprocess added, `board_name_violation` reused not forked). Full suite **1340** pass / **16** fail, byte-identical on parent `940c3b4`. Findings are test-honesty, not behavior: **BV1** §NXP.8 e2e exit-code row tautological (`tests/e2e/test_print_next_e2e.py:132-134`) and **BV2** data-integrity fence-body golden newline-insensitive (`tests/data_integrity/test_print_next_integrity.py:78-88`) — both proven vacuous by mutation; **BV3** builder producer nonce unrecorded, so `actor_session_id ≠ producer_session_id` is unassertable; **BV4** §NXP.3.6 / §NXP.4 branches untested. `verification_evidence` `bv_verdict: findings`, `test_output` sha256:`a1ea596e…`. NEXT → **NXP-b-FIX** then BV-r2 in a third chat.

- **2026-09-04** — **NXP-b code complete** on `feat/nxp-next-provenance` (not DONE). N1 twelve-step provenance + clock seam; N2 JSON identity keys; N3 `check-next` advisory exit `0`; N4 status board-name warn. §NXP.8 **45** green. Full suite **1340** pass / **16** pre-existing unrelated fails. NEXT → second-chat BV + ISR (`require`).

- **2026-09-02** — **ISR default → `require`** (operator posture). Absent key / shipped default is now `require` (was `off`); kit dogfood `require` (was `warn`). Opt out: `off` or `warn`. PHASE-ISR operator amend recorded. Closed-loop premise.

- **2026-09-02** — **ISR → main + MuseHub solidify DONE.** Hub → staging; created `aaronrene/overseer-kit`; pushed 85 commits; PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) @ `84db8c8`. NEXT → **queue-idle**.

- **2026-09-02** — **MuseHub-first before ISR merge** — Gap confirmed: hub `localhost:1337` dead; `aaronrene/overseer-kit` 404 on staging/production. Operator: solidify MuseHub staging then merge PR #74. Handover + paste + `MUSE-BRIDGE-WORKFLOW.md` retargeted.

- **2026-09-02** — **ISR → main land-a** — Muse FF `feat/isr-independent-second-reviewer` → `main` (`sha256:f59d4cc6…`) → muse-bridge → GitHub PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) OPEN/mergeable. Rebased stale `muse-mirror` onto `main` before re-export (LT #72/#73 had bypassed mirror). Merge held for MuseHub-first. `require_independent_second_reviewer` remains kit dogfood **warn**.

- **2026-09-02** — **ISR-b DONE** (Auto + second-chat BV `pass`, ISR-b-BV-r1). V1–V8 against freeze + branch diff; `independent_second_review` pass (actor `c72e9414…` ≠ producer `62762b24…`); Mode B `verification_evidence` (`test_output` sha256:`4a82e963…`). `test_isr_` **48** green. NEXT → **ISR → main (land-a)**. No merge this session.

- **2026-09-02** — **ISR-a DONE (Thinking freeze).** `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md` → `pass` (ISR-r4), stamp `sha256:e6284150…`. Second-chat / separate-verifier gate before Auto DONE; kit records/gates only; no model dispatch; portable CLI+docs primary; seven-tier §ISR.11 frozen. **No ISR-b Auto code this session.** NEXT → ISR-b Auto on `feat/isr-independent-second-reviewer`.

- **2026-09-02** — **consumer-lt-rollout DONE.** `ok sync` LT footprint into Knowtation, Scooling, VideoFactory, the-brain, bornfree-hub, ourware, scooling-lab, scooling-sc-brain. Knowtation/Scooling: `session_bookends` + honesty warn + hooks; VF/the-brain: bookends + hooks (honesty tip deferred). Knowtation/VF used `--only` to avoid clobbering living docs / consumer-modified policy. All synced repos `footprint_coverage: ok`. Deferred: MuseHub (no config.yaml), bornfree/ourware/lab bookends, VF full `--force` on customized tiers/rules, Knowtation `origin:kit` living-doc lock hygiene. NEXT → **ISR-a** (Independent second reviewer Thinking freeze).

- **2026-09-02** — **LT → main DONE (land-b).** GitHub PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) merged @ `ff737cc` (LT-a freeze + LT-b build). Local `main` FF; post-merge hygiene; NEXT → **consumer-lt-rollout**.

- **2026-09-01** — **LT-b DONE (Auto build + BV `pass`, LT-b-BV-r1).** Built exactly to frozen `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md`: footprint coverage gate; `session_bookends` (default off, dogfood enabled + hooks synced); kit honesty warn + active-slice Mode B; `ok handover-compact` + dogfood compact (**88** archived); optional-feature tips on `ok status`; workspace-root docs; §LT.10 **34** green. `ok sync --force` applied; `footprint_coverage: ok`. No consumer defaults; no tab-reload claim. NEXT → **queue-idle**.

- **2026-09-01** — **LT-a DONE (Thinking freeze).** `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md` → `pass` (LT-r2), stamp `sha256:6a5aafb5…`. Slices 1–4 frozen. **No LT-b Auto code this session.** NEXT → LT-b Auto on `feat/loop-tightening`.

- **2026-09-01** — **LT-a drafted (Thinking freeze, review pending).** Slices 1–4 in `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md` on `feat/loop-tightening`. Backlog captured: independent second reviewer, KH2 remask, session-type bookends, auto-enable hooks, host tab reload. No Auto code.

- Older entries: docs/archive/handover/CHANGE-LOG.md
<!-- /overseer:anchor:change-log -->

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `docs/ROADMAP.md` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Build verification (mandatory):** after `{step}b`, run `/build-verification-review` before ROADMAP status → **DONE**.
5. **Closing commit:** the session-ending commit bundles code/tests + `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md`.
6. **Change log compaction:** living change log keeps the newest 15 dated bullets. Older bullets move via `ok handover-compact --write` to `docs/archive/handover/CHANGE-LOG.md`.

See `docs/ROADMAP.md` → Model-split handover protocol (SD-3) and governance sync (SD-17).

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| **FRV-a** | Freeze-review verdict integrity **freeze `pass`** (FRV-r5), mechanical stamp `sha256:c113efa3…`. F1–F7 frozen as one Auto build: vocabulary split, self-describing stamp, inverted stickiness, ledger-based Auto authorization, both prose fallbacks deleted, operator block honored, archive reconciliation. Spec-only. |
| **NXP → main** | PR [#78](https://github.com/aaronrene/overseer-kit/pull/78) merged @ `c921bf1` (NXP-a + NXP-b). Muse `sha256:c07f2f34…`. |
| **NXP-b** | NEXT provenance + board identity **DONE** on `main`: N1 provenance line, N2 JSON identity keys, N3 `check-next` advisory at exit `0`, N4 `ok status` board-name warn. BV-r2 `pass` + ISR `pass`. |
| **ISR → main** | PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) merged @ `84db8c8` (ISR-a freeze + ISR-b + MuseHub docs). |
| **MuseHub solidify** | Hub → `staging.musehub.ai`; public `aaronrene/overseer-kit`; kit dogfood matches Knowtation/Scooling hub posture. |
| PR #73 | docs: LT land-b closeout + consumer rollout NEXT (merged 2026-09-02) |
<!-- /overseer:anchor:done-recently -->

## Change log

- **2026-09-12** — **FRV-a DONE (Thinking freeze).** `PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md` → `pass` (FRV-r5), stamp `sha256:c113efa3…`. F1–F7 frozen as **one** Auto build; verdict records move off the artifact and onto the hash-chained ledger. FRV-r4 caught a BLOCKER-class reachability defect (split-label-only gating = dead code; 4 of 103 rows). NEXT → **FRV-b**.

- **2026-09-05** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `8358f96`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-05** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `bdf1f20`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-05** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `1e1582c`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-05** — **NXP → main DONE (land-b).** PR [#78](https://github.com/aaronrene/overseer-kit/pull/78) @ `c921bf1`. NEXT → **queue-idle** (N5 backlog unblocked).
- **2026-09-04** — **NXP-b DONE.** BV-r2 `pass` + ISR `pass` (verifier `2869c11a…` ≠ producer `3a3eda52…`). BV-r1's two findings re-derived by mutation and confirmed closed. NEXT → **NXP-land-a** (Tier 3, no merge yet).
- **2026-09-04** — **NXP-b-BV-r1 → `findings`** (second chat). Implementation matches §NXP.3–§NXP.6; two §NXP.8 matrix rows asserted vacuously (mutation-proven). No ISR, no DONE. NEXT → **NXP-b-FIX**.
- **2026-09-04** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `ce16f9b`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-02** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `fc2ecb0`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-02** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `945d034`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-02** — **ISR → main + MuseHub solidify DONE.** PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) @ `84db8c8`; staging hub hosts kit. NEXT → **queue-idle**.
- **2026-09-02** — **MuseHub solidify DONE** — connected `staging.musehub.ai`; created public `aaronrene/overseer-kit`; first push 85 commits.
- **2026-09-02** — **ISR-b DONE** (Auto + BV `pass`, ISR-b-BV-r1).
- **2026-09-02** — **ISR-a DONE (Thinking freeze).** PHASE-ISR → `pass` (ISR-r4).
- **2026-09-02** — **consumer-lt-rollout DONE.** LT synced to live consumers.
- **2026-09-02** — **LT → main DONE (land-b).** PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) @ `ff737cc`.
