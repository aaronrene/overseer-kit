# Phase ISR — Independent second reviewer (Thinking freeze)

Status: **Reviewed → `pass` (ISR-r4).** ISR-a is **spec-only** and now frozen; no
code, no skill edit, and no honesty schema change land in this phase. ISR-b
(Auto) is cleared to build mechanically against this contract.

```yaml
phase: ISR
outputs:
- id: isr-independent-second-reviewer
  path: docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md
  frozen: true
frozen_inputs:
- id: kit-spec
  path: docs/OVERSEER-KIT-SPEC.md
- id: k5-freeze-reviewer
  path: docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
- id: k9a-honesty
  path: docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md
- id: p-evidence
  path: docs/archive/phases/PHASE-TRACK-P-P-EVIDENCE.md
- id: p-deploy
  path: docs/archive/phases/PHASE-TRACK-P-P-DEPLOY.md
- id: p-route
  path: docs/archive/phases/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md
- id: lt-loop-tightening
  path: docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md
- id: ons-operator-next
  path: docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md
- id: kh1-relay
  path: docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: check-ok
  path: docs/archive/phases/PHASE-CHECK-OK.md
- id: build-verification-skill
  path: cursor/skills/build-verification-review/SKILL.md
- id: build-verification-rule
  path: cursor/rules/build-verification-required.mdc
- id: honesty-types
  path: tools/honesty/types.py
- id: honesty-status
  path: tools/honesty/status.py
- id: honesty-validate
  path: tools/honesty/validate.py
- id: honesty-config
  path: adapters/config.py
- id: verification-evidence-gate
  path: tools/verification_evidence_gate/surface.py
- id: governance-hygiene-engine
  path: tools/governance_hygiene/engine.py
- id: status-exit
  path: cli/commands/status.py
- id: layered-honesty-vision-l0
  path: docs/archive/thinking/OVERSEER-KIT-LAYERED-HONESTY-VISION.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: model-labels
  path: policy/model-labels.yaml
- id: kit-boundary
  path: AGENTS.md
review_stamp:
  reviewed_at: '2026-09-02T12:24:04Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:e6284150fc755facb5a008ce33eb425d55081e798096a0373d5e54715f5b3bba
```

**Downstream edge:** ISR-b treats this document as ground truth without re-deriving
it (SPEC §6 mandatory reviewed freeze). The second chat / separate verifier runtime
*performs* the review; the kit only **records and optionally gates** the verdict.
The kit never dispatches, hosts, or calls a second model.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line**.
Uncited findings are invalid and are discarded. Fixes are Tier 1 on the feature
branch. Merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| ISR-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Semantic **R1-M1–M2** + **R1-N1**. Fixed in-tree before CLI stamp. |
| ISR-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** governance-sync wiring named `ReadFailure` (coverage path) instead of the LT Mode B engine-footer path. **R2-N1** validate helper “or equivalent”; **R2-N2** live skill dests vs `ok sync`. Fixed in-tree. |
| ISR-r3 | Freeze-review loop (CLI checklist + thinking, `thinking-high`) | findings | **R3-C4** CLI `blocked` on a C4 false positive (gate-token equals-sign). Rephrased. |
| ISR-r4 | Freeze-review loop (CLI checklist + thinking, `thinking-high`) | **pass** | R1–R3 confirmed RESOLVED. Boundary held (kit records/gates; no model dispatch). Mode D resolution + engine-footer wiring frozen. Seven-tier matrix complete. Stamp written by `ok review --freeze`. |

### Freeze-review findings ledger (ISR-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | consistency | `:575-586` (pre-fix) | V9 required an ISR ledger line as part of BV, but §ISR.7.3 appended that line only after BV `pass` — Auto could not order the steps. Frozen: V1–V8 then append then DONE-unlock V9. |
| R1-M2 | MAJOR | completeness | `:648` (pre-fix) | Exit constant lived in `status.py` **or** `honesty_status.py`. Frozen to `tools/honesty/status.py` only. |
| R1-N1 | MINOR | completeness | `:457` (pre-fix) | Mode D `--json` on usage/`38`/`4` and `_usage_result` extension were implied, not frozen. Now explicit. |
| R2-M1 | MAJOR | completeness | `:510` (pre-fix) | Governance-sync `ReadFailure("independent-second-reviewer")` pointed Auto at `reads.py` (coverage). LT Mode B fails in `engine.py` after the footer. Frozen to engine-footer + status `_exit_code_from_conditions`. |
| R2-N1 | MINOR | completeness | `:247` (pre-fix) | `find_matching_*` “or equivalent” weasel. Frozen to `tools/honesty/validate.py`. |
| R2-N2 | MINOR | consistency | `:596` (pre-fix) | “Amend live `.cursor/` / `.claude/` copies” vs required `ok sync --yes`. Frozen: edit `cursor/` source only. |
| R3-C4 | BLOCKER | security | `:541` (pre-fix) | Checklist C4 matched a gate-token equals-sign as a secret assignment. Rephrased to “the gate token is …”. |

**Citation discipline:** every review finding in this artifact **must** include
`path:line` so the operator can verify — never trust uncited review output
(§6.2 / K5).

---

## §ISR.0 — Simple summary

After an Auto build, the same chat that wrote the code can run
`/build-verification-review`, type **DONE**, and walk away. The build-verification
rule already *asks* for an independent verifier and a thinking-high model — "if
possible." That weasel is the hole. Loop tightening (LT) recorded the hole and
explicitly deferred it: no second chat, no different session id.

**Independent second reviewer freezes the missing gate:** before an Auto slice may
be claimed **DONE**, a **second chat or separate verifier** — not the agent that
built — must record a passing verdict. The kit **records and optionally gates**
that verdict on the honesty ledger. The kit **does not run another model**, does
not open a new IDE chat, and does not call any reviewer API for this gate.

