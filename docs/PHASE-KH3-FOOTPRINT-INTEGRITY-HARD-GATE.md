# Phase KH3 — Footprint self-integrity hard gate (Thinking freeze)

Status: **Reviewed → `pass` (KH3-r2).** KH3a is **spec-only** and now frozen; no code lands in this
phase. KH3b (Auto) is cleared to build mechanically against this frozen contract; it is the only
phase that writes files.

```yaml
phase: KH3
outputs:
- id: kh3-footprint-integrity-hard-gate
  path: docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md
  frozen: true
frozen_inputs:
- id: footprint-integrity-impl
  path: cli/commands/status.py
- id: substrate-health-impl
  path: tools/substrate_health/check.py
- id: muse-sync-impl
  path: tools/muse_sync/check.py
- id: version-lock-origin
  path: cli/version_lock.py
- id: footprint-resolver
  path: cli/footprint.py
- id: cli-review-freeze
  path: cli/commands/review.py
- id: governance-hygiene-reads
  path: tools/governance_hygiene/reads.py
- id: kh2-hard-gate-precedent
  path: docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md
- id: k7-dogfood-seed-rule
  path: docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
review_stamp:
  reviewed_at: '2026-07-13T07:42:05Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:4ad2c03864f7e6935d134d92fea11506dcd7e6bf287bb153c254a640b9452267
```

**Downstream edge:** KH3b treats this document as ground truth without re-deriving it (SPEC §6
mandatory reviewed freeze). It follows the exact `tools/substrate_health/` / `tools/muse_sync/`
family shape KH1b and KH2 already shipped — this contract governs one additive detection + wiring
slice, not a redesign of either predecessor.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| KH3-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist gate clean (0 findings). Semantic review raised one non-escalating MAJOR scope-risk finding: **R1-M1** (§KH3.1 initial draft trigger was "any kit-owned digest mismatch," which would fail-close `review --freeze`/`governance-sync` for *any* consumer repo whose kit-owned files have ever legitimately drifted from a stale lock hash — the exact false-positive class this same session just hit on `scripts/muse-bridge-deploy.sh`). Fixed: narrowed the frozen trigger to **kit-owned-and-declared-but-absent-from-disk only** (§KH3.4) — content-hash drift stays on the existing opt-in `--check-footprint` path, unchanged. |
| KH3-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read confirmed R1-M1 RESOLVED — trigger condition in §KH3.4 is unambiguously "declared in `version.lock` with `origin` other than `preserved`, and absent from disk," which cannot be true for any repo that has ever successfully run `overseer sync`; re-verified the three wiring points against the current `cli/commands/status.py` / `cli/commands/review.py` / `tools/governance_hygiene/reads.py` call order; exit-code reuse (`2`) does not renumber the frozen `2 > 6 > 3 > 0` `status` precedence; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (gate targets Tier-1 CLI read surfaces). Stamp written by `overseer review --freeze`. |

---

## §KH3.0 — Simple summary

This kit's whole job is catching drift before it becomes a silent, permanent gap. It just found one
in itself: for three days, this very repo's own tracking file said "these 13 rule and policy files
should exist" while none of them actually did — and nothing that runs automatically ever said a
word, because the one check that could have caught it only runs when someone remembers to ask for it
by hand.

