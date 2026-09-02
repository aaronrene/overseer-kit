# Phase LT — Loop tightening (slices 1–4)

Status: **Reviewed → `pass` (LT-r2).** LT-a is **spec-only** and now frozen; no code
lands in this phase. LT-b (Auto) is cleared to build mechanically against this contract.

```yaml
phase: LT
outputs:
- id: lt-loop-tightening
  path: docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md
  frozen: true
frozen_inputs:
- id: kit-spec
  path: docs/OVERSEER-KIT-SPEC.md
- id: ons-operator-next
  path: docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md
- id: kh1-relay
  path: docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: kh3-footprint
  path: docs/archive/phases/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md
- id: gfg-freshness
  path: docs/archive/phases/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md
- id: p-evidence
  path: docs/archive/phases/PHASE-TRACK-P-P-EVIDENCE.md
- id: k9a-honesty
  path: docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md
- id: gs-paste
  path: docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md
- id: check-ok
  path: docs/archive/phases/PHASE-CHECK-OK.md
- id: footprint-resolver
  path: cli/footprint.py
- id: status-exit
  path: cli/commands/status.py
- id: honesty-config
  path: adapters/config.py
- id: handover-template
  path: templates/OVERSEER-HANDOVER.template.md
- id: print-next-stop
  path: cursor/hooks/print-next-stop.json
- id: test-tiers
  path: policy/test-tiers.yaml
- id: model-labels
  path: policy/model-labels.yaml
review_stamp:
  reviewed_at: '2026-09-02T01:08:57Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:6a5aafb531d06ba2ee29a22185146826acba14b05596212d5bb2864ad3f99aab
```

**Downstream edge:** LT-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze).

**Review record (§6.2):** every freeze-review finding MUST cite **file+line**. Uncited
findings are invalid and are discarded. Fixes are Tier 1 on the feature branch.
Merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| LT-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI dry-run `pass` (0 checklist findings). Semantic **R1-M1–M4** (test prefix fork; executable-bit frozenset unnamed; dated-entry block boundary; `ok sync` flag weasel). Fixed in-tree. |
| LT-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | R1-M1–M4 resolved. Non-goals hold. Stamp written by `ok review --freeze`. |

### Freeze-review findings ledger (LT-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | completeness | `:500` (pre-fix) | Seven-tier prefix allowed `test_lt_*` **or** `test_loop_tightening_*` — Auto cannot choose. Frozen to `test_lt_` only. |
| R1-M2 | MAJOR | completeness | `:252` (pre-fix) | Hook scripts “same executable bit as muse-bridge-deploy” did not name adding dests to `EXECUTABLE_FOOTPRINT_DESTINATIONS`. Named both `.cursor/hooks/*.sh` dests. |
| R1-M3 | MAJOR | completeness | `:418-421` (pre-fix) | “contiguous block” dated entries had no end boundary. Frozen: start on dated regex; continue until next dated line or end of region. |
| R1-M4 | MAJOR | consistency | `:183` (pre-fix) | “`ok sync -y` or the existing non-interactive apply flag” — weasel. Frozen `ok sync --yes` (`-y` synonym). |

**Citation discipline:** every review finding in this artifact **must** include
`path:line` so the operator can verify — never trust uncited review output
(§6.2 / K5).

---

## §LT.0 — Simple summary

The kit already has a loop: freeze a spec, build it, prove it, update the two
living docs, print the next step from disk. Four everyday holes make that loop
weaker than it looks:

1. This repo (and any repo that skips `ok sync`) can be missing the newest
   rules even though the kit source has them. Cursor may also be pointed at a
   *parent* folder, so rules inside the repo never load.
2. Session start/end bookends exist only as unused recipes.
3. “DONE” can be a typed word. The honesty ledger and evidence flag exist but
   are off here.
4. The living handover is a long diary. People keep the tab open and think
   nothing changed.

This phase freezes the four slices that close those holes **without** pretending
the editor tab will refresh, **without** making Cursor the only way to use the
kit, and **without** turning honesty on for every consumer.

