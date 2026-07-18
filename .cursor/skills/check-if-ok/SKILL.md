---
name: check-if-ok
description: >-
  Ad-hoc honesty check for any work (roadmap or side research). Scaffolds a
  side-check freeze doc if needed, then runs the same freeze-review and optional
  build-verification path used by Scooling and every Overseer consumer.
---

# Check if OK

Use when the operator says **Check if OK**, **check if ok**, or **`/check-if-ok`** — for
roadmap phases **or** side research that is **not** on the ROADMAP. Does **not** open a
new `docs.lanes` entry.

## Purpose

Same twin honesty gates as roadmap re-review loops:

| Gate | When | Tool |
| --- | --- | --- |
| **Freeze review** | Spec / Thinking output ready (`frozen: true`) | This skill → `/freeze-review` / `/freeze-review-loop` + `ok review --freeze` / `ok check-if-ok` |
| **Build verification** | Implementation claims done | `/build-verification-review` |

Engine is kit-owned (`tools/freeze_reviewer/` + `cli/commands/review.py`) — identical in
Scooling, Knowtation, VideoFactory, and any repo after `ok sync`.

## How the operator runs it

**Preferred (any Cursor chat):** type `Check if OK` or invoke `/check-if-ok`.

**Terminal (no Cursor required):**

```bash
ok check-if-ok --topic "my-side-research" --dry-run
ok check-if-ok --path docs/reviews/2026-07-17-my-side-research.md
ok check-if-ok --path docs/PHASE-FOO.md   # existing freeze artifact
```

Chat does the **semantic** thinking-model review. Terminal runs the **mechanical** checklist
gate (same as `ok review --freeze`).

## Workflow (execute in this session)

1. **Identify the artifact**
   - If the operator names a freeze/spec path → use it.
   - Else if a PHASE / side-check doc already exists for the work → use it.
   - Else scaffold under `docs/reviews/<YYYY-MM-DD>-<slug>.md` via:

     ```bash
     ok check-if-ok --topic "<short-slug>" --scaffold-only
     ```

     Or create the file by hand using the template in
     `.cursor/skills/check-if-ok/SIDE-CHECK-TEMPLATE.md`.

2. **Fill scope** — intent, interfaces, fail-closed rules, seven-tier test matrix, what
   must not change. Commit on a feature branch (Tier 1).

3. **Freeze review (beginning gate)** — Model: `thinking-high`
   - Follow `.cursor/skills/freeze-review/SKILL.md` (or `/freeze-review-loop` for rounds).
   - Run mechanical gate:

     ```bash
     ok check-if-ok --path <artifact> --dry-run
     ok check-if-ok --path <artifact>          # stamps on pass when configured
     ```

     (`ok review --freeze <artifact>` is equivalent — same engine.)

4. **If Auto / code landed — build verification (end gate)**
   - Follow `.cursor/skills/build-verification-review/SKILL.md`.
   - Do **not** claim DONE / “shipped” without `pass`.

5. **Report** — verdict `pass` | `findings` | `blocked`; every finding needs `path:line`.
   Append the Review-record table on the artifact.

## Thinking sessions (always-on)

When the session Model is **Thinking** (or Thinking → Auto):

- **End of Thinking / before Auto:** freeze review must reach `pass` (step 3).
- **After Auto / implementation:** build verification must reach `pass` (step 4).

See `.cursor/rules/check-if-ok-thinking.mdc` (alwaysApply).

## Hard stops

Escalate to human — do not greenwash — for:

- `security` · `irreversible` · `real_money` · `gates_tier3`

Never open a new governance **lane** for a one-off check. Never merge to
`{{vcs.git.main_branch}}` as part of this skill (Tier 3).

## Read first

- `docs/OVERSEER-KIT-SPEC.md` §6
- `.cursor/skills/freeze-review/SKILL.md`
- `.cursor/skills/build-verification-review/SKILL.md`
- `.overseer/config.yaml` → `freeze_contract`
