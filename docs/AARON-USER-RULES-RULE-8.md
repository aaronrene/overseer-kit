# Paste into Cursor → Settings → Rules → User Rules

Replace the old **RULE 8 Orchestrator** block (hand-rolled `ROADMAP.md` /
`OVERSEER_HANDOVER.md` folklore) with the text below. Keep RULES #0–#7 as you prefer;
this file only modernizes Rule 8 to match installed Overseer Kit.

Kit-vendored always-on copy (preferred inside any governed repo after `ok sync`):
`.cursor/rules/orchestrator.mdc`.

---

##RULE 8 Orchestrator — use Overseer Kit

**Kit:** https://github.com/aaronrene/overseer-kit  
**CLI:** `ok` (`./cli/ok` from a kit checkout). Prefer `ok` over deprecated `overseer`.

When a repo has `.overseer/config.yaml`, run phased work **through the kit**. Do not invent a
parallel hand-rolled ROADMAP / HANDOVER protocol.

### Install / day-to-day CLI

| Situation | Command |
| --- | --- |
| First install | `ok init --regime <git-only\|muse+git-mirror\|muse-only>` |
| Existing living docs | `ok init --migrate …` (see kit K6 runbook) |
| Pull kit updates | `ok sync` |
| Health / drift | `ok status` |
| Docs vs VCS | `ok governance-sync --dry-run` then apply when correct |
| Freeze gate | `ok review --freeze <artifact>` |
| Ad-hoc honesty | `ok check-ok` or type **Check OK** / `/check-ok` |

Doc paths are **config-driven** (`docs.roadmap` / `docs.handover` in `.overseer/config.yaml`).
Do not assume root `ROADMAP.md` / `OVERSEER_HANDOVER.md` unless that config says so.

### Two durable docs (always together)

- **Roadmap** — phase control: Phase Model Key, build queue (phase → Model → Status → deliverable), Definition of Done
- **Handover** — session relay: NEXT SESSION, paste-ready prompt, verified snapshot, VCS table, change log

Trust the handover verified snapshot over chat history. Update both docs in the same closing
feature-branch commit.

### Model labels (required on every NEXT / paste block)

From kit `policy/model-labels.yaml`:

- **Thinking** — freeze WHAT/HOW (`frozen: true`); no mechanical build
- **Auto** — build exactly to the frozen spec; no redesign
- **Thinking → Auto** — emit `{step}a` then `{step}b` only (never one combined prompt)
- **Operator + Auto** — human for Tier-3 merge/live gates; Auto for impl + doc sync

Never Outline/Plan on Auto. Never start Auto until freeze review verdict is **pass**.
Never mark DONE on green tests alone — run `/build-verification-review` → **pass** first.

### Starting a phase

1. Fresh chat with the Model tier named in the handover
2. Read roadmap (target phase) + handover (NEXT + verified snapshot)
3. Paste the **Paste-ready prompt** fence
4. Thinking → `/freeze-review-loop` / `ok review --freeze` → pass
5. Auto → seven-tier tests (`policy/test-tiers.yaml`) → `/build-verification-review` → pass → DONE
6. Close: roadmap + handover together; `ok governance-sync`; feature-branch commit/PR
7. Merge to main = Tier 3 only (stop for operator)

### Agent behavior

- Prefer kit rules/skills under `.cursor/` and `.claude/` over folklore
- One THE ONE NEXT STEP at a time
- Dirty tree at session end is a failure
- When the kit is installed, **feature-branch** closing commits that bundle code/tests + roadmap +
  handover are Tier 1 (do them without waiting for a separate “please commit” ask). Merge to main
  remains Tier 3.
- Hard stops: secrets, live posture flips, real money, unauthorized main merge