**Technical summary:** add ledger kind `independent_second_review` (additive to the
K9a / P-evidence enum); require `producer_session_id` ≠ `actor_session_id` at
append time; add `honesty.require_independent_second_reviewer: off|warn|require`
(default `off`; `HONESTY_KEYS` + `HonestyConfig` field); add honesty-status
**Mode D** (`--independent-second-review PHASE_ID`, shared optional
`--producer-session` / `--frozen-spec`); add exit `38` + token
`missing_independent_second_review`; add an LT-shaped active-slice surface on
`ok status` / `governance-sync`; vendor a portable paste doc + twin skill; amend
build-verification V9 + the always-on BV rule. Portable CLI + docs are complete
without Cursor. No model dispatch. No ISR-b code in this Thinking phase.

---

## §ISR.1 — Verified problem (do not redesign)

| Fact | Evidence |
| --- | --- |
| BV skill says independent verifier **"if possible"** — not a gate | `cursor/skills/build-verification-review/SKILL.md` Model section |
| Always-on BV rule requires `/build-verification-review` before DONE; it does not require a different session | `cursor/rules/build-verification-required.mdc` |
| LT explicitly deferred second chat / different `agent_id` | `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md` §LT.2 non-goal + §LT.5.3 |
| K9a session inequality exists only for Mode A `verdict` hooks, and only when `--producer-session` is supplied | PHASE-K9A §K9.8; `tools/honesty/status.py` `_match_verdicts` |
| Mode B (`verification_evidence`) matches last `bv_verdict=pass` — no producer/session compare | P-evidence §PE.6.1; `find_matching_verification_evidence` |
| A producer may self-declare `actor_role: verifier` and append evidence | P-evidence §PE.3 role rule is role-string only |
| Kit is rule-holder, never model executor | P-route §PR.0; `AGENTS.md`; SPEC §6 reviewer is a *separate* freeze surface, not a dispatcher for DONE |
| Honesty Mode A/B/C + `_resolve_mode` already treat `--producer-session` as a Mode A partial | `tools/honesty/status.py` `_resolve_mode` (P-deploy §PD.5.0) |
| Active-slice Mode B surface already exists (warn/require, no historical retro-fail) | `tools/verification_evidence_gate/surface.py` §LT.5.2 |
| Used honesty / CLI exits include `33`–`37` | P-evidence `33`, P-deploy `34`, workspace `35`, PLS `36`, ONS `37` |
| Cursor cannot be required; ONS/LT: CLI + docs primary | PHASE-ONS; PHASE-LT §LT.4.1 / §LT.7 |

---

## §ISR.2 — Scope

**In scope (ISR-a freezes; ISR-b implements):**

1. Ledger kind `independent_second_review` + append/validate rules (§ISR.3).
2. Config `honesty.require_independent_second_reviewer` + `HONESTY_KEYS` /
   `HonestyConfig` wiring (§ISR.4).
3. Honesty-status **Mode D** flags, mode-resolution amendment, JSON, error token
   (§ISR.5).
4. Active-slice status / governance-sync surface (§ISR.6).
5. Portable CLI + docs + twin skill + BV V9 / rule amendment (§ISR.7).
6. Exit code `38` and reuse of existing codes (§ISR.8).
7. Boundary + rejection table — governance, not runtime (§ISR.9).
8. SPEC §5 additive row (§ISR.10).
9. Seven-tier matrix (§ISR.11).
10. Definition of Done (§ISR.12).

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected now |
| --- | --- |
| **Kit dispatches / hosts / calls a second model** | P-route + AGENTS.md boundary. Runtime / operator opens the second chat. |
| **Automate Cursor "new chat" / tab open** | No honest host command. Print instructions. Same family as tab-reload reject. |
| **Require ISR for every consumer** | Default `off`. Kit dogfood starts at **warn** (ISR-b writes; not this phase). |
| **`require` as Auto v1 dogfood** | High friction. Promote later. |
| **Replace build-verification or K5 freeze review** | ISR *who* certified DONE; BV *what* matches the spec; K5 *before* Auto starts. |
| **Apply ISR to Thinking freeze-review DONE** | "Not the same agent that **built**." Thinking stays K5. ISR = Auto slices only. |
| **New Mode A `verdict` hook or SHA co-requirement** | Different layer. Do not overload `verdict`. |
| **Reuse / extend `verification_evidence` with session fields** | That kind is artifact hashes (V8). ISR is independence of the certifier. |
| **Make `--producer-session` required on Mode D** | Lost token must not make the check unusable. Pin when supplied; entry still stores both ids. |
| **Cryptographic proof of chat identity as `git-only` baseline** | P0 provenance remains optional / soft under git-only. Kit records the *claim*. |
| **Session-type bookends (idle / Operator+Auto)** | Separate backlog row. ISR skips non-Auto active slices. |
| **KH2 remask, tab reload, auto-enable hooks** | Unchanged backlog. |
| **Wire `ok review --freeze` to Mode D** | Wrong gate: freeze is pre-Auto. Same as LT Mode B. |
| **New top-level CLI verb** (`ok isr`, `ok isr-status`) | Check = Mode D on `ok honesty-status`; record = `ok ledger append`. No second engine. |
| **Block historical DONE rows** | Active slice only (LT §LT.5.2 posture). |
| **MuseHub-only identity / signature as the gate** | K7: baseline on `git-only`. |
| **ISR-b Auto implementation in this Thinking phase** | SD-3 split. |
| **Tier-3 merge, staging push, live posture flips** | Never authorized here. |
| **Secrets, API keys, or model endpoints in config / ledger** | Names and opaque session strings only. |

