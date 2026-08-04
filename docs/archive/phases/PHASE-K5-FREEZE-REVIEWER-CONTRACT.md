# Phase K5 — Freeze Reviewer Contract (Frozen Thinking Outline, K5a)

Status: **Frozen contract for K5b (Auto Build). No reviewer CLI implementation in this step. No
`governance-sync` agent (that is 9A-5). No consumer-repo migration (that is K6). No live Automation
enablement that requires Tier-3 operator action. No `main` merge without review.** This doc is the
machine-checkable ground truth K5b implements mechanically against; it refines — and stays compatible
with — `docs/OVERSEER-KIT-SPEC.md` §6 (esp. §6.2), and adds no code.

## Freeze-contract declaration (§6.1 schema)

```yaml
phase: K5a
outputs:
  - id: k5-freeze-reviewer-contract
    path: docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
    frozen: true                     # K5b treats this as ground truth without re-deriving
frozen_inputs:
  - id: kit-spec-freeze-contract
    path: docs/OVERSEER-KIT-SPEC.md#6
  - id: kit-spec-freeze-reviewer-config
    path: docs/OVERSEER-KIT-SPEC.md#6.2
  - id: kit-vendoring-cli-contract
    path: docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md
  - id: kit-model-labels
    path: policy/model-labels.yaml
  - id: kit-test-tiers
    path: policy/test-tiers.yaml
  - id: freeze-review-skill
    path: cursor/skills/freeze-review/SKILL.md
```

**Downstream edge:** K5b (Auto) → consumes `k5-freeze-reviewer-contract` as ground truth. Per §6, this
is a **mandatory reviewed freeze** before K5b builds. Human escalation is required only if a finding
hits `security | irreversible | real_money | gates_tier3`. This contract defines the review capability
itself (including injection and least-privilege rules) — a `security` finding against this doc **does**
trigger human escalation before K5b may build.

**Review record (§6.2):**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 (2026-07-10) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | `blocked` (1 BLOCKER, 5 MAJOR, 3 MINOR) | Not cleared for K5b. No human escalation. Findings F1–F9 listed in round-1 table (historical). |
| 2 (2026-07-10) | Independent Freeze-Step Reviewer (Cursor, Thinking); file+line citations | `findings` (1 MAJOR, 2 MINOR) | F1–F9 **all confirmed resolved** (round-1 table). Full regression §K5.1–§K5.12 surfaced 3 new cited findings **N1–N3** (below). None escalating (no `security`/`irreversible`/`real_money`/`gates_tier3`) → **no human escalation**. Not cleared for K5b until N1–N3 resolved → `pass`. |
| 2-fix (2026-07-10) | Author fix revision (N1–N3) | — | **N1:** §K5.7 now defines a deterministic **pre-stamp canonical form** (excise `review_stamp` + re-serialize via a round-trip-stable serializer) so re-stamp digests are stable across runs; idempotent-stamp rule + §K5.12 data-integrity case updated. **N2:** §K5.6 citation-hard-rule now points to §K5.2 **step 9**. **N3:** §K5.1 exit-`4` row + §K5.4 refuse note now include the `--checklist` path/read causes (schema failures stay `2`). Awaiting round-3 confirmation. |
| 3 (2026-07-10) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | **`pass`** | N1–N3 **all confirmed resolved** (table below). Full regression §K5.1–§K5.12 green (F1–F9 hold; ground-truth edge; exits/`precedence`; nested reviewer + legacy; `reviewer_models`; findings/verdicts; fallback:human; §K5.9 one schema; Automation degrade; seven-tier matrix; security/injection/`adapter.status()` only; no K5b leak). **No human escalation.** Cleared for K5b Auto build. |

**Round 1 findings (cited) — historical; F1–F9 addressed in the fix revision below:**

| ID | Sev | Cat | Citation (at review time) | Resolution in this revision |
| --- | --- | --- | --- | --- |
| F1 | BLOCKER | completeness | §K5.7 stamp section | **Fixed:** §K5.7 freezes on-disk serialization for Markdown (fenced YAML) and YAML artifacts; machine stamp is `review_stamp:` inside the freeze block — not the narrative Review-record table. |
| F2 | MAJOR | consistency | §K5.0 vs §K5.7 locus | **Fixed:** locus pinned to **freeze block** (SPEC §6.2); narrative Review-record markdown table is human/agent-maintained only. |
| F3 | MAJOR | completeness | §K5.4 alternate grammar | **Fixed:** non-YAML / HTML-comment / heading-anchored forms dropped from K5b scope; only §6.1 YAML fence/mapping + operator-forced path. |
| F4 | MAJOR | completeness | `--checklist` row | **Fixed:** absent → §K5.5; present → **replaces** built-in; YAML `checks:` schema frozen; unit case added. |
| F5 | MAJOR | consistency | §K5.8 vs §K5.9 | **Fixed:** one report schema (§K5.9); human/fallback is the same object with escalation fields; human stdout vs `--json` rendering rules frozen. |
| F6 | MAJOR | completeness | `artifact_digest` / BOM | **Fixed:** digest uses §K4.7 **Canonical byte rules** items 1–2 by name (UTF-8 no BOM + LF line endings); parse and digest share that canonicalization. |
| F7 | MINOR | consistency | shared exit table | **Fixed:** `review --freeze` never emits `3` (DRIFT). |
| F8 | MINOR | consistency | exit `4` wording | **Fixed:** `4` causes match §K5.4 refuse list only. |
| F9 | MINOR | completeness | conflicting overrides | **Fixed:** `--mode human` + `--provider`/`--model` is ignore (not conflict); true conflicts enumerated. |

**Checks that passed in round 1 (no finding):** C1 ground-truth edge to K5b; args table §K5.2; exits `7`/`8` + precedence; nested `reviewer` schema + legacy normalization §K5.3; `reviewer_models` registry rule; findings/verdicts/citations §K5.6; `fallback: human` fail-closed; Automation degrade §K5.10; seven-tier matrix §K5.12; SPEC §6.2 field parity; injection/least-privilege; no K5b implementation leaked.

**Round 2 — F1–F9 re-verification (all confirmed RESOLVED):**

