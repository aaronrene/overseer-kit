# Phase Track P / P-deploy — Deployment gate (Thinking freeze)

Status: **Reviewed → `pass` (P-deploy-r3).** P-deploy Thinking is **spec-only** and now frozen; no
code, no skill file edit, and no honesty schema change land in this phase. The P-deploy Auto build
(`{step}b`) is cleared to start mechanically against this frozen contract; it is the only phase that
writes files. Do **not** re-derive this contract during the Auto build.

```yaml
phase: TRACK-P-P-DEPLOY
outputs:
- id: track-p-p-deploy
  path: docs/PHASE-TRACK-P-P-DEPLOY.md
  frozen: true
frozen_inputs:
- id: p-evidence-contract
  path: docs/PHASE-TRACK-P-P-EVIDENCE.md
- id: honesty-ledger-impl
  path: tools/honesty/ledger.py
- id: honesty-validate
  path: tools/honesty/validate.py
- id: honesty-types
  path: tools/honesty/types.py
- id: honesty-status
  path: tools/honesty/status.py
- id: build-verification-skill
  path: cursor/skills/build-verification-review/SKILL.md
- id: layered-honesty-vision-l0
  path: docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md#21-l0--governance-shipped
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: roadmap-p-deploy-row
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T23:33:58Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:a9fe1cd9c65a4e181d0b51bd186691df4a648a09a7f4f38730906effaee06b6d
```

**Downstream edge:** the P-deploy Auto build (`{step}b`) treats this document as ground truth
without re-deriving it (SPEC §6 mandatory reviewed freeze). The deploy-verification skill and the
L2 honesty Mode C check consume the frozen gate as ground truth for what a *deploy/health claim*
must look like before a "shipped" → DONE assertion — but the operator / CI / runtime, never the
kit, performs the deploy or produces the health-check bytes.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| P-deploy-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist not yet run. Semantic review raised two MAJOR completeness findings + one MINOR. No escalation categories. |
| P-deploy-r1 fix | Author (cited lines only) | — | **R1-M1** fixed: §PD.5.0 freezes mode-resolution algorithm so shared `--frozen-spec` does not imply Mode B when `--deploy-health` is set. **R1-M2** fixed: §PD.5 freezes `HonestyStatusOptions.deploy_health`, argparse `--deploy-health`, dataclass JSON field, and CLI stderr map for exit `34`. **R1-N1** fixed: Mode B/C optional `--frozen-spec` ownership stated once. |
| P-deploy-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | R1 items confirmed RESOLVED. New: **R2-M1** §PD.4 omitted explicit `HonestyConfig.require_deploy_health` dataclass field (parse/`HONESTY_KEYS` alone leave Auto without the typed default). **R2-M2** §PD.0/§PD.8 "by default" probe wording contradicted §PD.1 absolute never. **R2-N1** §PD.6 rule 3 "instead of a second BV round" readable as waiving mandatory BV. |
| P-deploy-r2 fix | Author (cited lines only) | — | **R2-M1** fixed: §PD.4 parse rule 5 requires `HonestyConfig` field + load wiring. **R2-M2** fixed: probe language hardened to never (no "by default" escape). **R2-N1** fixed: §PD.6 rule 3 states BV is never waived. |
| P-deploy-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings, dry-run). Semantic re-read confirmed R1-M1–M2, R1-N1, R2-M1–M2, R2-N1 RESOLVED; exit `34` + `missing_deploy_health` non-overlapping; Mode C resolution handles shared `--frozen-spec`; boundary held (kit records/gates, never deploys/probes); BV never waived; seven-tier matrix complete; rejection table present; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §PD.0 — Simple summary

Build-verification stops an agent from marking an Auto build **DONE** when the code does not match
the frozen spec. It does **not** stop an agent from saying "we shipped it" or "production is
healthy" without a durable, content-addressed health record. P-evidence already lets a verifier
*record* a `deploy_health` hash + opaque ref on the honesty ledger. What is missing is the
**gate**: an opt-in check that refuses a "shipped" claim when no matching deploy/health evidence
exists.

