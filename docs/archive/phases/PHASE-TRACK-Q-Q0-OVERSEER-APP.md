# Phase Track Q / Q0 — Freeze Overseer App (Thinking freeze)

Status: **Reviewed → `pass` (Q0-r2).** Q0 Thinking is **spec-only** and now frozen; no code,
no static UI, and no new CLI command land in this phase. The Track Q / Q1 Auto build (`{step}b`)
is cleared to start mechanically against this frozen contract; it is the only phase that writes
app server/UI files. Do **not** re-derive this contract during the Auto build.

```yaml
phase: TRACK-Q-Q0
outputs:
- id: track-q-q0-overseer-app
  path: docs/archive/phases/PHASE-TRACK-Q-Q0-OVERSEER-APP.md
  frozen: true
frozen_inputs:
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: k4-status-contract
  path: docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md
- id: k5-review-contract
  path: docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
- id: hygiene-agent
  path: docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: k9a-honesty
  path: docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md
- id: kh2-muse-sync
  path: docs/archive/phases/PHASE-KH2-MUSE-SYNC-HARD-GATE.md
- id: kh3-footprint
  path: docs/archive/phases/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: roadmap-track-q-rows
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T17:37:35Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:3c3f62296c0b7730ce831e051d6ce607aee72ba6a717348952a1bd695a807238
```

**Downstream edge:** the Track Q / Q1 Local web UI Auto build treats this document as ground
truth without re-deriving it (SPEC §6 mandatory reviewed freeze). Track Q / Q2 Tauri packaging
consumes Q1's shipped localhost UI as ground truth for packaging only — it does not reopen this
Q0 scope. The hosted governance dashboard (exploration backlog) is a **different** product and
must not be built from this contract.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| Q0-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist initially **blocked** on absolute-path false positive for URL paths (`api/health` with a leading slash matched §K5.5 C4). Semantic review added completeness findings below. No `irreversible`/`real_money`/`gates_tier3` escalation. |
| Q0-r1 fix | Author (cited items only) | — | **R1-C4** fixed: API paths written without leading slash in the artifact. **R1-M1** fixed: CORS includes `[::1]`; port default frozen to `8765` fail-closed; `::1` bind allowlist. **R1-M2** fixed: §Q0.7.6 frozen POST body schemas. **R1-M3** fixed: `api/status` mirrors `status --json` + always computes exit-code conditions into payload. **R1-M4** fixed: Q1 auth = Bearer + CSRF header only (cookies deferred). **R1-N1** fixed: multi-lane governance-sync flags CLI-only in Q1. **R1-N2** fixed: `app` COMMANDS registration + stdlib server refinement. |
| Q0-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings). Semantic re-read confirmed R1 items RESOLVED: loopback bind + `::1` CORS parity; port `8765` fail-closed; Bearer + CSRF-header auth (cookies deferred); closed `api/*` surface + §Q0.7.6 body schemas; `api/status` JSON + exit_code semantics; multi-lane CLI-only; stdlib server; seven-tier matrix complete; boundary held (frontend/distribution of governance, never runtime); no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `overseer review --freeze`. |

---

## §Q0.0 — Simple summary

Operators already run Overseer Kit from a terminal: `status`, living docs, freeze review,
governance-sync, ledger, honesty-status. A local window that shows the same state and triggers
the same gated actions would make day-to-day governance easier — without inventing a second
engine.

**Track Q / Q0 freezes `overseer app`:** a **local-only** web UI that sits **on top of** the
existing Python engine (`cli/` / `tools/` / `adapters/`). It is a frontend/distribution of
governance, never a runtime, dispatcher, or model host. Default bind is loopback only. Writes
stay fail-closed and CLI-parity. Q1 builds it; Q2 may package it with Tauri later.

**Technical summary:** freeze CLI `overseer app`, stdlib loopback HTTP server, thin handlers that
call existing engine functions (no HTTP re-implementation of gate logic), closed read/act API
surface, session-credential + CSRF auth for the local server, inert-first writes, seven-tier
matrix for Q1.

---

## §Q0.1 — Scope

**In scope (freeze only — this phase writes no code):**

