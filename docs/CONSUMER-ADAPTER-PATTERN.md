# Consumer adapter pattern

**Purpose:** How any repo adopts Overseer Kit without forking kit core.  
**Normative freeze:** `docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md` §K9.0 / §K9.12.

---

## Simple version

Install the kit, point `.overseer/config.yaml` at your docs, and keep your product-specific
checks in *your* repo. The kit supplies the shared machinery; you supply what “good” means for
your domain.

## Technical version

| Layer | Kit owns | Consumer owns |
| --- | --- | --- |
| **L0** | `init`/`sync`/`status`/`review`/`governance-sync`, templates, adapters | Living docs content, `docs.lanes`, VCS regime |
| **L1** | Orchestrator + policy/manifest schemas + `verify-step` | `policy/checkpoints.yaml`, verify scripts, manifests |
| **L2** | Ledger engine + roles + co-requirement hooks | Hook call sites, domain DoD, optional roster path (`roles_file` — v1 warn/ignore) |
| **L3** | Regime adapters (`realign`/`mirror`) | Choosing `muse+git-mirror` when ready |

---

## Install skeleton

```bash
KIT=/path/to/overseer-kit
REPO=/path/to/consumer

$KIT/cli/ok -C $REPO init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-<consumer>.yaml \
  --non-interactive --dry-run
# then apply without --dry-run
$KIT/cli/ok -C $REPO status --check-footprint
```

Customize only `.overseer/config.yaml` (regime, doc paths, future `checkpoints:` / `honesty:`).

---

## L0 — lanes vs rows vs repos

- **Lanes** — few durable handover/roadmap pairs (`docs.lanes`).
- **Rows / L1 manifests** — many instances of the same concern (videos, papers, closes).
- **Repos** — different trust boundaries or VCS regimes.

See `docs/archive/phases/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md` and vision §5.2.

---

## L1 — domain pack checklist

1. Write `policy/checkpoints.yaml` (`steps` + `templates` + optional `overrides`).
2. Ship `scripts/verify/*` that exit `0`/`≠0` (no placeholders in verified paths).
3. Point `checkpoints.active_manifest` at the active work-unit manifest.
4. Call `overseer verify-step --step …` after every step; never hand-set `verified: true`.
5. Keep detailed grids in consumer boards/JSON; L0 board stays a summary row if needed.

---

## L2 — honesty wiring checklist

1. Enable `honesty:` and set `ledger` path.
2. Set `require_verdict_on` to the hooks you enforce (absent → all three; hook not in list →
   `honesty-status` refuses `4`).
3. At every enabled `board_done` / `handoff` / `register` boundary, call  
   `overseer honesty-status --hook … --artifact …` (pass `--producer-session` when known).
4. Verifier sessions re-run L1/domain scripts and `overseer ledger append --kind verdict`
   (first append auto-writes a genesis line when the ledger is empty — no manual init required).
5. Do not treat producer self-reports as evidence. Optional `roles_file` is path-checked only in
   v1 (enum roles still apply; roster content is not loaded for enforcement).

---

## Reference consumers

Public stubs (boundary only). Sister-product pilot packs are **not** mirrored into
this repository — use fixtures + the migrate guide.

| Consumer | Public stub | Fixture |
| --- | --- | --- |
| Example / custom doc names | `docs/consumers/videofactory/OVERSEER-SETUP.md` | `tests/fixtures/pilot/config-videofactory.yaml` |
| Scooling | `docs/consumers/scooling/OVERSEER-SETUP.md` | `tests/fixtures/pilot/config-scooling.yaml` |
| Knowtation | `docs/consumers/knowtation/OVERSEER-SETUP.md` | `tests/fixtures/pilot/config-knowtation.yaml` |

Migrate steps: `docs/MIGRATE-EXISTING-REPO.md`. Fixture configs: `tests/fixtures/pilot/`.

---

## Positioning (developer-centric — way forward)

**Overseer Kit is governance machinery for developers**, not an end-user frontend product.
The public site and optional local UI explain patterns and point into the suite — they are not
where people “run Overseer” day to day.

| Surface | Role | Audience |
| --- | --- | --- |
| **Public site** (`overseerkit.com` → static `docs/landing/`) | Explain L0→L3 / scenarios; door into the suite | Devs & operators (marketing clarity) |
| **GitHub `overseer-kit`** | Clone, `ok init` / migrate, dogfood, contribute | Primary adopt path |
| **MuseHub** | Optional L3 substrate (signed identity, content-addressed history) | When provenance depth pays |
| **Knowtation** | Sister product — personal knowledge / vault; optional Track O Stage 4 bind | Separate product, not kit core |
| **Scooling** | Sister **product runtime** (task/agent orchestration under `src/phase9a/`) that **consumes** the kit for governance | Product owns runtime; kit never vendors Scooling code |
| **VideoFactory / other repos** | Peer consumers — same kit pattern, domain packs stay in-repo | Same L0–L2 sockets |
| **`ok app` / desktop / hosted-dashboard** | Optional operator tools in the kit checkout | Devs/operators — not a public SaaS |

**Kit vs Scooling (do not conflate):**

- **Kit** = portable governance (`ok`, roadmap/handover, freeze/BV, verify-step, honesty ledger, VCS adapters).
- **Scooling** = the product that can *run* multi-agent task work and wrap kit discipline for its users.
- Other products (Knowtation, VideoFactory, MuseHub) plug in the **same** kit; they are not forks of kit core.

**Public site CTAs (frozen intent):** explain patterns → GitHub (kit) → also MuseHub / Knowtation /
product docs as sibling doors. No browser signup, no chatbot-hosted runtime on `overseerkit.com`.

---

## Hard rules

- Never hardcode another product’s paths into kit core.
- Never require MuseHub for L0–L2 baseline.
- Never use an LLM as the pass/fail authority for measurable artifacts.
- Never claim the kit website or Track Q UI is an end-user product runtime (that lives in consumers
  such as Scooling).
- Never claim a browser-only signup or zero-install Path A until a **product** surface ships it.
