# 🆗 Overseer Kit

Portable governance for AI-assisted development: handover/roadmap discipline, VCS hygiene,
freeze-contract review, and repo-agnostic tooling you inject into any project.

---

## What it is

The Overseer Kit is the **single canonical source** for the overseer method — a disciplined way to
run phased AI-assisted work without losing context between sessions, merging without review, or
letting governance docs drift from reality.

Instead of hand-copying handover notes, tier rules, and model labels into every repository, you
vendor the kit locally and keep one small config file: `.overseer/config.yaml`.

```bash
./cli/overseer init              # first install (POSIX shim → python -m cli.main)
./cli/overseer sync              # pull template/policy updates
./cli/overseer status            # drift + VCS regime check
./cli/overseer governance-sync   # handover/roadmap hygiene (default: dry-run)
./cli/overseer review --freeze <path>

# Equivalent without the shim:
.venv/bin/python -m cli.main governance-sync --dry-run
```

Do **not** run `python cli/overseer` — `cli/overseer` is a shell script, not Python.

**Guardrail:** every baseline capability works on plain GitHub. MuseHub is an **optional**
substrate that deepens version control — it never gates core governance features.

---

## Core concepts

### Handover and Overseer Handover

| Term | Meaning |
| --- | --- |
| **Handover** | The practice of ending each work session with an honest relay: what landed, what is true now, and the **one** next step — so a fresh AI chat can continue without re-deriving context. |
| **`OVERSEER-HANDOVER.md`** | The living handover document in each repo (from `templates/OVERSEER-HANDOVER.template.md`). Contains a **NEXT SESSION** block with a paste-ready prompt, a verified snapshot (branch, phase status), and a change log. |
| **Overseer method** | The full system: roadmap phase control + handover relay + decision tiers + model labels + freeze review + governance sync + VCS hygiene. The kit productizes this into vendored files and CLI tools. |

Think of **ROADMAP** as the plan (what phases exist, their status, which model tier each uses) and
**HANDOVER** as the baton (what to do right now, copy-pasted into the next session).

### ROADMAP

`docs/ROADMAP.md` (from template) is the **phase control board**:

- Build queue table: phase → model label → status → deliverable
- Phase Model Key (`Thinking`, `Auto`, `Thinking → Auto`, `Operator + Auto`)
- Definition of Done per phase (tests, governance sync, no secrets)

Phases move **TODO → WIP → DONE → BLOCKED**. Only one **THE ONE NEXT STEP** should be active in
the handover at a time.

### Benefits

| Benefit | How the kit delivers it |
| --- | --- |
| **No session amnesia** | Handover NEXT block + verified snapshot give every new chat the same ground truth. |
| **No doc drift** | `governance-sync` compares docs to real VCS state and patches handover/roadmap together (SD-17). |
| **Safe phase boundaries** | Thinking phases freeze contracts; Auto phases build mechanically against them — reviewed before downstream work depends on them (§6 freeze contract). |
| **Clear authority** | Tier 1/2/3 policy (`policy/tiers.yaml`) — agents act on routine work, ask once on design choices, stop on merges/staging/secrets/money. |
| **One place to improve** | Fix governance once in the kit; `overseer sync` updates every consumer footprint. |
| **VCS honesty** | Adapter reads fail-closed; optional MuseHub `realign` + safe mirror export prevent canonical-history inversions. |
| **Test discipline** | RULE #0 seven-tier contract (`policy/test-tiers.yaml`) — unit through security before a phase is DONE. |
| **Tool portability** | Policy, templates, and CLI are IDE-agnostic; Cursor gets first-class rules/skills on top. |

---

## How it works (end-to-end flow)

```text
┌─────────────────────────────────────────────────────────────────┐
│  ROADMAP — phases, model labels, status, Definition of Done      │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
  Thinking / {step}a                      Auto / {step}b
  (design + freeze spec)                  (build to frozen spec)
         │                                       │
         ▼                                       ▼
  overseer review --freeze                  seven-tier tests
  (pass / findings / blocked)                      │
         │                                       ▼
         └───────────────┬───────────────────────┘
                         ▼
              governance-sync (handover + roadmap)
                         │
                         ▼
              feature-branch commit (Tier 1)
                         │
                         ▼
              PR → merge to main (Tier 3 — human)
```

### Step-by-step (one phase)

