# Phase K8 — Multi-lane living docs (Frozen contract)

Status: **Frozen for K8b Auto build.**

## Simple summary

One repo can now declare **two or more named overseer doc pairs** in `.overseer/config.yaml`
(e.g. `queue` + `active`, or `production` + `engineering`). `governance-sync --lane <name>`
patches only that pair. Single-lane configs are unchanged.

## Config shape (additive, `overseer_config_version: 1`)

```yaml
docs:
  # Required — must match docs.lanes[default_lane] when lanes is set (token backward compat).
  handover: VIDEO_OVERSEER_HANDOVER.md
  roadmap: VIDEO_PRODUCTION_STATUS_BOARD.md
  handover_title: Video Overseer Handover
  roadmap_title: Video Production Status Board
  coordination: null
  standing_decisions: VIDEO_PRODUCTION_STATUS_BOARD.md
  # Optional multi-lane (K8)
  default_lane: queue
  lanes:
    queue:
      handover: VIDEO_OVERSEER_HANDOVER.md
      roadmap: VIDEO_PRODUCTION_STATUS_BOARD.md
      handover_title: Video Overseer Handover
      roadmap_title: Video Production Status Board
    active:
      handover: videos/_active/HANDOVER.md
      roadmap: videos/_active/ROADMAP.md
      handover_title: Active Video Handover
      roadmap_title: Active Video Roadmap
```

**Rules:**

- `lanes` omitted → single-lane (legacy); `--lane` rejected.
- `lanes` present → `default_lane` required; each lane needs `handover` + `roadmap`; titles optional.
- Top-level `handover` / `roadmap` / titles **must equal** `lanes[default_lane]` (fail-closed).
- Lane doc paths may live outside `docs/` (e.g. `videos/_active/` with `root_relative_docs: "."`).
- All lane destinations are **preserved living docs** on migrate (same as handover/roadmap today).

## CLI

| Flag | Behavior |
| --- | --- |
| (none) | Sync `default_lane`, or sole pair when `lanes` absent |
| `--lane NAME` | Sync named lane only |
| `--all-lanes` | Sync every configured lane; **skip** lanes whose files are missing (emit message) |

## Tokens

`{{docs.handover_path}}` / `{{docs.roadmap_path}}` remain the **default lane** paths. Lane-specific
cursor rules use fixed paths in the consumer repo.

## VideoFactory (Option B)

VF uses **`queue` lane only** for overseer sync (master status board). Per-video honesty uses
`manifest.yaml` + mechanical verify + generated `PROGRESS.md` — not the `active` lane unless opted in.
