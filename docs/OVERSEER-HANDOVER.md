# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

## NEXT SESSION — Track P / P-deploy deployment-gate freeze (▶ NEXT)

**Date:** 2026-07-13  
**Current position:** **Track O / O3 Stage 3 upgrade-regime build DONE** (build-verified →
`pass`, O3-BV-r2). Track O kit chain (O0–O3) complete; §O2.6 product one-click may wrap
**only** `ok upgrade-regime`. Live Scooling `ok init` remains operator-gated.  
**Model:** **thinking-high**  
**Operator note:** Next queued exploration item is **P-deploy** (Thinking freeze only). Spec-only —
no deploy execution in the kit.


### What just landed


| Slice                                                             | Deliverable                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Track O / O3 Stage 3 upgrade-regime build DONE (Auto)**         | `ok upgrade-regime` (§O2.7); runbook `docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md`; product-contract + `tools/track_o/` retarget; SPEC §5. Seven-tier §O2.9. Full suite **761** green. `/build-verification-review` **`pass` (O3-BV-r2)**. No signup UI; no live consumer init; no C8.                                                                                                                                       |
| **Track O / O2 Stage 3 kit upgrade ceremony DONE (Thinking)**     | `docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md` reviewed → **`pass` (O2-r3)**, stamp `sha256:ac970077…`.                                                                                                                                                                                                                                                                                                                    |
| **Track O / O1 Normie custody product contracts DONE (Auto)**     | Product contract pack + harness; **728** suite baseline before O3.                                                                                                                                                                                                                                                                                                                                                             |
| **Track O / O0 Normie custody funnel DONE (Thinking)**            | `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` reviewed → **`pass` (O0-r3)**.                                                                                                                                                                                                                                                                                                                                                |



### THE ONE NEXT STEP — **Model: thinking-high**


|                |                                                                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **ID**         | **Track P / P-deploy** (Thinking)                                                                                                   |
| **Branch**     | `feat/track-p-p-deploy-freeze` (suggested)                                                                                          |
| **Read first** | `docs/ROADMAP.md` exploration backlog P-deploy; `docs/PHASE-TRACK-P-P-EVIDENCE.md`; build-verification skill V8                   |
| **Deliver**    | Freeze deploy/health claim gate (kit records/gates only — never deploys); seven-tier matrix; stamp via `/freeze-review-loop` → `pass` |
| **Hard stops** | No kit-side deploy/HTTP probe to production; no Tier-3 merge; no redesign of Track O ceremony                                       |



### Paste-ready prompt — Track P / P-deploy

