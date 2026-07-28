# Phase GFG — Governance freshness gate (Thinking freeze)

Status: **Reviewed → `pass` (GFG-r3).** GFG-a is **spec-only** and now frozen; no code lands in
this phase. GFG-b (Auto) is cleared to build mechanically against this frozen contract.

```yaml
phase: GFG
outputs:
- id: gfg-governance-freshness-gate
  path: docs/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md
  frozen: true
frozen_inputs:
- id: phase-9a5-triggers
  path: docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: governance-hygiene-engine
  path: tools/governance_hygiene/engine.py
- id: governance-hygiene-drift
  path: tools/governance_hygiene/drift.py
- id: governance-hygiene-reads
  path: tools/governance_hygiene/reads.py
- id: status-exit-code
  path: cli/commands/status.py
- id: land-check
  path: tools/close_ritual/land_check.py
- id: freeze-review-session-end-template
  path: cursor/automations/freeze-review-session-end.json
- id: kh2-hard-gate-precedent
  path: docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md
- id: kh3-hard-gate-precedent
  path: docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md
review_stamp:
  reviewed_at: '2026-07-28T13:34:41Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:fe8a3a15711bb92dfe44cc95c444e5fc70710a9c0f4018d07e3100279c6b8f66
```

**Downstream edge:** GFG-b treats this document as ground truth without re-deriving it (SPEC §6
mandatory reviewed freeze). It fills the permanent gap left when 9A-5 chose a session-end Cursor
Automation for `governance-sync` but only freeze-review Automation templates shipped, and when
`ok status --exit-code` could report green while D1/D2 drifted and `last_governance_sync` was
absent — the exact consumer incident after Scooling finish land #219 (2026-07-28).

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| GFG-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist gate clean (0 findings). Semantic: **R1-M1** skill/engine dry-run “writes nothing” wording must be amended for marker carve-out (`cursor/skills/governance-sync/SKILL.md`; `engine.py` emit ~line 366); **R1-M2** §GFG.5.3 underspecified stamp sites vs `fully_aligned` vs dry-run plan-emission (`engine.py` ~365); **R1-M3** missing consumer blast-radius honesty; **R1-N1** Automation `degrade.skill` style; **R1-N2** `cursor/README.md` Tier-3 enable wording. Fixed in-doc. |
| GFG-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** R1 cited `tests/data_integrity/test_governance_idempotency.py:76` as a dry-run test to rewrite — that line is mid-apply *failure* and must **keep** asserting no marker. Corrected deliverables: keep failure no-stamp; amend skill/engine strings; add §GFG.9 stamp tests. |
| GFG-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read: R1-M1–M3 / R1-N1–N2 / R2-M1 RESOLVED; non-goals hold (no post-merge hook, no silent main writes, no consumer hand-edit fix); D1/D2 fail-closed + marker stale rules precise; three stamp sites named; circular wiring into `governance-sync`/`review --freeze` correctly excluded; exit `2` reuse does not renumber `2 > 6 > 35 > 3 > 0`; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (Tier-1 CLI surfaces + Tier-2 Automation enable). Stamp written by `ok review --freeze`. |

---

## §GFG.0 — Simple summary

When a project’s main branch moves forward, the handover and roadmap notes are supposed to be
updated in the same work session. The tool that checks and fixes those notes already exists
(`ok governance-sync`), but nothing reliable runs it at session end, and nothing refuses to say
“all green” when the notes are stale. So merges can land while the living docs lie — and agents
keep trusting the lie.

**GFG closes that permanently in two complementary ways:** (B) ship the missing session-end
Automation template that runs `ok governance-sync --dry-run` (same pattern as freeze-review’s
session-end template), and (C) make `ok status --exit-code` (and `ok land-check` when the close
ritual is enabled) fail closed when handover/main drift is present or the local freshness stamp
is missing/stale after main has moved. No GitHub post-merge hook. No silent writes to `main`. No
one-off hand-edit of a consumer handover as the “fix.”

**Technical summary:** add `cursor/automations/governance-sync-session-end.json` (template only;
operator enables — Tier 2). Add `tools/governance_freshness/` (`GovernanceFreshnessReport` /
`check_governance_freshness`) that reuses D1/D2 from `tools/governance_hygiene/drift.py` plus an
enriched `.overseer/last_governance_sync` marker. Wire the probe into `ok status --exit-code`
(reuse exit `2`) and into `ok land-check` when `close_ritual.enabled: true`. Amend the marker write
path so a successful aligned verification stamps the marker (including on `--dry-run`) — a local
`.overseer/` side effect only; docs, commits, realign, and `main` remain untouched by dry-run.