- Product boundary and rejection table (§Q0.3).
- CLI surface `overseer app` (§Q0.4).
- Bind + listen policy (`127.0.0.1`-only default) (§Q0.5).
- Auth story for a local server (§Q0.6).
- Read/act HTTP API surface and engine call rule (§Q0.7).
- Fail-closed CLI parity rules (§Q0.8).
- Server/UI tech constraints for Q1 (§Q0.9).
- Exit / HTTP status mapping (§Q0.10).
- Boundary + capability table (§Q0.11).
- Seven-tier test matrix Q1 must satisfy (§Q0.12).

**Out of scope (explicit non-goals — prevent creep):**

- **Any engine rewrite.** Q1 must reuse existing `cli/commands/*` and `tools/*` callables. No
  parallel status/review/sync/ledger implementation under an `app/` package.
- **New governance capabilities** beyond what the CLI already does for the scoped commands.
- **Remote / LAN / hosted exposure by default.** Binding non-loopback is refused in Q1 defaults.
  The hosted read-only dashboard remains exploration backlog, not Track Q.
- **Model hosting, agent dispatch, OpenRouter, Cursor SDK, or worker/checker runtime.** Kit stays
  on the governance side of `AGENTS.md`.
- **`overseer init` / `sync` / `verify-step` / `route` in the Q1 UI.** Those stay CLI-only for this
  track. (Route remains a separate read-only CLI; UI inclusion needs a later freeze.)
- **Tauri / native packaging** — Track Q / Q2 only; Q0 freezes that Q2 adds no engine logic.
- **Native macOS/SwiftUI app** — explicitly deferred (ROADMAP Q2 note).
- **Multi-lane `governance-sync --lane` / `--all-lanes` in the UI** — CLI-only in Q1 (§Q0.7.5).
- **Cookie-based browser sessions** — deferred (§Q0.6.2); Q1 is Bearer + CSRF header only.
- **Tier-3 merge, staging push, or live capability flips** — this freeze never authorizes them.
- **Ledger binary blob storage, deploy execution, live HTTP health probes** — unchanged from
  P-evidence / kit boundary.

---

## §Q0.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| CLI commands | `init` \| `sync` \| `status` \| `review` \| `governance-sync` \| `verify-step` \| `honesty-status` \| `ledger` \| `route` | `cli/main.py` `COMMANDS` |
| Status | Read-only; `--exit-code`; substrate / muse-sync / footprint self-integrity / gates / cost surfaces | `cli/commands/status.py` |
| Review | `review --freeze PATH`; dry-run; stamp; exit `7`/`8` | `cli/commands/review.py`, K5 |
| Governance-sync | Default dry-run; `--write` applies on feature branch | `cli/commands/governance_sync.py` |
| Honesty / ledger | `honesty-status`; `ledger {append,verify,show}` | K9a / K10 / P-evidence |
| Hard gates | Muse-sync + footprint self-integrity refuse review / governance-sync / status `--exit-code` | KH2, KH3 |
| Kit boundary | Repo-agnostic governance; not a product runtime | `AGENTS.md` |
| Web UI today | Public landing pages only (`docs/landing/`); no `overseer app` | K12 |
| HTTP framework deps | None in-repo (no FastAPI/Flask dependency today) | `pyproject.toml` / tree |

Q0 **must not** change existing command semantics, exit-code meanings, or gate wiring. It only
**adds** a local presentation + thin HTTP adapter over a closed subset of those commands.

---

## §Q0.3 — Product boundary (frozen)

| Concern | Track Q Overseer App | Not Track Q |
| --- | --- | --- |
| What it is | Local UI over the vendored Python engine for **one repo working tree** | Hosted multi-repo org dashboard |
| Where it runs | Operator machine; process started by `overseer app` | Cloud SaaS |
| Authority | Same as CLI for scoped actions | New remote authority |
| Data plane | Local filesystem + local VCS adapters | GitHub/MuseHub APIs as sole source |
| Model / agent runtime | **Never** | Cursor / OpenRouter / Scooling 9A |
| Packaging (later) | Q2 Tauri wraps the **same** localhost UI | Parallel Swift rewrite |

**Frozen one-liner:** Overseer App is a **frontend/distribution of governance**, never a
runtime/dispatcher/model-host.

---

## §Q0.4 — CLI surface (frozen)

```text
overseer app [--repo PATH] [--port PORT] [--bind ADDRESS] [--open]
```