```
Phase Track P / P-deploy — deployment-gate freeze (overseer-kit).

Model: thinking-high

Read first: docs/ROADMAP.md (exploration backlog P-deploy);
  docs/PHASE-TRACK-P-P-EVIDENCE.md;
  docs/OVERSEER-KIT-SPEC.md;
  .cursor/skills/freeze-review-loop/SKILL.md;
  docs/OVERSEER-HANDOVER.md (shared context).

Task: Thinking freeze only — define the live-deploy sibling of build-verification:
  - Kit records/gates a verifiable deploy/health claim before "shipped" → DONE
  - Boundary: kit never performs the deploy / never HTTP-probes production by default
  - Artifact types / ledger linkage vs P-evidence; seven-tier matrix; rejection table
  - Stamp via /freeze-review-loop → pass; queue Auto only after frozen: true

Hard stops: no deploy code in kit; no live consumer probes; no Tier-3 merge; no Track O redesign.
```



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
| **Repo** | overseer-kit |
| **VCS regime** | `muse+git-mirror` (canonical: muse) |
| **Governance docs** | `docs/OVERSEER-HANDOVER.md`, `docs/ROADMAP.md` |
| **KH1 contract** | `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` — **reviewed → `pass` (KH1-r2)** |
| **KH2 contract** | `docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md` — **reviewed → `pass` (KH2-r2)**; Auto build **DONE** |
| **KH3 contract** | `docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md` — **reviewed → `pass` (KH3-r2)**; Auto build **DONE** |
| **Kit version** | `0.1.0` (`VERSION`) |
| **K12 / Track N** | **DONE** — landing + scenario gallery + LICENSE + funnel |
| **KH1 Handover relay** | **DONE** — contract `pass` (KH1-r2); §KH1.6 close-out complete |
| **Track P / P0** | **DONE** — agent identity & signed provenance; contract reviewed → `pass` (P0-r2), stamp `sha256:7db8681…` |
| **Track P / P1** | **DONE** — agent provenance build-verified → `pass` (P1-BV-r2); BV1 (§P0.6 verify-surface parity) fixed; **429** tests green (+30 §P0.8) |
| **Track P / P-route** | **DONE** — Thinking freeze (`docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` reviewed → `pass`, P-route-r2) + Auto build (build-verified → `pass`, P-route-BV-r1). Declarative model-routing policy shipped: `policy/model-routing.yaml`, `model_tiers`, `model_routing:` config, `overseer route`, exit `30`/`31`. **529** tests green (+43 §PR.8). Kit = rule-holder, runtime = executor |
| **Track P / P-cost** | **DONE** — Thinking freeze (`docs/PHASE-TRACK-P-P-COST-AWARENESS.md` reviewed → `pass`, P-cost-r2) + Auto build (build-verified → `pass`, P-cost-BV-r1). Cost-awareness surface shipped: `cost_class` on `model_tiers`, `tools/cost_awareness/`, `cost_awareness:` config, additive `overseer route` cost fields, exit `32`, status + governance-sync reminders. **569** tests green (+40 §PC.9). Kit = cost-awareness rule-holder, runtime = spender |
| **Track P / P-evidence** | **DONE** — Thinking freeze (`docs/PHASE-TRACK-P-P-EVIDENCE.md` reviewed → `pass`, P-evidence-r3) + Auto build (build-verified → `pass`, P-evidence-BV-r1). Verification-evidence capture shipped: `verification_evidence` kind, artifact types, `require_verification_evidence`, honesty-status Mode B, exit `33`, twin build-verification V8 delta. **612** tests green (+43 §PE.10). Kit records/gates; never deploys |
| **Track Q / Q0** | **DONE** — Thinking freeze (`docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` reviewed → `pass`, Q0-r2), stamp `sha256:3c3f6229…`. Freezes `overseer app` local-only UI contract |
| **Track Q / Q1** | **DONE** — Auto build (build-verified → `pass`, Q1-BV-r1). `overseer app` stdlib loopback server + static UI; `tools/app/` + `cli/commands/app.py`; closed `api/*`; Bearer + CSRF; seven-tier §Q0.12. **654** tests green (+42) |
| **Track Q / Q2a**         | **DONE** — Thinking freeze (`docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md` reviewed → `pass`, Q2a-r2), stamp `sha256:dbfbf9ad…`. Freezes canonical `ok` CLI entrypoint + `overseer` compat shim; seven-tier §Q2A.10. Spec-only. Cleared for Q2b |
| **Track Q / Q2b**         | **DONE** — Auto build (build-verified → `pass`, Q2b-BV-r1). `cli/ok` canonical + `cli/overseer` deprecation; `prog="ok"`; operator docs/templates/skills/CI pass; SPEC §5 + K4.1 naming; shims not footprint members. **668** tests green (+14 §Q2A.10). Cleared for Q3 |
| **Track Q / Q3**          | **DONE** — Auto build (build-verified → `pass`, Q3-BV-r1). Tauri desktop shell (`desktop/`) invokes `ok app`; `tools/desktop/` + bundle script; seven-tier §Q3. **696** tests green (+28). Track Q chain complete |
| **K6-Scooling runbook**   | **DONE** — `docs/consumers/scooling/OVERSEER-SETUP.md` (kit-side; live init still operator-gated; Track O cross-link in O1) |
| **Track O / O0**          | **DONE** — Normie custody funnel Thinking freeze (`docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` reviewed → `pass`, O0-r3), stamp `sha256:642076c9…` |
| **Track O / O1**          | **DONE** — Product contracts build-verified → `pass` (O1-BV-r1). Contract + Scooling/Knowtation stubs + `tools/track_o/` + §O0.8. **728** tests green (+32) |
| **Track O / O2**          | **DONE** — Stage 3 kit upgrade ceremony Thinking freeze (`docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md` reviewed → `pass`, O2-r3), stamp `sha256:ac970077…` |
| **Track O / O3**          | **DONE** — `ok upgrade-regime` build-verified → `pass` (O3-BV-r2). Runbook + contract/harness retarget; **761** tests green (+33 §O2.9). Track O kit chain complete |
| **CLI entrypoint**        | **`ok`** (canonical `./cli/ok`); **`overseer`** compat shim (`./cli/overseer`, one-line stderr deprecation) |
| **CLI subcommands**       | `init` \| `sync` \| `status` \| `review --freeze` \| `governance-sync` \| `verify-step` \| `honesty-status` \| `ledger` \| `route` \| `app` \| `upgrade-regime` |
| **Muse dogfood** | **D2 repaired** + substrate health + gate reminders + **muse-sync hard gate (KH2)** + **footprint self-integrity hard gate (KH3)** live; `muse rev-parse` reads plain-text SHA (0.2.x returns bare SHA on success; JSON only on failure/non-zero); `governance-sync --dry-run` exits 0; muse canonical HEAD `sha256:3e14450f…` (catch-up commit; genesis `sha256:4671b7f…`) |
| **KH1b** | **DONE** — substrate §1 + gate reminders §2 |
| **KH2** | **DONE** — Muse-sync hard gate (freeze `pass` KH2-r2 + Auto build); `tools/muse_sync/`; fail-closed on `status --exit-code` / `review --freeze` / `governance-sync` |
| **KH3** | **DONE** — Footprint self-integrity hard gate (freeze `pass` KH3-r2 + Auto build); `tools/footprint_integrity/`; fail-closed on `status --exit-code` / `review --freeze` / `governance-sync` when a declared kit-owned file is absent from disk |
| **Public brand** | **🆗 Overseer Kit** (locked in template + landing) |
| **Public landing** | `docs/landing/index.html` · scenario gallery `docs/landing/scenarios/index.html` |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-07-13)

| Item | Value |
| --- | --- |
| Branch                    | `feat/track-o-o3-upgrade-regime`                                                                        |
| HEAD                      | Track O / O3 Stage 3 upgrade-regime build (BV O3-BV-r2) + ROADMAP/HANDOVER close-out                    |
| Muse HEAD | (sync on close-out commit) |
| GitHub bridge | Feature branch (no merge) |
| Dirty                     | clean after O3 close-out                                                                                |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
## Change log

- **2026-07-13** — **Track O / O3 Stage 3 upgrade-regime build DONE (build-verified → `pass`, O3-BV-r2).**
  Shipped `ok upgrade-regime` against frozen O2: `--from muse-only --to muse+git-mirror` with
  `--dry-run` / `--apply` / `--live-bridge` / `--force` / `-y`; C0–C5 fail-closed; G1–G8; hard-stop
  before C8; composes sync/status + K7 bridge invariants (no adapter rewrite). Runbook
  `docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md`; product-contract Stage 3 + `tools/track_o/`
  harness retargeted together (no “deferred to O2” shipping claim; one-click still gated on §O2.6);
  SPEC §5 row. Seven-tier §O2.9 (**+33**); full suite **761** green. BV r1 findings (data-integrity
  mid-write; regime-only mutation honesty; COMPLETE_UPGRADE unit) → fixed; **O3-BV-r2 → `pass`**
  ([verifier](38527ede-ac3d-4c55-ba9f-6d8e4f4a4ad2)). Hard stops held. ROADMAP: O3 → DONE; Track O
  promoted complete. Handover NEXT → **Track P / P-deploy** Thinking.
- **2026-07-13** — **Track O / O2 Stage 3 kit upgrade ceremony freeze DONE (reviewed → `pass`, O2-r3).**
  Closed §O0.3.3 deferral in `docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`: C0–C8 ceremony for
  `muse-only` → `muse+git-mirror`; complete config write (no silent `vcs.regime` edit); footprint
  re-seed via sync/migrate + `--force` rules; bridge dry-run gates G1–G8 (SD-14); product unlock
  §O2.6 (one-click only after O3 BV `pass`); O3 deliverable `ok upgrade-regime` + runbook +
  contract/harness retarget; seven-tier §O2.9. Freeze-review loop: r1 (C1 repair / G8 / CLI flags) →
  fixed; r2 (product-contract retarget deferred to O3 for harness atomicity) → fixed; **O2-r3 →
  `pass`**; stamp `sha256:ac970077…`. **Spec-only — no ceremony code landed.** ROADMAP: O2 → DONE;
  O3 Auto queued. Handover NEXT → **Track O / O3**.