**Track P / P-deploy freezes that live-deploy sibling of build-verification.** The kit still never
deploys, never opens an HTTP(S) connection to a production URL, and never embeds health payloads in
the ledger. It only **records and optionally gates** operator-supplied deploy/health claims —
reusing P-evidence's `verification_evidence` kind and `deploy_health` artifact type.

**Technical summary:** add `honesty.require_deploy_health: off|warn|require` (default `off`;
`HONESTY_KEYS` membership); add honesty-status **Mode C** (`--deploy-health PHASE_ID`, mutually
exclusive with Mode A and Mode B) whose match rule is Mode B **plus** ≥1 `deploy_health` artifact;
add exit `34` + error token `missing_deploy_health`; freeze a twin skill
`/deploy-verification-review` with checklist D1–D8; document the rejection table and seven-tier
matrix. No new ledger kind. No Track O redesign. No kit-side deploy or live probe code.

---

## §PD.1 — Scope

**In scope (freeze only — this phase writes no code):**

- The Mode C match rule that consumes existing `verification_evidence` entries and requires ≥1
  `deploy_health` artifact (§PD.3).
- The optional `honesty.require_deploy_health` config flag + `HONESTY_KEYS` membership (§PD.4).
- Honesty-status Mode C flags, mutual exclusion with Modes A/B, JSON block, and error token
  (§PD.5).
- The normative `/deploy-verification-review` skill (twin paths) and its relationship to
  build-verification V8 (§PD.6).
- Exit code `34` and reuse of existing honesty codes (§PD.7).
- The boundary + rejection table (kit records/gates; never deploys / never probes)
  (§PD.8).
- The seven-tier test matrix the P-deploy Auto build must satisfy (§PD.9).

**Out of scope (explicit non-goals — prevent creep):**

- **Any deploy, HTTP(S) health probe, DNS resolve, browser automation, or screenshot capture inside
  the kit.** The kit never opens a network connection to a deploy target. Operator / CI / runtime
  produce health-record bytes; the kit only hashes and matches refs the caller supplies.
- **A new ledger entry kind.** P-deploy **reuses** `verification_evidence` + artifact type
  `deploy_health` frozen in P-evidence (§PE.3–§PE.4). Inventing a parallel `deploy_evidence` kind is
  rejected.
- **Changing `deploy_health` artifact field rules** (sha256 / required `ref`). Schema stays
  byte-identical to §PE.4.
- **Making deploy-health mandatory for every repo or every Auto build.** Default is `off` (inert).
  Most kit phases never claim a live deploy; they still use build-verification only.
- **Automated freshness / TTL of health records.** Entry `ts` remains audit metadata; the skill
  obliges the verifier to use a health record from the same ship session. No clock-gated Mode C
  reject in this slice.
- **Redesigning Track O** (O0–O3 ceremony, `ok upgrade-regime`, product contracts). Regime upgrade
  is not a P-deploy "shipped" claim.
- **Redesigning P0 provenance, P-route, P-cost, or P-evidence Mode A/B.** Mode C is additive;
  Mode A/B behavior stays byte-identical when Mode C flags are absent.
- **Tier-3 merge, staging push, or live capability flips.** This freeze never authorizes them.
- **Blocking `ok status --exit-code` or `governance-sync` on missing deploy health.** Exit `34` is
  confined to honesty-status Mode C (same posture as exit `33` for Mode B).

---

## §PD.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Ledger kind `verification_evidence` | Required fields `phase_id`, `frozen_spec`, `round`, `bv_verdict`, `artifacts[]`; role `verifier` | P-evidence §PE.3; `tools/honesty/` |
| Artifact type `deploy_health` | `sha256` (64 hex) + **required** opaque `ref`; kit never fetches | P-evidence §PE.4 |
| Mode A | `--hook` + `--artifact` (verdict co-requirement) | K10 / `tools/honesty/status.py` |
| Mode B | `--verification-evidence PHASE` [+ `--frozen-spec`]; match = last `bv_verdict=pass` | P-evidence §PE.6 |
| `require_verification_evidence` | `off\|warn\|require` (default `off`) | P-evidence §PE.6 |
| Build-verification V8 | Requires `deploy_health` in evidence **only when** claims mention deploy/health | twin build-verification skills |
| Exit `33` | `missing_verification_evidence` (Mode B + `require`) | P-evidence §PE.8 |
| Track P codes | `30`/`31` route, `32` cost, `33` verification evidence | P-route / P-cost / P-evidence |
| Boundary | Kit = governance / record / gate; never runtime deploy | `AGENTS.md`, §PE.9 |

