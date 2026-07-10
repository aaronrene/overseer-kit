# Overseer Kit

Portable governance for AI-assisted development: handover/roadmap discipline, VCS hygiene,
freeze-contract review, and repo-agnostic tooling you inject into any project.

## What it is

The Overseer Kit is the **single canonical source** for the overseer/handover method used across
Scooling, Knowtation, MuseHub, VideoFactory, and any other repo. Instead of hand-copying
`OVERSEER-HANDOVER.md`, tier rules, and model labels into every project, you run:

```bash
/path/to/overseer-kit/cli/overseer init    # first install into a consumer repo
/path/to/overseer-kit/cli/overseer sync    # pull template/policy updates
/path/to/overseer-kit/cli/overseer status  # drift + VCS regime check
```

Each consumer repo keeps one small config file: `.overseer/config.yaml`.

## Status

**K1 Bootstrap** — repo skeleton + frozen spec promoted from Scooling. Build phases K2–K6 + 9A-5
queued in `docs/ROADMAP.md`.

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