| ID | Verified at | Confirmation |
| --- | --- | --- |
| F1 | §K5.7 (locus table + on-disk serialization) | Serialization frozen for all three write paths — Markdown fence, whole-file YAML, and operator-forced `<!-- overseer:review-stamp -->` marker; machine stamp is `review_stamp:` in the freeze block, not the narrative table. **Resolved.** |
| F2 | §K5.0 write-column refinement; §K5.7 locus | Stamp locus pinned to the freeze block (= SPEC §6.2); narrative Review-record table is human/agent-maintained, never CLI-written. **Resolved.** |
| F3 | §K5.4 (declared form + out-of-scope list) | K5b parses only the §6.1 YAML mapping (whole `.yaml`/`.yml` or first fenced `yaml` block) + operator-forced; HTML-comment/heading/TOML/JSON declaration grammars explicitly out of scope. (The §K5.7 operator-forced *stamp write* marker is an output locus, not a declaration grammar — no conflict.) **Resolved.** |
| F4 | §K5.2 `--checklist` row + file schema; §K5.12 unit | Absent → §K5.5 built-in; present → **replace** (no union); `checks:` schema frozen; unit case asserts built-in ids absent from effective list. **Resolved.** |
| F5 | §K5.8 field table; §K5.9 one-schema report | Single §K5.9 report object for all outcomes; human/fallback fills escalation fields; `--json` vs human stdout rules frozen. **Resolved.** |
| F6 | §K5.7 "Canonical bytes for `artifact_digest`" | Cites §K4.7 **Canonical byte rules items 1 and 2** by name (UTF-8/BOM strip + LF), correctly disambiguated from the aggregate algorithm steps; parse and digest share the canonicalization. **Resolved.** |
| F7 | §K5.1 (exit table note + precedence); §K5.12 | `review --freeze` never emits `3`; precedence `2>4>5>8>7>0` omits `3`. **Resolved.** |
| F8 | §K5.1 exit-4 row; §K5.4 refuse list | `4` no longer used for verdicts; causes match the refuse semantics. (See N3 for a residual enumeration nit re the `--checklist` file.) **Resolved.** |
| F9 | §K5.2 conflicting/ignored override table | `--mode human` + `--provider`/`--model` = ignore (not conflict); true USAGE conflicts enumerated (unknown flag/enum, missing/duplicate `--freeze`). **Resolved.** |

**Round 2 findings (cited — new; line numbers at review time):**

| ID | Sev | Cat | Citation (at review time) | Finding |
| --- | --- | --- | --- | --- |
| N1 | MAJOR | consistency / data-integrity | §K5.7 canonical-bytes + idempotent-stamp rules (≈L531–546, L552–555); §K5.1 idempotency (≈L169–172); §K5.12 data-integrity (≈L723) | **Idempotent-stamp digest is non-deterministic for *interleaved* stamps.** `artifact_digest` is defined over "pre-stamp canonical bytes" where canonicalization = **only** §K4.7 rules 1–2 (BOM strip + LF). For a declared-Markdown fence or whole-file YAML the stamp is written **inside** the declaration mapping, so recovering "current pre-stamp canonical bytes" on a second run requires excising `review_stamp` and re-serializing — a transform whose bytes need not equal the original hand-authored pre-stamp bytes hashed on first write. No frozen rule defines that excision, so the recomputed digest can differ run-to-run, defeating the §K5.1 "no-op that does not rewrite the stamp timestamp" guarantee and the §K5.12 "run-twice identical / idempotent same-digest no-op" case. (Operator-forced *appended-block* Markdown is unaffected — its stamp is trailing and byte-recoverable.) **Fix:** freeze the pre-stamp digest as computed over the artifact with any existing `review_stamp` removed via the **same deterministic serializer** used to write it, so first-write and re-run digests agree. |
| N2 | MINOR | consistency (citation) | §K5.6 citation-hard-rule (≈L455); §K5.2 steps 8 & 9 (≈L247, L252) | The synthetic-uncited-finding rule is cross-referenced as "§K5.2 **step 8**," but step 8 is provider-reachability; the synthetic-`blocked` rule is **step 9**. Off-by-one citation error — notable because C8 (§K5.5) requires the contract's own review references to keep file+line discipline. **Fix:** change "step 8" → "step 9". |
| N3 | MINOR | completeness | §K5.1 exit-4 row (≈L150); §K5.4 refuse list (≈L394); §K5.2 `--checklist` (≈L217, step 5 ≈L242) | F8's resolution states "`4` causes match §K5.4 refuse list only," but `--checklist` path-escape/missing/unreadable → `4` (§K5.2) is a fourth-code cause **absent** from both the §K5.1 exit-4 row and the §K5.4 refuse list (exit-2's row *does* list checklist schema errors; exit-4's does not list checklist path errors). **Fix:** add the checklist-file refuse causes to §K5.1/§K5.4, or drop the word "only". |

**Round 3 — N1–N3 re-verification (all confirmed RESOLVED):**

| ID | Verified at | Confirmation |
| --- | --- | --- |
| N1 | §K5.7 pre-stamp canonical form (L565–603); idempotent stamp (L610–614); §K5.1 idempotency (L201–204); §K5.12 data-integrity (L782); §K5.4 parse share (L409–410) vs §K5.7 L601–603 | Pre-stamp form is deterministic and identical for never-stamped vs already-stamped across declared-MD fence, whole-file YAML (interleaved), and operator-forced appended marker (+ operator-forced YAML). Excision is byte-precise (outside-fence / prior bytes verbatim; stamp key deleted then re-serialized). Same round-trip-stable serializer required for write **and** digest. Idempotent no-op: no `reviewed_at` rewrite, no file write when digests match. Data-integrity tests cover re-stamp digest stability + YAML-whitespace invariance. Parse shares only §K4.7 items 1–2 (no contradiction with digest excision). **Resolved.** |
| N2 | §K5.6 citation-hard-rule (L487–489); §K5.2 steps 8–9 (L279–286) | Citation hard rule cites §K5.2 **step 9** (synthetic-`blocked`); step 8 remains reachability. Steps 1–12 numbering consistent end-to-end (incl. step-6 cross-refs at L259, L352). **Resolved.** |
| N3 | §K5.1 exit-`4` row (L182); §K5.4 refuse note (L426–429); §K5.2 `--checklist` (L248–249) | Exit `4` consolidates artifact **and** `--checklist` path/read refusals; checklist *schema* failures stay `2`. §K5.4 explicitly defers to §K5.1 for the full `4` set (no "§K5.4 only" overstatement in normative text). **Resolved.** |

**Freeze status:** **reviewed → `pass` (round 3).** Cleared for the K5b Auto build. **No human escalation** (no finding is `security`/`irreversible`/`real_money`/`gates_tier3`).

---

## Simple summary (no jargon)

This freezes exactly how the kit must run an automated check on a "frozen" document before a later
step is allowed to treat that document as settled truth. It nails down every switch the
`overseer review --freeze` command accepts, every exit number it can return, the shape of each
finding (always with a file and line so a human can verify), how a repo picks a local or remote
reviewer model (or a human), and what happens when that model is unreachable (always fall back to a
human — never skip the review). It also lists the full set of tests the build step must write and
pass. Nothing here implements the reviewer — it is the blueprint the next (mechanical) step follows.

## Technical summary

