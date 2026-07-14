# Phase K12 — Track N public landing (Frozen contract)

Status: **Frozen for K12 Auto build.**

Sources: `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md` §8; K9a §K9.13; ROADMAP K12 row.

## Simple summary

Ship a **public-facing landing** and **scenario gallery** so adopters understand L0→L3 without
reading the full spec. Add an **OSI LICENSE**, **SECURITY.md**, and a clear **GitHub → Kit →
MuseHub** funnel. This is marketing and clarity only — no new architecture, CLI commands, or
L1/L2 module changes.

## Technical summary

K12 delivers static assets under `docs/landing/`, root `LICENSE` (MIT; amended from Apache-2.0
via `docs/PHASE-K12-LICENSE-MIT-AMENDMENT.md`), root `SECURITY.md`,
and `tools/landing/validate.py` — a fail-closed validator the seven-tier test matrix runs against
a frozen `docs/landing/manifest.yaml` contract. Scenario personas A–E match vision §6; each card
carries a **status badge** (`dogfood` | `reference` | `aspirational`) to prevent overclaim.
GitHub Pages can serve `/docs/landing/index.html` from the repo default branch.

---

## §K12.0 — Non-goals (frozen)

| Out of scope | Reason |
| --- | --- |
| New CLI commands | Track N is marketing, not product runtime |
| L1/L2 redesign | K9a contract frozen |
| MuseHub-only features | K7 guardrail |
| Plugin marketplace UI | Vision §9 — avoid until 2+ domain packs dogfood |
| External analytics / third-party JS | Security; static HTML + CSS only |
| Provenance badge automation | K9a §K9.14 — marketing copy only; technical = mirror SHA |

---

## §K12.1 — Deliverables (frozen)

| Path | Purpose |
| --- | --- |
| `LICENSE` | MIT (OSI-approved; K12-LICENSE-MIT amendment) |
| `SECURITY.md` | Coordinated disclosure policy |
| `docs/landing/index.html` | Main landing (§8 sections) |
| `docs/landing/scenarios/index.html` | Scenario gallery A–E |
| `docs/landing/assets/style.css` | Shared styles (no external CDN) |
| `docs/landing/manifest.yaml` | Machine-readable section + persona contract |
| `tools/landing/validate.py` | Fail-closed landing validator |
| `docs/PHASE-K12-TRACK-N-LANDING-CONTRACT.md` | This freeze doc |

---

## §K12.2 — Landing sections (frozen order)

| # | Section id | Heading theme | Source |
| --- | --- | --- | --- |
| 1 | `hero` | Name, promise, subpromise, CTA | Vision §8.1 |
| 2 | `problem` | Agents forget, self-approve, skip tests | Vision §8.2 #1 |
| 3 | `l0` | Roadmap + handover in 60 seconds | Vision §8.2 #2 |
| 4 | `l1` | Mechanical checkpoints | Vision §8.2 #3 |
| 5 | `l2` | Boss / worker / checker honesty | Vision §8.2 #4 |
| 6 | `l3` | Optional MuseHub substrate | Vision §8.2 #5 |
| 7 | `modularity` | Lanes, modules, domain packs | Vision §8.2 #6 |
| 8 | `personas` | Studios, labs, classrooms, treasuries | Vision §8.2 #7 |
| 9 | `quickstart` | Git-only in 5 minutes | Vision §8.2 #8 + `GIT-ONLY-QUICKSTART.md` |
| 10 | `musehub-upgrade` | Same CLI, deeper history | Vision §8.2 #9 |
| 11 | `roadmap-public` | K9–K12 public status | Vision §8.2 #10 |
| 12 | `funnel` | GitHub → Kit → MuseHub | Vision §8.3 funnel graphic brief |

Each section MUST appear on `index.html` with `id="<section id>"`.

---

## §K12.3 — Scenario gallery personas (frozen)

| Id | Persona | Status badge | Vision ref |
| --- | --- | --- | --- |
| A | Video studio | `dogfood` | §6.3 — VideoFactory reference |
| B | Research paper pipeline | `reference` | §6.4 |
| C | Accounting close | `aspirational` | §6.5 |
| D | Classroom / Scooling | `reference` | §6.6 |
| E | Multi-org open source | `dogfood` | §6.7 — kit + CI freeze provider |