---

## §GFG.1 — Scope

**In scope (freeze only — this phase writes no code):**

- Session-end Automation template for `ok governance-sync --dry-run` (§GFG.3).
- `GovernanceFreshnessReport` + `check_governance_freshness` resolution rule (§GFG.4).
- Marker format + write rules, including the narrow dry-run carve-out vs 9A-5 §7 (§GFG.5).
- Fail-closed wiring for `ok status --exit-code` and `ok land-check` (§GFG.6).
- Explicit non-goals / rejection table (§GFG.2).
- Boundary table (§GFG.7) and seven-tier matrix for GFG-b (§GFG.9).

**Out of scope (explicit non-goals — prevent creep):**

| Non-goal | Why rejected |
| --- | --- |
| **GitHub `post-merge` hook (or any git hook) as primary trigger** | Already **REJECTED** in 9A-5 §1 (`docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` lines 88–96): does not fire for GitHub-side merges, does not work in `muse-only`, invisible per-clone. GFG does not reopen that decision. |
| **Silent writes on `main`** | SD-14 / Tier 3. Automation and dry-run never merge, never push `main`, never open a docs-only PR to `main`. Apply path remains feature-branch only (9A-5 §6). |
| **One-off hand-edit of consumer handovers as the fix** | That patches a symptom once; the next land re-creates the gap. GFG fixes the kit so every consumer gets detection + session-end trigger after `ok sync`. |
| **Auto-apply / auto-commit from session-end Automation** | Default remains `--dry-run`. Apply stays an explicit operator/agent action. |
| **Wiring freshness fail-closed into `ok governance-sync` itself** | Circular — the tool that repairs freshness must not refuse to run because freshness is stale. |
| **Wiring into `ok review --freeze`** | Out of this phase’s stated surfaces (status / land-check). Freeze review remains independent; operators may still review specs on a tree with stale handover. |
| **Making `close_ritual.enabled: true` the default for all consumers** | Scooling currently has `close_ritual.enabled: false`; flipping consumer posture is Tier 3 / out of kit Auto. Land-check wiring is additive when enabled; **status `--exit-code` is the always-on floor**. |
| **Fail-closing on D3 alone** | Prompt scopes fail-closed to **D1/D2** (or marker stale). D3 remains detectable by `governance-sync` but does not drive the GFG status/land-check exit. |
| **Redefining frozen `status --exit-code` precedence** | Reuse exit `2` (same tier as substrate / muse_sync / footprint_self_integrity). No new exit code; no renumber of `2 > 6 > 35 > 3 > 0`. |
| **Hosted dashboard / Track Q / consumer product changes** | Kit governance only. |

---

## §GFG.2 — Incident → permanent gap (verified, do not redesign)

| Fact | Evidence |
| --- | --- |
| 9A-5 chose slash command **+** session-end Automation; rejected post-merge hook | `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` §1 (lines 88–99) |
| Only freeze-review Automation templates exist today | `cursor/automations/freeze-review-session-end.json`, `freeze-review-on-merge.json` — no `governance-sync-*.json` |
| `governance-sync` CLI works; default dry-run; detects D1/D2 | `tools/governance_hygiene/`; live Scooling dry-run after SC #219 |
| Marker written only inside `_apply_plan` (patch path) | `tools/governance_hygiene/engine.py` line 464 — never on `fully_aligned` early return (lines 285–305), never on dry-run |
| `status` exposes `last_governance_sync` but never fail-closes on it | `cli/commands/status.py` lines 31–39, 279; `_exit_code_from_conditions` lines 91–120 ignore marker |
| `land-check` no-ops when `close_ritual.enabled: false` | `tools/close_ritual/land_check.py` lines 92–102 |
| K13 multi-repo did not break single-repo sync | `workspace_relay: not_configured` expected when workspace unset |

GFG **must not** redesign D1/D2 semantics, the VCS adapter interface, or 9A-5’s feature-branch commit strategy. It adds the missing Automation template, the missing fail-closed choke points, and the missing marker stamp on aligned verification.

---

## §GFG.3 — (B) Session-end Automation template (frozen)

Ship a new kit template next to the existing freeze-review templates:

**Path:** `cursor/automations/governance-sync-session-end.json`