- **2026-07-13** — **Track O / O1 Normie custody product contracts DONE (build-verified → `pass`, O1-BV-r1).**
  Built mechanically against frozen O0: shipped `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`
  (Stages 1–4, §O0.3.3 deferred Stage 3 ceremony, boundary + rejection tables — no redesign);
  Scooling `OVERSEER-SETUP.md` Track O cross-link (live init remains operator-gated); Knowtation
  stub `docs/consumers/knowtation/OVERSEER-SETUP.md` (Stage 4 pointer; no live init); optional
  `tools/track_o/` validator + mandatory seven-tier §O0.8 harness under `tests/` (**+32**; full
  suite **728** green). `/build-verification-review` → **`pass` (O1-BV-r1)**
  ([verifier](56bd3073-49be-4bad-bc94-5ebe858a008f)). Hard stops held: no signup UI, no Stage 3
  ceremony, no live consumer init, no new CLI/adapters. ROADMAP: O1 → DONE; O2 Thinking queued.
  Handover NEXT → **Track O / O2**.
- **2026-07-13** — **Track O / O0 Normie custody funnel freeze DONE (reviewed → `pass`, O0-r3).**
  Refined draft seed into freeze contract `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md`: Track O
  vs K6/Q identity; Stages 1–4; §O0.3.3 Stage 3 kit upgrade ceremony deferred (no silent
  `vcs.regime` edit; product one-click blocked until O2); custody identity; kit vs
  Scooling/Knowtation/MuseHub boundary; rejection table; O1 product-contracts-only deliverables
  (exact paths); seven-tier §O0.8. Freeze-review loop: r1 findings (Stage 3 ceremony gap; stress
  tier; Knowtation path; exact contract path; backlog wording) → fixed; r2 residual Stage 3
  consistency → fixed; **O0-r3 → `pass`**; stamp `sha256:642076c9…`. **Spec-only — no code landed.**
  ROADMAP: O0 → DONE; O1 Auto queued; exploration backlog promoted. Handover NEXT → **Track O / O1**.
- **2026-07-13** — **K6-Scooling consumer runbook + KH1 handover repair + Track O seed.**
  Added `docs/consumers/scooling/OVERSEER-SETUP.md`; cross-linked K6 operator runbook +
  `CONSUMER-ADAPTER-PATTERN.md`; queued Track O / O0 draft
  `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` (not frozen). Fixed Q3 close-out failure:
  NEXT had used invalid `Model: Operator choice` and omitted the paste-ready fence (KH1 H7/H8).
  ROADMAP: K6-Scooling → **DONE**; Track O / O0 → **TODO (Thinking)**; NEXT → Track O / O0.
- **2026-07-13** — **Track Q / Q3 Tauri desktop packaging DONE (build-verified → `pass`, Q3-BV-r1).**
  Shipped cross-platform Tauri shell (`desktop/`): Rust launcher spawns canonical **`ok app`**,
  parses one-time stderr banner (`url`, `session_credential`, `csrf_token`), loads Q1 loopback UI
  via `WebviewUrl::External`, and injects in-memory auth bootstrap (no `localStorage`). Python
  packaging contract in `tools/desktop/` (launcher argv builder, banner parser, manifest validator,
  init-script generator); `scripts/bundle-desktop-kit.sh` copies engine into Tauri resources for
  release builds. **No** new engine subcommands, exit codes, or `api/*` surface changes. Seven-tier
  §Q3: **28** new tests (**696** total green). `/build-verification-review` round 1 → **`pass`**
  (V1–V8 clean). ROADMAP: Track Q / Q3 → **DONE**; Track Q chain complete; NEXT was briefly
  mis-set to operator-choice without paste fence (repaired same day in K6-Scooling close-out).