Badge rules:

- **`dogfood`** — active or in-repo reference consumer; may say “in use here.”
- **`reference`** — documented pattern; not claimed production PASS in kit repo.
- **`aspirational`** — illustrative; must not imply shipped domain pack in kit core.

Each scenario page entry MUST include: title, pain summary, L0/L1/L2/L3 usage, MuseHub angle
(optional), status badge.

---

## §K12.4 — LICENSE (frozen; amended)

> **Amendment:** `docs/PHASE-K12-LICENSE-MIT-AMENDMENT.md` supersedes the original Apache-2.0
> identifier. Original K12 rationale (patent grant) is preserved as historical rationale only.

- **Identifier:** `MIT`
- **Copyright holder line:** `Copyright 2026 Overseer Kit contributors`
- **Rationale:** OSI-approved; short SPDX; matches operator house brand across open-source projects.

`pyproject.toml` `[project]` MUST include `license = { text = "MIT" }`.

---

## §K12.5 — SECURITY.md (frozen)

Required sections:

1. **Supported versions** — current kit release line (`0.1.x` while VERSION is `0.1.0`)
2. **Reporting a vulnerability** — email placeholder `security@overseer-kit.dev` (no secrets in
   repo); GitHub private advisory as alternate
3. **Response expectations** — acknowledge within 72h; patch on critical on best effort
4. **Out of scope** — consumer domain packs, third-party MuseHub runtime

---

## §K12.6 — Tone and funnel copy (frozen)

**Tone (vision §8.4):** Not “another agent framework.” Governance + honesty for people who
already use Cursor/GitHub. MuseHub is optional power, not homework.

**Funnel steps (must appear on landing):**

1. Start on **GitHub** — clone kit, `overseer init --regime git-only`
2. **Layer honesty** — add L1 checkpoints, L2 ledger when stakes rise
3. **Upgrade optional** — flip to `muse+git-mirror` when provenance matters; bridge workflow
   vendored on sync

Links MUST point to in-repo docs (`GIT-ONLY-QUICKSTART.md`, `K7-DOGFOOD-OPERATOR-RUNBOOK.md`)
using relative paths from `docs/landing/`.

---

## §K12.7 — Validator contract (frozen)

`tools/landing/validate.py` exposes:

```python
def validate_landing(kit_root: Path) -> ValidationResult:
    """Return ok=True or ok=False with human-readable errors."""
```

Checks (fail-closed):

| Check | Failure message prefix |
| --- | --- |
| `manifest.yaml` parses | `manifest_parse` |
| All §K12.2 section ids present in `index.html` | `missing_section` |
| All §K12.3 persona ids present in `scenarios/index.html` | `missing_persona` |
| Each persona has a status badge class | `missing_badge` |
| `LICENSE` contains `MIT` (matches `manifest.license`) | `license` |
| `SECURITY.md` contains `Reporting a vulnerability` | `security` |
| No `http://` script/src in landing HTML (HTTPS relative OK) | `external_script` |
| No patterns matching secret leak heuristics (same as kit security tests) | `secret_leak` |

Exit codes when run as CLI: `0` ok, `1` validation failure.

---

## §K12.8 — Seven-tier test matrix (frozen)

| Tier | Cases |
| --- | --- |
| unit | Manifest schema; section-id list; persona-id list; badge enum; LICENSE header parse |
| integration | `validate_landing` on fixture-complete tree; relative doc links exist |
| e2e | Full kit tree validates green; scenarios page links back to landing |
| stress | Validator on duplicated large HTML block completes bounded (<2s on fixture) |
| data-integrity | Manifest section order matches contract; badge counts stable on re-run |
| performance | Validator completes <500ms on real kit tree (CI-friendly bound) |
| security | Secret patterns absent; no inline `eval`; no external script tags |

---

## §K12.9 — Definition of Done (K12)

- [ ] All §K12.1 deliverables present
- [ ] Validator green on kit root
- [ ] Seven-tier K12 tests green; full suite green
- [ ] README links to landing; status reflects K12
- [ ] `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together
- [ ] No secrets committed

---

## §K12.10 — Cross-references

- `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md` §6–§8
- `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md` §K9.13
- `docs/GIT-ONLY-QUICKSTART.md`
- `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md`
