# Phase — Public landing + console access UX (Thinking freeze)

Status: **Reviewed → `pass` (LAC-r2).** Thinking is **spec-only**; no landing HTML/CSS,
Path B chrome rewrite, README ship edits, or DNS changes land in this phase. The Landing +
access clarity Auto build (`{step}b`) is cleared to start mechanically against this frozen
contract. Do **not** reopen Q0 bind/auth casually. Do **not** claim the website executes tasks
or mints session/CSRF.

```yaml
phase: LANDING-ACCESS-CLARITY
outputs:
- id: landing-access-clarity
  path: docs/archive/phases/PHASE-LANDING-ACCESS-CLARITY.md
  frozen: true
frozen_inputs:
- id: k12-landing
  path: docs/archive/phases/PHASE-K12-TRACK-N-LANDING-CONTRACT.md
- id: landing-hosting
  path: docs/landing/HOSTING.md
- id: q0-overseer-app
  path: docs/archive/phases/PHASE-TRACK-Q-Q0-OVERSEER-APP.md
- id: q4a-ui-redesign
  path: docs/archive/phases/PHASE-TRACK-Q-Q4A-UI-REDESIGN.md
- id: q3-release-installers
  path: docs/archive/phases/PHASE-Q3-RELEASE-DESKTOP-INSTALLERS.md
- id: desktop-runbook
  path: docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md
- id: kit-spec-freeze
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: roadmap
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-14T13:53:22Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:c0ac8162b8d86959c6a01c2201f8e8aa32dfff8120335bbbee4c13882235068a
```