**Technical summary:** (1) a fail-closed **footprint coverage** gate so a lock
that does not list current kit files cannot look green, plus dogfood `ok sync`
and “open the folder that contains `.overseer/`” docs; (2) optional
`session_bookends` config (default **off**) that, when on, vendors Cursor
`sessionStart` / `sessionEnd` / `stop` hooks — CLI `ok next` stays primary;
(3) kit-dogfood honesty `enabled: true` + `require_verification_evidence: warn`
with an **active-slice only** Mode B surface on `ok status` / governance-sync
(no historical DONE retro-fail); (4) `ok handover-compact` that archives old
change-log bullets and leaves NEXT / snapshot alone.

---

## §LT.1 — Verified problem (do not redesign)

| Fact | Evidence |
| --- | --- |
| Live dogfood `.cursor/` is a July-13 lock; source `cursor/` has newer always-on rules (`orchestrator.mdc`, `print-next-closeout.mdc`, `check-ok-thinking.mdc`, print-next / check-ok skills) | `.overseer/version.lock` `synced_at: 2026-07-13`; `cursor/rules/` vs `.cursor/rules/` |
| KH3 only fails on **declared-but-absent** files, not “kit grew files the lock never declared” | `docs/archive/phases/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md` existence-only trigger |
| `ok status` digest compares lock records to those same records — new unresolved files do not change `footprint_digest` | `cli/commands/status.py`; `cli/digest.py` |
| Kit cannot force an IDE tab to reload | ONS §ONS.1 / §ONS.2; no tab API in this repo |
| ONS hooks/Automations are templates, not footprint, not auto-enabled | `cursor/hooks/README.md`; ONS §ONS.9 |
| Cursor now has `sessionStart` / `sessionEnd` hook events | Cursor hooks skill (host); not used by the kit today |
| Honesty module defaults **off**; `require_verification_evidence` defaults **off** | `adapters/config.py` `HonestyConfig`; kit `.overseer/config.yaml` has no `honesty:` block |
| `honesty.enabled: true` requires a non-empty `honesty.ledger` | `adapters/config.py` `_parse_honesty` |
| Mode B (`ok honesty-status --verification-evidence`) already implements off/warn/require | `tools/honesty/status.py` `_run_mode_b`; P-evidence §PE.6 |
| KH1.9 already scans an **active slice** | `tools/governance_gates/scan.py` |
| Change log lives in `<!-- overseer:anchor:change-log -->` | `docs/OVERSEER-HANDOVER.md`; KH1 |
| GS-PASTE is the sole NEXT **regen** surface | `docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md` |
| Parent folder `OVERSEER_KIT/` is not the git repo; `.cursor/` lives under `overseer-kit/` | workspace vs `overseer-kit/.git` |

---

## §LT.2 — Scope

**In scope (LT-a freezes; LT-b implements):**

1. Slice 1 — footprint coverage + dogfood sync + workspace-root docs (§LT.3).
2. Slice 2 — session bookends, Cursor hooks when enabled, CLI remains primary (§LT.4).
3. Slice 3 — kit-dogfood honesty warn + active-slice Mode B surface (§LT.5).
4. Slice 4 — handover compact command + one dogfood compact (§LT.6).
5. Narrow ONS supersession for hooks-in-footprint **only when** `session_bookends.enabled` (§LT.4.4).
6. Additive SPEC §5 rows, seven-tier matrix (§LT.10), Definition of Done (§LT.11).

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected now |
| --- | --- |
| **Claim the kit can close/reopen or reload an editor tab** | No supported host command; CLI open often focuses the stale tab. Backlog: Host tab reload. |
| **Independent second reviewer / required second chat** | More honest; high friction. Backlog: Independent second reviewer. |
| **Session-type bookends (pick / build / land)** | Fuller hole-6 fix. Backlog: Session-type bookends. Slice 2 only injects disk NEXT. |
| **KH2 remask (later dirty edit hides Muse drift)** | Separate hard VCS problem. Backlog: KH2 remask. |
| **Default-on honesty for every consumer** | Blast radius. Kit dogfood only. |
| **`require_verification_evidence: require` in Auto v1** | Dogfood starts at **warn**. Promote later. |
| **Auto-enable hooks for every consumer on `ok sync`** | Default `session_bookends.enabled: false`. Backlog: Auto-enable session hooks. |
| **Force-enable Cursor Automations UI** | Host click; we cannot. Hooks files are the auto-on we *can* do when the flag is true. |
| **Regenerate NEXT via compact or `ok next`** | GS-PASTE sole regen. |
| **Per-branch handover names** | ONS A1. |
| **Widen KH3 to content-hash mismatch** | Already rejected (consumer false-close). Coverage is a *different* trigger. |
| **Write files outside the git repo** (parent `OVERSEER_KIT/.cursor`) | Not portable; not in this repo. |
| **Make Cursor required** | CLI + docs remain complete. |
| **Police every Task/subagent mid-flight** | End-of-session bookend only. |
| **LT-b Auto implementation in this Thinking phase** | SD-3 split. |

