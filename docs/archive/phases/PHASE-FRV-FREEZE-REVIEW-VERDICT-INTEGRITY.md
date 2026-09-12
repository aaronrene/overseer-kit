# Phase FRV — Freeze-review verdict integrity (Thinking freeze)

Status: **Reviewed → `pass` (FRV-r5).** FRV-a is **spec-only**; no code, no test file,
no CLI edit lands in this phase. FRV-b (Auto) is cleared to build mechanically
against this contract as **one** build.

```yaml
phase: FRV
outputs:
- id: frv-freeze-review-verdict-integrity
  path: docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md
  frozen: true
frozen_inputs:
- id: kit-spec
  path: docs/OVERSEER-KIT-SPEC.md
- id: k5-freeze-reviewer
  path: docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
- id: isr-independent-second-reviewer
  path: docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md
- id: gs-paste-ready-regen
  path: docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md
- id: k9a-honesty
  path: docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md
- id: p-evidence
  path: docs/archive/phases/PHASE-TRACK-P-P-EVIDENCE.md
- id: check-ok-paste
  path: docs/CHECK-OK.md
- id: freeze-reviewer-stamp
  path: tools/freeze_reviewer/stamp.py
- id: freeze-reviewer-types
  path: tools/freeze_reviewer/types.py
- id: freeze-reviewer-artifact
  path: tools/freeze_reviewer/artifact.py
- id: freeze-reviewer-serializer
  path: tools/freeze_reviewer/serializer.py
- id: freeze-reviewer-engine
  path: tools/freeze_reviewer/engine.py
- id: freeze-reviewer-report
  path: tools/freeze_reviewer/report.py
- id: freeze-reviewer-findings
  path: tools/freeze_reviewer/findings.py
- id: freeze-reviewer-providers
  path: tools/freeze_reviewer/providers/base.py
- id: freeze-reviewer-checklist
  path: tools/freeze_reviewer/checklist.py
- id: review-command
  path: cli/commands/review.py
- id: check-ok-command
  path: cli/commands/check_ok.py
- id: next-regen
  path: tools/governance_hygiene/next_regen.py
- id: governance-gates-scan
  path: tools/governance_gates/scan.py
- id: honesty-types
  path: tools/honesty/types.py
- id: honesty-validate
  path: tools/honesty/validate.py
- id: honesty-ledger
  path: tools/honesty/ledger.py
- id: honesty-ledger-io
  path: tools/honesty/ledger_io.py
- id: app-engine
  path: tools/app/engine.py
- id: config-parse
  path: adapters/config.py
- id: test-tiers
  path: policy/test-tiers.yaml
- id: model-labels
  path: policy/model-labels.yaml
- id: kit-boundary
  path: AGENTS.md
review_stamp:
  reviewed_at: '2026-09-12T11:31:24Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:c113efa33a12b892d55f9c055dd029830ed36ef48f42384bc8bff071edbb5b86
```

**Downstream edge:** FRV-b treats this document as ground truth without re-deriving
it (SPEC §6 mandatory reviewed freeze). Every problem claim in §FRV.1 was verified by
source inspection before this freeze was written and carries a `path:line` citation;
FRV-b must not re-derive or relitigate them.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line**.
Uncited findings are invalid and are discarded. Fixes are Tier 1 on the feature
branch. Merge to `main` is Tier 3 and is never part of this loop.

**Authority note specific to this phase.** FRV-a is repairing the very gate that
normally certifies a freeze. The `ok review --freeze` stamp on this document is
therefore treated as the **mechanical** check only — it proves the artifact parses,
declares `frozen: true`, carries a seven-tier matrix, has no absolute machine path
and no secret-shaped assignment. The **authoritative** verdict for FRV-a is the
thinking-model review rounds recorded in the table below. This is exactly the
distinction §FRV.3 makes permanent.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| FRV-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R1-M1** §FRV.6 emission put `mechanical_only` in `NextRegenDecision.reason`, which `next_regen.py:556-557` treats as ambiguity and which `next_regen.py:713-717` renders as `human_authorship_required` — a mechanical-only freeze would have **suppressed** NEXT regeneration entirely instead of emitting Thinking. Frozen to a separate additive `advisory` field. **R1-M2** the reader inventory named only `_freeze_pass_state`; `tools/governance_gates/scan.py:133` is a second consumer of the stamp verdict and `:236-241` is a **second** prose fallback with different regexes. Both added to §FRV.3.4 / §FRV.7. **R1-N1** `decide_split_emission` had no `config` parameter so no ledger path was reachable; frozen signature change + named test call sites. |
| FRV-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** `produced_by` was derivable only *inside* `LocalReviewProvider.review`, but the engine needs it *after* the call; frozen `producer_identity()` ordering + absent-method fail-closed value. **R2-M2** §FRV.9 did not say what happens to a doc whose slice is re-opened after archival; frozen digest-rebind rule. **R2-N1** illustrative YAML fences would have been picked up by this document's own `_freeze_pass_state` / `FENCE_RE` scan; all illustrative blocks moved to `text` fences. |
| FRV-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R3-M1** the frozen stamp was described as thirteen keys while §FRV.3.2 listed **fourteen** — an off-by-one in the normative count that FRV-b would have had to guess at, in five places incl. two seven-tier rows. **R3-M2** the two readers derive phase identity by **different** functions, so the gate scan and the emission path would have queried the ledger under different `phase_id` values and asserted opposite things about one slice; frozen §FRV.6.4.1. **R3-M3** exit `39` was specified without its `--dry-run` / `--no-stamp` interaction, leaving a write-refusal code reachable when no write was attempted. **R3-N1** `auto_may_start` had no defined reading for the `operator_forced_md` kind, where `freeze_mapping` is `None`. **R3-N2** the CLI's handling of a forged `gate: substantive` was defined for readers but not for the writer. |
| FRV-r4 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R4-M1 (BLOCKER-class reachability)** F4 was wired only to the `Thinking → Auto` label, which `tools/governance_hygiene/next_regen.py:509-510` makes the sole path reaching the freeze detector. Parsed live: **4** of **103** roadmap rows carry that label (all long DONE) against **43** plain `Auto` rows, because every phase since GS-PASTE uses the two-row `{id}-a` Thinking + `{id}-b` Auto convention. The authorization gate would have been **dead code in this repo and in every consumer copying its convention** — F4's central claim unenforceable. Frozen §FRV.6.5.1 extends the gate to plain `Auto` via the existing §GSP.4.3 ambiguity channel, excludes `Operator + Auto`, and pins the `phase_id` asymmetry (`{id}-b` authorizes; `{id}-a` authored). |
| FRV-r5 | Freeze-review loop (CLI checklist + thinking, `thinking-high`) | **pass** | R1–R4 confirmed RESOLVED; every changed count, reason name, and citation re-verified against source. Root cause held: no verdict record lives inside the artifact it judges, and authorization is a digest-bound entry on the existing hash chain with no parallel mechanism. Reachability re-derived after R4-M1: the gate now covers both labels that hand work to a model and no label that does not. Additive-only invariants re-checked against `tools/honesty/types.py:24-37` (entry-kind enum), `tools/honesty/status.py:26` (highest existing code `38`), `tools/freeze_reviewer/serializer.py:10-31` (key-order contract), `tools/freeze_reviewer/engine.py:133-147` (exit precedence), `tools/governance_hygiene/next_regen.py:27-33` (reason vocabulary). Seven-tier §FRV.12 complete. Stamp written by `ok review --freeze` as the mechanical check only. |

### Freeze-review findings ledger (FRV-r1 … FRV-r4)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | completeness | `tools/governance_hygiene/next_regen.py:556` | Any non-`None` reason returned by `decide_split_emission` short-circuits `plan_next_regen` to ambiguity, so `mechanical_only` carried in `reason` would have blocked NEXT regeneration instead of emitting Thinking. Frozen to an additive `advisory` field (§FRV.6.6). |
| R1-M2 | MAJOR | completeness | `tools/governance_gates/scan.py:133` | Second reader of the stamp verdict (suppresses the freeze-review pending gate) was unenumerated; `:236-241` `_narrative_freeze_pass` is a second, differently-worded prose fallback. Both now in scope (§FRV.3.4, §FRV.7.2). |
| R1-N1 | MINOR | completeness | `tools/governance_hygiene/next_regen.py:499-502` | `decide_split_emission(row, repo_root)` has no config parameter, so the configured ledger path was unreachable from the emission decision. Frozen signature + the two positional test call sites that must be updated (§FRV.6.5). |
| R2-M1 | MAJOR | consistency | `tools/freeze_reviewer/providers/base.py:154-155` | The scripted-vs-engine branch is decided inside `review()`, so `produced_by` cannot be read before the call. Frozen call ordering and the fail-closed value when a provider double lacks the method (§FRV.4.2). |
| R2-M2 | MAJOR | completeness | `tools/governance_hygiene/next_regen.py:522` | Freeze state is consulted only for rows in `OPEN_STATUSES`, so archived DONE rows are unreachable — but the re-open path was unspecified. Frozen digest-rebind requirement (§FRV.9.4). |
| R2-N1 | MINOR | consistency | `tools/governance_hygiene/next_regen.py:403` | `_freeze_pass_state` scans **every** `yaml`/`yml` fence in the document, and `tools/freeze_reviewer/artifact.py:17-19` `FENCE_RE` matches the first one; illustrative stamp examples in this artifact would have been parsed as real declarations. All illustrative blocks are `text` fences (§FRV.2.3). |
| R3-M1 | MAJOR | consistency | `:300` (pre-fix) | The normative stamp was called "thirteen keys" while the §FRV.3.2 listing enumerated fourteen. Corrected in all five occurrences, including the unit and data-integrity rows of §FRV.12 which assert the count. |
| R3-M2 | MAJOR | consistency | `tools/governance_gates/scan.py:121` | `_scan_freeze_review` iterates `_normalize_phase_id` display strings (`:86-98`) while `decide_split_emission` uses `compact_step_id` (`tools/governance_hygiene/next_regen.py:512`). Both would have queried the ledger under different `phase_id` values, so one appended entry could clear the reminder without authorizing the build, or the reverse. Frozen to a single derivation in §FRV.6.4.1. |
| R3-M3 | MAJOR | completeness | `tools/freeze_reviewer/engine.py:121-128` | Exit `39` ("a write was refused") was specified without its `--dry-run` / `--no-stamp` interaction, making it reachable on a run that attempts no write. Frozen locus + all four flag combinations in §FRV.5.2. |
| R3-N1 | MINOR | completeness | `tools/freeze_reviewer/artifact.py:86` | `parse_artifact` returns `freeze_mapping = None` for the `operator_forced_md` kind, so `auto_may_start` had no defined reading there. Frozen: absent, no block; a block requires a §6.1 declaration (§FRV.3.4). |
| R3-N2 | MINOR | completeness | `:341` (pre-fix) | A forged `gate: substantive` had reader semantics (refuse) but no writer semantics. Frozen: the writer normalizes it back to `mechanical`, and it does not trigger the §FRV.5.2 refusal (§FRV.3.4). |
| R4-M1 | BLOCKER | completeness | `tools/governance_hygiene/next_regen.py:509-510` | Non-split model labels return the queue model before the freeze detector is ever reached, so F4 as first frozen was reachable only from the `Thinking → Auto` label — **4** of **103** live roadmap rows, all DONE, against **43** plain `Auto` rows. The gate would have been unenforceable in the kit's own repo. Frozen §FRV.6.5.1. Severity is BLOCKER because the finding nullifies the phase's central guarantee rather than degrading it. |