**Downstream edge:** the **Landing + access clarity Auto** build treats this document as ground
truth without re-deriving it (SPEC §6). K12 remains the historical Track N ship; this freeze
**amends** public IA / CTAs / HOSTING honesty for the pre-public gate. Q0 bind + Bearer/CSRF rules
stay closed except the **narrow** `api/health` additive in §LAC.6.3. Q4a/Q4b Structure diagrams
are the SVG source of truth for offline embeds.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main`, DNS cutover, and live capability flips are Tier 3 and are never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| LAC-r1 | Freeze-review (checklist + thinking, `thinking-high`) | findings | **R1-M1** Path 1 step underspecified: installed `.dmg` defaults `repo_root` to bundled kit unless `OVERSEER_REPO_ROOT` is set (no folder picker). **R1-M2** Q0 `api/health` “liveness only” wording needs explicit amendment cite for `repo_root`. **R1-M3** Primary CTA arch label must say Apple Silicon (`aarch64`) only. **R1-C4** CLI blocked on `releases/latest` absolute-path false positive (leading slash). **R1-N1** Auto must not invent GUI repo picker. No true escalation. |
| LAC-r1 fix | Author (cited items only) | — | **R1-M1/N1** Path 1 + §LAC.7 bind honesty + rejection row. **R1-M2** §LAC.6.3 Q0 health amendment. **R1-M3** CTA labels. **R1-C4** rephrased `releases/latest`. |
| LAC-r2 | Freeze-review (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings, dry-run). Semantic re-read confirmed R1 RESOLVED: IA §LAC.3 amends K12; offline SVG embed; Download href frozen to signed v0.1.0 `.dmg`; Paths 1–3 + Path B chrome; `OVERSEER_REPO_ROOT` honesty; narrow health `repo_root` only; domain apex static-only; pre-public DNS gate; rejection table; seven-tier §LAC.12; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §LAC.0 — Simple summary

Visitors need a professional front door that shows how Overseer Kit is structured at a glance,
and operators need an obvious way to open the **local** governance console. A signed Mac
installer now exists on GitHub Release `v0.1.0`; browser Path B still needs paste-from-terminal;
the public site must not pretend to be the live app.

**This freeze locks:** public landing information architecture + visual direction; offline
structure flowcharts on the main page; suite doors + Download / clone CTAs; a single
“Open the local console” playbook (README + landing + Path B Overview); Path B chrome clarity
(bound repo, collapse bootstrap, tab explainers, Status auto-refresh once); domain honesty for
`overseerkit.com`; seven-tier matrix + Definitions of Done for Auto and for “ready to point DNS.”

**Technical summary:** amend `docs/landing/` contract beyond K12 §K12.2 section list; copy Q4b
SVGs under `docs/landing/assets/diagrams/`; wire primary CTA to the live signed `.dmg`; document
Python 3.11+; authorize one additive `repo_root` field on `GET api/health` for chrome honesty;
presentation-only Path B JS/HTML tweaks; extend landing validator + tests. Spec-only this phase.

---

## §LAC.1 — Scope

**In scope (freeze only — this phase writes no product code):**

- Public site IA + visual direction (§LAC.3–§LAC.4).
- Structure flowchart embed rule (§LAC.5).
- Suite doors + CTA hierarchy (§LAC.6.1).
- Single console-access playbook Paths 1–3 (§LAC.6).
- Path B chrome UX clarity (§LAC.6.2–§LAC.6.4).
- Bound-repo honesty (§LAC.7).
- Domain / hosting map (§LAC.8).
- Pre-public DNS gate DoD (§LAC.9).
- Rejection table (§LAC.10).
- Auto deliverable file list (§LAC.11).
- Seven-tier test matrix (§LAC.12).
- Definitions of Done (§LAC.13–§LAC.14).

**Out of scope (explicit non-goals):**

- **Reopening Q0 bind allowlist, CORS, peer check, Bearer + CSRF, cookie/`localStorage` auth.**
- **Public mint of `session_credential` / `csrf_token`** (website, API, or “magic link”).
- **Signup, OAuth, hosted task runner, chatbot runtime, website that “executes tasks.”**
- **Unsigned installer as primary Download CTA** (smoke AppImages / unsigned builds).
- **Claiming Windows/Linux signed installers exist** until Release assets + `signing.status: signed`.
- **Embedding Python in the installer** (Q3-release Auto v1 honesty unchanged).
- **Tier-3 DNS cutover, merge to `main`, staging push, or live gate flips** in Thinking.
- **Hosted governance dashboard redesign** (`ok hosted-dashboard` remains a different command).
- **LICENSE flip** (Apache-2.0 stays; MIT needs separate K12 §K12.4 Thinking).
- **Engine rewrite** beyond the narrow `api/health` additive in §LAC.6.3.

---

## §LAC.2 — Verified baseline (do not invent)

| Fact | Evidence / rule |
| --- | --- |
| Mac signed installer published | GitHub Release `v0.1.0` asset `Overseer.Kit_0.1.0_aarch64.dmg`; manifest signing method `developer_id_notarized`, `signing.status: signed` (operator-verified 2026-07-14) |
| Primary Download href (frozen for Auto v1) | `https://github.com/aaronrene/overseer-kit/releases/download/v0.1.0/Overseer.Kit_0.1.0_aarch64.dmg` |
| Releases index | `https://github.com/aaronrene/overseer-kit/releases/tag/v0.1.0` (and GitHub `releases/latest` for “find current tag”) |
| Win/Linux | **Unavailable** as primary CTAs until secrets exist and a signed Release row ships |
| Host Python | Path C Auto v1 still requires **Python 3.11+** on `PATH` |
| Path B today | `ok app` / `ok app --open`; paste credential + CSRF from **that** terminal; Q4b Overview/Structure shipped |
| Diagrams | `tools/app/static/assets/diagrams/{lanes,regimes,layers,kit-consumer}.svg` (Q4b) |
| Landing today | K12 static tree under `docs/landing/` with DONE status table residue — Auto must strip public WIP/DONE/TODO chrome |
| Domain intent | `overseerkit.com` → static `docs/landing/` only (`HOSTING.md`); not yet operator-wired |

---

## §LAC.3 — Public site IA (frozen)

### §LAC.3.1 — Section order (amends K12 §K12.2 for Auto)

Auto MUST update `docs/landing/manifest.yaml` + `index.html` so section `id`s match this order:

| # | Section id | Visitor job |
| --- | --- | --- |
| 1 | `hero` | Brand + one promise + primary/secondary CTAs |
| 2 | `problem` | Why governance honesty matters (plain language) |
| 3 | `structure` | Four offline structure flowcharts at a glance |
| 4 | `layers` | L0→L3 stack in visitor language (no module jargon dump) |
| 5 | `console-access` | Single “Open the local console” playbook (Paths 1–3) |
| 6 | `suite-doors` | Suite doors (GitHub, MuseHub, Knowtation, Scooling, VideoFactory, Consumer pattern) |
| 7 | `quickstart` | Clone / `ok init` secondary path |
| 8 | `funnel` | GitHub → Kit layers → optional MuseHub |
| 9 | `scenarios` | Link into scenario gallery (personas stay on `/scenarios/`) |

