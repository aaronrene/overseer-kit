# Overseer Kit — Master Thinking Session Prompt

**Purpose:** Copy everything below the `---` line into a **Thinking (high)** session in the **Overseer Kit** repo.  
**Status:** Executed 2026-07-11 — K9a contract drafted; vision expanded; ROADMAP/HANDOVER updated.  
**Remaining:** independent freeze review on `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md` before K9b Auto.  
**Do not Auto-build until freeze `pass`.**

---

# Overseer Kit — Master architecture freeze (Thinking session)

## What this session is

Freeze the **overarching plan** for Overseer Kit as a **portable governance system any repo can adopt** — not a VideoFactory-only tool, and not only the “honesty / boss-worker-checker” layer.

This session covers the full stack from **what already shipped (K1–K8)** through **what comes next (K9–K12 / Track N)** and how **consumer repos** (VideoFactory, MuseHub, Scooling, Knowtation) plug in without forking the pattern.

**Hard stops for this session:**
- No implementation code
- No redesign of K1–K8 unless a blocking gap is found
- No merging VideoFactory domain logic into the kit repo (domain packs stay in consumer repos)
- Produce a **K9a frozen contract** + updated `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md`

---

## Repo identity

| Item | Value |
|------|-------|
| **Canonical kit repo** | `OVERSEER_KIT/overseer-kit` (not the stale `~/overseer-kit` stub) |
| **Kit spec (L0, frozen)** | `docs/OVERSEER-KIT-SPEC.md` |
| **Kit roadmap** | `docs/ROADMAP.md` — K1–K8 **DONE**, K9a **▶ NEXT** |
| **Vision draft to expand** | `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md` |

---

## The problem we are solving (whole picture)

1. **Session amnesia** — every new AI chat reinvents context.
2. **Governance doc drift** — roadmap/handover/board say DONE while git/artifacts say otherwise.
3. **Spec mush** — Auto builds against unfrozen interfaces.
4. **Self-certification** — the agent that did the work also marks it passed (worst in paid media).
5. **Copied habits across repos** — same good patterns re-typed in VideoFactory, MuseHub, Scooling, Knowtation; copies drift (four Muse↔Git inversion incidents already paid for).

**Solution shape:** One **versioned, vendored kit** (`overseer init|sync|status|governance-sync|review`) injected into any consumer repo via `.overseer/config.yaml`. Improve once in the kit; sync everywhere.

---

## Layered architecture (L0 → L3) — the whole system, not just honesty

| Layer | Name | What it does | Kit status |
|-------|------|--------------|------------|
| **L0** | Governance | Handover + roadmap (or lane equivalents), phase model, freeze review, governance-sync, model tiers, seven-tier test contract, VCS adapters (`git-only` / `muse-only` / `muse+git-mirror`) | **DONE** (K1–K8) |
| **L1** | Domain checkpoints | Per-work-unit manifest + fail-closed verify scripts after every step (before next spend) | **K9** — generic contract + build; VF is first reference pack |
| **L2** | Honesty / roles | Optional Overseer · Producer · Verifier + hash-chained ledger + verdict co-requirement at handoff/register/DONE | **K10** — ports VideoFactory Track H as opt-in module |
| **L3** | Substrate | Optional MuseHub (signed identity, content-addressed history, realign/mirror) — deepens L0–L2, never gates baseline | **Available** via `muse+git-mirror` adapter; marketing in Track N |

**Key principle:** L0 alone is useful on plain GitHub. L1 stops remake-before-verify waste. L2 stops forged approvals at boundaries. L3 is the on-ramp to MuseHub for orgs that need cryptographic custody — **never required** for kit baseline.

---

## Track map (full program — kit + consumers)

| Track | Home | Intent | Status |
|-------|------|--------|--------|
| **K1–K8** | Overseer Kit | Core governance vendoring, CLI, adapters, freeze reviewer, multi-lane docs | **DONE** |
| **K9a** | Overseer Kit | **This session** — freeze L1 checkpoint plugin + L2 honesty module contracts | **▶ NEXT** |
| **K9b** | Overseer Kit | Build generic L1 orchestrator + policy schema | TODO after K9a |
| **K10** | Overseer Kit | Build L2 honesty module (ledger, roles, co-requirement hooks) | TODO |
| **K11** | Overseer Kit | API/CI freeze provider (headless review in Actions) | TODO |
| **K12 / Track N** | Overseer Kit | Public landing, LICENSE, scenario gallery, GitHub→MuseHub funnel | TODO |
| **FACTORY-WIRE** | VideoFactory | Production invocation wiring (Layer 0 UPFC) | **DONE** |
| **Track H** | VideoFactory → kit L2 | Honest factory org chart + verdict ledger + SIN-35..39 | Spec draft in VF; **port to K10, do not duplicate in kit as VF-only doc** |
| **Track M** | VideoFactory + Muse | Movie/serial continuity, cast registry; Muse `video-timeline` plugin (VID-*) | Prepared; **non-blocking** for K9–K12 |
| **VID-1+** | Muse (`muse-fresh`) | Timeline domain plugin for semantic diff / RationalTime | VID-1 MP open; VF consumes later |

---

## Consumer repos — how they plug in (no forking)

| Consumer | VCS regime | Kit lanes / docs | Domain pack (stays in consumer) |
|----------|------------|------------------|----------------------------------|
| **Overseer Kit** | `muse+git-mirror` (dogfood) | `OVERSEER-HANDOVER.md` + `ROADMAP.md` | — |
| **VideoFactory** | `git-only` | `queue` lane → `VIDEO_PRODUCTION_STATUS_BOARD.md`; handover → `VIDEO_OVERSEER_HANDOVER.md` | Episode board JSON (`review/production/PRODUCTION-STATUS-BOARD.json`), SIN gates, `policy/video-checkpoints.yaml`, verify scripts |
| **MuseHub / Knowtation** | `muse+git-mirror` | `MUSEHUB-OVERSEER-HANDOVER.md` + `MUSEHUB-ROADMAP.md` | Plugin/MCP domain logic |
| **Scooling** | `muse+git-mirror` | Product-specific handover/roadmap | Runtime in `src/phase9a/` |

