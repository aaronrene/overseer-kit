# Overseer Kit — Cross-Repo Governance System Architecture (Frozen Thinking Outline)

Status: **Frozen meta-architecture for the Build phases (K1–K6 + 9A-5). No implementation in
this step. No kit repo created yet. No env changes. No hooks installed. No `main` merges. No
`muse push staging`. No live effect of any kind.**

This document freezes WHAT and HOW for extracting the overseer/governance system out of the three
workspaces (Scooling, Knowtation, MuseHub) into a **single canonical, versioned, standalone
"Overseer Kit"** that any repo injects locally — so the system can be maintained and perfected in
one place, shared with every repo (mine and other developers'), and kept honest with proper
hygiene and human review only where genuinely required. It follows RULE #8 (Orchestrator) and the
single-model handover protocol: this is the contract layer; the kit code, CLI, adapters, and
seven-tier test bodies are the K1–K6 Build phases (Thinking → Auto per the queue).

Frozen inputs it composes with (does **not** fork):

- `docs/CROSS-REPO-COORDINATION.md` — the three-repo role/VCS table, the Standing Decisions (ADR)
  log (SD-1, SD-3, SD-11, SD-14, SD-17), the Decision Authority tiers (Tier 1/2/3), the overseer
  handover protocol, and the model-split protocol. **This kit is the productized form of that doc.**
- `docs/OVERSEER-HANDOVER.md` — the living relay whose shape becomes the kit's handover template.
- `docs/ROADMAP.md` — the phase-control doc whose shape becomes the kit's roadmap template + the
  Phase Model Key.
- `docs/GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md` — the recurring Muse↔Git inversion failure the
  kit's VCS adapter is designed to detect and prevent centrally.
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — the first agent tool the kit ships;
  rebased onto the kit's VCS adapter interface so it is repo-agnostic from day one.
- `knowtation/AGENTS.md`, `scooling/AGENTS.md`, `MUSE_HUB/docs/MUSEHUB-OVERSEER-HANDOVER.md` — the
  three concrete VCS regimes the kit's adapter backends must satisfy.

---

## Simple summary (no jargon)

Right now our "overseer system" is not really one system — it is the same set of good habits
re-typed by hand into three separate projects. Each project keeps its own handover note, its own
roadmap, the same rules about testing, the same rules about who is allowed to merge, and the same
labels for which AI model to use. Because it is copied instead of shared, the copies drift apart,
and we have already paid for that drift four times: four times someone merged on GitHub without
telling the canonical history (Muse), and each time a person had to manually stitch it back
together.

The fix is to put the whole system in **one place of its own** — a small standalone project we
will call the **Overseer Kit** — and then "inject" a thin, version-stamped copy of it into any
project that needs it. When we improve the system, we improve it once in the kit, then run one
command in each project to pull the update. It works whether a project uses our special history
tool (Muse), plain GitHub, or both — so it works for our three projects and for any outside
developer too. The kit also carries the "robot helpers": one that keeps the handover and roadmap
honest at the end of every session, and one that reviews the important "frozen" decisions and only
interrupts a human when it finds something that truly needs a human. Everything a computer can
safely check, the computer checks; humans are asked only for the few things that are risky,
irreversible, or cost real money.

## Technical summary

This freezes the design for a standalone `overseer-kit` repository that is the **single canonical
source** of the governance layer, distributed into consumer repos as a **pinned, vendored
footprint** driven by one small per-repo `.overseer/config.yaml`. The kit ships five layers:
(1) **policy + doc templates** (handover/roadmap skeletons, ADR/Standing-Decisions format, Tier
1/2/3 authority table, model labels, the RULE #0 seven-tier test contract); (2) **Cursor
primitives** (`.cursor/rules/*`, `.cursor/skills/*`, Automation templates); (3) a **VCS adapter
interface** (`read_head`, `read_canonical_anchor`, `realign`, `commit_feature`, `mirror`, plus
`status`) with three fail-closed backends — `muse+git-mirror`, `muse-only`, `git-only`; (4) the
**agent tools** (Governance Hygiene Agent = Phase 9A-5, and the Freeze-Step Reviewer); and (5) a
**language-agnostic vendoring CLI** (`ok init|sync|status|governance-sync|review`; compatibility synonym `overseer`) that
writes `.overseer/version.lock` and warns on drift. The kit is **VCS-agnostic by construction**:
everything that is identical everywhere lives in the kit; the only per-repo variance
(VCS regime, remote names, doc paths, thresholds, SD-log location) lives in `.overseer/config.yaml`.
The kit **dogfoods its own rules** by being dual-hosted (Muse canonical + GitHub mirror) and
governed by its own handover/roadmap. The Freeze-Contract policy (§6) turns SD-3's `Thinking →
Auto` boundary into a machine-checkable rule: any phase output another phase consumes as ground
truth without re-deriving is a **mandatory reviewed freeze**, auto-reviewed by an agent that must
cite file+line, with human escalation only on security/irreversibility/real-money/Tier-3 linkage.

---

## §0 — Scope (this Outline only)

This Thinking step freezes, and only freezes:

1. The distribution decision + rejected alternatives, with rationale (§1).
2. The kit repository layout (§2).
3. The `.overseer/config.yaml` schema — the single per-repo variance point (§3).
4. The VCS adapter interface + the three fail-closed backends (§4).
5. The vendoring CLI contract — commands, footprint, `version.lock`, drift check (§5).
6. The Freeze-Contract review policy + automation routing (§6).
7. Versioning, release, and update semantics (§7).
8. The migration path for the three existing repos (§8).
9. Security / privacy gate checklist (§9).
10. The seven-tier test expectation per Build phase + explicit blockers + Definition of Done (§10).
11. The Build-phase breakdown K1–K6 + governance-sync guidance (§11).

**Not in scope (build-later):** creating the `overseer-kit` repo, writing any kit code, CLI, or
adapter, installing any hook or Automation, running `overseer init` against any repo, any env flip,
any `main` merge, any `muse push staging`. This doc adds **no code** — only a frozen contract the
K-phases implement mechanically.

**Compose, do not redesign (frozen boundary):** the kit is the **productized, DRY form of
`docs/CROSS-REPO-COORDINATION.md`**. It does not invent new governance policy; it extracts the
existing policy (tiers, model labels, seven-tier tests, handover/roadmap shape, SD log) into a
shareable artifact and adds a thin distribution + automation mechanism around it. The Standing
Decisions log remains authored by humans in each repo's coordination doc; the kit ships its
*format and validators*, not its *contents*.

---

## §1 — Distribution decision (frozen) + rejected alternatives

**Decision:** a **standalone `overseer-kit` repository** that is canonical and versioned, injected
into consumer repos as a **pinned vendored footprint** via a **language-agnostic CLI**, with a
`.overseer/version.lock` and a drift check.

| Option | Verdict | Rationale (verifiable) |
| --- | --- | --- |
| **Standalone repo + vendored CLI install + pinned version + `sync` + drift check** | **CHOSEN** | One canonical source to maintain/perfect; one command updates any workspace; works for Muse-only / Muse+Git / Git-only; usable by any teammate; carries its own governance (dogfood). |
| Git submodule | **REJECTED** | MuseHub is **Muse-only, Git/GitHub forbidden** (`CROSS-REPO-COORDINATION.md` VCS table) — a Git submodule cannot mount there at all. Submodules are also hostile to outside collaborators and to Muse's bridge model. |
| npm / pip package **only** (as primary) | **REJECTED as primary** | Language-locks the system; consumer repos span **TypeScript (Scooling)**, **Python (Knowtation, MuseHub plugin)**, and unknown teammate stacks. A registry package may still be an *optional convenience wrapper* for the CLI (§5), but the injected footprint must be language-agnostic vendored files. |
| Folder inside one product repo (e.g. keep it in Scooling) | **REJECTED** | Couples the kit's release lifecycle to one product; cannot be shared cleanly with the other repos or externally; re-creates the "one repo owns everyone's process" coupling we are trying to remove. |
| Status quo — hand-copied per repo | **REJECTED** | This **is** the drift problem: four documented Muse↔Git inversions (`GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md`, 2026-06-24 / 06-26 / 07-09 / 07-10) and three separately-maintained handover docs that must be updated by hand. |

**Why "vendored footprint" and not "runtime dependency":** the governance system must keep working
offline, with no cloud credentials, and must be auditable inside each repo's own history (the
kit's files are visible and diffable in the consumer repo). A pinned vendored copy + `version.lock`
gives reproducibility and an explicit, reviewable update step, which matches the "review-before-
write for durable changes" boundary.

---

## §2 — Kit repository layout (frozen)

```text
overseer-kit/
  README.md                         # what it is, install, update, dogfood note
  VERSION                           # single source of the kit's semver (e.g. 0.1.0)
  CHANGELOG.md                      # human-readable release notes, semver-tagged
  docs/
    OVERSEER-KIT-SPEC.md            # the frozen spec (this doc, promoted to the kit)
    FREEZE-CONTRACT-POLICY.md       # §6 policy, canonical copy
    ADAPTER-CONTRACTS.md            # §4 VCS adapter interface, canonical copy
    ROADMAP.md                      # the kit's OWN roadmap (dogfood)
    OVERSEER-HANDOVER.md            # the kit's OWN handover (dogfood)
  templates/                        # copied verbatim (with token substitution) into consumers
    OVERSEER-HANDOVER.template.md
    ROADMAP.template.md
    STANDING-DECISIONS.template.md  # ADR format only, not contents
    CROSS-REPO-COORDINATION.template.md
  policy/                           # machine-readable policy the tools enforce
    tiers.yaml                      # Tier 1/2/3 authority table
    model-labels.yaml               # Thinking | Auto | Thinking → Auto | Operator + Auto
    test-tiers.yaml                 # the seven RULE #0 tiers + what each proves
    freeze-contract.schema.yaml     # phase output/frozen-input declaration schema
  cursor/                           # portable Cursor primitives
    rules/                          # .cursor/rules/* fragments (governance-sync, no-docs-only-PR, etc.)
    skills/                         # .cursor/skills/* (governance-sync, freeze-review)
    automations/                    # Automation templates (session-end, on-merge)
  adapters/                         # VCS adapter interface + three backends (§4)
    interface.md                    # frozen method contract
    muse_git_mirror/                # backend impl (build-later)
    muse_only/
    git_only/
  tools/                            # the agent tools (build-later)
    governance_hygiene/             # Phase 9A-5
    freeze_reviewer/                # §6 reviewer
  cli/                              # the vendoring CLI (build-later)
    overseer                        # entrypoint (POSIX shell shim → portable runtime)
  test/                             # seven-tier tests for kit code (RULE #0)
  .overseer/                        # the kit's OWN config (dogfood: git-only or muse+git)
    config.yaml
    version.lock
```

Rationale for the split: `templates/` + `policy/` + `cursor/` are what get **vendored** into
consumers (small, language-agnostic, diffable). `adapters/` + `tools/` + `cli/` are the **engine**
that the CLI runs; they are versioned in the kit and referenced by the pinned footprint, not
duplicated wholesale into every consumer.

---

## §3 — `.overseer/config.yaml` — the single per-repo variance point (frozen)

Everything shared is in the kit; the **only** thing each repo customizes is this file. Frozen
schema (values shown are illustrative, not defaults to assume):

```yaml
overseer_config_version: 1          # schema version, integer; fail closed if unknown

repo:
  name: scooling                    # human label used in handover/roadmap tokens
  root_relative_docs: docs          # where the living docs live in this repo

vcs:
  regime: muse+git-mirror           # one of: muse+git-mirror | muse-only | git-only
  canonical: muse                   # muse | git — which history is source of truth
  git:
    remote: origin                  # only when regime includes git
    main_branch: main
    mirror_branch: muse-mirror      # the permanent mirror branch (SD-14)
    feature_branch_pattern: "feat/{slug}"
  muse:
    staging_remote: staging         # only when regime includes muse; null for git-only
    main_branch: main

docs:
  handover: OVERSEER-HANDOVER.md
  roadmap: ROADMAP.md
  coordination: CROSS-REPO-COORDINATION.md   # null if the repo has none
  standing_decisions: CROSS-REPO-COORDINATION.md   # where the SD/ADR log lives

thresholds:
  realign_max_commits: 50           # muse realignment dry-run guard (§4, 9A-5 spec)
  drift_warn_only: true             # drift check warns; never blocks or writes

freeze_contract:
  enabled: true
  reviewer: agent                   # agent | human — default agent (auto-first)
  human_escalation:                 # conditions that force human review (§6)
    - security
    - irreversible
    - real_money
    - gates_tier3
```

**Fail-closed rule (frozen):** if `.overseer/config.yaml` is missing, unparseable, has an unknown
`overseer_config_version`, or names a `vcs.regime` the installed kit does not implement, every kit
tool **stops and reports** — it never guesses a regime, never writes, never realigns.

**No secrets in config (frozen):** `.overseer/config.yaml` holds names and booleans only — no
tokens, no URLs with credentials, no absolute machine paths, no hostnames beyond a remote *name*.
It is safe to commit. The kit's `.museignore`/`.gitignore` templates keep `version.lock` committed
but exclude any local scratch the tools produce.

---

## §4 — VCS adapter interface (frozen) + three fail-closed backends

The recurring inversion failure lives at the VCS boundary, so the kit isolates it behind **one
interface** implemented by **three backends**. Every method is **read-fail-closed**: any underlying
command failure returns a typed error that halts the caller; no method guesses state.

Frozen method contract (language-neutral; concrete signatures are K2 Build work):

| Method | Input | Output (typed) | Fail-closed behavior |
| --- | --- | --- | --- |
| `status()` | none | `{ regime, dirty: bool, branch, notes[] }` | If the VCS status command errors → `ReadError{command}`; caller stops. |
| `read_head()` | `{ ref }` (e.g. `origin/main`) | `{ sha, kind }` | Missing ref / command error → `ReadError`; never returns a fabricated sha. |
| `read_canonical_anchor()` | none | `{ anchor_sha, source }` | For `muse+git`: the Muse↔Git bridge anchor. For `muse-only`: `muse log main` tip. For `git-only`: `origin/main` tip. Command error → `ReadError`. |
| `realign()` | `{ dry_run, max_commits }` | `{ would_import: n, applied: bool, from_ref, to_ref }` | Only defined for regimes with a canonical/mirror split. Dry-run first; if `n > max_commits` → refuse + report. `git-only` = **no-op** (returns `applied:false, reason:"single-history"`). |
| `commit_feature()` | `{ branch, message, paths[] }` | `{ committed: bool, sha }` | Tier 1 only. Refuses if `branch` resolves to a `main`/canonical-main; never commits to protected refs. |
| `mirror()` | `{ dry_run }` | `{ diff_summary, pushed: bool }` | Tier 3-linked; in the kit's runtime it **stops for operator authorization** before any push; `dry_run` reports the mirror delta only. |

**Backend behaviors (frozen):**

- **`muse+git-mirror`** (Scooling, Knowtation): canonical = Muse; `read_canonical_anchor` reads the
  bridge anchor; `realign` wraps the `muse bridge git-import --incremental --preserve-merge-commits`
  recovery from `GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md`, guarded by dry-run + `realign_max_commits`;
  `mirror` follows SD-14 (`muse-mirror → main`, never `git push origin main`). **Never** merges a
  feature branch directly to GitHub `main`.
- **`muse-only`** (MuseHub): `git`/`mirror` methods are hard **no-ops that report "git forbidden in
  this regime"**; `read_head`/`read_canonical_anchor` use `muse log`; `realign` is a no-op
  (single canonical history). Honors "never run git/gh in MuseHub."
- **`git-only`** (external developers, no Muse): canonical = Git `origin/main`; `read_canonical_anchor`
  = `origin/main` tip; `realign` = no-op (single history); `mirror` = no-op. Governance-sync, drift
  check, freeze review, handover/roadmap upkeep all still work — this is what makes the kit usable
  by any teammate with a plain GitHub repo.

**Cross-repo cwd safety (frozen, from `CROSS-REPO-COORDINATION.md` 2026-06-20 note):** every Muse
invocation the backends make MUST use an explicit `muse -C <absolute-repo-root>` (or a genuine
`cd`) and confirm branch + HEAD before any `add`/`commit`/`checkout`, so an agent's cwd cannot leak
one repo's state into another.

---

## §5 — Vendoring CLI contract (frozen)

One entrypoint, **`ok`** (compatibility synonym **`overseer`**), runnable with **no global install** (POSIX shell shims `cli/ok` and `cli/overseer` in the kit engine tree that locate the portable runtime; `cli/overseer` prints a one-line stderr deprecation per process and runs the same runtime as `cli/ok`; an optional published package is a convenience wrapper only, never the sole path). All commands are **read-first and idempotent**; running any command twice with no external change produces the same result.

| Command | Purpose | Writes? | Idempotent |
| --- | --- | --- | --- |
| `ok init` | First install into a repo: create `.overseer/config.yaml` (interactive/regime-detected), vendor the footprint, write `version.lock`. Refuses to overwrite an existing config without `--force`. | Yes (footprint + config) | Yes (re-run = no-op if lock matches) |
| `ok sync` | Update the vendored footprint to the kit version the CLI carries; rewrite `version.lock`; show a diff of changed template/policy/cursor files. | Yes (footprint) | Yes |
| `ok status` | Report: kit version, `version.lock` version, drift (behind/ahead), VCS regime, dirty tree, last governance-sync. Read-only. | No | Yes |
| `ok governance-sync` | Run the Governance Hygiene Agent (Phase 9A-5) against this repo's `.overseer/config.yaml`: detect drift between docs and true VCS state, patch handover/roadmap, guard-realign, commit to a feature branch. `--dry-run` = report only. | Yes (docs, feature branch) | Yes |
| `ok review --freeze <path>` | Run the Freeze-Step Reviewer (§6) on a freeze artifact; emit findings with **file+line citations**; set exit status by verdict; escalate to human per config. `--dry-run` prints the review only. | No (review output only) | Yes |
| `ok verify-step [--manifest PATH] [--step ID \| --through current \| --all] [--policy PATH] [--dry-run] [--json]` | L1 checkpoint orchestrator (K9b): run domain verify scripts in template order; update active manifest per step; optional `--dry-run` plan-only. Module gate: `checkpoints.enabled` must be true. Exit extensions: `10` verify fail, `11` step order. | Yes (manifest + optional progress) | Yes (re-verify overwrites) |
| `ok honesty-status --hook HOOK --artifact PATH [--producer-session ID] [--json]` | L2 co-requirement check (K10): require a passing independent `verdict` for artifact SHA before board/handoff/register hooks. Module gate: `honesty.enabled` must be true. Exit extensions: `20` missing verdict, `4` hook not enabled / module off. | No | Yes |
| `ok ledger append --kind KIND [--file JSON_PATH \| --stdin]` | L2 verdict ledger append (K10): hash-chained JSONL entry with role gates. Auto-genesis on first append. Exit extensions: `21`–`24`, `22` on verify. | Yes (ledger) | Append-only |
| `ok ledger verify` | L2 ledger chain verification (K10). Missing/empty ledger → `0`. Break → `22`. | No | Yes |
| `ok ledger show [--last N]` | L2 ledger read (K10): print last N JSONL records. Missing/empty → `0` with no lines. Default N=20. | No | Yes |
| `ok upgrade-regime --from muse-only --to muse+git-mirror [--dry-run \| --apply] [--live-bridge] [--force] [-y]` | Stage 3 kit ceremony (Track O / O3): ordered `muse-only` → `muse+git-mirror` upgrade composing `init`/`sync`/`status` + K7 bridge gates (C0–C5 / G1–G8). `--dry-run` default when `--apply` absent. `--live-bridge` requires gate success + `-y` (C6); never performs C8 merge. Frozen detail: `docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`. | Yes (config + footprint when `--apply`; optional C7 via deploy script) | Yes (complete upgrade → exit 0) |
| `ok hosted-dashboard [--port PORT] [--bind ADDRESS] [--config PATH] [--open]` | Read-only remote governance dashboard preview (Hosted governance dashboard): GitHub/MuseHub **read** glance of ROADMAP/HANDOVER/gates; Bearer viewer auth; default `127.0.0.1:8766`. Never mutates git/muse/GitHub. Operator runbook: `docs/HOSTED-GOVERNANCE-DASHBOARD-OPERATOR-RUNBOOK.md`. Frozen: `docs/PHASE-HOSTED-GOVERNANCE-DASHBOARD.md`. | No | Yes |

**Vendored footprint (frozen — what `init`/`sync` copy into a consumer):** the contents of
`templates/` (token-substituted with `.overseer/config.yaml` values), `policy/`, and `cursor/`,
plus a thin pointer to the kit engine version. The **engine** (`adapters/`, `tools/`, `cli/`) is
carried by the CLI itself and pinned by `version.lock` — it is not copied file-by-file into every
repo, keeping the footprint small and diffable.

**`version.lock` (frozen shape):**

```yaml
kit_version: 0.1.0                  # matches overseer-kit/VERSION at install/sync time
installed_at: "<iso-8601>"          # timestamp only, no user identity
footprint_digest: "sha256:<hex>"    # digest of the vendored files, for drift detection
config_version: 1
```

**Drift check (frozen):** `ok status` compares the local `footprint_digest` + `kit_version`
against the kit the CLI carries. If behind, it **warns** with the version delta and the changed
files; per `thresholds.drift_warn_only` it **never** auto-updates or blocks. Updating is always the
explicit `ok sync` step (review-before-write).

**K4a refinement (frozen detail):** the per-command argument contract, exit-code taxonomy, the
extended (spec-compatible, additive) `version.lock` shape with a per-file manifest, and the
deterministic `footprint_digest` algorithm are frozen in `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md`.
K4b builds against that document.

---

## §6 — Freeze-Contract review policy (frozen)

This formalizes the operator's closing requirement: **anything that is a frozen spec, or that a
later step depends on as ground truth, must be reviewed** — and the review should be **as automated
as possible**, interrupting a human only when genuinely necessary.

### §6.1 — Declarations (the machine-checkable part)

Each phase in a roadmap declares, in a small structured block (schema =
`policy/freeze-contract.schema.yaml`):

```yaml
phase: 9A-5
outputs:                            # artifacts this phase produces
  - id: hygiene-agent-spec
    path: docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
    frozen: true                    # declared frozen = downstream may treat as ground truth
frozen_inputs:                      # artifacts this phase consumes without re-deriving
  - id: kit-adapter-interface
    path: docs/OVERSEER-KIT-ARCHITECTURE-OUTLINE.md#4
```

**The rule (frozen):** an edge exists from phase A to phase B when B lists one of A's `outputs` in
its `frozen_inputs`. If that output is `frozen: true` **and B treats it as ground truth without
re-deriving it**, the edge is a **mandatory reviewed freeze**. This is exactly the SD-3
`Thinking → Auto` boundary (a Thinking phase freezes a contract; an Auto phase builds against it
without re-deriving it) made explicit and machine-detectable.

**Cheap heuristic the reviewer applies (operator's own test):** *"does a later phase treat this
output as ground truth without re-deriving it?"* If yes → review it. Pure mechanical Auto builds
against an already-frozen, already-reviewed spec are **not** re-reviewed (lower value, per the
operator's recommendation).

### §6.2 — Automated review (default path)

- The **Freeze-Step Reviewer** runs (via `overseer review --freeze <path>`, or the K5 Automation on
  freeze commits) on every artifact declared `frozen: true`.
- It **must cite file + line for every finding**, so the parent/operator can verify rather than
  trust — this is the safeguard that lets a real finding be distinguished from a reviewer
  hallucination (the operator's explicit requirement).
- Verdict is one of `pass` / `findings` / `blocked`. `findings` returns the cited list; `pass`
  records a review stamp in the artifact's freeze block; `blocked` triggers §6.3.

**K5 design requirement (frozen):** the reviewer is **user-configurable per repo** — local model,
remote API, or human — via an extended `freeze_contract` block in `.overseer/config.yaml`. The K5a
Thinking phase **must** freeze this config schema before K5b builds the reviewer. Required fields:

```yaml
freeze_contract:
  reviewer:
    mode: agent            # agent | human
    model: thinking-high   # label from policy/model-labels.yaml — never a hardcoded vendor slug
    provider: local        # local | api  — portability and privacy/cost choice
    fallback: human        # what to do if the model/provider is unreachable → fail-closed to human
  human_escalation: [security, irreversible, real_money, gates_tier3]
```

**Guardrails (frozen):** (1) fail-closed — if `provider` is unreachable, fall back to `human` rather
than skipping review; (2) model is a **label**, never a vendor slug, so the config is portable across
providers; (3) `provider: local` is a **first-class** option — the kit must work fully offline with no
API key required; (4) no core review capability may be `api`-only. These are non-negotiable: they
preserve the kit's offline/repo-agnostic promise.

**K5a refinement (frozen detail):** the `overseer review --freeze` argument contract, review-specific
exit codes (`7` findings / `8` blocked-or-human), extended `freeze_contract.reviewer` schema with
legacy-string normalization, finding/verdict/stamp/escalation rules, provider reachability + human
packet, Automation degrade path, and the K5b seven-tier test matrix are frozen in
`docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md`. K5b builds against that document.

### §6.3 — Human escalation (only when necessary)

The reviewer escalates to a human **only** when a finding (or the artifact's declared linkage) hits
one of the `human_escalation` conditions in `.overseer/config.yaml`:

- **security** — auth, scope, secrets, injection surface, redaction.
- **irreversible** — data deletion, migrations, anything not cheaply revertible.
- **real_money** — billing/live model spend (composes with SD-16).
- **gates_tier3** — the frozen artifact gates a Tier 3 action (merge to `main`, `muse push
  staging`, live-capability flip, cross-repo merge).

Everything else the agent reviewer resolves or reports without a human stop. This keeps human
review **rare and meaningful** and satisfies "as automated as possible."

### §6.4 — How it layers on Tier 1/2/3 (additive, not a rewrite)

The Freeze-Contract sits **on top of** the existing Decision Authority tiers:

- Tier 1 (feature-branch commits, tests, formatting) is unchanged — no freeze review needed.
- Tier 2 (recommend-and-confirm) is unchanged.
- Tier 3 (main merges, staging push, live flips) is unchanged as the human hard-gate — the
  Freeze-Contract simply **guarantees** a reviewed freeze exists *before* a Tier-3 action consumes
  it, and routes the automated-vs-human decision.

---

## §7 — Versioning, release, and update semantics (frozen)

- **Semver** in `overseer-kit/VERSION` + `CHANGELOG.md`. MAJOR = breaking template/policy/adapter
  contract change; MINOR = additive policy/template/tool; PATCH = fixes.
- **Consumers pin** via `version.lock`. `overseer status` reports drift; `overseer sync` performs
  the explicit, reviewed update and rewrites the lock.
- **Config compatibility:** `overseer_config_version` is independent of kit semver; a kit that does
  not understand a config version **fails closed** (§3).
- **The kit governs itself** (dogfood): the kit repo carries its own `docs/ROADMAP.md` +
  `docs/OVERSEER-HANDOVER.md` and is developed under the same phase/commit/freeze discipline it
  ships. Its own release is a phase with the same Definition of Done (§10).

---

## §8 — Migration path for the three existing repos (frozen order)

Canonical-first, one repo at a time, non-destructive (the kit is added *alongside* existing docs;
nothing is deleted until parity is proven):

1. **Scooling first** (richest policy source, `muse+git-mirror`): `overseer init` with regime
   `muse+git-mirror`; vendor templates; map existing `docs/OVERSEER-HANDOVER.md` + `docs/ROADMAP.md`
   as the living docs in `.overseer/config.yaml`; confirm `governance-sync --dry-run` reproduces
   the current hand-maintained state before enabling writes. Standing Decisions log stays in
   `CROSS-REPO-COORDINATION.md` (kit ships format only).
2. **Knowtation** (`muse+git-mirror`, plus the `no-docs-only-PR-to-main` rule): `overseer init`;
   confirm the kit's rule fragment matches the existing
   `.cursor/rules/no-docs-only-pr-to-main.mdc` before replacing it with the vendored version.
3. **MuseHub** (`muse-only`): `overseer init` with regime `muse-only`; verify all `git`/`mirror`
   methods report "git forbidden" and do nothing; map `MUSEHUB-OVERSEER-HANDOVER.md` +
   `MUSEHUB-ROADMAP.md`.
4. **Parity gate:** for each repo, the kit-driven `governance-sync --dry-run` output must match the
   repo's current hand-maintained handover/roadmap **before** any hand process is retired. Only
   after parity is proven (and per each repo's VCS rules) does the repo switch to kit-driven upkeep.
5. **External developer template:** publish a `git-only` quickstart so any teammate can
   `overseer init` a plain GitHub repo and get the same discipline.

No migration step merges to `main`, pushes staging, or flips a gate; each is Tier-1 feature-branch
work in its own repo under that repo's VCS rules.

---

## §9 — Security / privacy gate checklist (frozen)

- **No secrets anywhere in the kit or footprint** — config is names/booleans only; tools never log
  tokens, URLs-with-credentials, or absolute machine paths; reviewer output and `version.lock`
  carry no identity beyond a timestamp.
- **No hardcoded SHAs** in any kit script or template — all shas are read at runtime via the
  adapter and never committed into automation logic.
- **Fail closed on every read** — any `status`/`read_head`/`read_canonical_anchor` failure halts
  the caller with the exact failing command; no tool ever writes partial state or guesses.
- **Least privilege** — `muse-only` backend cannot invoke git; `git-only` cannot invoke muse; a
  regime never gains a capability it did not declare.
- **Injection surface** — templates use explicit token substitution from a fixed key set (repo
  name, doc paths); no arbitrary shell interpolation of doc content; reviewer treats artifact text
  as data, not as instructions.
- **Review-before-write** — every durable change (sync, governance-sync writes, migration) is an
  explicit reviewable step; drift only warns.
- **Human hard-gates preserved** — Tier 3 (main merge, staging push, live flip, payments, secrets)
  is never automated by the kit.

---

## §10 — Seven-tier test expectation (per Build phase) + blockers + Definition of Done

Per RULE #0, every Build phase that adds code ships all seven tiers. The matrix each K-phase must
satisfy (bodies are Build work):

| Tier | What it proves for the kit |
| --- | --- |
| **unit** | Each adapter method, config parse, template token-substitution, and CLI arg-parse behaves per contract, including every fail-closed branch. |
| **integration** | CLI + adapter + config compose: `init`/`sync`/`status`/`governance-sync`/`review` against a fixture repo per regime. |
| **e2e** | A full session-end governance-sync on a fixture repo produces a correct handover/roadmap patch on a feature branch (no `main`, no push). |
| **stress** | Large roadmaps/handovers, many phases, `realign` at the `realign_max_commits` boundary, many freeze edges. |
| **data-integrity** | Idempotency (run-twice = same result); `version.lock` digest correctness; no partial writes on induced mid-operation failure. |
| **performance** | `status`/drift check and a governance-sync complete within a bounded time on a realistic repo; no unbounded VCS scans. |
| **security** | No secret/identity leakage in outputs/logs; injection-safe templating; regime least-privilege enforced; fail-closed on every simulated read failure. |

**Inert double / dry-run (frozen):** the safe default for both agent tools is a **dry-run mode that
reports what it would do and writes nothing** (`governance-sync --dry-run`, `review --dry-run`).
This is the kit's equivalent of the "posture hard-`false`" inert-first pattern.

**Blockers (explicit):**

| Blocker | State | Consequence |
| --- | --- | --- |
| `overseer-kit` repo does not exist yet | OPEN (K1) | Nothing installs until K1 bootstraps it. |
| Muse bridge behavior for `realign` must be re-verified per Muse version | OPEN (K2) | `muse+git-mirror` backend gated on a verified `git-import --incremental` dry-run. |
| Cursor Automation availability differs per environment (Agents Window) | OPEN (K5) | Automation triggers degrade gracefully to the `/overseer` CLI + slash command when the editor handoff is unavailable. |

**Definition of Done (every K-phase):** deliverables match this frozen spec; required test tiers
green locally; no secrets/hardcoded SHAs; fail-closed verified; both governance docs (kit's own
ROADMAP + OVERSEER-HANDOVER) updated; feature branch → commit → (push/PR per the kit repo's own VCS
rules). No phase is DONE until its tests pass.

---

## §11 — Build-phase breakdown (queued; not this session) + governance sync

| Phase | Scope | Model |
| --- | --- | --- |
| **K1 Bootstrap** | Create `overseer-kit` repo skeleton (§2), `VERSION`/`CHANGELOG`, dual-host + self-governance docs, README. | **Thinking → Auto** |
| **K2 Config + adapters** | `.overseer/config.yaml` schema (§3) + the VCS adapter interface (§4) + three fail-closed backends + their unit/integration/security tests. | **Thinking → Auto** |
| **K3 Extract shared assets** | Move the existing handover/roadmap/SD-format/tier/model-label/test-tier policy out of the three repos into `templates/` + `policy/` + `cursor/`, token-parameterized. | **Auto** |
| **K4 Vendoring CLI** | `overseer init|sync|status` + `version.lock` + drift check (§5) + seven-tier tests. Contract frozen in `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` (K4a); K4b builds against it. | **Thinking → Auto** |
| **K5 Freeze reviewer + automation routing** | The §6 reviewer (file+line citations, verdicts, escalation) + `overseer review` + session-end/on-merge Automation templates + tests. Contract frozen in `docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md` (K5a); K5b builds against it. | **Thinking → Auto** |
| **9A-5 Governance Hygiene Agent** | The first shipped tool, built against its own frozen spec (`PHASE-9A-5-…-OUTLINE.md`), rebased onto the K2 adapter interface. | **Auto** |
| **K6 Pilot install + migration** | `overseer init` into Scooling → Knowtation → MuseHub per §8; parity gate; external `git-only` quickstart. | **Thinking → Auto** |

**Governance sync (mandatory on each phase completion):** update the owning repo's `ROADMAP.md`
status row + `OVERSEER-HANDOVER.md` NEXT SESSION together in the closing commit (SD-17); for
`Thinking → Auto` phases emit `{K}a`/`{K}b` split prompts per SD-3. A phase that ends without both
governance docs updated is INCOMPLETE.

---

## Cross-references

- `docs/CROSS-REPO-COORDINATION.md` — the policy source this kit productizes (tiers, SD log,
  handover protocol, model-split protocol). **A pointer to this outline should be added there** as
  part of the roadmap/handover update in this same session.
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — the first tool, specified against the §4
  adapter interface.
- `docs/GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md` — the failure pattern §4's backends prevent.
- `docs/ROADMAP.md` — Phase 9A-5 + the Overseer Kit (K1–K6) track added to the queue.