**Removed from public main page (frozen):** `roadmap-public` status table with DONE/TODO/WIP rows;
any “K9b DONE” style phase residue; links that imply the site is a live console.

**Kept:** scenario gallery A–E + badges (`dogfood`/`reference`/`aspirational`) on
`scenarios/index.html` (K12 §K12.3 unchanged). Footer may link SECURITY + LICENSE + HOSTING.

### §LAC.3.2 — Hero copy (frozen intent)

| Element | Rule |
| --- | --- |
| Brand | **🆗 Overseer Kit** — hero-level (not nav-only) |
| Promise | Governance + honesty for phased AI work — without amnesia, fake DONE, or silent drift |
| Subpromise | Portable patterns for any repo; product task runtimes live in sister projects |
| Primary CTA | **Download Mac console (Apple Silicon)** → frozen `.dmg` href (§LAC.2) |
| Secondary CTA | **Clone / init on GitHub** → `https://github.com/aaronrene/overseer-kit` |
| Tertiary | Scenarios · MuseHub · Knowtation (suite doors; not primary) |

**Forbidden hero claims:** “Run agents here”, “Sign up”, “Open live console on this domain”,
“Windows/Linux download ready”, “No Python required”, “Pick any folder in the app” (no picker).

### §LAC.3.3 — Visitor language (frozen)

Prefer: phases, living docs, checkpoints, independent review, local console.  
Avoid on the main page: DONE/TODO/WIP status boards, freeze-contract digests, Tier jargon unless
a short glossary footnote is needed. Developer detail stays in linked docs.

---

## §LAC.4 — Visual direction (frozen)

| Concern | Frozen choice |
| --- | --- |
| Medium | Static HTML + CSS only; **no** external script CDN; **no** analytics tags |
| Palette | Refine existing Track N tokens (`docs/landing/assets/style.css`): dark surface, green accent, clear hierarchy — professional explainer, not a neon “AI dashboard” |
| Type | System / UI stack OK; larger display scale for brand + H1; readable body ≥16px |
| Layout | One composition in the first viewport: brand, one headline, one short support line, CTA group — then diagrams |
| Diagrams | Offline SVG embeds; captions + text fallbacks (same accessibility rule as Q4a §Q4A.6.5) |
| Cards | Allowed only for suite-door / persona interaction blocks — not in the hero |
| Motion | Optional subtle CSS only; no JS animation framework |
| Residue strip | Auto MUST remove public DONE/TODO/WIP tables and “dev residue” from main landing |

---

## §LAC.5 — Structure flowcharts (frozen)

### §LAC.5.1 — Assets

Auto MUST copy (byte-stable or regenerated-from-same mermaid as Q4a §Q4A.6) into:

| Landing path | Source |
| --- | --- |
| `docs/landing/assets/diagrams/lanes.svg` | `tools/app/static/assets/diagrams/lanes.svg` |
| `docs/landing/assets/diagrams/regimes.svg` | `tools/app/static/assets/diagrams/regimes.svg` |
| `docs/landing/assets/diagrams/layers.svg` | `tools/app/static/assets/diagrams/layers.svg` |
| `docs/landing/assets/diagrams/kit-consumer.svg` | `tools/app/static/assets/diagrams/kit-consumer.svg` |

**Offline rule:** no runtime Mermaid CDN. Captions match Q4a §Q4A.6.1–§Q4A.6.4 intent (±10% wording).

### §LAC.5.2 — Placement

All four diagrams appear in section `structure` on the **main** landing page (at-a-glance).
Scenario pages may keep ASCII/diagram snippets; they are not required to duplicate the SVG gallery.

---

## §LAC.6 — Console access playbook (frozen)

Canonical title everywhere: **Open the local console**.

Map to existing Track Q Path letters (do not erase A/B/C runbook language):

| Playbook | Track Q letter | Who |
| --- | --- | --- |
| **Path 1** | Path C signed installer | Operators who want a native window (preferred when Mac Release exists) |
| **Path 2** | Path B browser | Developers with Python + kit/consumer checkout |
| **Path 3** | Path C build-from-source | Contributors developing the desktop shell |

### §LAC.6.1 — Path steps (exact intent)

**Path 1 — Download Mac console (preferred for operators on Apple Silicon)**