P-deploy **must not** change Mode A/B semantics, existing exit-code meanings, the canonical-hash
algorithm, provenance rules, or the `deploy_health` artifact schema. It only **adds** one config
flag, one honesty-status mode, one exit code, one error token, one skill, and the Mode C match
predicate.

---

## §PD.3 — Mode C match rule (frozen)

A **matching deploy-health evidence** entry for check inputs `(phase_id, frozen_spec?)` is an
entry where **all** of:

1. `kind == verification_evidence`
2. `actor_role == verifier`
3. `bv_verdict == pass`
4. `phase_id` equals the requested phase id (exact string match)
5. If the caller supplies `frozen_spec`, it equals the entry's `frozen_spec`; if the caller omits
   it, any `frozen_spec` matches
6. `artifacts` contains **at least one** object with `type == deploy_health` (validated shape per
   §PE.4 — already enforced at append time)

Scan order: ledger file order; **last** matching entry wins (same newest-append-wins posture as
Mode B).

**Relationship to Mode B:**

| Check | Requires `test_output`? | Requires `deploy_health`? |
| --- | --- | --- |
| Mode B (`require_verification_evidence`) | Skill process yes for BV `pass`; schema no | No |
| Mode C (`require_deploy_health`) | No (schema) | **Yes** (≥1) |

A single ledger entry may satisfy both Mode B and Mode C if its `artifacts` include both
`test_output` and `deploy_health`. Separate appends are also valid (last Mode C match wins
independently of Mode B).

**Pure helper the Auto build MUST add (frozen):**

```text
find_matching_deploy_health(entries, *, phase_id, frozen_spec) -> entry | None
```

Implemented beside `find_matching_verification_evidence` in `tools/honesty/validate.py` (or
equivalent). Must not open network or read `ref` as a URL.

---

## §PD.4 — Config: `honesty.require_deploy_health` (frozen)

Extend the existing `honesty:` block with one additive key (default preserves current behavior):

```yaml
honesty:
  enabled: false
  # … existing keys unchanged …
  require_deploy_health: off   # off | warn | require — default off
```

| Value | Meaning |
| --- | --- |
| `off` | (default) Mode C may still be invoked; the match is computed for JSON but **never** fails the exit code (`0` on the match dimension even when no entry exists). Repos that never set the key stay inert. |
| `warn` | Mode C on miss: stderr warning (`warning: no matching deploy_health evidence entry`) + exit `0` (reminder posture — same family as `require_verification_evidence: warn`). |
| `require` | Mode C on miss: exit `34`. |

Parse rules (frozen):

1. Value MUST be one of `off|warn|require` (string); anything else → config exit `2`.
2. Auto MUST add `require_deploy_health` to `HONESTY_KEYS` in `adapters/config.py` (unknown-key
   fail-closed). Omitting that frozenset update would reject a valid config as
   `unknown honesty keys`.
3. Default when the key is absent: `off`.
4. The flag is meaningless when `honesty.enabled: false` (module short-circuit exit `4` on ledger /
   honesty-status paths remains unchanged).
5. Auto MUST add `require_deploy_health: str = "off"` to the `HonestyConfig` dataclass in
   `adapters/config.py` and wire the parsed value into `load_config` / the returned config object
   (same pattern as `require_verification_evidence`).

Regime: **regime-agnostic** `git-only` baseline capability. No Muse dependency. Optional
`provenance` on evidence entries follows P0 soft/hard rules independently.

---

## §PD.5 — `honesty-status` Mode C (frozen)

Extend Mode resolution so three mutually exclusive modes exist. Exact CLI flag names are frozen
(no aliases in this slice):