---

## §ISR.3 — Ledger kind `independent_second_review` (frozen schema)

**Additive amendment of the K9a / P-evidence entry-kind enum:** add **exactly one**
new value. Every prior kind's required fields and semantics stay byte-identical.
Auto must extend `ENTRY_KINDS` in `tools/honesty/types.py` and the matching
`validate_append_body` branches — no second ledger, no renumbering.

```text
independent_second_review
```

**Envelope (unchanged K9a / P0 rules):** every non-genesis entry carries `v: 1`,
`kind`, `ts` (server may fill), `prev_hash` / `entry_hash` (server fills),
`actor_role`, `actor_session_id`, and optional `provenance`.

**Role rule (frozen):** `actor_role` MUST be `verifier`. Any other role → exit `23`.

**Independence invariant (frozen, enforced at append):**

1. `producer_session_id` is a required opaque non-empty string (the builder
   session / separate-producer nonce the operator supplied).
2. `actor_session_id` is the second reviewer's session (envelope; required on
   every non-genesis kind).
3. If `actor_session_id == producer_session_id` → exit `2` (malformed; not a
   role violation). The builder cannot honestly append their own ISR pass.
4. The kit does **not** invent, scrape, or infer either id. The caller supplies
   both. The kit records the claim.

**Kind-specific required fields (frozen):**

| Field | Type | Rule |
| --- | --- | --- |
| `phase_id` | non-empty string | Opaque phase / slice id (same family as P-evidence). |
| `frozen_spec` | non-empty string | Opaque path-shaped string. Append checks **non-empty string only** — no must-exist, no path-confine of the stored string (same as §PE.3). |
| `round` | integer ≥ 1 | ISR review round. `< 1` or non-int → exit `2`. |
| `isr_verdict` | string enum | Closed vocabulary: `pass` \| `findings` \| `blocked` (lowercase). Any other value → exit `2`. |
| `producer_session_id` | non-empty string | Builder / producer session nonce. Empty / missing / non-string → exit `2`. |

**Optional fields (frozen):**

| Field | Type | Rule |
| --- | --- | --- |
| `producer_agent_id` | string | Opaque. When **both** `producer_agent_id` and `verifier_agent_id` are present and equal → exit `2`. One present, one absent → allowed. |
| `verifier_agent_id` | string | Opaque. Inequality rule above. Does not require P0 provenance. |
| `bound_verification_evidence_hash` | string | Optional `entry_hash` of a `verification_evidence` line. Auto v1 **does not** require or resolve this at match time (Mode B remains a separate gate). If present: non-empty string; no live ledger lookup at append. |
| `notes` | string | Advisory; never a substitute for independence or for BV. |
| `provenance` | object | Optional; identical to P0 rules. |

**Example (normative shape, illustrative ids):**

```json
{
  "v": 1,
  "kind": "independent_second_review",
  "ts": "2026-09-02T12:00:00Z",
  "actor_role": "verifier",
  "actor_session_id": "verifier-chat-2",
  "phase_id": "ISR-b",
  "frozen_spec": "docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md",
  "round": 1,
  "isr_verdict": "pass",
  "producer_session_id": "builder-chat-1",
  "notes": "second chat re-ran build-verification V1-V9",
  "prev_hash": "…",
  "entry_hash": "…"
}
```

Genesis must not carry any of these kind-specific keys. Extend the existing
genesis forbid-list in `validate_append_body` to include `phase_id`,
`frozen_spec`, `round`, `isr_verdict`, `producer_session_id`,
`producer_agent_id`, `verifier_agent_id`, `bound_verification_evidence_hash`
— additive to keys already refused. (`phase_id` / `frozen_spec` / `round` may
already be forbidden from P-evidence; do not remove them.)

**CLI record surface (frozen):** reuse
`ok ledger append --kind independent_second_review` (`--file` / `--stdin`).
No new top-level verb. `ok ledger verify` / `show` treat the new kind like any
other (hash continuity). Kind authority: CLI `--kind` remains authoritative vs
body `kind`.

**Pure helper Auto MUST add:**

```text
find_matching_independent_second_review(entries, *, phase_id, frozen_spec, producer_session) -> entry | None
```

Implemented beside `find_matching_verification_evidence` /
`find_matching_deploy_health` in `tools/honesty/validate.py`.
Must not open a network connection, must not call a model, must not read
session ids from the IDE.

---

## §ISR.4 — Config: `honesty.require_independent_second_reviewer` (frozen)

Extend the existing `honesty:` block with one additive key (default preserves
current behavior):

```yaml
honesty:
  enabled: false
  require_independent_second_reviewer: off   # off | warn | require — default off
```

| Value | Meaning |
| --- | --- |
| `off` | (default) Mode D may still be invoked; the match is computed for JSON but **never** fails the exit code (`0` on the match dimension even when no entry exists). Repos that never set the key stay inert. |
| `warn` | Mode D on miss: stderr warning (`warning: no matching independent_second_review entry`) + exit `0`. Active-slice status / governance-sync: reminder only (never fail). |
| `require` | Mode D on miss: exit `38`. Active-slice status `--exit-code` / governance-sync: reuse exit `2` (no new status exit). |

Parse rules (frozen):

1. Value MUST be one of `off|warn|require` (string); anything else → config exit `2`.
2. Auto MUST add `require_independent_second_reviewer` to `HONESTY_KEYS` in
   `adapters/config.py` (unknown-key fail-closed). Omitting that frozenset update
   would reject a valid config as `unknown honesty keys`.
3. Default when the key is absent: `off`.
4. The flag is meaningless when `honesty.enabled: false` (module short-circuit
   exit `4` on ledger / honesty-status paths remains unchanged).