**Frozen JSON shape** (keys mirror `cursor/automations/freeze-review-session-end.json`):

```json
{
  "name": "overseer-governance-sync-session-end",
  "description": "Session-end governance freshness check (dry-run) — degrade to CLI when Automations unavailable",
  "trigger": "session_end",
  "command": "ok governance-sync --dry-run",
  "degrade": {
    "manual_cli": "ok governance-sync --dry-run",
    "skill": "/governance-sync"
  },
  "note": "Template only — operator must enable in Cursor (Tier 2 confirm-once). Default dry-run: no governance-doc writes, no commits, no main merge/push. Aligned runs may stamp local .overseer/last_governance_sync only (§GFG.5). Never treat Automation unavailability as pass."
}
```

**Frozen rules:**

1. **Not auto-enabled.** Vendoring the JSON into a consumer does not turn the Automation on. Enabling in Cursor is **Tier 2** (confirm once) — confirm-once recommendation, not a merge/live gate. GFG-b must correct the outdated `cursor/README.md` row that currently says “Tier-3 to enable” for `automations/*.json` so it matches this Tier-2 posture (and the freeze-review-loop skill’s Automation tier note).
2. **Command is always `--dry-run`.** Session-end never auto-applies patches.
3. **Degrade path required.** If Automations are unavailable, agents/operators run `ok governance-sync --dry-run` (or the governance-sync skill). Unavailability ≠ pass.
4. **No on-merge Automation for governance-sync in GFG.** 9A-5 rejected post-merge as primary; GFG does not add a GitHub/git merge Automation that pretends to replace it. Session-end + explicit CLI remain the triggers.
5. **Canonical CLI name is `ok`.** Match Q2a/Q2b; do not introduce a new `overseer`-only template for this slice (existing freeze-review templates may keep their historical `overseer` command string until a separate cleanup).

---

## §GFG.4 — (C) `GovernanceFreshnessReport` + `check_governance_freshness` (frozen)

New module `tools/governance_freshness/` (sibling to `tools/muse_sync/` / `tools/footprint_integrity/`):

```python
@dataclass(frozen=True)
class GovernanceFreshnessReport:
    state: str  # ok | drifted | stale_marker | unreadable | not_applicable
    message: str
    remediation: str | None
    d1: str | None = None          # aligned | drifted | unreadable | None if not run
    d2: str | None = None
    marker_present: bool = False
    marker_r1: str | None = None
    actual_r1: str | None = None

    @property
    def ok(self) -> bool:
        return self.state in {"ok", "not_applicable"}


def check_governance_freshness(
    config: OverseerConfig,
    repo_root: Path,
    *,
    adapter: VcsAdapter | None = None,
    runner: CommandRunner | None = None,
) -> GovernanceFreshnessReport:
    ...
```

### §GFG.4.1 — Reads used by the probe (frozen)

The probe needs **D1 and D2 only** (not D3). To avoid coupling status to `gh` (R4):

1. Perform **R1, R2, R3, R5** via the existing adapter/read helpers (same sources as
   `perform_verified_reads` in `tools/governance_hygiene/reads.py`), **skipping R4** (`gh pr list`).
2. Construct a `VerifiedReads` (or an internal equivalent) with `r4_merged_prs=()` so
   `detect_drift` can run; **ignore** `d3_queue_vs_merged` for ok/not-ok (D3 may be `aligned` by
   vacuity when R4 is empty — that MUST NOT be treated as a freshness failure).
3. Read default-lane handover text from config docs paths (same resolution as governance-sync
   default lane). Roadmap text may be omitted or empty for this probe when only D1/D2 are needed;
   if `detect_drift` requires roadmap bytes, pass the real roadmap file contents but still ignore D3
   in the freshness verdict.
4. Any R1/R2/R3/R5 read failure → `state="unreadable"` (fail closed), with `message` naming the
   failing command — same posture as 9A-5 §7 / KH2 unreadable.

**Frozen non-requirement:** the probe does **not** call `gh`. Status must remain usable offline
relative to GitHub PR listing.

### §GFG.4.2 — Resolution rule (frozen, evaluated in this order)

Let `initialized` mean `.overseer/version.lock` exists and parses (same install signal status uses).