| Mode | Required flags | Forbidden together with |
| --- | --- | --- |
| **A — verdict co-requirement (existing)** | `--hook HOOK` + `--artifact PATH` | `--verification-evidence`, `--frozen-spec`, `--deploy-health` |
| **B — verification evidence (existing)** | `--verification-evidence PHASE_ID` | `--hook`, `--artifact`, `--producer-session`, `--deploy-health` |
| **C — deploy health (new)** | `--deploy-health PHASE_ID` | `--hook`, `--artifact`, `--producer-session`, `--verification-evidence` |

**Shared optional flag:** `--frozen-spec PATH_STRING` is allowed with **Mode B or Mode C** (not both
modes in one invocation). It is an opaque string passed through to the match rule — not a
filesystem must-exist check. It is forbidden with Mode A.

**Auto wiring (frozen — required for Mode C to be reachable):**

1. `HonestyStatusOptions` gains additive field `deploy_health: str | None = None` (alongside
   existing `verification_evidence` / `frozen_spec`).
2. `cli/main.py` registers argparse `--deploy-health PHASE_ID` on the honesty-status parser
   (metavar `PHASE_ID`).
3. `cli/commands/honesty_status.py` passes `deploy_health=getattr(args, "deploy_health", None)`
   into `HonestyStatusOptions` and maps exit `34` → stderr error token text
   `missing deploy health` (same family as exit `33` → `missing verification evidence`).
4. `HonestyStatusJson` gains additive optional field `deploy_health: dict[str, Any] | None = None`
   emitted only on Mode C responses (§PD.5.1).

### §PD.5.0 — Mode-resolution algorithm (frozen)

Today `_resolve_mode` in `tools/honesty/status.py` treats any `--frozen-spec` as Mode B partial and
rejects `--frozen-spec` without `--verification-evidence`. Auto **must replace** that logic with
the following (normative). Pseudocode:

```text
mode_a_partial = hook or artifact or producer_session
mode_a_full    = hook and artifact
mode_b_full    = verification_evidence is set
mode_c_full    = deploy_health is set
# --frozen-spec is SHARED metadata — it does NOT by itself imply Mode B or Mode C
frozen         = frozen_spec is set

if mode_b_full and mode_c_full:
    return None   # usage
if mode_a_partial and (mode_b_full or mode_c_full or frozen):
    return None   # Mode A exclusive of B/C/frozen-spec
if frozen and not mode_b_full and not mode_c_full:
    return None   # --frozen-spec alone is usage
if not mode_a_full and not mode_b_full and not mode_c_full:
    return None
if mode_c_full:
    return "mode_c"
if mode_b_full:
    return "mode_b"
return "mode_a"
```

**Invariant:** `--deploy-health PHASE --frozen-spec PATH` resolves to `mode_c` (not usage).
`--verification-evidence PHASE --frozen-spec PATH` resolves to `mode_b` (unchanged).
`--frozen-spec PATH` alone remains usage `1`.

**Usage exit `1` when** the algorithm returns `None`.

When Mode C flags are absent, Mode A/B behavior is **byte-identical** to pre-P-deploy for every
invocation that does not pass `--deploy-health`.

Mode C applies `require_deploy_health` per §PD.4 (`off` → always `0` for the match dimension and
still emits the JSON block below; `warn` → stderr warning + `0` on miss; `require` → `34` on miss).
Module disabled → existing `4` short-circuit before mode logic.

The `/deploy-verification-review` skill (§PD.6) is the process obligation that *creates* / confirms
the entry; Mode C is how CI / operators *confirm* it later before a "shipped" → DONE claim.

### §PD.5.1 — Mode C JSON + error token (frozen)

Extend `HonestyErrorToken` (`tools/honesty/types.py`) with exactly one additive value:

```text
missing_deploy_health
```

Used when Mode C exits `34`. Do not overload `missing_verification_evidence`, `missing_verdict`, or
`evidence_free` for this case.

`HonestyStatusJson.to_dict()` gains one additive key, present **only on Mode C responses**
(Mode A/B responses omit the key entirely so existing consumers stay compatible):

```json
{
  "ok": false,
  "exit_code": 34,
  "command": "honesty-status",
  "hook": null,
  "artifact": null,
  "artifact_sha256": null,
  "producer_session": null,
  "matched_verdict_hash": null,
  "error": "missing_deploy_health",
  "deploy_health": {
    "phase_id": "Track P / P-deploy",
    "frozen_spec": null,
    "require": "require",
    "matched_entry_hash": null
  }
}
```

