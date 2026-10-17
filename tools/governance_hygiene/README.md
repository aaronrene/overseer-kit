# Governance Hygiene Agent (Phase 9A-5)

Repo-agnostic agent invoked as `ok governance-sync` (default: dry-run).

## Layout

| Module | Role |
| --- | --- |
| `reads.py` | Verified reads R1–R5 (adapter + gh) |
| `drift.py` | Drift detection D1–D3 |
| `patch.py` | Templated anchor replacement on handover + roadmap |
| `realign.py` | Muse realign guard (§5) |
| `engine.py` | Orchestration, commit, PR URL |

## CLI

```bash
ok governance-sync          # dry-run (default)
ok governance-sync --write  # apply patches + feature-branch commit + push
```

Ground truth: `docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md`