**KH3 closes that gap with a hard, fail-closed check**, not an opt-in flag anyone can forget to
pass: whenever the kit's own tracking file says a file it owns should exist, and that file is
completely absent from the working tree, the kit's own commands (`status --exit-code`,
`review --freeze`, `governance-sync`) refuse to say everything is fine — the same way they already
refuse when MuseHub falls behind Git (KH2) or when Muse's metadata is hollow (KH1b). It deliberately
does **not** fire on files that merely *differ* in content from a stale recorded hash — that softer
case stays on the existing opt-in `overseer status --check-footprint` path, so repos that have
legitimately customized a kit-owned file (and haven't yet marked it `preserved`) are not suddenly
broken by this phase.

**Technical summary:** add a new `tools/footprint_integrity/` probe, sibling to
`tools/substrate_health/` and `tools/muse_sync/`, exposing `FootprintIntegrityReport` and
`check_footprint_integrity(config, repo_root, kit=None)`. It resolves the current footprint
(`cli/footprint.py::resolve_footprint`), reads `.overseer/version.lock`, and — for every
lock-declared, non-`preserved` (`origin: kit` or omitted) destination — checks only whether the
file **exists on disk**. Any absence yields `state="missing"` (not `ok`); an unreadable lock is
`state="unreadable"` (fail closed); everything present is `state="ok"`. This is a strict subset of
the existing `_compute_footprint_integrity` logic in `cli/commands/status.py` — it never looks at
byte content or hashes, only existence — which is exactly why it is safe to run unconditionally
without the false-positive risk a full content-digest check would carry for repos with legitimate,
not-yet-`preserved` customizations. Wire `check_footprint_integrity` into the same three fail-closed
choke points KH1b/KH2 already use — `overseer status --exit-code`, `overseer review --freeze`,
`overseer governance-sync` — all returning the existing exit code `2`.

---

## §KH3.1 — Scope

**In scope (freeze only — this phase writes no code):**

- The `FootprintIntegrityReport` shape and the `check_footprint_integrity` resolution rule (§KH3.4).
- The three wiring points and the exact exit-code treatment (§KH3.5).
- The precise boundary of what this gate does and does not catch, stated plainly so it is never
  oversold (§KH3.6).
- The seven-tier test matrix KH3b must satisfy (§KH3.8).

**Out of scope (explicit non-goals — prevent creep):**

- **Making the existing `overseer status --check-footprint` full content-digest check run by
  default.** That check compares byte-for-byte content against recorded hashes and would fail-close
  on *any* kit-owned file a consumer has customized without yet marking `origin: preserved` — a real,
  live false-positive risk this same session hit directly (`scripts/muse-bridge-deploy.sh`'s stale
  hash, `docs/ROADMAP.md`/`docs/OVERSEER-HANDOVER.md` before reclassification). Flipping that check's
  default posture is a materially different, higher-blast-radius decision affecting every existing
  consumer install (Scooling, Knowtation, VideoFactory per prior pilots) and is explicitly deferred to
  a future, separately-scoped phase if ever pursued.
- **Automatically running `overseer sync` on the operator's behalf.** This gate only detects and
  refuses; it never writes files for anyone. Seeding missing files is a decision a human or an
  explicitly-invoked `overseer sync` action makes, never a side effect of a read-only status/gate
  check.
- **Any change to `overseer sync`'s own conflict/classification logic** (`cli/sync_classify.py`,
  `cli/commands/sync.py`). KH3 is a new *read-only detector*, wired into existing choke points; it
  does not alter how `sync` decides to write, seed, or refuse.
- **Any change to the `origin: preserved` mechanism** (§K6.4). KH3 respects it exactly as-is —
  preserved entries are never checked for existence by this gate, mirroring how they are already
  excluded from the digest in `_compute_footprint_integrity`.
- **Redefining the frozen `status --exit-code` precedence order.** KH3 reuses exit code `2` — the
  same tier `substrate_ok`/`muse_sync_ok` already occupy — rather than inserting a new tier into
  `2 > 6 > 3 > 0`.

---

## §KH3.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Footprint content-integrity check | `_compute_footprint_integrity(repo_root, lock, rendered)` recomputes a kit-only digest over **all** non-`preserved` entries and compares to `lock.footprint_digest`; a single missing OR content-differing file both collapse into one `"mismatch"` outcome with no distinction | `cli/commands/status.py` |
| That check's activation | Only computed when `args.check_footprint` is `True` — an opt-in CLI flag, unlike `substrate`/`muse_sync` which are always computed | `cli/commands/status.py::run_status` |
| That check's wiring | **Not referenced anywhere** in `cli/commands/review.py` or `tools/governance_hygiene/reads.py` — confirmed by direct search; `overseer review --freeze` and `overseer governance-sync` currently have zero awareness of footprint state | `cli/commands/review.py`, `tools/governance_hygiene/reads.py` |
| `origin: preserved` semantics | Lock entries whose `origin` resolves to `preserved` are excluded from the kit-only digest entirely (`compute_lock_digest`); this is the correct mechanism for legitimate living-doc / consumer-customized content, already exercised by KH3's own predecessor hygiene fix this session | `cli/version_lock.py` |
| `resolve_footprint` | Deterministic, pure function of `(config, kit_root)` — enumerates every destination the kit currently expects to exist, given the active regime and config; already used by both `status` and `sync` | `cli/footprint.py` |
| `MISSING` vs `BOTH_CHANGED` classification | `overseer sync`'s own classifier (`cli/sync_classify.py`) already distinguishes `MISSING` (absent from disk) from `BOTH_CHANGED`/`CONSUMER_MODIFIED` (present but differs) — this distinction exists in `sync` today but has no equivalent in `status`'s digest check, which conflates both into one `"mismatch"` bit | `cli/sync_classify.py` |
| `substrate_health` / `muse_sync` wiring pattern (frozen precedent) | Both are always computed (no opt-in flag), both check exactly one existing `StatusResult`/filesystem read with no extra I/O, both wired identically into `status.py` (`_exit_code_from_conditions`), `review.py` (early return `2` before any provider runs), and `governance_hygiene/reads.py` (`ReadFailure` mapped to exit `2`) | `tools/substrate_health/check.py`, `tools/muse_sync/check.py`, `cli/commands/review.py`, `tools/governance_hygiene/reads.py` |
| Live incident this gate is a direct response to | K4b (`042ac5c`, 2026-07-10) hand-authored 13 `version.lock` footprint entries for `.cursor/rules/*`, `.cursor/skills/*/SKILL.md`, `.overseer/policy/*.yaml`, `.overseer/STANDING-DECISIONS.reference.md` without ever running `overseer init`/`sync` against this dogfood repo; the gap survived 3 days and 20 merged PRs undetected because no default-on check distinguishes "declared and absent" from "everything's fine" | This session's own hygiene investigation, fixed via `overseer sync --yes` (PR #20) |