---

## §LT.3 — Slice 1. Footprint coverage + dogfood sync + workspace-root

### §LT.3.1 — Footprint coverage gate (closes the “lock never heard of new files” twin of KH3)

Add `tools/footprint_coverage/` (`FootprintCoverageReport` / `check_footprint_coverage`).

**Inputs:** `version.lock` + `resolve_footprint(config)` (same resolver `ok sync` uses).

**States (closed set):**

| `state` | When | `ok` |
| --- | --- | --- |
| `not_applicable` | Lock missing, unreadable, or `footprint` list is empty (fixtures / pre-init) | `true` |
| `ok` | Every `resolve_footprint` destination appears in the lock (any origin) | `true` |
| `missing_from_lock` | At least one resolve destination is **absent** from the lock | `false` |

**Not this gate:** content hash, `origin:preserved` living-doc growth, KH3 declared-but-absent
(KH3 stays unchanged). A path in the lock that is *not* in resolve is existing
drift / `--check-footprint` territory, not this trigger.

**Remediation string (exact token):** `ok sync` (then re-run status).

**Wiring (same three choke points as KH3, reuse exit `2`, no renumber of
`2 > 6 > 35 > 3 > 0`):**

| Surface | Behavior |
| --- | --- |
| `ok status --exit-code` | `footprint_coverage.ok` false → exit `2`. Additive JSON key `footprint_coverage` `{state, ok, missing[], message, remediation}`. Human line when not `ok` / not `not_applicable`. Always-on — no new flag. |
| `ok review --freeze` | Refuses before the reviewer provider runs (same posture as KH3). |
| `ok governance-sync` | `perform_verified_reads` returns `ReadFailure("footprint-coverage", …)` mapped to exit `2`. |

`missing[]` is a sorted list of destination POSIX paths (no absolute machine paths).

### §LT.3.2 — Dogfood sync (this repo)

LT-b **first** mechanical step on the kit checkout: `ok sync --yes`
(`-y` is the existing synonym). After sync, live `.cursor/` and
`.claude/skills/` match `cursor/`, coverage is `ok`, and KH3 remains `ok`.

Do **not** `--force` overwrite living `docs/ROADMAP.md` / `docs/OVERSEER-HANDOVER.md`
(`origin: preserved`).

### §LT.3.3 — Workspace-root honesty (docs only)

The kit cannot choose which folder the operator opens in an IDE.

Auto **must** add the same sentence to `AGENTS.md`, `cursor/README.md`,
`docs/PRINT-NEXT.md`, and `cursor/rules/orchestrator.mdc`:

> Open the repository root (the folder that contains `.overseer/`) as the IDE
> workspace. If you open a parent folder, project rules and skills under
> `.cursor/` often do not load. The CLI still works. The open editor tab is
> not the source of truth — run `ok next`.

`ok status` (human mode) prints one reminder line when `.overseer/` exists:
`ide: open the repo root (folder containing .overseer) so .cursor/rules load`.
JSON key `ide_workspace_hint` (string). Never fail status on this hint.
Never write files outside the repo.

