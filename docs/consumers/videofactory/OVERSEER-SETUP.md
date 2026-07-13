# VideoFactory — overseer kit setup

Use the same overseer discipline as other repos, with **VideoFactory-specific names** for the living
docs so multi-repo workspaces stay unambiguous.

## Doc mapping (same system, different labels)

| Kit concept | VideoFactory file | Display title |
| --- | --- | --- |
| Roadmap / phase queue | `VIDEO_PRODUCTION_STATUS_BOARD.md` | Video Production Status Board |
| Handover / session relay | `VIDEO_OVERSEER_HANDOVER.md` | Video Overseer Handover |

The status board is your **video queue and grid** — phases, videos in play, build status. The kit
treats it as the roadmap (SD-17 sync target). `governance-sync` and handover regeneration keep it
**honest vs git reality**, the same way a software roadmap stays honest.

**Renaming is supported.** Each repo's `.overseer/config.yaml` sets `docs.handover`, `docs.roadmap`,
`docs.handover_title`, and `docs.roadmap_title`. MuseHub can use `MUSEHUB-ROADMAP.md` / `MUSEHUB-OVERSEER-HANDOVER.md`
in the same workspace — no conflict.

## Prepared config

Copy or reference:

`tests/fixtures/pilot/config-videofactory.yaml`

Every field is commented in that file.

## Install

```bash
KIT=/path/to/overseer-kit
VF=/path/to/videofactory

# Dry-run first (migrate preserves existing living docs)
$KIT/cli/ok -C $VF init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-videofactory.yaml \
  --non-interactive --dry-run

# Apply
$KIT/cli/ok -C $VF init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-videofactory.yaml \
  --non-interactive

$KIT/cli/ok -C $VF status --check-footprint
```

If you **already** have a Video Production Status Board and handover file with different names,
either rename them to match the config or edit `docs.handover` / `docs.roadmap` in
`.overseer/config.yaml` to match your filenames before `init --migrate`.

## Mandatory review gates (kit-wide, not optional)

Shipped in every consumer install via templates + `.cursor/rules/build-verification-required.mdc`:

| Gate | When | Skill |
| --- | --- | --- |
| Freeze review | Before Auto build (`{step}a` → `{step}b`) | `/freeze-review-loop` |
| Build verification | After Auto build, **before DONE** | `/build-verification-review` |
| Tests | During/after build | `policy/test-tiers.yaml` |
| Governance sync | Session end | `/governance-sync` |

Agents must not mark a phase **DONE** on the status board until build verification **`pass`**.

## Day-to-day (VideoFactory)

1. Open `VIDEO_OVERSEER_HANDOVER.md` → paste NEXT prompt.
2. Work on `feat/<slug>` branch.
3. Thinking phase: freeze spec → `/freeze-review-loop` until pass.
4. Auto phase: build → tests → `/build-verification-review` until pass.
5. Update status board + handover together → `governance-sync --dry-run` → commit.
6. PR → merge with Tier-3 authorization.

## Hard stops

- No `--force --include-preserved` on live migrate (pilot rule)
- No merge to `main` without Tier 3
- No marking videos/phases DONE without build verification pass

---

## Multiple roadmaps? Video queue + software work in one tree

**Today (K7):** `.overseer/config.yaml` wires **one** living-doc pair into `governance-sync`:

- `docs.handover` → one relay doc (Video Overseer Handover)
- `docs.roadmap` → one queue doc (Video Production Status Board)

There is no second auto-synced roadmap/handover pair in the same repo yet. Optional
`docs.coordination` (e.g. `CROSS-REPO-COORDINATION.md`) is **preserved on migrate** but is **not**
patched by `governance-sync`.

### Recommended VideoFactory layout (works now)

| Concern | Where it lives | Synced by kit? |
| --- | --- | --- |
| Video production queue (always on) | `VIDEO_PRODUCTION_STATUS_BOARD.md` | Yes — primary roadmap |
| Session relay for video work | `VIDEO_OVERSEER_HANDOVER.md` | Yes — primary handover |
| Major software/tooling build | **Section** on the same status board (`## Engineering`) **or** a separate `ENGINEERING_ROADMAP.md` you maintain manually | Manual only if separate file |
| Per-video work | `feat/video/<slug>` branch + **one row** on the status board | Row updated on phase close; branch is the isolation unit |

You do **not** need a full second roadmap + handover pair for every video. You need:

1. **One repo-level status board** — master grid of videos and engineering lanes.
2. **One repo-level handover** — current session relay (whichever lane you are in).
3. **One branch per video** (your existing habit) — isolates assets, edits, and agent context.
4. **One row per video** on the status board — honest status vs merged reality.

When you switch from “shipping Threads ep. 42” to “building a new export pipeline,” you change the
**NEXT prompt** in the handover and the **active row** on the status board. You do not spin up a
second synced doc pair unless we add multi-lane config (future K8+).

### Future extension (not required for VF install)

A natural kit evolution is `docs.lanes[]` — named pairs, e.g. `production` + `engineering`, each
with its own handover/roadmap paths and optional `governance-sync --lane`. Until then, **one synced
pair + sections** (or a manual second file) is the supported pattern.

---

## Per-video specs: templates, not a thinking model every time

Repetitive video types (Threads in Time + Reels, Trend + verticals, thumbnails, CTA, music, avatar
rules, cadence/expression) should be **frozen once**, not re-specified per video.

### Three layers (all live in the VideoFactory repo, not in overseer-kit core)

| Layer | Purpose | Freeze review? |
| --- | --- | --- |
| **Template library** | `docs/video-specs/` or `policy/video/` — one frozen spec per format | **Once** per template (thinking model); re-run only when the template changes |
| **Status board row** | Instance: template ID, topic, due date, branch, status | No full spec — references template |
| **Instance manifest** (optional) | `videos/<slug>/manifest.yaml` on the video branch — params only | No — Auto reads template + manifest |

**Gate 1 (freeze):** Run `/freeze-review-loop` when you **author or change** a template — not on
every episode.

**Gate 2 (build verification):** Run `/build-verification-review` **per video** before marking the
row `DONE` — checks implementation against the **frozen template ID** + instance checklist (export
settings, CTA present, music bed, avatar rules, etc.). This is the honesty gate you want for
publish-ready work without paying for a thinking model on identical structure every time.

### Is a frozen spec necessary for every video?

| Situation | Freeze loop? | Build verification? |
| --- | --- | --- |
| New video type or template change | Yes | Yes |
| Same template, new topic/episode | No | Yes |
| Trivial tweak inside one template | Optional delta note on template | Yes |

### When is a video “reviewed”?

1. **During build** — tests / export checks per `policy/test-tiers.yaml` (you define VF tiers in
   consumer `policy/`).
2. **Before DONE** — mandatory `/build-verification-review` (always-on Cursor rule).
3. **Before publish** — human spot-check or your publish pipeline (outside kit).

There is no separate “freeze spec per video” unless that video is a one-off departure from all
templates.

---

## Modularity: molding the kit for VideoFactory (and any project)

The kit is **repo-agnostic governance**, not a VideoFactory runtime. Customization stays in the
**consumer repo**:

| Extension point | VideoFactory example |
| --- | --- |
| `.overseer/config.yaml` | Custom doc paths and display titles |
| Preserved living docs | Status board + handover content and sections |
| `policy/` | Video checklists, test tiers, model labels |
| `docs/video-specs/` | Frozen format templates (your domain) |
| `.cursor/rules/` | VF-specific always-on rules (promoted on migrate if under kit paths) |
| `.cursor/skills/` | Optional VF skills (e.g. “verify export against template X”) |
| VCS adapter | `git-only`, `muse-only`, or `muse+git-mirror` per repo |

You do **not** fork overseer-kit. You **install** it into VideoFactory; domain templates and video
policy live in VideoFactory. Other repos (MuseHub, Knowtation) use the same kit with different doc
names and policy files.

**Stub / add-on pattern:** Core CLI and adapters expose fixed contracts (`init`, `sync`, `status`,
`review`, `governance-sync`). Domain-specific behavior is added via consumer **policy**, **preserved
docs**, and **Cursor skills/rules** — not by editing kit source unless you are contributing upstream.

---

## Quick decision guide

| Question | Answer |
| --- | --- |
| Can I use Video Status Board and a software roadmap at once? | Yes — **one** pair is auto-synced; use sections on the status board or a manual second roadmap file for engineering. |
| One roadmap per video? | No — one **row** per video on the repo status board; one **branch** per video. |
| Thinking model every video? | No — freeze **templates** once; per-video **build verification** only. |
| Is the kit ready for VF? | Yes — install with `config-videofactory.yaml`, add template library in VF, branch-per-video + status rows. |
| Multi-lane auto-sync later? | Optional K8+ `docs.lanes[]`; not blocking VF install. |
