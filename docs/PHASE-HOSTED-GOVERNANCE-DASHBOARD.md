# Phase Hosted governance dashboard — Thinking freeze

Status: **Reviewed → `pass` (HGD-r3).** Hosted governance dashboard Thinking is **spec-only** and
now frozen; no dashboard server, no fetch client, no static UI, and no new CLI command land in this
phase. The Hosted governance dashboard Auto build (`{step}b`) is cleared to start mechanically
against this frozen contract; it is the only phase that writes hosted-dashboard runtime files. Do
**not** re-derive this contract during the Auto build. Do **not** merge scopes with Track Q
(`docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md`).

```yaml
phase: HOSTED-GOV-DASH
outputs:
- id: hosted-governance-dashboard
  path: docs/PHASE-HOSTED-GOVERNANCE-DASHBOARD.md
  frozen: true
frozen_inputs:
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: k7-musehub-optional
  path: docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
- id: track-q-q0-local-contrast
  path: docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md
- id: kh1-handover
  path: docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: p-deploy-boundary
  path: docs/PHASE-TRACK-P-P-DEPLOY.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: roadmap-exploration
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-14T00:27:51Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:af8419e15e206dbbbcee006ea5d852b103b349f58529df044f7484db1a247f57
```

**Downstream edge:** the Hosted governance dashboard Auto build treats this document as ground
truth without re-deriving it (SPEC §6 mandatory reviewed freeze). Track Q (`ok app` local UI) is
**not** an input and must not be rewritten from this freeze. P-deploy / deploy-verification remain
claim-recording gates only — this dashboard never deploys and never probes production product URLs.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| HGD-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist dry-run **pass** (0 findings). Semantic review raised non-escalating completeness/consistency findings below. No `security`/`irreversible`/`real_money`/`gates_tier3` escalation. |
| HGD-r1 fix | Author (cited items only) | — | **R1-M1** fixed: §HGD.5.5–§HGD.5.7 freeze response field contracts. **R1-M2** fixed: §HGD.4.2 discovery bounded to configured orgs + allowlist element shape. **R1-M3** fixed: §HGD.6.1 table + preview auth = Bearer from env/startup. **R1-M4** fixed: §HGD.11 upstream auth → HTTP `502` + token. **R1-N1** fixed: §HGD.0 viewer-vs-preview wording. **R1-N2** fixed: default ref = `github_meta` default_branch. **R1-N3** fixed: §HGD.6.5 public anonymous policy deferred/off in v1. |
| HGD-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | R1 items confirmed addressed on re-read. Residual: SSRF status dual-coded; upstream host allowlist not frozen; UI viewer-token bootstrap unspecified. No escalation categories. |
| HGD-r2 fix | Author (cited items only) | — | **R2-M1** fixed: §HGD.6.6 default upstream host allowlist. **R2-N1** fixed: SSRF → HTTP `403`. **R2-N2** fixed: §HGD.6.7 UI Bearer paste bootstrap. |
| HGD-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings, dry-run). Semantic re-read confirmed R1/R2 items RESOLVED: response field contracts; bounded allowlist/discovery; Bearer viewer auth + UI bootstrap; upstream host allowlist; HTTP `502`/`403` tokens locked; Track Q separation + rejection table; K7 baseline; seven-tier matrix complete; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §HGD.0 — Simple summary

Operators already keep ROADMAP and HANDOVER honest in each repo. Sometimes they want to **see an
org's governance at a glance** in a browser — without opening a local working tree, and without
giving a remote UI power to change git or muse. The **viewer** of a deployed hosted instance does
not need a kit install; the optional `ok hosted-dashboard` CLI is operator **preview/dogfood**
only (§HGD.10).

**This freeze defines a hosted, read-only governance dashboard:** it reads roadmap, handover, and
gate-related signals from GitHub and optional MuseHub APIs (or documented equivalents), and shows
them. It never mutates remote history, never runs the local `ok` engine against a checkout, and
never becomes a product data store or CD system. Track Q stays the local act-capable UI; this
dashboard stays remote and read-only.