---

## §LT.4 — Slice 2. Session bookends (portable primary + optional Cursor hooks)

### §LT.4.1 — Portable primary (unchanged, still required)

| Action | Command |
| --- | --- |
| Print NEXT from disk | `ok next` / `ok governance-sync --print-next` |
| Session-end hygiene | `ok governance-sync --dry-run` |
| Ad-hoc honesty | `ok check-ok` / `/check-ok` |

Claude Code, Copilot, and paste-only hosts stay on this table. Missing Cursor
hooks is **not** pass and **not** fail — degrade to CLI.

### §LT.4.2 — Config (additive, default off)

```yaml
session_bookends:
  enabled: false
```

- Omitted key → `enabled: false` (current consumers unchanged).
- Unknown keys under `session_bookends` → `ConfigError` (fail closed).
- `enabled` must be a boolean.
- Add `session_bookends` to `OverseerConfig` and parse via a helper like
  `_parse_cost_awareness` / `_parse_governance_gates`. Absent block → default
  `enabled: false`.
- **No secrets, no absolute paths, no hostnames** in this block.

Kit dogfood `.overseer/config.yaml` sets `enabled: true` in LT-b (this repo
only).

### §LT.4.3 — When `enabled: true`, `ok sync` / `ok init` vendors these files

Treat them as normal footprint members **only if** `session_bookends.enabled`
is true. When false, `resolve_footprint` **must not** add them (ONS default
preserved).

| Destination | Source |
| --- | --- |
| `.cursor/hooks.json` | `cursor/hooks/hooks.json` (full file, not a snippet) |
| `.cursor/hooks/session-start-next.sh` | `cursor/hooks/session-start-next.sh` |
| `.cursor/hooks/session-end-closeout.sh` | `cursor/hooks/session-end-closeout.sh` |
| `.cursor/hooks/README.md` | `cursor/hooks/README.md` (updated) |

Scripts **must** be executable in the footprint write. Auto **must** add both
destinations to `EXECUTABLE_FOOTPRINT_DESTINATIONS` in `cli/footprint.py`
(today that frozenset is only `scripts/muse-bridge-deploy.sh`). POSIX `sh`. They locate `ok` by, in
order: `$OVERSEER_OK` if set; `./cli/ok` if present; `ok` on `PATH`. If none
work, print a stderr line and exit 0 (fail **open**).

`cursor/hooks/print-next-stop.json` remains the ONS snippet for humans who
merge by hand. The vendored **full** `hooks.json` **composes** stop +
sessionStart + sessionEnd. Sync merge rule: if a consumer already has
`.cursor/hooks.json` and it differs, classify like any other footprint file
(`missing` → seed; `both-changed` → do not clobber without `--force`). No
JSON deep-merge in Auto v1 (too easy to corrupt). Document: enable the flag
on a greenfield or accept `--force` / hand-merge.

### §LT.4.4 — Narrow ONS supersession

ONS §ONS.9 said hooks are **not** in `resolve_footprint` and **not**
auto-enabled. **This phase does not reopen tab-reload or per-branch names.**
It amends only: when `session_bookends.enabled` is true, the files in §LT.4.3
**are** footprint members and **are** written by `ok sync`. Default remains
false. Cursor Automations JSON templates stay Tier-2 UI, not footprint.

### §LT.4.5 — Hook behavior (fail-open, `loop_limit: 1` on stop)