1. Confirm **Python 3.11+** on the host (`python3 --version`).
2. Download the signed **Apple Silicon (`aarch64`)** `.dmg` from the frozen Release asset href (§LAC.2).
3. Optionally verify `SHA256SUMS.txt` + manifest `signing.status: signed` (runbook steps).
4. **Bind a governed checkout before launch:** set `OVERSEER_REPO_ROOT` to the absolute path of
   the consumer (or kit) repo that already has `.overseer/` from `ok init`.  
   **Default without that env var:** the desktop launcher binds `repo_root` to the **bundled kit
   root inside the app resources** (`desktop/src-tauri/src/launcher.rs` `resolve_repo_root`) —
   useful for dogfooding the kit itself, **not** an automatic “pick my project” folder dialog.
5. Open the app; desktop shell auto-fills session bootstrap (same as Path 3 auto-fill).
6. Confirm the chrome shows the expected bound path (§LAC.6.3) before any write action.

Honesty line (must appear near CTA): *Apple Silicon (`aarch64`) Mac · signed+notarized · requires
Python 3.11+. Set `OVERSEER_REPO_ROOT` to your governed repo. Windows/Linux signed installers are
not published yet. No in-app folder picker in Auto v1.*

**Rejected for this Auto:** inventing a GUI repo-folder picker or changing launcher bind defaults
without a dedicated Thinking freeze.

**Path 2 — Browser (`ok app`)**

1. From a governed repo (`.overseer/` present): `ok app --open` (or `ok app` then open the printed URL).
2. In the **same** terminal that started the server, copy `session_credential` and `csrf_token`.
3. Paste into Session bootstrap → Connect.
4. Credentials are process-lifetime only; never commit them; website never mints them.

**Path 3 — Dev desktop**

1. From kit root: `./scripts/bundle-desktop-kit.sh` then `cd desktop && npm install && npm run tauri dev`.
2. Same auto-fill behavior as Path 1 install; still needs Python 3.11+ + Rust/Node for **dev builds**.

### §LAC.6.2 — Surfaces that MUST carry the playbook

| Surface | Requirement |
| --- | --- |
| `README.md` | Dedicated short section “Open the local console” with Paths 1–3 + Python honesty |
| `docs/landing/index.html` `#console-access` | Same three paths; primary visual weight on Path 1 when Mac asset exists |
| Path B Overview (`tools/app/static/`) | Compact Paths 1–3 + bound-repo honesty; link to GitHub Releases for Download |
| `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` | Align §Release vs dev with live Mac Release; keep Win/Linux honest |
| `docs/landing/HOSTING.md` | Domain map + “site does not mint CSRF / does not run console” |

Copy MUST be consistent across surfaces (same path names and order). Wording may tighten ±10%.

### §LAC.6.3 — Path B chrome UX (frozen for Auto)

| Behavior | Rule |
| --- | --- |
| After Connect succeeds | Collapse or hide `#auth-panel` Session bootstrap (may keep a small “Reconnect / new session” control) |
| Bound repo | Show absolute bound checkout path in chrome (header or Overview) from `GET api/health` → `result.repo_root` |
| Overview tabs | Plain-language one-liner for each tab (Status, Roadmap, Handover, Gates, Actions, Ledger, Structure) |
| Status enter | Auto-refresh **once** when the Status tab is activated (manual Refresh remains) |
| Auth | Still in-memory only; no cookies/`localStorage` (Q0 §Q0.6) |

**Narrow Q0 additive (authorized here only):**

Amends Q0 §Q0.7 health result (`docs/archive/phases/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` success `result` for
`GET api/health`) from `{ status, port, bind }` to:

```json
{ "status": "ok", "port": <int>, "bind": "<literal>", "repo_root": "<absolute path>" }
```

| Rule | Detail |
| --- | --- |
| Meaning | Absolute filesystem path of the bound checkout this process mutates (§LAC.7) |
| Auth | Still requires Bearer session credential (Q0 §Q0.6); not anonymous |
| Secrets | Path is local workspace location, not a credential; still **must not** appear in public HTML |
| Non-goals | Does **not** reopen bind allowlist, CORS, CSRF, cookies, or any other `api/*` schema |
| Server touch | Pass `config.repo_root` into `handle_health` only; no engine rewrite |

