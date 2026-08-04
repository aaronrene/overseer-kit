# Phase Track P / P-evidence — Verification evidence capture (Thinking freeze)

Status: **Reviewed → `pass` (P-evidence-r3).** P-evidence Thinking is **spec-only** and now frozen; no
code, no skill file edit, and no ledger schema change land in this phase. The P-evidence Auto build
(`{step}b`) is cleared to start mechanically against this frozen contract; it is the only phase that
writes files. Do **not** re-derive this contract during the Auto build.

```yaml
phase: TRACK-P-P-EVIDENCE
outputs:
- id: track-p-p-evidence
  path: docs/archive/phases/PHASE-TRACK-P-P-EVIDENCE.md
  frozen: true
frozen_inputs:
- id: k9a-l1-l2-module-freeze
  path: docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md
- id: honesty-ledger-impl
  path: tools/honesty/ledger.py
- id: honesty-validate
  path: tools/honesty/validate.py
- id: honesty-types
  path: tools/honesty/types.py
- id: honesty-artifact
  path: tools/honesty/artifact.py
- id: build-verification-skill
  path: cursor/skills/build-verification-review/SKILL.md
- id: layered-honesty-vision-l2
  path: docs/archive/thinking/OVERSEER-KIT-LAYERED-HONESTY-VISION.md#23-l2--honesty--roles-track-h--kit-honesty-module
- id: p0-agent-provenance
  path: docs/archive/phases/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: roadmap-p-evidence-row
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T17:24:10Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:c1b9fb3007085bdebba5986aa331ccf9383d120222c6e51f82574e827cd0c99b
```

**Downstream edge:** the P-evidence Auto build (`{step}b`) treats this document as ground truth
without re-deriving it (SPEC §6 mandatory reviewed freeze). The build-verification skill and the
L2 honesty ledger consume the frozen evidence schema as ground truth for what a *verification
evidence* record looks like — but the runtime / operator / CI runner, never the kit, produces the
underlying bytes (test logs, health-check records, screenshots) or performs any deploy.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| P-evidence-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist gate clean (0 findings). Semantic review raised three MAJOR completeness findings + two MINOR consistency findings. No escalation categories. |
| P-evidence-r1 fix | Author (cited lines only) | — | **R1-M1** fixed: §PE.6.3 freezes `missing_verification_evidence` + Mode B JSON key. **R1-M2** fixed: §PE.6.2 Mode A/B mutual exclusion + usage `1`. **R1-M3** fixed: §PE.3 `frozen_spec` opaque non-empty string, no must-exist. **R1-N1** fixed: exact flag names. **R1-N2** fixed: additive K9a enum amendment note in §PE.3. |
| P-evidence-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | R1 items confirmed RESOLVED. New: **R2-M1** §PE.6 omitted mandatory `HONESTY_KEYS` frozenset update (`adapters/config.py` unknown-key fail-closed) — Auto would ship a key that config rejects. **R2-N1** §PE.6 `off` wording contradicted §PE.6.2 (check still runs for JSON). |
| P-evidence-r2 fix | Author (cited lines only) | — | **R2-M1** fixed: §PE.6 parse rule 2 requires `HONESTY_KEYS` membership. **R2-N1** fixed: `off` row aligned with Mode B JSON-still-emits semantics. |
| P-evidence-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings). Semantic re-read confirmed R1-M1–M3, R1-N1–N2, R2-M1, R2-N1 RESOLVED; exit `33` + `missing_verification_evidence` non-overlapping; Mode A/B mutual exclusion deterministic; `frozen_spec` opaque; boundary held (kit records/gates, never deploys); seven-tier matrix complete; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `overseer review --freeze`. |

---

## §PE.0 — Simple summary

After an Auto build, an agent can say "tests are green," "health check passed," or "the UI looks
right" in the handover — and today the only check that those claims match reality is a thinking
reviewer reading git and test output in the moment (build-verification V8). That review is not
itself recorded as durable, content-addressed evidence on the honesty ledger. The claim lives in
prose; the proof evaporates with the chat.