| `deploy_health` field | Rule |
| --- | --- |
| `phase_id` | Echo of `--deploy-health` |
| `frozen_spec` | Echo of `--frozen-spec` or `null` |
| `require` | Effective config value `off`\|`warn`\|`require` |
| `matched_entry_hash` | `entry_hash` of the last matching Mode C entry, or `null` |

On Mode C success (`0`): `ok: true`, `error: null`, `matched_entry_hash` set when a match exists;
under `off` with no match, `ok: true`, `matched_entry_hash: null`, `error: null` (check not
enforced). On `warn` miss: `ok: true`, `error: null`, `matched_entry_hash: null`, plus stderr
warning.

Mode B responses continue to emit `verification_evidence` and **must not** emit `deploy_health`.
Mode C responses emit `deploy_health` and **must not** emit `verification_evidence`.

---

## §PD.6 — Deploy-verification skill (frozen, normative)

The Auto build adds **both** vendored skill paths as twins (same content):

- `cursor/skills/deploy-verification-review/SKILL.md`
- `.cursor/skills/deploy-verification-review/SKILL.md`

**When to run (frozen process rule):** invoke `/deploy-verification-review` **before** marking a
phase **DONE** in ROADMAP / regenerating HANDOVER when **any** of the following claims appear in
the session's deliverable, handover text, or ROADMAP row:

- live deploy / production (or staging-as-production) rollout
- public or customer-facing URL is "up" / "healthy" / "verified"
- "shipped" meaning **running outside the local repo** (not merely "code merged to a feature branch")

**Non-triggers (frozen):** ordinary Auto builds that only claim code + tests + local CLI behavior
(e.g. kit governance phases, Track O ceremony code without a live consumer probe) continue to use
`/build-verification-review` alone. Track O `ok upgrade-regime` is a **regime ceremony**, not a
P-deploy trigger.

**Checklist (every item needs evidence):**

| # | Check | Dishonesty signal |
| --- | --- | --- |
| D1 | Deploy/health claim is in scope for this phase (frozen spec authorizes a ship claim) | "Shipped" for a spec that forbids live probes / deploys |
| D2 | Operator-supplied health record exists on disk or in CI artifacts (bytes the verifier hashed) | Claim with no record file |
| D3 | Ledger entry (when `honesty.enabled`) is `verification_evidence` with `bv_verdict: pass` and ≥1 `deploy_health` artifact | Pass claim with only `test_output` / `screenshot` |
| D4 | `deploy_health.sha256` digests the **same** health-record bytes the verifier inspected | Hash of unrelated file |
| D5 | `deploy_health.ref` identifies the check (URL string, job id, env name) as opaque metadata — not fetched by the kit | Kit "proved" health by opening the URL itself |
| D6 | Health record is from **this** ship session (verifier cites session/time; no automated TTL) | Reusing last quarter's health JSON |
| D7 | No kit code path performs deploy or production HTTP probe as part of "verification" | Auto added `urllib.request.urlopen(prod)` under tools/ |
| D8 | ROADMAP/HANDOVER "shipped"/DONE wording matches Mode C (when honesty enabled + `require`) | DONE without matching ledger entry under `require` |

**Relationship to build-verification V8 (frozen):**

1. `/build-verification-review` remains mandatory for every Auto build DONE (existing rule).
2. When the build session claims deploy/health, V8 already requires a `deploy_health` artifact in
   the BV evidence entry (§PE.7 rule 4) — unchanged.
3. `/deploy-verification-review` is the **sibling gate for shipped/live claims**. It runs when a
   ship/live-health claim is present; it does **not** replace or waive `/build-verification-review`
   for Auto build DONE (rule 1). If BV already passed and the only remaining claim is live health,
   a deploy-verification round is sufficient for that ship claim. Under `honesty.enabled: true`, a
   skill `pass` MUST append or confirm a Mode C–matching entry.
4. When `honesty.enabled: false`, ledger append is skipped; D1–D8 still require claims↔record
   honesty in the review text (baseline without L2).
