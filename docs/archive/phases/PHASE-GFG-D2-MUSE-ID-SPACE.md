# Phase GFG-D2-FIX — muse+git-mirror D2 ID-space (Thinking freeze)

Status: **Reviewed → `pass` (D2F-r2).** GFG-D2-FIX-a is **spec-only** and now frozen; no product
code lands in this Thinking close. GFG-D2-FIX-b (Auto) is cleared to build mechanically against
this contract.

```yaml
phase: GFG-D2-FIX
outputs:
- id: gfg-d2-muse-id-space
  path: docs/archive/phases/PHASE-GFG-D2-MUSE-ID-SPACE.md
  frozen: true
frozen_inputs:
- id: gfg-freshness-gate
  path: docs/archive/phases/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md
- id: hygiene-outline-d2
  path: docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: drift-detect-d2
  path: tools/governance_hygiene/drift.py
- id: muse-git-mirror-adapter
  path: adapters/muse_git_mirror/adapter.py
- id: adapter-bridge-helpers
  path: adapters/base.py
- id: realign-guard
  path: tools/governance_hygiene/realign.py
- id: verified-reads
  path: tools/governance_hygiene/reads.py
review_stamp:
  reviewed_at: '2026-07-28T15:50:11Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:3148c577ef724f456d1b9da88564a301f4280783f76040c0fae7c94e4eaf7cac
```

**Downstream edge:** GFG-D2-FIX-b treats this document as ground truth. It amends the **R2 ID space**
used by D2 (and realign verify) under Muse 0.2.x content-addressed tips. It does **not** reopen GFG
fail-closed wiring, marker rules, Automation templates, or exit-code precedence. It does **not**
make `git-import` into Muse main the default dogfood recovery path.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| D2F-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R1-M1** §D2F.4.2 mirror-ref fallback was underspecified (could still return a git tip compared to `sha256:` R3). Tightened: if `[last_export]` exists without `muse_commit_id` → `ReadError`; mirror-ref fallback only when `[last_export]` section absent. **R1-M2** §D2F.5 must cite `plan_realign` using `reads.r2_anchor_sha` for ancestry (`realign.py` lines 25–29) so Auto replaces that call site with R2_git. Fixed. |
| D2F-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings, dry-run). Semantic re-read: R1-M1/R1-M2 RESOLVED; §D2F.3 ID-space rule matches live Scooling bridge evidence; realign ancestry/verify split precise; non-goals hold (no freshness default-off, no default git-import dogfood); no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §D2F.0 — Simple summary

Overseer checks whether the Muse↔Git bridge still matches Muse’s main tip. That check was comparing
the **Git** export SHA (a 40-character hex string) to Muse’s tip (a `sha256:…` content hash). Those
are different ID systems, so a healthy bridge always looked “drifted,” and the tool offered to import
GitHub history into Muse — the wrong default on a working consumer.

**This phase freezes the correct comparison:** under `muse+git-mirror`, D2 is aligned when the
bridge’s **`last_export.muse_commit_id`** equals Muse main tip (same ID space). The Git export SHA
stays for realign ancestry / `from_ref` only. Realign verification must use the Muse ID, not
`git_sha == muse tip`.

**Technical summary:** amend `read_canonical_anchor` (and D2/realign consumers of R2) so R2 for
`muse+git-mirror` is `last_export.muse_commit_id` from `.muse/git-bridge.toml`. Keep
`read_bridge_git_sha` for `realign()` `from_ref` and the Git ancestry/superset precondition. Fail
closed when `muse_commit_id` is absent. Do not silent-default-off `governance_freshness`.

---

## §D2F.1 — Verified incident (do not redesign around folklore)

Live Scooling (2026-07-28, post GFG `ok sync`):