Frozen `hooks.json` shape (`version: 1`):

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "command": ".cursor/hooks/session-start-next.sh",
        "failClosed": false
      }
    ],
    "sessionEnd": [
      {
        "command": ".cursor/hooks/session-end-closeout.sh",
        "failClosed": false
      }
    ],
    "stop": [
      {
        "command": ".cursor/hooks/session-start-next.sh",
        "failClosed": false,
        "loop_limit": 1,
        "note": "Print NEXT once on stop. Do not re-run governance-sync --dry-run here (sessionEnd already did)."
      }
    ]
  }
}
```

**session-start-next.sh:** run `ok next` (repo root = hook cwd / git root).
Stdout to the host **must** be a single JSON object with **both** keys set to
the same body (hosts ignore unknown keys; `sessionStart` uses
`additional_context`, `stop` uses `followup_message`):

`{"additional_context":"<body>","followup_message":"<body>"}`

`<body>` = CURRENT NEXT heading + fence + workspace-root sentence + stale-tab
sentence. The stale-tab sentence is exactly:

> If an editor tab of the handover looks old, close it and reopen it. The kit
> cannot reload the tab. Trust `ok next`, not the tab.

If `ok next` exits non-zero, still exit 0 and set both keys to the
stderr/reason (fail-open).

**session-end-closeout.sh:** run `ok governance-sync --dry-run` then `ok next`.
Stdout JSON: `{"followup_message":"<dry-run one-line summary + CURRENT NEXT block>"}`
when possible; if the host ignores unknown fields, that is fail-open.
Never write docs, never commit, never merge, never claim tab reload.
`--dry-run` may stamp `.overseer/last_governance_sync` per GFG (already
allowed). Do **not** pass `--write`.

`failClosed` is always **false**. Hooks never block DONE.

### §LT.4.6 — Agent rules (already in source; become live after slice 1 sync)

No new alwaysApply rule beyond what `cursor/rules/print-next-closeout.mdc` and
`check-ok-thinking.mdc` already say. After dogfood sync they load **if** the
operator opened the repo root.

---

## §LT.5 — Slice 3. Mechanical DONE — kit dogfood only, warn first

### §LT.5.1 — Kit config (LT-b writes; consumers untouched)

Add to the kit’s `.overseer/config.yaml` (this repo):

```yaml
honesty:
  enabled: true
  ledger: .overseer/honesty/VERDICT-LEDGER.jsonl
  require_verification_evidence: warn
```

Do **not** set `require_verification_evidence: require` in Auto v1.
Do **not** enable honesty in templates or `ok init` defaults.
Do **not** require `require_agent_signature` (Muse-only hardness; git-only
consumers must stay valid — this *kit* is muse+git-mirror, but defaults stay
soft).

Ledger path is repo-relative. Auto creates the parent directory if missing.
Genesis of the ledger uses existing `ok ledger` / append rules (K10). Do not
gitignore the ledger (it is the honesty record). No secrets in the ledger.

### §LT.5.2 — Active-slice Mode B surface (reuse P-evidence)

When `honesty.enabled` is true **and** `require_verification_evidence` is
`warn` or `require`:

1. Resolve the KH1.9 **active slice** (same scan as `scan_governance_gates`).
2. If there is no active slice, or the active Model is not `Auto` and not the
   Auto half of a split (`{step}b`), **skip** (no historical DONE retro-scan).
3. If the active Auto slice status is `TODO` or `WIP` and the handover does
   **not** claim BV `pass` / DONE, **skip**.
4. If the handover or roadmap claims that active Auto slice is **DONE** or BV
   **`pass`**, run the existing Mode B match:
   - `phase_id` = the active phase id string from KH1.9 (same as gate scan).
   - `--frozen-spec`: if the active ROADMAP deliverable cell contains exactly
     one path matching `docs/archive/phases/PHASE-*.md` (or consumer equivalent
     under `docs/`), pass that path; if zero or more than one such path, omit
     `--frozen-spec` (Mode B already allows omit). Never guess.

| Mode | Missing match | Status `--exit-code` | governance-sync |
| --- | --- | --- | --- |
| `off` | n/a | unchanged | unchanged |
| `warn` | reminder line + JSON `verification_evidence_gate: {ok: true, mode: warn, matched: false}` | **0** (never fail) | footer reminder only |
| `require` | same JSON with `ok: false` + token `missing_verification_evidence` | **2** | `ReadFailure` / exit `2` |

Do **not** invent a new exit code. Token stays `missing_verification_evidence`
(P-evidence).

`review --freeze` is **not** wired to Mode B (wrong gate: freeze is pre-Auto).

### §LT.5.3 — What this does not do

- Does not require a second chat or a different `agent_id` (backlog).
- Does not fail old DONE rows.
- Does not mark ROADMAP DONE by itself.
- Does not deploy, HTTP-probe, or screenshot.

---

## §LT.6 — Slice 4. Compact the living change log

### §LT.6.1 — Command

`ok handover-compact [--dry-run | --write] [--keep N] [--lane NAME] [--json]`

- Default when neither `--dry-run` nor `--write`: **`--dry-run`** (report only).
- `--write` and `--dry-run` together → exit `2`.
- `--keep` default **15**. Must be an integer `>= 5`. Invalid → exit `2`.
- `--lane` uses existing `resolve_lane_docs` (same as `ok next --lane`).
- Add `handover-compact` to `COMMANDS`.
- Must **not** call `muse` or `git`. Config + filesystem only.
- Must **not** regenerate NEXT / paste (GS-PASTE unchanged).

### §LT.6.2 — Algorithm

1. Read the config-driven handover.
2. Require `<!-- overseer:anchor:change-log -->` … `<!-- /overseer:anchor:change-log -->`.
   Missing / unreadable → exit `2`, reason `change_log_anchor_missing`.
3. Inside the region, collect **dated entries** in file order. An entry
   **starts** on a line matching `^- \*\*\d{4}-\d{2}-\d{2}\*\*` and
   **continues** through following lines until the next line that matches that
   regex or the end of the region. Continuation lines belong to the current
   entry. The pointer line in step 7 is **not** a dated entry.
4. If `len(entries) <= keep`, no-op (exit 0, `compacted: 0`).
5. **Frozen order:** the living change log is **newest-first**. Keep the
   **first** `keep` dated entries; archive the remainder (still newest-first
   in the archive heading batch). Do not reverse.
6. Append archived entries (in the same order) under a dated heading
   `## Compacted YYYY-MM-DD` in
   `{root_relative_docs}/archive/handover/CHANGE-LOG.md`, creating directories
   as needed. Create the file with a one-line title
   `# Archived handover change log — {repo.name}` if it does not exist.
