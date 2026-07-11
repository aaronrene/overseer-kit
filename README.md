# 🆗 Overseer Kit
Portable governance for AI-assisted development: handover/roadmap discipline, VCS hygiene,
freeze-contract review, and repo-agnostic tooling you inject into any project.

## What it is

The Overseer Kit is the **single canonical source** for the overseer/handover method used across
Scooling, Knowtation, MuseHub, VideoFactory, and any other repo. Instead of hand-copying
`OVERSEER-HANDOVER.md`, tier rules, and model labels into every project, you run:

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

Each consumer repo keeps one small config file: `.overseer/config.yaml`.

## Status

**K5b + 9A-5** — freeze reviewer + governance-sync CLI live. **K6 Pilot install** is NEXT
(Thinking → Auto). See `docs/ROADMAP.md`.

## Reference implementation

Scooling Phase 9A (`scooling/src/phase9a/`) is the **runtime** reference for
Overseer → Foreman → Worker → Checker → Auditor orchestration inside a product. This kit owns the
**governance layer** (docs, VCS adapters, hygiene agent, freeze reviewer) that any project —
including Scooling — vendors locally.

## Docs

| Doc | Purpose |
| --- | --- |
| `docs/OVERSEER-KIT-SPEC.md` | Frozen architecture (K1–K6 contract) |
| `docs/OVERSEER-HANDOVER.md` | Living relay for kit development |
| `docs/ROADMAP.md` | Phase control for kit build |
| `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` | First shipped agent tool spec |

## Dogfood

This repo uses its own handover/roadmap workflow while being built. VCS regime: **git-only**
(see `.overseer/config.yaml`).
