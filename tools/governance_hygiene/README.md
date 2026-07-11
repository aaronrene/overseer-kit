# Governance Hygiene Agent (Phase 9A-5)

Repo-agnostic agent invoked as `overseer governance-sync` (default: dry-run).

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
overseer governance-sync          # dry-run (default)
overseer governance-sync --write  # apply patches + feature-branch commit + push
```

Ground truth: `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md`