**Technical summary:** freeze product identity vs Track Q; closed remote read surface; document-
derived gate view plus optional advisory CI checks; read-only credential scopes; K7-compatible
capability tiers; rejection table; Auto deliverables under `tools/hosted_dashboard/`; seven-tier
matrix. Spec-only — no code in Thinking.

---

## §HGD.1 — Scope

**In scope (freeze only — this phase writes no code):**

- Product identity and Track Q contrast (§HGD.2).
- What exists now / verified baseline (§HGD.3).
- Data plane: remote APIs only (§HGD.4).
- Closed read surface (HTTP + parse contracts) (§HGD.5).
- Auth + credential scope rules for hosted exposure (§HGD.6).
- Gate-status semantics (document-derived vs advisory) (§HGD.7).
- Boundary + capability tiers (§HGD.8).
- Rejection table (§HGD.9).
- Auto build deliverables (§HGD.10).
- Fail-closed / error behavior (§HGD.11).
- Seven-tier test matrix for Auto (§HGD.12).
- Hard stops + tier linkage (§HGD.13).
- Definitions of Done (§HGD.14).

**Out of scope (explicit non-goals — prevent creep):**

- **Any local git / muse / filesystem mutation** of consumer or kit working trees.
- **Any Track Q rewrite** — no change to `ok app`, loopback bind policy, Bearer/CSRF local auth,
  or the Q0 closed `api/*` act surface.
- **CD / deploy / live product health probes** — unchanged from P-deploy: kit never deploys and
  never HTTP-probes production product URLs; this dashboard is not a deploy console.
- **Hosting product domain data stores** (user content, wallets, media, vault blobs, agent
  transcripts as a service of record). Kit remains governance presentation, never a product
  runtime or primary store.
- **Model hosting, agent dispatch, OpenRouter, Cursor SDK, worker/checker runtime.**
- **Write-capable GitHub/MuseHub tokens or endpoints** (PRs, merges, content updates, webhooks that
  mutate).
- **Re-implementing KH2/KH3/substrate hard gates** inside the hosted process as authoritative
  truth (those gates run in a local working tree via `ok`).
- **Tier-3 merge, staging push, or live capability flips** authorized by this freeze.
- **Multi-tenant SaaS billing / real-money metering** inside the kit Auto build.

---

## §HGD.2 — Product identity vs Track Q (frozen)

| Concern | Track Q — `ok app` | Hosted governance dashboard |
| --- | --- | --- |
| Where it runs | Operator machine; loopback process | Operator- or org-hosted web surface (non-loopback expected when deployed) |
| Data plane | Local filesystem + local VCS adapters via Python engine | GitHub / MuseHub **read** APIs (or documented equivalents) |
| Authority | CLI parity for scoped read **and** gated acts | **Read-only** presentation; no remote write authority |
| Typical user | Operator with a checkout | Operator / reviewer without a local install |
| Mutate living docs / freeze stamp | Yes (inert-first, CLI parity) | **Never** |
| Relationship | Local frontend of governance | Remote glance surface of governance |

**Frozen one-liner:** Hosted governance dashboard is a **read-only remote viewer of published
governance artifacts**, never a second engine, never a Track Q port, never a product runtime.

**Scope separation rule (frozen):** Auto must not import Track Q HTTP handlers as the hosted
data path, and must not teach `ok app` to bind non-loopback “for hosting.” Distinct modules;
distinct auth; distinct bind/deploy story.

---

## §HGD.3 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Local UI | `ok app` loopback stdlib server + static UI; closed act+read `api/*` | Track Q Q0–Q3 |
| Living docs | ROADMAP + HANDOVER paths from `.overseer/config.yaml` | KH1, K8 |
| Gate reminders | Pending-gates surfaces on `ok status` / governance-sync | KH1b |
| Hard gates | Muse-sync + footprint self-integrity refuse certain CLI paths | KH2, KH3 |
| Public web today | Landing + scenario gallery only | K12 |
| Remote governance viewer | **None** | Exploration backlog row (this freeze) |
| Kit boundary | Repo-agnostic governance; not a product runtime | `AGENTS.md` |
| Deploy claims | Ledger/gate only; never deploy/probe | P-deploy |