5. Hard stops unchanged: no merge to `main` on `findings`/`blocked`; uncited findings invalid;
   no Tier-3 automation.

**Optional Cursor rule (Auto may add, default inert):** a non-`alwaysApply` rule or a short
pointer in `build-verification-required.mdc` noting the sibling skill for shipped claims. Do **not**
make deploy-verification always-on for every phase (would false-close kit-only Auto builds).

---

## §PD.7 — Exit codes (frozen)

Additive code; non-overlapping with existing
`1`,`2`,`4`,`5`,`7`,`8`,`10`–`11`,`20`–`26`,`30`–`33`:

| Code | Meaning | Where |
| --- | --- | --- |
| `34` | Deploy health required but missing (no matching Mode C entry under §PD.3) | `honesty-status` Mode C when `require_deploy_health: require`; JSON `error` = `missing_deploy_health` (§PD.5.1) |

Reused (no renumbering):

| Code | Reuse for this gate |
| --- | --- |
| `1` | Usage — Mode A/B/C underspecified or combined (§PD.5) |
| `2` | Malformed schema on append (existing PE rules); bad config value for `require_deploy_health` |
| `4` | Honesty module disabled / config refuse (existing short-circuit) |
| `23` | Role violation on append (`actor_role` ≠ `verifier`) |
| `24` | Evidence-free append (`artifacts` empty) |
| `25`/`26` | Provenance (P0; unchanged) |
| `33` | Mode B missing verification evidence (unchanged; not used for Mode C) |

`34` is confined to honesty-status Mode C. It does not change `status --exit-code` precedence and
does not block `governance-sync` by itself.

---

## §PD.8 — Boundary, capability, and rejection table (frozen)

**Single most important frozen rule:** the kit records and optionally gates deploy/health claims;
it never performs the deploy and never HTTP-probes production.

### Boundary table

| Concern | Overseer Kit (gate / recorder) | Operator / CI / runtime |
| --- | --- | --- |
| Append `verification_evidence` with `deploy_health` | Yes (existing PE surface) | Supplies health-record bytes + ref |
| Mode C match / `require_deploy_health` | Yes | Decides when to enable |
| Hash file bytes path-confined | Yes (read-only helper) | Produces the files |
| Deploy to a host / public URL | **Never** | Yes (outside kit) |
| HTTP(S) health probe of production | **Never** | Yes; then supply record bytes + ref |
| Embed health body bytes in ledger | **Never** | Store blobs elsewhere |
| Tier-3 merge authorization | **Never** | Operator |
| Track O regime upgrade | Untouched | `ok upgrade-regime` (separate track) |

### Capability tiers

| Capability | `git-only` (baseline) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Record deploy_health on file ledger | Full (via PE) | Full (identical) |
| Mode C gate | Full | Full |
| Optional signed `provenance` | Soft (unsigned OK) | Hard when `require_agent_signature: true` (P0) |
| Perform deploy / live health check | **Not in the kit** | **Not in the kit** |

### Rejection table (frozen — Auto must fail closed if asked to ship these)

| Rejected ask | Why |
| --- | --- |
| Add `tools/*/deploy.py` that SSHes / kubectl-applies / uploads artifacts | Kit is not a CD system (`AGENTS.md`) |
| Add default HTTP client that GETs `ref` URLs to "verify" health | Violates §PD.1 / §PE.9; `ref` is opaque |
| New ledger kind `deploy_evidence` | Parallel store; PE already froze `deploy_health` |
| Require Mode C on every Auto DONE | False-closes non-ship phases; default `off` |
| Soften Mode C to accept `screenshot` alone as ship proof | Screenshot ≠ deploy/health record |
| Wire exit `34` into `status --exit-code` precedence | Out of scope; reminder/CI invoke Mode C explicitly |
| Redesign Track O Stage 3 / `upgrade-regime` as a deploy gate | Separate custody ceremony; hard stop |
| Auto-merge to `main` after Mode C pass | Tier 3 always human |

---

## §PD.9 — Seven-tier test matrix (P-deploy Auto build must satisfy)

The P-deploy Auto build ships all seven tiers green locally before DONE
(`policy/test-tiers.yaml`).