| Field | Value |
| --- | --- |
| `last_export.git_sha` | `1e734a922a8de5dcac248007b8dfb706c4a0f84e` (40-hex) |
| `last_export.muse_commit_id` | `sha256:67001f71f4481906b1bad7a9f46ccf61f9113c44a6cf64473416c4c77a8b6116` |
| `muse rev-parse main` | `sha256:67001f71f4481906b1bad7a9f46ccf61f9113c44a6cf64473416c4c77a8b6116` |
| D1 | `aligned` (handover claim fixed) |
| D2 (broken) | `drifted` permanently — compares `git_sha` to Muse tip |
| Bridge health | `muse_commit_id == muse tip` (healthy export) |
| Dry-run realign | offered `muse bridge git-import` with `would_import=47` — correctly withheld on consumer (Tier 3 / SD-14) |

**Root cause (code):**

1. `adapters/muse_git_mirror/adapter.py` `read_canonical_anchor` (lines 63–66) returns
   `read_bridge_git_sha(..., "last_export")` — Git ID space.
2. `tools/governance_hygiene/drift.py` `_detect_d2` (lines 55–60) equates
   `r2_anchor_sha` to `r3_canonical_main_sha` (Muse tip, `sha256:…`).
3. `tools/governance_hygiene/realign.py` verify (lines 85–86) demands
   `anchor.anchor_sha == muse tip` — same cross-ID false fail after a real import.
4. `adapters/base.py` `read_bridge_git_sha` (lines 164–183) only parses `git_sha`; no
   `muse_commit_id` reader exists.

GFG itself is correct to fail-closed on D2 drift. The D2 **predicate** is wrong under Muse 0.2.x.

---

## §D2F.2 — Scope

**In scope (freeze only — this Thinking phase writes no product code):**

- Correct D2 alignment predicate for `muse+git-mirror` under Muse content-hash tips (§D2F.3).
- Bridge field roles: `muse_commit_id` vs `git_sha` (§D2F.4).
- Realign plan/verify amendments so healthy bridges do not plan `git-import`, and verify does not
  demand `git_sha == muse tip` (§D2F.5).
- Fail-closed rules when `muse_commit_id` is missing (§D2F.6).
- Auto deliverables + seven-tier matrix (§D2F.8–§D2F.9).
- Explicit non-goals (§D2F.7).

**Out of scope:**

| Non-goal | Why rejected |
| --- | --- |
| Silent default-off for `governance_freshness` | Recreates the GFG incident floor hole (§GFG.8.1). |
| Making `git-import` into Muse main the default dogfood “fix” | SD-14 / Tier 3; healthy bridges must not look drifted. |
| Redefining D1, D3, marker format, Automation templates, exit codes | GFG freeze stays; this is an R2 ID-space amendment only. |
| Equating `git_sha` to Muse tip via hash translation tables | No stable bijection; inventing one is dishonest. |
| Consumer posture/env flips; kit `main` merge | Tier 3 / out of Auto. |
| Rewriting Muse bridge export tooling | Kit consumes `.muse/git-bridge.toml`; does not own Muse. |

---

## §D2F.3 — Frozen D2 rule (`muse+git-mirror`)

Let:

- **R3** = Muse main tip from `adapter.read_head("muse:<muse.main_branch>")` (today:
  `sha256:…` under Muse 0.2.x).
- **R2_muse** = `.muse/git-bridge.toml` → `[last_export].muse_commit_id` (string, case-normalized
  for comparison).
- **R2_git** = `.muse/git-bridge.toml` → `[last_export].git_sha` (40-hex), used **only** for
  realign `from_ref` / Git ancestry — **never** for D2 equality against R3.

**D2 resolution for `muse+git-mirror` (frozen):**

1. If R3 is unreadable → D2 `unreadable`.
2. If `muse_commit_id` is missing/empty in `[last_export]` → D2 `unreadable` (fail-closed).
   Do **not** fall back to comparing `git_sha` to R3.
3. Else if `normalize(R2_muse) == normalize(R3)` → D2 `aligned`.
4. Else → D2 `drifted`.

**Regression locked:** when `muse_commit_id == R3` and `git_sha ≠ R3` (the permanent healthy-bridge
case under Muse content hashes), D2 MUST be `aligned`. That inequality alone is **not** drift.

**Other regimes (unchanged):**

| Regime | D2 rule |
| --- | --- |
| `git-only` | Existing: R2 (git tip / origin/main) vs R3 (same ID space). |
| `muse-only` | Existing: R2 is Muse tip via adapter; equals R3 when readable. |