This Thinking phase **adds no runtime**. Auto later **adds** a hosted read path without changing
existing `ok app` or CLI gate semantics.

---

## §HGD.4 — Data plane (frozen)

### §HGD.4.1 — Allowed sources (closed vocabulary)

| Source id | Role | Baseline? |
| --- | --- | --- |
| `github_contents` | Read file bytes for living docs / marker files via GitHub Contents (or raw-content) API | **Yes — baseline** |
| `github_meta` | Read repo metadata needed for org/repo listing (name, default branch, visibility the token may see) | **Yes — baseline** |
| `github_checks_advisory` | Optional commit/check-run summaries labeled **advisory** only | Optional |
| `musehub_read` | Optional MuseHub (or Muse bridge) **read** API for canonical Muse-side doc bytes when configured | Optional deepen — **never** sole baseline (K7) |

No other source ids in Auto v1. Adding a source requires a later Thinking freeze.

### §HGD.4.2 — Repo eligibility (frozen)

**Allowlist element shape (frozen):** each `org_allowlist` entry is a string `owner/repo`
matching `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`. Org-only entries (`owner` without `/repo`) mean:
enumerate repositories visible to the credential under that `owner`, then apply the marker filter
below. Enumeration is capped at a documented bound (Auto MUST pick and test a finite cap,
default sketch `100` repos per org per refresh); never unbounded internet search.

**Default ref (frozen):** for each eligible repo, resolve `ref` = `default_branch` from
`github_meta` (fail closed if missing). No caller-supplied arbitrary ref query in Auto v1.

A repo appears in the org glance only when **all** of the following hold:

1. **Membership:** the repo is listed explicitly as `owner/repo` in `org_allowlist`, **or** it was
   enumerated under an org-only allowlist entry **and** discovery finds kit marker file
   `.overseer/config.yaml` on the resolved default branch.
2. **Readability:** the credential can read the required paths (otherwise repo shows as
   `unreadable`, never as fabricated green status).
3. **Doc paths:** ROADMAP / HANDOVER paths come from:
   - Parsed `.overseer/config.yaml` living-doc keys when readable, else
   - Kit defaults `docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` (documented fallback only).

If `org_allowlist` is empty → org summary returns zero repos (fail closed; no implicit “scan my
token’s entire universe”).

Arbitrary `?path=` reads of any file in any repo are **forbidden**. Closed path set only
(§HGD.5).

### §HGD.4.3 — Caching (frozen)

- In-memory or operator-configured ephemeral cache of **fetched bytes + content sha256** is
  allowed for performance.
- The kit Auto build **must not** introduce a kit-owned durable multi-tenant database of consumer
  governance documents as a product store of record.
- Cached copies are never authoritative over the remote API response at refresh time.
- Cache must not store raw OAuth/PAT secrets.

### §HGD.4.4 — Equivalence clause

Where MuseHub or a future Git host exposes a Contents-equivalent read API, Auto may implement an
adapter behind the same closed source ids / response shapes. Behavior and fail-closed rules stay
identical; Muse deepen remains optional.

---

## §HGD.5 — Closed read surface (frozen)

URL paths below are written **without** a leading slash so the §K5.5 checklist absolute-path
detector does not false-positive; Auto implements them as normal absolute URL paths (leading
slash present on the wire).

### §HGD.5.1 — Endpoint set (Auto v1)

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `api/health` | Process liveness; no repo secrets; no doc bodies |
| `GET` | `api/org/summary` | Allowlisted / discovered repos + high-level eligibility |
| `GET` | `api/repos/{owner}/{repo}/roadmap` | ROADMAP text + sha256 + source id + ref |
| `GET` | `api/repos/{owner}/{repo}/handover` | HANDOVER text + sha256 + source id + ref |
| `GET` | `api/repos/{owner}/{repo}/gates` | Gate view per §HGD.7 |
| `GET` | `api/repos/{owner}/{repo}/config-marker` | Redacted presence/parse summary of `.overseer/config.yaml` living-doc paths only — **no** secret values |