K5a freezes the argument contract, exit-code taxonomy, I/O / idempotency / dry-run semantics for
`overseer review --freeze`; the extended (spec-compatible, additive) `freeze_contract.reviewer`
config schema (`mode`, `model`, `provider`, `fallback`) with legacy-string normalization; the
reviewer-model label registry rule (labels only — never vendor slugs; `provider: local` first-class;
`fallback: human` fail-closed); the finding / verdict / stamp / escalation contracts; the provider
reachability + human-escalation report behavior; the Automation routing degrade path; and the concrete
seven-tier test matrix K5b must turn green. The engine remains Python (matching `cli/` +
`adapters/`), fronted by the existing POSIX `cli/overseer` shim. Review is read-first; the only
optional write is a local review stamp on `pass` (never a VCS commit). No core review capability may
be API-only.

---

## §K5.0 — Scope and hard stops (frozen)

**In scope for K5b (Auto Build):** implement `overseer review --freeze` exactly to this contract;
extend `adapters/config.py` to parse the nested `freeze_contract.reviewer` schema (with legacy
string normalization); add the `reviewer_models` registry to `policy/model-labels.yaml` per §K5.3;
implement the Freeze-Step Reviewer engine under `tools/freeze_reviewer/` (provider interface +
local/api backends + human-escalation report path); emit findings with mandatory file+line citations;
verdict → exit-code mapping; optional stamp write on `pass`; Automation **templates** (session-end /
on-merge) that invoke the CLI and degrade to slash-command/CLI when Automations are unavailable; the
seven-tier tests below.

**Explicitly NOT in K5:**

| Out of scope | Belongs to |
| --- | --- |
| `overseer governance-sync` (doc patching, realign, feature-branch commit) | 9A-5 |
| Any consumer-repo migration / running `init` against Scooling/Knowtation/MuseHub | K6 |
| Dogfood flip to `muse+git-mirror` | K7 |
| Live enablement of Cursor Automations that requires operator Tier-3 authorization | operator (templates ship; enablement is not automated by the kit) |
| Any `mirror` / `realign` / write to `main` or canonical | Tier 3, human |
| Any `main` merge of K5 work without review | governance gate |
| Redesign of §6 policy (verdicts, escalation conditions, citation rule) | frozen in SPEC; this doc only refines CLI/config/engine contracts |

**Adapter surface K5 may call:** `adapter.status()` only (read-only context in reports). Review never
calls `read_head`, `read_canonical_anchor`, `realign`, `commit_feature`, or `mirror`. The optional
stamp write is a local filesystem write into the reviewed artifact (Tier 1); committing that stamp is
the operator's normal feature-branch step, not the CLI's job.

**Refinement of SPEC §5 write column (frozen):** the table row "No (review output only)" means **no
VCS writes and no footprint/config/lock writes**. On `pass` without `--dry-run`, the CLI **may**
write a `review_stamp` mapping into the artifact's **freeze block** (§K5.7 — same locus as SPEC
§6.2). The narrative markdown Review-record table is not written by the CLI. `--dry-run` writes
nothing.

---

## §K5.1 — Global conventions (frozen; inherits §K4.1)

**Invocation:** `overseer review --freeze <path> [options]`. The published entrypoint remains the
POSIX shim `cli/overseer` → Python runtime. No global install required.

**Repo/config resolution:** identical to §K4.1 (`--repo` / walk-up / cwd; `--config` override;
absolute repo root before any file operation).

**Global options:** identical to §K4.1 (`-C/--repo`, `--config`, `--json`, `-q/--quiet`,
`-v/--verbose`, `--no-color`, `-h/--help`, `--version`).

**Output discipline (frozen):** human/report output → **stdout**; diagnostics/warnings/errors →
**stderr**. `--json` prints exactly one JSON object to stdout and nothing else on stdout. No command
prints secrets, tokens, credentialed URLs, **absolute machine paths**, or user identity (SPEC §9).
**All file references in every stream are repo-relative (POSIX).** Timestamps are ISO-8601 UTC with
trailing `Z`.

**Shared exit codes (inherited from §K4.1; review-relevant subset):**

| Code | Name | Meaning |
| --- | --- | --- |
| `0` | OK | Success — for review: verdict `pass`. |
| `1` | USAGE | Unknown command, bad/conflicting flags, missing required `<path>`. |
| `2` | CONFIG | Fail-closed: config missing/unparseable, unknown version, unsupported regime, invalid `freeze_contract` schema, unknown reviewer model label, invalid `--checklist` file, or adapter `ReadError` on a required read. |
| `4` | REFUSED | Review refused: `freeze_contract.enabled: false`; artifact `<path>` **or** `--checklist <path>` escapes repo root; artifact/checklist path missing/unreadable/not a regular file; artifact UTF-8 decode failure (`not-utf8`). (Invalid `--checklist` *schema* is a config error → `2`; a path/read *refusal* on either file is `4`.) |
| `5` | IO | Stamp write failed (atomic-replace failure). No half-written artifact. |
| `6` | INTEGRITY | Reserved (K4 lock/digest). Review does not emit `6` unless a future flag reuses integrity checks; K5b must not overload `6` for verdicts. |

**Not used by `review --freeze`:** exit `3` (DRIFT) remains a §K4.1 `status --exit-code` code only.
`review --freeze` **never** emits `3`.

**Review-specific exit codes (frozen — additive):**

| Code | Name | Meaning |
| --- | --- | --- |
| `7` | FINDINGS | Verdict `findings` — cited non-escalating findings; no human stop required by config. |
| `8` | BLOCKED | Verdict `blocked`, **or** human escalation required (`mode: human`, fallback-to-human after unreachable provider, or a finding whose category intersects `human_escalation`). |

**Exit-code precedence for `review --freeze` (frozen):**
**`2` (fail-closed) > `4` (refused) > `5` (IO) > `8` (blocked/human) > `7` (findings) > `0` (pass).**
The report payload still lists every condition detected (e.g. both findings and an escalation hit), so
a non-zero exit never hides a second condition.

**Idempotency (frozen):** running `review --freeze` twice on an unchanged artifact with the same
config produces the same verdict, the same finding set (stable ordering — §K5.6), and the same exit
code. A second successful stamp write on an already-stamped `pass` is a no-op that does not rewrite
the stamp timestamp (§K5.7).

**Dry-run (frozen):** `--dry-run` runs the full review and prints the report (including the stamp it
*would* write) but **writes nothing**. This is the inert-first default (`policy/test-tiers.yaml`).

---

## §K5.2 — `overseer review --freeze` argument contract (frozen)

**Purpose:** run the Freeze-Step Reviewer (SPEC §6) on a freeze artifact; emit findings with
**mandatory file+line citations**; set exit status by verdict; escalate to human per config.