1. If config/repo cannot be loaded → `state="unreadable"`.
2. If not `initialized` → `state="not_applicable"` (no install → no freshness obligation yet).
3. Run freshness reads (§GFG.4.1). On read failure → `state="unreadable"`.
4. Compute D1/D2 via `detect_drift` (existing functions in `tools/governance_hygiene/drift.py`).
   - If D1 or D2 is `unreadable` → `state="unreadable"`.
   - If D1 or D2 is `drifted` → `state="drifted"`, remediation =
     `ok governance-sync --dry-run` then apply when the plan is correct
     (`ok governance-sync` without dry-run / explicit apply path).
5. Else (D1 and D2 both `aligned`): evaluate the marker (§GFG.5):
   - Parse `.overseer/last_governance_sync`.
   - **Missing marker** while a regime tip is known (`actual_r1` readable for
     `git-only`/`muse+git-mirror`, or `r3` readable for `muse-only`) →
     `state="stale_marker"` (“never stamped” / missing after main advanced).
   - **Marker has `r1=` (or muse-only `r3=`) and that value ≠ current tip** (case-normalized) →
     `state="stale_marker"` (“main advanced since last stamp”).
   - **Legacy marker** (ISO timestamp only, no tip field): counts as **present** for the
     missing-marker check; does **not** alone prove tip freshness. When D1/D2 are aligned and
     tip is known, legacy-only → `state="stale_marker"` with remediation to re-run
     `ok governance-sync --dry-run` so GFG-enriched stamp is written (forces upgrade once).
   - Otherwise → `state="ok"`.

**Frozen non-triggers:**

- Mid-feature-branch dirty work with handover still correctly claiming the current GitHub/`main`
  tip → D1 stays `aligned`; marker tip still matches → **ok** (session work in progress).
- D3 drifted alone → **not** a GFG fail (governance-sync still reports it; status/land-check GFG
  ignores D3).
- `close_ritual.enabled: false` → does not change status GFG; only land-check stays no-op for
  the close-ritual path (§GFG.6).

---

## §GFG.5 — Marker format + write rules (frozen; amends 9A-5 §7 narrowly)

### §GFG.5.1 — File location

Path: `{repo_root}/.overseer/last_governance_sync`  
Constant name remains `last_governance_sync` (`cli/commands/status.py` line 31;
`tools/governance_hygiene/engine.py` line 26).

### §GFG.5.2 — Enriched format (frozen)

UTF-8 text, LF newlines:

```text
<ISO-8601Z timestamp>
r1=<github_main_sha_or_empty>
r3=<canonical_main_sha_or_empty>
```

- Line 1: timestamp (existing meaning).
- `r1=` : GitHub / git main tip SHA when regime has git; empty for `muse-only`.
- `r3=` : canonical main tip SHA (Muse main or git-only equivalent).
- Unknown keys ignored for forward compatibility.
- Status JSON `last_governance_sync` continues to expose the **timestamp string** (line 1) for
  backward compatibility; tip fields appear only under the new
  `governance_freshness` payload (§GFG.6).

### §GFG.5.3 — When the marker is written (frozen)

Write/refresh the enriched marker (§GFG.5.2) when **all** of the following hold in a
`governance-sync` run:

1. Verified reads succeeded.
2. D1 and D2 are both `aligned` (D3 may be drifted — still allow stamp; stamp proves D1/D2 ritual
   only).
3. The run is in one of these engine paths (GFG-b must cover **each**):
   - **`fully_aligned` early-return** (`tools/governance_hygiene/engine.py` lines 285–305) — today
     returns without writing; GFG-b inserts `_write_sync_marker` (enriched) before return, for both
     dry-run and apply.
   - **Dry-run plan-emission path** (the `if dry_run:` branch after drift is not fully aligned —
     currently `tools/governance_hygiene/engine.py` ~line 365) **when D1 and D2 are nonetheless
     aligned** (D3-only drift). Stamp before returning the planned patch; still write zero
     handover/roadmap bytes. Update the emit string currently reading
     `dry-run: no writes, commits, or realign apply` (~line 366) so it does not lie when the
     marker stamp occurs (e.g. name the marker exception).
   - **`_apply_plan` success path** (line 464 today) — keep the write; upgrade to enriched format.

**Must not stamp when D1 or D2 is `drifted` or `unreadable`** — including dry-run that only reports
a D1/D2 plan. **Must not stamp on mid-apply failure** — keep
`tests/data_integrity/test_governance_idempotency.py` line 76
(`test_mid_apply_failure_leaves_no_commit`) asserting the marker is absent after exit `5`.

