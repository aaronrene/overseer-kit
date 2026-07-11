# VideoFactory — Option B production honesty (paste into fresh chat)

Copy everything below the line into a **thinking-high** session in the VideoFactory repo.

---

# VideoFactory — Option B: templates + manifest + checkpoints + PROGRESS.md

## Prerequisite

Overseer Kit installed with **K8 `queue` lane** (master status board):

```bash
KIT=<path-to-overseer-kit>
VF=<path-to-videofactory>

$KIT/cli/overseer -C $VF init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-videofactory.yaml \
  --non-interactive

$KIT/cli/overseer -C $VF status --check-footprint
```

Living docs (lane `queue` — sole overseer-sync target for VF):

- `VIDEO_PRODUCTION_STATUS_BOARD.md` — master queue (all worktrees; truth on `main`)
- `VIDEO_OVERSEER_HANDOVER.md` — session relay

**Do not redesign overseer-kit.** VF domain files only.

## Architecture (frozen for this build)

```text
main (VideoFactory)
  VIDEO_PRODUCTION_STATUS_BOARD.md     ← overseer lane: queue (one row per video)
  VIDEO_OVERSEER_HANDOVER.md

permanent worktree + video branch
  videos/_active/manifest.yaml         ← machine state (current_step, verified flags)
  videos/_active/PROGRESS.md           ← human drill-down (generated from manifest)
  videos/_active/<assets>/             ← narration, avatar, export, etc.

repo-level
  docs/video-specs/<type_id>.md        ← frozen template (once per video type)
  policy/video-checkpoints.yaml        ← mechanical check wiring
  scripts/verify/vf_verify_*.py        ← fail-closed gates (exit ≠ 0)
```

**We do NOT use per-video ROADMAP/HANDOVER.** Option B = manifest + verify + PROGRESS.md.
K8 `active` lane is available but **not required** for VF videos.

**Worktree flow:** each permanent worktree pulls `main` for master board; active video work on
`feat/video/<slug>` with `videos/_active/` on that branch; on DONE → merge → archive
`videos/_active/` → `videos/archive/<slug>/` → update master board row.

---

## THE PROBLEM

Agents ignore rules and mark steps done without evidence. **Mechanical checkpoints** after every
step catch failures early (wrong narration, avatar, thumb, CTA) — not at final render.

| Layer | Enforcement |
| --- | --- |
| Always-on Cursor rule | No step advance without verify exit 0 |
| Verify scripts | Fail-closed; stderr cites exact failure |
| Manifest | Only orchestrator sets `verified: true` |
| Master board row | Shows `current_step`; not DONE until all verified |
| Final gate | `/build-verification-review` before row DONE |

Thinking model: **template freeze once** + **final build verification** — not every step.

---

## DELIVERABLES (all required)

| # | Deliverable | Path |
| --- | --- | --- |
| 1 | Video type catalog | `docs/video-specs/CATALOG.md` |
| 2 | Failure pattern register | `docs/video-specs/FAILURE-PATTERNS.md` |
| 3 | Frozen template per type | `docs/video-specs/<type_id>.md` |
| 4 | Checkpoint policy | `policy/video-checkpoints.yaml` |
| 5 | Verify scripts | `scripts/verify/vf_verify_<step>.py` |
| 6 | Orchestrator | `scripts/verify/vf_verify_step.py` |
| 7 | Progress renderer | `scripts/tools/render_progress.py` |
| 8 | Shared verify lib | `scripts/verify/_lib.py` |
| 9 | Active manifest fixture | `videos/_fixtures/demo-slug/manifest.yaml` |
| 10 | Fixture assets | `videos/_fixtures/demo-slug/...` |
| 11 | Always-on rule | `.cursor/rules/video-production-checkpoints.mdc` |
| 12 | Step verify skill | `.cursor/skills/vf-step-verify/SKILL.md` |
| 13 | Tests (seven tiers) | `tests/verify/...` |
| 14 | Master board columns | `VIDEO_PRODUCTION_STATUS_BOARD.md` |

Every checkpoint = script with **exit 1 on failure**.

---

## PHASE 1 — Scan video types

Search: `videos/`, `projects/`, `exports/`, `templates/`, `assets/`, worktree-related paths,
branch patterns (`feat/video/*`, `video/BOR-*`), scripts, CI, `.cursor/`, git history for rework
patterns (missing narration, wrong avatar, missing CTA, bad thumb).

**Output `docs/video-specs/CATALOG.md`:**

| type_id | name | worktree | platforms | aspect | duration | series? |

Include: Threads in Time (long + reel), Trend + vertical, thumbnail workflow, distribution,
hand-off, and any others found. Do not assume the list is complete.

---

## PHASE 2 — Failure patterns → checkpoints

**Output `docs/video-specs/FAILURE-PATTERNS.md`:**

| pattern_id | symptom | root cause | step | mechanical check |

Mine git history and docs. Map every pattern to a verify script step.

---