Static UI assets are served outside the `api/` prefix.

### §HGD.5.2 — Forbidden methods / routes (frozen)

- Any `POST` / `PUT` / `PATCH` / `DELETE` that mutates git, muse, GitHub, or MuseHub state.
- Endpoints for: `init`, `sync`, `governance-sync`, `review --freeze` stamp write, `ledger append`,
  merge, mirror export, staging push, deploy, live gate flip.
- Proxy endpoints that forward arbitrary upstream URLs (SSRF class).
- Track Q act endpoints (`api/review/freeze`, `api/governance-sync`, `api/ledger/append`, etc.).

### §HGD.5.3 — Success envelope (frozen)

```json
{
  "ok": true,
  "result": {},
  "meta": {
    "source_id": "github_contents",
    "ref": "main",
    "fetched_at": "2026-07-13T00:00:00Z",
    "content_sha256": "lowercase-hex",
    "authoritative_workflow": "local"
  }
}
```

Rules:

- `authoritative_workflow` is always the string `local` (reminder: dashboard is glance-only).
- Doc endpoints’ `result` MUST include `path` (repo-relative), `text` (UTF-8), `sha256`
  (lowercase hex of raw bytes).
- Unknown query keys → HTTP `400`; no upstream call.
- Path params `owner` / `repo` MUST match `^[A-Za-z0-9._-]+$` (fail closed otherwise).

### §HGD.5.4 — `api/health` result (frozen)

`{ "status": "ok", "mode": "hosted-read-only" }` — no tokens, no doc bodies, no org lists.

### §HGD.5.5 — `api/org/summary` result (frozen)

`result` is an object:

| Field | Type | Rule |
| --- | --- | --- |
| `repos` | array | Zero or more repo summary objects |
| `repos[].owner` | string | Owner login |
| `repos[].name` | string | Repo name |
| `repos[].full_name` | string | `owner/name` |
| `repos[].default_branch` | string | From `github_meta` |
| `repos[].eligibility` | string | Closed vocabulary: `eligible` \| `unreadable` \| `no_marker` |
| `repos[].marker_present` | bool | Whether `.overseer/config.yaml` was readable |

No living-doc bodies in this endpoint.

### §HGD.5.6 — `api/repos/{owner}/{repo}/gates` result (frozen)

| Field | Type | Rule |
| --- | --- | --- |
| `document_derived` | object | Always present |
| `document_derived.ok` | bool | `false` on parse failure |
| `document_derived.error` | string or null | Error token when `ok` is false; else null |
| `document_derived.phases` | array | Zero or more `{ "id": string, "status": "TODO\|WIP\|DONE\|BLOCKED" }` when parse succeeds; empty array on failure |
| `document_derived.pending_gates_excerpt` | string or null | Optional short excerpt from HANDOVER pending-gates prose; null if absent |
| `advisory_checks` | object or null | Null when source disabled; else `{ "ok": bool, "label": "Advisory — not kit hard gates", "items": [ { "name": string, "conclusion": string } ] }` |

### §HGD.5.7 — `api/repos/{owner}/{repo}/config-marker` result (frozen)

| Field | Type | Rule |
| --- | --- | --- |
| `present` | bool | Marker file readable |
| `roadmap_path` | string or null | Repo-relative path from parse or null |
| `handover_path` | string or null | Repo-relative path from parse or null |
| `vcs_regime` | string or null | Regime string if present in marker; else null |
| `raw_text` | — | **Forbidden** in Auto v1 (do not return full config YAML) |

---

## §HGD.6 — Auth + credential scopes (frozen)

Hosted non-loopback exposure **requires** authentication. Anonymous public read of **private**
org repos is forbidden.

### §HGD.6.1 — Viewer session (Auto v1 primary path)