1. **Read** `docs/ROADMAP.md` target phase and `docs/OVERSEER-HANDOVER.md` NEXT block.
2. **Paste** the handover prompt into your AI session (any tool — see below).
3. **Thinking phase** (if applicable): produce or update a frozen spec; commit on a feature branch.
4. **Freeze review**: `./cli/overseer review --freeze <spec-path> [--dry-run]`.
5. **Auto phase** (if applicable): implement exactly against the frozen spec; run tests.
6. **Governance sync**: `./cli/overseer governance-sync --dry-run` then apply when correct.
7. **Close**: update ROADMAP status row + handover NEXT block together; feature-branch commit.
8. **Publish**: open PR; merge to `main` only with Tier-3 operator authorization.

For **`Thinking → Auto`** phases, the handover emits **two** prompts: `{step}a` (Thinking) then
`{step}b` (Auto) — never both at once unless `{step}a` is incomplete.

---

## Where models are set

Models are **labels and routing policy**, not hard-coded API calls. The kit tells you *which class
of model* to use; you select the actual model in your IDE or CLI.

| Source | What it controls |
| --- | --- |
| **`policy/model-labels.yaml`** | Canonical labels: `Thinking`, `Auto`, `Thinking → Auto`, `Operator + Auto`. Every roadmap row and handover NEXT block must include `Model:`. |
| **`docs/ROADMAP.md`** | Phase Model Key table + per-phase `Model` column in the build queue. |
| **`docs/OVERSEER-HANDOVER.md`** | `Model:` on NEXT SESSION and paste-ready prompts; split rules for `{step}a` / `{step}b`. |
| **`.overseer/config.yaml` → `freeze_contract.reviewer`** | Freeze reviewer provider/mode (local or API) for `overseer review --freeze`. |
| **`policy/model-labels.yaml` → `reviewer_models`** | Hints for freeze-review model tier (`thinking-high` vs `auto-default`). |
| **`cursor_model_hint` fields** | Non-binding guidance mapping labels to common IDE model families. |

The kit **never** chooses your API model automatically during normal build work — it enforces that
you *declare* the tier so sessions stay consistent.

---

## AI tool compatibility

The kit is **IDE- and vendor-neutral at the core**. Policy, templates, handover paste blocks, and
the `overseer` CLI work the same regardless of which assistant you use.

| Layer | Cursor | Claude Code | GitHub Copilot | Any assistant (paste-only) |
| --- | --- | --- | --- | --- |
| **ROADMAP + HANDOVER docs** | ✓ | ✓ | ✓ | ✓ — primary interface |
| **`overseer` CLI** | ✓ terminal | ✓ terminal | ✓ terminal | ✓ terminal |
| **`policy/*.yaml`** | ✓ | ✓ | ✓ | ✓ — read for tier/model rules |
| **`.cursor/rules/*.mdc`** | Auto on `init`/`sync` | Manual / if your tool reads project rules | Partial — no native skills | N/A — use `policy/tiers.yaml` instead |
| **`.cursor/skills/*/SKILL.md`** | Native Agent Skills | Copy workflow into prompts | Not supported | Follow SKILL steps manually |
| **Cursor Automations** | Optional templates in `cursor/automations/` | N/A | N/A | Use CLI (`governance-sync`, `review --freeze`) instead |

### What changes per tool

| Tool | Typical usage pattern |
| --- | --- |
| **Cursor** | Richest integration: rules always apply, skills invocable, optional session-end Automations. Paste handover prompt when starting a phase chat. |
| **Claude Code** | Use terminal for `overseer` CLI; read `AGENTS.md` + handover/roadmap; paste NEXT block into Claude. Project rules may need manual setup if your environment supports them. |
| **GitHub Copilot** | Same docs + CLI; no skills/automations. Rely on handover paste blocks and `policy/tiers.yaml` for authority boundaries. |
| **Any other assistant** | Fully supported via **docs-first**: open HANDOVER, paste the prompt, follow ROADMAP phase, run CLI commands yourself, commit on a feature branch. |

**Degrade path (by design):** if Cursor Automations are unavailable, `overseer governance-sync`
and `overseer review --freeze` are the portable fallback — no Cursor-only gate on core governance.

---

## VCS regimes

| Regime | Canonical history | Best for |
| --- | --- | --- |
| **`git-only`** | GitHub `main` | Any repo with Git alone — full kit features, no Muse install |
| **`muse+git-mirror`** | MuseHub (`sha256:` commits) | Teams that want content-addressed history + safe GitHub mirror |
| **`muse-only`** | MuseHub only | Muse-native projects where Git is not used |

Same CLI commands in every regime. The adapter layer handles the differences fail-closed.

### Git-only (start here)

No MuseHub required. See `docs/GIT-ONLY-QUICKSTART.md`.

```bash
./cli/overseer init --regime git-only --non-interactive
./cli/overseer status --check-footprint
./cli/overseer governance-sync --dry-run
```