**Narrow carve-out vs 9A-5 §7 dry-run inertness:** 9A-5 §7 states dry-run “writes nothing.” GFG
**amends that sentence** to: dry-run writes nothing **except** the local
`.overseer/last_governance_sync` marker when D1/D2 are aligned. Dry-run still must not patch
handover/roadmap, must not commit, must not realign, must not touch `main`. This carve-out is
required so session-end Automation (`--dry-run`) can clear `stale_marker` without forcing a no-op
apply.

**Mandatory companion doc updates (not optional):** amend
`cursor/skills/governance-sync/SKILL.md` (and twin vendored skill if footprint copies it) so
“Writes only on explicit non-dry-run” names the marker carve-out. Existing integration dry-run
doc-byte assertions (`tests/integration/test_governance_sync_dry_run.py` —
`test_governance_sync_dry_run_tree_unchanged`) remain valid if they only check handover/roadmap
bytes; GFG-b adds positive marker-stamp coverage via §GFG.9 rather than weakening the mid-apply
failure no-stamp guarantee.

### §GFG.5.4 — Gitignore

GFG-b adds `.overseer/last_governance_sync` to the kit’s `.gitignore` / `.museignore` (and ensures
consumer sync footprint or docs mention it) so the stamp stays **clone-local**. A fresh clone after
main advanced must re-stamp via `ok governance-sync --dry-run` — fail-closed until then.

---

## §GFG.6 — Wiring: status + land-check (frozen)

Reuse exit code **`2`**. Do **not** renumber `2 > 6 > 35 > 3 > 0`.

| Surface | Behavior |
| --- | --- |
| `ok status` / `ok status --json` | Always compute `check_governance_freshness` when initialized (additive). JSON key `governance_freshness: {state, ok, message, remediation, d1, d2, marker_present, marker_r1, actual_r1}`. Human mode prints a line when not ok (mirror `muse_sync` / `substrate`). Plain status without `--exit-code` still exits `0`. |
| `ok status --exit-code` | Extend `_exit_code_from_conditions` with `governance_freshness_ok`. Fold into the top tier: `config_error or not substrate_ok or not muse_sync_ok or not footprint_self_integrity_ok or not governance_freshness_ok → 2`. |
| `ok land-check` | When `close_ritual.enabled: false`, keep today’s no-op exit `0` (**unchanged**). When enabled, after existing path checks, run `check_governance_freshness`; if not ok → fail land-check with exit `2` and emit freshness message/remediation (never merge). |
| `ok governance-sync` | **Not** fail-closed on freshness (circular). Implements marker write rules (§GFG.5). |
| `ok review --freeze` | **Not** wired in GFG. |

---

## §GFG.7 — Boundary table (frozen, stated plainly)

| Scenario | Caught by GFG? |
| --- | --- |
| GitHub `main` advances; handover VCS-table SHA stale; `ok status --exit-code` | **Yes** — D1 `drifted` |
| Muse↔Git anchor/canonical mismatch | **Yes** — D2 `drifted` |
| Docs hand-edited to match main but ritual never run; marker missing | **Yes** — `stale_marker` |
| Marker tip SHA behind current R1; D1 somehow aligned | **Yes** — `stale_marker` (main advanced) |
| Session-end Automation unavailable | **Degrade** — CLI/skill required; not treated as pass |
| `close_ritual.enabled: false` (Scooling today) | Status GFG still active; land-check GFG inactive (no-op) |
| D3 queue vs merged PRs only | **No** (by design) — use `ok governance-sync` |
| Mid-edit feature work; handover still names current main tip; marker current | **No trigger** |
| GitHub post-merge without local session | **Not via hook** — caught next local `status --exit-code` / session-end dry-run |
| One-off consumer handover rewrite without kit change | **Not a solution** — rejected non-goal |

---

## §GFG.8 — Config & docs touchpoints (frozen)

- **No new required config block** for the status gate (always-on when initialized), matching KH2/KH3.
- Optional future `governance_freshness:` suppress flag is **out of scope** for GFG (would recreate
  the skip path that caused the incident).
- Update kit operator-facing notes only as needed for the new Automation template path + marker
  gitignore (README / `cursor/README.md` one-line rows, including Tier-2 enable correction). No
  consumer handover rewrites in GFG-b.
- SPEC §5 command table: no new subcommand; document additive `governance_freshness` on status if
  SPEC lists status JSON keys (additive only).