| Flag | Default | Rule |
| --- | --- | --- |
| `--repo` | cwd resolution (same as other commands) | Path-confined; must contain `.overseer/` after init |
| `--port` | `8765` | Integer 1–65535. If the chosen port is occupied → fail closed with exit `2` (do not silently pick another port). Operator passes `--port` to override. |
| `--bind` | `127.0.0.1` | Only loopback literals allowed in Q1: `127.0.0.1`, `localhost` (resolved to loopback), or `::1`. Any other value → refuse, exit `2` |
| `--open` | off | Optional: open default browser to the local UI URL after listen succeeds |

**Startup behavior (frozen):**

1. Resolve repo + load config (same fail-closed path as `status`).
2. Refuse non-loopback `--bind` (§Q0.5).
3. Generate ephemeral session credential (§Q0.6); print **once** to stderr (human-readable
   startup banner). Do not write the credential to the repo tree. Do not append it to
   governance docs.
4. Listen; serve static UI + JSON API routes under the `api/` prefix (§Q0.7).
5. Block until SIGINT/SIGTERM; then exit `0` if clean shutdown.

**Command registration (frozen):** Q1 adds exactly one new top-level command id `app` to
`cli/main.py` `COMMANDS` (and the argparse subparser). No other new top-level commands.

**Non-goals for the CLI process:** no background daemon install, no launchd/systemd unit in Q1,
no auto-start on login.

---

## §Q0.5 — Bind + listen policy (frozen)

| Rule | Requirement |
| --- | --- |
| Default bind | `127.0.0.1` |
| Allowed bind values (Q1) | `127.0.0.1`, `localhost`, `::1` |
| Refused | `0.0.0.0`, `::` (unspecified), `*`, LAN NIC addresses, hostname that resolves off-loopback |
| Peer check | If peer address is not loopback, reject the request (defense in depth even on loopback bind) |
| TLS | Not required on loopback for Q1; no certificate generation in-kit |
| CORS | Reflect only `http://127.0.0.1:<port>`, `http://localhost:<port>`, and `http://[::1]:<port>`; deny others |

Changing default bind to non-loopback is **out of Q1** and would require a later Thinking freeze
(security + Tier-2). Q1 must not ship a hidden “bind all interfaces” escape hatch.

---

## §Q0.6 — Auth story (frozen)

Loopback reduces remote internet exposure; it does **not** stop other local processes for the
same OS user. Q1 therefore ships defense-in-depth auth for the local server.

### §Q0.6.1 — Session credential

| Property | Rule |
| --- | --- |
| Generation | Cryptographically secure random; ≥ 128 bits of entropy |
| Lifetime | Process lifetime only (regenerated every `overseer app` start) |
| Delivery | Printed once on stderr at startup together with the CSRF value (§Q0.6.3) |
| Storage | In-memory in the server process only |
| Persistence | **Forbidden** in the repo, `version.lock`, handover, roadmap, or world-readable temp files |
| Presentation to API | Required on every `api/*` request via `Authorization: Bearer <credential>` |

### §Q0.6.2 — Browser UI bootstrap

The static UI prompts the operator once per process to paste the session credential (and holds it
in a JS memory variable for `Authorization` headers). **Forbidden in Q1:** cookies,
`localStorage`, `sessionStorage`, and durable disk caches under the repo. Cookie-based session
bootstrap is deferred to a later freeze if packaging (Q2) needs it.

### §Q0.6.3 — Mutating requests (CSRF)

At startup the server also generates a CSRF value (≥ 128 bits), printed once on stderr with the
session credential. Every state-changing method (`POST`, `PUT`, `PATCH`, `DELETE`) on `api/*`
MUST require header `X-Overseer-CSRF` equal to that value. GETs that only read are exempt from
CSRF but still require the Bearer credential. The UI holds the CSRF value in memory the same way
as the session credential.

### §Q0.6.4 — Fail closed

| Condition | Behavior |
| --- | --- |
| Missing / wrong session credential | HTTP `401`; no engine call |
| Missing / wrong CSRF on mutating call | HTTP `403`; no engine call |
| Non-loopback peer | HTTP `403`; no engine call |
| Disallowed Origin | HTTP `403`; no engine call |

No anonymous read API in Q1 — even `status` requires the session credential. Rationale: living
docs and ledger contents may include internal planning detail the operator did not intend to
expose to every local process without a shared secret.

### §Q0.6.5 — Explicit non-goals (auth)

- No OAuth, SSO, or multi-user accounts in Q1.
- No long-lived API keys checked into `.overseer/`.
- No “disable auth” flag in Q1.

---

## §Q0.7 — HTTP API surface (frozen)

