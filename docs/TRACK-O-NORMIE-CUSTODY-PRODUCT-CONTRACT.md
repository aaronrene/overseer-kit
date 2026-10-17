# Track O — Normie custody product contract

**Audience:** product teams wrapping 🆗 Overseer Kit (Scooling, Knowtation, and future
entry products).

**Authority:** restates frozen `docs/archive/phases/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` (§O0.3–§O0.6)
for implementers. **Do not redesign** stages, regimes, or boundaries here — fix the freeze
document via Thinking if the contract must change.

**Kit role:** rule-holder + `ok` CLI. Products own signup wizards that call existing `ok`
surfaces. Track O is **not** a fourth VCS regime, not a vault store, and not a Scooling
dependency.

---

## Stages 1–4 (normie path)

### Stage 1 — Start

Preferred: create a personal space under `muse-only` (no Git required).

Also fully supported: `git-only` (K7 baseline — no Muse required).

Product may wrap: `ok init` (+ regime selection) for a new or empty tree.

Direct init into `muse+git-mirror` is allowed when both substrates are ready at start
(K6 Scooling shape).

### Stage 2 — Work

Living docs (`ROADMAP` + `HANDOVER`) + paste-ready prompts into any chatbot.

Product may hide `ok governance-sync` / `ok status` behind UX; kit CLI remains authority.
Cursor rules/skills are optional boosters, never required.

### Stage 3 — Optional GitHub backup

Allowed regime transition: `muse-only` → `muse+git-mirror` (existing adapters + SD-14 bridge).

**Kit ceremony:** frozen in `docs/archive/phases/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md` and shipped as
`ok upgrade-regime` (`--from muse-only --to muse+git-mirror`; `--dry-run` / `--apply` /
`--live-bridge` / `--force` per §O2.7). Operator runbook:
`docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md`.

Products must **not** ship one-click backup until §O2.6 unlock criteria hold (O2 freeze `pass`
**and** Track O / O3 build-verification `pass`; wrap **only** `ok upgrade-regime`; C6 consent;
never auto C8). Silent config edit of only `vcs.regime` without footprint re-seed is
**forbidden**.

Never required to start; never invent a push-to-`main` shortcut.

### Stage 4 — Optional Knowtation bind

Bind a Knowtation vault root to the same custody identity (below).

Knowtation owns vault bytes + bind UX; the kit does **not** become the vault.

---

## Custody identity

Custody identity means the durable association of:

1. One repo working tree (personal space),
2. That tree's `.overseer/config.yaml` (regime + doc paths),
3. The VCS history selected by the regime (Muse and/or Git),
4. Optionally, a Knowtation vault root bound by the **product** to that same tree.

| Fact | Rule |
| --- | --- |
| Kit stores | Config, footprint, living-doc paths, adapter state — never vault blobs |
| Knowtation stores | Vault markdown/media under its own data roots |
| Scooling stores | Product accounts / runtime — never required for kit custody |
| Shared "same person" claim | Product-owned bind metadata; kit does not mint a global user id |

Products must not invent a kit-side identity registry, SSO, or cross-product account table.

---

## Boundary table (kit vs products)

| Concern | Overseer Kit | Scooling | Knowtation | MuseHub |
| --- | --- | --- | --- | --- |
| `ok init` / regimes / adapters | **Owns** | Consumes | Consumes | `muse-only` dogfood substrate |
| Normie signup / Stage 1–4 wizard | Declares **contract only** | May host entry UX (optional) | Vault bind UX (optional) | Substrate only |
| Personal vault bytes | **Never** | **Never** | **Owns** vault store | History substrate |
| GitHub create-repo / backup button | No UI; ships bridge scripts + `ok upgrade-regime` | Wrap **only after** §O2.6 (O3 BV `pass`) | Wrap **only after** §O2.6 | N/A |
| Operator bridge (SD-14) | Ships K7 scripts + dogfood docs | May wrap later | May wrap later | — |
| Multi-agent runtime | Reference only (`AGENTS.md`) | **Owns** product runtime | — | — |
| Local governance UI | Track Q `ok app` / Tauri (operator) | May point at consumer tree | May point at consumer tree | — |

**K7 MuseHub-optional guardrail:** no MuseHub-only baseline. Every baseline capability
(`init` / `sync` / `status`, drift, footprint, templates, policy, freeze review,
governance-sync) remains fully functional on `git-only`.

**Product rule:** a Scooling account is **not** required to use Overseer Kit. Scooling is
an optional entry product, not a kit dependency.

---

## Rejection table

| Proposal | Verdict |
| --- | --- |
| Require Scooling signup before `ok init` | **Reject** |
| Require Knowtation vault before governance works | **Reject** |
| Require MuseHub for baseline `ok status` / freeze review | **Reject** (K7) |
| Require Cursor IDE for Stage 2 work | **Reject** |
| Require Track Q desktop for Stage 1 | **Reject** |
| Add a fourth VCS regime for "normie mode" | **Reject** |
| Kit hosts vault bytes or Knowtation credentials | **Reject** |
| Product pushes directly to GitHub `main` bypassing `muse-mirror` | **Reject** (SD-14) |
| O1 ships signup UI inside overseer-kit | **Reject** |
| O1 performs live Scooling/Knowtation `ok init` | **Reject** (operator-gated) |
| Silent `vcs.regime` edit for Stage 3 without footprint re-seed | **Reject** |
| Product ships Stage 3 one-click backup before O2 kit ceremony freeze | **Reject** |
| Product ships Stage 3 one-click before O3 build-verification `pass` (§O2.6) | **Reject** |

---

## Allowed regime transitions (summary)

| From | To | Who may perform |
| --- | --- | --- |
| *(none)* | `muse-only` | Product wizard or operator `ok init` |
| *(none)* | `git-only` | Product wizard or operator `ok init` |
| *(none)* | `muse+git-mirror` | Product wizard or operator `ok init` (both substrates ready) |
| `muse-only` | `muse+git-mirror` | Operator via `ok upgrade-regime`; product UX only after §O2.6 |
| `git-only` | `muse+git-mirror` | Operator / later product (explicit Muse init) |
| Any other pair | — | **Forbidden** without a later Thinking freeze |

---

## Hard stops for product implementers

- No inventing kit regimes, CLI semantics, or MuseHub-only baseline features.
- No live consumer `ok init` without named-repo operator consent.
- No Stage 3 one-click until §O2.6 (O2 freeze `pass` **and** O3 build-verification `pass`).
- Wrap Stage 3 **only** via `ok upgrade-regime` — no silent `vcs.regime` edit without footprint re-seed.
- Never `git push` canonical `main` for mirror regimes — use isolated mirror → `muse-mirror` PR
  (SD-14).

## Cross-references

- Freeze: `docs/archive/phases/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md`
- Stage 3 ceremony freeze: `docs/archive/phases/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`
- Stage 3 operator runbook: `docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md`
- Spec regimes/CLI: `docs/OVERSEER-KIT-SPEC.md` §4–§5
- Scooling runbook: `docs/consumers/scooling/OVERSEER-SETUP.md`
- Knowtation stub: `docs/consumers/knowtation/OVERSEER-SETUP.md`
- Migrate path: `docs/MIGRATE-EXISTING-REPO.md`
- K7 bridge / MuseHub-optional: `docs/archive/phases/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`
