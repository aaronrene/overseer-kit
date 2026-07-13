# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

## NEXT SESSION — Track P / P-cost Auto build (▶ NEXT)

**Date:** 2026-07-13  
**Current position:** **Track P / P-cost Thinking freeze DONE (reviewed → `pass`, P-cost-r2).** Froze `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` (stamp digest `sha256:9f26678…`): a **cost-*awareness* surface, not a dollar pricer**. Frozen surface — optional, ordinal, currency-free `cost_class` (`free < low < moderate < high`) on each `model_tiers[]` entry; deterministic `paid_step_before_spend` derivation (`free` + reserved `human` unpaid; absent band conservatively paid); additive `cost_class` + `paid_step_before_spend` annotation on read-only `overseer route`; optional default-inert `cost_awareness:` config (`enabled: false`, `surfaces: [status, governance-sync]`); a read-only active-slice spend-awareness surface on `overseer status` (+ `--json`) and the `governance-sync` footer (reuses §KH1.9 active-slice scan; **reminder-only, never blocks**); exit `32` (malformed cost metadata, confined to `overseer route`); seven-tier §PC.9 matrix. **No dollar amount, currency, budget, spend cap, network, or model call in the kit** — the runtime converts a band to money and decides spend. Predecessor **Track P / P-route** (Thinking freeze + Auto build) **DONE**, **529** tests green.  
**Model:** **Auto** (mechanical build against the frozen P-cost contract; run seven tiers; feature-branch commit)  
**Operator choice:** default next slice is the **Track P / P-cost Auto build**. Operator may instead pick **Track P / P-evidence** or **Track Q / Q0** (Overseer App freeze).

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| **Track P / P-cost Thinking freeze DONE** | `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` reviewed → `pass` (P-cost-r2), stamp `sha256:9f26678…`. Freezes optional currency-free `cost_class` on `model_tiers`; `paid_step_before_spend` derivation; additive cost annotation on `overseer route`; optional `cost_awareness:` config; active-slice spend-awareness surface on `overseer status` + `governance-sync` footer (reminder-only); exit `32`; seven-tier matrix. Kit = cost-awareness rule-holder, runtime = spender; **price-agnostic by design.** Spec-only — no code landed. |
| **Track P / P-route Auto build DONE (build-verified)** | `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` built → `/build-verification-review` **`pass` (P-route-BV-r1)**. Vendored `policy/model-routing.yaml`; `model_tiers` in `policy/model-labels.yaml`; optional `model_routing:` config; read-only `overseer route` + exit `30`/`31`; status routing-validity when enabled. **529** tests green (+43 §PR.8). |
| **KH3 Footprint self-integrity hard gate DONE (Thinking + Auto)** | `docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md` reviewed → `pass` (KH3-r2). New `tools/footprint_integrity/` (`FootprintIntegrityReport`/`check_footprint_integrity`, frozen trigger: `version.lock`-declared + non-`preserved` + absent from disk — existence-only, never content-hash); wired fail-closed into `status --exit-code` (always-on, no flag), `review --freeze`, `governance-sync` (exit `2`, no renumbering of the frozen `2 > 6 > 3 > 0` precedence). **486** tests green (+30 §KH3.8). |
| **Self-footprint seed (hygiene, PR #20)** | Seeded the 13 kit-owned files `version.lock` had declared since K4b but were never rendered — real `overseer sync --yes`, zero `--force` (all `missing`, not conflicts). Verified no secrets, no unsubstituted-token bugs. |
| **KH2 Muse-sync hard gate DONE (Thinking + Auto)** | `docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md` reviewed → `pass` (KH2-r2). `StatusResult.muse_dirty`/`git_dirty` (all three adapters); `tools/muse_sync/` (`MuseSyncReport`/`check_muse_sync`, frozen trigger `muse_dirty and not git_dirty`); wired fail-closed into `status --exit-code`, `review --freeze`, `governance-sync` (exit `2`, no renumbering of the frozen `2 > 6 > 3 > 0` precedence). **456** tests green (+27 §KH2.8). |
| **Muse-sync catch-up (hygiene)** | Muse main was 2 git commits behind (`52b7e6e`, `4eb6d26` — the muse-rev-parse fix and the P-route freeze) with no matching `muse commit`. Ran `muse code add -A && muse commit` — catch-up commit `sha256:3e14450f…`. |
| **Track P / P-route Thinking freeze DONE** | `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` reviewed → `pass` (P-route-r2), stamp `sha256:ab6b6a9…`. Frozen: `policy/model-routing.yaml` schema (first-match-wins + mandatory `defaults`; `fallback[0] == model_tier` terminating in `human`); `model_tiers` extension for `policy/model-labels.yaml` (abstract tiers, no vendor slugs); optional `model_routing:` config; read-only `overseer route` + exit `30`/`31`; seven-tier matrix. Kit = rule-holder, runtime = executor; **no model calls in the kit.** |
| **Track P / P1 DONE (build-verified)** | `provenance` envelope + Ed25519 verify + `require_agent_signature` + exit `25`/`26`; **429** tests green (+30 §P0.8) |
<!-- /overseer:anchor:done-recently -->

### THE ONE NEXT STEP — **Model: Auto (Track P / P-cost build)**

Build the **Track P / P-cost** cost-awareness surface mechanically against the frozen
`docs/PHASE-TRACK-P-P-COST-AWARENESS.md` (reviewed → `pass`, P-cost-r2). Do **not** re-derive or
redesign the contract. Hold the boundary: kit declares currency-free cost bands and derives the
paid flag; the runtime converts a band into dollars and decides spend. **No dollar amount, currency,
budget, spend cap, network call, or model call in the kit.**

| | |
| --- | --- |
| **ID** | **Track P / P-cost build** (Auto) |
| **Branch** | `feat/track-p-cost-build` (slug = `track-p-cost-build`) |
| **Read first** | `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` (frozen contract); `docs/ROADMAP.md` (P-cost build row); `policy/model-labels.yaml`; `policy/model-routing.yaml`; `AGENTS.md` boundary |
| **Build** | §PC.3 `cost_class` key on `model_tiers`; §PC.4 `paid_step_before_spend`; §PC.5 `overseer route` annotation; §PC.6 `cost_awareness:` config; §PC.7 active-slice surface + exit `32`; §PC.9 seven-tier tests |
| **Hard stops** | No dollar/currency/budget/spend-cap/network/model-call in the kit; no redesign of the frozen contract or P-route; no Tier-3 merge without authorization |

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — Track P / P-cost Auto build

```
Phase Track P / P-cost build — Auto (overseer-kit).

Model: Auto (mechanical build against a frozen, reviewed spec; run seven tiers; feature-branch commit).

Shared context:
- Project: 🆗 Overseer Kit — repo-agnostic governance vendoring CLI
- Frozen spec (ground truth — do NOT re-derive): docs/PHASE-TRACK-P-P-COST-AWARENESS.md
  (reviewed → pass, P-cost-r2, stamp sha256:9f26678…)
- Read first: that contract; docs/ROADMAP.md (P-cost build row); policy/model-labels.yaml;
  policy/model-routing.yaml; AGENTS.md boundary
- Boundary (K7 / AGENTS.md): the kit declares currency-free cost bands + derives the paid flag;
  the runtime converts a band to dollars and decides spend. NEVER a runtime/dispatcher/model-host/spender.

Task (build exactly to the frozen contract — no redesign):
- §PC.3: optional cost_class key on each model_tiers[] entry (closed vocab free|low|moderate|high;
  recognized key, not rejected as unknown; invalid value/type → exit 32).
- §PC.4: deterministic paid_step_before_spend (free + reserved human unpaid; absent band → unknown, paid).
- §PC.5: additive cost_class + paid_step_before_spend on overseer route output (resolution unchanged).
- §PC.6: optional cost_awareness: config (enabled default false; surfaces default [status, governance-sync]).
- §PC.7: read-only active-slice spend-awareness surface on overseer status (+ --json) and the
  governance-sync footer (reuse §KH1.9 active-slice scan; reminder-only, never blocks); exit 32
  confined to overseer route; status/governance-sync degrade to a warning on malformed cost metadata.
- Add a static "Spend awareness" reminder line to templates/OVERSEER-HANDOVER.template.md.
- §PC.9: all seven test tiers green locally before DONE.

Hard stops:
- No dollar amount, currency symbol, price, budget, spend cap, network call, or model call in the kit.
- No change to P-route resolution / model-routing schema / exit codes 30,31.
- No Tier-3 merge to main without operator authorization.

Governance gates (mandatory — remind only; silence is not pass):
- Build verification: run /build-verification-review before ROADMAP status → DONE (Auto).
- overseer status and overseer governance-sync emit pending gates for the active slice.
- Update docs/ROADMAP.md + docs/OVERSEER-HANDOVER.md together in the closing commit (SD-17).
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
| **Governance gates** | §KH1.9 **live** — `overseer status` + `governance-sync` pending-gate reminders |
| **Muse dev tree** | `overseer status --exit-code` must show `substrate.ok: true`, `muse_sync.ok: true`, **and** `footprint_self_integrity.ok: true` before phase DONE. Hollow substrate → `muse init --force .`; Muse behind Git (`muse_sync: pending`) → `muse code add -A && muse commit -m "…"`; declared-but-absent kit file (`footprint_self_integrity: missing`) → `overseer sync` (all Tier 1) |

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
| **Track P / P-cost** | **Thinking freeze DONE** — `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` reviewed → `pass` (P-cost-r2), stamp `sha256:9f26678…`. Cost-*awareness* surface (not a dollar pricer): optional currency-free `cost_class` (`free<low<moderate<high`) on `model_tiers`; `paid_step_before_spend` derivation; additive cost annotation on `overseer route`; optional `cost_awareness:` config; active-slice spend-awareness surface on `overseer status` + `governance-sync` footer (reminder-only); exit `32`; seven-tier matrix. **Auto build TODO** (gated on `/build-verification-review`). Kit = cost-awareness rule-holder, runtime = spender; price-agnostic by design |
| **Track Q / Q0–Q2** | **TODO** — Overseer App: local web UI over the existing engine (Q1) packaged with **Tauri** into a cross-platform desktop app (Q2); needs Q0 Thinking freeze first; not yet started |
| **Muse dogfood** | **D2 repaired** + substrate health + gate reminders + **muse-sync hard gate (KH2)** + **footprint self-integrity hard gate (KH3)** live; `muse rev-parse` reads plain-text SHA (0.2.x returns bare SHA on success; JSON only on failure/non-zero); `governance-sync --dry-run` exits 0; muse canonical HEAD `sha256:3e14450f…` (catch-up commit; genesis `sha256:4671b7f…`) |
| **KH1b** | **DONE** — substrate §1 + gate reminders §2 |
| **KH2** | **DONE** — Muse-sync hard gate (freeze `pass` KH2-r2 + Auto build); `tools/muse_sync/`; fail-closed on `status --exit-code` / `review --freeze` / `governance-sync` |
| **KH3** | **DONE** — Footprint self-integrity hard gate (freeze `pass` KH3-r2 + Auto build); `tools/footprint_integrity/`; fail-closed on `status --exit-code` / `review --freeze` / `governance-sync` when a declared kit-owned file is absent from disk |
| **Public brand** | **🆗 Overseer Kit** (locked in template + landing) |
| **CLI** | `init` \| `sync` \| `status` \| `review --freeze` \| `governance-sync` \| `verify-step` \| `honesty-status` \| `ledger` \| `route` |
| **Public landing** | `docs/landing/index.html` · scenario gallery `docs/landing/scenarios/index.html` |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-07-13)

| Item | Value |
| --- | --- |
| Branch | `feat/track-p-cost-freeze` (branched from `feat/track-p-route-build` @ `16e3006`) |
| HEAD (pre closing-commit) | uncommitted (P-cost freeze doc + ROADMAP + this handover) |
| Muse HEAD | `sha256:4543518e…` (branch `main`; genesis `sha256:4671b7f…`) |
| GitHub bridge | no bridge PR currently open |
| Dirty | yes (new `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` + ROADMAP + this handover — pending closing commit on `feat/track-p-cost-freeze`) |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
## Change log

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