**Track P / P-evidence freezes verification-evidence capture:** extend the L2 honesty ledger with
one new entry kind that records content-addressed verification artifacts — a **test-output hash**,
a **deploy/health-check ref** (plus hash of the operator-supplied record), and a **screenshot ref**
(plus image hash) — and extend the build-verification skill so a `pass` (and recorded `findings` /
`blocked` rounds) can bind those artifacts to a phase, round, and verdict. The kit never runs the
deploy, never hits a public URL, never takes a screenshot, and never stores binary blobs in the
ledger. It only **records and optionally gates claims** against hashes and opaque refs the
operator or runtime supplies.

**Technical summary:** add ledger kind `verification_evidence` to the frozen entry-kind enum;
freeze a closed artifact-type vocabulary (`test_output` | `deploy_health` | `screenshot`); validate
`sha256` (lowercase hex of referenced bytes) + per-type `ref` rules; extend `honesty:` with
optional `require_verification_evidence: off|warn|require` (default `off`); extend
`/build-verification-review` so V8 and the skill output cite/bind these artifacts; add exit code
`33` for missing required evidence. Reuses the existing L2 ledger chain, provenance envelope, and
role model — no parallel store.

---

## §PE.1 — Scope

**In scope (freeze only — this phase writes no code):**

- The new ledger entry kind `verification_evidence` and its required fields (§PE.3).
- The closed artifact-type vocabulary and per-type `sha256` / `ref` rules (§PE.4).
- Append / validate / show behavior on the existing `overseer ledger` surface (§PE.5).
- The optional `honesty.require_verification_evidence` config flag, honesty-status Mode A/B
  mutual exclusion, Mode B JSON key, and `missing_verification_evidence` error token (§PE.6).
- The normative build-verification skill delta (V8 + evidence table + optional ledger append)
  (§PE.7).
- Exit code `33` and reuse of existing honesty codes for schema / role / evidence-free / usage
  faults (§PE.8).
- The boundary + capability table (kit records/gates claims; never deploys) (§PE.9).
- The seven-tier test matrix the P-evidence Auto build must satisfy (§PE.10).

**Out of scope (explicit non-goals — prevent creep):**

- **Any deploy, HTTP health-check, browser automation, or screenshot capture inside the kit.** The
  kit never opens a network connection to a deploy target, never shells out to a browser, and never
  writes image files. Operator / CI / runtime produce those artifacts; the kit only hashes and
  records refs the caller supplies.
- **Storing binary blobs (screenshots, full logs) inside the ledger JSONL.** Ledger entries carry
  hashes and opaque refs only. Bytes live on disk / in CI artifact storage under consumer control.
- **The live deployment gate (P-deploy).** ROADMAP exploration backlog already names P-deploy as
  the sibling that may later *gate* a "shipped" claim on a recorded deploy/health check. This slice
  only freezes the *record* shape (`deploy_health` artifact type). Implementing a hard "shipped"
  gate is out of scope.
- **Redesigning P0 provenance, P-route, or P-cost.** Provenance remains optional and additive on
  the new kind exactly as on every other non-genesis kind. Routing and cost-awareness are untouched.
- **Changing existing entry kinds** (`verdict`, `hook_check`, …) or the L1 `evidence.reexecuted`
  shape. L1 verdict evidence stays L1; L0 build-verification evidence is a separate kind so
  co-requirement matching and `require_l1_evidence` stay unambiguous.
- **Making verification-evidence mandatory for every repo.** Default is `off` (inert). Opt-in
  `warn` / `require` only. K7 guardrail: baseline capability remains fully usable on `git-only`
  without Muse and without forcing evidence appends.
- **Tier-3 merge, staging push, or live capability flips.** This freeze never authorizes them.

---