KH3 **must not** change `_compute_footprint_integrity`'s existing opt-in content-digest behavior,
`overseer sync`'s classifier, the `origin: preserved` mechanism, or the frozen `status` exit-code
ordering. It only **adds** one new read-only probe module and additive checks at three existing
fail-closed choke points, scoped strictly to file-existence.

---

## §KH3.3 — Why "missing" only, never "content differs" (frozen scope boundary)

This is the single most important design decision in this contract, and it is frozen precisely
because getting it wrong has real blast radius across every consumer of this kit, not just this
dogfood repo:

| Trigger considered | Verdict | Reason |
| --- | --- | --- |
| Any kit-owned file whose on-disk content differs from its recorded `version.lock` hash | **Rejected** (R1-M1, fixed in KH3-r2) | A consumer repo can legitimately have a kit-owned file that has drifted from a stale lock hash for entirely benign reasons — exactly what this session found for `scripts/muse-bridge-deploy.sh` (a fresh render was byte-identical to disk; only the *lock's* recorded hash was stale) and for `docs/ROADMAP.md`/`docs/OVERSEER-HANDOVER.md` before their `origin: preserved` reclassification. Fail-closing `review --freeze`/`governance-sync` on this condition by default would immediately risk breaking any existing pilot install (Scooling, Knowtation, VideoFactory) the first time it hits an equally benign, already-existing drift — with no opportunity for the operator to triage first, because these are hard refusals, not warnings. |
| A kit-owned, non-`preserved` file declared in `version.lock` that is **completely absent** from disk | **Adopted (frozen trigger)** | There is no legitimate reason for this state to persist. It cannot arise from a customization (customizing a file requires the file to exist). It can only arise from (a) `overseer init`/`sync` never having been run for that destination — this session's exact incident — or (b) the file having been deleted after install. Both are unambiguous action items (`overseer sync`), never a decision a consumer would want to defer indefinitely. |

This means KH3's gate and the existing `--check-footprint` content-digest gate are **complementary,
non-overlapping** safety nets: KH3 is the always-on floor ("nothing the kit promised is silently
absent"); `--check-footprint` remains the opt-in, more thorough ceiling ("nothing the kit promised
has silently changed either") for operators who want it, unchanged by this phase.

---

## §KH3.4 — `FootprintIntegrityReport` + `check_footprint_integrity` (frozen)

New module `tools/footprint_integrity/` (sibling package to `tools/substrate_health/` and
`tools/muse_sync/`, same shape for consistency):

```python
@dataclass(frozen=True)
class FootprintIntegrityReport:
    state: str  # ok | missing | unreadable
    message: str
    remediation: str | None
    missing: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.state == "ok"


def check_footprint_integrity(
    config: OverseerConfig,
    repo_root: Path,
    *,
    kit: Path | None = None,
) -> FootprintIntegrityReport:
    ...
```

**Resolution rule (frozen, evaluated in this order):**

1. `.overseer/version.lock` cannot be read/parsed (`LockError`) → `state="unreadable"` — fail closed,
   mirroring the existing `unreadable` treatment in `check_muse_sync` §KH2.4 and the existing
   `lock_error` handling already present in `cli/commands/status.py`.
2. `resolve_footprint(config, kit=kit)` raises `ConfigError` → `state="unreadable"` (same fail-closed
   posture; a config that cannot resolve its own footprint cannot prove anything is present).
3. For every resolved `FootprintFile`, look up its `version.lock` entry (if any) and resolve its
   `origin` via the existing `entry_origin` helper (default `"kit"` when the entry is absent or the
   field is omitted, per current `cli/version_lock.py` semantics). **Skip** any entry whose origin is
   `"preserved"` — never check existence for those (mirrors §K6.4 exactly; a preserved living doc that
   somehow doesn't exist yet is `sync`'s / the operator's concern, not this gate's).
4. Among the remaining (`kit`-origin) entries, collect every destination whose absolute path
   (`repo_root / destination`) is **not** an existing file. If that set is non-empty →
   `state="missing"`, `missing=` the sorted tuple of those destinations, `message` names the count and
   lists them, `remediation="overseer sync"`.
5. Otherwise → `state="ok"`.

**Frozen non-triggers (must not fire — this is the false-positive guard, per §KH3.3):**

- A file that **exists** but whose content differs from its recorded hash → never `missing`. This
  gate performs no hashing and reads no file content at all beyond an existence check
  (`Path.is_file()`); it is a strict subset of `_compute_footprint_integrity`'s existing logic.
- Any entry whose resolved `origin` is `"preserved"` → never checked, regardless of whether it exists.
- A destination that `resolve_footprint` does not currently produce for the active `config.vcs.regime`
  (e.g. `MUSE-BRIDGE-WORKFLOW.md` / `scripts/muse-bridge-deploy.sh` when the regime is not
  `muse+git-mirror`) → never considered, because it is never in the resolved set to begin with — this
  is unchanged, existing `resolve_footprint` regime-conditional behavior (§K7.2.3).
- A brand-new repo before its first `overseer init` (`.overseer/` directory absent entirely) → this
  gate is never reached; `run_status`/`run_review`/`perform_verified_reads` all already return early
  (`initialized: false` / `"not initialized"` / equivalent) before any footprint or substrate check
  runs, unchanged by KH3.

---

## §KH3.5 — Wiring: three fail-closed choke points (frozen)

All three reuse the **existing exit code `2`** — the tier `not substrate_ok` / `not muse_sync_ok`
already occupy in each surface today. No new exit code is introduced; no existing exit-code tier is
renumbered.

| Surface | Where the check runs | Behavior on `not ok` |
| --- | --- | --- |
| `overseer status --exit-code` | Unconditionally (no flag needed), immediately after the existing `lock`/`rendered` resolution already performed for drift/footprint computation — reuses the already-loaded `config`/`lock`/`rendered` values, no extra filesystem walk beyond the `Path.is_file()` checks §KH3.4 already requires. Extend `_exit_code_from_conditions` with a `footprint_integrity_ok` input, OR'd into the existing top tier: `if config_error or not substrate_ok or not muse_sync_ok or not footprint_integrity_ok: return 2`. Plain `overseer status` (no `--exit-code`) still always exits `0` — unchanged human/JSON informational behavior. The existing opt-in `--check-footprint` content-digest check and its own exit-`6` tier are **unchanged and independent** of this new always-on existence check. | JSON payload gains a `footprint_self_integrity: {state, ok, message, remediation, missing}` object (additive key, distinct from the existing `footprint_integrity` string key so the two checks are never confused); human mode prints `footprint_self_integrity: {state} — {message}` + a remediation line, mirroring the existing `substrate`/`muse_sync` warning blocks exactly. |
| `overseer review --freeze` | Immediately after the existing `muse_sync` check (after `check_substrate`, after `adapter.status()`/`ReadError` check, after `check_muse_sync`), before any review provider runs. | `ctx.output.error(f"footprint_self_integrity: {report.state} — {report.message}")` + remediation line; `return 2`. Mirrors the existing `substrate.ok`/`muse_sync.ok` refusal exactly (same function, same early-return shape, same exit code). |
| `overseer governance-sync` | Inside `perform_verified_reads` (`tools/governance_hygiene/reads.py`), immediately after the existing `check_muse_sync` check (which itself runs right after `check_substrate` and the `adapter.status()`/`ReadError` check). | Returns `ReadFailure("footprint-self-integrity", report.message, regime)` — the exact existing fail-closed return type this function already uses. `run_governance_sync` already maps any `ReadFailure` to `exit_code=2`; no change needed in `engine.py`. |

---

## §KH3.6 — Boundary: what this gate does and does not catch (frozen, stated plainly)

| Scenario | Caught? |
| --- | --- |
| A kit-owned file declared in `version.lock` (non-`preserved`) is completely absent from disk | **Yes** — the exact failure this phase was written to close (this session's own incident). |
| A kit-owned file exists but its content differs from the recorded lock hash (stale hash, template updated upstream, or a genuine hand-edit not yet marked `preserved`) | **Not caught by this gate** — by design (§KH3.3). Remains available via the existing opt-in `overseer status --check-footprint` (exit `6`), unchanged. |
| A living doc / consumer customization correctly marked `origin: preserved` that happens to be deleted from disk | **Not caught by this gate** — preserved entries are never existence-checked (§KH3.4 step 3); this is intentionally the operator's/`sync`'s domain, mirroring how preserved entries are already excluded from the digest. |
| A destination `resolve_footprint` does not produce for the current regime (e.g. bridge files outside `muse+git-mirror`) | **Not applicable** — never in the checked set to begin with. |
| Before the first `overseer init` on a fresh repo | **Not applicable** — the surrounding command already returns before any footprint/substrate check runs. |
| `version.lock` itself is missing, corrupt, or unparseable | **Caught as `unreadable`** — fail-closed, not silently treated as `ok`. |

This table is deliberately part of the frozen contract so KH3b's build — and anyone reading the
result later — cannot overstate what shipped.

---

## §KH3.7 — Config & regime interaction

No new config block. `check_footprint_integrity` activates automatically for every regime once
`.overseer/` is initialized — consistent with how `substrate_health` and `muse_sync` also require no
dedicated config flag (each simply becomes `not_applicable`/vacuously `ok` where irrelevant — here,
vacuously `ok` whenever `resolve_footprint` yields no non-`preserved` destinations, e.g. a config
with zero policy/rule files declared). This keeps the gate on by default with zero new schema
surface to document or drift.

---

## §KH3.8 — Seven-tier test matrix (KH3b Auto build must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | `check_footprint_integrity` resolution table (§KH3.4) for all three states (`ok`, `missing`, `unreadable`), including every frozen non-trigger: an existing-but-content-differing file never yields `missing`; a `preserved`-origin entry that is absent from disk never yields `missing`; a destination outside the active regime's resolved set is never considered; a missing/corrupt `version.lock` yields `unreadable`, not `ok`. |
| **integration** | `overseer status --json --exit-code` returns `2` with a `footprint_self_integrity` payload when a fixture declares a kit-owned destination absent from disk, and `0`/`ok` when every kit-owned destination is present; `overseer review --freeze` and `overseer governance-sync --dry-run` each refuse with exit `2` under the same fixture condition and proceed normally once the file is present; confirm the existing opt-in `--check-footprint` content-digest behavior and its exit-`6` tier are byte-for-byte unchanged by this phase (regression-guard against §KH3.1's explicit non-goal). |
| **e2e** | Full cycle on a fixture repo: `overseer init` → delete one kit-owned rendered file → `overseer status --exit-code` (exit `2`) → `overseer review --freeze` (exit `2`, `footprint_self_integrity` message) → `overseer governance-sync --dry-run` (exit `2`, `error_command="footprint-self-integrity"`) → `overseer sync --yes` restores the file → all three commands proceed normally (exit `0`) on the same fixture, no further changes. |
| **stress** | A fixture with a large number of declared footprint destinations (hundreds of policy/rule files) resolves `check_footprint_integrity` in bounded time — the check performs one `Path.is_file()` per resolved destination and no hashing, so cost is linear in destination count only, never in file size. |
| **data-integrity** | `check_footprint_integrity` is a pure function of `(config, repo_root, kit, on-disk existence, lock contents)` at call time — identical filesystem state always yields an identical `FootprintIntegrityReport`; running it twice with no intervening writes produces byte-identical `missing` tuples in the same sorted order. |
| **performance** | `overseer status --exit-code` with the new check adds no additional shell/adapter invocation — the existing `lock`/`rendered` values already computed for footprint/drift purposes are reused; the added cost is bounded to the number of resolved destinations' `Path.is_file()` calls, negligible versus the existing baseline. |
| **security** | No new command execution surface (existence checks are pure filesystem stats, never shell-invoked); remediation text (`"overseer sync"`) is a static, non-executed string; no secret/identity leakage in the new `footprint_self_integrity` payload or messages (destinations only — no file contents are ever read by this gate); fail-closed on `unreadable` rather than optimistically reporting `ok`. |

---

## §KH3.9 — Close-out (execute only when KH3 marked DONE)

1. Freeze-review `pass` recorded in the Review record table above (stamp written by
   `overseer review --freeze`).
2. ROADMAP KH3a row: freeze **DONE**; KH3b (Auto build) row added against this contract.
3. Handover NEXT flips to KH3b with a paste-ready prompt + the mandatory governance-gate reminders,
   once KH3b itself is complete in the same session, flips onward to the next queued slice.
4. Governance sync: `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together in the same
   commit (SD-17).