---

## §D2F.4 — Frozen adapter / read surface

### §D2F.4.1 — `read_bridge_muse_commit_id`

Add `adapters/base.py` helper (sibling to `read_bridge_git_sha`):

- Read `.muse/git-bridge.toml` section `last_export` or `last_import` as requested.
- Parse `muse_commit_id = "…"` (TOML string; accept `sha256:…` and any future Muse id form that
  is a non-empty quoted string).
- Return `None` when file/section/key absent.

### §D2F.4.2 — `read_canonical_anchor` (`muse+git-mirror`)

Amend `MuseGitMirrorAdapter.read_canonical_anchor` (`adapters/muse_git_mirror/adapter.py`
lines 63–79):

1. If `.muse/git-bridge.toml` has a `[last_export]` section:
   - Read `muse_commit_id` via `read_bridge_muse_commit_id(repo, "last_export")`.
   - If present and non-empty →
     `AnchorResult(anchor_sha=<muse_commit_id>,
     source=".muse/git-bridge.toml:last_export.muse_commit_id")`.
   - If missing/empty → `ReadError("read_canonical_anchor",
     "missing last_export.muse_commit_id")` — **fail-closed**. Do **not** return `git_sha`.
2. Else (no `[last_export]` section): keep today’s mirror-ref fallback
   (`{remote}/{mirror_branch}` git tip) when readable; else the existing
   “no bridge anchor…” `ReadError`.
3. Never return `git_sha` as `anchor_sha` when `[last_export]` exists.

**Frozen intent:** after Auto, R2 flowing into `VerifiedReads.r2_anchor_sha` for
`muse+git-mirror` with a live `[last_export]` bridge is the Muse ID (`muse_commit_id`), so
existing `_detect_d2` equality against R3 (`drift.py` lines 55–60) becomes correct. Auto may
instead keep a dual-field design if and only if it still satisfies §D2F.3 bit-for-bit.

### §D2F.4.3 — `git_sha` retention

- `read_bridge_git_sha` remains; `realign()` continues to use it for `from_ref`.
- `plan_realign` / `_github_superset_of_anchor` MUST use **R2_git** (`git_sha`), never the Muse
  content-hash R2, for `git merge-base --is-ancestor`.

---

## §D2F.5 — Frozen realign plan / verify

Amend `tools/governance_hygiene/realign.py`:

1. **Plan trigger:** still “only when D2 drifted” (9A-5 §5; `plan_realign` lines 19–20).
   After §D2F.3, a healthy bridge (`muse_commit_id == muse tip`) yields D2 aligned →
   **skip realign** (no `git-import` plan).
2. **Superset precondition:** today `plan_realign` passes `reads.r2_anchor_sha` into
   `_github_superset_of_anchor` (lines 25–29). After §D2F.4.2 that field is a Muse ID and
   **must not** be fed to `git merge-base --is-ancestor`. Auto MUST pass **R2_git**
   (`read_bridge_git_sha(..., "last_export")` or equivalent) as the ancestry argument.
   If R2_git is missing when D2 is drifted → withhold realign with a clear reason (operator
   required); do not invent a Muse-ID ancestry check.
3. **Verify after apply:** today lines 85–86 compare `anchor.anchor_sha` to Muse tip. After
   §D2F.4.2 that comparison is Muse-ID equality (correct). Forbidden: reintroducing
   `git_sha == muse tip` as the verify predicate.

**Hard stop retained:** Auto/apply realign into Muse main remains operator-gated on consumers
(Tier 3 / SD-14). This phase stops the **false** plan on healthy bridges; it does not auto-apply
imports.

---

## §D2F.6 — Fail-closed honesty

| Condition | Result |
| --- | --- |
| `muse_commit_id` missing under `muse+git-mirror` with bridge present | D2 / anchor read `unreadable` — not optimistic `aligned` |
| `muse_commit_id` ≠ Muse tip | D2 `drifted` — genuine bridge lag / inversion signal |
| `muse_commit_id` == Muse tip, `git_sha` ≠ Muse tip | D2 `aligned` |
| Unreadable Muse tip | D2 `unreadable` |
| Turning off governance freshness to green status | **Forbidden** |