## §PE.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Entry-kind enum | `genesis`, `task_assigned`, `verdict`, `dispute_opened`, `overseer_ruling`, `approval_recorded`, `board_advance`, `hook_check` | `tools/honesty/types.py` (`ENTRY_KINDS`) |
| Verdict evidence | `evidence.reexecuted` non-empty string list (L1 step ids); empty → exit `24` | `tools/honesty/validate.py` |
| Artifact digest helper | `sha256_file_bytes(path)` → lowercase hex of raw file bytes | `tools/honesty/artifact.py` |
| Ledger append / verify / show | Hash-chained JSONL; server fills `prev_hash` / `entry_hash`; optional `provenance` | `tools/honesty/ledger.py`, `canonical.py` |
| Roles | `owner` \| `overseer` \| `producer` \| `verifier`; `verdict` requires `verifier` | `tools/honesty/types.py`, `validate.py` |
| L1 evidence posture | `honesty.require_l1_evidence: off\|warn\|require` (default `warn`) | `adapters/config.py`, K9a §K9.7 |
| Build-verification skill | Checklist V1–V8; V8 = "Agent claims match verifiable git state"; no ledger write | `cursor/skills/build-verification-review/SKILL.md` |
| Honesty exit codes | `20`–`24` (L2), `25`/`26` (provenance) | K9a / P0 |
| Track P codes | `30`/`31` (route), `32` (cost metadata) | P-route / P-cost |
| Boundary | Kit = governance / record / gate; never runtime deploy or model host | `AGENTS.md`, vision §2.3 |

P-evidence **must not** change existing kinds' required fields, existing exit-code meanings, the
canonical-hash algorithm, or the provenance envelope. It only **adds** one kind, one config flag,
one exit code, skill-normative text, and the validation rules for the new kind.

---

## §PE.3 — Ledger kind `verification_evidence` (frozen schema)

**Additive amendment of the K9a entry-kind enum:** K9a §K9.7 froze the prior closed set. This
phase **adds exactly one new value** and leaves every prior kind's required fields and semantics
byte-identical. Auto must extend `ENTRY_KINDS` in `tools/honesty/types.py` (and the matching
`validate_append_body` branches) — it must not fork a second ledger or renumber existing kinds.

```text
verification_evidence
```

**Envelope (unchanged rules from K9a / P0):** every non-genesis entry carries `v: 1`, `kind`,
`ts` (server may fill), `prev_hash` / `entry_hash` (server fills; client must not supply),
`actor_role`, `actor_session_id`, and optional `provenance` (validated exactly as today).

**Role rule (frozen):** `actor_role` MUST be `verifier`. Any other role → exit `23` (role
violation). Rationale: build-verification is an independent honesty gate; the producer of the build
must not certify their own evidence pack. This mirrors `verdict` requiring `verifier`.

**Kind-specific required fields (frozen):**