5. Auto MUST add `require_independent_second_reviewer: str = "off"` to the
   `HonestyConfig` dataclass and wire the parsed value into `load_config` / the
   returned config object (same pattern as `require_verification_evidence` /
   `require_deploy_health`).
6. Unknown keys under `honesty:` remain fail-closed (existing rule).

Regime: **regime-agnostic** `git-only` baseline. No Muse dependency. Optional
`provenance` on ISR entries follows P0 soft/hard rules independently.

**Kit dogfood (ISR-b writes; not this phase):** this repo's
`.overseer/config.yaml` sets `require_independent_second_reviewer: warn`.
Do **not** set `require`. Do **not** enable the key in `ok init` defaults or
templates. Consumers stay `off` until they opt in.

### Operator amend 2026-09-02 — default `require` (closed loop)

**Authority:** operator Tier-3 posture flip (Aaron). Premise: the independent
second pass is the closed loop; default opt-out was portability, not
optionality of the gate.

| Was (ISR-r4) | Now |
| --- | --- |
| Absent key → `off` | Absent key → `require` |
| `HonestyConfig` default `off` | default `require` |
| Kit dogfood `warn` | Kit dogfood `require` |
| Tip when `off`: enable warn\|require | Tip when `off`: you opted out; set `require` to re-enable |

Opt out per repo: `honesty.require_independent_second_reviewer: off` (or `warn`).
Rejection row “Default `require` for all consumers” is **superseded** by this
amend for shipped defaults; frozen Mode D / ledger / exit `38` mechanics are
unchanged.

---

## §ISR.5 — `honesty-status` Mode D (frozen)

### §ISR.5.1 — Flags

Exact CLI flag names are frozen (no aliases in this slice):

| Mode | Required flags | Forbidden together with |
| --- | --- | --- |
| **A — verdict co-requirement (existing)** | `--hook HOOK` + `--artifact PATH` | `--verification-evidence`, `--frozen-spec`, `--deploy-health`, `--independent-second-review` |
| **B — verification evidence (existing)** | `--verification-evidence PHASE_ID` | `--hook`, `--artifact`, `--producer-session`, `--deploy-health`, `--independent-second-review` |
| **C — deploy health (existing)** | `--deploy-health PHASE_ID` | `--hook`, `--artifact`, `--producer-session`, `--verification-evidence`, `--independent-second-review` |
| **D — independent second review (new)** | `--independent-second-review PHASE_ID` | `--hook`, `--artifact`, `--verification-evidence`, `--deploy-health` |

**Shared optional flags:**

- `--frozen-spec PATH_STRING` — allowed with Mode B, C, or D (not more than one
  of those modes in one invocation). Opaque string; not a filesystem must-exist
  check. Forbidden with Mode A.
- `--producer-session ID` — allowed with Mode A (existing optional pin) **or**
  Mode D (optional pin). Forbidden with Mode B and Mode C (unchanged).

**Auto wiring (frozen — required for Mode D to be reachable):**

1. `HonestyStatusOptions` gains additive field
   `independent_second_review: str | None = None`.
2. `cli/main.py` registers argparse `--independent-second-review PHASE_ID`
   on the honesty-status parser (metavar `PHASE_ID`).
3. `cli/commands/honesty_status.py` passes
   `independent_second_review=getattr(args, "independent_second_review", None)`
   into `HonestyStatusOptions` and maps exit `38` → stderr text
   `missing independent second review`.
4. `HonestyStatusJson` gains additive optional field
   `independent_second_review: dict | None = None` emitted **only** on Mode D
   responses (Mode A/B/C omit the key).

### §ISR.5.2 — Mode-resolution algorithm (frozen; amends §PD.5.0)

Today `_resolve_mode` treats `--producer-session` as a Mode A partial and
rejects it with Mode B/C / `--frozen-spec`. Auto **must replace** that logic
with the following (normative). Pseudocode:

```text
mode_a_core    = hook or artifact
mode_a_full    = hook and artifact
mode_b_full    = verification_evidence is set
mode_c_full    = deploy_health is set
mode_d_full    = independent_second_review is set
frozen         = frozen_spec is set
producer       = producer_session is set

# --producer-session is SHARED metadata for Mode A (optional) and Mode D (optional).
# It does NOT by itself imply Mode A when Mode D is selected.
mode_a_partial = mode_a_core or (producer and not mode_d_full)

if (mode_b_full + mode_c_full + mode_d_full) > 1:
    return None
if mode_a_partial and (mode_b_full or mode_c_full or mode_d_full or frozen):
    return None
if frozen and not mode_b_full and not mode_c_full and not mode_d_full:
    return None
if not mode_a_full and not mode_b_full and not mode_c_full and not mode_d_full:
    return None
if mode_d_full:
    return "mode_d"
if mode_c_full:
    return "mode_c"
if mode_b_full:
    return "mode_b"
return "mode_a"
```

**Invariants (frozen):**

1. `--independent-second-review PHASE --frozen-spec PATH` → `mode_d`.
2. `--independent-second-review PHASE --producer-session ID` → `mode_d`.
3. `--independent-second-review PHASE --producer-session ID --frozen-spec PATH` → `mode_d`.
4. `--independent-second-review PHASE` alone → `mode_d`.
5. `--producer-session ID` alone → usage `1` (unchanged).
6. `--verification-evidence PHASE --producer-session ID` → usage `1` (unchanged).
7. `--deploy-health PHASE --producer-session ID` → usage `1` (unchanged).
8. `--hook H --artifact P --independent-second-review PHASE` → usage `1`.
9. When Mode D flags are absent, Mode A/B/C behavior is **byte-identical** to
   pre-ISR for every invocation that does not pass `--independent-second-review`.