**Rule:** Kit owns **portable machinery**. Consumers own **domain content** (video gates, plugin APIs, checkpoint definitions). Never hardcode VideoFactory paths in kit core.

---

## VideoFactory relationship (clarify the confusion)

VideoFactory has **three related but separate things**:

1. **L0 governance** — kit installed (`init --migrate`); queue lane on `VIDEO_PRODUCTION_STATUS_BOARD.md`; session relay on `VIDEO_OVERSEER_HANDOVER.md`. Legacy `OVERSEER_HANDOVER.md` + `ROADMAP.md` remain for infra programs (FACTORY-WIRE, Track H).

2. **Episode production board** — `review/production/PRODUCTION-STATUS-BOARD.json` + MD mirror + SOP. This is the **video pipeline truth** (per-BOR gates, quarantine, `verifiedOnDiskAt`). The kit queue lane is a **one-row summary**; the JSON board is the **detailed grid**. Do not abandon the JSON board — it becomes the VF **domain pack** behind the kit lane.

3. **Track H honesty spec** — `docs/thinking/VF-OVERSEER-HONEST-FACTORY-SPEC-20260709.md` (v2, not frozen). This is **L2 source material** for K10, not the kit master spec. Do not treat Track H as the whole overseer plan.

**Option B (VF L1 dogfood):** Per-video `videos/_active/manifest.yaml` + `PROGRESS.md` + `vf_verify_*.py` checkpoints on the video branch. Merged in VF PR #34. Generalize the *pattern* in K9; keep VF YAML/scripts as reference pack.

---

## Why VideoFactory-named files appeared inside the kit repo

Those files (`VIDEOFACTORY-OVERSEER-SETUP.md`, `VIDEOFACTORY-CHECKPOINT-BUILD-PROMPT.md`) were added during **K6 pilot install** as **operator runbooks for the first consumer** — not because VF owns the kit. They are **reference adapters**, not kit architecture. This Thinking session should decide:

- Keep them under `docs/consumers/videofactory/` (or delete from kit and keep only in VF), **or**
- Replace with a generic `docs/CONSUMER-ADAPTER-PATTERN.md` + one VF example in `tests/fixtures/pilot/`

**Recommendation to freeze:** Kit `docs/` should be **kit-neutral**; consumer-specific prompts live in consumer repos or `docs/consumers/<name>/`.

---

## Parallel work (do not block kit on these)

| Work | Where | Blocks kit? |
|------|-------|-------------|
| Muse VID-1 MP (video-timeline) | `muse-fresh` / staging | No — Track M consumes later |
| Knowtation plugin | `gabriel-muse` | No — separate consumer |
| VF BOR-60 production | reel-factory worktree | No — uses existing board + gates |
| Track H H-0.5 threat model | VideoFactory thinking | Informs K10 L2 contract; can proceed in parallel with K9a L1 |

---

## Deliverables for this Thinking session

1. **Expand** `OVERSEER-KIT-LAYERED-HONESTY-VISION.md` — challenge assumptions; add missing domains; confirm L0–L3 boundaries.

2. **Draft K9a frozen contract** (`docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md`):
   - L1 checkpoint plugin: config schema, manifest shape, verify CLI contract, exit codes, extension hook
   - L2 honesty module: opt-in config, ledger format, role enum, co-requirement hook points (no VF-specific gate names in core)
   - Seven-tier test matrix for K9b/K10b
   - Explicit non-goals

3. **Track N seed** (K12): landing page section outline + scenario gallery list (A–E personas) + LICENSE posture — **marketing only**, not new architecture.

4. **Consumer doc hygiene decision** — where VF/MuseHub/Scooling adapter docs live.

5. **Update** `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` — single ▶ NEXT = K9a complete; K9b blocked until freeze review passes.

6. **Run** `/freeze-review-loop` (or `overseer review --freeze`) on the K9a contract before marking Thinking DONE.

---

## Source documents to read (in order)

1. `docs/OVERSEER-KIT-SPEC.md` — frozen L0 architecture  
2. `docs/ROADMAP.md` — K1–K8 done, queue ahead  
3. `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md` — vision to expand  
4. `docs/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md` — lane pattern VF uses  
5. **VideoFactory (reference only, do not copy into kit core):**
   - `VideoFactory/docs/thinking/VF-OVERSEER-HONEST-FACTORY-SPEC-20260709.md` — L2 source (Track H)
   - `VideoFactory/docs/video-production-status-board-sop.md` — episode board domain
   - `VideoFactory/VIDEO_PRODUCTION_STATUS_BOARD.md` — kit queue lane instance
   - `VideoFactory/policy/video-checkpoints.yaml` — L1 reference pack (if present)

---

## Success criteria

- One frozen K9a contract a cheap Auto model can build K9b/K10 against without re-deriving architecture.
- Clear answer: **kit vs consumer** for every artifact type.
- Track H positioned as **L2 / K10 input**, not the master plan.
- Track N positioned as **K12 go-to-market**, not a second spec.
- No VideoFactory-only filenames required in kit `docs/` root after hygiene pass.

---

## Model tier

**Thinking (high)** — `claude-opus-4-8-thinking-high` or equivalent.  
Next build after freeze: **Auto** (`gpt-5.3-codex`) for K9b only.