| Property | Rule |
| --- | --- |
| Mechanism (primary, frozen for Auto v1) | `Authorization: Bearer <credential>` where `<credential>` is the value of env `OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN` (≥ 128 bits entropy; generated by operator or printed once at preview startup to stderr). OAuth App / GitHub App browser login is **deferred** to a later freeze; Auto v1 MUST NOT require OAuth to reach DONE. |
| Upstream read credential | Separate env `OVERSEER_HOSTED_DASHBOARD_TOKEN` (or documented synonym in the runbook) used only for GitHub/MuseHub **read** APIs — never returned in API JSON. |
| Persistence | Viewer + upstream secrets in process memory (and optionally httpOnly secure cookies mirroring the viewer Bearer on hosted TLS deploys); **never** committed into the kit repo, living docs, or `version.lock`. |
| CSRF | No mutating `api/*` methods in v1. If a session cookie mirrors the viewer Bearer, set `Secure` + `HttpOnly` + `SameSite=Lax` (or stricter) on non-loopback TLS deploys. |

### §HGD.6.2 — Upstream credential scopes (frozen)

Allowed upstream scopes (conceptual; map to GitHub/MuseHub names in Auto docs):

- Repository metadata read
- Contents / file read

**Rejected upstream scopes (non-exhaustive, fail closed if requested or detected):**

- `contents:write` / any content mutation
- `administration` / org admin
- `workflows` write
- Deploy keys with write
- Mirror / push credentials
- Any scope that can open PRs, merge, or delete repos

Startup / config validation MUST refuse to run the hosted server when the configured credential
advertises a rejected write class (when the host API can report granted scopes). If scopes cannot
be introspected, the operator runbook MUST require read-only credentials and Auto tests MUST
prove the code path never calls write HTTP verbs on upstream hosts.

### §HGD.6.3 — Fail closed (auth)

| Condition | Behavior |
| --- | --- |
| Missing / invalid viewer session on `api/*` except documented public `api/health` policy | HTTP `401`; no upstream call |
| Disallowed Origin (CORS allowlist from config) | HTTP `403` |
| Credential with rejected write scope | Refuse process start or refuse org routes with explicit error token `write_scope_refused` |
| SSRF / disallowed upstream host | HTTP `403`; no connect |

**`api/health` auth policy (frozen):** may be unauthenticated for load-balancer probes **only**
when it returns the §HGD.5.4 body with no secrets. All other `api/*` routes require auth.

### §HGD.6.4 — TLS / bind (frozen)

| Mode | Bind | TLS |
| --- | --- | --- |
| Local preview (`ok hosted-dashboard` or equivalent) | Default `127.0.0.1`; loopback-only unless operator opts into documented preview bind | TLS not required on loopback |
| Hosted deploy | Non-loopback allowed **only** behind operator TLS terminator or in-process TLS | TLS required for non-loopback |

No hidden “disable auth” flag in Auto v1.

### §HGD.6.5 — Public anonymous policy (frozen)

Anonymous unauthenticated read of **public** repos is **off in Auto v1** (all `api/*` except
`api/health` still require the viewer Bearer). Enabling public anonymous glance requires a later
Thinking freeze (Tier-2 product decision).

### §HGD.6.6 — Upstream host allowlist (frozen)

Default allowed upstream hosts for Auto v1:

- `api.github.com`
- `raw.githubusercontent.com`

Optional Muse deepen may add exactly the hostnames documented in the operator runbook for
`musehub_read` (finite list; no wildcard `*`). Any other host → refuse with HTTP `403` /
`write_scope_refused` is **not** used here; use error token `upstream_host_refused`. Literal IP
literals and link-local/metadata addresses are always refused.

### §HGD.6.7 — UI viewer bootstrap (frozen)

Static UI prompts once per browser load to paste the viewer Bearer credential (from stderr startup
banner or operator secret store) and holds it in a JS memory variable for `Authorization` headers.
**Forbidden in Auto v1:** persisting the viewer or upstream token in `localStorage`,
`sessionStorage`, or repo-tree files. Cookie mirror of the viewer Bearer is optional on hosted TLS
deploys only (§HGD.6.1).