Usage exit `1` when the algorithm returns `None`.

Mode D applies `require_independent_second_reviewer` per §ISR.4
(`off` → always `0` for the match dimension and still emits the JSON block;
`warn` → stderr warning + `0` on miss; `require` → `38` on miss).
Module disabled → existing `4` short-circuit before mode logic.

### §ISR.5.3 — Mode D match rule (frozen)

A **matching** `independent_second_review` entry for inputs
`(phase_id, frozen_spec?, producer_session?)` is an entry where **all** of:

1. `kind == independent_second_review`
2. `actor_role == verifier`
3. `isr_verdict == pass`
4. `phase_id` equals the requested phase id (exact string match)
5. If the caller supplies `frozen_spec`, it equals the entry's `frozen_spec`;
   if omitted, any `frozen_spec` matches
6. `actor_session_id != producer_session_id` (entry-internal; already append-enforced)
7. If the caller supplies `producer_session`, it equals the entry's
   `producer_session_id` **and** `actor_session_id !=` that same id; if omitted,
   rule 7 is skipped (last ISR pass for the phase still must satisfy 1–6)

Scan order: ledger file order; **last** matching entry wins.

`findings` / `blocked` entries never satisfy the gate. A later `pass` is a
separate append (new `round`).

### §ISR.5.4 — Mode D JSON + error token (frozen)

Extend `HonestyErrorToken` with exactly one additive value:

```text
missing_independent_second_review
```

Used when Mode D exits `38`. Do not overload `missing_verdict`,
`missing_verification_evidence`, or `missing_deploy_health`.

Mode D JSON (nested key present **only** on Mode D responses):

```json
{
  "ok": false,
  "exit_code": 38,
  "command": "honesty-status",
  "hook": null,
  "artifact": null,
  "artifact_sha256": null,
  "producer_session": "builder-chat-1",
  "matched_verdict_hash": null,
  "error": "missing_independent_second_review",
  "independent_second_review": {
    "phase_id": "ISR-b",
    "frozen_spec": null,
    "producer_session": "builder-chat-1",
    "require": "require",
    "matched_entry_hash": null
  }
}
```

| Nested field | Rule |
| --- | --- |
| `phase_id` | Echo of `--independent-second-review` |
| `frozen_spec` | Echo of `--frozen-spec` or `null` |
| `producer_session` | Echo of `--producer-session` or `null` |
| `require` | Effective config value `off`\|`warn`\|`require` |
| `matched_entry_hash` | `entry_hash` of the last matching pass entry, or `null` |

Top-level `producer_session` continues to echo `--producer-session` or `null`
(existing Mode A field; Mode D reuses it).

On Mode D success (`0`): `ok: true`, `error: null`, `matched_entry_hash` set
when a match exists; under `off` with no match, `ok: true`,
`matched_entry_hash: null`, `error: null`. On `warn` miss: `ok: true`,
`error: null`, `matched_entry_hash: null`, plus stderr warning.

Mode A/B/C responses **must not** emit `independent_second_review`.
Mode D responses **must not** emit `verification_evidence` or `deploy_health`.

`--json` emits this object on **every** Mode D exit, including `1` / `4` /
`38` / `0` (existing honesty-status always-emit pattern). Usage (`1`) that
included `--independent-second-review` still echoes `phase_id` in the nested
block when the phase argument was present; `matched_entry_hash` is `null`.

Auto MUST extend `_usage_result` in `tools/honesty/status.py` so it can
carry `independent_second_review=` the same way it already carries
`verification_evidence=` / `deploy_health=`.

---

## §ISR.6 — Active-slice status / governance-sync surface (frozen)

Reuse the LT §LT.5.2 skip / claim posture. New helper module
`tools/independent_second_reviewer/` (`IndependentSecondReviewerGateReport` /
`build_independent_second_reviewer_gate`) parallel to
`tools/verification_evidence_gate/`.

When `honesty.enabled` is true **and** `require_independent_second_reviewer` is
`warn` or `require`:

1. Resolve the KH1.9 **active slice** (same scan as `scan_governance_gates`).
2. If there is no active slice, or the active Model is not `Auto` and not the
   Auto half of a split (`{step}b`), **skip**.
3. If the active Auto slice status is `TODO` or `WIP` and the handover does
   **not** claim BV `pass` / DONE, **skip**.
4. If the handover or roadmap claims that active Auto slice is **DONE** or BV
   **`pass`**, run §ISR.5.3 with:
   - `phase_id` = the active phase id string from KH1.9
   - `--frozen-spec`: if the active ROADMAP deliverable cell contains exactly
     one path matching `docs/archive/phases/PHASE-*.md` (or consumer equivalent
     under `docs/`), pass that path; if zero or more than one, omit
   - `producer_session` omitted (status cannot know the builder chat)

| Mode | Missing match | Status `--exit-code` | governance-sync |
| --- | --- | --- | --- |
| `off` | n/a | unchanged | unchanged |
| `warn` | reminder line + JSON `independent_second_reviewer_gate: {ok: true, mode: warn, matched: false}` | **0** (never fail) | footer reminder only |
| `require` | same JSON with `ok: false` + token `missing_independent_second_review` | **2** | engine footer + return `2` (not `reads.py` `ReadFailure`) |

Do **not** invent a new `ok status` exit code. Token stays
`missing_independent_second_review`.

**Auto wiring (frozen — parallel to LT Mode B, not to footprint-coverage):**

1. `tools/independent_second_reviewer/__init__.py` exports
   `IndependentSecondReviewerGateReport`,
   `build_independent_second_reviewer_gate`,
   `format_independent_second_reviewer_gate_line`,
   `independent_second_reviewer_gate_payload`.