**Synopsis:**

```text
overseer review --freeze <path> [options]
```

`<path>` is **required**. It is a repo-relative or absolute path to a single freeze artifact file
(Markdown or YAML). After resolution it **must** lie inside the resolved repo root; `..` traversal or
any escape → exit `4`. Missing/unreadable file → exit `4`.

**Command-specific options:**

| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--freeze <path>` | path | *(required)* | Artifact to review. The flag form is mandatory (`review` without `--freeze` is USAGE → `1`). |
| `--dry-run` | flag | off | Full review report; write nothing (no stamp). |
| `--mode <agent\|human>` | enum | *(from config)* | Override `freeze_contract.reviewer.mode` for this invocation only. |
| `--provider <local\|api>` | enum | *(from config)* | Override `freeze_contract.reviewer.provider` for this invocation only. Ignored when effective mode is `human`. |
| `--model <label>` | string | *(from config)* | Override `freeze_contract.reviewer.model`. Must be a `reviewer_models[].id` from `policy/model-labels.yaml`. Ignored when effective mode is `human`. |
| `--no-stamp` | flag | off | Even on `pass` without `--dry-run`, do not write the review stamp. Report still includes the stamp payload that *would* have been written. |
| `--checklist <path>` | path | *(absent)* | Optional checklist file (repo-confined). **Absent** → use the built-in §K5.5 checklist. **Present** → **replace** the built-in entirely with that file (no union/augment). See checklist file schema below. |

**`--checklist` file schema (frozen — replace semantics):**

```yaml
checks:
  - id: C1                          # required; non-empty string
    title: Ground-truth edge        # required; non-empty string
    typical_severity: MAJOR         # required; BLOCKER | MAJOR | MINOR
  # ... one or more entries; empty `checks` → CONFIG `2`
```

Invalid YAML, missing `checks`, empty `checks`, missing required fields, or unknown `typical_severity`
→ exit `2`. Path escape / missing / unreadable checklist file → exit `4`.

**Disallowed / deferred flags (frozen — K5b must reject as USAGE `1` if present):**
`--write-vcs`, `--commit`, `--push`, `--escalate-force-pass`, any flag that would skip review after
provider failure, any flag that accepts a vendor model slug (e.g. `--model gpt-4o`).

**Conflicting / ignored override rules (frozen):**

| Combination | Result |
| --- | --- |
| `--mode human` together with `--provider` and/or `--model` | **Not a conflict.** Provider/model flags are **ignored**; effective mode is `human` (§K5.2 step 6). |
| `--dry-run` together with `--no-stamp` | **Not a conflict.** Both mean no write; dry-run wins for report `dry_run: true`. |
| Unknown flag, unknown `--mode`/`--provider` enum value, missing `--freeze` | USAGE → `1`. |
| `--freeze` given more than once with different paths | USAGE → `1` (conflicting). |

**Behavior (frozen sequence):**

1. Parse args. Missing `--freeze` / unknown flags / conflicting overrides (table above) → `1`.
2. Resolve repo root + load/validate config (fail closed → `2`). If config missing → `2` with
   "run `overseer init` first".
3. If `freeze_contract.enabled` is `false` → refuse (`4`) with a clear report; do not invoke a
   provider.
4. Resolve `<path>` inside repo root; read artifact bytes as **data**; canonicalize for parse per
   §K5.7 digest rules (UTF-8, strip BOM, LF line endings). Escape/missing/not-utf8 → `4`.
5. If `--checklist` given: resolve path inside repo root; load/validate schema above → `2`/`4` on
   failure. Effective checklist = file contents (replace). Else effective checklist = §K5.5.
6. Resolve effective reviewer settings: CLI overrides > config > defaults (§K5.3). Validate model
   label against `reviewer_models` (§K5.3). Unknown label → `2`.
7. If effective `mode` is `human` → emit the report with human escalation (§K5.8 / §K5.9); exit `8`.
   No provider call.
8. If effective `mode` is `agent` → probe provider reachability (§K5.8).
   - Reachable → run reviewer engine (§K5.5 or replacement checklist) via that provider.
   - Unreachable → apply `fallback` (§K5.3). With `fallback: human` (the only allowed value) → emit
     report with human escalation stating provider failure cause; exit `8`. **Never skip review.
     Never fabricate a `pass`.**
9. Collect findings; enforce citation rule (§K5.6). Any uncited finding is a reviewer-engine error →
   treat as `blocked` with a synthetic finding citing the engine fault (path = artifact, line = `1`
   if no better locus).
10. Derive verdict (§K5.6). Emit human report and/or `--json` payload (§K5.9).
11. If verdict is `pass` and not `--dry-run` and not `--no-stamp` → write stamp (§K5.7). IO failure →
    `5` (artifact unchanged via atomic replace).
12. Exit per verdict / precedence table.

**Writes:** none under `--dry-run` or `--no-stamp` or non-`pass` verdicts. On `pass` (default path):
atomic in-place update of the freeze-block `review_stamp` only (§K5.7).

**VCS:** never commits, never pushes, never touches `main`/canonical.

---

## §K5.3 — Extended `freeze_contract.reviewer` schema (frozen)

### Canonical shape (nested mapping)

```yaml
freeze_contract:
  enabled: true
  reviewer:
    mode: agent              # agent | human — default agent (auto-first)
    model: thinking-high     # id from policy/model-labels.yaml → reviewer_models[] — NEVER a vendor slug
    provider: local          # local | api — local is first-class; offline-capable
    fallback: human          # ONLY allowed value — fail-closed if provider unreachable
  human_escalation:          # unchanged from SPEC §6.3
    - security
    - irreversible
    - real_money
    - gates_tier3
```

### Field rules (frozen)

| Field | Type | Required | Allowed values | Notes |
| --- | --- | --- | --- | --- |
| `enabled` | bool | yes | `true` \| `false` | `false` → CLI refuses review (`4`). |
| `reviewer` | mapping **or** legacy string | yes | see below | Canonical = mapping. |
| `reviewer.mode` | string | yes (when mapping) | `agent` \| `human` | Default when normalizing legacy: the legacy string itself. |
| `reviewer.model` | string | yes when `mode: agent`; optional when `mode: human` | id ∈ `reviewer_models` | **Label only** — never `gpt-*`, `claude-*`, `composer-*`, or other vendor slugs. |
| `reviewer.provider` | string | yes when `mode: agent`; optional when `mode: human` | `local` \| `api` | `local` must work with no API key. |
| `reviewer.fallback` | string | yes when `mode: agent`; optional when `mode: human` | `human` only | No `skip`, no `pass`, no `ignore`. |
| `human_escalation` | list[str] | yes | subset of the four SPEC conditions | Unknown token → `2`. Empty list is allowed (agent never auto-escalates by category; BLOCKER severity still yields `blocked`). |

### Legacy string normalization (frozen — additive, config version stays `1`)

Existing configs use:

```yaml
freeze_contract:
  enabled: true
  reviewer: agent    # or human
  human_escalation: [...]