**Citation discipline:** every review finding in this artifact **must** include
`path:line` so the operator can verify — never trust uncited review output
(§6.2 / K5).

---

## §FRV.0 — Simple summary

Right now the kit's "freeze review" writes its own report card into the same
document it is grading, using the same word a real review would use. The default
reviewer is not a reviewer at all — it is a short list of word searches. If a
document contains four magic phrases and no machine paths, it gets stamped
**pass**, and that stamp names a thinking model that never ran. Worse, if a human
opens the document and downgrades the verdict by hand to record an objection, the
next run silently erases the objection and re-stamps **pass**. And that same field
is what tells the kit it may hand the work to a mechanical build session.

FRV fixes the shape of the problem, not just the symptom: **a verdict record must
not live inside the document it judges.** The kit already solved this once. The
independent-second-reviewer phase put verdicts in a hash-chained ledger outside
the document. FRV reuses that machinery. The document keeps a clearly-labelled
*mechanical* result that can never authorize a build; authorization comes from a
ledger entry bound to the exact bytes of the artifact.

**Technical summary.** Separate the vocabulary (`mechanical_verdict` + a required
`gate` discriminator; `verdict` reserved for a substantive record the CLI never
writes). Make the stamp self-describing (`produced_by`, `provider_kind`,
`checklist_ids`, `findings_count`) and stop asserting `reviewer_model` when a rule
engine produced the result. Invert the write polarity: merge unknown keys instead
of replacing the mapping, and refuse to escalate an existing non-pass record
without an explicit flag. Add one additive hash-chained ledger kind
`freeze_review`, matched on `phase_id` + `frozen_spec` + `artifact_digest`, as the
only thing that may emit `Auto` — for the plain `Auto` label as well as the split
one, without which the gate would be dead code under this repo's own two-row
roadmap convention. Delete both prose fallbacks. Honor an explicit
`auto_may_start: false` operator block. Freeze the reconciliation for the 36
archived phase documents that today authorize on a mechanical stamp or on bold
prose.

---

## §FRV.1 — Verified problem (do not redesign, do not re-derive)

Every row was confirmed by reading the named source before this freeze was
written. FRV-b treats these as ground truth.

### §FRV.1.1 — The gate is a word search, and it signs a model's name

| ID | Finding | Citation |
| --- | --- | --- |
| P1 | `ok check-ok` is **not** a separate gate. It scaffolds (or reuses) an artifact and then calls the identical engine as `ok review --freeze`, constructing a `review` Namespace and delegating. | `cli/commands/check_ok.py:82-93` |
| P2 | The default provider is a rule engine, not a review. `provider_for` returns `LocalReviewProvider` unless `provider == "api"`. | `tools/freeze_reviewer/providers/base.py:208-219` |
| P3 | That engine tests only for the presence of four regex families and one literal substring: `GROUND_TRUTH_RE` (C1), `TIER_MATRIX_RE` (C2), `ABSOLUTE_PATH_RE` / `SECRET_RE` (C4), and `"file+line"` lowercased (C8). C3 and C5–C7 emit no finding at all. | `tools/freeze_reviewer/providers/base.py:15-19`, `:51-125` |
| P4 | `LocalReviewProvider.review` accepts a `reviewer` argument and never reads it. No model is consulted, no network call is made. | `tools/freeze_reviewer/providers/base.py:145-160` |
| P5 | Zero findings is the only way to reach `pass`, so satisfying those four checks **is** a pass. | `tools/freeze_reviewer/findings.py:60-67` |

### §FRV.1.2 — The record lives inside the artifact, in borrowed words

| ID | Finding | Citation |
| --- | --- | --- |
| P6 | The verdict written into the artifact is the string literal `"pass"`, hardcoded in the stamp builder. It is not derived from the review; it is the constant that the `pass` branch writes. | `tools/freeze_reviewer/stamp.py:33-42` |
| P7 | It is written as the key `verdict` — the same field name and the same closed vocabulary (`pass` / `findings` / `blocked`) a substantive design review uses. | `tools/freeze_reviewer/types.py:18`, `:82-91` |
| P8 | The stamp carries **no** gate provenance. `ReviewStamp.to_mapping` emits exactly seven keys: `reviewed_at`, `verdict`, `reviewer_mode`, `reviewer_model`, `reviewer_provider`, `kit_version`, `artifact_digest`. There is no `gate`, no originating command, no checklist ids, no findings count. A mechanical stamp and a substantive one are byte-identical in shape. | `tools/freeze_reviewer/types.py:82-91` |
| P9 | The stamp asserts `reviewer_model` from effective config even when the rule engine produced the result, so the document claims a model that had no causal role. Confirmed live across the whole archive: **all 31** stamped phase documents read `reviewer_model: thinking-high`, `reviewer_provider: local` (§FRV.9.1). | `tools/freeze_reviewer/stamp.py:38`, `tools/freeze_reviewer/engine.py:42-53`, `adapters/config.py:507-518` |

### §FRV.1.3 — Polarity is inverted: sticky on pass, self-healing back to pass

| ID | Finding | Citation |
| --- | --- | --- |
| P10 | `pre_stamp_canonical_bytes` removes `review_stamp` from the mapping before hashing, in every artifact kind. Therefore **no edit inside `review_stamp` can ever change `artifact_digest`.** | `tools/freeze_reviewer/artifact.py:119-147` |
| P11 | The no-op guard requires the **existing** verdict to already be `pass`. A human downgrade fails the guard, so the write is not suppressed. | `tools/freeze_reviewer/stamp.py:45-52` |
| P12 | The write is a wholesale replacement of the `review_stamp` mapping, not a merge. Any key a human or operator added inside it is discarded, and the replacement carries the hardcoded `pass` from P6. Net effect: a downgrade recorded in `review_stamp` is erased and restamped `pass`; an existing `pass` is sticky and untouched. | `tools/freeze_reviewer/stamp.py:55-58`, `:61-88`, `:91-101` |

### §FRV.1.4 — The field is load-bearing, and the fallbacks are wider than the field