2. `cli/commands/status.py` calls the builder (same handover/roadmap texts as
   Mode B), prints the human line, attaches JSON when the probe did not skip,
   and folds `independent_second_reviewer_gate.ok` into
   `_exit_code_from_conditions` as a new `independent_second_reviewer_gate_ok`
   argument (default `True`) on the existing `2` tier. Do not renumber
   `2 > 6 > 35 > 3 > 0`.
3. `tools/governance_hygiene/engine.py` calls the same builder beside the
   existing `verification_gate` block: emit the human line; when
   `ok` is false, `mode` is `require`, and the gate token is
   `missing_independent_second_review`, return `2`. Do **not** add a
   `ReadFailure` in `tools/governance_hygiene/reads.py` (that path is for VCS /
   coverage / muse-sync reads, not honesty claim gates).

JSON key (when the probe did not skip): `independent_second_reviewer_gate`
`{ok, mode, matched}` plus `phase_id` when known plus `token` when set.

Human line when a message exists:
`independent_second_reviewer_gate: <message>`

Exact miss message (require):
`missing independent_second_review ledger entry for active Auto slice`

Exact miss message (warn):
`warning: no matching independent_second_review entry for active Auto slice`

Exact remediation string (require path / engine footer / status JSON):
`second chat: append independent_second_review then ok honesty-status --independent-second-review PHASE`

`ok review --freeze` is **not** wired to this surface.

Do **not** fail old DONE rows. Do **not** mark ROADMAP DONE. Do **not**
dispatch a model from status or governance-sync.

---

## §ISR.7 — Portable primary (CLI + docs) + optional host niceties

### §ISR.7.1 — Portable contract (complete without Cursor)

| Action | Command / doc |
| --- | --- |
| Record the second verdict | `ok ledger append --kind independent_second_review` |
| Check the gate | `ok honesty-status --independent-second-review PHASE [--producer-session ID] [--frozen-spec PATH] [--json]` |
| Print NEXT for the second chat | `ok next` / `ok governance-sync --print-next` |
| Paste instructions (Copilot / any host) | `docs/INDEPENDENT-SECOND-REVIEWER.md` |

Claude Code, Copilot, and paste-only hosts stay on this table. Missing Cursor
skills or hooks is **not** pass and **not** fail — degrade to CLI + paste doc.

The kit **never** opens a second chat. The operator / host runtime does.

### §ISR.7.2 — Paste doc (ISR-b writes)

Path: `docs/INDEPENDENT-SECOND-REVIEWER.md` (kit docs; same family as
`docs/CHECK-OK.md` / `docs/PRINT-NEXT.md`).

Auto **must** include, verbatim as the opening sentence:

> The kit records and gates the second verdict. It does not run another model.
> Open a new chat or a separate verifier runtime; then use the CLI below.

The doc **must** tell the builder to invent or copy an opaque
`producer_session` nonce and give it to the second chat (chat / composer id
when the host exposes one; otherwise a human-chosen nonce). Auto v1 does
**not** add a new handover HTML anchor for this nonce (GS-PASTE sole NEXT
regen; do not reopen).

The doc **must** include the two CLI lines from §ISR.7.1 and state that a
human counts as the second verifier.

### §ISR.7.3 — Twin skill (ISR-b writes)

Source (Auto writes): `cursor/skills/independent-second-reviewer/SKILL.md`.
Dest twins after the required ISR-b `ok sync --yes`:
`.cursor/skills/independent-second-reviewer/SKILL.md` and
`.claude/skills/independent-second-reviewer/SKILL.md` (existing dual glob).

Invoke: `/independent-second-reviewer`.

Process rules (frozen):

1. Confirm this session is **not** the builder session. If it is, stop and
   tell the operator to open a second chat. Do not append a pass. Do not
   write ROADMAP **DONE**.
2. Re-run `/build-verification-review` **V1–V8 only** against the frozen spec
   + diff (implementation honesty). **V9 is not part of this step** — it is
   the DONE-unlock check in §ISR.7.4 and cannot be satisfied before the
   append in step 3.
3. On V1–V8 `pass`, append `independent_second_review` with
   `isr_verdict: pass`, this session as `actor_session_id`, and the builder
   nonce as `producer_session_id`.
4. When `honesty.require_verification_evidence` is `warn` or `require`, the
   second session also appends / confirms Mode B `verification_evidence` (V8)
   **before** claiming DONE. ISR does not replace Mode B.
5. ROADMAP **DONE** is allowed only after step 3 (and step 4 when it applies).
   That is when V9 holds if ISR is `warn` or `require`.
6. When ISR config is `off`, the skill is advisory; Mode D / status do not fail.
7. `findings` / `blocked` on V1–V8: do not append `isr_verdict: pass`. A
   `findings` ISR append is allowed but not required (same family as
   P-evidence rule 6).
8. Never merge to `main`. Never call a model via the kit CLI for this gate
   (`ok review --freeze` remains the K5 spec reviewer, not the ISR dispatcher).

### §ISR.7.4 — Build-verification skill + always-on rule (ISR-b amends)

Amend the source twin `cursor/skills/build-verification-review/SKILL.md`.
Live `.cursor/` / `.claude/` copies update via the required ISR-b
`ok sync --yes` — do not require a separate hand-edit of those dests.

**Model section — replace "if possible":**

> Always `thinking-high`. When `honesty.require_independent_second_reviewer` is
> `warn` or `require`, this review **must** run in a second chat or separate
> verifier runtime — not the session that built. A builder-session BV `pass`
> does not unlock DONE. When the flag is `off`, prefer a second session but do
> not fail the kit gate (process honesty only).

**Add V9 (DONE-unlock only — not a V1–V8 implementation check):**