---

## §HGD.7 — Gate-status semantics (frozen)

The dashboard **does not** run `ok status`, KH2, or KH3 against a remote bare API as
authoritative truth.

### §HGD.7.1 — Document-derived gates (primary)

`GET api/repos/{owner}/{repo}/gates` `result.document_derived` is built only from:

- Parsed HANDOVER tables / verified-snapshot / pending-gates prose already present in fetched
  bytes, and/or
- Parsed ROADMAP Build-status rows (phase id + Status tokens `TODO|WIP|DONE|BLOCKED` when
  present).

If parsing fails → `document_derived.ok: false` with error token; **never** invent `DONE`.

### §HGD.7.2 — Advisory checks (optional)

When `github_checks_advisory` is enabled:

- Populate `result.advisory_checks` from GitHub Checks / status APIs for the resolved ref.
- UI MUST label these **Advisory — not kit hard gates**.
- Advisory red/green MUST NOT be shown as KH2/KH3 pass.

### §HGD.7.3 — Honesty banner (mandatory in UI)

Every repo detail view MUST show: authoritative workflow remains **local** (`ok` CLI / Track Q);
this page is a glance surface only.

---

## §HGD.8 — Boundary & capability tiers (frozen)

| Concern | Hosted governance dashboard | Not this product |
| --- | --- | --- |
| Show org/repo ROADMAP + HANDOVER | Yes (remote read) | — |
| Show document-derived / advisory gates | Yes | Authoritative local hard gates |
| Mutate git / muse / GitHub / MuseHub | **Never** | Local `ok` / human Tier-3 |
| Local working-tree engine | **Never** | Track Q / CLI |
| Model / agent runtime | **Never** | Consumer runtimes |
| Product domain data store | **Never** | Consumer products |
| Deploy / CD / live product probes | **Never** | Operator / CI / P-deploy claims |
| Track Q loopback UI | **Never merge scopes** | Track Q Q0–Q3 |

| Capability | `git-only` (GitHub APIs) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Org glance + doc fetch via `github_*` | **Full (baseline)** | Full (baseline still GitHub-visible mirror/docs as configured) |
| Optional `musehub_read` deepen | N/A / unused | Optional — never required for baseline glance |
| Authoritative hard gates | **Not on this surface** | **Not on this surface** |
| Remote write | **Never** | **Never** |

**K7 guardrail restated:** no core hosted-dashboard feature may be MuseHub-only. GitHub-baseline
read path must work for `git-only` orgs.

---

## §HGD.9 — Rejection table (frozen)

| Proposal | Verdict |
| --- | --- |
| Port Track Q act endpoints to the hosted service | **Reject** |
| Default-bind `ok app` to `0.0.0.0` “so it is hosted” | **Reject** |
| `contents:write` or PR/merge automation from the dashboard | **Reject** |
| Kit-owned durable DB as store of record for all consumer roadmaps | **Reject** |
| Dashboard performs deploys or production HTTP health probes | **Reject** |
| Dashboard claims KH2/KH3 pass from remote advisory checks alone | **Reject** |
| Host product user/vault/wallet data in kit Auto modules | **Reject** |
| MuseHub-only baseline (no GitHub read path) | **Reject** (K7) |
| Thinking phase ships server/UI/fetch code | **Reject** |
| This freeze authorizes merge to `main` | **Reject** (Tier 3) |
| Arbitrary file read API (`path=` escape) | **Reject** |
| Open upstream URL proxy | **Reject** |
| Public anonymous org glance in Auto v1 | **Reject** (§HGD.6.5) |
| OAuth-required DONE for Auto v1 | **Reject** (deferred; Bearer viewer is primary) |

---

## §HGD.10 — Auto build deliverables (frozen)

After freeze `pass`, the Auto build ships **only**:

1. **Library** under `tools/hosted_dashboard/` — source adapters (`github_contents`,
   `github_meta`, optional `github_checks_advisory`, optional `musehub_read`), path allowlist,
   parsers for document-derived gates, envelope helpers, scope refuse helpers.
2. **HTTP read server** (stdlib preferred; new mandatory web framework needs Tier-2 confirm) that
   implements §HGD.5 only.
3. **Static UI** — org summary + repo ROADMAP/HANDOVER/gates views with honesty banner (§HGD.7.3).
4. **CLI preview entry** — exactly one new top-level command id `hosted-dashboard` on `ok`
   (compat shim `overseer` unchanged aside from registration), flags frozen below.
5. **Operator runbook** — `docs/HOSTED-GOVERNANCE-DASHBOARD-OPERATOR-RUNBOOK.md` (read-only
   credentials, TLS, CORS allowlist, K7 note).
6. **Seven-tier tests** per §HGD.12.
7. **SPEC §5 row** additive mention of `ok hosted-dashboard` as read-only remote preview (no
   redesign of other commands).

### §HGD.10.1 — CLI flags (frozen)

```text
ok hosted-dashboard [--port PORT] [--bind ADDRESS] [--config PATH] [--open]
```

| Flag | Default | Rule |
| --- | --- | --- |
| `--port` | `8766` | Integer 1–65535; occupied → exit `2` (no silent port hop). Distinct from Track Q `8765`. |
| `--bind` | `127.0.0.1` | Preview default loopback. Non-loopback only when config explicitly sets
  `hosted_dashboard.allow_non_loopback: true` **and** auth + TLS rules in §HGD.6 hold; else refuse
  exit `2`. |
| `--config` | cwd `.overseer/config.yaml` if present, else explicit required in hosted mode | Path-confined |
| `--open` | off | Optional browser open to local preview URL |

**Startup:** load allowlist + credential env (`OVERSEER_HOSTED_DASHBOARD_TOKEN` upstream read;
`OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN` viewer Bearer — generate ephemeral viewer token at
startup if unset in preview mode and print once to stderr); refuse write scopes; listen; block
until signal; clean exit `0`. Never hardcode secrets.

**Non-goals for the CLI process:** no launchd/systemd unit, no background daemon install in Auto
v1, no mutation of the preview host’s git/muse state.

### §HGD.10.2 — Config block (frozen sketch — Auto fills schema tests)

Optional default-inert:

```yaml
hosted_dashboard:
  enabled: false
  allow_non_loopback: false
  cors_origins: []
  org_allowlist: []
  sources:
    github_contents: true
    github_meta: true
    github_checks_advisory: false
    musehub_read: false
```

Unrecognized keys fail closed at load (same family as other kit config blocks).

---

## §HGD.11 — Fail-closed / errors (frozen)

| Condition | Behavior |
| --- | --- |
| Upstream 404 / missing living doc | `ok: false`, error token `not_found`; HTTP `404` |
| Upstream auth failure | error token `upstream_unauthorized`; HTTP `502` (viewer auth remains `401`; do not conflate) |
| Parse failure for gates | `document_derived.ok: false`; do not fabricate DONE |
| Rate limit | error token `upstream_rate_limited`; bounded retry only if documented; never tight spin |
| Path / owner / repo validation fail | HTTP `400`; no upstream call |
| Write verb attempted in client code | Must be unreachable; security tests assert allowlist of methods `GET`/`HEAD` only to upstream |

Process exit codes for the CLI preview:

| Code | Meaning |
| --- | --- |
| `0` | Clean shutdown |
| `1` | Usage / argument error |
| `2` | Config / bind / scope / listen failure |

No new exit code number is allocated beyond existing kit conventions unless Auto discovers a
collision — then Thinking amendment required before shipping a new code.

---

## §HGD.12 — Seven-tier test matrix (Auto build must satisfy)

The Auto build ships all seven tiers green locally before DONE (`policy/test-tiers.yaml`).