7. Rewrite the living region to: the kept entries, a blank line, then exactly
   one pointer line (repo-relative POSIX path, no absolute paths):
   `- Older entries: docs/archive/handover/CHANGE-LOG.md`
   (substitute `root_relative_docs` if it is not `docs`).
8. Idempotent: second run with no new dated bullets → `compacted: 0`, archive
   unchanged. The pointer line is ignored when collecting entries.

Human stdout (non-JSON): `handover-compact: compacted=<n> keep=<k> archive=<relpath>`
plus a trailing newline. `--json`:
`{"ok": true, "compacted": n, "keep": k, "archive": "<relpath>", "wrote": false|true}`.

Do **not** edit NEXT, paste-ready, snapshot, VCS table, or regeneration rules.

### §LT.6.3 — Template + dogfood

Add handover template regeneration rule **10**:

> Living change log keeps the newest 15 dated bullets. Older bullets move via
> `ok handover-compact --write` to `docs/archive/handover/CHANGE-LOG.md`.

LT-b runs `ok handover-compact --write` once on the kit handover after the
command exists.

KH1 still requires a Change log **section**. A short section is valid.

---

## §LT.7 — Tool neutrality (normative)

| Host | Slice 1 | Slice 2 | Slice 3 | Slice 4 |
| --- | --- | --- | --- | --- |
| Any (`ok` CLI) | coverage gate + hint | `ok next` / `governance-sync --dry-run` | Mode B surface | `ok handover-compact` |
| Cursor | same + rules load if repo root | hooks if flag on | same | same |
| Claude Code | same + `.claude/skills` after sync | no hooks; skills + CLI | same | same |
| Copilot / paste | same | `docs/PRINT-NEXT.md` | same | same |

No MuseHub-only behavior. Coverage, compact, and Mode B run on `git-only`.

---

## §LT.8 — SPEC §5 additive rows (LT-b writes)