---

## §D2F.7 — Boundary / rejection table

| Scenario | After this fix |
| --- | --- |
| Healthy Scooling bridge (`muse_commit_id == tip`) | D2 aligned; dry-run may stamp marker; `status --exit-code` → 0 when D1+marker ok |
| False realign plan (`would_import=N`) on healthy bridge | **Must not** appear solely because `git_sha ≠ tip` |
| True Muse tip ahead of last export’s `muse_commit_id` | D2 drifted (real) |
| GitHub-only history ahead; operator wants Muse catch-up via import | Still Tier 3 / SD-14; realign path remains available when D2 truly drifted + superset holds |
| Equate git SHA to sha256 tip | **Rejected** |

---

## §D2F.8 — Auto deliverables (exact)

1. `read_bridge_muse_commit_id` in `adapters/base.py`.
2. Amend `MuseGitMirrorAdapter.read_canonical_anchor` per §D2F.4.2.
3. Amend `plan_realign` / `execute_realign_guard` per §D2F.5 (git_sha for ancestry; Muse ID for verify).
4. Ensure `_detect_d2` + freshness probe inherit correct R2 (via anchor read and/or explicit
   muse+git-mirror branch that still matches §D2F.3).
5. Update fixtures that assumed `git_sha`-as-anchor for muse+git-mirror to include
   `muse_commit_id` matching the fixture Muse tip where D2 aligned is expected.
6. Seven-tier tests per §D2F.9 (unit/integration/e2e minimum named below).
7. `/build-verification-review` → `pass` before ROADMAP → DONE.
8. Update `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` together; feature-branch commit.
   NEXT after land = consumer re-stamp (Scooling first): `ok sync` →
   `ok governance-sync --dry-run` → `ok status --exit-code` → `0`.

---

## §D2F.9 — Seven-tier test matrix (Auto must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | D2 `aligned` when `muse_commit_id == sha256:…` tip and `git_sha` is a different 40-hex; D2 `drifted` when `muse_commit_id ≠ tip`; D2 `unreadable` when `muse_commit_id` missing; `read_canonical_anchor` returns muse id + source suffix `muse_commit_id`; `read_bridge_muse_commit_id` parses live-shaped TOML. |
| **integration** | `plan_realign` returns skip when D2 aligned under content-hash tips even if `git_sha ≠ tip`; realign verify success path compares Muse IDs (mock); does not require `git_sha == tip`. |
| **e2e** | Fixture muse+git-mirror: healthy bridge (`muse_commit_id == tip`, mismatched `git_sha`) → freshness/D2 aligned → dry-run stamps marker path available without planning git-import as the repair for that mismatch. |
| **stress** | Bridge TOML with large unrelated sections — parsers still isolate `[last_export]` keys. |
| **data-integrity** | Round-trip: muse_commit_id string preserved (including `sha256:` prefix); no mutation of `git_sha` when reading Muse id. |
| **performance** | Bridge parse is file-local; no network; no `gh`. |
| **security** | Fail-closed on missing muse id (no optimistic aligned); remediation strings non-executed; no secrets from bridge file; no silent freshness disable. |

---

## §D2F.10 — Hard stops

- No kit `main` merge without Tier 3.
- No consumer posture/env flips.
- No “fix” that is default `git-import` into Muse main on healthy bridges.
- No silent default-off for `governance_freshness`.

---

## §D2F.11 — Acceptance (post Auto + consumer re-stamp)

On a `muse+git-mirror` consumer where `last_export.muse_commit_id == muse tip` and D1 is aligned:

1. `ok governance-sync --dry-run` stamps `.overseer/last_governance_sync` (D1/D2 aligned path).
2. `ok status --exit-code` → `0` with `governance_freshness.ok` true.

---

## Cross-references

- `docs/archive/phases/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md` §GFG.4 / §GFG.8.1 — freshness still fail-closed on D2.
- `docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` §3 D2 / §5 realign — amended ID space only.
- Live bridge shape: `.muse/git-bridge.toml` `[last_export]` keys `muse_commit_id` + `git_sha`.