Q0’s phrase “process liveness only (no repo secrets)” remains: `repo_root` is not a secret and
does not expose living-doc contents. Living docs stay behind existing authenticated doc routes.

### §LAC.6.4 — Overview tab explainers (frozen intent)

| Tab | Plain-language job |
| --- | --- |
| Overview | What this console is; suite doors; how to open it; bound repo |
| Status | Health of governance for the bound repo |
| Roadmap | Living phase board |
| Handover | Next-session relay / paste prompt |
| Gates | Pending honesty/governance reminders |
| Actions | Dry-run-first freeze review + governance-sync + honesty-status |
| Ledger | Append-only honesty ledger view/verify |
| Structure | Full flowchart gallery |

---

## §LAC.7 — Bound-repo honesty (frozen)

| Mechanism | Surface | Meaning |
| --- | --- | --- |
| Process cwd + `.overseer` walk | Path 2 (`ok app`) | Default when `--repo` omitted (`cli/paths.py` `resolve_repo_root`) |
| `--repo PATH` | Path 2 | Explicit bind for `ok app` |
| `OVERSEER_REPO_ROOT` | Path 1 / Path 3 | Desktop launcher bind when set (`desktop/.../launcher.rs`) |
| Default without env | Path 1 / Path 3 | **Bundled kit root** (not a consumer project picker) |

**Frozen statement (must appear in playbook + Overview):**  
*This console is bound to one local checkout. Reads and writes (when confirmed) apply only to that
tree — not to overseerkit.com and not to arbitrary remote repos. Desktop Path 1/3: set
`OVERSEER_REPO_ROOT` to your governed repo; otherwise the shell binds the bundled kit.*

Auto MUST NOT invent multi-repo switcher UI or a folder picker in this phase.

---

## §LAC.8 — Domain map (frozen)

| Host | Content |
| --- | --- |
| `overseerkit.com` (apex) | Static landing ONLY (`docs/landing/`) |
| Optional `docs.overseerkit.com` | Static docs mirror (still not a live `ok app`) |
| Any `app.*` / `console.*` subdomain | **Forbidden** if it pretends to host live Path B/C without a separate Thinking freeze |
| Hosted dashboard | Different CLI: `ok hosted-dashboard` — must not be branded as the apex product console |

**HOSTING.md Auto updates:** replace outdated “signed installers optional later / developers clone”
primary-path wording with Path 1 Mac Release honesty + Python 3.11+; keep “not a product runtime.”

---

## §LAC.9 — Pre-public gate (ready to point DNS)

Operator may point DNS to the static host **only when all are true:**

1. Landing + access clarity Auto seven-tier matrix green (§LAC.12) + `/build-verification-review` → `pass`.
2. Access playbook present on README + landing `#console-access` + Path B Overview.
3. Primary Mac Download CTA `href` resolves to a Release asset with `signing.status: signed` (frozen
   v0.1.0 `.dmg` or a later signed tag Auto retargets **only** via governance note — never unsigned).
4. No unsigned-as-primary marketing; Win/Linux not claimed ready.
5. HOSTING.md matches §LAC.8; no subdomain marketed as live `ok app`.
6. No public CSRF/session mint claims anywhere on the site.

**DNS cutover itself remains Tier 3** (human operator). This freeze does not authorize it.

---

## §LAC.10 — Rejection table + hard stops

| Proposal | Verdict |
| --- | --- |
| GUI folder picker / multi-repo switcher in Auto | **Reject** (needs dedicated Thinking) |
| Website mints or proxies `session_credential` / CSRF | **Reject** |
| `app.overseerkit.com` as live Path B | **Reject** (needs dedicated Thinking + security) |
| Primary CTA = unsigned smoke AppImage / unsigned `.dmg` | **Reject** |
| “No Python required” for Auto v1 Path C | **Reject** |
| Signup / OAuth / task runtime on landing | **Reject** |
| Reopen non-loopback bind or disable auth | **Reject** |
| New `api/*` beyond health `repo_root` additive | **Reject** (later freeze) |
| LICENSE → MIT in this phase | **Reject** |
| Tier-3 merge / DNS in Thinking session | **Reject** |

Escalate to human (`security` / `gates_tier3`) if Auto attempts any of the above.

---

## §LAC.11 — Auto deliverables (file list)