```

K5b **must** accept this form and normalize it to:

```yaml
reviewer:
  mode: <legacy-string>          # agent | human
  model: thinking-high           # default label when mode=agent
  provider: local                # default — preserves offline/first-class local
  fallback: human
```

When `legacy-string` is `human`, `model`/`provider`/`fallback` are set to the defaults above but
**unused** at runtime (step 6 of §K5.2). Invalid legacy string (not `agent`|`human`) → `2`.

If `reviewer` is a mapping, all required fields for the effective mode must be present; missing →
`2`. Extra unknown keys under `reviewer` → `2` (fail-closed; no silent ignore).

### Guardrails (frozen — non-negotiable, from SPEC §6.2)

1. **Fail-closed:** unreachable provider → `fallback: human` (exit `8`), never skip review.
2. **Model is a label**, never a vendor slug — config stays portable across providers.
3. **`provider: local` is first-class** — full review works offline with no API key.
4. **No core review capability may be `api`-only** — every review feature available via `local` must
   also be available via `api` (and vice versa for the shared finding/verdict/stamp surface). API may
   offer different model backends; it must not gate the capability.

### `reviewer_models` registry (frozen — K5b adds to `policy/model-labels.yaml`)

Phase-model labels (`thinking`, `auto`, `thinking_to_auto`, `operator_plus_auto`) remain for
roadmap/handover **Model:** lines. They are **not** valid as `reviewer.model`.

K5b must add a sibling section:

```yaml
reviewer_models:
  - id: thinking-high
    display: Thinking (high)
    meaning: >
      Extended reasoning for freeze-contract review — interfaces, fail-closed rules,
      security, escalation edges, test-matrix completeness.
    cursor_model_hint: extended thinking / Opus-class / gpt-5.3-codex-class
  - id: auto-default
    display: Auto (default)
    meaning: >
      Faster mechanical review pass against an already-structured freeze checklist.
    cursor_model_hint: default / Composer / Sonnet-class
```

**Validation rule (frozen):** `reviewer.model` must equal some `reviewer_models[].id` in the
**kit-carried** `policy/model-labels.yaml` (the CLI's kit root), not a consumer-edited copy, so a
consumer cannot invent an undeclared label without a kit upgrade. Unknown id → config error `2`.

**Default model (frozen):** `thinking-high` (matches SPEC §6.2 example and the depth expected of a
freeze review).

### Spec §3 example supersession (frozen)

SPEC §3's illustrative `reviewer: agent` string remains a **valid legacy input**. The **canonical
documented form** for new configs and for `overseer init` generators after K5b is the nested mapping
above. K5b updates `cli/config_gen.py` + fixtures to emit the nested form; legacy fixtures keep
passing via normalization.

---

## §K5.4 — Artifact eligibility (frozen)

An artifact is eligible for `review --freeze` when **all** hold:

1. Path resolves to a regular file inside the repo root.
2. File is UTF-8 decodable after the §K5.7 canonicalization (strip BOM; LF line endings for
   parse/digest). Raw decode failure → `4` with cause `not-utf8`.
3. File contains a machine-checkable freeze declaration **or** is explicitly passed as a freeze
   artifact by the operator:
   - **Declared (only form K5b must parse):** a YAML mapping matching the §6.1 schema (`phase`,
     `outputs` with at least one `frozen: true`, optional `frozen_inputs`), appearing either as:
     - the **entire** contents of a `.yaml` / `.yml` artifact, or
     - the **first** fenced `yaml` (or `yml`) code block in a Markdown artifact whose mapping
       parses as §6.1.
   - **Operator-forced:** any other file passed to `--freeze` is still reviewed; the report notes
     `declaration: absent` and applies the cheap heuristic from SPEC §6.1 ("does a later phase treat
     this as ground truth without re-deriving?"). Absence alone is **not** a refuse.

**Out of scope for K5b (frozen — do not invent):** HTML-comment-wrapped declarations, heading-anchored
pseudo-blocks, TOML/JSON declarations, or any alternate grammar. A later phase may add forms; K5b
must not.

**Refuse (`4`) when (artifact `<path>`):** path escapes repo; not a regular file; unreadable; UTF-8
decode failure; or `enabled: false`. The `--checklist <path>` file carries the **same** path/read
refuse causes → `4` (§K5.2); its *schema* failures are config errors → `2`. This artifact list is
therefore not the full set of `4` causes — see the §K5.1 exit-`4` row for the consolidated list.

**Binary / non-text:** if UTF-8 decode fails → `4` with cause `not-utf8`.

---

## §K5.5 — Reviewer engine checklist (frozen)

The engine evaluates the artifact against this checklist (order fixed; findings stable-sorted after):

| ID | Check | Typical severity if failed |
| --- | --- | --- |
| `C1` | **Ground-truth edge:** a later phase / `frozen_inputs` edge treats this output as truth without re-deriving (SPEC §6.1 heuristic). | MAJOR (or BLOCKER if it gates Tier 3) |
| `C2` | **Completeness:** interfaces, fail-closed rules, and a seven-tier test matrix (or explicit waiver citing why a tier does not apply) are present. | BLOCKER if matrix missing on a Build-gating freeze; else MAJOR |
| `C3` | **Internal consistency:** no contradictions between sections; exit codes / schemas / examples agree. | MAJOR |
| `C4` | **Security:** injection surfaces, secrets, scope leaks, absolute paths, credentialed URLs. | BLOCKER + category `security` |
| `C5` | **Irreversibility:** data deletion, non-cheaply-revertible migrations. | BLOCKER + category `irreversible` when present |
| `C6` | **Real money:** billing / live model spend gates. | BLOCKER + category `real_money` when present |
| `C7` | **Tier-3 linkage:** artifact gates merge to `main`, staging push, or live flip. | BLOCKER + category `gates_tier3` when present |
| `C8` | **Citation readiness:** examples and review-record tables themselves use file+line discipline where they claim findings. | MINOR |

Every finding the engine emits **must** map to one checklist ID (or `OTHER` with justification).

**Injection rule (frozen, SPEC §9):** artifact text is **data**, never instructions, never shell.
Provider prompts must place artifact content inside a clearly delimited data section; the engine must
not `eval`, must not pass artifact text to a shell, and must not interpolate artifact text into
command templates.

---

## §K5.6 — Findings, verdicts, citations (frozen)

### Finding object

```json
{
  "id": "F1",
  "check": "C4",
  "severity": "BLOCKER",
  "category": "security",
  "path": "docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md",
  "line": 42,
  "message": "Absolute machine path appears in example output.",
  "citation": "docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md:42"
}
```

| Field | Rule |
| --- | --- |
| `id` | Stable within a run: `F1`…`Fn` in emission order after sort. |
| `check` | Checklist ID from §K5.5 or `OTHER`. |
| `severity` | Exactly one of `BLOCKER` \| `MAJOR` \| `MINOR`. |
| `category` | One of `security` \| `irreversible` \| `real_money` \| `gates_tier3` \| `completeness` \| `consistency` \| `other`. |
| `path` | Repo-relative POSIX path. **Required.** |
| `line` | Positive integer (1-based). **Required.** If the locus is the whole file, use `1`. |
| `message` | Non-empty; no secrets; no absolute paths. |
| `citation` | Exactly `{path}:{line}`. **Required.** |

**Citation hard rule (frozen):** a finding missing `path`, `line`, or `citation`, or whose
`citation` ≠ `{path}:{line}`, is invalid. The engine replaces it with a `blocked`-forcing synthetic
finding as in §K5.2 step 9.

**Stable sort (frozen):** findings sorted by `(path asc, line asc, severity desc, check asc, message
asc)` before `id` assignment, so identical inputs yield identical ids/order.

### Verdict derivation (frozen)

| Condition | Verdict |
| --- | --- |
| Zero findings | `pass` |
| ≥1 finding whose `category` ∈ configured `human_escalation` | `blocked` |
| ≥1 finding with `severity: BLOCKER` (even if category not in escalation list) | `blocked` |
| Else (≥1 MAJOR/MINOR, none escalating) | `findings` |

`mode: human` or fallback-to-human **short-circuits** to exit `8` with verdict `blocked` and
`escalation: human` before checklist findings are required (the §K5.9 report may still include
pre-parse notes as `findings`).

### Mapping verdict → exit (frozen)

| Verdict | Exit | Stamp? |
| --- | --- | --- |
| `pass` | `0` | Yes (unless `--dry-run` / `--no-stamp`) |
| `findings` | `7` | No |
| `blocked` | `8` | No |

---

## §K5.7 — Review stamp (frozen)

### Locus (pinned — aligns with SPEC §6.2 "freeze block")

On `pass` (and only then), the CLI writes a machine stamp as a top-level YAML key `review_stamp`
**inside the artifact's freeze block**. The freeze block is:

| Artifact kind | Freeze block |
| --- | --- |
| Markdown with a §6.1 fenced YAML declaration | That **first** matching fenced `yaml`/`yml` block |
| YAML/YML whose whole file is a §6.1 mapping | The whole file |
| Operator-forced (no §6.1 declaration) | A **new** trailing region created on first stamp (see serialization below) |

The narrative markdown **Review record** table (Round / Reviewer / Verdict / Resolution) is
**human/agent-maintained only**. The CLI **never** edits that table.

### Stamp fields (frozen)

```yaml
review_stamp:
  reviewed_at: "2026-07-10T00:00:00Z"   # ISO-8601Z; timestamp only — no identity
  verdict: pass
  reviewer_mode: agent                  # effective mode
  reviewer_model: thinking-high         # label, or null when mode=human
  reviewer_provider: local              # local | api | null when mode=human
  kit_version: "0.1.0"                  # from kit VERSION
  artifact_digest: "sha256:<64-hex>"    # sha256 of canonical pre-stamp bytes (§ below)