| Field | Type | Rule |
| --- | --- | --- |
| `phase_id` | non-empty string | Opaque phase / slice id (e.g. `Track P / P-cost`). Matches what ROADMAP / handover use for the slice under review. |
| `frozen_spec` | non-empty string | **Opaque path-shaped string** naming the frozen spec under review (conventionally repo-relative, e.g. `docs/archive/phases/PHASE-TRACK-P-P-COST-AWARENESS.md`). Append validation checks **non-empty string only** — it does **not** require the path to exist on disk and does **not** path-confine the stored string (existence may be ephemeral across machines; the hash chain records the claim, not a live FS check). Optional digest helpers that *read* a file to fill `subject_sha256` are separately path-confined (§PE.5). |
| `round` | integer ≥ 1 | Build-verification round number (matches the skill's "round N"). |
| `bv_verdict` | string enum | Closed vocabulary: `pass` \| `findings` \| `blocked` (lowercase). Any other value → exit `2`. |
| `artifacts` | non-empty array of objects | Each object validated per §PE.4. Empty array or non-array → exit `24` (evidence-free; same semantic family as empty `evidence.reexecuted`). |

**Optional fields (frozen):**

| Field | Type | Rule |
| --- | --- | --- |
| `subject_sha256` | string | When present: lowercase 64-char hex SHA-256 of the frozen-spec file bytes at review time (`sha256_file_bytes`). Malformed → exit `2`. Append does **not** recompute or verify this against disk unless a helper was used to produce it. |
| `notes` | string | Optional free-text reviewer notes (advisory; never a substitute for `artifacts`). |
| `provenance` | object | Optional; identical to P0 rules. |

**Example (normative shape, illustrative digests):**

```json
{
  "v": 1,
  "kind": "verification_evidence",
  "ts": "2026-07-13T18:00:00Z",
  "actor_role": "verifier",
  "actor_session_id": "bv-session-1",
  "phase_id": "Track P / P-cost",
  "frozen_spec": "docs/archive/phases/PHASE-TRACK-P-P-COST-AWARENESS.md",
  "round": 1,
  "bv_verdict": "pass",
  "subject_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "artifacts": [
    {
      "type": "test_output",
      "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "ref": "pytest -q (569 passed)",
      "notes": "seven-tier suite"
    },
    {
      "type": "screenshot",
      "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "ref": "docs/archive/verify/p-cost-status.png"
    }
  ],
  "prev_hash": "…",
  "entry_hash": "…"
}
```

Genesis must not carry any of these kind-specific keys (extend the existing genesis forbid-list in
`validate_append_body` to include `phase_id`, `frozen_spec`, `round`, `bv_verdict`, `artifacts`,
`subject_sha256` — additive to the keys already refused).

---

## §PE.4 — Artifact object schema (frozen)

Each element of `artifacts[]` is an object with:

| Field | Required? | Rule |
| --- | --- | --- |
| `type` | yes | Closed vocabulary (lowercase): `test_output` \| `deploy_health` \| `screenshot`. Unknown → exit `2`. |
| `sha256` | yes | Lowercase hex string of length 64 matching `^[0-9a-f]{64}$`. Digests **raw bytes** of the referenced content (same algorithm family as `sha256_file_bytes`). Uppercase or wrong length → exit `2`. |
| `ref` | per-type | Non-empty string when required by type (below). Opaque to the kit — never fetched, never executed. |
| `notes` | no | Optional string. |

**Per-type rules (frozen):**

| `type` | What `sha256` digests | `ref` |
| --- | --- | --- |
| `test_output` | Raw bytes of the test runner output the verifier used (stdout capture, JUnit/XML file, or equivalent durable log). | **Optional.** Opaque label or repo-relative path naming the capture. |
| `deploy_health` | Raw bytes of an **operator-supplied** health-check *record* (e.g. saved response body, CLI health JSON, CI job log excerpt). The kit does **not** perform the check. | **Required.** Opaque operator/CI ref identifying the check (URL string, job id, environment name, etc.). Stored only; never fetched. |
| `screenshot` | Raw bytes of the image file. | **Required.** Repo-relative path or opaque storage label for the image. Bytes are not embedded in the ledger. |

**Cardinality (frozen):**

1. `artifacts` MUST contain at least one object.
2. Duplicate `type` values in one entry are **allowed** (e.g. two screenshots); order is preserved
   as supplied and is part of the canonical hash payload.
3. No artifact type is mandatory for every entry at the schema layer. Policy for "what a `pass`
   needs" is the skill (§PE.7) + optional config (§PE.6), not a hard schema require of all three
   types on every append.

**What the kit never does with `ref`:** resolve DNS, open HTTP(S), follow redirects, shell out to
image tools, or treat `ref` as a filesystem write target. Optional Auto-build helpers may *read* a
repo-confined path solely to compute `sha256` when the caller passes a path flag — that helper is
read-only path-confined I/O, not a deploy or health probe.

---

## §PE.5 — Ledger CLI surface (frozen, additive)

Reuse existing commands; no new top-level verb required.

| Surface | Behavior |
| --- | --- |
| `overseer ledger append --kind verification_evidence` | Validates §PE.3–§PE.4; appends one JSONL line; auto-genesis when ledger empty (existing rule). Body via `--file` / `--stdin` (existing cardinality). |
| `overseer ledger verify` | Existing chain + provenance walk; new kind participates identically (hash continuity). No special-case skip. |
| `overseer ledger show` | Existing show; new kind appears like any other entry. |

**Kind authority:** CLI `--kind` remains authoritative vs body `kind` (K9a rule unchanged).

**Helpers the Auto build MAY add (frozen allowance, not a redesign):**

- A small pure function `validate_verification_artifacts(artifacts) -> None` in `tools/honesty/`
  (or extend `validate_append_body`).
- An optional convenience to compute `sha256` from a path-confined file for the caller (wrapping
  `sha256_file_bytes`) — still no network.

No new `overseer evidence` command is required in this slice. If the Auto build finds a thin
wrapper improves UX, it must remain a thin alias over `ledger append` and must not add network or
deploy capabilities.

---

## §PE.6 — Config: `honesty.require_verification_evidence` (frozen)

Extend the existing `honesty:` block with one additive key (default preserves current behavior):

```yaml
honesty:
  enabled: false
  # … existing keys unchanged …
  require_verification_evidence: off   # off | warn | require — default off
```

| Value | Meaning |
| --- | --- |
| `off` | (default) Mode B may still be invoked; the match is computed for JSON but **never** fails the exit code (`0` on the match dimension even when no entry exists). Repos that never set the key stay inert. |
| `warn` | Mode B on miss: stderr warning + exit `0` (reminder posture — same family as `require_l1_evidence: warn`). |
| `require` | Mode B on miss: exit `33`. |

Parse rules (frozen):

1. Value MUST be one of `off|warn|require` (string); anything else → config exit `2`.
2. Auto MUST add `require_verification_evidence` to `HONESTY_KEYS` in `adapters/config.py` (unknown-key fail-closed at `adapters/config.py` ~690–692). Omitting that frozenset update would reject a valid config as `unknown honesty keys`.
3. Default when the key is absent: `off`.
4. The flag is meaningless when `honesty.enabled: false` (module short-circuit exit `4` on ledger / honesty-status paths remains unchanged).

Regime: **regime-agnostic** `git-only` baseline capability. No Muse dependency. Optional
`provenance` on evidence entries follows P0 soft/hard rules independently.

### §PE.6.1 — Match rule (frozen)

A **matching** `verification_evidence` entry for check inputs `(phase_id, frozen_spec?)` is an
entry where all of:

1. `kind == verification_evidence`
2. `actor_role == verifier`
3. `bv_verdict == pass`
4. `phase_id` equals the requested phase id (exact string match)
5. If the caller supplies `frozen_spec`, it equals the entry's `frozen_spec`; if the caller omits
   it, any `frozen_spec` matches

Scan order: ledger file order; **last** matching entry wins (same "newest append wins" posture as
`matched_verdict_hash` for verdicts).

### §PE.6.2 — `honesty-status` invocation modes (frozen)

Today `overseer honesty-status` requires `--hook` + `--artifact` (`tools/honesty/status.py`).
P-evidence adds a **second, mutually exclusive mode**. Exact CLI flag names are frozen (no
aliases in this slice):

| Mode | Required flags | Forbidden together with |
| --- | --- | --- |
| **A — verdict co-requirement (existing)** | `--hook HOOK` + `--artifact PATH` | `--verification-evidence`, `--frozen-spec` |
| **B — verification evidence (new)** | `--verification-evidence PHASE_ID` | `--hook`, `--artifact`, `--producer-session` |

Optional in Mode B only: `--frozen-spec PATH_STRING` (opaque string passed through to the match
rule; not a filesystem must-exist check).

**Usage exit `1` when:**

- Neither mode is fully specified (missing Mode A pair and missing Mode B flag), or
- Flags from Mode A and Mode B appear in the same invocation (any overlap), or
- `--frozen-spec` appears without `--verification-evidence`

When Mode B flags are absent, Mode A behavior is **byte-identical** to pre-P-evidence (including
existing JSON keys and exit codes).

Mode B applies `require_verification_evidence` per §PE.6 (`off` → always `0` for the match
dimension and still emits the JSON block below; `warn` → stderr warning + `0` on miss;
`require` → `33` on miss). Module disabled → existing `4` short-circuit before mode logic.

The build-verification skill (§PE.7) is the process obligation that *creates* the entry; Mode B
is how CI / operators *confirm* it later.

`require_verification_evidence` does **not** alter `require_verdict_on` / board_done / handoff /
register co-requirement. Those remain L2 verdict gates. Verification evidence is the L0
build-verification honesty record.

### §PE.6.3 — Mode B JSON + error token (frozen)

Extend `HonestyErrorToken` (`tools/honesty/types.py`) with exactly one additive value:

```text
missing_verification_evidence
```

Used when Mode B exits `33`. Do not overload `missing_verdict` or `evidence_free` for this case.

`HonestyStatusJson.to_dict()` gains one additive key, present **only on Mode B responses**
(Mode A responses omit the key entirely so existing consumers stay compatible):

```json
{
  "ok": false,
  "exit_code": 33,
  "command": "honesty-status",
  "hook": null,
  "artifact": null,
  "artifact_sha256": null,
  "producer_session": null,
  "matched_verdict_hash": null,
  "error": "missing_verification_evidence",
  "verification_evidence": {
    "phase_id": "Track P / P-cost",
    "frozen_spec": null,
    "require": "require",
    "matched_entry_hash": null
  }
}
```

| `verification_evidence` field | Rule |
| --- | --- |
| `phase_id` | Echo of `--verification-evidence` |
| `frozen_spec` | Echo of `--frozen-spec` or `null` |
| `require` | Effective config value `off`\|`warn`\|`require` |
| `matched_entry_hash` | `entry_hash` of the last matching pass entry, or `null` |

On Mode B success (`0`): `ok: true`, `error: null`, `matched_entry_hash` set when a match exists;
under `off` with no match, `ok: true`, `matched_entry_hash: null`, `error: null` (check not
enforced). On `warn` miss: `ok: true`, `error: null`, `matched_entry_hash: null`, plus stderr
warning.

---

## §PE.7 — Build-verification skill delta (frozen, normative)

The Auto build updates **both** vendored skill paths so they stay twins:

- `cursor/skills/build-verification-review/SKILL.md`
- `.cursor/skills/build-verification-review/SKILL.md`

**V8 (replace / extend the existing one-liner):**

| # | Check | Dishonesty signal |
| --- | --- | --- |
| V8 | Agent claims match verifiable state **and** (when `honesty.enabled`) are bound to ledger `verification_evidence` artifacts | "All green" with empty/unrelated diff; "tests passed" with no `test_output` hash; "deployed" / "healthy" with no `deploy_health` ref+hash; "UI verified" with no `screenshot` hash — or a claimed `pass` with no matching ledger entry when `require_verification_evidence: require` |

**Evidence table (required in skill output whenever honesty module is enabled, and recommended
always):**

```markdown
### Evidence
| type | sha256 | ref | notes |
| --- | --- | --- | --- |
| test_output | <64 hex> | <label or path> | <optional> |
```

Rules for a skill verdict of **`pass`** (frozen process rules):

1. V1–V7 unchanged in meaning.
2. V8 requires citing verifiable git/test state as today.
3. When `honesty.enabled: true`, a `pass` MUST be accompanied by appending (or confirming a prior
   append of) a `verification_evidence` entry with `bv_verdict: pass`, matching `phase_id` +
   `frozen_spec` + `round`, and a non-empty `artifacts` list that includes at least one
   `test_output` artifact whose `sha256` digests the test output the reviewer actually used.
4. `deploy_health` and `screenshot` artifacts are **required in the entry only when the build
   session's claims mention deploy/health or visual/UI proof**; otherwise they are omitted. The
   skill must not invent fake deploy/screenshot evidence.
5. When `honesty.enabled: false`, ledger append is skipped; V8 still requires claims↔git/test
   honesty in the review text (baseline without L2).
6. `findings` / `blocked` rounds MAY append `verification_evidence` with the corresponding
   `bv_verdict` so the chain records failed rounds; this is allowed but not required for skill
   progress. A later `pass` round is a separate append (new `round`).

Hard stops unchanged: no merge to `main` on `findings`/`blocked`; uncited findings invalid.

---

## §PE.8 — Exit codes (frozen)

Additive code; non-overlapping with existing `1`,`2`,`4`,`5`,`7`,`8`,`10`–`11`,`20`–`26`,`30`–`32`:

| Code | Meaning | Where |
| --- | --- | --- |
| `33` | Verification evidence required but missing (no matching `bv_verdict=pass` entry under §PE.6.1) | `honesty-status` Mode B when `require_verification_evidence: require`; JSON `error` = `missing_verification_evidence` (§PE.6.3) |

Reused (no renumbering):

| Code | Reuse for this kind |
| --- | --- |
| `1` | Usage — Mode A/B underspecified or combined (§PE.6.2) |
| `2` | Malformed schema (unknown type, bad sha256, missing required `ref`, bad `bv_verdict`, bad `round`, …) |
| `4` | Honesty module disabled / config refuse (existing short-circuit) |
| `23` | Role violation (`actor_role` ≠ `verifier`) |
| `24` | Evidence-free (`artifacts` empty or missing) |
| `25`/`26` | Provenance signature failure / required signature absent (P0; unchanged) |

`33` is confined to honesty-status Mode B. It does not change `status --exit-code` precedence and
does not block `governance-sync` by itself.

---

## §PE.9 — Boundary & capability table (frozen)

The single most important frozen rule: **the kit records and optionally gates verification
claims; it never performs the underlying verification actions that produce the bytes.**

| Concern | Overseer Kit (evidence recorder / gate) | Operator / CI / runtime |
| --- | --- | --- |
| Append `verification_evidence` to L2 ledger | Yes | Supplies JSON body / files |
| Hash file bytes path-confined | Yes (read-only helper) | Produces the files |
| Validate schema + roles | Yes | — |
| Run test suite | **Never required of the kit CLI for this kind** | Yes (caller runs tests, then hashes output) |
| Deploy to a host / public URL | **Never** | Yes (outside kit) |
| HTTP(S) health probe of a deploy | **Never** | Yes; then supply record bytes + ref |
| Capture / render screenshots | **Never** | Yes |
| Embed screenshot or log bytes in ledger | **Never** | Store blobs elsewhere |
| Opt-in require/warn on missing evidence | Yes (`require_verification_evidence`) | Decides when to enable |
| Tier-3 merge authorization | **Never** (stop for human) | Operator |

Capability tiers:

| Capability | `git-only` (baseline) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Record verification evidence on file ledger | Full | Full (identical) |
| Optional signed `provenance` on evidence entries | Soft (unsigned OK) | Hard when `require_agent_signature: true` (P0) |
| Perform deploy / live health check | **Not in the kit** | **Not in the kit** |

P-deploy (exploration backlog) may later add a gate that *consumes* `deploy_health` artifacts
before a "shipped" claim; that gate is a separate Thinking freeze and is not authorized here.

---

## §PE.10 — Seven-tier test matrix (P-evidence Auto build must satisfy)

The P-evidence Auto build ships all seven tiers green locally before DONE
(`policy/test-tiers.yaml`).

| Tier | Proves |
| --- | --- |
| **unit** | `verification_evidence` accepted in `ENTRY_KINDS`; validate accepts a minimal valid body; rejects unknown `type`, uppercase/short `sha256`, missing `ref` for `deploy_health`/`screenshot`, empty `artifacts` → `24`, non-verifier `actor_role` → `23`, bad `bv_verdict` → `2`, `round < 1` → `2`; genesis forbid-list includes new keys; `frozen_spec` accepts opaque non-empty string without requiring file existence; `require_verification_evidence` parse (`off\|warn\|require`, default `off`, unknown → config `2`); key accepted in `HONESTY_KEYS` (not rejected as unknown); `HonestyErrorToken` includes `missing_verification_evidence`. |
| **integration** | `ledger append --kind verification_evidence` writes a hash-chained line; `ledger verify` returns `0` on a chain including the new kind; Mode B `honesty-status --verification-evidence PHASE` with `require` and no match → `33` + JSON error token; with a matching `pass` entry → `0` + `matched_entry_hash`; `warn` missing → `0` + stderr warning; `off` → check not enforced; combining Mode A + Mode B flags → `1`; Mode A without Mode B flags remains byte-identical; `honesty.enabled: false` → existing `4` short-circuit unchanged. |
| **e2e** | Fixture repo: append genesis + `verification_evidence` with `test_output` (+ optional `screenshot`); show lists it; honesty-status Mode B match rule last-wins across two rounds (`findings` then `pass`); skill-normative fixture asserts a `pass` body includes `test_output`. Identical behavior under `git-only` and a Muse regime for the unsigned path. |
| **stress** | Large `artifacts` list (bounded, e.g. ≥ 50 objects) appends and verifies within a documented bound; many evidence entries do not break chain verify; order stability of artifacts in canonical hash. |
| **data-integrity** | Canonical hash includes `artifacts` content (tamper of a stored sha256 breaks verify → `22`); append does not embed file bytes in the JSONL line; path helper (if present) is path-confined (escape → refuse); idempotent verify; no partial ledger write on validation failure. |
| **performance** | Append + verify of a realistic evidence entry completes within a bounded time; match scan is linear in ledger length with no unbounded filesystem walk of screenshot trees. |
| **security** | `ref` values that look like URLs or shell metacharacters are treated as opaque strings — never fetched, never executed; no network on append/verify/match paths (asserted); no secrets required in evidence fields; producer role cannot append (`23`); ledger lines contain hashes/refs only (no raw screenshot/log payload); exit `33` cannot be waived by omitting the check flag when CI invokes it under `require`. |

---

## §PE.11 — Shared-contract note (informative)

- **Build-verification agents** treat this schema as the durable proof side of V8 when honesty is
  enabled.
- **Consumer CI** may call `honesty-status --verification-evidence …` after Auto builds to fail
  closed under `require`.
- **P-deploy (future)** should reuse `deploy_health` artifact objects rather than inventing a
  parallel record shape.
- **VideoFactory / other L1 consumers** keep using `verdict.evidence.reexecuted` for checkpoint
  re-execution; they may *additionally* append `verification_evidence` for L0 build-verification
  of kit-side phases — the kinds do not substitute for each other.

---

## §PE.12 — Definition of Done (Thinking freeze)

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `overseer review --freeze`
- [x] Review-record table stamped; `review_stamp` filled
- [x] `docs/ROADMAP.md` P-evidence Thinking → DONE; Auto build row present / queued
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for P-evidence Auto build (SD-17)
- [x] No code / skill / config landed in the Thinking phase itself
- [x] No Tier-3 merge performed

## §PE.13 — Definition of Done (Auto build — for the next session)

- [x] Mechanical implementation matches §§PE.3–PE.8
- [x] Both skill paths updated per §PE.7
- [x] Seven-tier matrix §PE.10 green
- [x] `/build-verification-review` → `pass` before ROADMAP Auto row → DONE
- [x] Governance sync (ROADMAP + HANDOVER) in the closing commit
- [x] Feature-branch push / PR only; merge remains Tier 3