## PHASE 3 — Frozen templates

One `docs/video-specs/<type_id>.md` per catalog row. Front matter: `template_id`, `frozen: true`.

**Standard steps** (omit N/A per type): `brief` → `narration` → `avatar` → `visuals` → `timeline`
→ `thumbnail` → `cta` → `music` → `captions` → `export` → `metadata` → `publish`.

Each step: concrete paths under `videos/_active/` (use `{slug}` in policy overrides), numeric
bounds, and **Mechanical checks** list matching verify scripts.

`/freeze-review-loop` once per template — **not** per video.

---

## PHASE 4 — `policy/video-checkpoints.yaml`

- `steps:` shared definitions → `verify_script` path
- `templates:` ordered step lists per `type_id`
- `overrides:` per-template thresholds and artifact paths (`videos/_active/...` on branch)

Single source of machine truth. Templates are human-readable; policy is what scripts enforce.

---

## PHASE 5 — Verify scripts

```bash
python scripts/verify/vf_verify_step.py \
  --manifest videos/_active/manifest.yaml \
  --step narration
# exit 0 = pass; exit 1 = fail + stderr
```

**Minimum scripts:** `brief`, `narration`, `avatar`, `visuals`, `timeline`, `thumbnail`, `cta`,
`music`, `captions`, `export`, `metadata`.

**Orchestrator modes:**

- `--step ID` — one step; on pass update manifest `verified` + run `render_progress.py`
- `--through current` — all steps up to `current_step`
- `--all` — full pipeline (final pre-DONE gate)

Agents must **not** hand-set `verified: true` — only orchestrator after exit 0.

---

## PHASE 6 — Manifest (active video state machine)

**Path:** `videos/_active/manifest.yaml` on the video branch.

```yaml
template_id: threads-in-time-reel
slug: threads-ep-042
worktree: threads-in-time
branch: feat/video/threads-ep-042
current_step: narration
steps:
  brief:     { verified: false, verified_at: null }
  narration: { verified: false, verified_at: null }
  # ... all steps for template
```

Rule: advance `current_step` only when previous step `verified: true`.

---

## PHASE 7 — `PROGRESS.md` (human tracking)

**Path:** `videos/_active/PROGRESS.md` — **separate** from master board (not duplicated).

Generated by `scripts/tools/render_progress.py` from manifest after each successful verify.

Master board = one row summary (`current_step`, status). PROGRESS.md = full phase list for **this
video only**.

---

## PHASE 8 — Master status board

Add columns to `VIDEO_PRODUCTION_STATUS_BOARD.md`:

| video | worktree | template_id | branch | current_step | steps_passed | status |

Status: `TODO` | `WIP` | `VERIFY-FAIL` | `READY-FOR-FINAL` | `DONE`

Sync with: `overseer governance-sync --lane queue --dry-run` (or default).

---

## PHASE 9 — Agent guardrails

### `.cursor/rules/video-production-checkpoints.mdc` (`alwaysApply: true`)

1. Read `videos/_active/manifest.yaml` + `docs/video-specs/<template_id>.md`
2. Work only on `current_step`
3. After step: run `vf_verify_step.py --step <current_step>`
4. Exit ≠ 0 → fix and re-run; do not advance
5. On pass: orchestrator updates manifest + PROGRESS.md
6. Never mark board row `DONE` until `--all` passes + `/build-verification-review` pass
7. No placeholder assets in verified steps

### `.cursor/skills/vf-step-verify/SKILL.md`

Run verify → fix cited stderr only → re-run → update manifest.

---

## PHASE 10 — Extra checkpoints (search and add if applicable)

| Check | Signal |
| --- | --- |
| Dead air in first 3s | audio energy in opening window |
| Series continuity | intro/outro asset IDs match series template |
| Dual export (long + reel) | both files pass ffprobe |
| Placeholder detection | `placeholder`, `temp`, `draft` in verified paths |
| Licensed music ID | bed ID in approved library |
| Caption sync | max drift ms |
| No black/silent tail | ffprobe + frame sample |

Document skipped checks in FAILURE-PATTERNS.md with reason.

---

## PHASE 11 — Tests

```bash
pytest tests/verify/ -v
```

Seven tiers: unit per script, integration manifest+policy, e2e demo-slug pipeline, security on
`--manifest` path traversal.

---

## SESSION CLOSE — report

1. Catalog count + types found
2. FAILURE-PATTERNS count
3. Templates + freeze review status
4. `policy/video-checkpoints.yaml` complete?
5. Verify scripts + pytest result
6. Sample: `vf_verify_step.py --manifest videos/_fixtures/demo-slug/manifest.yaml --step narration`
7. Non-machine-checkable items (human review only)

## Hard stops

- No board row DONE without `--all` verify pass + build verification pass
- No per-video thinking-model spec — templates only
- No duplicate checkpoint defs in template + policy + PROGRESS (policy is machine source)
- Fix only verify-cited failures — no unrelated refactors