| # | Check | Dishonesty signal |
| --- | --- | --- |
| V9 | When ISR is `warn` or `require`, ROADMAP/HANDOVER may claim **DONE** only after a matching `independent_second_review` pass exists for this Auto slice with `actor_session_id` ≠ `producer_session_id` | Builder chat wrote DONE; no ISR ledger line; equal session ids |

V1–V8 meaning unchanged. V9 does **not** block a V1–V8 implementation `pass`
and does **not** require the ISR line to exist *before* the second session
appends it (§ISR.7.3 order: V1–V8 → ISR append → Mode B when it applies →
DONE). V9 is **N/A** (not
a fail) when the flag is `off` or honesty is disabled. A builder-session
V1–V8 `pass` still does not unlock DONE when ISR is `warn` or `require`.

Amend `cursor/rules/build-verification-required.mdc` (alwaysApply) with one
short paragraph: when ISR is `warn` or `require`, do not mark DONE in the
builder chat; open a second chat or follow `docs/INDEPENDENT-SECOND-REVIEWER.md`.
Do **not** add a new alwaysApply rule file in Auto v1 (coverage blast).

### §ISR.7.5 — Other doc pointers (ISR-b writes)

Auto **must** add one pointer sentence (no new ceremony) to:

- `AGENTS.md`
- `docs/consumers/scooling/OVERSEER-SETUP.md`
- `docs/consumers/knowtation/OVERSEER-SETUP.md`

Each sentence names `docs/INDEPENDENT-SECOND-REVIEWER.md` and states the kit
does not run another model. No live consumer `ok init`.

Amend `tools/optional_feature_tips/surface.py`: when `honesty.enabled` is true
and `require_independent_second_reviewer` is `off`, append one tip naming the
config key and the paste doc. When honesty is off, extend the existing honesty
tip to mention ISR as well as verification-evidence. Do not fail status on tips.

### §ISR.7.6 — Tool neutrality (normative)

| Host | Record | Check | Instructions |
| --- | --- | --- | --- |
| Any (`ok` CLI) | `ledger append` | Mode D + status surface | paste doc |
| Cursor | same | same | skill + amended BV rule (if repo root) |
| Claude Code | same | same | `.claude/skills` after sync |
| Copilot / paste | same | same | `docs/INDEPENDENT-SECOND-REVIEWER.md` |

No MuseHub-only behavior. Mode D and the status surface run on `git-only`.

Cursor hooks / Automations are **not** in scope and are **not** a DONE gate.

---

## §ISR.8 — Exit codes (frozen)

Additive code; non-overlapping with existing
`1`, `2`, `4`, `5`, `7`, `8`, `10`–`11`, `20`–`26`, `30`–`37`:

| Code | Meaning | Where |
| --- | --- | --- |
| `38` | Independent second review required but missing (no matching `isr_verdict=pass` under §ISR.5.3) | `honesty-status` Mode D when `require_independent_second_reviewer: require`; JSON `error` = `missing_independent_second_review` |

Constant name (frozen): `EXIT_MISSING_INDEPENDENT_SECOND_REVIEW = 38` in
`tools/honesty/status.py`. CLI and tests import that name. Do not reuse
`33` / `34` / `20`.

Reused (no renumbering):

| Code | Reuse |
| --- | --- |
| `1` | Usage — Mode D combined with A/B/C or other §ISR.5.2 `None` |
| `2` | Malformed schema (bad `isr_verdict`, `round < 1`, empty `producer_session_id`, same-session ids, both agent ids equal, …); **and** `ok status --exit-code` / governance-sync when the active-slice require probe misses |
| `4` | Honesty module disabled / config refuse |
| `23` | Role violation (`actor_role` ≠ `verifier`) |
| `25` / `26` | Provenance (P0; unchanged) |

`38` is confined to honesty-status Mode D. It does not change
`status --exit-code` precedence (`2 > 6 > 35 > 3 > 0`).

---

## §ISR.9 — Boundary, capability, rejection (governance, not runtime)

**The single most important frozen rule:** the kit records and optionally gates
the second-reviewer *claim*. It never runs another model, never opens a second
chat, and never treats host UI as a control surface.

| Concern | Overseer Kit | Operator / host runtime |
| --- | --- | --- |
| Append `independent_second_review` | Yes (validate + chain) | Supplies JSON body + session ids |
| Gate Mode D / status / governance-sync | Yes (off/warn/require) | Decides when to enable |
| Open a second chat / composer | **Never** | Yes |
| Dispatch / host / call a reviewer model | **Never** | Yes (Cursor picker, Claude, human, CI agent) |
| Infer session ids from the IDE | **Never** | Supplies opaque strings |
| Run `/build-verification-review` thinking | **Never** (skill is process; K5 `ok review --freeze` is a different gate) | Second chat / verifier |
| Prove chat identity cryptographically | Optional P0 only | Muse / operator |
| Tier-3 merge authorization | **Never** | Operator |

Capability tiers:

| Capability | `git-only` (baseline) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Record + gate ISR on file ledger | Full | Full (identical) |
| Optional signed `provenance` | Soft (unsigned OK) | Hard when `require_agent_signature: true` (P0) |
| Dispatch a second model | **Not in the kit** | **Not in the kit** |

| Temptation | Verdict |
| --- | --- |
| `ok` shells out to a reviewer model to "be the second reviewer" | **Reject** |
| Cursor hook that clicks "New Chat" | **Reject** — no honest API; not portable |
| Same session appends ISR with a made-up second id as a kit-blessed pass | **Reject as process**; kit cannot stop a liar, only refuse equal ids |
| Default `require` for all consumers | **Reject this phase** |
| Waive BV because ISR passed | **Reject** — both gates; V1–V8 still apply |
| Waive ISR because Mode B evidence exists | **Reject** — evidence ≠ independence |
| Apply ISR to this Thinking freeze before the kind exists | **Reject** — K5 freeze-review is the ISR-a gate |