| Path | Action |
| --- | --- |
| `docs/landing/index.html` | Rewrite IA per §LAC.3; embed diagrams; CTAs; console-access |
| `docs/landing/scenarios/index.html` | Nav/copy parity; keep persona badges |
| `docs/landing/assets/style.css` | Visual direction §LAC.4 |
| `docs/landing/assets/diagrams/*.svg` | Four offline SVGs (§LAC.5) |
| `docs/landing/manifest.yaml` | Section ids per §LAC.3.1 |
| `docs/landing/HOSTING.md` | Domain + Download honesty |
| `tools/landing/validate.py` (+ schema if needed) | Enforce new section ids, Download href allowlist, forbidden strings |
| `README.md` | “Open the local console” playbook |
| `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` | Align with live Mac Release |
| `tools/app/engine.py` + `tools/app/server.py` | Narrow `api/health` `repo_root` additive only |
| `tools/app/static/index.html` + `assets/app.js` (+ CSS as needed) | Chrome UX §LAC.6.3–§LAC.6.4; Overview playbook |
| `tests/` | Seven-tier harness §LAC.12 |
| `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` | Governance sync after BV `pass` |

**Must not modify for Auto DONE:** Q0 freeze artifact text (except citing this additive),
`LICENSE`, desktop signing secrets, non-loopback bind defaults.

---

## §LAC.12 — Seven-tier test matrix (Auto must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | Manifest section ids match §LAC.3.1; primary Download href equals frozen `.dmg` URL; forbidden strings absent (`Sign up`, `Create account`, `executes tasks`, `mint`+`csrf`/`session_credential` on landing); no DONE/TODO/WIP status table on main landing; four diagram paths referenced; health result schema documents `repo_root`. |
| **integration** | `validate_landing` green on kit tree; relative doc links exist; `api/health` returns `repo_root` with Bearer; Path B static still serves; unknown `api/` still rejected. |
| **e2e** | Landing fixtures validate; start `ok app` → Connect → auth panel collapsed/hidden → Overview shows bound path + Paths 1–3 → Status auto-fetches once on tab enter → SIGINT `0`. |
| **stress** | Concurrent static GETs of landing SVGs + `api/health` (≥20) do not crash or leak credentials into responses. |
| **data-integrity** | Landing SVG files non-empty well-formed `<svg>`; checksum-stable across two runs; Download href host is `github.com` releases path only. |
| **performance** | Landing validator completes within existing K12 performance bound class; health additive adds no full-repo walk. |
| **security** | No external script tags; no secret heuristics; CSRF/session never appear as minted values in HTML; `repo_root` only on authenticated health; bind/auth non-loopback rules unchanged; no auth-disable. |

---

## §LAC.13 — Definition of Done (Thinking freeze)

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [x] Review-record table stamped; `review_stamp` filled
- [x] `docs/ROADMAP.md` row → DONE (Thinking); Auto remains TODO gated on this contract
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for Landing + access clarity Auto
- [x] No landing/UI/README product rewrite landed in Thinking itself (governance + this artifact only)
- [x] No Tier-3 DNS/merge performed

## §LAC.14 — Definition of Done (Auto build)

- [x] Mechanical implementation matches §§LAC.3–LAC.8 and §LAC.11
- [x] Seven-tier matrix §LAC.12 green
- [x] `/build-verification-review` → `pass` before ROADMAP Auto → DONE (**LAC-BV-r1**)
- [x] Closed Q0 bind/auth unchanged except §LAC.6.3 health additive (diff proof in BV)
- [x] Pre-public checklist §LAC.9 items 1–6 ready for operator DNS (DNS itself still Tier 3)
- [x] Governance sync (ROADMAP + HANDOVER) in the closing commit
- [ ] Feature-branch push / PR only; merge remains Tier 3

---

## §LAC.15 — Boundary & capability table

| Concern | This phase (after Auto) | Not this phase |
| --- | --- | --- |
| Explain kit + diagrams on overseerkit.com | Yes (static) | Live governance server on apex |
| Download signed Mac console | Yes (link to GitHub Release) | Embed installer binary in repo |
| Open local console Paths 1–3 | Document + chrome clarity | Public session mint |
| Mutate remote repos from website | **Never** | — |
| Merge / DNS / live flips | **Never** (Tier 3 human) | — |

| Capability | `git-only` | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Static landing | Full | Full |
| Path B/C console | Full (local) | Full (local) |
| Muse-only landing features | **None** | **None** (K7) |