| Tier | Proves |
| --- | --- |
| **unit** | Path/owner/repo validators; allowlist vs discovery marker rules; empty allowlist → zero repos; scope refuse helper rejects write-class scopes; upstream host allowlist accepts only frozen hosts; envelope builder sets `authoritative_workflow: local`; document-derived parser never invents `DONE` on garbage input; default port `8766`; bind refuse without `allow_non_loopback`; endpoint allowlist rejects unknown routes and all mutating methods; config unknown-key refuse; source-id closed vocabulary; viewer Bearer required except `api/health`. |
| **integration** | Fixture HTTP upstream (no real network required) serves Contents-shaped payloads; each §HGD.5 GET returns expected envelope; missing doc → `not_found`; write-scope config → start refuse or route refuse; CORS deny for non-allowlisted Origin; disallowed upstream host → `upstream_host_refused` / HTTP `403`; `api/health` body matches §HGD.5.4; Track Q paths not registered. |
| **e2e** | Start `ok hosted-dashboard` against fixture upstream → authenticate with viewer Bearer (`OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN` or startup-printed ephemeral) → org summary → open roadmap + handover + gates → honesty banner present in UI bytes → SIGINT exit `0`; no files under the fixture repo’s `.git` / `.muse` mutated (mtime/hash invariant). |
| **stress** | Bounded concurrent GETs (≥ 20) against summary/doc routes do not corrupt process state; large ROADMAP/HANDOVER fixture stays bounded in memory (documented cap or streaming hash); org enumeration respects finite cap from §HGD.4.2; no unbounded org crawl beyond allowlist/discovery rules. |
| **data-integrity** | Twin fetch of same ref → identical `content_sha256`; cache (if enabled) does not alter sha; refresh replaces stale bytes; secrets/token values never appear in `result` JSON, UI, or logs under default sanitization. |
| **performance** | Documented bound for single-repo doc fetch + parse on fixture; startup listen bound; no full-history clone. |
| **security** | Mutating HTTP methods on hosted `api/*` → `405` or `404`; upstream client method allowlist is GET/HEAD only; rejected scopes refuse; SSRF: disallowed host/IP refused with HTTP `403`; path traversal in path params refused; no credential in repo after e2e; no auth-disable flag; no Track Q act routes; no deploy/probe URLs called; no `localStorage` persistence of viewer token; MuseHub-only baseline impossible (`github_contents` still required for baseline tests). |

---

## §HGD.13 — Hard stops + tier linkage (frozen)

| Action | Tier | Rule |
| --- | --- | --- |
| Feature-branch commits for this freeze / Auto | Tier 1 | SD-1 / SD-17 |
| `git push` feature branch / open PR | Tier 1 | No merge |
| Confirm new mandatory web framework dependency | Tier 2 | Recommend once + ADR if not stdlib |
| Merge to `main` | Tier 3 | Human only — not authorized here |
| Staging push / live capability flip | Tier 3 | Human only |
| Real-money billing for hosted SaaS | Tier 3 / out of kit Auto | Not in this freeze |

Escalation categories for freeze review remain: `security`, `irreversible`, `real_money`,
`gates_tier3`.

---

## §HGD.14 — Definitions of Done

### §HGD.14.1 — Thinking freeze (this phase)

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [x] Review-record table stamped; `review_stamp` filled
- [x] `docs/ROADMAP.md` — exploration row promoted / Build queue row → Thinking DONE; Auto TODO
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for Hosted governance dashboard Auto (SD-17)
- [x] No dashboard / fetch / UI / CLI code landed in Thinking
- [x] No Tier-3 merge performed

### §HGD.14.2 — Auto build (later)

- [ ] Mechanical implementation matches §§HGD.4–HGD.11 and §HGD.10
- [ ] Seven-tier matrix §HGD.12 green
- [ ] `/build-verification-review` → `pass` before ROADMAP Auto → DONE
- [ ] Governance sync (ROADMAP + HANDOVER) in the closing commit
- [ ] Feature-branch push / PR only; merge remains Tier 3
- [ ] Track Q surfaces unchanged (no scope merge)
