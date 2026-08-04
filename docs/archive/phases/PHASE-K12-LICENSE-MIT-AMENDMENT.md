# Phase — K12 §K12.4 LICENSE amendment (Apache-2.0 → MIT)

Status: **DONE** — freeze-review → `pass` (MIT-r1); build-verification → `pass` (MIT-BV-r1).
Operator-directed SPDX flavor swap. Does **not** “make the kit open source” — it already was under
Apache-2.0. This amends only the frozen license identity to **MIT** for house-brand consistency
with the operator’s other open-source projects.

```yaml
phase: K12-LICENSE-MIT
outputs:
- id: k12-license-mit-amendment
  path: docs/archive/phases/PHASE-K12-LICENSE-MIT-AMENDMENT.md
  frozen: true
frozen_inputs:
- id: k12-landing
  path: docs/archive/phases/PHASE-K12-TRACK-N-LANDING-CONTRACT.md
review_stamp:
  reviewed_at: '2026-07-14T18:25:00Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:6c4d46b9f5564aa4404eccdcdb4201d7508811330499a6246b86f51cc63c0f04
```

---

## Simple summary

Change the project license from Apache 2.0 to MIT everywhere people look: the LICENSE file,
package metadata, landing page, local console footer, and validators/tests. Keep the same
copyright holder line. No product, CLI, or engine redesign.

## Technical summary

Amend K12 §K12.4 + §K12.7 license checks so the fail-closed landing validator expects **MIT**.
Auto ships: root `LICENSE` (MIT text), `pyproject.toml` SPDX, `docs/landing/manifest.yaml`,
public landing + scenarios footers, Path B console copy, `tools/landing/validate.py`, and
seven-tier assertion updates. Historical freeze narratives that said “no LICENSE flip *in that
phase*” stay historically true; this amendment is the authorized reopen.

---

## §MIT.0 — Operator decision (authority)

| Item | Value |
| --- | --- |
| Decision | Switch kit SPDX from `Apache-2.0` to `MIT` |
| Authority | Operator (product owner) — brand consistency with other MIT repos |
| Tier | Feature-branch implement + PR = Tier 1 hygiene; merge to `main` remains Tier 3 |
| Non-reason | Not required to “become open source” (Apache already was OSI open source) |
| Accepted trade-off | MIT has a quieter patent posture than Apache-2.0’s explicit patent grant |

---

## §MIT.1 — Amendments to K12 (authoritative)

### §K12.4 — LICENSE (as amended)

Replace the frozen K12 body with:

- **Identifier:** `MIT`
- **Copyright holder line:** `Copyright 2026 Overseer Kit contributors`
- **Rationale:** OSI-approved; short SPDX text; matches operator house brand across projects.

`pyproject.toml` `[project]` MUST include `license = { text = "MIT" }`.

Root `LICENSE` MUST be the standard MIT permission notice including the copyright line above.

### §K12.7 — Validator contract (license row only)

| Check | Failure message prefix |
| --- | --- |
| `LICENSE` contains `MIT` (and matches `manifest.license`) | `license` |

All other §K12.7 rows remain unchanged.

### §K12.1 deliverable table (LICENSE row)

| Path | Purpose |
| --- | --- |
| `LICENSE` | MIT (OSI-approved) |

---

## §MIT.2 — Deliverables (Auto)

| Path | Change |
| --- | --- |
| `LICENSE` | Replace Apache-2.0 text with MIT |
| `pyproject.toml` | `license = { text = "MIT" }` |
| `docs/landing/manifest.yaml` | `license: MIT` |
| `docs/landing/index.html` | Footer link label → MIT |
| `docs/landing/scenarios/index.html` | Footer link label → MIT |
| `docs/landing/HOSTING.md` | License note → MIT current; Apache historical |
| `tools/app/static/index.html` | Overview + footer SPDX → MIT |
| `tools/landing/validate.py` | Fail-closed MIT checks (not Apache) |
| `docs/archive/phases/PHASE-K12-TRACK-N-LANDING-CONTRACT.md` | Amend §K12.1 / §K12.4 / §K12.7 license rows |
| `tests/unit/test_landing_k12.py` | Assert MIT |
| `tests/security/test_landing_security.py` | Fixture LICENSE uses MIT text |
| `README.md` | K12 DONE blurb → MIT |
| `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` | Phase status + promotion row closed |

**Must not modify:** `desktop/package-lock.json` third-party dependency license strings;
Q0 bind/auth; engine Python beyond landing validator; desktop signing secrets.

---

## §MIT.3 — Non-goals

| Out of scope | Reason |
| --- | --- |
| Dual-license Apache+MIT | Operator chose single MIT |
| Relicensing third-party deps | Unrelated npm dependency metadata |
| Claiming patents via MIT | MIT does not add Apache-style patent grant |
| Live DNS / Release republish in this slice | Separate operator Tier-3 work |
| Rewriting historical Q4a/LAC freeze text | Those “no flip *in that phase*” rules were correct then |

---

## §MIT.4 — Seven-tier test matrix

| Tier | Cases |
| --- | --- |
| unit | Manifest `license == MIT`; LICENSE contains `MIT License` + copyright line; validator rejects Apache-only LICENSE when manifest is MIT |
| integration | `validate_landing(kit_root)` green after flip |
| e2e | Landing HTML footers show MIT; Path B static HTML shows MIT; validate_landing ok |
| stress | Existing landing large-HTML stress still passes (copies real LICENSE) |
| data-integrity | `manifest.license` equals SPDX string in `pyproject.toml` and appears in `LICENSE` |
| performance | Validator still <500ms on kit tree (unchanged bound) |
| security | No secrets in LICENSE/HTML; secret-injection fixture still fails closed |

---

## §MIT.5 — Definition of Done

- [x] Freeze-review → `pass` on this artifact
- [x] K12 contract amended as §MIT.1
- [x] All §MIT.2 deliverables landed
- [x] Seven-tier matrix green
- [x] Build-verification → `pass`
- [x] ROADMAP + HANDOVER updated together
- [ ] Feature branch → push → PR (merge Tier 3)

---

## Review-record

**Review record (§6.2):** every freeze-review and build-verification finding MUST cite
**file+line** (`path:line`) per SPEC §6 / K5 C8. Uncited findings are invalid and discarded.
Fixes applied during the loop are Tier 1 (feature branch); merge to `main` is Tier 3 and is never
part of this loop.

| Round | Gate | Verdict | Notes |
| --- | --- | --- | --- |
| MIT-r1 | Freeze-review | **`pass`** | CLI stamp written; artifact_digest `sha256:6c4d46b9…` |
| MIT-BV-r1 | Build-verification | **`pass`** | V1–V7 match §MIT.2; suite **936** passed (1 deselected: env port 8765 busy); test_output sha256 `6ccc33d24227d128eb504f8f69757a5e4d95a2f48bc52aff328cd7c685e20808` |