---

## §ISR.10 — SPEC §5 additive row (ISR-b writes)

Amend the existing `ok honesty-status` row. Do not add a new command row.

Additive clause (normative text Auto must include):

> **ISR additive:** Mode D `--independent-second-review PHASE_ID` with optional
> `--producer-session` / `--frozen-spec`; exit `38` +
> `missing_independent_second_review` when
> `require_independent_second_reviewer: require` and no match. Frozen:
> `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md`.

`ok status` additive JSON key: `independent_second_reviewer_gate` (optional;
absent when the probe skips). `--exit-code` folds
`independent_second_reviewer_gate.ok` (require mode only) into the existing
`2` tier. Frozen in this document §ISR.6.

SPEC §5 `ok status` row must gain an **ISR additive** clause naming that JSON
key and the exit-`2` fold.

---

## §ISR.11 — Seven-tier matrix (ISR-b)

| Tier | Must prove |
| --- | --- |
| **unit** | `independent_second_review` in `ENTRY_KINDS`; validate accepts a minimal valid body; rejects same `actor_session_id`/`producer_session_id` → `2`; empty/missing `producer_session_id` → `2`; non-verifier → `23`; bad `isr_verdict` → `2`; `round < 1` → `2`; both agent ids equal → `2`; one agent id only → accept; genesis forbid-list includes new keys; `frozen_spec` opaque non-empty without must-exist; `require_independent_second_reviewer` parse (`off\|warn\|require`, default `off`, unknown → config `2`); key in `HONESTY_KEYS`; `HonestyConfig` field default `off`; `HonestyErrorToken` includes `missing_independent_second_review`; `_resolve_mode` invariants §ISR.5.2 (1)–(8); `find_matching_independent_second_review` last-wins, pin when producer supplied, reject `findings`. |
| **integration** | `ledger append --kind independent_second_review` writes a hash-chained line; `ledger verify` → `0`; Mode D `require` + no match → `38` + JSON token; matching `pass` → `0` + `matched_entry_hash`; `warn` miss → `0` + stderr warning; `off` → not enforced; Mode D + Mode B flags → `1`; Mode D + `--hook` → `1`; Mode A without Mode D flags remains byte-identical; `honesty.enabled: false` → `4`; fixture lock/status: Auto DONE claim + `require` + no ISR → `status --exit-code` `2` + JSON gate; after append, coverage of this gate no longer forces `2`. |
| **e2e** | git-only fixture: enable honesty + ISR warn + active Auto DONE without ledger → status exit `0` + warn payload; `require` → exit `2` + token; Mode D with `--producer-session` matching entry → `0`; same session ids refused at append; `ok next` still extracts the same fence after docs pointer edit. Identical unsigned path under a Muse-regime fixture. |
| **stress** | Ledger with ≥ 50 ISR entries; match scan last-wins; no unbounded walk. |
| **data-integrity** | Canonical hash includes `producer_session_id` / `isr_verdict` / session ids (tamper breaks verify → `22`); append does not embed chat transcripts; dry-run / validate-fail writes nothing; Mode D omit-producer vs pin-producer do not rewrite the ledger. |
| **performance** | Append + Mode D match + active-slice probe finish in a bounded time (same order as `ok status`). |
| **security** | Session ids / notes that look like URLs or shell metacharacters are opaque — never fetched, never executed; no network and no model call on append/verify/match/status paths (asserted); no secrets required in ISR fields; producer role cannot append (`23`); equal session ids cannot pass; exit `38` cannot be waived by omitting Mode D when CI invokes it under `require`; no absolute machine paths in JSON gate payload. |

Exact test file prefix: `test_isr_` (under `tests/` seven-tier folders). Do not
invent a second family name.

---

## §ISR.12 — Definition of Done

**ISR-a (this phase):** this document reviewed → `pass` with a CLI stamp;
ROADMAP ISR-a → DONE; NEXT → ISR-b; no Auto code; no `main` merge; no live
posture flips; no secrets.

**ISR-b:** every in-scope deliverable exists at the path this freeze names;
§ISR.11 green; kit dogfood `require_independent_second_reviewer: warn` written;
`ok sync --yes` so new skill twins land in the lock (coverage stays `ok`);
SPEC §5 + AGENTS + consumer stubs + paste doc + BV V9 + BV rule + optional
tips updated; no consumer defaults; no model dispatch; no tab/new-chat claim;
`ok status --exit-code` not failing this gate on this repo unless an active
Auto slice falsely claims DONE; ROADMAP + HANDOVER updated together;
`/build-verification-review` → `pass` **from a second chat** before ISR-b
DONE (dogfood the gate at warn). Merge remains Tier 3.

---

## §ISR.13 — Operator paste for ISR-b (informational; GS-PASTE may regen)

Model: **Auto**. Build exactly against this file. Do not redesign. Do not
dispatch a model. Do not enable ISR `require` for consumers. Do not claim the
kit opened a second chat.

---

## §ISR.14 — Cross-references

- LT §LT.2 / §LT.5.3 — deferred this gate; active-slice skip posture reused
- P-evidence — Mode B / V8; not replaced
- P-deploy — Mode C / §PD.5.0 resolution pattern this phase amends
- P-route — rule-holder, not executor
- K5 / K9a / K10 — freeze review, roles, ledger
- K7 — no MuseHub-only baseline
- ONS — portable CLI + docs; no tab-reload claim
- Check OK — ad-hoc honesty; not a substitute for ISR on Auto DONE