| Command | Purpose | Writes? |
| --- | --- | --- |
| `ok handover-compact [--dry-run\|--write] [--keep N]` | Archive old handover change-log bullets. Default dry-run. | Yes only with `--write` (handover + archive file) |
| `ok status` (additive JSON) | `footprint_coverage`, `ide_workspace_hint`, optional `verification_evidence_gate` | No |

`session_bookends` is a config block, not a command.

---

## §LT.9 — Rejection / honesty table

| Temptation | Verdict |
| --- | --- |
| Automate close/reopen of the handover tab | **Reject** — no host API |
| Default hooks on for all consumers | **Reject this phase** — flag default false |
| Fail every historical Auto DONE without a ledger line | **Reject** — active slice only |
| Parent-folder `.cursor/` outside the git repo | **Reject** |
| New exit code for coverage | **Reject** — reuse `2` |
| Compact by deleting history | **Reject** — archive file |

---

## §LT.10 — Seven-tier matrix (LT-b)

| Tier | Must prove |
| --- | --- |
| **unit** | Coverage: empty lock → `not_applicable`; dest missing from lock → `missing_from_lock`; all dests listed → `ok`. Config: omitted `session_bookends` → false; unknown key → `ConfigError`; `enabled` non-bool → `ConfigError`. Compact: `keep < 5` → 2; both `--write` and `--dry-run` → 2; missing anchor → 2; `<= keep` → no-op. Mode B skip when honesty off / require off / no active Auto. |
| **integration** | Fixture repo: lock without a new resolve dest → `status --exit-code` 2 + JSON `footprint_coverage`. After writing the dest into the lock, exit not 2 from coverage. `session_bookends.enabled: true` → `resolve_footprint` includes the four hook paths; `false` → those dests absent. Compact `--write` shortens the living region and creates the archive. |
| **e2e** | git-only fixture: enable honesty warn + active Auto DONE without ledger → status exit 0 + warn payload; `require` → exit 2 + `missing_verification_evidence`. Compact then `ok next` still extracts the same fence. |
| **stress** | Handover with 200 dated bullets; compact keep=15; archive grows; living region bounded. Coverage with 50 dests. |
| **data-integrity** | Compact twice → second `compacted: 0`, archive byte-identical. Coverage does not rewrite the lock. Dry-run compact writes nothing. |
| **performance** | `check_footprint_coverage` + compact on a realistic handover finish in a bounded time (same order as `ok status`). |
| **security** | No absolute machine paths in JSON `missing[]` or archive. Hook scripts never interpolate handover body into a shell. Compact does not follow `..` archive paths. Regime least-privilege: git-only fixtures invoke zero `muse`. Fail-open hooks never block on missing `ok`. |

Exact test file prefix: `test_lt_` (under `tests/` seven-tier folders). Do not
invent a second family name.

---

## §LT.11 — Definition of Done

**LT-a (this phase):** this document reviewed → `pass` with a CLI stamp;
ROADMAP LT-a → DONE; NEXT → LT-b; no Auto code; no `main` merge.

**LT-b:** every in-scope deliverable exists at the path this freeze names;
§LT.10 green; kit dogfood `ok sync` applied; kit `session_bookends.enabled: true`
and honesty warn block present; one dogfood compact done; `ok status --exit-code`
not failing for coverage on this repo; no secrets; ROADMAP + HANDOVER updated
together; `/build-verification-review` → `pass` before LT-b DONE. Merge remains
Tier 3.

---

## §LT.12 — Operator paste for LT-b (informational; GS-PASTE may regen)

Model: **Auto**. Build exactly against this file. Do not redesign. Do not
enable honesty or hooks for consumers by default. Do not claim tab reload.

---

## §LT.13 — Cross-references

- ONS — print NEXT; tab-reload non-claim; this phase’s only ONS amendment is §LT.4.4
- KH3 — declared-but-absent; this phase adds coverage (lock behind resolve)
- GFG — dry-run session-end stamp carve-out reused by the end hook
- P-evidence — Mode B + `missing_verification_evidence`
- K9a / K10 — honesty enable + ledger path
- KH1 — change-log section remains required; length may shrink
