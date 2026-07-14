# Consumer adapter pattern

**Purpose:** How any repo adopts Overseer Kit without forking kit core.  
**Normative freeze:** `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md` §K9.0 / §K9.12.

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

See `docs/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md` and vision §5.2.

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

| Consumer | Kit docs |
| --- | --- |
| VideoFactory | `docs/consumers/videofactory/OVERSEER-SETUP.md`, `CHECKPOINT-BUILD-PROMPT.md` |
| Scooling | `docs/consumers/scooling/OVERSEER-SETUP.md` |
| MuseHub / Knowtation | Add under `docs/consumers/<name>/` when piloted |

Fixture configs: `tests/fixtures/pilot/`.

---

## Public website, browser UI, and non-developers (honesty)

| Surface | Role today | Who it is for |
| --- | --- | --- |
| **Public site** (e.g. `overseerkit.com` → static `docs/landing/`) | Explain L0→L3, scenarios, link to GitHub | Everyone — marketing + clarity (K12) |
| **Path A — handover paste** | After a governed repo exists, open the handover and paste the NEXT prompt into **any** chatbot | Non-devs and configs; **no Cursor required** |
| **`ok app` / desktop** | Same local governance UI (loopback) | Operators/devs with a checkout; signed installers not required for developers (build-from-source or `ok app`) |
| **`ok hosted-dashboard`** | Read-only glance of remote ROADMAP/HANDOVER | Operators; **not** a signup product or write console |
| **Zero-install cloud app on the website** | **Not shipped** | Track O contracts exist; signup / Stage 1 product UX lives in consumer products (e.g. Scooling), not in kit core |

**Plain process for a non-developer today (no Cursor):**

1. Someone technical (or a product wrapper) installs the kit into the project once (`ok init` / migrate).
2. The living **HANDOVER** file gets a paste-ready NEXT prompt.
3. The non-developer copies that prompt into ChatGPT / Claude / etc., works the step, then asks the
   agent (or a teammate) to update roadmap + handover honestly before the next session.
4. Merge to `main` stays a human Tier-3 decision.

The website alone does **not** create a governed project yet. It educates and points to GitHub
(and later to product wrappers that call kit CLI under the hood).

---

## Hard rules

- Never hardcode another product’s paths into kit core.
- Never require MuseHub for L0–L2 baseline.
- Never use an LLM as the pass/fail authority for measurable artifacts.
- Never claim a browser-only signup or zero-install Path A until a product surface ships it.