```

### On-disk serialization (frozen)

**Markdown, declaration present:** parse the first §6.1 fenced YAML block; set/replace the
top-level key `review_stamp` with the stamp mapping; serialize that mapping back into the **same**
fence (fence language tag unchanged). Do not modify text outside that fence except as required to
replace the fence body. Key order inside the freeze mapping: preserve existing keys' relative order;
place `review_stamp` after `frozen_inputs` if present, else after `outputs`, else last.

**YAML/YML, whole-file declaration:** set/replace top-level `review_stamp` in the document; write
the whole file atomically. Same key-order rule.

**Operator-forced (no declaration) — Markdown:** if no `<!-- overseer:review-stamp -->` marker
exists, append a blank line, then the HTML comment `<!-- overseer:review-stamp -->`, then a fenced
`yaml` block whose sole top-level key is `review_stamp` with the stamp fields above. If the marker
already exists, replace only the fenced YAML block that immediately follows it.

**Operator-forced (no declaration) — YAML/YML:** set/replace top-level `review_stamp` only (do not
invent a fake `phase`/`outputs` declaration).

### Canonical bytes for `artifact_digest` (frozen)

`artifact_digest` is `sha256:` over the artifact's **pre-stamp canonical form** — a deterministic
byte reduction that is **identical whether the artifact has never been stamped or already carries a
`review_stamp`**, so the first stamp and every re-run produce the same digest. (The earlier "raw
pre-stamp bytes" wording was ambiguous for interleaved stamps; this form is the frozen definition.)

**Pre-stamp canonical form (frozen — derived on every run, first or subsequent):**

1. Read the raw file bytes.
2. Apply `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` §K4.7 **Canonical byte rules** items **1 and 2**
   (not the aggregate algorithm's numbered steps):
   - **Encoding:** UTF-8; if a UTF-8 BOM (`EF BB BF`) is present, strip it before hashing **and**
     before parse (same bytes for both).
   - **Line endings:** replace every `\r\n` and every lone `\r` with `\n`; no trailing-whitespace
     stripping; no addition or removal of a final newline.
3. **Excise any existing stamp and re-serialize with the same serializer used to write it**, so a
   hand-authored artifact and an already-stamped artifact reduce to identical bytes:
   - **Declared Markdown fence:** parse the first §6.1 fenced YAML block; delete the top-level
     `review_stamp` key if present; re-serialize that block with the frozen deterministic serializer
     (see below) back into the fence. All bytes **outside** the fence are preserved verbatim.
   - **Whole-file YAML/YML:** parse the document; delete top-level `review_stamp` if present;
     re-serialize the whole document with the same deterministic serializer.
   - **Operator-forced Markdown:** remove the trailing region the stamp writer appends — the blank
     separator line, the `<!-- overseer:review-stamp -->` marker, and the fenced YAML block that
     immediately follows it — leaving the prior bytes **verbatim** (no prose re-serialization). If no
     marker is present the bytes are already the pre-stamp form.
   - **Operator-forced YAML/YML:** parse; delete top-level `review_stamp` if present; re-serialize
     with the same deterministic serializer.

Then: `artifact_digest = "sha256:" + sha256(pre_stamp_canonical_form).hexdigest()` (lowercase hex).

**Deterministic serializer (frozen requirement):** the YAML serializer K5b uses for stamping MUST be
round-trip stable — `serialize(parse(x)) == serialize(parse(serialize(parse(x))))` — and MUST be the
**same** serializer used both to (a) write/replace `review_stamp` (§ On-disk serialization above) and
(b) produce the pre-stamp canonical form here. This is what makes the digest reproducible across runs
regardless of hand-authored YAML style. Parse (eligibility §K5.4), stamp write, and digest **must**
all share the §K4.7 items 1–2 canonicalization so a BOM-only or CRLF-only difference never forks
behavior.

### Other rules (frozen)

- No username, host, email, token, or absolute path in the stamp.
- **Atomic write:** temp file in the same directory + `os.replace()`. Failure → exit `5`, original
  bytes preserved.
- **Idempotent stamp:** on a `pass` re-run, recompute the **pre-stamp canonical form** (above) of the
  on-disk artifact and its `artifact_digest`. If an existing `review_stamp` already records
  `verdict: pass` **and** that recomputed `artifact_digest` equals the stored one, the stamp is
  unchanged: do **not** rewrite `reviewed_at` and perform **no file write**. Because the pre-stamp
  form excises the existing stamp before hashing, the digest is stable across repeated stamped runs.
- Stamp write updates only the freeze-block / stamp-marker region defined above; it must not reorder
  unrelated prose sections.

---

## §K5.8 — Provider reachability, local/api, human escalation (frozen)

### Provider interface (language-neutral; K5b implements in `tools/freeze_reviewer/`)

| Method | Input | Output | Fail-closed |
| --- | --- | --- | --- |
| `reachable()` | none | `bool` + optional `cause` | Errors → unreachable (not a crash of the CLI). |
| `review(artifact, checklist, config)` | artifact text + checklist + effective reviewer settings | list of findings (pre-validation) | Provider exception → treat as unreachable → fallback. |

**`local`:** invokes a local model runner available on the operator machine (no cloud API key
required). Exact runner wiring is K5b implementation detail but **must** be injectable in tests via a
fake provider (no real model calls in CI).

**`api`:** invokes a remote API. Credentials come from the **environment / secret store**, never from
`.overseer/config.yaml`. Missing credentials → unreachable.

**Reachability probe (frozen):** `reachable()` runs before `review()`. It must not send artifact
content. It must not log secrets.

### Human escalation (frozen — same report schema as §K5.9)

When mode is `human` or fallback fires, the CLI emits the **§K5.9 report object** with these field
values (not a separate packet schema):

| Field | Value |
| --- | --- |
| `verdict` | `blocked` |
| `exit_code` | `8` |
| `escalation` | `"human"` |
| `reason` | `"mode_human"` or `"provider_unreachable"` |
| `provider_cause` | optional cause string (no secrets), or `null` |
| `checklist` | list of effective checklist ids (built-in or `--checklist`) |
| `instructions` | `"Perform Freeze-Step Review per SPEC §6; cite file+line for every finding; record verdict in the artifact review record."` |
| `findings` | `[]` unless pre-parse notes produced synthetic findings |
| `stamp` | `null` |

**Stdout rules (frozen):**

- **With `--json`:** print exactly that one §K5.9 JSON object (including the escalation fields above).
- **Without `--json`:** print the §K5.9 **human** rendering, including `Escalation:`, `Reason:`, and
  `Instructions:` lines (see §K5.9 human example for escalation).

Exit `8`. No stamp. No provider `review()` call after fallback is chosen.

---

## §K5.9 — Report payload (frozen)

One schema for all outcomes. Human escalation (§K5.8) fills the optional escalation fields; agent
reviews leave them null/absent as specified.

### Human (stdout, when `--json` is off)

Agent review example:

```
Freeze review: docs/FOO.md
Verdict: findings
Findings (2):
  F1 MAJOR completeness docs/FOO.md:120  Missing seven-tier matrix section.
  F2 MINOR consistency docs/FOO.md:88   Exit code 7 mentioned in prose but not in table.
