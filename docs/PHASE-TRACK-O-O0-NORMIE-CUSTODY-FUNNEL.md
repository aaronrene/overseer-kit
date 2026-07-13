# Track O / O0 — Normie custody funnel (Thinking freeze DRAFT)

**Status:** **Draft seed only — not yet `frozen: true`.** Open a **Thinking** session, refine this
document, then run `/freeze-review-loop` until `pass` before any Auto build.

**Intent:** Make “your AI work lands in your vault, optionally backed up, Muse-enriched” a
seamless product path for non-developers — without making Overseer Kit Cursor-centric or
Scooling-mandatory.

---

## Simple summary

People who are not developers still want ownership of what they produce with AI: notes, plans,
decisions, and memory that follow *them* across chatbots. Overseer Kit already provides the
governance docs and CLI. What they need next is a **product wrapper**: create a personal space
(ideally Muse-first, no Git required to start), optionally one-click GitHub backup, and optional
Knowtation vault binding — all without teaching them bare `git` or bridge scripts.

## Technical summary

Freeze a **Track O** onboarding contract that composes existing kit regimes (`muse-only`,
`git-only`, `muse+git-mirror`) with consumer product UX (Scooling and/or Knowtation). The kit
remains **rule-holder + CLI**; products own signup wizards that call `ok init`, governance-sync,
and (later) mirror under the hood. Baseline governance must stay fully usable without Muse or
Scooling.

---

## §O0.1 — Scope (Thinking freeze)

Freeze:

1. Identity of Track O vs K6 consumer pilots vs Track Q desktop distribution.
2. Normie path stages: Muse-first create → optional GitHub backup → optional Knowtation bind.
3. Boundary table: kit vs Scooling vs Knowtation vs MuseHub.
4. Explicit non-requirements (no Scooling account required to use the kit).
5. Seven-tier matrix for any future Auto (likely mostly product/docs + thin glue — not core engine).
6. ROADMAP/HANDOVER promotion rules after review `pass`.

**Out of scope for O0:** shipping signup UI, automatic account creation, marketplace plugins,
live consumer installs.

---

## §O0.2 — Boundary table (draft)

| Concern | Kit | Scooling | Knowtation | MuseHub |
| --- | --- | --- | --- | --- |
| `ok init` / regimes / adapters | Owns | Consumes | Consumes | `muse-only` dogfood |
| Normie signup wizard | Declares contract only | May host entry UX | Vault bind UX | Substrate |
| Personal vault bytes | Not the vault | Not the vault | Owns vault store | History substrate |
| GitHub create-repo button | No | Product optional | Product optional | N/A |
| Operator bridge scripts | Ships K7 scripts | May wrap later | May wrap later | — |

**Frozen guardrail (K7):** no core governance feature may be MuseHub-only.

---

## §O0.3 — Normie stages (draft)

```text
1. Start (muse-only or product-managed repo) — no Git required
2. Work via HANDOVER paste in any chatbot + hidden governance-sync
3. Optional: “Add GitHub backup” → upgrade to muse+git-mirror
4. Optional: bind Knowtation vault to same custody identity
```

Dev path (terminal + `cli/ok` + bridge) remains for operators; normie path is the same adapters
behind a simpler shell.

---

## §O0.4 — Definition of Done (Thinking)

- [ ] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [ ] `frozen: true` + `review_stamp` filled
- [ ] ROADMAP Track O / O0 → DONE (Thinking); O1 Auto gated on contract
- [ ] No product UI code landed in the Thinking phase
- [ ] No Tier-3 merge performed as part of freeze

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §4 regimes, §8 migration
- `docs/K6-PILOT-OPERATOR-RUNBOOK.md` — operator (dev) path
- `docs/consumers/scooling/OVERSEER-SETUP.md` — first consumer
- `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` — UI surfaces today
- `docs/ROADMAP.md` exploration backlog — Track O entry
