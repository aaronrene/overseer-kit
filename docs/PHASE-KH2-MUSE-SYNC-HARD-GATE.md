# Phase KH2 — Muse-sync hard gate (Thinking freeze)

Status: **Reviewed → `pass` (KH2-r2).** KH2a is **spec-only** and now frozen; no code lands in this
phase. KH2b (Auto) is cleared to build mechanically against this frozen contract; it is the only
phase that writes files.

```yaml
phase: KH2
outputs:
- id: kh2-muse-sync-hard-gate
  path: docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md
  frozen: true
frozen_inputs:
- id: substrate-health-impl
  path: tools/substrate_health/check.py
- id: adapter-status-interface
  path: adapters/base.py
- id: adapter-types
  path: adapters/types.py
- id: muse-git-mirror-status
  path: adapters/muse_git_mirror/adapter.py
- id: cli-status-exit-precedence
  path: cli/commands/status.py
- id: cli-review-freeze
  path: cli/commands/review.py
- id: governance-hygiene-reads
  path: tools/governance_hygiene/reads.py
- id: kh1b-gate-reminder-precedent
  path: docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: agents-md-day-to-day-rule
  path: AGENTS.md
- id: bridge-workflow-day-to-day
  path: MUSE-BRIDGE-WORKFLOW.md
review_stamp:
  reviewed_at: '2026-07-12T23:52:32Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:735cbcede8a41a4378d2fe8de6f4b8085078ba4b8dc79c6836c68f3a286f563f
```

**Downstream edge:** KH2b treats this document as ground truth without re-deriving it (SPEC §6
mandatory reviewed freeze). It extends the `tools/substrate_health/` family KH1b already shipped —
this contract governs the additional detection + wiring, not a redesign of KH1b.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| KH2-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist gate clean (0 findings). Semantic review raised one non-escalating MAJOR internal-consistency finding: **R1-M1** (§KH2.5 `governance-sync` wiring row claimed the `StatusResult` was available immediately after `check_substrate`, before `adapter.status()` is actually called in `tools/governance_hygiene/reads.py` — contradicted the function's real call order). Fixed: the row now correctly places the check after the existing `status = adapter.status()` call and its `ReadError` check. |
| KH2-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read confirmed R1-M1 RESOLVED and consistent with the verified call order in `tools/governance_hygiene/reads.py`; `review --freeze` and `status --exit-code` insertion points independently re-verified against `cli/commands/review.py` / `cli/commands/status.py`; exit-code reuse (`2`) does not renumber the frozen `2 > 6 > 3 > 0` precedence; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (gate targets Tier-1 CLI surfaces, not a Tier-3 action directly). Stamp written by `overseer review --freeze`. |

---

## §KH2.0 — Simple summary

Overseer Kit already lets a repo say "MuseHub is my real source of truth; GitHub is just a mirror."
That promise is only real if MuseHub actually *has* everything. Right now, saving work to Git and
saving work to MuseHub are two separate manual actions on two separate systems, and nothing checks
that the second one actually happened. On this very repo, that gap let real work sit in Git for a
while with zero trace in MuseHub, and nothing warned anyone — the kit's own health check only looks
for whether MuseHub's *files* exist, not whether its *content* is current.

**KH2 closes that gap with a hard, fail-closed check**, not a reminder that can be ignored: whenever
a repo is set up so MuseHub is canonical and Git is the mirror, and Git has already captured a change
that MuseHub has not, the kit's own commands (`status --exit-code`, `review --freeze`,
`governance-sync`) refuse to say everything is fine. It only fires on the specific, precise condition
that actually happened — "Git is clean, Muse is not" — so normal mid-edit work is never falsely
blocked.