| Tier | Proves |
| --- | --- |
| **unit** | `require_deploy_health` parse (`off\|warn\|require`, default `off`, unknown → config `2`); key accepted in `HONESTY_KEYS`; `HonestyErrorToken` includes `missing_deploy_health`; `find_matching_deploy_health` returns last pass entry with ≥1 `deploy_health`; rejects (returns `None`) for pass-without-deploy_health, findings verdict, wrong phase, wrong frozen_spec, non-verifier; Mode resolution per §PD.5.0: `--deploy-health`+`--frozen-spec` → `mode_c`; Mode C + Mode B flags → usage invalid; `--frozen-spec` alone → invalid; Mode A + `--deploy-health` → invalid. |
| **integration** | Mode C `honesty-status --deploy-health PHASE` with `require` and no match → `34` + JSON error token; with matching entry (deploy_health present) → `0` + `matched_entry_hash`; entry with only `test_output` does **not** satisfy Mode C; `warn` missing → `0` + stderr warning; `off` → check not enforced; combining Mode A/B/C flags → `1`; Mode A and Mode B without Mode C flags remain byte-identical; `honesty.enabled: false` → existing `4` short-circuit unchanged. |
| **e2e** | Fixture repo: append genesis + `verification_evidence` with `test_output` only → Mode B may match, Mode C misses; append second entry adding `deploy_health` → Mode C last-wins match; skill-normative fixture asserts a deploy-verification `pass` body includes `deploy_health`. Identical unsigned behavior under `git-only` and a Muse regime. |
| **stress** | Many evidence entries (bounded, e.g. ≥ 100) with sparse deploy_health matches; match scan remains last-wins and completes within a documented bound; no unbounded filesystem walk of `ref` strings. |
| **data-integrity** | Mode C match depends on artifact `type` string equality (`deploy_health`); tampering a stored artifact type or sha256 breaks chain verify (`22`) or fails match; append still embeds hashes/refs only (no health body bytes); path helper (if present) is path-confined; no partial ledger write on validation failure. |
| **performance** | Mode C match over a realistic ledger completes within a bounded time; linear in ledger length; no network. |
| **security** | `ref` values that look like URLs or shell metacharacters remain opaque — never fetched, never executed; no network on Mode C / append / verify paths (asserted); no secrets required in deploy_health fields; producer role cannot append evidence (`23`); exit `34` cannot be waived by omitting the check flag when CI invokes Mode C under `require`; Auto build must not introduce kit-side production probes (grep/tests assert absence of deploy/HTTP probe helpers in honesty / new skill surfaces). |

---

## §PD.10 — Shared-contract note (informative)

- **Build-verification agents** keep using `/build-verification-review` for every Auto DONE; they
  already require `deploy_health` in the evidence entry when claims mention deploy (V8 / §PE.7).
- **Deploy-verification agents** use `/deploy-verification-review` when the DONE claim is
  shipped/live health; Mode C is the mechanical CI gate under `require_deploy_health: require`.
- **P-evidence** remains the schema owner for artifact objects; this phase only consumes them.
- **Consumer CD systems** (GitHub Actions deploy jobs, Scooling runtimes, etc.) produce health
  records and call `ok honesty-status --deploy-health …` — they do not move into the kit.

---

## §PD.11 — Definition of Done (Thinking freeze)

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [x] Review-record table stamped; `review_stamp` filled
- [x] `docs/ROADMAP.md` P-deploy Thinking → DONE; Auto build row present / queued
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for P-deploy Auto build (SD-17)
- [x] No code / skill / config landed in the Thinking phase itself
- [x] No Tier-3 merge performed
- [x] No Track O files redesigned

## §PD.12 — Definition of Done (Auto build — for the next session)

- [x] Mechanical implementation matches §§PD.3–PD.7
- [x] Twin deploy-verification skill paths added per §PD.6
- [x] Seven-tier matrix §PD.9 green
- [x] `/build-verification-review` → `pass` before ROADMAP Auto row → DONE
- [x] Governance sync (ROADMAP + HANDOVER) in the closing commit
- [x] Feature-branch push / PR only; merge remains Tier 3
- [x] No deploy/HTTP probe code introduced in the kit