### §Q0.7.1 — Engine call rule (mandatory)

Handlers MUST invoke existing Python functions used by the CLI (shared modules under `tools/`
and/or thin wrappers around `cli/commands/*` run functions). Handlers MUST NOT:

- Re-implement muse-sync / footprint / honesty validation in the HTTP layer.
- Shell out to a second copy of policy logic.
- Bypass `--dry-run` defaults or gate checks.

Subprocess `overseer …` is allowed only as a last-resort test helper, not as the production
handler path for Q1.

### §Q0.7.2 — Closed endpoint set (Q1)

URL paths below are rooted at the server origin. They are written **without** a leading slash in
this freeze artifact so the §K5.5 checklist absolute-path detector does not false-positive; Q1
implements them as normal absolute URL paths (leading slash present on the wire).

| Method | Path | Engine parity | Default posture |
| --- | --- | --- | --- |
| `GET` | `api/health` | Process liveness only (no repo secrets) | Requires session credential |
| `GET` | `api/status` | `overseer status --json` payload shape; see §Q0.7.6 | Read-only |
| `GET` | `api/docs/roadmap` | Read living ROADMAP path from config | Read-only; path-confined |
| `GET` | `api/docs/handover` | Read living HANDOVER path from config | Read-only; path-confined |
| `GET` | `api/gates` | Pending-gates slice already computed for status | Read-only |
| `POST` | `api/review/freeze` | `overseer review --freeze` | Body includes freeze path; **`dry_run` default `true`**; stamp write only when `dry_run=false` and engine allows |
| `POST` | `api/governance-sync` | `overseer governance-sync` | **`dry_run` / non-write default**; `write=true` maps to CLI `--write` and remains feature-branch only |
| `GET` | `api/ledger/show` | `overseer ledger show` | Read-only |
| `POST` | `api/ledger/verify` | `overseer ledger verify` | Read-only verify |
| `POST` | `api/ledger/append` | `overseer ledger append` | Same schema/role gates as CLI; fail-closed |
| `POST` | `api/honesty-status` | `overseer honesty-status` | Same Mode A/B flags as CLI |

Static UI assets are served outside the `api/` prefix (document root and an `assets/` tree).

### §Q0.7.3 — Doc read rules

- Paths come from `.overseer/config.yaml` living-doc configuration (same helpers as CLI).
- Responses return text + repo-relative path metadata.
- Path escape / traversal → refuse (same family as CLI exit `4` / path confinement).
- No arbitrary `?path=` file read API in Q1.

### §Q0.7.4 — Write confirmation

UI MUST require an explicit operator confirm step before sending `write=true` governance-sync or
non-dry-run freeze stamp. The API still enforces defaults server-side even if the UI is bypassed.

### §Q0.7.5 — Forbidden endpoints (Q1)

No HTTP endpoints for: `init`, `sync`, `verify-step`, `route`, merge-to-main, staging push,
mirror export, or live capability flips.

**Multi-lane governance-sync (`--lane` / `--all-lanes`):** CLI-only in Q1. The HTTP
`api/governance-sync` body MUST NOT accept lane selectors; lane workflows stay on the terminal
until a later freeze.

### §Q0.7.6 — Request / response field contracts (frozen)

**`GET api/status`**

- Builds the same JSON object `overseer status --json` would emit for the repo.
- Always computes the `--exit-code` condition set into the response envelope’s `exit_code`
  field (so the UI can show red/green without a second call). HTTP status remains `200` when the
  adapter itself succeeded; a non-zero `exit_code` means gate/drift failure, not an HTTP transport
  error.
- Query params: none in Q1 (no partial field filters).

**`POST api/review/freeze` body (JSON object):**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `path` | string | yes | Repo-relative freeze artifact path; path-confined |
| `dry_run` | bool | no | Default `true`. `false` allows stamp write per CLI rules |
| `no_stamp` | bool | no | Default `false`; maps to CLI `--no-stamp` when dry-run is false |

**`POST api/governance-sync` body (JSON object):**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `write` | bool | no | Default `false` (dry-run). `true` maps to CLI `--write` |

No other body keys in Q1 on any POST endpoint (unknown keys → HTTP `400`, no engine call).
The same unknown-key rule applies to `api/review/freeze`, `api/ledger/append`, and
`api/honesty-status`.

**`POST api/ledger/verify` body:** empty object `{}` (or no body). No fields in Q1.