**Technical summary:** extend `StatusResult` (`adapters/types.py`) with two new optional fields,
`muse_dirty` and `git_dirty`, so the `muse+git-mirror` adapter's already-computed-but-discarded
per-VCS dirty signals survive past the point where they are currently OR'd together and lost. Add a
new `tools/muse_sync/` probe, sibling to `tools/substrate_health/`, that derives a `MuseSyncReport`
from those two fields: `pending` exactly when `muse_dirty` is true and `git_dirty` is false (Git has
committed content that Muse's last commit does not reflect); `not_applicable` outside
`muse+git-mirror`; `unreadable` when either flag could not be determined (fail closed). Wire
`check_muse_sync` into the same three fail-closed choke points KH1b already uses for substrate
health — `overseer status --exit-code`, `overseer review --freeze`, `overseer governance-sync` — all
returning the existing exit code `2` (the same "the declared canonical VCS state cannot currently be
trusted" tier substrate-health already occupies; no new exit code, no change to the frozen `2 > 6 >
3 > 0` `status` precedence order).

---

## §KH2.1 — Scope

**In scope (freeze only — this phase writes no code):**

- The `StatusResult.muse_dirty` / `StatusResult.git_dirty` field additions and which adapters
  populate them (§KH2.3).
- The `MuseSyncReport` shape and the `check_muse_sync` resolution rule (§KH2.4).
- The three wiring points and the exact exit-code treatment (§KH2.5).
- The precise boundary of what this gate does and does not catch, stated plainly so it is never
  oversold (§KH2.6).
- The seven-tier test matrix KH2b must satisfy (§KH2.8).

**Out of scope (explicit non-goals — prevent creep):**

- **Automatically running `muse commit` on the operator's behalf.** This gate only detects and
  refuses; it never writes a Muse commit for anyone. A content commit is a decision a human or an
  explicitly-invoked agent action makes, never a side effect of a read-only status/gate check.
- **Detecting drift that survives a subsequent edit.** If Git becomes dirty again before the gate is
  ever run (new edits stacked on top of an already-uncaptured Muse-lagging commit), this specific
  check goes quiet again, because its trigger condition is specifically "Git clean, Muse dirty." This
  known boundary is documented, not silently ignored (§KH2.6) — closing it fully would require a
  persisted "last Git SHA Muse has seen" anchor, which is deliberately deferred as a separate,
  future-scoped enhancement so this phase stays small and provably correct for the failure mode that
  actually occurred.
- **`muse-only` and `git-only` regimes.** Both are single-VCS; there is no second history to fall
  behind, so the gate is `not_applicable` there by definition, not merely unimplemented.
- **Any change to the `realign` / bridge-export mechanism.** Those already correctly guard the
  opposite direction (GitHub main diverging ahead of Muse via a bypassed push). KH2 is additive and
  orthogonal.
- **Redefining the frozen `status --exit-code` precedence order.** KH2 reuses exit code `2` — the
  same tier `substrate_ok` already occupies — rather than inserting a new tier into `2 > 6 > 3 > 0`.

---

## §KH2.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Adapter already computes both signals | `MuseGitMirrorAdapter.status()` calls `self._muse_dirty()` and `self._git("status", "--porcelain")`, then discards the distinction: `dirty = muse_dirty or bool(git_dirty.stdout.strip())` | `adapters/muse_git_mirror/adapter.py` |
| `_muse_dirty()` helper | Already reads `muse status --json` (`dirty` or `total_changes` field) with a `--porcelain` fallback; shared by `muse+git-mirror` and `muse-only` adapters | `adapters/base.py` |
| `StatusResult` | `{ regime, dirty, branch, notes }` — one combined boolean, no per-VCS breakdown | `adapters/types.py` |
| Substrate health | Checks `.muse/HEAD` / `repo.json` / `config.toml` **exist** — structural presence only, no content-freshness check | `tools/substrate_health/check.py` |
| `status` exit precedence (frozen) | `_exit_code_from_conditions`: `2 (config_error or not substrate_ok) > 6 (footprint mismatch) > 3 (drift behind/ahead) > 0` | `cli/commands/status.py` |
| `review --freeze` substrate gate | `substrate = check_substrate(...); if not substrate.ok: return 2` before any review runs | `cli/commands/review.py` |
| `governance-sync` substrate gate | `perform_verified_reads` calls `check_substrate` first; on failure returns `ReadFailure`, which `run_governance_sync` maps to `exit_code=2` | `tools/governance_hygiene/reads.py`, `tools/governance_hygiene/engine.py` |
| Governance gate reminders | `tools/governance_gates/` — `gate_id` enum is exactly `freeze_review \| build_verification \| handover_paste`; no sync-freshness gate exists | `tools/governance_gates/types.py` |
| Documented day-to-day rule (already frozen) | "Feature work: `muse commit` on a feature branch" — a manual step with no automated cross-check today | `AGENTS.md`, `MUSE-BRIDGE-WORKFLOW.md` |

KH2 **must not** change `_muse_dirty()`'s algorithm, the existing `dirty` field's meaning, the
`realign`/bridge mechanism, or the frozen `status` exit-code ordering. It only **adds** two
`StatusResult` fields, one new read-only probe module, and additive checks at three existing
fail-closed choke points.

---

## §KH2.3 — `StatusResult` field additions (frozen)

Add two optional fields to `adapters/types.py`'s `StatusResult`, appended after `notes` so existing
positional/keyword construction in tests and adapters is unaffected:

```python
@dataclass(frozen=True)
class StatusResult:
    regime: str
    dirty: bool
    branch: str
    notes: list[str] = field(default_factory=list)
    muse_dirty: bool | None = None   # None = not determined / not applicable to this regime
    git_dirty: bool | None = None    # None = not determined / not applicable to this regime
```

Population rules per adapter (frozen):

| Adapter | `muse_dirty` | `git_dirty` |
| --- | --- | --- |
| `MuseGitMirrorAdapter` | The already-computed `self._muse_dirty()` result | The already-computed `git status --porcelain` non-empty check |
| `MuseOnlyAdapter` | The already-computed `self._muse_dirty()` result | `None` (no Git in this regime) |
| `GitOnlyAdapter` | `None` (no Muse in this regime) | The already-computed `git status --porcelain` non-empty check |

The existing combined `dirty` field's value and meaning are **unchanged** in every adapter — this is
a pure addition, not a behavior change to anything already reading `.dirty`.

---

## §KH2.4 — `MuseSyncReport` + `check_muse_sync` (frozen)

New module `tools/muse_sync/` (sibling package to `tools/substrate_health/`, same shape for
consistency):

```python
@dataclass(frozen=True)
class MuseSyncReport:
    regime: str
    state: str  # synced | pending | not_applicable | unreadable
    message: str
    remediation: str | None

    @property
    def ok(self) -> bool:
        return self.state in {"synced", "not_applicable"}


def check_muse_sync(config: OverseerConfig, status: StatusResult) -> MuseSyncReport:
    ...
```

**Resolution rule (frozen, evaluated in this order):**

1. `config.vcs.regime != "muse+git-mirror"` → `state="not_applicable"` (`muse-only` and `git-only`
   have exactly one history each; there is nothing to fall behind).
2. `status.muse_dirty is None or status.git_dirty is None` → `state="unreadable"` — fail closed:
   the gate refuses to claim "synced" when it cannot prove it, exactly mirroring the fail-closed
   philosophy already used by `read_head`/`read_canonical_anchor`/substrate health.
3. `status.muse_dirty is True and status.git_dirty is False` → `state="pending"` — the precise,
   frozen trigger condition: Git's working tree is clean (the last unit of work has already been
   committed to Git) while Muse's working tree still differs from Muse's last commit (that same work
   has not been captured in Muse). `message` names this exactly; `remediation` is the literal
   two-command sequence `muse code add -A && muse commit -m "<message>"`.
4. Otherwise → `state="synced"`.

**Frozen non-triggers (must not fire — this is the false-positive guard):**

- `git_dirty is True` (regardless of `muse_dirty`) → never `pending`. Mid-edit work, before anything
  has been committed anywhere, is normal and must not be flagged. This is why the rule is specifically
  "Git clean, Muse dirty," not "Muse dirty."
- `muse-only` / `git-only` regimes → always `not_applicable`, never `pending` or `unreadable`.

---

## §KH2.5 — Wiring: three fail-closed choke points (frozen)

All three reuse the **existing exit code `2`** — the tier `not substrate_ok` already occupies in
each surface today. No new exit code is introduced; no existing exit-code tier is renumbered.

| Surface | Where the check runs | Behavior on `not ok` |
| --- | --- | --- |
| `overseer status --exit-code` | After `vcs_result = read_vcs_status(...)`, compute `muse_sync = check_muse_sync(config, vcs_result)`. Extend `_exit_code_from_conditions` with a `muse_sync_ok` input, OR'd into the existing top tier: `if config_error or not substrate_ok or not muse_sync_ok: return 2`. Plain `overseer status` (no `--exit-code`) still always exits `0` — unchanged human/JSON informational behavior, per the existing `use_exit_code` gate. | JSON payload gains a `muse_sync: {state, ok, message, remediation}` object (additive key); human mode prints `muse_sync: {state} — {message}` + a remediation line, mirroring the existing `substrate` warning block exactly. |
| `overseer review --freeze` | Immediately after the existing `status = adapter.status()` call (no extra adapter invocation — reuses the already-fetched `StatusResult`), before any review provider runs. | `ctx.output.error(f"muse_sync: {muse_sync.state} — {muse_sync.message}")` + remediation line; `return 2`. Mirrors the existing `substrate.ok` refusal exactly (same function, same early-return shape, same exit code). |
| `overseer governance-sync` | Inside `perform_verified_reads` (`tools/governance_hygiene/reads.py`), immediately after the existing `status = adapter.status()` call and its `ReadError` check (that call already happens right after the `check_substrate` gate, before R1/anchor/R3 are read) — reuses that same `StatusResult`, no extra adapter invocation. | Returns `ReadFailure("muse-sync", muse_sync.message, regime)` — the exact existing fail-closed return type this function already uses for substrate failures. `run_governance_sync` already maps any `ReadFailure` to `exit_code=2`; no change needed in `engine.py`. |

---

## §KH2.6 — Boundary: what this gate does and does not catch (frozen, stated plainly)

| Scenario | Caught? |
| --- | --- |
| Git commit lands; Muse untouched; `overseer status --exit-code` run before any further edits | **Yes** — the exact failure this phase was written to close. |
| Mid-session editing, nothing committed to either VCS yet | **No trigger** (by design — `git_dirty=True` suppresses `pending`; this is normal work, not a violation). |
| Git commit lands; Muse untouched; then a *further* uncommitted edit is made before the gate is ever run | **Not caught by this check alone** — `git_dirty` becomes `True` again, masking the still-outstanding Muse gap. Documented limitation (§KH2.1); a persisted Git-SHA anchor would be needed to close this fully and is deliberately out of scope for KH2. |
| `muse-only` or `git-only` regime | **Not applicable** — single-history regimes have no cross-VCS gap to detect. |
| GitHub `main` pushed directly, bypassing Muse (the opposite-direction Muse↔Git inversion) | **Not this gate's job** — already covered by `realign` / D2 drift detection (`tools/governance_hygiene/drift.py`), unchanged by KH2. |

This table is deliberately part of the frozen contract so KH2b's build — and anyone reading the
result later — cannot overstate what shipped.

---

## §KH2.7 — Config & regime interaction

No new config block. `muse_sync` activates automatically whenever `vcs.regime == "muse+git-mirror"`
in the already-loaded `.overseer/config.yaml` — consistent with how `substrate_health` also requires
no dedicated config flag. This keeps the gate on by default for the one regime it protects, with zero
new schema surface to document or drift.

---

## §KH2.8 — Seven-tier test matrix (KH2b Auto build must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | `StatusResult` accepts/defaults the two new fields without breaking existing positional/keyword construction; `check_muse_sync` resolution table (§KH2.4) for all four states, including both frozen non-triggers (`git_dirty=True` never yields `pending`; non-`muse+git-mirror` regimes always `not_applicable`). |
| **integration** | `MuseGitMirrorAdapter.status()` populates `muse_dirty`/`git_dirty` from injected `muse status --json` / `git status --porcelain` command output; `MuseOnlyAdapter`/`GitOnlyAdapter` populate exactly one of the two fields per §KH2.3; `overseer status --json --exit-code` returns `2` with a `muse_sync` payload when `muse_dirty=true, git_dirty=false`, and `0` when synced. |
| **e2e** | Full cycle on a fixture repo: git commit lands (simulated clean `git status --porcelain`) with Muse still dirty → `overseer review --freeze` refuses with exit `2` and a `muse_sync` message; `overseer governance-sync` (dry-run) refuses with exit `2` and `error_command="muse-sync"`; after a simulated `muse commit` (both dirty flags false), the same three commands proceed normally. |
| **stress** | Large simulated repo status calls (many files reported by `muse status --json` / `git status --porcelain`) resolve `check_muse_sync` in bounded time — the check only inspects two booleans, never a per-file diff, so cost is O(1) regardless of file count. |
| **data-integrity** | `check_muse_sync` is a pure function of `(regime, muse_dirty, git_dirty)` — identical inputs always yield an identical `MuseSyncReport`; no partial state, no I/O inside the function itself. |
| **performance** | `overseer status --exit-code` with the new check adds no additional adapter/shell invocation (reuses the already-fetched `StatusResult`) — no measurable overhead over the pre-KH2 baseline. |
| **security** | No new command execution surface is introduced (the two booleans come from calls the adapter already made); remediation text is a static, non-executed string (never shell-invoked by the kit itself); no secret/identity leakage in the new `muse_sync` payload or messages; fail-closed on `unreadable` rather than optimistically reporting `synced`. |

---

## §KH2.9 — Close-out (execute only when KH2 marked DONE)

1. Freeze-review `pass` recorded in the Review record table above (stamp written by
   `overseer review --freeze`).
2. ROADMAP KH2a row: freeze **DONE**; KH2b (Auto build) row added against this contract.
3. Handover NEXT flips to KH2b with a paste-ready prompt + the mandatory governance-gate reminders,
   once KH2b itself is complete in the same session, flips onward to the next queued slice.
4. Governance sync: `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together in the same
   commit (SD-17).