- **2026-07-13** — **Track Q / Q2b OK CLI entrypoint build DONE (build-verified → `pass`, Q2b-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md`: shipped `cli/ok`
  canonical POSIX shim + `cli/overseer` compatibility shim (exact one-line stderr deprecation);
  `argparse` prog `ok`; operator-facing remediation/banner strings → `ok`; operator docs/templates/
  twin `.cursor/` + `cursor/` skills/CI examples → `ok`; SPEC §5 command table + K4.1 invocation
  amended; footprint integrity + muse-sync remediation strings updated; engine shims explicitly
  excluded from `resolve_footprint` / `version.lock`. Seven-tier §Q2A.10: **14** new tests (**668**
  total green). `/build-verification-review` round 1 → **`pass`** (V1–V8 clean). ROADMAP: Track Q /
  Q2b → **DONE**; NEXT → **Track Q / Q3** Tauri (`ok app` launcher).
- **2026-07-13** — **Track Q / Q2a Freeze OK CLI entrypoint DONE (reviewed → `pass`, Q2a-r2).**
  Drafted and froze `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md`: canonical CLI name `ok`
  (`cli/ok` → `python -m cli.main`; `argparse` prog `ok`); `cli/overseer` remains compatibility
  shim with exact one-line stderr deprecation per process; no subcommand/exit-code/`.overseer/`
  path changes; engine shims explicitly **not** footprint members (supersedes earlier Q2b
  “footprint + version.lock entry” wording); SPEC §5 command table must rewrite to `ok …` in Q2b;
  existing-test stderr migration rule; twin `.cursor/` + `cursor/` skill doc pass; seven-tier
  §Q2A.10. Freeze-review loop: r1 findings (C4 path placeholder; existing-test migration; SPEC
  rewrite mandate; DoD shim spelling; twin skills) → fixed; **Q2a-r2 → `pass`**; stamp
  `sha256:dbfbf9ad…`. **Spec-only — no code landed.** ROADMAP: Track Q / Q2a → **DONE (Thinking)**;
  NEXT → **Track Q / Q2b**.
- **2026-07-13** — **Track Q / Q0 Freeze Overseer App DONE (reviewed → `pass`, Q0-r2).**
  Drafted and froze `docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md`: local-only `overseer app` web UI over
  the existing Python engine (zero rewrite). Frozen surface — CLI `overseer app`; bind default
  `127.0.0.1` (allow `localhost`/`::1`; refuse non-loopback); Bearer + CSRF-header auth (cookies
  deferred); stdlib HTTP server (FastAPI not required); closed `api/*` read/act set (status,
  ROADMAP/HANDOVER, review --freeze, governance-sync, ledger, honesty-status) with §Q0.7.6 body
  schemas; fail-closed CLI parity; seven-tier §Q0.12. Freeze-review loop: r1 findings (path
  notation C4 false positive; CORS/`::1`; POST schemas; status exit_code semantics; auth narrowed;
  multi-lane CLI-only) → fixed; **Q0-r2 → `pass`**; stamp `sha256:3c3f6229…`. **Spec-only — no
  code landed.** ROADMAP: Track Q / Q0 → **DONE (Thinking)**; NEXT → **Track Q / Q1**.

- **2026-07-13** — **Track P / P-evidence Auto build DONE (build-verified → `pass`, P-evidence-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-EVIDENCE.md` (no redesign): ledger kind
  `verification_evidence` + `validate_verification_artifacts` (§PE.3–§PE.4); genesis forbid-list
  extended; `honesty.require_verification_evidence: off|warn|require` (default `off`; `HONESTY_KEYS`
  membership); honesty-status Mode B (`--verification-evidence` / `--frozen-spec`) with Mode A/B
  mutual exclusion; exit `33` + `missing_verification_evidence`; twin build-verification V8 + Evidence
  table skill delta (`.cursor/` + `cursor/` paths). Seven-tier §PE.10 matrix: **43** new tests
  (**612** total green). `/build-verification-review` round 1 → **`pass`** (V1–V8 clean). ROADMAP
  P-evidence build → **DONE**; NEXT was **Track Q / Q0** (now also DONE this session).

- **2026-07-13** — **Track P / P-evidence Thinking freeze DONE (reviewed → `pass`, P-evidence-r3).**
  Drafted and froze `docs/PHASE-TRACK-P-P-EVIDENCE.md`: verification-evidence capture that closes
  build-verification V8's durability gap. Frozen surface — ledger kind `verification_evidence`
  (additive K9a enum amendment; `actor_role=verifier`); closed artifact types
  `test_output`\|`deploy_health`\|`screenshot` (content hashes + opaque refs; no blobs in ledger;
  kit never deploys / HTTP-probes / screenshots); `honesty.require_verification_evidence:
  off\|warn\|require` (default `off`; must join `HONESTY_KEYS`); honesty-status Mode A/B mutual
  exclusion (`--verification-evidence` / `--frozen-spec`); exit `33` +
  `missing_verification_evidence`; normative build-verification skill V8 + Evidence table delta
  (both twin paths); seven-tier §PE.10 matrix. Freeze-review loop: r1 findings (Mode B JSON/token,
  Mode A/B mutual exclusion, `frozen_spec` opacity, flag names, K9a amendment note) → fixed; r2
  findings (`HONESTY_KEYS`, `off` wording) → fixed; **P-evidence-r3 → `pass`**; stamp written by
  `overseer review --freeze` (digest `sha256:c1b9fb3…`). **Spec-only — no code landed.** ROADMAP:
  Track P / P-evidence → **DONE (Thinking)**; added **Track P / P-evidence build** (Auto, TODO).
  Handover NEXT flips to the P-evidence Auto build. **569** tests unchanged.

- **2026-07-13** — **Track P / P-cost Auto build DONE (build-verified → `pass`, P-cost-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` (no redesign): optional
  `cost_class` on `model_tiers` (closed vocabulary `free|low|moderate|high`; recognized key); deterministic
  `paid_step_before_spend` derivation; additive `cost_class` + `paid_step_before_spend` on read-only
  `overseer route` (resolution unchanged); optional default-inert `cost_awareness:` config; active-slice
  spend-awareness surface on `overseer status` (+ `--json`) and `governance-sync` footer (reuses §KH1.9
  scan; reminder-only); exit `32` confined to `overseer route` (status/governance-sync degrade to warning);
  handover template spend-awareness reminder. New module `tools/cost_awareness/`; seven-tier §PC.9 matrix:
  **40** new tests (**569** total green). `/build-verification-review` round 1 → **`pass`** (V1–V8 clean).
  ROADMAP P-cost build → **DONE**; NEXT → **Track P / P-evidence Thinking freeze**.
- **2026-07-13** — **Track P / P-cost Thinking freeze DONE (reviewed → `pass`, P-cost-r2).** Drafted
  and froze `docs/PHASE-TRACK-P-P-COST-AWARENESS.md`: a **cost-*awareness* surface, not a dollar
  pricer**. Frozen surface — an optional, ordinal, **currency-free** `cost_class`
  (`free < low < moderate < high`) on each `model_tiers[]` entry; a deterministic
  `paid_step_before_spend` derivation (`free` + the reserved `human` terminal are unpaid; any other
  band — and, conservatively, an **absent** band → `unknown` — is paid, mirroring vision §1.2
  fail-closed-before-spend); an **additive** `cost_class` + `paid_step_before_spend` annotation on the
  read-only `overseer route` output (routing resolution itself unchanged); an optional default-inert
  `cost_awareness:` config block (`enabled: false`, `surfaces: [status, governance-sync]`); a
  read-only **active-slice spend-awareness surface** on `overseer status` (+ `--json` key) and the
  `overseer governance-sync` footer that reuses the existing §KH1.9 active-slice scan (derives
  `phase_tier` from the slice `Model:` label and `gate` from any pending governance gate; `position`
  stays `None` — deliberate coarseness, the runtime resolves precisely via `overseer route`),
  **reminder-only and never blocking**; a single new non-overlapping exit code `32` (malformed cost
  metadata, **confined to `overseer route`** — `status`/`governance-sync` degrade to a
  `cost_awareness: invalid` warning, matching the frozen `model_routing: invalid` precedent); the
  rule-holder-not-spender boundary table; and the §PC.9 seven-tier matrix. **Boundary held (K7 /
  `AGENTS.md`):** the kit declares the bands and derives the paid flag; the runtime (Cursor /
  OpenRouter / Scooling 9A) converts a band into money and decides spend. **No dollar amount,
  currency, price, budget, spend cap, network connection, or model call in the kit.**
  `/freeze-review-loop`: CLI checklist gate clean both rounds; **P-cost-r1** raised one
  non-escalating MAJOR internal-consistency finding (R1-M1: the exit-code section described a
  malformed-cost-metadata fault as both exit `32` and the existing `2` fail-closed tier on
  `overseer status`, contradicting the warning-only `model_routing` precedent) → fixed minimally by
  confining `32` to `overseer route` and degrading the informational surfaces to a warning;
  **P-cost-r2 → `pass`**; stamp written by `overseer review --freeze` (digest `sha256:9f26678…`).
  **Spec-only — no code landed.** ROADMAP: Track P / P-cost → **DONE (Thinking)**; added **Track P /
  P-cost build** (Auto, TODO). Handover NEXT flips to the P-cost Auto build. **529** tests unchanged.
- **2026-07-13** — **Track P / P-route Auto build DONE (build-verified → `pass`, P-route-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` (no redesign):
  vendored `policy/model-routing.yaml` (v1; first-match-wins + mandatory `defaults`; `fallback[0] ==
  model_tier` terminating in `human`); extended `policy/model-labels.yaml` with `model_tiers`
  (abstract capability tiers, no vendor slugs); optional default-inert `model_routing:` config block;
  read-only `overseer route` (resolve / `--validate` / explain — no model call, no network, no
  dispatch, no key); exit codes `30` (malformed policy) / `31` (missing/unreadable policy);
  `overseer status` routing-validity line when `model_routing.enabled: true`. New module
  `tools/model_routing/`; seven-tier §PR.8 matrix: **43** new tests (**529** total green).
  `/build-verification-review` round 1 → **`pass`** (V1–V8 clean). ROADMAP P-route build → **DONE**;
  NEXT → **Track P / P-cost Thinking freeze**.

- **2026-07-13** — **KH3 Footprint self-integrity hard gate DONE (Thinking + Auto, same session —
  permanent fix for this repo's own self-footprint drift).** Direct follow-on to the seed-fix below:
  after seeding the 13 missing files, closed *why* they were ever silently missing for three days.
  Root cause: `overseer status --check-footprint` (the only existing check that could see this) is an
  opt-in flag, and is not wired into `review --freeze` or `governance-sync` at all — confirmed by
  direct search of both modules. **Freeze** (`docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md`,
  self-reviewed via `overseer review --freeze` checklist + semantic pass; round 1 raised one
  non-escalating MAJOR scope-risk finding — R1-M1: the initial draft trigger was "any kit-owned
  digest mismatch," which would fail-close `review --freeze`/`governance-sync` for *any* consumer
  repo with a legitimate, not-yet-`preserved` content drift (the exact false-positive class this
  session's prior hygiene fix hit for `scripts/muse-bridge-deploy.sh`) — narrowed to
  **declared-but-absent-from-disk only**; **KH3-r2 → `pass`**, stamp digest
  `sha256:4ad2c038…`): new `tools/footprint_integrity/` (`FootprintIntegrityReport`/
  `check_footprint_integrity`) checks every non-`preserved` entry **already recorded in
  `version.lock`** for existence on disk — deliberately never re-resolves the current kit templates
  and never hashes content, so it cannot fail-close on benign drift or on lightweight test fixtures.
  **Auto build** wires it into the same three fail-closed choke points KH1b/KH2 use — `overseer
  status --exit-code` (always-on, no flag — new additive `footprint_self_integrity` JSON key,
  distinct from the existing opt-in `footprint_integrity` string key, which is byte-for-byte
  unchanged), `overseer review --freeze`, `overseer governance-sync` — all reusing the existing exit
  code `2`. **Build-time refinement from the frozen §KH3.4 draft** (documented transparently, not a
  redesign): switched from checking against a fresh `resolve_footprint()` re-render to checking only
  what `version.lock` itself already declares — strictly narrower and more faithful to the actual
  incident (a kit template that has never been through a completed `sync` yet is *drift*, already
  covered by the existing `overseer status` drift check, not "declared but missing"), and this
  change alone took the initial implementation from 31 failing pre-existing tests (fixtures with
  synthetic/empty locks that don't declare the full self-footprint) down to 0. Seven-tier KH3 matrix:
  **30** new tests (**486** total green). Verified live on this repo: `overseer status
  --check-footprint --exit-code` exits `0` with `footprint_self_integrity: {state: ok}` post-fix.
  ROADMAP: added **KH3a** (Thinking, DONE) + **KH3b** (Auto, DONE). NEXT reverts to the **Track P /
  P-route Auto build** (unchanged from before this detour, same as KH2's precedent).

- **2026-07-13** — **Hygiene: seed 13 self-footprint files that were declared in
  `.overseer/version.lock` since K4b (2026-07-10) but never actually existed on disk** — `.cursor/rules/*`
  (4 files), `.cursor/skills/*/SKILL.md` (4 files), `.overseer/policy/*.yaml` (3 files),
  `.overseer/STANDING-DECISIONS.reference.md`. Root cause: the K4b commit (`042ac5c`) hand-authored the
  full manifest shape in `version.lock` to spec out §K4 without ever running `overseer init`/`sync`
  against this dogfood repo itself, and no later phase closed that gap — `overseer status
  --check-footprint` never caught it because `MISSING` classification only blocks `overseer sync`
  (needs a write), it does not fail `status`'s digest check the way `both-changed` does. Confirmed this
  is the exact, already-frozen §K7.3 "new destination absent on disk → seed" path (`docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`
  line 285), so ran `overseer sync --yes` for real (no `--force` needed — none of the 13 were
  conflicts, only `missing`). Verified: no unsubstituted `{{token}}` leakage bugs — `.mdc`/`SKILL.md`/
  policy `*.yaml` files are copied **verbatim** by design (§K4.5, `cli/footprint.py`); the `{{docs.*}}` /
  `{{vcs.*}}` notation inside them is intentional human-readable prose, not a live template token (only
  `ROADMAP.template.md`, `OVERSEER-HANDOVER.template.md`, `STANDING-DECISIONS.template.md`,
  `MUSE-BRIDGE-WORKFLOW.template.md`, and `muse-bridge-deploy.sh.template` go through real
  `render_template()` substitution). No secrets in any seeded file (scanned). `overseer status
  --check-footprint` now reports `footprint_integrity: ok` with `preserved_living` correctly listing only
  the two living docs. 456/456 tests green post-fix.

- **2026-07-12** — **Hygiene: reclassify `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` as
  `origin: preserved` in `.overseer/version.lock`; refresh stale `scripts/muse-bridge-deploy.sh` hash.**
  Root-caused a `footprint_integrity: mismatch` on `overseer status --check-footprint`. Verified by
  rendering each file fresh from its current template + `.overseer/config.yaml` and diffing byte-for-byte
  against the live file: `ROADMAP.md`/`OVERSEER-HANDOVER.md` render to a ~2KB generic seed skeleton vs.
  ~20–28KB live content — genuine, intentional living-doc growth, not drift, confirmed **not** a
  section-structure problem (headers identical `aa9cf74`→`HEAD`, single `NEXT SESSION` block +
  fenced `Paste-ready prompt` stable since `aa9cf74` 2026-07-12 09:25; the multi-block/table regression
  the operator recalled was `3061b5d`→`343093c`, 2026-07-11 08:19–14:12, already self-corrected before
  this fix). `scripts/muse-bridge-deploy.sh`'s fresh render was **byte-identical** to the live file — not
  a customization at all, just a stale `version.lock` hash from before the last real edit; kept
  `origin: kit` and refreshed via `overseer sync --force --only scripts/muse-bridge-deploy.sh` (file
  bytes unchanged, confirmed via `git diff --stat`). Root cause of why `origin: preserved` had to be set
  by hand: `cli/commands/sync.py::_is_preserved_path` only falls back to config's `living_doc_destinations()`
  when a path has **no** prior lock entry; once an entry exists (as here, from initial install) its
  explicit/default `origin` wins, so a living doc that got its first lock entry as `kit` stays `kit`
  forever without a manual reclassification — this is the supported §K6.4 mechanism, not a workaround.
  456/456 tests green post-fix. **New finding surfacing separately (not yet actioned):** `overseer status
  --check-footprint` still reports `mismatch` for a different, unrelated reason — `.cursor/rules/`,
  `.cursor/skills/`, `.overseer/policy/*.yaml`, and `.overseer/STANDING-DECISIONS.reference.md` are all
  declared in `version.lock` but do not exist anywhere in the working tree or git history (no
  `.gitignore` exclusion either) — flagged to the operator for a decision before touching it.

- **2026-07-12** — **KH2 Muse-sync hard gate DONE (Thinking + Auto, same session — permanent fix for
  live MuseHub/GitHub drift).** Diagnosed why Muse fell behind Git on this repo: two git commits
  (`52b7e6e`, `4eb6d26`) landed with no matching `muse commit`, despite `muse+git-mirror` declaring
  Muse canonical (`AGENTS.md`) — a **process gap**, not a tooling defect: `tools/substrate_health/`
  (KH1b) only ever checked that `.muse/HEAD`/`repo.json`/`config.toml` **exist**, never that Muse's
  tracked **content** was current, so nothing could have caught it. Ran the catch-up
  `muse code add -A && muse commit` first (Tier 1; commit `sha256:3e14450f…`), then froze and built
  the permanent gate in the same session so this cannot recur silently. **Freeze**
  (`docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md`, self-reviewed via `/freeze-review-loop`; round 1 raised one
  non-escalating MAJOR internal-consistency finding — R1-M1, the `governance-sync` wiring row
  described `StatusResult` as available before `adapter.status()` is actually called in
  `tools/governance_hygiene/reads.py`, contradicting the verified call order — fixed; **KH2-r2 →
  `pass`**): adds `StatusResult.muse_dirty`/`git_dirty` (populated by all three adapters, defaulted
  `None` — fully additive, existing `.dirty` meaning unchanged); a new `tools/muse_sync/` probe
  (`MuseSyncReport`/`check_muse_sync`) whose **frozen trigger** is precisely `muse_dirty and not
  git_dirty` — Git already clean (committed) while Muse's tracked snapshot still differs — so normal
  mid-edit work (both dirty, nothing committed anywhere yet) is a **frozen non-trigger** and is never
  falsely blocked; `not_applicable` for `muse-only`/`git-only` (single-history regimes have no
  cross-VCS gap). **Auto build** wires `check_muse_sync` into the same three fail-closed choke points
  `substrate_health` already uses — `overseer status --exit-code`, `overseer review --freeze`,
  `overseer governance-sync` — all reusing the **existing exit code `2`** (no renumbering of the
  frozen `status` precedence `2 > 6 > 3 > 0`). Documented boundary (§KH2.6, stated plainly, not
  oversold): does not catch drift re-masked by a *later* uncommitted edit stacked on top of an
  already-missed git commit — closing that fully needs a persisted Git-SHA anchor, deliberately
  deferred as separate scope. Seven-tier KH2 matrix: **27** new tests (**456** total green). Verified
  live on this repo: `overseer status --exit-code` now exits `0` post-catch-up, and would have exited
  `2` at the exact moment the drift first occurred had this gate existed then. ROADMAP: added **KH2a**
  (Thinking, DONE) + **KH2b** (Auto, DONE). Branch `feat/kh2-muse-sync-hard-gate` (kept separate from
  the still-open P-route PR #16 to keep both PRs single-concern). NEXT reverts to the **Track P /
  P-route Auto build** (unchanged from before this detour).
- **2026-07-12** — **Track P / P-route Thinking freeze DONE (reviewed → `pass`).** Drafted and froze
  `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md`: a **declarative model-routing policy** (not a runtime
  dispatcher). Frozen surface — `policy/model-routing.yaml` (`version 1`) mapping the selector triple
  `{position, phase_tier, gate}` → `model_tier` + ordered `fallback`, resolved by first-match-wins
  with a mandatory `defaults` terminal (total resolution); `fallback[0] == model_tier` and every chain
  terminates in `human` (fail-closed, mirrors the freeze-reviewer `fallback: human`); the additive
  `model_tiers` section extending (not forking) `policy/model-labels.yaml` with abstract capability
  tiers (no vendor slugs / endpoints / prices / keys); an optional default-inert `model_routing:`
  config block; a read-only `overseer route` surface (resolve / `--validate` / explain — no model
  call, no network, no dispatch, no key); non-overlapping exit codes `30` (malformed policy) / `31`
  (missing/unreadable policy); the rule-holder-not-executor boundary table; and the §PR.8 seven-tier
  matrix. **Boundary held (K7 / AGENTS.md):** the kit holds and validates the rulebook; the runtime
  (Cursor / OpenRouter / Scooling 9A) maps a tier to a concrete model and executes. `/freeze-review-loop`:
  checklist gate clean both rounds; **P-route-r1** raised two non-escalating MINOR consistency findings
  (R1-N1 exit-`31` wording vs. the `enabled:false` explicit-`route` path; R1-N2 unspecified
  `model_tier`↔`fallback[0]` relationship) → fixed minimally; **P-route-r2 → `pass`**; stamp written by
  `overseer review --freeze` (digest `sha256:ab6b6a9…`). **Spec-only — no code landed.** ROADMAP:
  Track P / P-route → **DONE (Thinking)**; added **Track P / P-route build** (Auto, TODO). Handover NEXT
  flips to the P-route Auto build. **429** tests unchanged.
- **2026-07-12** — **Muse adapter plain-text SHA fix + first muse canonical commit + GitHub bridge (PR #15).**
  Follow-up to the earlier `rev-parse` compat fix: discovered `muse rev-parse` (0.2.x) returns a
  **bare SHA string** on success (exit 0) and JSON only on failure (exit 1); the prior helper tried to
  parse JSON on the success path, causing `governance-sync --dry-run` to emit `invalid JSON in
  rev-parse output` after the first muse commit existed. Fixed `_muse_rev_parse_sha` in
  `adapters/base.py` to read `result.stdout.strip()` directly; updated 6 test mocks (3 e2e + 1 perf
  + 1 security + 1 unit) from JSON-wrapped responses to plain SHA strings.
  `governance-sync --dry-run` now exits 0. First **muse canonical commit** created:
  `sha256:4671b7f...` (316 files, branch `main`, author `aaronrene`, agent `cursor-agent`).
  **GitHub bridge** via `scripts/muse-bridge-deploy.sh`: exported 316 files to git `muse-mirror`
  branch; PR #15 opened (`muse-mirror -> main`). **429** tests still green.
- **2026-07-12** — **Muse adapter compat fix: `muse log --format=%H` → `rev-parse` + JSON.** Muse
  0.2.0rc15 removed the git-style `--format=%H` flag from `muse log`; all four call sites in
  `adapters/muse_only/adapter.py` + `adapters/muse_git_mirror/adapter.py` now use
  `muse rev-parse <ref>` and parse the `commit_id` field from JSON output (same pattern as
  `_muse_dirty`). Added `_muse_rev_parse_sha` helper to `adapters/base.py`. Updated 7 test mocks
  to use the new command. `governance-sync --dry-run` error now reads `muse rev-parse main: not found`
  (accurate: muse substrate has no commits on this dogfood tree) instead of an `--format=%H` syntax
  crash. **429** tests still green.
- **2026-07-12** — **Track P / P1 DONE — build verified → `pass` (P1-BV-r2).** Ran
  `/build-verification-review` (V1–V8) against frozen `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md`.
  V1/V3/V4/V5/V6/V7/V8 clean on first pass; **428** tests confirmed green; §P0.8 seven-tier matrix
  (29 tests) exercises real paths; no social features; no secrets; K7 git-only guardrail intact
  (`config.py:346` forbids `require_agent_signature` under git-only, exit `26`). **Round 1 finding
  BV1** (V2, MAJOR): §P0.6 names `verify` as a surface for exit `2` (malformed provenance), but
  `verify_chain` (`tools/honesty/ledger.py`) validated provenance structure only at append — a
  hash-consistent but structurally malformed `provenance` (unknown key) returned `0` instead of `2`.
  **Fix (feature branch, no commit):** `verify_chain` now runs `validate_provenance` per non-genesis
  entry → exit `2`; `cli/commands/ledger.py` verify path emits "malformed provenance envelope";
  added data-integrity regression `test_verify_flags_malformed_provenance_exit_2`. **Round 2 → `pass`**;
  **429** tests green (+30 §P0.8). ROADMAP P1 → **DONE**; NEXT flips to Track P / P-route Thinking freeze.
- **2026-07-12** — **Track P / P1 Auto build landed (WIP).** Shipped optional `provenance` envelope
  (`agent_id`/`model_id`/Ed25519 `sig`/`pubkey`) on non-genesis ledger entries; extended
  `compute_entry_hash` to exclude `provenance.sig` (v1 chain unbroken); `honesty.require_agent_signature`
  config (git-only `true` → config exit `26`); ledger/honesty-status verify exit `25`/`26`; Muse key
  registry seam; `cryptography` dependency for verify-only path. Seven-tier §P0.8 matrix: **29** new
  tests; **428** total green. ROADMAP P1 → **WIP** pending mandatory `/build-verification-review`.
- **2026-07-12** — **Track Q — Overseer App queued (promoted from exploration backlog).** Added
  **Q0** (Thinking freeze — `overseer app` scope: local-only web UI over the existing Python engine,
  zero engine rewrite, `127.0.0.1`-only, same fail-closed gates as the CLI), **Q1** (Auto — build the
  local web UI), **Q2** (Auto — package Q1 with **Tauri** into an installable cross-platform desktop
  app; native macOS/SwiftUI explicitly deferred) to the ROADMAP build queue. Removed the now-queued
  Track Q entry from the exploration backlog (P-deploy, hosted dashboard, P-route reference remain
  ideas-only). Verified `overseer status` gate scanner parses the new rows cleanly (0 pending gates).
  NEXT unchanged — **Track P / P1** remains the active build; Track Q awaits its own Q0 freeze session.
- **2026-07-12** — **Roadmap slices + exploration backlog added.** Queued **Track P / P-route**
  (declarative model-routing *policy*, not a dispatcher), **P-cost** (cost-*awareness* surface, not a
  dollar pricer), **P-evidence** (verification evidence capture) as TODO (each needs a Thinking freeze
  before build). Added an **Exploration backlog** section: **P-deploy** (deployment gate), **Track Q —
  Overseer App** (local GUI over the Python engine → Tauri desktop; Swift/native deferred; hosted
  read-only dashboard as a separate variant), hosted governance dashboard, and a P-route runtime
  reference (consumer-side). All captured as ideas only; boundary held: kit = governance/frontend,
  never runtime/dispatcher/model-host. NEXT unchanged (Track P / P1 build).
- **2026-07-12** — **Track P / P0 DONE (freeze reviewed → `pass`).** Ran `/freeze-review-loop` on
  `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md`: round 1 checklist gate raised F1 (C8 citation
  discipline) + F2 (C4 path-like token `/api/social/...` in §P0.9) — both non-escalating heuristic
  surfaces, fixed minimally; round 2 checklist clean + semantic review clean → `overseer review
  --freeze` wrote a `pass` stamp (digest `sha256:7db8681…`). ROADMAP P0 → DONE, added P1 (Auto)
  row; handover NEXT → Track P / P1 build.
- **2026-07-12** — **Track P / P0 scope LOCKED + contract drafted.** After reviewing the Muse social
  domain (issue #6) and the Abacus/GPT-5.6 orchestration transcript, held the kit boundary:
  **no social features in the kit.** Track P narrowed to **agent identity & signed provenance** —
  drafted `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md` (optional `provenance` envelope on ledger
  entries; canonical hash excludes `provenance.sig`; `v` stays 1; soft under git-only, hard under
  Muse; shared schema with Muse social). Social confirmed consumer-only (Muse protocol +
  Schooling UI). Pending freeze-review `pass` before P1 Auto build.
- **2026-07-12** — **Session git commit `aa9cf74`.** Synced the git branch with muse-mirrored
  K9b/K10/K11/K12 work (branch was far behind the working tree) and landed this session's KH1b +
  KH1 close-out. `.muse/` added to `.gitignore`; no secrets; 143 files, **399** tests green.
- **2026-07-12** — **KH1 DONE (close-out §KH1.6).** Locked public branding **🆗 Overseer Kit** in
  `templates/OVERSEER-HANDOVER.template.md` + `templates/README.md` token guidance; seeded **Track P / P0**
  row in ROADMAP; flipped handover NEXT → **Track P / P0 (freeze)**. KH1 + KH1b both **DONE**. **399** tests green.
- **2026-07-12** — **KH1b DONE (Auto).** Shipped §KH1.9 gate reminders:
  `tools/governance_gates/` read-only scan; `governance_gates` config schema;
  `overseer status` pending-gates JSON + human section; `governance-sync` dry-run footer;
  handover template Governance gates checklist. Seven-tier KH1b matrix (**19** new tests);
  **399** total green.
- **2026-07-12** — **Substrate health shipped (KH1b §1).** `tools/substrate_health/` probes
  `.muse/HEAD` + `repo.json` + `config.toml` when config is Muse-backed. `overseer status`
  (`--exit-code` → 2), `review --freeze`, and `governance-sync` fail-closed with remediation hint.
  **Postmortem:** K7 marked D2 DONE in docs while this checkout had hollow `.muse/`; tests used
  injected runners (K7.P4–P8), not live tree; K9a logged CLI blocked nine rounds but treated as
  workaround not blocker. ROADMAP now mandates `substrate.ok` before phase DONE.
- **2026-07-12** — **Muse dogfood repair.** Dev tree had hollow `.muse/` (`.museattributes` present but no
  `HEAD`/`repo.json` — K7 D2 never completed on this checkout). Ran `muse init --force` (Tier 1).
  Fixed muse adapters: `status --json` for Muse 0.2+ with `--porcelain` fallback. Dogfood CLI now
  green: `overseer review --freeze` + `status` on default config. §KH1.9 gate reminders
  **operator-approved**; KH1b Auto queued (reminders not automatic yet).
- **2026-07-12** — **KH1-r2 → `pass`.** Freeze-review loop (rounds 1–2) on
  `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md`: R1-M1–M4 + R1-N1 resolved; §KH1.9 governance gate
  reminder spec frozen. CLI checklist `pass` + `review_stamp` via
  `overseer --config tests/fixtures/config-git-only.yaml review --freeze …` (muse+git-mirror dev tree
  still blocked without `muse init`). Handover/contract aligned to K4/K9a ceremony. Next: **KH1 close-out**.
- **2026-07-12** — **KH1 Thinking freeze (draft).** Frozen handover relay standard
  (`docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md`): canonical NEXT SESSION shape, H1–H12 D4
  checklist for `governance-sync`, anchor map, dogfood rules. Aligned `docs/OVERSEER-HANDOVER.md`
  to `templates/OVERSEER-HANDOVER.template.md` (NEXT block, VCS table, hard stops, regeneration
  rules). Close-out deferred per §KH1.6 (branding lock + Track P seed). **380** tests unchanged.
  Next: **KH1 close-out**.
- **2026-07-12** — **K12 DONE (Thinking → Auto).** Shipped Track N public presence:
  `docs/landing/index.html` (§8 sections + GitHub→MuseHub funnel),
  `docs/landing/scenarios/index.html` (personas A–E with dogfood/reference/aspirational badges),
  Apache-2.0 `LICENSE`, `SECURITY.md`, `docs/landing/manifest.yaml`,
  `tools/landing/validate.py`, freeze contract `docs/PHASE-K12-TRACK-N-LANDING-CONTRACT.md`.
  Seven-tier K12 matrix: **19** new tests; **380** total green. No L1/L2/CLI changes. Next: **KH1**.
- **2026-07-12** — **K11 DONE (Auto).** Shipped headless API freeze provider:
  `tools/freeze_reviewer/providers/api_client.py` (`GET /health`, `POST /review`),
  injection-safe delimited artifact payloads, model-hint resolution from
  `policy/model-labels.yaml`, `OVERSEER_REVIEW_API_KEY` + `OVERSEER_REVIEW_API_URL`
  env gate (never in config), API transport/review failures → `provider_unreachable`
  exit `8`, `.github/workflows/freeze-review.yml` + `templates/ci/freeze-review-github-actions.yml`,
  `tools/freeze_reviewer/README.md` API/CI docs. Seven-tier K11 matrix: **21** new tests;
  **361** total green. No L1/L2 changes. Next: **K12 / Track N**.
- **2026-07-12** — **K10 DONE (Auto).** Shipped L2 honesty module:
  `overseer honesty-status`, `overseer ledger {append,verify,show}`, `tools/honesty/` (canonical
  JSON hash chain, genesis bootstrap, role gates, co-requirement hooks, `require_verdict_on`
  allowlist, `roles_file` v1 warn/ignore), neutral fixture pack under `tests/fixtures/honesty/`,
  SPEC §5 command table update. Seven-tier K10 matrix: **38** new tests; **340** total green.
  No L1 orchestrator changes. Next: **K11** API/CI freeze provider.
<!-- /overseer:anchor:change-log -->

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `docs/ROADMAP.md` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Build verification (mandatory):** after `{step}b`, run `/build-verification-review` before ROADMAP status → **DONE**.
5. **Closing commit:** the session-ending commit bundles code/tests + `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md`.

See `docs/ROADMAP.md` → Model-split handover protocol (SD-3) and governance sync (SD-17).