| ID | Finding | Citation |
| --- | --- | --- |
| P13 | `decide_split_emission` reads freeze state and returns `"Auto"` on pass, i.e. a rule-engine result authorizes a mechanical build session. | `tools/governance_hygiene/next_regen.py:517-524` |
| P14 | `_freeze_pass_state` reads `review_stamp.verdict` out of any `yaml`/`yml` fence in the document. | `tools/governance_hygiene/next_regen.py:395-413` |
| P15 | With no `review_stamp`, `_freeze_pass_state` falls back to scanning **whole-document text**: a bare `verdict` / `pass` pairing, or a bold `**pass**`, or `reviewed → pass`, authorizes Auto. Every phase document in this repo carries a review-record table with bold `pass` cells, so this fallback is routinely reachable — confirmed live on **5** archived documents that authorize on prose alone (§FRV.9.1). | `tools/governance_hygiene/next_regen.py:415-436` |
| P16 | Keys placed **outside** `review_stamp` survive re-runs (they are preserved by `dict(mapping)` in `_insert_review_stamp` and by the serializer's order-preserving pass) but the kit never reads any of them. `auto_may_start` appears **zero** times in the entire tree, so an operator block written there is invisible. | `tools/freeze_reviewer/stamp.py:55-58`, `tools/freeze_reviewer/serializer.py:10-31` |
| P17 | **Second reader, unenumerated until FRV-r1.** `tools/governance_gates/scan.py:133` suppresses the freeze-review pending gate whenever the stamp's `verdict` equals `pass`, and `:236-241` `_narrative_freeze_pass` is a **second** prose fallback with regexes different from P15's. Two independent prose paths, two independent readers. | `tools/governance_gates/scan.py:112-146`, `:236-241` |
| P18 | The reader set is **closed at three modules**. An exhaustive scan of non-test, non-doc source for `review_stamp`, `extract_existing_stamp`, and verdict reads yields only `tools/freeze_reviewer/*`, `tools/governance_gates/scan.py`, and `tools/governance_hygiene/next_regen.py`. `tools/hosted_dashboard/` does not read freeze verdicts. FRV-b has no fourth reader to find. | `tools/freeze_reviewer/artifact.py:157-175`, `tools/governance_gates/scan.py:132-133`, `tools/governance_hygiene/next_regen.py:395-436` |

### §FRV.1.5 — Kit intent was already correct, and the structural cause is recorded

| ID | Finding | Citation |
| --- | --- | --- |
| P19 | The kit already labels the CLI path the "Mechanical gate" in operator documentation. The intent was right; only the enforcement was missing. | `docs/CHECK-OK.md:19-22` |
| P20 | The structural cause is a recorded rejection: PHASE-ISR declined to "Wire `ok review --freeze` to Mode D" as "wrong gate: freeze is pre-Auto." That is why the freeze gate inherited no ledger requirement while the build-verification gate did. | `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:182` |
| P21 | The machinery to fix it already exists and is additive by design: `ENTRY_KINDS` is a `frozenset` that ISR extended by exactly one value, with `find_matching_*` helpers beside each other and a v1 hash chain that has not been broken by any prior addition. | `tools/honesty/types.py:24-37`, `tools/honesty/validate.py:64-156`, `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:194-198` |

### §FRV.1.6 — Root cause frozen

> **A verdict record must not live inside the artifact it judges.**

The corollary, which drives every decision below: the artifact may carry a
*mechanical* result, because a mechanical result makes no claim that requires
independence — it only asserts "this file parses and passes lint-grade checks."
Anything that authorizes a build must live outside the artifact, in the existing
hash-chained ledger, and must be **bound to the artifact's bytes** so that editing
the artifact invalidates the authorization.

**Reuse, do not reinvent.** FRV-b adds one `ENTRY_KINDS` value, one
`find_matching_*` helper beside the existing three, and one shared read-only state
function. No second ledger, no parallel registry, no new top-level CLI verb.

---

## §FRV.2 — Scope

### §FRV.2.1 — In scope (FRV-a freezes; FRV-b implements as ONE build)

1. **F1** Vocabulary separation — `mechanical_verdict` + required `gate`; `verdict` reserved (§FRV.3).
2. **F2** Self-describing stamp; no false model claim (§FRV.4).
3. **F3** Inverted stickiness — merge, refuse escalation, explicit override (§FRV.5).
4. **F4** Ledger-based Auto authorization — additive kind `freeze_review`, gating
   **both** the `Thinking → Auto` and the plain `Auto` label (§FRV.6, §FRV.6.5.1).
5. **F5** Prose fallbacks deleted — **both** of them (§FRV.7).
6. **F6** `auto_may_start` honored as a real operator block (§FRV.8).
7. **F7** Migration / reconciliation, with the affected archive enumerated (§FRV.9).
8. Exit code `39` and reuse of existing codes (§FRV.10).
9. Boundary + rejection table (§FRV.11).
10. Seven-tier matrix, prefix `test_frv_` (§FRV.12).
11. Definition of Done (§FRV.13).

**Single build, deliberately.** F3 and F5 touch the same functions as F1, F2, F4
and F6: `build_stamp` / `stamp_is_idempotent_noop` / `_insert_review_stamp` in
`tools/freeze_reviewer/stamp.py:27-101`, and `_freeze_pass_state` /
`decide_split_emission` in `tools/governance_hygiene/next_regen.py:395-524`.
Splitting F1–F7 into separate Auto builds would land the tree in an intermediate
state where a stamp is relabelled but still authorizing, or authorization is moved
but the prose fallback still bypasses it. **FRV-b is one build.** Do not split it.

### §FRV.2.2 — Out of scope (explicit non-goals)

| Non-goal | Why rejected now |
| --- | --- |
| **Make the freeze gate require a different session (ISR Mode D)** | FRV revisits the `PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:182` rejection **only** to the extent of putting the freeze verdict in the ledger. Session independence for the freeze gate is a separate, larger posture change with its own friction profile. `producer_session_id` is optional on the new kind and its inequality rule applies only when supplied (§FRV.6.2). A later phase may promote it. |
| **Kit dispatches, hosts, or calls a review model** | AGENTS.md / P-route boundary, restated in `PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:170`. The runtime performs the review; the kit records and gates the claim. |
| **Teach the rule engine to judge C3 / C5–C7** | `tools/freeze_reviewer/providers/base.py:40-49` already documents why those require judgment rather than keyword matching. FRV's answer is to stop letting the rule engine's silence read as a review — not to make the rule engine smarter. |
| **Replace or redesign `ChecklistEngine`** | The engine is honest about what it is once it is labelled. Its checks stay byte-identical. |
| **Retro-stamp or rewrite archived phase documents** | §FRV.9 forbids a bulk migration commit and forbids retro-failing historical DONE rows. |
| **Renumber any existing exit code** | Additive only. `39` is the single new code (§FRV.10). |
| **Change honesty Mode A / B / C / D behavior** | Untouched. FRV adds a kind and a match helper; it adds no honesty-status mode and no new `HonestyErrorToken`. |
| **Break the v1 ledger chain** | One additive `ENTRY_KINDS` value, same discipline as `independent_second_review`. Canonical hashing rules unchanged. |
| **A second ledger, a registry file, or a new top-level verb** | Record via `ok ledger append --kind freeze_review`; read via one shared helper. |
| **A config knob that re-enables the prose fallback** | An opt-in prose fallback is the same hole with a switch on it. F5 deletes both paths outright (§FRV.7.3). |
| **Consumer rollout** | This repo **is** the kit, so the change reaches consumers through `ok sync`. Activating it in live consumer repos is a later operator-gated slice, not FRV-b. |
| **`ok check-ok` becoming a distinct engine** | It stays the same engine (P1). F1 makes it *say* so, which is the honest fix. |
| **FRV-b Auto implementation in this Thinking phase** | SD-3 split. Emit FRV-b as a separate Auto prompt (§FRV.14). |
| **Tier-3 merge, staging push, live posture flips, secrets** | Never authorized here. |

### §FRV.2.3 — Self-reference hazard (frozen authoring rule)

This artifact describes the parser that will read it. Two concrete hazards, both
confirmed against source:

1. `tools/governance_hygiene/next_regen.py:403` iterates **every** `yaml`/`yml`
   fence in the document looking for `review_stamp`, and
   `tools/freeze_reviewer/artifact.py:17-19` `FENCE_RE` matches the **first**
   `yaml`/`yml` fence as the §6.1 declaration. An illustrative stamp shown in a
   `yaml` fence is therefore indistinguishable from a real one.
2. `tools/freeze_reviewer/providers/base.py:16` `SECRET_RE` matches any of
   `api_key`, `api-key`, `apikey`, `secret`, `password`, or the word for an opaque
   credential string, when followed by a colon or equals sign and any non-space
   character. Writing a reason name in that shape self-triggers a C4 **BLOCKER**.
   This is the same class of false positive recorded as R3-C4 in
   `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:96`, and this
   very paragraph triggered it during FRV-r2 before being rephrased.

**Frozen rule for this artifact and for FRV-b's documentation edits:** the sole
`yaml` fence is the §6.1 declaration at the top of the file. Every illustrative
mapping uses a `text` fence. Reason names are written as "reason name — `x`",
never with a colon or equals sign directly following one of the words
`SECRET_RE` matches.

---

## §FRV.3 — F1: Separate the vocabulary (frozen)

### §FRV.3.1 — The two records

| Record | Written by | Lives in | May authorize Auto |
| --- | --- | --- | --- |
| **Mechanical** | `ok review --freeze` and `ok check-ok` (same engine, P1) | `review_stamp` inside the artifact | **Never** |
| **Substantive** | A human or a reviewing runtime, via `ok ledger append --kind freeze_review` | The hash-chained ledger, outside the artifact | Yes (§FRV.6.3) |

`gate` is the discriminator, and it is **required** on every stamp the CLI writes.
A stamp without a readable `gate` is not treated as a substantive record by any
reader — it is treated as mechanical at best (§FRV.3.4).

### §FRV.3.2 — Frozen key names and stamp shape

`ReviewStamp` (`tools/freeze_reviewer/types.py:70-91`) gains the F1 + F2 fields.
`to_mapping()` emits exactly these **fourteen** keys, in exactly this order,
always all present:

```text
review_stamp:
  gate: mechanical                # F1 — required discriminator; closed set below
  reviewed_at: 2026-09-12T00:00:00Z
  mechanical_verdict: pass        # F1 — closed set: pass | findings | blocked
  produced_by: checklist_engine   # F2 — closed set, §FRV.4.2
  provider_kind: rule_engine      # F2 — closed set: rule_engine | model_api
  reviewer_mode: agent
  reviewer_model: null            # F2 — MUST be null when provider_kind is rule_engine
  reviewer_provider: local
  checklist_ids:                  # F2 — effective checklist ids, in effective order
  - C1
  - C2
  checklist_source: builtin       # F2 — closed set: builtin | operator_file
  findings_count: 0               # F2 — computed, never hardcoded
  override_applied: false         # F3 — §FRV.5.4
  kit_version: 0.1.0
  artifact_digest: sha256:<64-hex>
```

**Frozen vocabulary.**

| Key | Closed set / type | Rule |
| --- | --- | --- |
| `gate` | `mechanical` | The CLI writes **only** `mechanical`. `substantive` is a reserved value that lives in the ledger and that the CLI **must never** write into an artifact. Readers treat any other value, or a non-string, as unreadable → non-authorizing (§FRV.3.4). |
| `mechanical_verdict` | `pass` \| `findings` \| `blocked` | Same derivation as today (`tools/freeze_reviewer/findings.py:60-75`); only the key name changes. `Verdict` (`tools/freeze_reviewer/types.py:18`) is reused unchanged. |
| `verdict` | — | **Reserved.** The CLI never writes it. `build_stamp` must not emit it and `_insert_review_stamp` must not synthesize it. |

**Why `gate` is first.** The key order is a human-legibility decision, not a
byte-compatibility one: an operator opening the fence sees the word `mechanical`
before the word `pass`. The order is frozen so the serializer output is
deterministic across runs, which the data-integrity tier asserts.

### §FRV.3.3 — Serializer contract (unchanged, and why)

`tools/freeze_reviewer/serializer.py:10-31` places the `review_stamp` **key**
after `frozen_inputs` if present, else after `outputs`, else last. **That contract
is not touched by FRV-b.** F1 changes what is *inside* the `review_stamp` value,
not where the key sits.

Order *inside* the stamp mapping is governed by `to_mapping()` insertion order,
because `dump_freeze_mapping` calls `yaml.safe_dump(..., sort_keys=False)`
(`tools/freeze_reviewer/serializer.py:37-43`). The §FRV.3.2 order is therefore the
on-disk order, and `round_trip_stable` (`:57-61`) must stay true for the new shape.

**Digests are unaffected.** Because `pre_stamp_canonical_bytes` pops `review_stamp`
before hashing in every artifact kind (P10, `tools/freeze_reviewer/artifact.py:119-147`),
renaming and extending the stamp **cannot** change any artifact's `artifact_digest`.
Every one of the 31 archived digests stays valid. FRV-b must assert this in the
data-integrity tier rather than assuming it.

### §FRV.3.4 — Legacy acceptance window (frozen)

For one release, readers accept a legacy stamp — one carrying `verdict` and no
`gate` — as **mechanical-only**. It never authorizes Auto. It is not an error, and
it is not rewritten in place.

**Frozen resolution order** for reading a stamp mapping, implemented **once** in
the shared module of §FRV.6.4 and used by all three readers:

1. `gate` present and equal to `mechanical` → mechanical record; the verdict value is `mechanical_verdict`.
2. `gate` present and equal to `substantive` → **refuse**. The CLI never writes this into an artifact (§FRV.3.2), so its presence means the document was hand-edited to impersonate a ledger record. Treated as non-authorizing with advisory name `forged_substantive_gate`.
3. `gate` present and anything else, or not a string → non-authorizing, advisory name `unreadable_gate`.
4. `gate` absent and `mechanical_verdict` present → mechanical record (a partially-migrated stamp).
5. `gate` absent, `mechanical_verdict` absent, `verdict` present, and `ACCEPT_LEGACY_VERDICT_STAMP` is true → mechanical record using `verdict` as the value.
6. Otherwise → no record.

**Frozen CLI normalization of a forged gate.** Branch 2 is a *reader* verdict.
The **writer** treats a forged `gate: substantive` as an ordinary CLI-owned key
and overwrites it with `mechanical` on the next stamp (§FRV.5.1 rule 1). This is
deliberate: the CLI erases the impersonation rather than preserving it. It does
**not** trigger the §FRV.5.2 refusal, because that refusal is about a non-`pass`
*verdict value*, not about a bad `gate`. FRV-b must implement both halves — reader
refuses, writer normalizes — and the security tier asserts both.

**Frozen behavior when there is no freeze mapping.** `parse_artifact` returns
`freeze_mapping = None` for the `operator_forced_md` kind
(`tools/freeze_reviewer/artifact.py:86`), and `extract_existing_stamp` then reads
the stamp out of the trailing marker region instead
(`tools/freeze_reviewer/artifact.py:161-174`). The §FRV.3.4 resolver therefore
operates on whatever mapping `extract_existing_stamp` returns, for every artifact
kind. `auto_may_start`, however, is a **freeze-block** key: when there is no
freeze mapping there is nowhere for it to live, so it reads as absent and no
operator block applies (§FRV.8.1). An operator who needs a block on an
operator-forced Markdown artifact must first give it a §6.1 declaration.

**Frozen constant.** `ACCEPT_LEGACY_VERDICT_STAMP = True` in the §FRV.6.4 module,
with a docstring naming this section. Flipping it to `False` is a **separate
phase**, not FRV-b, and requires the §FRV.9 reconciliation to have completed in
consumers. FRV-b must not add a config knob for it: the window is a kit-version
property, not a per-repo choice.

**Frozen window definition.** "One release" is every kit version below `0.3.0`
(`VERSION` is `0.1.0` at freeze time). Removal lands in the phase that bumps to
`0.3.0` and must be announced in `CHANGELOG.md` at that time.

### §FRV.3.5 — Surfaces that must be updated by FRV-b

| Surface | Change | Citation |
| --- | --- | --- |
| `ReviewStamp` dataclass + `to_mapping` | Thirteen fields, frozen order | `tools/freeze_reviewer/types.py:70-91` |
| `build_stamp` | Populate all fourteen; never emit `verdict` | `tools/freeze_reviewer/stamp.py:27-42` |
| `stamp_is_idempotent_noop` | Read via the §FRV.3.4 resolver; true no-op test per §FRV.5.3 | `tools/freeze_reviewer/stamp.py:45-52` |
| `report.py` `build_report` | `stamp` payload carries the new shape; add top-level `gate: "mechanical"` and `operator_block` (§FRV.8.3) to the report | `tools/freeze_reviewer/report.py:44-73` |
| `report.py` `render_human_report` | Print `Gate: mechanical` and `Mechanical verdict: <v>`; the word `Verdict:` alone must not appear for a mechanical run | `tools/freeze_reviewer/report.py:76-104` |
| `governance_gates/scan.py` | Read via the §FRV.3.4 resolver | `tools/governance_gates/scan.py:132-133` |
| `governance_hygiene/next_regen.py` | Read via the §FRV.3.4 resolver | `tools/governance_hygiene/next_regen.py:395-413` |
| `tools/freeze_reviewer/README.md` | Describe the mechanical/substantive split | `tools/freeze_reviewer/README.md:13` |
| `docs/CHECK-OK.md` | State that the CLI line is mechanical and cannot authorize Auto; the existing "Mechanical gate" label (P19) becomes normative | `docs/CHECK-OK.md:19-22` |

---

## §FRV.4 — F2: Self-describing stamp, no false model claim (frozen)

### §FRV.4.1 — What the stamp must disclose

`produced_by` and `provider_kind` answer "what code produced this result";
`checklist_ids` + `checklist_source` answer "against what"; `findings_count`
answers "how much was found". Together they make a mechanical stamp
self-evidently mechanical without reading the kit's source.

### §FRV.4.2 — Producer identity (frozen mechanism)

The `ReviewProvider` Protocol (`tools/freeze_reviewer/providers/base.py:21-35`)
gains one additive method:

```text
producer_identity() -> tuple[str, str]     # (produced_by, provider_kind)
```

**Frozen return values.**

| Provider state | `produced_by` | `provider_kind` | Citation |
| --- | --- | --- | --- |
| `LocalReviewProvider`, `scripted_findings is None` | `checklist_engine` | `rule_engine` | `tools/freeze_reviewer/providers/base.py:157-160` |
| `LocalReviewProvider`, `scripted_findings` set | `scripted_provider` | `rule_engine` | `tools/freeze_reviewer/providers/base.py:154-155` |
| `ApiReviewProvider`, `scripted_findings` set | `scripted_provider` | `rule_engine` | `tools/freeze_reviewer/providers/base.py:195-196` |
| `ApiReviewProvider`, real client call | `api_model` | `model_api` | `tools/freeze_reviewer/providers/base.py:197-203` |

**Frozen call ordering (R2-M1).** The scripted-vs-engine branch is decided *inside*
`review()`, so `run_freeze_review` MUST call `provider.review(...)` first and
`provider.producer_identity()` **after** it returns
(`tools/freeze_reviewer/engine.py:105-118`). Calling it earlier is a defect the
unit tier must catch.

**Frozen fail-closed default.** The Protocol is structural, and `ctx.review_provider_factory`
lets a caller inject a double (`cli/commands/review.py:176-178`). When the
effective provider has no `producer_identity` attribute, the engine MUST resolve
`("unknown", "rule_engine")` — never raise, and never claim `model_api`. "Fail
closed" here means *never inflate the claim*: an unknown producer is recorded as a
rule engine, which is the value that cannot authorize anything.

### §FRV.4.3 — `reviewer_model` must be null when a rule engine produced the verdict

**Frozen invariant.** `provider_kind == "rule_engine"` → `reviewer_model` is
`null`. Not the config label, not an empty string, not `"local"`.

- `reviewer_mode` and `reviewer_provider` keep their current meaning — they
  describe the *invocation* that was configured, which is a true statement, and
  they are what `report.py:14-28` already reports.
- `reviewer_model` is the only field that reads as a **causal** claim ("this model
  reviewed this document"), so it is the only one nulled.
- `mode: human` never reaches the stamp path at all: `run_freeze_review` returns
  `blocked` before any provider call (`tools/freeze_reviewer/engine.py:90-94`) and
  `build_stamp` is only invoked on `pass` (`:121-128`). No stamp, nothing to null.

**Consequence to state plainly:** after FRV-b, a default `ok review --freeze` run
on this repo produces `reviewer_model: null`. That is the correct reading of the
current configuration — `.overseer/config.yaml:32` uses the legacy string form
`reviewer: agent`, which defaults the model label at `adapters/config.py:507-518`
and sends it to a provider that ignores it (P4).

### §FRV.4.4 — `checklist_ids`, `checklist_source`, `findings_count`

| Field | Source | Rule |
| --- | --- | --- |
| `checklist_ids` | `ReviewResult.checklist_ids`, already populated | Emitted as a YAML sequence in effective order. Non-empty by construction (`tools/freeze_reviewer/engine.py:64-66`; `load_checklist_file` rejects an empty list at `tools/freeze_reviewer/checklist.py:41-43`). |
| `checklist_source` | `builtin` when `--checklist` absent, `operator_file` when present | Distinguishes the eight built-in checks from an operator replacement, which `tools/freeze_reviewer/checklist.py:31-60` allows to be **any** set — including one that omits C4. Without this field a stamp cannot be read for what it actually checked. |
| `findings_count` | `len(result.findings)` | **Computed, never hardcoded.** Honest note: under FRV-b this is always `0`, because `derive_verdict` returns `pass` only for an empty findings list (`tools/freeze_reviewer/findings.py:66-67`). It is frozen as computed so a future substantive record with non-blocking findings is representable without a schema change. FRV-b must not write the literal `0`. |

### §FRV.4.5 — Not in the stamp (frozen exclusions)

Unchanged from `PHASE-K5-FREEZE-REVIEWER-CONTRACT.md:607`: no username, host,
email, credential, session id, or absolute machine path. `produced_by` is a closed
vocabulary, not free text, precisely so it cannot become an identity leak.

---

## §FRV.5 — F3: Invert the stickiness (frozen)

### §FRV.5.1 — Merge, do not replace

`_insert_review_stamp` (`tools/freeze_reviewer/stamp.py:55-58`) must merge.

**Frozen merge rule.** Let `E` be the existing `review_stamp` mapping (or `{}`),
and `N` the newly built stamp mapping from §FRV.3.2. The written mapping is:

1. The fourteen CLI-owned keys of `N`, in the §FRV.3.2 order. CLI-owned keys in
   `E` are overwritten.
2. Then every key of `E` that is **not** CLI-owned, in its original relative
   order, appended after — value preserved verbatim, including nested structures.
3. The legacy `verdict` key is **dropped** when `N` is written: it is CLI-owned
   under §FRV.3.4 (it is the key `N` replaces), so it must not survive as a stale
   sibling that a future reader could mistake for a live record.

**Frozen CLI-owned key set** (the fourteen of §FRV.3.2 plus legacy `verdict`, fifteen names
in total),
named as a single constant in `tools/freeze_reviewer/stamp.py` so the merge and
the §FRV.3.4 resolver cannot drift apart.

This applies to all four artifact kinds, including the two operator-forced paths
(`tools/freeze_reviewer/stamp.py:73-86`), where today the Markdown path rebuilds
the stamp region from scratch.

### §FRV.5.2 — Refuse to escalate

**Frozen rule.** If the existing stamp resolves (§FRV.3.4) to a record whose
verdict value is a non-empty string other than `pass`, the CLI **must not write**,
and must exit non-zero, unless the explicit override flag is given.

| Item | Frozen value |
| --- | --- |
| Flag | `--override-non-pass-stamp` |
| Exit code | `39` |
| Constant | `EXIT_STAMP_ESCALATION_REFUSED = 39` in `tools/freeze_reviewer/engine.py`, beside `resolve_exit_code` (`tools/freeze_reviewer/engine.py:133-147`) |
| Reason name | `stamp_escalation_refused` |
| `ReviewResult` fields | `escalation_refused: bool = False`, `escalation_refuse_cause: str \| None = None` — additive to `tools/freeze_reviewer/types.py:94-113` |

**Frozen message and payload.** stderr carries one line naming the reason and the
existing value, with no absolute path; the JSON report carries
`"reason": "stamp_escalation_refused"` and the existing verdict value. The
artifact is left byte-identical.

**Frozen locus.** The check runs in `run_freeze_review` on the `pass` branch,
**before** `write_stamp_or_fail` is called
(`tools/freeze_reviewer/engine.py:121-128`) — not inside `write_stamp`. Putting it
in the engine is what makes the next rule expressible.

**Frozen interaction with `--dry-run` and `--no-stamp`.** `39` means *a write was
refused*. Under `--dry-run` or `--no-stamp` no write is attempted, so the command
exits on the normal verdict (`0` for a mechanical pass) and does **not** return
`39`. The condition is still reported: `escalation_refused: true` appears in the
JSON report and the human report prints the same one-line notice. This keeps
`--dry-run` a pure inspection mode, consistent with
`PHASE-K5-FREEZE-REVIEWER-CONTRACT.md:231` ("Full review report; write nothing"),
while never hiding the conflict from the operator. The integration tier asserts
all four combinations.

**Frozen precedence.** `resolve_exit_code` becomes `2 > 4 > 5 > 39 > 8 > 7 > 0`.
No existing code moves. `39` sits after the IO code because an IO failure is a
worse condition, and before `8` so a refusal is never masked by an escalation that
cannot co-occur with it (a refusal only arises on the `pass` branch, where `7` and
`8` are unreachable — `tools/freeze_reviewer/engine.py:121-128`). The placement is
frozen explicitly so FRV-b does not have to infer it.

**Frozen non-goal for the flag.** `--override-non-pass-stamp` permits overwriting
a **document record**. It cannot change a derived verdict, cannot skip the
provider, and is **not** a synonym for the permanently-banned
`--escalate-force-pass` (`cli/commands/review.py:25-32`). That flag stays in
`DISALLOWED_FLAGS`; the new flag must **not** be added to it.

**Frozen plumbing.** Both `ok review --freeze` and `ok check-ok` accept the flag.
`run_check_ok` builds a `review` Namespace by hand and must pass it through
(`cli/commands/check_ok.py:82-92`); a missing attribute there is a silent
capability gap the integration tier must catch.

**Frozen override behavior.** With the flag, the write proceeds and the stamp
records `override_applied: true`. Without it, `override_applied` is `false`. The
field is always present so the shape never varies.

### §FRV.5.3 — A true no-op

`stamp_is_idempotent_noop` (`tools/freeze_reviewer/stamp.py:45-52`) today asks a
question about the *old* schema. Frozen replacement: a re-run is a no-op when
**all** hold.

1. The existing stamp resolves (§FRV.3.4) to a mechanical record.
2. Its verdict value equals the new `mechanical_verdict`.
3. Its `artifact_digest` equals the recomputed one.
4. **The fully merged mapping of §FRV.5.1 serializes byte-identically to what is
   already on disk.**

Condition 4 is the real test and subsumes 1–3; 1–3 are kept as cheap short
circuits and as the readable statement of intent. Condition 4 is what makes
"re-running the gate is a true no-op" assertable for the new shape, and it is what
makes the first post-FRV-b run on a legacy seven-key stamp correctly write **once**
— that single rewrite is the migration, and §FRV.9.3 frozen expects it.

`reviewed_at` must not be refreshed on a no-op, unchanged from
`PHASE-K5-FREEZE-REVIEWER-CONTRACT.md:610-614`.

### §FRV.5.4 — Why a document edit still cannot lie

P10 stands: edits inside `review_stamp` do not change `artifact_digest`. FRV does
not try to fix that — it makes it irrelevant. After F4, nothing inside
`review_stamp` authorizes anything. Authorization is a ledger entry bound to the
digest of the artifact's bytes **excluding** `review_stamp`, so:

- editing `review_stamp` cannot forge authorization (the stamp is not consulted for authorization);
- editing anything else in the artifact changes the digest and **invalidates** the bound ledger entry;
- flipping `auto_may_start`, which lives outside `review_stamp`, also changes the digest (§FRV.8.2).

---

## §FRV.6 — F4: Move Auto authorization onto the ledger (frozen)

### §FRV.6.1 — Additive entry kind

**Additive amendment of the K9a / P-evidence / ISR entry-kind enum:** add
**exactly one** new value. Every prior kind's required fields and semantics stay
byte-identical. FRV-b extends `ENTRY_KINDS` in `tools/honesty/types.py:24-37` and
adds the matching `validate_append_body` branch
(`tools/honesty/validate.py:164-...`) — no second ledger, no renumbering.

```text
freeze_review
```

**Envelope (unchanged K9a / P0 rules):** every non-genesis entry carries `v: 1`,
`kind`, `ts` (server may fill), `prev_hash` / `entry_hash` (server fills),
`actor_role`, `actor_session_id`, and optional `provenance`.

**Role rule (frozen):** `actor_role` MUST be `verifier`. Any other role → exit `23`.

### §FRV.6.2 — Frozen schema

**Required fields.**

| Field | Type | Rule |
| --- | --- | --- |
| `phase_id` | non-empty string | Opaque phase / slice id, same family as P-evidence and ISR. |
| `frozen_spec` | non-empty string | Opaque path-shaped string. Append checks **non-empty string only** — no must-exist, no path-confine of the stored string (same as `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:225`). |
| `round` | integer ≥ 1 | Freeze-review round. `< 1` or non-int → exit `2`. |
| `freeze_verdict` | `pass` \| `findings` \| `blocked` | Lowercase closed vocabulary. Any other value → exit `2`. Named distinctly from `bv_verdict` and `isr_verdict` so no existing match helper can ever select the wrong kind. |
| `gate` | `substantive` | **Required and must equal `substantive`.** Any other value → exit `2`. A mechanical result never produces a ledger entry; this field makes that structural rather than conventional. |
| `artifact_digest` | string matching `sha256:` + 64 lowercase hex | The binding to the reviewed bytes. Shape-validated at append only — **no file read, no path resolution, no network** on the append path. |
| `reviewer_model` | non-empty string | The model label that actually performed the review. **Not** validated against `policy/model-labels.yaml` at append: the ledger records the claim, and a consumer may legitimately use a label the kit does not ship. This is the same records-the-claim posture as `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:217-218`. |

**Optional fields.**

| Field | Type | Rule |
| --- | --- | --- |
| `checklist_ids` | list of non-empty strings | When present, must be a non-empty list of non-empty strings; else exit `2`. |
| `findings_count` | integer ≥ 0 | When present, `< 0` or non-int → exit `2`. |
| `producer_session_id` | non-empty string | **Optional by deliberate decision** (§FRV.2.2 row 1). When present **and** equal to `actor_session_id` → exit `2`, reusing the ISR independence rule (`docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:209-219`) only where the caller opted in. |
| `notes` | string | Advisory; never a substitute for the verdict. |
| `provenance` | object | Optional; identical to P0 rules. |

**Example (normative shape, illustrative ids).**

```text
{
  "v": 1,
  "kind": "freeze_review",
  "ts": "2026-09-12T00:00:00Z",
  "actor_role": "verifier",
  "actor_session_id": "review-chat-1",
  "phase_id": "FRV-b",
  "frozen_spec": "docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md",
  "round": 5,
  "gate": "substantive",
  "freeze_verdict": "pass",
  "artifact_digest": "sha256:<64-hex>",
  "reviewer_model": "thinking-high",
  "checklist_ids": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
  "findings_count": 0,
  "prev_hash": "...",
  "entry_hash": "..."
}
```

**Genesis forbid-list (frozen).** Extend the existing genesis forbid-list in
`validate_append_body` with `gate`, `freeze_verdict`, `artifact_digest`,
`checklist_ids`, `findings_count` — additive to keys already refused. `phase_id`,
`frozen_spec`, `round`, and `producer_session_id` are already forbidden from
P-evidence / ISR; **do not remove them**.

**CLI record surface (frozen).** Reuse `ok ledger append --kind freeze_review`
(`--file` / `--stdin`). No new top-level verb. `ok ledger verify` / `show` treat
the new kind like any other. CLI `--kind` remains authoritative over body `kind`
(`tools/honesty/validate.py:172-174`).

**App API (frozen, no code needed).** `tools/app/engine.py:305` validates the kind
against `ENTRY_KINDS` dynamically, so the new kind becomes appendable through the
loopback API with **no** change to `tools/app/`. FRV-b must not add a special case
there, and the security tier must assert the path stays behind the existing Bearer
+ CSRF auth rather than becoming a new unauthenticated surface.

### §FRV.6.3 — Match rule (frozen)

New pure helper, implemented beside the existing three in
`tools/honesty/validate.py:64-156`:

```text
find_matching_freeze_review(entries, *, phase_id, frozen_spec, artifact_digest) -> entry | None
```

An entry matches when **all** hold:

1. `kind` equals `freeze_review`.
2. `actor_role` equals `verifier`.
3. `gate` equals `substantive`.
4. `freeze_verdict` equals `pass`.
5. `phase_id` equals the supplied `phase_id`.
6. `frozen_spec` equals the supplied value **when supplied** (`None` skips, same as the existing helpers).
7. `artifact_digest` equals the supplied value **when supplied** (`None` skips).
8. `producer_session_id`, **when present on the entry**, differs from `actor_session_id`.

**Last-wins** among matches, identical to `tools/honesty/validate.py:84`, `:117`,
`:155`.

**Frozen caller obligation.** The authorization caller of §FRV.6.4 MUST supply all
three of `phase_id`, `frozen_spec`, and `artifact_digest`. The `None`-skips
affordance exists for parity with the sibling helpers and for diagnostic callers;
it must never be used on the authorization path. The security tier asserts this by
mutation: a caller that omits `artifact_digest` must fail a test.

**No network, no model, no IDE session read** on any path in this helper — same
constraint as `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:281-282`.

### §FRV.6.4 — Shared authorization state (frozen)

FRV-b adds **one** new module, `tools/freeze_authorization/`, following the
established per-phase module pattern (`tools/muse_sync/`, `tools/footprint_integrity/`,
`tools/land_closeout/`). It is the single implementation of the §FRV.3.4 resolver
and of the authorization state machine, imported by **both** readers
(`tools/governance_hygiene/next_regen.py` and `tools/governance_gates/scan.py`).
This placement also avoids `tools/governance_hygiene/` growing a direct dependency
on `tools/honesty/`.

```text
freeze_authorization_state(repo_root, artifact_path, *, phase_id, config)
    -> FreezeAuthorization
```

`FreezeAuthorization` is a frozen dataclass carrying `state`, `advisory`, and
`matched_entry_hash`.

**Frozen `state` vocabulary** (closed set):

| `state` | Meaning |
| --- | --- |
| `substantive` | A `find_matching_freeze_review` hit bound to the artifact's current digest. **The only authorizing state.** |
| `mechanical_only` | No ledger match; the stamp resolves to a mechanical record with verdict `pass`. |
| `non_pass` | The stamp resolves to a mechanical record with a non-`pass` verdict. |
| `blocked_by_operator` | `auto_may_start` is present and false, or is present and not a boolean (§FRV.8). |
| `absent` | No readable record at all. |

**Frozen evaluation order** (first match wins):

1. Parse the artifact with the existing `parse_artifact`
   (`tools/freeze_reviewer/artifact.py:89-101`). Unreadable or not-UTF-8 → `absent`;
   never raise.
2. Read `auto_may_start` from the top level of the freeze mapping. Present and not
   `True` → `blocked_by_operator` (§FRV.8.1). This is checked **before** the
   ledger so an operator block cannot be out-voted by a stale entry.
3. Compute the artifact's current digest with the existing `artifact_digest`
   (`tools/freeze_reviewer/artifact.py:150-154`) — the same function the stamp
   writer uses, so there is one digest definition in the kit.
4. Resolve the ledger path via `_resolve_ledger_path` semantics already used by
   `tools/honesty/ledger.py:80-84`; read entries with
   `read_ledger_entries` (`tools/honesty/ledger_io.py:45-57`).
5. Verify the chain with `verify_chain` (`tools/honesty/ledger.py:31-37`). A
   non-zero result means the ledger is untrustworthy → **no match is possible**;
   continue to step 7 with advisory name `ledger_chain_broken`.
6. Call `find_matching_freeze_review` with all three keys (§FRV.6.3). Hit →
   `substantive`, `matched_entry_hash` set.
7. No match: resolve the stamp per §FRV.3.4 → `mechanical_only` /
   `non_pass` / `absent`, carrying the §FRV.3.4 advisory name when one applies.

**Fail-closed, never-raise (frozen).** Missing ledger file, empty ledger, malformed
JSONL (`read_ledger_entries` raises `ValueError` at `tools/honesty/ledger_io.py:37-40`),
`honesty.enabled: false`, unreadable artifact, or a config with no honesty block —
every one of these yields a **non-authorizing** state and never an exception.
Specifically: honesty disabled means **no repo can authorize Auto by ledger**,
which is the safe direction and which the integration tier must assert.

### §FRV.6.4.1 — `phase_id` must be derived identically by both readers (frozen)

The two readers reach this function from different data, and they must not
disagree about what `phase_id` means — a divergence would make the gate scan and
the emission path assert opposite things about the same slice.

| Reader | Today's phase identity | Citation |
| --- | --- | --- |
| `decide_split_emission` | `compact_step_id(row.phase_label)` — a compact token such as `FRV` | `tools/governance_hygiene/next_regen.py:512` |
| `_scan_freeze_review` | `_normalize_phase_id(...)` — a **whitespace-collapsed display string** such as `FRV-a Freeze-review verdict integrity`, drawn from either the handover `ID` cell or a roadmap row label | `tools/governance_gates/scan.py:86-110`, `:121` |

**Frozen rule.** `freeze_authorization_state` is always called with a `phase_id`
produced by `compact_step_id` (`tools/governance_hygiene/next_regen.py:355-362`,
built on `tools/governance_hygiene/parse.py:75` `phase_tokens`). `_scan_freeze_review`
therefore must **not** pass its normalized display string: it must resolve the
roadmap row it already matched in `_contract_path_for_phase`
(`tools/governance_gates/scan.py:210-233`) and derive the compact token from that
row's `phase` group.

`_normalize_phase_id` keeps its existing role — set membership for `active`
(`tools/governance_gates/scan.py:86-98`) — and is **not** repurposed as a ledger
key. The unit tier asserts that both readers produce the same `phase_id` for the
same roadmap row, and the integration tier asserts that a single appended
`freeze_review` entry simultaneously clears the pending gate and authorizes the
emission.

**Chain verification is mandatory here (frozen).** `verify_chain` walks the
entries already in memory (`tools/honesty/ledger.py:45-56`); it opens no file and
makes no network call, so the cost is one pass over a file the step already read.
A tampered or truncated ledger must not authorize a build. `require_agent_signature`
is **not** forced on from this path — it stays whatever the config says
(`adapters/config.py:443-448`), so the git-only baseline is preserved per
`docs/ROADMAP.md:166-174`.

### §FRV.6.5 — Emission change (frozen)

`decide_split_emission` (`tools/governance_hygiene/next_regen.py:499-524`).

**Frozen signature.**

```text
decide_split_emission(row, repo_root, *, config) -> tuple[str | None, str | None, bool, str | None]
```

The fourth element is the **advisory name** (§FRV.6.6). `config` is keyword-only
and required; `plan_next_regen` already holds it
(`tools/governance_hygiene/next_regen.py:539-555`).

**Frozen call-site updates.** Exactly two positional three-tuple call sites exist
outside the module and FRV-b must update both:
`tests/unit/test_gs_paste_next_regen.py:78` and `:94`. No production call site
outside `next_regen.py` exists.

**Frozen decision table for the `Thinking → Auto` label.** `phase_id` for the
lookup is `compact_step_id(row.phase_label)`, the same token the existing detector
uses (`tools/governance_hygiene/next_regen.py:512`); `frozen_spec` is the
candidate's repo-relative POSIX path.

| Candidate states across `discover_freeze_candidates` | Emission | Advisory |
| --- | --- | --- |
| Any `blocked_by_operator` | `("Thinking", None, False)` | `operator_block` |
| Any `substantive` **and** any `non_pass` | `(None, REASON_SPLIT, False)` | — (existing fail-closed ambiguity, `:520-521`, preserved byte-for-byte) |
| Any `substantive`, row status in `OPEN_STATUSES` | `("Auto", None, True)` | — |
| Any `mechanical_only`, no `substantive` | `("Thinking", None, False)` | `mechanical_only` |
| All `absent` | `("Thinking", None, False)` | — |
| No candidates found | `("Thinking", None, False)` | — (unchanged, `:514-515`) |

`blocked_by_operator` is evaluated first and outranks a `substantive` match: an
explicit operator block is the strongest signal in the table.

### §FRV.6.5.1 — The plain `Auto` label must gate too (frozen, R4-M1)

**Verified reachability problem.** `decide_split_emission` returns the queue model
unchanged for every non-split label (`tools/governance_hygiene/next_regen.py:509-510`),
so the freeze detector runs **only** for rows whose Model cell is literally
`Thinking → Auto`. Parsed live against the current `docs/ROADMAP.md`: of **103**
queue rows, **4** carry `Thinking → Auto` (`K1`, `K2`, and two `K12` rows — all
long DONE) while **43** carry plain `Auto`. Every phase since at least GS-PASTE
uses the modern two-row convention — an `{id}-a` row on `Thinking` and an
`{id}-b` row on `Auto` — so a freeze gate wired only to the split label would be
**dead code in this repo and in every consumer that copies its convention**. F4
would have shipped an authorization gate that the kit's own roadmap style
bypasses.

**Frozen extension.** `decide_split_emission` consults
`freeze_authorization_state` for an open row whose normalized model is **either**
`Thinking → Auto` **or** `Auto`.

| Open row model | Freeze artifact discoverable? | State | Emission | Reason / advisory |
| --- | --- | --- | --- | --- |
| `Auto` | no candidates | — | `("Auto", None, False)` | — (unchanged; the kit never invents a freeze requirement for a row that declared none) |
| `Auto` | yes | `substantive` | `("Auto", None, False)` | — |
| `Auto` | yes | `mechanical_only` \| `non_pass` \| `blocked_by_operator` \| `absent` | `(None, REASON_FREEZE_NOT_SUBSTANTIVE, False)` | reason `freeze_not_substantive` |
| `Thinking` / `Operator` / `Operator + Auto` | — | — | unchanged (`:509-510`) | — |

**Why ambiguity and not a downgrade.** A plain `Auto` row has no `{step}a` sibling
to fall back to, so emitting `Thinking` would **fabricate** a step the roadmap does
not contain — exactly what `docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md:176`
forbids ("Do **not** invent a NEXT from … prose … or chat memory"). The honest
behavior is the existing fail-closed ambiguity channel of §GSP.4.3: NEXT and
paste-ready bodies are left untouched, all other patches proceed, and the operator
is told precisely why. This reuses a frozen mechanism rather than adding a
suppression path.

**Why `Operator + Auto` is excluded.** That label denotes an operator-driven slice
with human Tier-3 gates, not a mechanical build session handed to a model. Gating
it would block land / dogfood rows on a freeze artifact they legitimately do not
have. Frozen as out of scope.

**Frozen reason name** (an *ambiguity* reason, additive beside
`REASON_ZERO`…`REASON_LAND_PHASE_UNREADABLE` at
`tools/governance_hygiene/next_regen.py:27-33`, and distinct from the §FRV.6.6
advisory names):

```text
REASON_FREEZE_NOT_SUBSTANTIVE = "freeze_not_substantive"
```

It renders through the existing unchanged paths as
`next_regen: human_authorship_required (freeze_not_substantive)` and
`next_regen=human_authorship_required:freeze_not_substantive`
(`tools/governance_hygiene/next_regen.py:712-725`).

**Frozen `phase_id` under the two-row convention.** `compact_step_id` preserves the
`-a` / `-b` suffix (`tools/governance_hygiene/next_regen.py:355-362`), so it yields
`FRV-a` for the Thinking row and `FRV-b` for the Auto row. The entry that
authorizes a build therefore carries the **Auto row's** `phase_id` (`FRV-b`) while
its `frozen_spec` points at the **freeze artifact** authored under the Thinking row.
These two values intentionally differ; §FRV.9.3 states the operator procedure.
`discover_freeze_candidates` already strips a trailing `-a` / `-b` when building
its search tokens (`:466`), so the `-b` row still discovers the shared artifact.

### §FRV.6.6 — Advisory channel (frozen, R1-M1)

`mechanical_only` MUST NOT be carried in `NextRegenDecision.reason`. Any non-`None`
`reason` short-circuits `plan_next_regen` to ambiguity
(`tools/governance_hygiene/next_regen.py:556-557`) and renders as
`human_authorship_required` (`:712-725`) — which would **suppress** NEXT
regeneration instead of emitting a Thinking step. That is the opposite of the
intent.

**Frozen mechanism.** `NextRegenDecision` (`tools/governance_hygiene/next_regen.py:336-344`)
gains one additive field `advisory: str | None = None`, defaulted so every existing
construction site stays valid. `plan_next_regen` populates it from the fourth
tuple element and still returns the row, so regeneration proceeds normally.

**Frozen reason-name vocabulary** (additive module constants beside
`REASON_ZERO`…`REASON_LAND_PHASE_UNREADABLE` at `tools/governance_hygiene/next_regen.py:27-33`;
these are **advisory** names, not ambiguity reasons):

```text
ADVISORY_MECHANICAL_ONLY = "mechanical_only"
ADVISORY_OPERATOR_BLOCK = "operator_block"
ADVISORY_LEDGER_CHAIN_BROKEN = "ledger_chain_broken"
ADVISORY_FORGED_SUBSTANTIVE_GATE = "forged_substantive_gate"
ADVISORY_UNREADABLE_GATE = "unreadable_gate"
```

**Frozen rendering.** `format_next_regen_token` (`:712-717`) and
`format_change_log_fragment` (`:720-725`) keep their current output when
`advisory` is `None`. When set, they append it:

```text
next_regen: regenerated (advisory=mechanical_only)
next_regen=regenerated:advisory=mechanical_only
```

The existing `human_authorship_required` strings are unchanged. No new handover
HTML anchor is introduced — GS-PASTE remains the sole NEXT surface
(`docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md:130`).

---

## §FRV.7 — F5: Delete the prose fallbacks (frozen)

### §FRV.7.1 — Bold text in a table must never authorize a build

Delete `tools/governance_hygiene/next_regen.py:415-436` outright — the
`verdict`/`pass` text search, the `**pass**` / `→ **pass**` / `reviewed → pass`
search, and the loose `review_stamp:` … `verdict:` text scan. All three are
whole-document text searches that cannot distinguish a record from a sentence
about a record.

`_freeze_pass_state` is then **replaced**, not patched: its whole job moves into
`freeze_authorization_state` (§FRV.6.4). FRV-b removes the function rather than
leaving a second, weaker reader in the tree.

### §FRV.7.2 — The second prose fallback goes too (R1-M2)

`tools/governance_gates/scan.py:236-241` `_narrative_freeze_pass` is a **separate**
prose fallback with different regexes (`reviewed → pass`, `Freeze status: … pass`,
`→ pass … Cleared`), consulted at `:135-136`. Delete it.

**Frozen replacement for the gate scan.** `_scan_freeze_review`
(`tools/governance_gates/scan.py:112-146`) calls `freeze_authorization_state` and:

- `substantive` → no pending gate (the gate is genuinely satisfied);
- `mechanical_only` → the pending gate **remains**, with its message naming
  `mechanical_only` so the reminder tells the operator exactly what is missing;
- `non_pass`, `blocked_by_operator`, `absent` → pending gate remains, message
  naming the state.

**Frozen non-escalation.** This scan is a **reminder** surface. Its output flows
into `PendingGate` records (`tools/governance_gates/types.py:12`) and has never set
an exit code, and FRV-b must not give it one. More reminders is the safe direction
of change; a new failing exit on this path is out of scope.

### §FRV.7.3 — No opt-in (frozen)

A config knob that re-enables prose matching is the same hole with a switch on it,
and it would have to be read by both readers, doubling the surface. **There is no
opt-in.** The replacement path is complete without it: `ok review --freeze` writes
the mechanical stamp, and `ok ledger append --kind freeze_review` records the
substantive verdict.

---

## §FRV.8 — F6: Honor an explicit operator block (frozen)

### §FRV.8.1 — Key, locus, semantics

| Item | Frozen value |
| --- | --- |
| Key | `auto_may_start` |
| Locus | **Top level of the freeze block**, sibling of `phase` / `outputs` / `frozen_inputs` / `review_stamp` — **not** inside `review_stamp` |
| Type | boolean |
| Default | **Absent.** Absent means "no operator opinion" and has no effect. Never required, never written by the kit. |

| Value | Effect |
| --- | --- |
| absent | No effect. |
| `true` | No effect. An operator cannot *grant* authorization with this key; only the ledger grants it. |
| `false` | `blocked_by_operator` — non-authorizing regardless of ledger or stamp (§FRV.6.4 step 2, §FRV.6.5 row 1). |
| any non-boolean (e.g. the string `"false"`) | `blocked_by_operator` with advisory name `operator_block_malformed`. **Fail closed:** a malformed block is honored as a block, never silently ignored. |

`ADVISORY_OPERATOR_BLOCK_MALFORMED = "operator_block_malformed"` joins the
§FRV.6.6 constants.

### §FRV.8.2 — Why the locus matters (frozen rationale)

`pre_stamp_canonical_bytes` pops **only** `review_stamp` before hashing
(`tools/freeze_reviewer/artifact.py:119-147`). A top-level sibling key is therefore
**inside** `artifact_digest`. Two consequences, both desirable, both frozen:

1. Adding or flipping `auto_may_start` changes the artifact digest, which
   **invalidates** any bound `freeze_review` ledger entry (§FRV.6.3 rule 7). An
   operator block cannot be out-voted by a pre-existing authorization.
2. Because it sits outside `review_stamp`, the §FRV.5.1 stamp merge never touches
   it, and the `dict(mapping)` copy in `_insert_review_stamp` plus the
   order-preserving serializer already carry it through a stamp write unharmed
   (P16). No new preservation logic is needed — only a reader.

### §FRV.8.3 — CLI behavior (frozen)

`ok review --freeze` and `ok check-ok` **still run and still stamp** when
`auto_may_start` is false: the block governs whether Auto may start, not whether
the document may be checked. The CLI:

- **never** writes, removes, reorders, or normalizes the key;
- reports it as `operator_block: true | false | null` in the JSON report
  (`tools/freeze_reviewer/report.py:44-73`);
- prints one line in the human report when it is present and not true, naming the
  block (`tools/freeze_reviewer/report.py:76-104`);
- does **not** change its exit code because of it — `39` is for §FRV.5.2 only.

Documented in `docs/CHECK-OK.md` and `tools/freeze_reviewer/README.md` by FRV-b.

---

## §FRV.9 — F7: Migration and reconciliation (mandatory, in scope)

### §FRV.9.1 — Enumerated blast radius (verified, read-only)

`docs/archive/phases/` holds **40** documents. Verified by parsing each one's first
`yaml`/`yml` fence and by running the current `_freeze_pass_state` against it:

| Class | Count | Post-FRV-b state |
| --- | --- | --- |
| Mechanical stamp, `verdict: pass`, `reviewer_model: thinking-high`, `reviewer_provider: local` | **31** | `mechanical_only` (via the §FRV.3.4 legacy window) |
| No stamp; authorizes today **only** through the prose fallback | **5** | `absent` |
| No stamp and no prose pass; already non-authorizing | **4** | `absent` (unchanged) |

All 31 stamped documents carry the identical false model claim of P9 — not a
sample, the whole set.

**The 5 prose-only documents**, named so the reconciliation is verifiable rather
than asserted:

```text
docs/archive/phases/PHASE-CHECK-OK.md
docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md
docs/archive/phases/PHASE-K6-PILOT-INSTALL-MATRIX.md
docs/archive/phases/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
docs/archive/phases/PHASE-K9A-L1-L2-MODULE-FREEZE.md
```

**The 4 already-non-authorizing documents:**

```text
docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
docs/archive/phases/PHASE-K12-TRACK-N-LANDING-CONTRACT.md
docs/archive/phases/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md
docs/archive/phases/PHASE-PR-LAND-AFTER-CHECKS.md
```

**Discovery reachability (verified).** `docs/` has **zero** top-level `PHASE-*.md`
files, and `discover_freeze_candidates` globs only `docs/*.md`
(`tools/governance_hygiene/next_regen.py:473-483`). Archived phase documents are
reachable **only** through the deliverable-cited-path branch
(`:486-494`), which accepts any `docs/…​.md` confined under `docs/`
(`:439-449`). A ROADMAP row whose deliverable cell cites its archive path is
therefore the sole discovery route in this repo today.

### §FRV.9.2 — No bulk migration, no retro-fail (frozen)

1. **FRV-b rewrites no archived phase document.** There is no bulk migration
   commit, no script, no retro-stamp.
2. **No ROADMAP row changes status.** Every historical **DONE** row stays DONE.
   This is structurally safe, not merely a promise: `decide_split_emission`
   consults freeze state only for a row whose status is in `OPEN_STATUSES`
   (`tools/governance_hygiene/next_regen.py:522`, `:35`) **and** whose model cell
   is `Thinking → Auto` (`:509-510`). Archived DONE slices are never re-evaluated.
3. **No archived document regresses because of F1.** The §FRV.3.4 legacy window
   keeps all 31 stamped documents readable as `mechanical_only` rather than
   `absent`.
4. **The 5 prose-only documents become `absent`.** All five belong to closed
   slices, so the state is unreachable from the emission path per point 2. This is
   a deliberate, enumerated, bounded consequence — not a surprise.

### §FRV.9.3 — Forward procedure (frozen)

For every phase that starts after FRV-b lands:

1. Thinking session authors the freeze artifact with `frozen: true`.
2. `ok review --freeze <artifact>` → the **mechanical** stamp
   (`gate: mechanical`). On a pre-FRV-b seven-key stamp this performs exactly
   **one** rewrite to the fourteen-key shape (§FRV.5.3 condition 4); that rewrite
   **is** the per-document migration, it is idempotent from then on, and it does
   **not** change `artifact_digest` (§FRV.3.3).
3. Substantive review rounds run and are recorded in the document's review-record
   table, which stays human/agent-maintained and which the CLI never edits
   (`docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md:530-531`).
4. `ok ledger append --kind freeze_review` records the substantive verdict, with
   `artifact_digest` set to the digest reported in step 2, `frozen_spec` set to the
   freeze artifact's repo-relative path, and `phase_id` set to the compact id of
   the **row that will be authorized** — the `{id}-b` Auto row, not the `{id}-a`
   Thinking row that authored the artifact (§FRV.6.5.1).
5. `ok governance-sync` then emits the `{id}-b` Auto paste. Before step 4, a
   `Thinking → Auto` row emits `{step}a` on `Thinking` with advisory
   `mechanical_only`, and a plain `Auto` row is held as ambiguous with reason
   `freeze_not_substantive` (§FRV.6.5.1).

### §FRV.9.4 — Re-opening an archived slice (frozen, R2-M2)

If an operator moves an archived row back to an open status, the old mechanical
stamp will **not** authorize Auto. The operator must append a fresh `freeze_review`
entry bound to the artifact's **current** digest.

Back-dating is impossible by construction rather than by rule: the digest binding
of §FRV.6.3 rule 7 means an entry can only match bytes that already existed when
it was written, and the hash chain makes insertion at an earlier position
detectable by `ok ledger verify`.

### §FRV.9.5 — Consumers (frozen boundary)

This repo **is** the kit, so FRV-b reaches consumers through `ok sync`. On the
first sync a consumer's archived documents behave exactly as this repo's do —
`mechanical_only`, emitting Thinking. Nothing in a consumer breaks and nothing
fails closed on a gate it did not opt into. **Consumer rollout is a later
operator-gated slice and is not part of FRV-b** (§FRV.2.2).

---

## §FRV.10 — Exit codes (frozen)

Additive code; non-overlapping with existing `1`, `2`, `4`, `5`, `7`, `8`,
`10`–`11`, `20`–`26`, `30`–`38` (highest existing is `EXIT_MISSING_INDEPENDENT_SECOND_REVIEW = 38`
at `tools/honesty/status.py:26`):

| Code | Meaning | Where |
| --- | --- | --- |
| `39` | Refused to escalate an existing non-pass stamp without `--override-non-pass-stamp` | `ok review --freeze` / `ok check-ok`; JSON report `reason` is `stamp_escalation_refused` |

Constant name (frozen): `EXIT_STAMP_ESCALATION_REFUSED = 39` in
`tools/freeze_reviewer/engine.py`. CLI and tests import that name. Do not reuse
`5`, `7`, `8`, `33`, `34`, or `38`.

Reused (no renumbering):

| Code | Reuse |
| --- | --- |
| `1` | Usage — unknown flag, banned flag (`cli/commands/review.py:35-46`) |
| `2` | Config / malformed `freeze_review` append body (bad `freeze_verdict`, `gate` ≠ `substantive`, malformed `artifact_digest`, `round < 1`, equal session ids when `producer_session_id` supplied) |
| `4` | Refuse — freeze contract disabled, path escape, not-UTF-8, honesty disabled |
| `5` | Stamp IO failure (atomic write preserved) |
| `7` / `8` | Findings / blocked-or-human (unchanged) |
| `22` | Ledger chain broken (unchanged; also the condition that makes §FRV.6.4 step 5 non-authorizing) |
| `23` | Role violation — `actor_role` ≠ `verifier` on `freeze_review` |
| `25` / `26` | Provenance (P0; unchanged) |

**Frozen precedence.** `resolve_exit_code` becomes `2 > 4 > 5 > 39 > 8 > 7 > 0`
(`tools/freeze_reviewer/engine.py:133-147`). `ok status --exit-code` precedence
(`2 > 6 > 35 > 3 > 0`) is **not** touched: `39` is confined to the review /
check-ok commands and never folds into status.

**Not exit codes (frozen).** `freeze_not_substantive` is an **ambiguity reason**
carried in `NextRegenDecision.reason` and rendered in the governance-sync plan and
change-log strings; the §FRV.6.6 advisory names are **advisory** and never
suppress regeneration. Neither adds, changes, or reuses an exit code.
`governance-sync` keeps whatever code the §GSP.4.3 ambiguity path already returns,
and the §FRV.7.2 gate-scan reminder keeps setting none.

---

## §FRV.11 — Boundary, capability, rejection

**The single most important frozen rule:** the kit **records and gates** review
claims. It never runs a review model, never opens a chat, and never treats its own
rule engine as a reviewer. FRV's whole contribution is making that boundary
legible in the data the kit writes.

| Concern | Kit does | Kit never does |
| --- | --- | --- |
| Mechanical checks | Runs the §K5.5 rule engine and labels the result `gate: mechanical` | Calls it a review, or lets it authorize Auto |
| Substantive review | Records a `freeze_review` ledger entry bound to artifact bytes | Performs the review, dispatches a model, or infers a verdict from prose |
| Model attribution | Records `reviewer_model` only where a model actually ran | Asserts a config label as a causal claim |
| Operator intent | Reads and honors `auto_may_start: false` | Writes, normalizes, or overrides it |
| Authorization | Emits `Auto` only on a digest-bound ledger match | Accepts a document's self-assessment |

**Regime parity (frozen).** Everything in FRV works fully on `git-only`. The
ledger is a repo-local JSONL file; `verify_chain` needs no Muse and no network;
`require_agent_signature` stays off under git-only by config validation
(`adapters/config.py:443-448`). No FRV capability is MuseHub-only, per
`docs/ROADMAP.md:166-174`.

---

## §FRV.12 — Seven-tier matrix (FRV-b)

Per `policy/test-tiers.yaml`. Exact test file prefix: `test_frv_` under the
existing `tests/` seven-tier folders. Do not invent a second family name.

| Tier | Must prove |
| --- | --- |
| **unit** | `ReviewStamp.to_mapping` emits the fourteen §FRV.3.2 keys in the frozen order and **never** `verdict`; `gate` is always `mechanical`; `mechanical_verdict` derives from `derive_verdict` for all three verdicts; §FRV.3.4 resolver returns the right record for each of its six branches incl. `forged_substantive_gate` and `unreadable_gate`; `ACCEPT_LEGACY_VERDICT_STAMP` gates branch 5; `producer_identity()` returns each of the four §FRV.4.2 pairs; a provider double lacking the method resolves `("unknown", "rule_engine")`; `reviewer_model` is `null` whenever `provider_kind` is `rule_engine` and non-null only for `api_model`; `checklist_source` is `builtin` vs `operator_file`; `findings_count` equals `len(findings)` and is not the literal `0`; §FRV.5.1 merge keeps unknown keys in order and drops legacy `verdict`; §FRV.5.3 four-condition no-op; `freeze_review` in `ENTRY_KINDS`; `validate_append_body` accepts a minimal valid body and rejects each of `gate` ≠ `substantive`, bad `freeze_verdict`, malformed `artifact_digest` (wrong prefix / wrong length / uppercase hex), `round < 1`, non-int `round`, empty `phase_id`, empty `frozen_spec`, negative `findings_count`, empty `checklist_ids`, and `producer_session_id == actor_session_id` → `2`; non-`verifier` role → `23`; genesis forbid-list covers the five new keys; `find_matching_freeze_review` last-wins, rejects `findings`/`blocked`, rejects `gate` ≠ `substantive`, rejects digest mismatch; `freeze_authorization_state` returns each of the five states; `auto_may_start` absent / `true` / `false` / non-boolean; advisory constants and `REASON_FREEZE_NOT_SUBSTANTIVE` exist with the frozen spellings; both readers derive the same `phase_id` from the same roadmap row (§FRV.6.4.1); `compact_step_id` retains the `-a` / `-b` suffix so the Auto row's id differs from the Thinking row's. |
| **integration** | `ok review --freeze` on a clean artifact writes the fourteen-key stamp and exits `0`; re-run writes nothing and exits `0` with `reviewed_at` unchanged; a hand-downgraded stamp → exit `39`, reason `stamp_escalation_refused`, artifact byte-identical; the same case under `--dry-run` and under `--no-stamp` → exit `0` with `escalation_refused: true` and **no** `39` (all four flag combinations, §FRV.5.2); same run with `--override-non-pass-stamp` → exit `0`, `override_applied: true`; a forged `gate: substantive` is normalized back to `mechanical` by the writer and refused by every reader; `ok check-ok --path` reaches all of the above through its hand-built Namespace (`cli/commands/check_ok.py:82-92`); `--escalate-force-pass` still exits `1`; `ok ledger append --kind freeze_review` writes a hash-chained line and `ok ledger verify` → `0`; **`Thinking → Auto` row:** emits `Auto` only with a digest-bound match, else `Thinking` + advisory `mechanical_only`; **plain `Auto` row (§FRV.6.5.1):** emits `Auto` with a match, is held ambiguous with reason `freeze_not_substantive` on `mechanical_only` / `non_pass` / `absent` / `blocked_by_operator`, and emits `Auto` unchanged when no freeze artifact is discoverable; **`Operator + Auto` row is never gated**; `auto_may_start: false` blocks even with a valid match; `honesty.enabled: false` makes `substantive` unreachable; a broken ledger chain makes `substantive` unreachable with advisory `ledger_chain_broken`; one appended entry simultaneously clears the pending gate and authorizes the emission (§FRV.6.4.1); `governance-sync --dry-run` renders the advisory in both the plan token and the change-log fragment without printing `human_authorship_required`, and renders the ambiguity reason through the existing unchanged strings; gate scan leaves the pending gate for `mechanical_only` and clears it for `substantive`, and sets no exit code either way; app API accepts the new kind via `ENTRY_KINDS` with auth unchanged. |
| **e2e** | git-only fixture repo, full loop on a `Thinking → Auto` row: author artifact → `ok review --freeze` → `ok governance-sync --dry-run` shows `{step}a` on `Thinking` with advisory `mechanical_only` → `ok ledger append --kind freeze_review` bound to the reported digest → `governance-sync --dry-run` now shows `{step}b` on `Auto` → edit one prose byte of the artifact → `Auto` is withdrawn back to `Thinking` because the digest no longer matches. Same loop on the **two-row** convention (`{id}-a` Thinking DONE + `{id}-b` Auto open), which is the convention this repo actually uses: the Auto row is held with reason `freeze_not_substantive` until the entry is appended under `phase_id` `{id}-b`, then emits `Auto`, then is withdrawn again after a one-byte artifact edit. Identical loops under a Muse-regime fixture. A fixture carrying only a bold `pass` review table and no stamp never emits `Auto`. An `Operator + Auto` row with a mechanically-stamped artifact emits unchanged. `ok next` still extracts the same paste fence after the docs-pointer edits. |
| **stress** | Ledger with ≥ 50 `freeze_review` entries plus ≥ 50 entries of other kinds: match is last-wins with one pass and no unbounded walk; artifact with ≥ 200 `yaml`/`text` fences and a ≥ 1 MB body parses within the existing freeze-contract-edge bounds of `policy/test-tiers.yaml`; `discover_freeze_candidates` cap on `docs/*.md` is unchanged (no recursive walk introduced). |
| **data-integrity** | Re-running the gate is a **true** no-op — zero bytes written, `reviewed_at` unchanged, verified by mtime **and** content hash; a verdict can **never** be escalated by a re-run (a non-pass stamp survives an unflagged re-run byte-for-byte); unknown keys inside `review_stamp` survive a re-stamp with order preserved; keys outside `review_stamp` survive; `artifact_digest` for all four artifact kinds is **identical** before and after the F1/F2 rename (asserted against a recorded pre-FRV-b digest, so the 31 archived digests are proven stable); `round_trip_stable` holds for the fourteen-key shape; the serializer still places the `review_stamp` key per `tools/freeze_reviewer/serializer.py:10-31`; ledger tamper (flip one byte of a body, truncate a line, reorder two lines, insert a forged entry) breaks `ok ledger verify` **and** removes authorization; an IO failure mid-stamp leaves the original bytes (exit `5`). |
| **performance** | `freeze_authorization_state` — parse + digest + ledger read + `verify_chain` + match — completes within the same order as `ok status` on a realistic repo; `governance-sync --dry-run` shows no regression attributable to the ledger read; no unbounded VCS log scan and no network call is introduced on any read path. |
| **security** | **A document cannot self-authorize:** no edit confined to the artifact yields `substantive`, asserted by mutation across all four artifact kinds. **No magic-phrase path yields Auto authorization:** a document containing only the four §FRV.1.1 trigger phrases stamps `mechanical` and emits `Thinking`. **Prose cannot authorize:** bold `pass`, `reviewed → pass`, `Freeze status: … pass`, and a bare `verdict`/`pass` pairing each emit `Thinking` — asserted against **both** deleted fallbacks (`next_regen` and `governance_gates`). **A forged `gate: substantive` in a document never authorizes** and is reported as `forged_substantive_gate`. **An operator block cannot be overwritten without the explicit flag:** `auto_may_start: false` survives every CLI path and outranks a valid ledger match; a non-boolean value fails closed to blocked. **The authorization caller cannot omit the digest:** a mutation that drops `artifact_digest` from the §FRV.6.3 call must fail a test. No network call, no model call, and no subprocess on append / verify / match / authorization paths (asserted, not assumed). No secret, credential, session id, username, host, or absolute machine path in the stamp, in the ledger entry, in the JSON report, or in any advisory string. `ok ledger append` treats `notes` / `frozen_spec` / `reviewer_model` as opaque — never fetched, never executed. App API auth for the new kind is unchanged. |

---

## §FRV.13 — Definition of Done

**FRV-a (this phase).** This document reviewed → `pass` by the thinking-model
rounds recorded above, with a CLI **mechanical** stamp as the secondary check;
`docs/ROADMAP.md` FRV-a row → DONE with the FRV-b row queued; `docs/OVERSEER-HANDOVER.md`
NEXT → FRV-b; `ok governance-sync`; one feature-branch commit bundling roadmap +
handover + this artifact. **No Auto code, no test file, no CLI edit this session.**
No `main` merge. No live posture flips. No secrets. The pre-existing
`governance_freshness: drifted` and any pending Muse sync are cleared in this
closing session before FRV-a is marked DONE.

**FRV-b.** Every in-scope deliverable exists at the path this freeze names; §FRV.12
green with prefix `test_frv_`; the full suite shows no new failures beyond the
recorded pre-existing set; `ok sync --yes` so any changed kit-owned asset lands in
the lock and footprint coverage stays `ok`; `ok status --exit-code` → `0`;
`docs/CHECK-OK.md` + `tools/freeze_reviewer/README.md` + SPEC §6 pointer updated;
`tests/unit/test_gs_paste_next_regen.py:78` and `:94` updated to the new signature;
no archived phase document rewritten; no consumer defaults changed; no exit code
renumbered; no honesty mode changed; `/build-verification-review` → **pass** from a
**second chat** with an `independent_second_review` entry appended before DONE
(`honesty.require_independent_second_reviewer` is `require` on this repo per
`.overseer/config.yaml:57`). Green tests alone are **not** DONE. Merge remains
Tier 3.

---

## §FRV.14 — Operator paste for FRV-b (informational; GS-PASTE may regen)

Model: **Auto**. Build exactly against this file as one build. Do not split F1–F7.
Do not redesign. Do not re-derive §FRV.1. Do not dispatch a model. Do not rewrite
archived phase documents. Do not renumber exit codes. Do not add a config knob for
the prose fallback or for the legacy window.

---

## §FRV.15 — Cross-references

- **K5** `docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md` — §K5.5 checklist, §K5.7 stamp locus / digest / idempotency, §K5.2 flag contract; FRV amends the stamp *contents* and the write *polarity*, not the locus or the digest definition
- **ISR** `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md` — the ledger-kind pattern FRV reuses; `:182` is the rejection FRV narrowly revisits for the freeze gate only
- **GS-PASTE** `docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md` — §GSP.5.2 split detector FRV replaces; §GSP.4.3 ambiguity semantics FRV must not disturb
- **P-evidence / P-deploy** — `verification_evidence` precedent for opaque `frozen_spec` and for artifact-hash-not-blob recording
- **K9a / K10** — ledger, roles, canonical hashing
- **K7** — no MuseHub-only baseline; FRV is fully functional on `git-only`
- **KH1.9 / governance gates** — the reminder surface FRV makes consistent with authorization
- **Check OK** `docs/CHECK-OK.md` — the "Mechanical gate" label FRV makes normative