**`POST api/ledger/append` body (JSON object):**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `kind` | string | yes | Same closed vocabulary as CLI `--kind` |
| `entry` | object | yes | Append body identical to CLI JSON file / stdin schema |

**`POST api/honesty-status` body (JSON object):**

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `hook` | string | no | Mode A — same as CLI `--hook` |
| `artifact` | string | no | Mode A — path-confined |
| `producer_session` | string | no | Mode A |
| `verification_evidence` | string | no | Mode B phase id |
| `frozen_spec` | string | no | Mode B opaque path string |

Mode A/B mutual exclusion and defaults match CLI `honesty-status` (including exit `1` when both
mode families are combined illegally).

**`GET api/docs/roadmap` / `GET api/docs/handover` success `result`:**

| Field | Type | Rule |
| --- | --- | --- |
| `path` | string | Repo-relative living-doc path |
| `text` | string | Full file text (UTF-8) |
| `sha256` | string | Lowercase hex of raw file bytes |

**`GET api/ledger/show`:** query `last` optional positive int (maps to CLI `--last`); default
`20` (same as `cli/commands/ledger.py`); response `result` is the list/payload equivalent of
CLI show output.

**`GET api/gates`:** `result` equals the pending-gates object already embedded in status JSON
(no second policy invention).

**`GET api/health` success `result`:** `{ "status": "ok", "port": <int>, "bind": "<literal>" }`
with no repo document contents.

---

## §Q0.8 — Fail-closed CLI parity (frozen)

| Rule | Detail |
| --- | --- |
| Same gates | Muse-sync, footprint self-integrity, substrate, config, honesty, and freeze-review escalations apply identically when the underlying command would apply them |
| Same exit codes in payloads | JSON responses include `exit_code` with the **same integers** the CLI would return for that operation |
| No capability inflation | If the CLI cannot do it, the app cannot |
| Inert-first | Mutating endpoints default to dry-run / non-write |
| No Tier-3 automation | App never merges to `main`, never `muse push` staging, never flips live gates |
| Regime baseline | Full function on `git-only` (K7 guardrail); Muse deepens substrate checks, does not invent app-only features |
| Sanitization | Reuse CLI sanitization for paths/secrets in error strings |

Parity proof obligation for Q1 tests: for each scoped command, at least one integration case shows
HTTP `exit_code` equals direct CLI invocation on the same fixture.

---

## §Q0.9 — Server + UI tech constraints (frozen for Q1)

| Layer | Frozen choice | Rationale |
| --- | --- | --- |
| HTTP server | Python **stdlib** (`http.server` / `ThreadingHTTPServer` or equivalent stdlib stack) | Kit has no FastAPI/Flask dependency today; baseline must stay offline-install simple |
| FastAPI / Starlette | **Not required** for Q1; introducing them needs an explicit dependency decision outside this freeze’s “zero new engine” spirit — deferred | Avoid mandatory new runtime deps |
| Frontend | Static HTML/CSS/vanilla JS served by the same process | No Node build step required for Q1 DONE |
| Layout package | New modules under `tools/app/` (+ `cli/commands/app.py` entry) | Keeps UI adapter beside other tools; does not fork `tools/honesty` etc. |
| Q2 | Tauri packages the **same** server+UI; no second API | Packaging-only |

ROADMAP’s “FastAPI/stdlib” sketch is hereby refined: **stdlib is the frozen Q1 server.**

---

## §Q0.10 — Process exit codes + HTTP mapping (frozen)

### §Q0.10.1 — `overseer app` process exits

| Code | Meaning |
| --- | --- |
| `0` | Clean shutdown after successful listen |
| `1` | Usage / argument error |
| `2` | Config / bind refusal / listen failure / not initialized |
| `4` | Path escape / refused path confinement on `--repo` |

No new process-level exit code is allocated for Track Q in Q0. HTTP-layer auth failures are not
process exits.

### §Q0.10.2 — `api/*` response shape

```json
{
  "ok": false,
  "exit_code": 2,
  "error": "config",
  "result": null
}
```

- On success: `ok: true`, `exit_code: 0` (or the engine’s success code), `result` holds the
  command payload.
- On engine failure: `ok: false`, `exit_code` mirrors CLI, `error` token when the CLI/JSON
  surfaces already define one.
- Auth failures use HTTP `401`/`403` with `exit_code` omitted or set null — they are adapter
  refusals, not CLI outcomes.

---

## §Q0.11 — Boundary & capability table (frozen)