Repos that already have hand-authored handover/roadmap files should use `init --migrate` instead
(see `docs/K6-PILOT-OPERATOR-RUNBOOK.md`).

### MuseHub optional upgrade (`muse+git-mirror`)

| Capability | What you gain |
| --- | --- |
| **Content-addressed history** | Muse commits (`sha256:…`) as the canonical record |
| **`realign`** | Detect and repair Muse↔Git history drift |
| **Safe mirror export** | Publish to GitHub via an isolated checkout — never on your dev tree |
| **Provenance** | Richer version metadata than Git commit ids alone |

**How to connect a repo:**

1. Install [Muse](https://musehub.ai) and authenticate (`muse --version`).
2. Initialize Muse in the repo: `muse -C <repo-root> init` (creates `.muse/` locally).
3. Flip `.overseer/config.yaml` to `regime: muse+git-mirror`, `canonical: muse`, and set
   `vcs.git.mirror_branch` (typically `muse-mirror`).
4. Run `./cli/overseer sync` — seeds `MUSE-BRIDGE-WORKFLOW.md` and
   `scripts/muse-bridge-deploy.sh` when the regime requires them.
5. **Day-to-day:** `muse commit` on feature branches in Muse.
6. **Publish to GitHub:** only via the safe deploy script:

   ```bash
   ./scripts/muse-bridge-deploy.sh "mirror: <summary>"
   ```

   Flow: Muse `main` → isolated `.muse/mirror/` → `origin/muse-mirror` → PR → `main`.

**Hard rules (SD-14):**

- Never `muse bridge git-export --git-dir .` on your working tree.
- Never `git push origin main` when Muse is canonical — mirror via `muse-mirror` PR only.

Full operator steps: `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md` and root `MUSE-BRIDGE-WORKFLOW.md`.

---

## Install and day-to-day usage

### First install (any repo)

```bash
# From a clone of this kit (or path to cli/overseer):
./cli/overseer -C <your-repo> init --regime git-only --non-interactive

# Or migrate an existing repo with living docs:
./cli/overseer -C <your-repo> init --migrate --from-config <prepared.yaml> --non-interactive
```

This writes: governance docs, `policy/`, `.cursor/` fragments, `.overseer/version.lock`, and
`AGENTS.md` (when in footprint).

### Every session

1. Open `docs/OVERSEER-HANDOVER.md` → copy **Paste-ready prompt**.
2. Work on a **feature branch** (Tier 1).
3. Run tests for your phase tier.
4. Before ending: `./cli/overseer governance-sync --dry-run` → fix drift → apply if needed.
5. Commit docs + code together on the feature branch.
6. Open PR; merge only with Tier-3 authorization.

### Pull kit updates

```bash
./cli/overseer sync              # preview drift
./cli/overseer sync -y           # apply kit footprint updates
./cli/overseer status --check-footprint
```

---

## Status

**K7 DONE** — vendoring CLI, freeze reviewer, governance-sync, pilot install/migrate, Muse bridge
footprint, operator dogfood on this repo. **255** seven-tier tests green. See `docs/ROADMAP.md`.

---

## Runtime vs governance

This kit owns the **governance layer** (docs, VCS adapters, hygiene agent, freeze reviewer).
Multi-agent product runtime (orchestrator / worker / checker patterns) lives in consumer
codebases — see `docs/OVERSEER-KIT-SPEC.md`. The kit does not ship product adapters.

---

## Docs

| Doc | Purpose |
| --- | --- |
| `docs/OVERSEER-KIT-SPEC.md` | Frozen architecture |
| `docs/OVERSEER-HANDOVER.md` | Living relay (this repo's handover) |
| `docs/ROADMAP.md` | Phase control + build status |
| `policy/model-labels.yaml` | Model tier labels + handover split rules |
| `policy/tiers.yaml` | Decision authority Tier 1/2/3 |
| `policy/test-tiers.yaml` | Seven-tier test contract |
| `docs/GIT-ONLY-QUICKSTART.md` | Greenfield install without Muse |
| `docs/K6-PILOT-OPERATOR-RUNBOOK.md` | Migrate + install on consumer repos |
| `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md` | Flip a repo to `muse+git-mirror` |
| `MUSE-BRIDGE-WORKFLOW.md` | SD-14 mirror rules (vendored when regime requires) |
| `cursor/README.md` | What ships into `.cursor/` on init/sync |

---

## Dogfood

This repo uses its own handover/roadmap workflow while being built. VCS regime:
**`muse+git-mirror`** — MuseHub canonical, GitHub mirror via `scripts/muse-bridge-deploy.sh` only
(see `.overseer/config.yaml` and `AGENTS.md`).