### §GFG.8.1 — Consumer blast radius (frozen honesty — not optional prose)

After GFG-b merges and consumers `ok sync`, any workflow that runs `ok status --exit-code` will
start returning `2` until that clone runs `ok governance-sync --dry-run` at least once with D1/D2
aligned (or apply when drifted). That is the intended permanent floor, not a bug. GFG-b must not
ship a silent default-off switch. Operator docs may state the one-time re-stamp expectation;
they must not soften the gate.

---

## §GFG.9 — Seven-tier test matrix (GFG-b Auto must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | `check_governance_freshness` resolution table: ok / drifted (D1) / drifted (D2) / stale_marker (missing) / stale_marker (r1 mismatch) / stale_marker (legacy timestamp-only) / unreadable / not_applicable; D3-only drift does not force not-ok; marker parse accepts enriched + legacy. |
| **integration** | `ok status --json --exit-code` returns `2` with `governance_freshness.state=drifted` when handover claim ≠ R1; returns `2` with `stale_marker` when marker absent and initialized; returns `0` when D1/D2 aligned and enriched marker matches tip. `ok governance-sync --dry-run` on aligned fixture stamps marker without modifying handover/roadmap bytes. |
| **e2e** | Fixture: advance main tip + leave stale handover → status `--exit-code` fails → dry-run reports plan → apply (or aligned stamp path) → status `--exit-code` passes. Land-check with `close_ritual.enabled: true` fails on drifted freshness even when `require_paths` match. |
| **stress** | Large handover/roadmap (200+ queue rows) — freshness probe skips R4 and still finishes in bounded time; no per-PR GitHub listing. |
| **data-integrity** | Dry-run with D1/D2 aligned: marker written; handover/roadmap byte-identical; no commit. Dry-run with D1 drifted: no marker refresh; no doc writes. Idempotent double dry-run when aligned. |
| **performance** | `ok status --exit-code` adds no `gh` invocation for GFG; R1/R2/R3/R5 only. |
| **security** | No secrets in marker/payload; tip SHAs are runtime reads; remediation strings are non-executed; muse-only never calls git/gh; fail-closed on unreadable rather than optimistic `ok`; Automation template cannot merge or push. |

---

## §GFG.10 — GFG-b Auto deliverables (exact)

1. `cursor/automations/governance-sync-session-end.json` per §GFG.3.
2. `tools/governance_freshness/` package (`__init__.py`, report + `check_governance_freshness`).
3. Marker write/enrichment in `tools/governance_hygiene/engine.py` per §GFG.5 — **all three** stamp
   sites (fully_aligned early-return, dry-run plan-emission when D1/D2 aligned, `_apply_plan`).
4. `cli/commands/status.py` wiring + JSON/human surfaces per §GFG.6.
5. `tools/close_ritual/land_check.py` freshness check when enabled per §GFG.6.
6. `.gitignore` / `.museignore` entry for `.overseer/last_governance_sync`.
7. Minimal kit doc row updates: `cursor/README.md` Automations tier wording (Tier 2 enable) +
   README Automations table row for governance-sync session-end — no consumer handover rewrites.
8. Amend `cursor/skills/governance-sync/SKILL.md` dry-run write sentence for the marker carve-out
   (and twin vendored skill path if footprint copies it); amend engine dry-run emit string (~366).
9. Keep `test_mid_apply_failure_leaves_no_commit` no-marker assertion
   (`tests/data_integrity/test_governance_idempotency.py:76`). Do not weaken it.
10. Seven-tier tests under `tests/` covering §GFG.9 (including positive dry-run marker stamp when
    D1/D2 aligned, and no stamp when D1 drifted).
11. `/build-verification-review` → `pass` before ROADMAP GFG-b → DONE.

---

## §GFG.11 — Hard stops (unchanged)

- No kit `main` merge without Tier 3 authorization.
- No consumer posture/env flips; no secrets.
- No GitHub post-merge hook.
- No silent writes on `main`.

---

## Cross-references

- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` §1 — trigger decision this phase completes.
- `docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md` / `docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md` —
  fail-closed wiring precedent (exit `2`).
- `docs/OVERSEER-KIT-SPEC.md` §6 — Freeze-Contract review policy.
- `cursor/automations/freeze-review-session-end.json` — template shape precedent.
- `cli/commands/status.py` — exit precedence and `last_governance_sync` read.
- `tools/close_ritual/land_check.py` — land-check no-op when disabled.