Escalation: none
Stamp: (not written — verdict != pass)
```

Human-escalation example (`mode: human` or provider fallback):

```
Freeze review: docs/FOO.md
Verdict: blocked
Findings (0):
Escalation: human
Reason: mode_human
Provider cause: (none)
Checklist: C1, C2, C3, C4, C5, C6, C7, C8
Instructions: Perform Freeze-Step Review per SPEC §6; cite file+line for every finding; record verdict in the artifact review record.
Stamp: (not written — verdict != pass)
```

### JSON (`--json`)

```json
{
  "command": "review",
  "freeze": "docs/FOO.md",
  "verdict": "findings",
  "exit_code": 7,
  "escalation": null,
  "reason": null,
  "provider_cause": null,
  "checklist": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
  "instructions": null,
  "enabled": true,
  "declaration": "present",
  "reviewer": {
    "mode": "agent",
    "model": "thinking-high",
    "provider": "local",
    "fallback": "human"
  },
  "findings": [ /* Finding objects §K5.6 */ ],
  "stamp": null,
  "dry_run": false
}
```

| Field | Rule |
| --- | --- |
| `escalation` | `null` on agent path; `"human"` on human/fallback path. |
| `reason` | `null` unless escalation; then `mode_human` \| `provider_unreachable`. |
| `provider_cause` | `null` or non-secret cause string when `reason` is `provider_unreachable`. |
| `checklist` | Always the effective checklist id list. |
| `instructions` | Non-null string only when `escalation` is `"human"`; else `null`. |
| `declaration` | `"present"` \| `"absent"` (§K5.4). |
| `stamp` | On `pass` with stamp written: the `review_stamp` object (§K5.7). On `--dry-run` pass: the would-be stamp and `dry_run: true`. Otherwise `null`. |

---

## §K5.10 — Automation routing (frozen contract; templates only in K5b)

SPEC §10 blocker: Cursor Automation availability differs per environment. Frozen degrade path:

| Trigger intent | Preferred | Degrade |
| --- | --- | --- |
| Session-end freeze check | Cursor Automation template invoking `overseer review --freeze <path> --dry-run` | Operator runs CLI or `/freeze-review` skill manually |
| On-merge / pre-Auto-build gate | Automation or CI step running `overseer review --freeze <path>` (non-dry-run on the feature branch) | Same CLI; **no** silent skip |

**K5b ships:** Automation **template files** under `cursor/` (or `templates/` as appropriate for
vendoring) plus documentation in `tools/freeze_reviewer/README.md`. **K5b does not** auto-enable live
Automations in the operator's editor (Tier-2/3 human action).

**Hard rule:** when Automations are unavailable, the kit still provides full review capability via
the CLI. Unavailability is never treated as `pass`.

---

## §K5.11 — Security / privacy gate (frozen, inherits SPEC §9 + §K4.9)

- No secrets/tokens/credentialed URLs/absolute paths in config, stamps, findings, or logs.
- No vendor slugs in config; no hardcoded SHAs in engine logic (digests computed at runtime).
- Artifact text = data only; injection-safe prompt fencing; no shell interpolation of artifact text.
- Path args confined to repo root (`..` → `4`).
- Least privilege: only `adapter.status()` among VCS methods; no VCS writes; `muse-only` consumers
  get full review (review is VCS-write-free).
- API credentials never enter `.overseer/config.yaml`.
- Fail-closed on every config/provider failure path; never fabricate `pass`.
- `--dry-run` is the safe CI default.

---

## §K5.12 — Seven-tier test matrix for K5b (frozen)

Per RULE #0 and SPEC §10. All under `tests/` (pytest). Provider calls are **faked** via an injectable
test double — no real local-model or API calls, no network, no `main` merge, no real consumer repos.
All seven tiers must be green locally before K5b is DONE.

| Tier | Module(s) (new under `tests/`) | Cases that must pass |
| --- | --- | --- |
| **unit** | `tests/unit/test_review_argparse.py`, `test_reviewer_config.py`, `test_findings_verdict.py`, `test_review_stamp.py`, `test_provider_fallback.py` | Arg parsing: missing `--freeze` → `1`; unknown flag → `1`; `--help` → `0`; `--mode human` + `--provider`/`--model` ignored (not USAGE). Config: nested mapping parse; legacy string `reviewer: agent\|human` normalizes to defaults; unknown model label → `2`; unknown `provider`/`fallback`/`mode` → `2`; unknown `human_escalation` token → `2`; extra reviewer keys → `2`. Checklist: absent → §K5.5 ids; `--checklist` valid file **replaces** built-in (assert built-in ids absent from effective list); empty/invalid checklist → `2`; checklist path escape → `4`. Verdict: zero findings → `pass`/`0`; MAJOR only → `findings`/`7`; BLOCKER → `blocked`/`8`; category ∈ escalation → `blocked`/`8` even if MAJOR. Citation: missing path/line rejected → synthetic blocked finding. Stamp: Markdown fence gets `review_stamp` key; YAML whole-file gets top-level `review_stamp`; operator-forced Markdown uses `<!-- overseer:review-stamp -->` marker; narrative Review-record table bytes unchanged; idempotent same-digest no-op; atomic failure → `5` with original bytes; digest matches §K4.7 Canonical byte rules 1–2 (BOM strip + LF). Provider: unreachable + `fallback: human` → §K5.9 report with `escalation: human` + `8`; never `pass`. Exit precedence `2>4>5>8>7>0`; never emits `3`. |
| **integration** | `tests/integration/test_cli_review_freeze.py` | For **each** regime fixture (`git-only`, `muse-only`, `muse+git-mirror`): fixture artifact with declared `frozen: true` → fake provider returns controlled findings → CLI exit/JSON match contract; `enabled: false` → `4`; path escape → `4`; legacy config string still reviews; `--dry-run` writes zero bytes; `--mode human` skips provider (assert fake not called) and exits `8` with unified §K5.9 JSON (`escalation`, `reason`, `checklist`, `instructions`). CLI↔config↔reviewer compose through frozen interfaces. |
| **e2e** | `tests/e2e/test_freeze_review_cycle.py` | Full lifecycle on a fixture repo: seed a freeze artifact → `review --freeze --dry-run` reports would-be stamp → `review --freeze` with fake `pass` writes stamp → second run idempotent → edit artifact → review yields `findings` or `blocked` per injected provider → confirm no VCS commit occurred. |
| **stress** | `tests/stress/test_large_freeze_artifact.py` | Very large artifact (many sections, many synthetic freeze edges) + many findings from fake provider; sort/id assignment stable; memory bounded; runtime completes without unbounded scans. |
| **data-integrity** | `tests/data_integrity/test_review_idempotency.py`, `test_stamp_atomic.py` | Run-twice identical inputs → identical JSON (except allowed timestamp stability on idempotent stamp); stamp digest matches independently computed reference. **Re-stamp digest stability (§K5.7 pre-stamp canonical form):** for each stamp locus — declared-Markdown fence, whole-file YAML (both *interleaved*), and operator-forced appended-marker Markdown — a first stamp then a second `pass` run recompute the **same** `artifact_digest` and perform **no** second write (assert byte-identical file after run 2, `reviewed_at` unchanged); a hand-authored artifact whose freeze block differs only in YAML whitespace/quoting yields the same pre-stamp digest as its re-serialized form (deterministic serializer round-trip). Simulated `OSError` mid-stamp leaves original artifact bytes unchanged; dry-run / `--no-stamp` write zero bytes. |
| **performance** | `tests/performance/test_review_bounded.py` | Review on a realistic-size fixture with fake provider completes within a bounded wall-clock budget; assert provider `review()` called at most once per invocation; `reachable()` called at most once. |
| **security** | `tests/security/test_review_injection.py`, `test_review_no_secret_leak.py`, `test_review_least_privilege.py` | Artifact containing shell metacharacters / instruction-like text cannot cause shell execution (assert no shell runner invoked); findings/stamp/stdout/stderr contain no absolute paths, tokens, or identity; `--repo`/`--freeze`/`--checklist` traversal cannot read/write outside repo root (`4`); config rejects vendor slug models; API-key-like env values never appear in output; `RecordingRunner` shows no VCS write verbs; unreachable API without key → human fallback `8`, never silent pass; `muse-only` fixture never invokes git. |

**Definition of Done for K5b (frozen):** `overseer review --freeze` behaves exactly per §K5.1–§K5.11;
config schema + legacy normalization live; `reviewer_models` registry present; Automation templates
shipped with documented degrade path; all seven tiers above green locally; no secrets/hardcoded SHAs;
both governance docs updated together; feature-branch → commit → PR under the kit's own `git-only`
rules; **no `main` merge without review** (this contract is the reviewed freeze that gates K5b).

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §6 (Freeze-Contract review policy), §6.2 (automated review + reviewer
  config requirement), §9 (security), §10 (seven-tier + dry-run), §11 (K5 phase) — the frozen parent
  spec this refines.
- `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` — global CLI conventions, exit taxonomy `0–6`, output
  discipline reused here.
- `policy/model-labels.yaml` — phase labels today; K5b adds `reviewer_models` per §K5.3.
- `policy/test-tiers.yaml` — RULE #0 tier contract; lists `review --freeze --dry-run` as inert default.
- `cursor/skills/freeze-review/SKILL.md` — operator-facing checklist aligned with §K5.5.
- `tools/freeze_reviewer/README.md` — placeholder today; K5b replaces with engine docs.
- `adapters/config.py` — K5b extends `FreezeContractConfig` for the nested reviewer mapping.