| Concern | Overseer Kit App (Q1) | Runtime / operator |
| --- | --- | --- |
| Show status / docs / gates | Yes | Reads the UI |
| Run freeze review / governance-sync / ledger / honesty-status | Yes (parity wrappers) | Confirms writes |
| Call models / host agents | **Never** | Cursor / other runtimes |
| Bind non-loopback by default | **Never** | — |
| Merge to `main` / staging push | **Never** | Tier-3 human |
| Deploy product workloads | **Never** | Outside kit |
| Package as desktop (Q2) | Packaging only | Operator installs |

| Capability | `git-only` | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| `overseer app` loopback UI | Full | Full |
| Hard gates reflected in UI | Full (gates that apply) | Full (+ muse substrate/sync) |
| Hosted multi-repo dashboard | **Not this track** | **Not this track** |

---

## §Q0.12 — Seven-tier test matrix (Q1 Auto build must satisfy)

The Q1 Auto build ships all seven tiers green locally before DONE (`policy/test-tiers.yaml`).

| Tier | Proves |
| --- | --- |
| **unit** | Bind allowlist accepts only `127.0.0.1`/`localhost`/`::1` and refuses `0.0.0.0`/`::`; default port `8765` busy → exit `2`; session credential entropy ≥ 128 bits; CSRF required on POST; endpoint allowlist rejects unknown routes; JSON envelope parse; doc path helper refuses escape; default `dry_run=true` / non-write for review + governance-sync handlers; `app` registered in `COMMANDS`. |
| **integration** | Each scoped endpoint calls into real engine functions on a fixture repo; HTTP `exit_code` matches CLI for representative success and fail-closed cases (config missing, muse-sync refuse, footprint refuse, honesty role/`33` paths as applicable); static UI served; `--bind 0.0.0.0` CLI refuse → process exit `2`; occupied `--port 8765` → exit `2`. |
| **e2e** | Start `overseer app` against fixture → authenticate → view status + ROADMAP/HANDOVER → dry-run freeze review → dry-run governance-sync → ledger show/verify → honesty-status; then confirmed write path only when fixture expects feature-branch writes; SIGINT clean exit `0`. |
| **stress** | Concurrent read requests (bounded, e.g. ≥ 20) against status/docs do not corrupt process state; large handover/roadmap read stays bounded; no unbounded VCS scan introduced by the HTTP layer. |
| **data-integrity** | Dry-run twice = same report; write path uses same atomic/doc helpers as CLI; no partial stamp/doc write on induced failure; session credential never appears in ledger JSONL, version.lock, or living docs. |
| **performance** | Status and doc read endpoints complete within a documented bound on a realistic fixture; startup listen within a documented bound; no extra full-repo walk beyond what CLI status already does. |
| **security** | Non-loopback peer rejected; missing Bearer credential → `401`; bad/missing CSRF on POST → `403`; disallowed Origin (including wrong host form) → `403`; no credential/CSRF values in repo files after e2e; path traversal on doc endpoints refused; handlers do not open outbound model/provider network connections; no `init`/`sync`/`merge` routes present; no auth-disable flag; no cookie/`localStorage` persistence of secrets. |

---

## §Q0.13 — Q2 packaging note (informative, not Q1 work)

Q2 may wrap Q1’s stdlib server + static UI in Tauri. Frozen constraints for that future phase:

- No second implementation of governance logic inside Rust/JS.
- Same loopback + auth defaults unless a later freeze revisits them.
- Native SwiftUI remains deferred.

---

## §Q0.14 — Definition of Done (Thinking freeze)

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `overseer review --freeze`
- [x] Review-record table stamped; `review_stamp` filled
- [x] `docs/ROADMAP.md` Track Q / Q0 → DONE (Thinking); Q1 remains Auto TODO gated on this contract
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for Track Q / Q1 (SD-17)
- [x] No app server / UI / CLI code landed in the Thinking phase itself
- [x] No Tier-3 merge performed

## §Q0.15 — Definition of Done (Auto build — Track Q / Q1)

- [ ] Mechanical implementation matches §§Q0.4–Q0.10
- [ ] Seven-tier matrix §Q0.12 green
- [ ] `/build-verification-review` → `pass` before ROADMAP Q1 → DONE
- [ ] Governance sync (ROADMAP + HANDOVER) in the closing commit
- [ ] Feature-branch push / PR only; merge remains Tier 3
