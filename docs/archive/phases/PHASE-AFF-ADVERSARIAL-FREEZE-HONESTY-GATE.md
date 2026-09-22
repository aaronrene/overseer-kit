# Phase AFF — Adversarial-freeze honesty gate (Thinking freeze)

Status: **Reviewed → `pass` (AFF-ADV-r5).** AFF-a is **spec-only** and is
now ROADMAP DONE. A different-chat attack review independently re-derived
ADV4-M1–M2 closed at the claimed fail-closed layers and re-derived every
ADV1–ADV3 repair intact (not narrowed). No CLI edit, honesty schema change,
skill edit, or test file landed in this phase. No `adversarial_freeze` entry
was appended (AFF-a bootstrap; the kind does not exist until AFF-b), and
`auto_may_start: true` remains absent. No FRV `freeze_review` rebind was
required (no prior bound entry). NEXT is **AFF-b** (Auto). The
`review_stamp` below is the post-AFF-ADV-r5 mechanical stamp; it remains
non-authorizing.

```yaml
phase: AFF
outputs:
- id: aff-adversarial-freeze-honesty-gate
  path: docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md
  frozen: true
frozen_inputs:
- id: kit-spec
  path: docs/OVERSEER-KIT-SPEC.md
- id: k5-freeze-reviewer
  path: docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
- id: frv-verdict-integrity
  path: docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md
- id: isr-independent-second-reviewer
  path: docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md
- id: p-evidence
  path: docs/archive/phases/PHASE-TRACK-P-P-EVIDENCE.md
- id: p-deploy
  path: docs/archive/phases/PHASE-TRACK-P-P-DEPLOY.md
- id: p-route
  path: docs/archive/phases/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md
- id: gs-paste
  path: docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md
- id: ons-operator-next
  path: docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md
- id: lt-loop-tightening
  path: docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md
- id: check-ok
  path: docs/archive/phases/PHASE-CHECK-OK.md
- id: freeze-review-loop-skill
  path: cursor/skills/freeze-review-loop/SKILL.md
- id: freeze-review-skill
  path: cursor/skills/freeze-review/SKILL.md
- id: check-ok-thinking-rule
  path: cursor/rules/check-ok-thinking.mdc
- id: honesty-types
  path: tools/honesty/types.py
- id: honesty-status
  path: tools/honesty/status.py
- id: honesty-ledger
  path: tools/honesty/ledger.py
- id: honesty-validate
  path: tools/honesty/validate.py
- id: honesty-config
  path: adapters/config.py
- id: freeze-authorization
  path: tools/freeze_authorization/resolve.py
- id: next-regen
  path: tools/governance_hygiene/next_regen.py
- id: governance-hygiene-engine
  path: tools/governance_hygiene/engine.py
- id: isr-surface
  path: tools/independent_second_reviewer/surface.py
- id: status-exit
  path: cli/commands/status.py
- id: kit-boundary
  path: AGENTS.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: model-labels
  path: policy/model-labels.yaml
review_stamp:
  gate: mechanical
  reviewed_at: '2026-09-20T14:13:27Z'
  mechanical_verdict: pass
  produced_by: checklist_engine
  provider_kind: rule_engine
  reviewer_mode: agent
  reviewer_model: null
  reviewer_provider: local
  checklist_ids:
  - C1
  - C2
  - C3
  - C4
  - C5
  - C6
  - C7
  - C8
  checklist_source: builtin
  findings_count: 0
  override_applied: false
  kit_version: 0.1.0
  artifact_digest: sha256:5b8a9aa52ee25e9d4824e72b1df4154f8c184cc82bd30703a9b1bb5737eb96c3
```

**Downstream edge:** AFF-b treats this document as ground truth without
re-deriving it (SPEC §6 mandatory reviewed freeze). The second chat / separate
verifier *performs* the attack-posture review. The kit only **records and
optionally gates** the verdict. The kit never dispatches, hosts, or calls a
second model. A later host may spawn a second agent; that is out of kit scope.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line**.
Uncited findings are invalid and are discarded. Fixes are Tier 1 on the feature
branch. Merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| AFF-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R1-M1–M3** + **R1-N1–N2**. Fixed in-tree before CLI stamp. |
| AFF-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-N1** digest contradiction; **R2-N2** skip last-wins key; **R2-N3** two match helpers named. Fixed in-tree. |
| AFF-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | R1–R2 confirmed RESOLVED. **R3-N1** paste nonce placeholder (no IDE scrape). Mechanical stamp was then written at historical digest `sha256:f60ad824…`; AFF-ADV-r1 later changed artifact bytes. |
| AFF-ADV-r1 | Adversarial freeze (different chat, attack posture, `Thinking`) | **findings** | **ADV1-B1**, **ADV1-M1–M3**, **ADV1-N1–N2**. Author fix required; no adversarial pass recorded; AFF-a remains WIP. |
| AFF-r4 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | ADV1-B1, ADV1-M1–M3, and ADV1-N1–N2 resolved in §AFF.5.1/§AFF.5.3/§AFF.5.5–§AFF.5.6, §AFF.7.2–§AFF.7.4, §AFF.8.1–§AFF.8.3, §AFF.10, and §AFF.14–§AFF.15. Fresh adversarial review next; AFF-a remains WIP. |
| AFF-ADV-r2 | Adversarial freeze (different chat from producer nonce `aff-a-author-2026-09-19`, attack posture, `Thinking`) | **findings** | R1 repairs independently confirmed, but **ADV2-M1–M2** and **ADV2-N1–N3** remain. No adversarial pass or ledger append; AFF-a remains WIP. |
| AFF-r5 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | ADV2-M1–M2 and ADV2-N1–N3 resolved in §AFF.2, §AFF.5.2, §AFF.7.1, §AFF.8.1–§AFF.8.2, §AFF.9, §AFF.14, and §AFF.16. Fresh adversarial review next; AFF-a remains WIP. |
| AFF-ADV-r3 | Adversarial freeze (different chat from producer nonce `aff-a-author-fix-r2-2026-09-20`, attack posture, `Thinking`) | **findings** | ADV2-M1–M2/N1–N3 independently confirmed closed and ADV1 repairs re-derived intact, but **ADV3-M1–M3** remain. No adversarial ledger append; AFF-a remains WIP. |
| AFF-r6 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | ADV3-M1–M3 resolved in §AFF.4.3, §AFF.5.5–§AFF.5.6, §AFF.7.1, §AFF.9, and §AFF.14. Fresh adversarial review next; AFF-a remains WIP. |
| AFF-ADV-r4 | Adversarial freeze (different chat from producer nonce `aff-a-author-fix-r3-2026-09-20`, attack posture, `Thinking`) | **findings** | **ADV4-M1–M2**: hash-valid malformed AFF entries can still pass the envelope/type boundary and authorize. No adversarial ledger append; AFF-a remains WIP. |
| AFF-r7 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | ADV4-M1–M2 resolved in §AFF.5, §AFF.5.2–§AFF.5.5, §AFF.8.3, §AFF.14, and §AFF.16; ADV1–ADV3 re-derived in the AFF-r7 resolution map. Fresh adversarial review next; AFF-a remains WIP. |
| AFF-ADV-r5 | Adversarial freeze (different chat from producer nonce `aff-a-author-fix-r4-2026-09-20`, attack posture, `Thinking`) | **pass** | ADV4-M1–M2 independently re-derived closed at the claimed layers; ADV1–ADV3 repairs re-derived intact and not narrowed. AFF-a bootstrap: Review-record only; no `adversarial_freeze` append; no FRV rebind required; no `auto_may_start: true`. AFF-a → DONE; AFF-b Auto is queued. |

### Freeze-review findings ledger (AFF-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | BLOCKER | completeness | §AFF.5.5 / `next_regen.py:478` (pre-fix) | Matching AFF pass only on `compact_step_id` of the open Auto row misses a pass recorded during `{id}-a` (this repo's two-row convention). Same class as FRV-r4. Frozen: Auto-hold match is `frozen_spec` + `artifact_digest`. |
| R1-M2 | MAJOR | completeness | §AFF.7.1 (pre-fix); `next_regen.py:475-476` | Hold was specified only when FRV would emit Auto. `decide_split_emission` returns Thinking rows unchanged, so after author freeze-review-loop pass `ok next` would keep the author paste, not the adversarial paste. Frozen: second trigger on Thinking / `{step}a` after author-loop complete. |
| R1-M3 | MAJOR | completeness | §AFF.8.3 (pre-fix) | Mode E skip vs `--producer-session` unspecified; a skip body forbids `producer_session_id`, so a pinned producer would miss a valid skip. Frozen: skip match ignores `--producer-session`. |
| R1-N1 | MINOR | completeness | `next_regen.py:435-457` | `discover_freeze_candidates` is top-level `docs/*.md` **plus** deliverable-cited paths. Archive freezes are found only via the backtick path in the Auto row deliverable. Frozen: AFF-b deliverable must cite this artifact. |
| R1-N2 | MINOR | completeness | §AFF.8.1 (pre-fix) | `--artifact-digest` as the only digest source is extra ceremony when `--frozen-spec` is a real file. Frozen: digest source order. |
| R2-N1 | MINOR | completeness | §AFF.8.1 | Both `--artifact-digest` and a hashable `--frozen-spec` with unequal values was unspecified. Frozen: usage `1`. |
| R2-N2 | MINOR | consistency | §AFF.5.3 | Skip last-wins key still named `(phase_id, artifact_digest)` after R1-M1. Frozen: `(frozen_spec, artifact_digest)`. |
| R2-N3 | MINOR | completeness | §AFF.5.5 | Match helper signature was `(...)`. Frozen: two named helpers (`_pass` / `_skip`) so skip cannot be queried as pass. |
| R3-N1 | MINOR | completeness | §AFF.7.2 | Paste said "including the author producer_session_id" without saying `next_regen` must not scrape IDE ids. Frozen: placeholder `<AUTHOR_PRODUCER_SESSION_NONCE>`. |

**Citation discipline:** every review finding in this artifact **must** include
`path:line` so the operator can verify — never trust uncited review output
(§6.2 / K5).

---

## §AFF.0 — Simple summary

After a Thinking freeze, the same chat that wrote the spec can run
`/freeze-review-loop`, get `ok review --freeze` to stamp pass, and treat Auto
as cleared. A second look that *tries to break the spec* is something the
operator invented by hand. Independent freeze review lives in handover folklore.
Independent-second-reviewer only runs after Auto claims DONE. Complex security
freezes (NFT transfer, KYC) needed extra attack-posture passes the operator
ran outside the kit. Those extra passes found real holes.

**Adversarial freeze makes that extra pass a kit honesty gate.** After the
author loop stamps a freeze, `ok next` prints an attack-posture Thinking
paste for a *different* chat (prefer a different model) until that side-check
records a real pass — or, if the repo chose `suggest`, the operator records
skip once. The kit still does not call a model and still holds no key.

**Technical summary:** add `honesty.adversarial_freeze: off|suggest|require`
(derived default `suggest` when `freeze_contract.human_escalation` includes
`security`; `require` is operator-opt-in). Add ledger kind
`adversarial_freeze` (pass/findings/blocked/skip). Author
`/freeze-review-loop` MUST NOT write `auto_may_start: true` and MUST NOT treat
mechanical stamp as Auto-cleared. After FRV would emit Auto, `ok next` emits
an adversarial Thinking paste until a digest-bound pass exists, or a skip
exists under `suggest`. Honesty-status **Mode E**; exit `40`; active-slice
status/governance-sync surface; portable paste doc + twin skill. Four review
kinds stay distinct. No model dispatch. No AFF-b code in this Thinking phase.

---

## §AFF.1 — Verified problem (do not redesign)

| Fact | Evidence |
| --- | --- |
| Author freeze-review-loop treats CLI stamp as success and exits | `cursor/skills/freeze-review-loop/SKILL.md:60-62` — on pass, run `ok review --freeze`, stamp, "EXIT success". No adversarial paste. No `auto_may_start` prohibition. No ledger append. |
| Mechanical CLI stamp cannot authorize Auto (FRV) | SPEC §6.2 FRV amendment; `tools/freeze_reviewer/` writes `gate: mechanical` |
| Same-session `freeze_review` ledger *can* authorize Auto | `tools/honesty/validate.py:402-408` — `producer_session_id` is optional on `freeze_review`. `tools/honesty/validate.py:187-194` — session inequality is skipped when that field is absent. Author can append `freeze_review` pass in the same chat. |
| FRV deliberately did not import session independence for freeze | `docs/archive/phases/PHASE-FRV-FREEZE-REVIEW-VERDICT-INTEGRITY.md` — "ledger record required, session independence **not** imported" |
| ISR rejected applying ISR to Thinking freeze-review DONE | `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md:182` — ISR = Auto slices only |
| ISR is post-Auto ROADMAP DONE | `cursor/skills/independent-second-reviewer/SKILL.md:1-6`; `docs/INDEPENDENT-SECOND-REVIEWER.md:11-14` |
| Independent freeze review is folklore, not a kit gate | `docs/archive/thinking/OVERSEER-KIT-MASTER-THINKING-PROMPT.md:5` — "Remaining: independent freeze review … before K9b Auto". `cursor/skills/freeze-review/SKILL.md:48-51` — multi-round loop is optional; no second-chat gate |
| `ok next` emits Auto when FRV state is `substantive` | `tools/governance_hygiene/next_regen.py:491-493` (plain `Auto`); `:510-511` (`Thinking → Auto` → `{step}b`) |
| `auto_may_start: true` does not grant Auto | `tools/freeze_authorization/resolve.py:142-143`; FRV §FRV.8.1 — only `false` blocks; `true` has no effect. Kit never writes the key (FRV §FRV.8.1 / `docs/CHECK-OK.md:27-28`) |
| Check-OK thinking rule starts Auto on freeze `pass` | `cursor/rules/check-ok-thinking.mdc:21` — "Do not start Auto until verdict is **`pass`**". No adversarial hold |
| Kit dogfood already escalates `security` | `.overseer/config.yaml:33-37` — `human_escalation` includes `security` |
| No `adversarial_freeze` honesty key exists | `adapters/config.py:34-47` `HONESTY_KEYS`; `.overseer/config.yaml:53-57` honesty block |
| Honesty-status modes stop at D | `tools/honesty/status.py:146-175` `_resolve_mode` — A/B/C/D only |
| Used additive honesty/CLI exits include `33`–`39` | P-evidence `33`, P-deploy `34`, workspace `35`, PLS `36`, ONS `37`, ISR `38`, FRV stamp `39` |
| Kit is rule-holder, never model executor | P-route; `AGENTS.md`; SPEC §6 |
| Operator-observed extra attack passes found real holes | Operator report: NFT transfer / KYC freezes needed hand-invented adversarial rounds (K1–K5, R2-A1–A5, R3-I1). Those rounds are **not** a kit gate today. This freeze does not import consumer product code |

---

## §AFF.2 — Scope

**In scope (AFF-a freezes; AFF-b implements):**

1. Four-way review vocabulary (§AFF.3).
2. Config `honesty.adversarial_freeze` + derived default (§AFF.4).
3. Ledger kind `adversarial_freeze` + skip rules (§AFF.5).
4. Author freeze-review-loop MUST NOT set `auto_may_start: true` (§AFF.6).
5. `ok next` / `next_regen` adversarial Thinking paste until pass or skip (§AFF.7).
6. Honesty-status **Mode E** (§AFF.8).
7. Active-slice status / governance-sync surface (§AFF.9).
8. Portable CLI + docs + twin skill + freeze-review / check-ok-thinking amendments (§AFF.10).
9. Exit code `40` and reuse of existing codes (§AFF.11).
10. Boundary + rejection table — governance, not runtime (§AFF.12).
11. SPEC §5 additive clauses (§AFF.13).
12. Seven-tier matrix (§AFF.14).
13. Definition of Done (§AFF.15).

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected now |
| --- | --- |
| **Kit dispatches / hosts / calls a second model** | P-route + AGENTS.md. Runtime / operator opens the second chat. Host spawn is out of kit scope. |
| **Automate Cursor "new chat" / tab open** | No honest host command. Print the paste. Same family as tab-reload reject. |
| **`require` as shipped default or kit-dogfood Auto v1** | Operator-opt-in per consumer. Derived / dogfood default is `suggest`. |
| **Replace FRV `freeze_review` Auto authorization** | AFF is an *additional* hold when enabled. FRV still required. |
| **Force session inequality on `freeze_review`** | That would redesign FRV. Independent freeze review stays distinct; AFF carries the required independence for attack posture. |
| **Apply ISR to Thinking freeze-review DONE** | Already rejected (ISR §ISR.2). ISR stays post-Auto implementation. |
| **Reuse `independent_second_review` or `freeze_review` for attack posture** | Wrong lifecycle and wrong posture. New kind. |
| **Reuse `warn` as the middle mode** | ISR `warn` reminds and does not hold Auto. AFF `suggest` holds Auto until pass *or* skip. Different word, different semantics. |
| **Write `auto_may_start: false` from freeze-review-loop** | FRV: kit never writes the key. Writing `false` would block AFF-b until flipped, and flipping invalidates the digest-bound ledger. Prohibition is "MUST NOT set `true`", not "MUST write `false`". |
| **Treat `auto_may_start: true` as granting Auto** | FRV already forbids the grant. AFF does not reopen it. |
| **Make docs/reviews Check-OK files themselves require AFF** | Recursion. AFF applies to roadmap-discovered freeze candidates (`discover_freeze_candidates`), same as FRV. |
| **New top-level CLI verb** (`ok adversarial-freeze`) | Record = `ok ledger append`; check = Mode E on `ok honesty-status`; paste = `ok next`. |
| **Block historical DONE rows** | Active slice only (LT / ISR posture). |
| **MuseHub-only identity as the gate** | K7: baseline on `git-only`. |
| **Cryptographic proof of chat identity as git-only baseline** | P0 remains optional / soft under git-only. Kit records the claim. |
| **Require different `reviewer_model` as a hard gate** | Paste *prefers* a different model. Kit cannot honestly know models. `reviewer_model` is **required** on pass/findings/blocked as a recorded label (§AFF.5.2). Inequality vs optional `producer_model` is preference only; equal labels still accept. Skip does not carry `reviewer_model`. |
| **AFF-b Auto implementation in this Thinking phase** | SD-3 split. |
| **Consumer product Auto, bornfree-hub product code, hub Main deploy** | Operator hard stop. Kit contract only. |
| **Tier-3 merge, staging push, live posture flips** | Never authorized here. |
| **Secrets, API keys, or model endpoints in config / ledger** | Names and opaque session strings only. |

---

## §AFF.3 — Four review kinds (frozen vocabulary)

These four names are **normative**. Skills, paste docs, NEXT paste, and this
freeze MUST use them without collapsing two kinds into one.

| Kind | When | Posture | Session | What a pass means | Kit record |
| --- | --- | --- | --- | --- | --- |
| **freeze-review-loop** | Author Thinking session, same chat that wrote the spec | Improve until clean | **Same session** | Mechanical CLI stamp + review-record rounds | `ok review --freeze` mechanical stamp. Does **not** authorize Auto. |
| **independent freeze review** | After the author claims close | **Verify claimed close** (did they actually freeze what they said?) | Different chat, recommended | Substantive `freeze_review` ledger pass bound to digest | Existing kind `freeze_review` (FRV). Session inequality remains **optional** (FRV). Not a new kind. Not this gate. |
| **adversarial freeze** | After freeze-review-loop pass, **before Auto** | **Try to kill** the spec (attack, fail-open, self-auth, missing tests, injection) | **Different chat**, prefer different model | Digest-bound `adversarial_freeze` `aff_verdict: pass` (or `skip` once under `suggest`) | New kind `adversarial_freeze`. This phase. |
| **independent second reviewer (ISR)** | After Auto implementation, **before ROADMAP DONE** | Re-check the *build* against the freeze | Different chat from the builder | `independent_second_review` pass | Existing ISR. Unchanged. |

**Ordering (frozen):**

```text
author Thinking
  → freeze-review-loop (same session) → mechanical stamp
  → independent freeze review (optional folklore unless the operator appends freeze_review)
  → adversarial freeze (this gate, when suggest|require)
  → Auto build
  → build-verification
  → ISR (when warn|require)
  → ROADMAP DONE
```

Independent freeze review and adversarial freeze MAY run in the same second
chat **only if** that chat is not the author session. They remain different
postures and different ledger kinds. A chat MUST NOT append
`adversarial_freeze` `pass` and then start Auto in that same chat — Auto is a
fresh session after the gate clears (`ok next` then emits Auto).

---

## §AFF.4 — Config: `honesty.adversarial_freeze` (frozen)

### §AFF.4.1 — Key, vocabulary, HONESTY_KEYS

Additive honesty key. Unknown-key fail-closed still applies
(`adapters/config.py:773-775`).

```yaml
honesty:
  adversarial_freeze: suggest   # off | suggest | require
```

Closed vocabulary (frozen): `off` | `suggest` | `require`. Any other value →
`ConfigError` exit `2`, message names the key.

Auto MUST add `adversarial_freeze` to `HONESTY_KEYS` in
`adapters/config.py`. Omitting that frozenset update would reject a valid
config as `unknown honesty keys`.

Do **not** reuse `L1_EVIDENCE_MODES` (`off|warn|require`). Frozen new
constant:

```text
ADVERSARIAL_FREEZE_MODES = frozenset({"off", "suggest", "require"})
```

in `adapters/config.py` next to `L1_EVIDENCE_MODES`.

Auto MUST add `adversarial_freeze: str = "suggest"` to `HonestyConfig`.
The dataclass default matches the common derived default (SPEC
`human_escalation` example includes `security`). Parse, not the dataclass,
is authoritative for a real config file.

### §AFF.4.2 — Derived default (frozen)

When the key is **absent**:

| `freeze_contract.human_escalation` contains token `security` | Resolved mode |
| --- | --- |
| yes | `suggest` |
| no | `off` |

`require` is **never** derived. Operator-opt-in: the key must be present and
equal to `require`.

When the key is **present**, use it. Derivation does not override an explicit
`off` even if `security` is in `human_escalation`.

Parse wiring (frozen): `_parse_honesty` today does not see
`human_escalation` (`adapters/config.py:432-442` parse escalation, then
`:442` `_parse_k9_modules(raw, path)`). Auto MUST pass the already-validated
escalation list into honesty parse. Do **not** re-open `freeze_contract`
inside honesty parse. Do **not** default-derive by reading a second file.

Empty `human_escalation` list → absent key resolves `off`.

`freeze_contract.enabled: false` does not skip derivation: the escalation
list still exists and still decides the absent-key default.

### §AFF.4.3 — Mode semantics (frozen)

| Mode | `ok next` after FRV would emit Auto | Status / governance-sync | Mode E miss | Skip ledger |
| --- | --- | --- | --- | --- |
| `off` | FRV behavior unchanged | Probe skips (JSON key absent) | Match dimension always `0` if Mode E is invoked | Skip does not authorize (and is unnecessary) |
| `suggest` | Hold Auto; emit adversarial Thinking paste until pass **or** skip | Warn surface; `--exit-code` stays non-failing for this gate | `0` + warning | A latest skip authorizes for its path/digest until a later verdict supersedes it |
| `require` | Hold Auto; emit adversarial Thinking paste until pass. Skip does **not** authorize | Fail-closed: fold into existing exit `2` like ISR require | exit `40` + token `missing_adversarial_freeze` | Inert if present; does not authorize |

`suggest` **holds Auto**. That is the difference from ISR `warn`. Naming it
`warn` would teach the wrong lesson.

**Honesty-module bypass (ADV3-M1; frozen):** `honesty.enabled: false` is a
NEXT bypass for **both** Trigger A and Trigger B, evaluated **before** any
AFF probe, even when the resolved `adversarial_freeze` mode is an explicit
or derived `suggest` or `require`. Status and governance-sync already skip
when honesty is disabled. Helper state is `off`. Helper `off` is never a
hold and is never mapped to `pending`. Mode E with the module disabled
remains exit `4` (`refused`); that explicit query is not a NEXT bypass.

### §AFF.4.4 — Kit dogfood vs shipped consumers (AFF-b writes)

| Repo | What AFF-b writes |
| --- | --- |
| Kit `.overseer/config.yaml` | Explicit `adversarial_freeze: suggest` (not `require`) |
| Consumer init template | Key **absent** (derived default applies) |
| This Thinking phase | **No** config write |

---

## §AFF.5 — Ledger kind `adversarial_freeze` (frozen schema)

**Additive amendment of the K9a / FRV entry-kind enum:** add **exactly one**
new value. Every prior kind's required fields and semantics stay
byte-identical apart from the shared envelope/exact-integer hardening frozen
below. Auto must extend `ENTRY_KINDS` in `tools/honesty/types.py`
and the matching `validate_append_body` branches — no second ledger, no
renumbering.

```text
adversarial_freeze
```

**Envelope (strict K9a / P0 rules, hardened by ADV4-M1):** every stored entry,
including genesis, carries `v: 1` where `type(v) is int` (JSON/Python boolean
is rejected), and `ts` as a string whose `strip()` is non-empty. Every
non-genesis entry also carries `kind`, `prev_hash` / `entry_hash` (server
fills), `actor_role`, `actor_session_id`, and optional
`provenance`.

AFF-b MUST harden both shared boundaries rather than rely on AFF-kind schema
alone:

1. `validate_append_body` rejects a supplied `v` unless `type(v) is int` and
   `v == 1` (exit `2`). A client may omit `ts` for server fill; if supplied,
   `ts` MUST be a string whose `strip()` is non-empty or append exits `2`.
   The server's `_finalize_entry` fills `ts` only when it is omitted, before
   hashing.
2. `verify_chain` checks every stored entry, genesis included, before hash or
   provenance acceptance: `type(entry.get("v")) is int`, value exactly `1`,
   and `ts` is a string whose `strip()` is non-empty. Missing/blank/non-string
   `ts`, boolean `v`, or otherwise invalid `v` are ledger breakage (exit
   `22`), even when the attacker recomputed a matching
   `entry_hash`.

This is shared envelope validation only. `verify_chain` does not re-run each
kind's body schema; the AFF resolver remains the defensive kind-schema
boundary for `phase_id`, `round`, `reviewer_model`, role, posture, sessions,
path, digest, and verdict.

**Shared exact-round repair (ADV4-M2):** AFF-b MUST replace every
`validate_append_body` positive-integer round check with one shared exact-type
rule: `type(round) is int and round >= 1`. This applies to the existing
`verification_evidence`, `independent_second_review`, and `freeze_review`
branches as well as new `adversarial_freeze` pass/findings/blocked/skip
bodies. It changes no other schema or semantics; it only rejects JSON/Python
booleans that the existing `isinstance(round, int)` checks admit.

**Genesis forbid-list:** Auto MUST add the new kind-specific keys to the
genesis forbid list in `validate_append_body` (`tools/honesty/validate.py:228-256`).

### §AFF.5.1 — Closed verdict vocabulary

```text
AFF_VERDICTS = frozenset({"pass", "findings", "blocked", "skip"})
```

in `tools/honesty/types.py` next to `FREEZE_VERDICTS`. Any other
`aff_verdict` → exit `2`.

`findings` / `blocked` never authorize Auto. Every completed adversarial
review appends its actual verdict; a reviewer MUST NOT omit a negative verdict
and leave an older pass live. A later `pass` is a new append (new `round`). For
one match subject, ledger file order is authoritative: the latest eligible
`pass|findings|blocked|skip` entry is the verdict. Therefore a later
`findings` or `blocked` entry revokes an older pass for the same subject and
digest until a still-later pass is appended.

### §AFF.5.2 — Pass body (attack posture)

**Role rule:** `actor_role` MUST be `verifier`. Any other role → exit `23`.

**Independence invariant (frozen, enforced at append — unlike `freeze_review`):**

1. `producer_session_id` is a **required** opaque non-empty string (author
   freeze-review-loop session / nonce).
2. `actor_session_id` is the adversarial reviewer's session.
3. If `actor_session_id == producer_session_id` → exit `2`. The author cannot
   honestly append their own adversarial pass.
4. The kit does **not** invent, scrape, or infer either id.

**Kind-specific required fields (pass / findings / blocked):**

| Field | Type | Rule |
| --- | --- | --- |
| `phase_id` | non-empty string | Opaque, required at append. Recommended value: freeze-block `phase:` (here `AFF`) so `{id}-a` and `{id}-b` share one id. **Not** the Auto-hold match key (§AFF.5.5). |
| `frozen_spec` | non-empty string | Opaque path-shaped string. Append checks **non-empty string only** — no must-exist (same as §PE.3 / §ISR.3). |
| `round` | exact integer ≥ 1 | `type(round) is not int` (including JSON/Python boolean) or `< 1` → exit `2`. |
| `aff_verdict` | string enum | `pass` \| `findings` \| `blocked` for this body. |
| `aff_posture` | string enum | Closed: `attack`. Any other value → exit `2`. |
| `artifact_digest` | string | `sha256:` + 64 lowercase hex. Same shape as `freeze_review` (`validate.py:387-388`). |
| `producer_session_id` | non-empty string | Author nonce. Empty / missing / non-string → exit `2`. |
| `reviewer_model` | non-empty string | Label, never a vendor slug. **Required** on pass/findings/blocked (missing, empty, or non-string → exit `2`). This is the only optionality rule: the field is recorded, not optional. Equal to an optional `producer_model` is **allowed**. Inequality is preference, never a gate. Skip does not carry this field. |

**Optional fields (pass / findings / blocked):**

| Field | Type | Rule |
| --- | --- | --- |
| `producer_model` | string | Opaque label. When **both** `producer_model` and `reviewer_model` are present and equal → still accept. Paste prefers inequality; kit does not gate it. |
| `producer_agent_id` / `verifier_agent_id` | string | Same inequality rule as ISR when **both** present. One present, one absent → allowed. |
| `bound_freeze_review_hash` | string | Optional `entry_hash` of a `freeze_review` line. Auto v1 does **not** require or resolve this at match time (FRV remains a separate gate). If present: non-empty string; no live ledger lookup at append. |
| `notes` | string | Advisory; never a substitute for independence or for attack posture. |
| `side_check_path` | string | Optional path-shaped string for a Check-OK file under `docs/reviews/`. Opaque at append (no must-exist). Never authorizes by itself. |
| `provenance` | object | Optional; identical to P0 rules. |

### §AFF.5.3 — Skip body (operator skip ledger)

Used only to record "operator skipped adversarial freeze once" under
`suggest`.

**Role rule:** `actor_role` MUST be `owner`. Any other role → exit `23`.

**Required fields:**

| Field | Type | Rule |
| --- | --- | --- |
| `phase_id` | non-empty string | Same as pass. |
| `frozen_spec` | non-empty string | Same as pass. |
| `round` | exact integer ≥ 1 | Same exact-type rule as pass; boolean is rejected. |
| `aff_verdict` | string | Must be `skip`. |
| `artifact_digest` | string | Same digest shape as pass. Skip of digest D does not cover digest D′. |

**Forbidden on skip:** `aff_posture`, `producer_session_id` (skip is not a
second-session review). If either is present → exit `2`.

**Optional:** `notes`, `provenance`.

Skip is structurally valid at append **regardless of config** (validate stays
config-free, same as ISR). Authorization honors skip **only** when resolved
mode is `suggest` (§AFF.4.3). Under `require`, a skip line is inert. Under
`off`, skip is inert.

**Last-verdict-wins:** skip participates in the one §AFF.5.5 resolver with
`pass`, `findings`, and `blocked`; it is not resolved in a skip-only scan. Two
skips for the same `(frozen_spec, artifact_digest)` are both structurally
valid and the later eligible entry wins. Process says "once"; the kit does
not refuse a second skip append. `phase_id` is stored but is not the
Auto-hold authorization key.

### §AFF.5.4 — Example pass (normative shape, illustrative ids)

```json
{
  "v": 1,
  "kind": "adversarial_freeze",
  "actor_role": "verifier",
  "actor_session_id": "adversarial-chat-2",
  "phase_id": "AFF",
  "frozen_spec": "docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md",
  "round": 1,
  "aff_verdict": "pass",
  "aff_posture": "attack",
  "artifact_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "producer_session_id": "aff-a-author-session",
  "reviewer_model": "thinking-high"
}
```

### §AFF.5.5 — Match helper (frozen)

New functions in `tools/honesty/validate.py`:

```text
find_latest_adversarial_freeze_verdict(
    entries, *, frozen_spec: str, artifact_digest: str,
    phase_id: str | None = None, producer_session: str | None = None,
) -> dict | None

find_matching_adversarial_freeze_pass(
    entries, *, frozen_spec: str, artifact_digest: str,
    phase_id: str | None = None, producer_session: str | None = None,
) -> dict | None

find_matching_adversarial_freeze_skip(
    entries, *, frozen_spec: str, artifact_digest: str,
    phase_id: str | None = None,
) -> dict | None
```

`find_latest_adversarial_freeze_verdict` is the **only scanner**. The pass and
skip helpers are narrow wrappers over its result: the pass wrapper returns
the winner only when `aff_verdict == pass`; the skip wrapper returns it only
when `aff_verdict == skip`; otherwise each returns `None`. Neither wrapper may
filter ledger entries by verdict before the latest entry is selected. The
authorization helper in §AFF.5.6 MUST call the latest-verdict resolver once,
not call the pass and skip wrappers independently.

Auto-hold / status omit `phase_id` and `producer_session`. Mode E may pass
them as pins (`phase_id` on every verdict; `producer_session` on
`pass|findings|blocked` only). Skip ignores the producer pin because its body
forbids `producer_session_id`.

**Auto-hold / status probe match (frozen):** `frozen_spec` + `artifact_digest`
of the freeze candidate file. `phase_id` is **not** part of this match.
That is the FRV-r4 repair for this gate: a pass recorded during `{id}-a`
still clears `{id}-b` Auto if the file path and digest still match.

A ledger entry is **eligible** for Auto-hold subject
`(frozen_spec, artifact_digest)` when every applicable rule below holds.
The resolver scans ledger file order and returns the **last eligible entry
across all four verdicts**. An ineligible line is skipped; it cannot win
and cannot authorize, including when `verify_chain` returns `0` (ADV3-M3).

1. `kind == adversarial_freeze`
2. for `pass|findings|blocked`: `actor_role == verifier`
3. `aff_verdict` is one of `pass|findings|blocked|skip`
4. for `pass|findings|blocked`: `aff_posture == attack`
5. `frozen_spec` equals the candidate's repo-relative path (POSIX)
6. `artifact_digest` equals the candidate's current digest (required)
7. for `pass|findings|blocked`: both session ids are non-empty strings and
   `actor_session_id != producer_session_id`
8. for `skip`: `actor_role == owner`, and both `aff_posture` and
   `producer_session_id` are absent
9. `phase_id` is a non-empty string (`isinstance(str)` and `str.strip()`
   non-empty). Applies to all four verdicts.
10. `round` is an exact integer ≥ 1 (`type(round) is int` and `>= 1`; the
    same rule as `validate_append_body`). JSON/Python boolean is ineligible.
    Applies to all four verdicts.
11. for `pass|findings|blocked`: `reviewer_model` is a non-empty string
    (same rule as `phase_id`). Skip does not carry this field.

Append validation remains the primary schema boundary; these checks are
defensive so a malformed historical line cannot authorize. `verify_chain`
confirms the strict common envelope, hashes, and provenance but does **not**
re-run kind schema validation; eligibility rules 9–11 are the fail-closed
AFF schema defense.

A latest winner authorizes as follows:

| Latest winner | `suggest` | `require` | `off` |
| --- | --- | --- | --- |
| `pass` | authorize | authorize | gate not evaluated |
| `skip` | authorize | pending | gate not evaluated |
| `findings` / `blocked` | pending; older pass revoked | pending; older pass revoked | gate not evaluated |
| none | pending | pending | gate not evaluated |

**Mode E match** adds optional pins before latest selection: if the caller
supplies `phase_id`, it must equal the entry's `phase_id`; if the caller
supplies `producer_session`, rule 12 applies to `pass|findings|blocked` while
skip **ignores** `producer_session` (R1-M3).

Mode E extra pin for `pass|findings|blocked` when `producer_session` is
supplied:

12. `producer_session_id` equals the caller value **and** `actor_session_id`
    differs from that value.

Does not open a network connection, call a model, or read IDE session ids.

### §AFF.5.6 — Shared authorization helper (frozen)

New module `tools/adversarial_freeze/` (ISR-shaped; not folded into
`tools/freeze_authorization/resolve.py`).

`adversarial_authorization_state(repo_root, artifact_path, *, config)`
returns a frozen dataclass.

It hashes `artifact_path` with the same `artifact_digest()` FRV uses
(`tools/freeze_reviewer/artifact.py:150-154`) and matches on that digest plus
the repo-relative POSIX path. It does **not** take `phase_id` for the Auto-hold
match (R1-M1). Mode E may call the validate helper with extra pins.

| `state` | Meaning |
| --- | --- |
| `off` | Mode `off` or honesty disabled — not a hold. Callers MUST treat this as a bypass, never as Trigger A's "otherwise hold" fallthrough and never as Trigger B pending. |
| `pass` | Latest eligible verdict is pass |
| `skipped` | Latest eligible verdict is skip and mode is `suggest` |
| `pending` | Mode `suggest` or `require`, and the latest eligible verdict is `findings`, `blocked`, a non-authorizing skip, or none. **Never** assigned for honesty disabled or mode `off`. |
| `absent` | Fail-closed read error (broken chain, unreadable artifact) — treat as hold when mode is `suggest` or `require` |

Do **not** change `AuthState` in `tools/freeze_authorization/resolve.py`.
FRV `substantive` stays "freeze_review matched". AFF is a second question.
The helper verifies the full ledger chain/provenance before resolving, calls
`find_latest_adversarial_freeze_verdict` exactly once, and maps that winner by
the table above. It never separately asks "is there any pass?" and "is there
any skip?" because that would resurrect an older favorable entry after a
later negative verdict.

Candidate discovery reuses `discover_freeze_candidates`
(`next_regen.py:415-459`) — top-level `docs/PHASE-*.md` **and**
backtick-cited `docs/…/*.md` paths in the row deliverable. Archive freezes
(this artifact lives under `docs/archive/phases/`) are reached **only** via
the deliverable citation (R1-N1). AFF-b's roadmap deliverable MUST cite
this path in backticks.

Named helpers in `tools/adversarial_freeze/` (frozen; shared by NEXT and
status so the two surfaces cannot drift):

```text
aff_hold_bypassed(config) -> bool
  True when honesty.enabled is false OR resolved adversarial_freeze is off.

frv_authorizing_freeze_paths(repo_root, candidates, *, phase_id, config)
  -> list[Path]
  Discover-order paths whose freeze_authorization_state is substantive.
  This is Trigger A's candidate subset and the status/governance-sync
  probe subset (ADV3-M2).

aggregate_adversarial_authorization_states(states) -> str
  Worst-state aggregate over pass|skipped|pending|absent. Frozen rank
  (worst first): absent > pending > skipped > pass. Empty input is not
  called (probe skip). Helper off is dropped before aggregation; if none
  remain, treat as bypass / probe skip, never pending.
```

---

## §AFF.6 — Author freeze-review-loop MUST NOT set `auto_may_start: true`

### §AFF.6.1 — Skill contract (AFF-b edits `cursor/skills/` source only)

Amend `cursor/skills/freeze-review-loop/SKILL.md` (live `.cursor/` / `.claude/`
copies via `ok sync --yes`, same as ISR-r2 / R2-N2):

1. On pass (today `:60-62`): write the Review-record row and finish all
   artifact edits **before** running `ok review --freeze`; then stamp the
   final bytes. Never update the Review record after stamping without
   immediately restamping. This is the author-loop half of §AFF.7.4.
2. **MUST NOT** write, insert, or flip `auto_may_start` to `true`.
3. **MUST NOT** write `auto_may_start` at all (FRV: kit never writes the key;
   the skill is not a back door).
4. **MUST NOT** append `adversarial_freeze` `pass` in the author session.
5. **MUST NOT** claim Auto is cleared. Replace "EXIT success" with: stop.
   Print that `ok next` will emit the adversarial paste when
   `honesty.adversarial_freeze` is `suggest` or `require`. Invent / copy a
   `producer_session` nonce into the handover NEXT block.
6. Appending `freeze_review` in the author session remains **allowed**
   (independent freeze review / FRV substantive record). It does **not**
   satisfy AFF.

Amend `cursor/skills/freeze-review/SKILL.md` with the §AFF.3 table and a
pointer to `/adversarial-freeze-review`.

Amend `cursor/rules/check-ok-thinking.mdc:21`: freeze `pass` is the author
loop, not Auto-cleared, when AFF is `suggest` or `require`.

### §AFF.6.2 — `auto_may_start` semantics unchanged (FRV)

AFF does not amend FRV §FRV.8:

| Value | Effect (still) |
| --- | --- |
| absent | No effect |
| `true` | No effect (cannot grant) |
| `false` | `blocked_by_operator` — outranks freeze_review **and** adversarial pass |
| non-boolean | Fail-closed block |

Tests under §AFF.14 must prove the skill/docs prohibition **and** that
`next_regen` does not emit Auto from author-loop success alone when AFF is
on. They must not re-open FRV's grant-path prohibition as a redesign.

---

## §AFF.7 — `ok next` emits adversarial Thinking paste (frozen)

### §AFF.7.1 — When the hold applies

Apply AFF in `plan_next_regen` **after** `decide_split_emission`
(`next_regen.py:544-557`), not only inside it. Thinking-only rows return
early at `next_regen.py:475-476` and would otherwise never see the gate
(R1-M2).

`aff_hold_bypassed(config)` → no hold, FRV/Thinking emission unchanged.
That is true for resolved mode `off` **and** for `honesty.enabled: false`,
even when the resolved AFF mode is an explicit or derived `suggest` or
`require` (ADV3-M1). Evaluate this bypass **before** Trigger A or Trigger B
probes. `Operator + Auto` → no hold.

Helper `off` is never `pending`. If a probe still receives `off` after the
bypass, Trigger A treats it as cleared and Trigger B does not rewrite the
paste.

**Trigger A — FRV would emit Auto** (`emit_model == "Auto"` or
`is_step_b is True`):

1. If `aff_hold_bypassed(config)`, stop: emit Auto as FRV would.
2. Collect the same freeze candidates FRV used (`discover_freeze_candidates`).
3. If there are **no** candidates, AFF does not hold (FRV already emits Auto
   with nothing to bind — `next_regen.py:482-483`). Do not invent a freeze.
4. Restrict to `frv_authorizing_freeze_paths` (FRV `state == substantive`).
   If that subset is empty, AFF does not hold.
5. For every path in that subset, run `adversarial_authorization_state`
   (path + digest).
6. If every such candidate is `pass`, or (mode `suggest` and `skipped`),
   or `off`, emit Auto as FRV would. Advisory `adversarial_freeze_skip`
   when at least one candidate authorized via skip.
7. Otherwise hold (`pending` or `absent` only): `emit_model = "Thinking"`,
   `is_step_b = False`, `reason = None` (still regenerate), `advisory =
   ADVISORY_ADVERSARIAL_FREEZE_PENDING` (`"adversarial_freeze_pending"`).

**Trigger B — author freeze-review-loop complete, Auto not yet the emission**
(open row Model is `Thinking`, or `Thinking → Auto` emitting `{step}a` /
Thinking):

1. If `aff_hold_bypassed(config)`, do not hold (keep the author freeze paste).
2. Collect freeze candidates for that row.
3. If none, do not hold (still drafting; keep the author freeze paste).
4. Author-loop complete when **any** candidate satisfies the Trigger-B
   fresh-stamp predicate below. `absent` / `non_pass` /
   `blocked_by_operator` → not complete.
5. If complete and any completed candidate's AFF state is `pending` or
   `absent`, hold with the same Thinking + `adversarial_freeze_pending`
   paste as Trigger A.
6. If complete and every completed candidate is `pass`, `skipped`, or
   `off`, do **not** rewrite the paste into Auto (the row is still
   Thinking). Leave FRV/Thinking emission. Operator marks the Thinking row
   DONE; the next row is Auto, which is Trigger A.

**Trigger-B fresh-stamp predicate (ADV2-M1; Trigger-B only):**

A candidate is author-loop complete when the matching row below is **yes**:

| FRV `state` | Additional required check | Complete? |
| --- | --- | --- |
| `substantive` | None. FRV already matched `freeze_review` to the current digest. | yes |
| `mechanical_only` | Fresh-stamp: `extract_existing_stamp(parsed)["artifact_digest"]` is a well-formed `sha256:` + 64 lowercase hex string **and** equals the current `artifact_digest(parsed)` computed by FRV `tools/freeze_reviewer/artifact.py:150-154`. | yes only when the equality holds |
| `mechanical_only` | Stamp digest missing, not a string, malformed, or unequal to the current digest (post-stamp byte edit outside `review_stamp`). | **no** — keep the author freeze paste |
| any other state | — | no |

Do **not** change `AuthState` or `freeze_authorization_state`
(`tools/freeze_authorization/resolve.py`). A stale mechanical stamp may
still resolve `mechanical_only` for FRV. That FRV result still cannot
authorize Auto (`substantive` remains the only Auto authorizer). Trigger B
must not treat that stale `mechanical_only` as author-loop complete.

Auto implements the predicate as
`author_loop_complete(frv_state, *, stamp_digest, current_digest) -> bool`
in `tools/adversarial_freeze/` (not in `tools/freeze_authorization/`).
`next_regen` Trigger B calls that helper after `freeze_authorization_state`.
It never remaps FRV `mechanical_only` to `absent` and never consults the
stamp digest when deciding FRV Auto emission.

Do **not** reuse `REASON_FREEZE_NOT_SUBSTANTIVE` — that fails regen. AFF
pending **must** still print NEXT.

### §AFF.7.2 — Paste body when advisory is `adversarial_freeze_pending`

`render_paste_ready` (`next_regen.py:653-700`) currently dumps the roadmap
deliverable. When `decision.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING`,
Auto MUST render the frozen AFF paste instead of the Auto-deliverable list.

Frozen paste requirements (all must appear in the fence body):

- `Model: Thinking`
- Attack posture: try to **kill** the spec; do not rubber-stamp close
- Different chat from the author; if this is the author session, stop
- Prefer a different model than the author (preference, not a kit gate)
- Read the freeze artifact path
- Cite every finding `path:line`
- Follow the mandatory Review-record/restamp/FRV-rebind/AFF-append transaction
  in §AFF.7.4; no ledger verdict is written before the artifact is final
- On pass: append `adversarial_freeze` with the §AFF.5.2 fields only as the
  final transaction step, including `aff_posture: attack` and
  `producer_session_id: <AUTHOR_PRODUCER_SESSION_NONCE>` (`next_regen` v1
  emits that placeholder; it does **not** scrape IDE session ids — same rule
  as ISR)
- On findings/blocked: append that actual verdict as the final transaction
  step; never append `pass`, and never omit the negative append merely to
  preserve an older pass for the same subject/digest
- Under `suggest`, operator skip is a separate owner append (`aff_verdict:
  skip`) — the reviewer chat does not skip for the operator
- Kit performs no model call and holds no key
- No merge to `main`

`render_next_session` heading stays the open row's title. `**Model:**
Thinking`. THE ONE NEXT STEP text MUST say adversarial freeze, not Auto
build.

`ok next` stdout layout (ONS/NXP twelve-step provenance) is unchanged. Only
the fence body and Model label change.

### §AFF.7.3 — Side-check (what "exists with substantive pass" means)

Authoritative side-check = matching `adversarial_freeze` ledger **pass**
(§AFF.5.5), or matching **skip** under `suggest`.

A `docs/reviews/<date>-<phase_id>-adversarial-freeze.md` Check-OK file is
**optional evidence** (`side_check_path`). It does **not** authorize Auto.
It does **not** itself require AFF (no recursion). Mechanical stamp on that
file does not authorize anything.

The freeze artifact's Review-record table MUST gain an adversarial round row
before any digest-bound ledger append. That row is review history, not the
gate; its bytes do participate in the artifact digest.

### §AFF.7.4 — Review-record / restamp / rebind / append transaction

This is a narrow AFF supersession of FRV §FRV.9.3 steps 2–4 whenever the
Review-record row is being added: the row must precede the stamp whose digest
the ledger records.

For every completed adversarial round after AFF-b exists, the reviewer MUST
perform this exact order. It applies to `pass`, `findings`, and `blocked`:

1. Finish the review and decide the verdict **without** appending an AFF
   ledger entry.
2. Write the adversarial round, verdict, and cited finding/resolution summary
   into the freeze artifact's Review-record table. Complete every other edit
   to that artifact now.
3. Run `ok review --freeze <artifact>` and require mechanical pass. Recompute
   with FRV `artifact_digest()` and require the stamp's `artifact_digest` to
   equal the current value `D`. Because `review_stamp` is excluded from the
   canonical bytes, this restamp MUST leave `D` unchanged.
4. If Auto requires FRV authorization, append a new `freeze_review` pass for
   the same repo-relative `frozen_spec` and `artifact_digest: D`. This step is
   mandatory when a previous `freeze_review` pass was bound to the pre-row
   digest; the old entry is historical and cannot be reused. Its `phase_id`
   remains FRV's compact id for the Auto row being authorized. Verify the
   ledger after the append before continuing.
5. Append exactly one `adversarial_freeze` entry carrying the round's actual
   `pass|findings|blocked` verdict, the same `frozen_spec`, and
   `artifact_digest: D`. This is the final binding operation. Verify the
   ledger again.
6. Do not edit the freeze artifact after step 5. Any later byte change outside
   `review_stamp` invalidates both bindings and requires restarting at step 2:
   update the Review record, restamp, rebind FRV when required, then append a
   fresh AFF verdict for the new digest.

`ok next`, active-slice status, and Mode E may authorize only when their
independently computed current path/digest select the latest AFF verdict and,
where Auto requires it, FRV independently selects `freeze_review` for that
same current digest. They MUST NOT treat the AFF append as repairing a stale
FRV binding or vice versa.

**AFF-a bootstrap exception:** AFF-a is freezing the kind before AFF-b creates
it. Its fresh adversarial reviewer records the Review-record row before the
final restamp and may append/rebind existing `freeze_review`, but MUST NOT
append the nonexistent `adversarial_freeze` kind. The different-chat Review
record is sufficient only to close the AFF-a Thinking freeze and queue AFF-b;
it is not a runtime AFF authorization and does not waive FRV for AFF-b.

---

## §AFF.8 — Honesty-status Mode E (frozen)

### §AFF.8.1 — Flag

Additive flag on `ok honesty-status`:

```text
--adversarial-freeze PHASE_ID
```

Shared optional `--producer-session` / `--frozen-spec` (same as Mode D).
Optional Mode-E-only metadata `--artifact-digest DIGEST`. It never selects a
mode by itself and is invalid unless both `--adversarial-freeze` and
`--frozen-spec` are present. Digest/path resolution (R1-N2, R2-N1, ADV1-N1):

1. If `--frozen-spec` is supplied, confine it under the repo and normalize it
   to the repo-relative POSIX path used by the ledger. Path escape or a
   confine/`stat` I/O error is refusal `4`; no ledger match runs. A
   successful `stat` of an existing non-regular path is not an I/O error.
2. If `--artifact-digest` is supplied, it must match `sha256:` + 64 lowercase
   hex or the invocation is usage `1`. It is the effective digest.
3. When both flags are supplied and the confined path is an existing readable
   regular file, hash it with FRV `artifact_digest()`; unequal flag/file
   digests are usage `1` (caller contradiction). When the confined path is
   absent, the explicit digest remains usable for this explicit ledger query.
4. When both flags are supplied and the confined path **exists and is not a
   readable regular file** (directory, fifo, socket, device, or other
   non-regular): do **not** hash it, do **not** emit usage `1`, and do **not**
   emit refusal `4` unless confine/stat itself failed. The confined
   repo-relative POSIX path plus the valid explicit digest remain usable for
   this explicit ledger query — the same query class as an absent path
   (ADV2-N1). Classify with a successful `stat` after confine; do not open the
   path as a freeze artifact.
5. Without `--artifact-digest`, an existing readable `--frozen-spec` file is
   hashed with FRV `artifact_digest()` and supplies the effective digest.
6. Without an effective path or digest, Mode E is a fail-closed **miss**. A
   missing/non-file `--frozen-spec` without an explicit digest is also a miss
   (this includes an existing non-regular path without `--artifact-digest`).
   There is no "last pass for phase regardless of digest" shortcut.

Complete flag matrix:

| Invocation shape | Result |
| --- | --- |
| No `--adversarial-freeze`, no `--artifact-digest` | Pre-AFF Mode A/B/C/D resolution, byte-identical |
| `--artifact-digest` without `--adversarial-freeze` (alone or with A/B/C/D) | usage `1`; never silently ignored |
| `--adversarial-freeze` plus any Mode A core or B/C/D selector | usage `1` |
| `--adversarial-freeze` alone, or plus only `--producer-session` | Mode E; forced miss because effective path/digest are null |
| `--adversarial-freeze --frozen-spec PATH` | Mode E; hash readable file, otherwise fail-closed miss (path escape/I/O → `4`) |
| `--adversarial-freeze --frozen-spec PATH --artifact-digest D` | Mode E when `D` is valid and agrees with a readable existing file; absent file may be queried by normalized path + explicit `D` |
| `--adversarial-freeze --frozen-spec PATH --artifact-digest D` where PATH exists and is not a readable regular file, `D` valid | Mode E; explicit ledger query by confined POSIX path + `D`; no hash; not usage `1`; not refusal `4` |
| `--adversarial-freeze --artifact-digest D` without `--frozen-spec` | usage `1` |
| Any supplied malformed digest, or flag/file digest mismatch | usage `1` |

### §AFF.8.2 — Mode-resolution algorithm (amends §ISR.5.2)

Replace the Mode B/C/D mutex with B/C/D/E. `--producer-session` is shared
metadata for Mode A (optional), Mode D (optional), and Mode E (optional).
It does **not** by itself imply Mode A when Mode D or E is selected.

Normative pseudocode:

```text
mode_a_core    = hook or artifact
mode_a_full    = hook and artifact
mode_b_full    = verification_evidence is set
mode_c_full    = deploy_health is set
mode_d_full    = independent_second_review is set
mode_e_full    = adversarial_freeze is set
frozen         = frozen_spec is set
producer       = producer_session is set
digest          = artifact_digest is set

mode_a_partial = mode_a_core or (producer and not mode_d_full and not mode_e_full)

if digest and not mode_e_full:
    return None
if mode_e_full and digest and not frozen:
    return None
if (mode_b_full + mode_c_full + mode_d_full + mode_e_full) > 1:
    return None
if mode_a_partial and (mode_b_full or mode_c_full or mode_d_full or mode_e_full or frozen):
    return None
if frozen and not mode_b_full and not mode_c_full and not mode_d_full and not mode_e_full:
    return None
if not mode_a_full and not mode_b_full and not mode_c_full and not mode_d_full and not mode_e_full:
    return None
if mode_e_full:
    return "mode_e"
if mode_d_full:
    return "mode_d"
if mode_c_full:
    return "mode_c"
if mode_b_full:
    return "mode_b"
return "mode_a"
```

**Invariants (frozen):**

1. `--adversarial-freeze PHASE --frozen-spec PATH` → `mode_e`.
2. `--adversarial-freeze PHASE --producer-session ID` → `mode_e`.
3. `--adversarial-freeze PHASE --producer-session ID --frozen-spec PATH` → `mode_e`.
4. `--adversarial-freeze PHASE` alone → `mode_e`.
5. `--adversarial-freeze PHASE --artifact-digest D` without
   `--frozen-spec` → usage `1`.
6. `--artifact-digest D` without `--adversarial-freeze` → usage `1`, with
   any other flags or alone.
7. `--adversarial-freeze PHASE --independent-second-review PHASE` → usage `1`.
8. `--hook H --artifact P --adversarial-freeze PHASE` → usage `1`.
9. When both AFF flags are absent, Mode A/B/C/D behavior is **byte-identical**
   to pre-AFF for every invocation that passes neither
   `--adversarial-freeze` nor `--artifact-digest`.
10. Pre-ISR invariants 5–8 remain true when both AFF flags are absent.
11. `--adversarial-freeze PHASE --frozen-spec PATH --artifact-digest D`
    when PATH exists and is not a readable regular file → `mode_e` (not
    usage), provided `D` is well-formed. Effective path is the confined
    POSIX path; effective digest is `D`.

`HonestyStatusOptions` gains `adversarial_freeze: str | None = None` and
`artifact_digest: str | None = None`.

### §AFF.8.3 — JSON + error token

`HonestyErrorToken` gains `missing_adversarial_freeze`.

`HonestyStatusJson` gains optional `adversarial_freeze: dict | None`. A valid
Mode E invocation always emits the block below; a valid Mode A/B/C/D
invocation omits it. In valid Mode E, the other optional mode blocks
`verification_evidence`, `deploy_health`, and `independent_second_review` are
all absent (not JSON `null`). Mode-A top-level fields remain present and are
fixed as shown:

```json
{
  "ok": true,
  "exit_code": 0,
  "command": "honesty-status",
  "hook": null,
  "artifact": null,
  "artifact_sha256": null,
  "producer_session": null,
  "matched_verdict_hash": null,
  "error": null,
  "adversarial_freeze": {
    "phase_id": "AFF",
    "frozen_spec": "docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md",
    "artifact_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "producer_session": null,
    "mode": "suggest",
    "matched_via": "pass",
    "matched_entry_hash": "example-entry-hash"
  }
}
```

Exact nested types/nullability:

| Key | Type | Value |
| --- | --- | --- |
| `phase_id` | string | Exact `--adversarial-freeze` value |
| `frozen_spec` | string or null | Effective confined repo-relative POSIX path, else null |
| `artifact_digest` | string or null | Effective validated/hashed digest, else null |
| `producer_session` | string or null | Exact optional pin |
| `mode` | `off\|suggest\|require` | Resolved config mode |
| `matched_via` | `pass\|skip` or null | Authorizing latest verdict only |
| `matched_entry_hash` | string or null | `entry_hash` of that authorizing verdict only |

The top-level `producer_session` equals the same pin; it is null in the
example only because the flag is absent. `matched_verdict_hash` remains null
because that field belongs to Mode A. A miss, `off`, refusal, chain failure,
or usage result has `matched_via: null` and `matched_entry_hash: null`.

Mode E applies `honesty.adversarial_freeze` per §AFF.4.3:

| Outcome | `ok` | exit | `error` | warning |
| --- | --- | --- | --- | --- |
| `off` | true | `0` | null | none; no ledger match is attempted |
| `suggest`, latest winner is pass/skip | true | `0` | null | none |
| `suggest`, miss/findings/blocked | true | `0` | null | `warning: no authorizing adversarial_freeze entry` |
| `require`, latest winner is pass | true | `0` | null | none |
| `require`, miss/skip/findings/blocked | false | `40` | `missing_adversarial_freeze` | none beyond existing role warning |
| module disabled / path or ledger refusal | false | `4` | `refused` | existing refusal text |

Skip under `suggest` counts as `matched_via: skip`; under `require` it is a
miss. Skip ignores `--producer-session` (R1-M3). A later `findings` or
`blocked` winner produces a miss even when an older matching pass exists.

**Integrity-before-match (ADV1-M2, ADV4-M1):** for `suggest` and `require`, after the
ledger is parsed and before `find_latest_adversarial_freeze_verdict` runs,
Mode E MUST call `verify_chain(entries, regime=config.vcs.regime,
require_agent_signature=config.honesty.require_agent_signature)`. It verifies
the entire non-empty ledger, including the strict `v`/`ts` envelope and
provenance, not merely matching lines.
The resolver is never called on nonzero verification:

| `verify_chain` result | Mode E result |
| --- | --- |
| `22` | exit `22`, `ok: false`, `error: ledger_broken` |
| `2`, `25`, or `26` | preserve that exit, `ok: false`, `error: refused` |

`suggest` does not soften integrity failures to exit `0`; a stored pass in a
tampered chain can never match. Missing/empty ledger is an ordinary miss, not
a chain failure. `off` performs no ledger match and therefore no ledger read.

When `--adversarial-freeze` is present but mode resolution returns usage `1`,
the response is not Mode E: `ok: false`, `error: usage`; its diagnostic
`adversarial_freeze` block uses the supplied `phase_id` and producer pin,
resolved config `mode`, null effective path/digest, and null match fields.
Other explicitly selected B/C/D diagnostic blocks may also be present. A
configuration failure before mode resolution keeps the pre-AFF config-error
JSON shape and omits every optional mode block.

---

## §AFF.9 — Active-slice status / governance-sync surface (frozen)

ISR-shaped (`tools/independent_second_reviewer/surface.py`). New
`tools/adversarial_freeze/surface.py`.

When `honesty.enabled` is true **and** resolved mode is `suggest` or
`require` **and** the active slice is an Auto-authorizable row (plain `Auto`
or `{step}b` after FRV would emit Auto):

- Discover the same freeze candidates Trigger A uses
  (`discover_freeze_candidates`). Empty discovery → probe **skip** (JSON
  key absent); AFF does not apply (Trigger A no-candidate path).
- Restrict the probe to `frv_authorizing_freeze_paths` — the identical
  FRV-authorizing (`substantive`) subset Trigger A probes (ADV3-M2).
  Non-substantive siblings (`mechanical_only`, `absent`, `non_pass`,
  `blocked_by_operator`) are not probed and cannot create a status-only
  hold. Empty authorizing subset → probe **skip**.
- For each path in that subset, run `adversarial_authorization_state`
  (path + digest; not `compact_step_id` as the ledger match key).
- Aggregate those helper states with
  `aggregate_adversarial_authorization_states`. Auto v1 JSON stays a
  single scalar `state`; do not emit a per-candidate payload. Mixed
  outcomes follow the frozen rank `absent > pending > skipped > pass`:
  pass+pending → `pending` (NEXT holds); pass+absent → `absent` (NEXT
  holds); pass+skipped → `skipped` (NEXT Auto + skip advisory); all pass
  → `pass` (NEXT Auto).
- Helper `absent` (broken chain, unreadable artifact) is a **probe result**,
  not a probe skip. `ok next` already holds on `absent`; status and
  governance-sync MUST surface that hold (ADV2-N3).
- `require` + aggregated pending/absent → `ok` false; `ok status --exit-code`
  folds into existing `2` (not `40`). Token
  `missing_adversarial_freeze`.
- `suggest` + aggregated pending → warn line; JSON key present; exit still
  `0` for this gate.
- `suggest` + aggregated absent → warn line that names the read-error hold;
  JSON key **present** (never omitted); exit still `0` for this gate.
- `off` or probe skip (honesty disabled, mode `off`, the slice is not
  Auto-authorizable, no freeze candidates, or empty FRV-authorizing
  subset) → JSON key **absent**. Helper `absent` is not a skip. Helper
  `off` is not a skip-vs-hold conflict: it is a skip.

`ok status` additive JSON key: `adversarial_freeze_gate` (optional; absent
when the probe skips). When the probe runs, the object is:

```json
{
  "ok": true,
  "mode": "suggest",
  "state": "absent",
  "matched": false
}
```

Exact nested fields:

| Key | Type | Value |
| --- | --- | --- |
| `ok` | bool | `false` only for `require` + pending/absent. `true` for `suggest` + pending **and** `suggest` + absent. |
| `mode` | `suggest\|require` | Resolved config mode |
| `state` | `pass\|skipped\|pending\|absent` | Aggregated helper state of the FRV-authorizing subset. Distinguishes pending (no authorizing verdict) from absent (read-error hold). |
| `matched` | bool | `true` only when `state` is `pass` or `skipped` |
| `token` | string, omitted if null | `missing_adversarial_freeze` on `require` + pending/absent only |

Exact warn / footer strings (human line; also the governance-sync footer):

| Outcome | Line |
| --- | --- |
| `suggest` + pending | `warning: no authorizing adversarial_freeze entry for active Auto slice` |
| `suggest` + absent | `warning: adversarial_freeze unreadable (broken ledger or artifact) for active Auto slice` |
| `require` + pending/absent | existing fail-closed message; token `missing_adversarial_freeze`; no additional suggest-style warning |

Governance-sync footer: same probe, ISR-shaped engine-footer path
(`tools/governance_hygiene/engine.py` after the ISR footer, not a new
`ReadFailure` in `reads.py` — ISR-r2 / R2-M1 lesson). The footer MUST
print the `suggest` + absent line when the **aggregated** state is
`absent`; it MUST NOT look like a skipped probe. Mixed candidate sets MUST
agree with `ok next` on hold vs Auto (same subset, same aggregate).

`--exit-code` precedence unchanged: `2 > 6 > 35 > 3 > 0`. AFF require miss
is a `2`. `40` is confined to honesty-status Mode E.

Optional-feature tips: when honesty is on and `adversarial_freeze` resolves
`off`, one tip naming the key and the paste doc (ISR §ISR.7.5 shape).

---

## §AFF.10 — Portable CLI + docs + twin skill (AFF-b)

Primary portable surface: `docs/ADVERSARIAL-FREEZE-REVIEW.md` (ISR twin of
`docs/INDEPENDENT-SECOND-REVIEWER.md`).

Twin skill (edit `cursor/skills/` source only; `ok sync` writes both
`.cursor/skills/` and `.claude/skills/`):

```text
cursor/skills/adversarial-freeze-review/SKILL.md
```

Invoke: **`/adversarial-freeze-review`**. Extending `/freeze-review` with a
new skill is the frozen choice (keep `/freeze-review` as the author/single
pass path; do not overload it with attack posture).

Skill process (frozen):

1. Confirm this session is **not** the author freeze-review-loop session. If
   it is, stop. Do **not** append pass. Do **not** start Auto.
2. Attack posture: try to kill the spec. Re-read the freeze + frozen_inputs.
   Do not trust the author Review-record.
3. Cite every finding `path:line`.
4. For every completed verdict, execute §AFF.7.4 in exact order: write the
   Review-record row; complete artifact edits; restamp and establish final
   digest `D`; rebind required FRV `freeze_review` to `D`; then append the
   actual AFF verdict against `D` as the final binding operation.
5. On pass: append `adversarial_freeze` with `aff_verdict: pass`,
   `aff_posture: attack`, this session as `actor_session_id`, and the author
   nonce as `producer_session_id`. On findings/blocked: append that negative
   verdict, never pass; the latest-verdict rule revokes any older pass for the
   same subject/digest.
6. Any later freeze-artifact edit restarts the full §AFF.7.4 sequence. Never
   claim that an AFF append repaired a stale FRV binding.
7. Never merge to `main`. Never call a model via the kit CLI.

Also amend:

- `cursor/skills/freeze-review-loop/SKILL.md` (§AFF.6.1)
- `cursor/skills/freeze-review/SKILL.md` (§AFF.3 table)
- `cursor/rules/check-ok-thinking.mdc`
- `docs/CHECK-OK.md` (one sentence: author freeze pass ≠ Auto when AFF is on)
- `AGENTS.md` (ISR-shaped short section)
- `docs/consumers/scooling/OVERSEER-SETUP.md`
- `docs/consumers/knowtation/OVERSEER-SETUP.md`

No live consumer `ok init`. No bornfree-hub product edit.

Footprint: new skill files under `cursor/skills/` are picked up by the
existing `resolve_footprint` rglob (`cli/footprint.py:135-155`). No
footprint-resolver redesign.

---

## §AFF.11 — Exit codes (frozen)

Additive code; non-overlapping with existing
`1`, `2`, `4`, `5`, `7`, `8`, `10`–`11`, `20`–`26`, `30`–`39`:

| Code | Meaning | Where |
| --- | --- | --- |
| `40` | Adversarial freeze required but the latest eligible verdict is not pass (or none exists) | `honesty-status` Mode E when `adversarial_freeze: require`; JSON `error` = `missing_adversarial_freeze` |

Constant name (frozen): `EXIT_MISSING_ADVERSARIAL_FREEZE = 40` in
`tools/honesty/status.py`. CLI and tests import that name. Do not reuse
`38` / `39` / `33`.

Reused (no renumbering):

| Code | Reuse |
| --- | --- |
| `1` | Usage — Mode E combined with A/B/C/D or other §AFF.8.2 `None` |
| `2` | Malformed schema; **and** `ok status --exit-code` / governance-sync when the active-slice require probe misses |
| `4` | Honesty module disabled / config refuse |
| `22` | Mode E ledger chain broken; JSON `error` = `ledger_broken` |
| `23` | Role violation (`pass` body `actor_role` ≠ `verifier`; `skip` body ≠ `owner`) |
| `25` / `26` | Mode E provenance failure / required signature absent (P0; unchanged) |
| `39` | FRV stamp escalation — unchanged, not an AFF code |

`40` is confined to honesty-status Mode E. It does not change
`status --exit-code` precedence (`2 > 6 > 35 > 3 > 0`).

---

## §AFF.12 — Boundary, capability, rejection (governance, not runtime)

**The single most important frozen rule:** the kit records and optionally
gates the adversarial-review *claim*. It never runs another model, never
opens a second chat, and never treats host UI as a control surface. A host
may later spawn a second agent; that is **not** a kit feature and **not**
an AFF-b deliverable.

| Concern | Overseer Kit | Operator / host runtime |
| --- | --- | --- |
| Append `adversarial_freeze` | Yes (validate + chain) | Supplies JSON body + session ids |
| Gate Mode E / status / next_regen | Yes (`off`/`suggest`/`require`) | Decides `require` opt-in |
| Open a second chat / composer | **Never** | Yes |
| Dispatch / host / call a reviewer model | **Never** | Yes (Cursor picker, Claude, human, CI agent) |
| Infer session ids from the IDE | **Never** | Supplies opaque strings |
| Spawn a second agent automatically | **Never** (out of kit scope) | Host may, later |
| Write `auto_may_start: true` | **Never** | Operator could hand-edit; it still does not grant Auto |
| Prove chat identity cryptographically | Optional P0 only | Muse / operator |
| Tier-3 merge authorization | **Never** | Operator |
| Consumer product Auto / hub Main deploy | **Never** | Operator |

Capability tiers:

| Capability | `git-only` (baseline) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Record + gate AFF on file ledger | Full | Full (identical) |
| Optional signed `provenance` | Soft (unsigned OK) | Hard when `require_agent_signature: true` (P0) |
| Dispatch a second model | **Not in the kit** | **Not in the kit** |

| Temptation | Verdict |
| --- | --- |
| `ok` shells out to a reviewer model to "be the attacker" | **Reject** |
| Cursor hook that clicks "New Chat" | **Reject** |
| Same session appends AFF pass with a made-up second id as a kit-blessed pass | **Reject as process**; kit cannot stop a liar, only refuse equal ids |
| Default `require` for all consumers | **Reject** |
| Waive FRV `freeze_review` because AFF passed | **Reject** — both gates |
| Waive AFF because `freeze_review` exists | **Reject** — verify-claimed-close ≠ try-to-kill |
| Waive ISR because AFF passed | **Reject** — pre-Auto spec vs post-Auto build |
| Treat mechanical `ok review --freeze` as AFF pass | **Reject** |
| Author freeze-review-loop sets `auto_may_start: true` | **Reject** |
| Fold AFF into `freeze_authorization_state` AuthState | **Reject** — second question, second helper |
| Apply AFF to `docs/reviews/` Check-OK artifacts | **Reject** — recursion |
| AFF-b Auto in this Thinking phase | **Reject** |

---

## §AFF.13 — SPEC §5 additive clauses (AFF-b writes)

Amend the existing `ok honesty-status` row. Do not add a new command row.

Additive clause (normative text Auto must include):

> **AFF additive:** Mode E `--adversarial-freeze PHASE_ID` with optional
> `--producer-session` / `--frozen-spec`; optional `--artifact-digest`
> requires `--frozen-spec` and is Mode-E-only. Exit `40` +
> `missing_adversarial_freeze` when `honesty.adversarial_freeze: require`
> and the latest eligible verdict is not pass. Frozen:
> `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md`.

`ok status` additive JSON key: `adversarial_freeze_gate` (optional; absent
when the probe skips). `--exit-code` folds `adversarial_freeze_gate.ok`
(`require` mode only) into the existing `2` tier.

`ok next` / paste-regen: when FRV would emit Auto and AFF is `suggest` or
`require` without a matching pass (or `suggest` skip), emit Thinking + the
adversarial paste. Frozen in this document §AFF.7.

SPEC §6.2 gains one sentence: author freeze-review-loop + mechanical stamp
do not clear Auto when AFF is on; Auto also needs digest-bound
`adversarial_freeze` pass (or `suggest` skip).

---

## §AFF.14 — Seven-tier matrix (AFF-b)

Prefix: `test_aff_`. All seven tiers required before AFF-b DONE.

| Tier | Must prove |
| --- | --- |
| **unit** | `adversarial_freeze` in `ENTRY_KINDS`; validate accepts a minimal valid pass body **and** a minimal valid `findings` body **and** a minimal valid `blocked` body (each with required `reviewer_model`, `producer_session_id`, `aff_posture: attack`, and distinct session ids); shared append validation rejects client `v: true`, every integer other than exact `1`, and supplied empty/non-string `ts`, while omitted `ts` is server-filled; shared `verify_chain` rejects stored missing/empty/non-string `ts` and `v: true` with `22`; every round-bearing append kind (`verification_evidence`, `independent_second_review`, `freeze_review`, and every `adversarial_freeze` verdict) rejects `round: true`; missing `reviewer_model` on pass/findings/blocked → `2`; rejects same-session ids → `2`; missing `producer_session_id` on pass → `2`; missing `aff_posture` on pass → `2`; `aff_posture` ≠ `attack` → `2`; skip with `aff_posture` present → `2`; skip with non-owner role → `23`; pass with non-verifier → `23`; bad `aff_verdict` → `2`; `round < 1` and non-int `round` → `2`; digest not `sha256:`+64 hex → `2`; genesis forbid-list includes new keys; `adversarial_freeze` parse (`off\|suggest\|require`; unknown → config `2`); absent key + `security` in `human_escalation` → `suggest`; absent key without `security` → `off`; explicit `off` wins over `security`; `require` never derived; key in `HONESTY_KEYS`; `HonestyConfig` field default `suggest`; `HonestyErrorToken` includes `missing_adversarial_freeze`; every `_resolve_mode` / `--artifact-digest` combination in §AFF.8.1–§AFF.8.2 including existing non-regular `--frozen-spec` + valid `--artifact-digest` → `mode_e`; Auto-hold match is path+digest and **ignores** `phase_id`; Mode E optional phase pin; skip match ignores `producer_session`; the common resolver selects the last eligible verdict before pass/skip wrappers inspect it; `pass → findings`, `pass → blocked`, and `pass → skip` never return the older pass; `author_loop_complete` is true for `substantive` and for `mechanical_only` only when stamp digest equals current digest, and false for `mechanical_only` with missing/unequal stamp digest; `aff_hold_bypassed` is true for honesty disabled and for mode `off`, false for honesty enabled + `suggest`/`require`; helper `off` is never classified as `pending`; resolver eligibility rejects missing/empty `phase_id`, non-int/`<1`/boolean `round`, and missing/empty `reviewer_model` on pass/findings/blocked, and rejects missing/empty `phase_id` or invalid/boolean `round` on skip; `frv_authorizing_freeze_paths` returns only `substantive` paths; `aggregate_adversarial_authorization_states` uses rank `absent > pending > skipped > pass`. |
| **integration** | `ledger append --kind adversarial_freeze` writes a hash-chained line for a valid **pass** body **and** for a valid **findings** body **and** for a valid **blocked** body (same required reviewer/session/posture fields); `ledger verify` → `0` after each; these three append round-trips MUST be proven before any last-verdict revocation assertion that consumes a `findings` or `blocked` winner. Mode E `require` + no match → `40` + JSON token; matching `pass` → `0` + exact §AFF.8.3 JSON; `suggest` miss → `0` + stderr warning; `off` → exact block/no ledger read; valid Mode E excludes B/C/D blocks; Mode E + Mode D flags → `1` diagnostic shape; all digest-only/malformed/mismatch combinations match §AFF.8.1; existing non-regular `--frozen-spec` + valid `--artifact-digest` is Mode E explicit ledger query (not usage `1`, not refusal `4`); `honesty.enabled: false` → `4`; skip authorizes under `suggest` and does not under `require`; fixture status: Auto would-emit + `require` + no AFF → `status --exit-code` `2` + JSON gate; after pass append, this gate no longer forces `2`; fixture status `suggest` + helper `absent` → exit `0`, JSON key present, `state: absent`, exact §AFF.9 absent warning; mixed FRV-authorizing candidate sets (pass+pending, pass+absent, pass+skipped) produce the same hold-vs-Auto decision on `ok status` / governance-sync as `ok next` (identical subset + aggregate); a non-substantive sibling candidate cannot create a status-only hold. |
| **e2e** | git-only fixture, two-row convention (`AFF-a` Thinking + `AFF-b` Auto; Auto deliverable backtick-cites `docs/archive/phases/…`) **and** `Thinking → Auto` split. **Trigger B:** after mechanical stamp, `ok next` on the still-open Thinking row is attack-posture Thinking (`adversarial_freeze_pending`), not the author freeze paste. **Post-stamp mutation (ADV2-M1):** edit one byte of the freeze artifact outside `review_stamp` → `ok next` returns to the author freeze paste (not adversarial) until restamped; the same mutation on an Auto row must **not** emit Auto (FRV still requires `substantive`). Restamp → Trigger B holds again with the adversarial paste. Append AFF pass with `phase_id` `AFF` (not `AFF-b`) + path + digest → Trigger B releases to ordinary Thinking paste; mark `{id}-a` DONE. **Trigger A:** open `{id}-b` Auto + FRV `freeze_review` (phase_id `{id}-b`, FRV unchanged) → without AFF, `ok next` is still adversarial Thinking; the **same** path+digest pass recorded during `{id}-a` must clear Auto (R1-M1). Execute the §AFF.7.4 transaction: adding the Review-record row invalidates old FRV/AFF bindings; restamp alone does not restore Auto; rebind FRV alone still leaves AFF pending; appending AFF last restores both gates for the final digest. One-byte later artifact edit withdraws Auto again. Same loop with `suggest` + skip → Auto, advisory `adversarial_freeze_skip`. `off` → Auto immediately after FRV. **Disabled honesty (ADV3-M1):** `honesty.enabled: false` plus explicit `adversarial_freeze: suggest` **and** the derived-suggest shape (key absent + `security` in `human_escalation`): Trigger B after a fresh mechanical stamp keeps the author freeze paste (not `adversarial_freeze_pending`); Trigger A on an Auto row with freeze candidates stays FRV `freeze_not_substantive` (not an AFF hold); Trigger A on an Auto row with no freeze candidates still emits Auto; `ok status` omits `adversarial_freeze_gate`. Identical loops under a Muse-regime fixture. `Operator + Auto` unchanged. |
| **stress** | 200-row roadmap with one open Auto row + large ledger; AFF probe bounded; no OOM. |
| **data-integrity** | Last-verdict matrix for one path/digest: pass→pass = last pass; pass→findings and pass→blocked = pending with older pass revoked; findings→pass = pass; skip→pass = pass; pass→skip = skip only under `suggest`; skip→findings = pending. The `pass → findings` and `pass → blocked` rows MUST use entries that survived `validate_append_body` / CLI append (the integration findings/blocked round-trips), not in-memory dicts that skip append validation. Different digest/path entries do not revoke each other. Skip digest D does not authorize digest D′. `ok next` twice with no ledger change → identical fence bytes. Broken ledger chain → `absent` hold, never Auto; `suggest` + that `absent` still emits the §AFF.9 JSON key and absent warning on status/governance-sync. Mode E itself is exercised with a valid authorizing pass followed by mutations of `prev_hash`, body bytes/`entry_hash`, malformed provenance, bad signature, and required-signature absence: it returns `22`/`2`/`25`/`26` per §AFF.8.3 and never `0`, including `suggest`. **Hash-consistent malformed ledger (ADV3-M3 / ADV4-M1–M2):** write mutations as hash-consistent JSONL (not via `ledger append`, which would reject them). Lines with omitted/empty `phase_id`, non-int or `<1` `round`, or omitted/empty `reviewer_model` retain the strict envelope and are chain-valid (`verify_chain` → `0`) but MUST NOT win the resolver, authorize Auto, or produce Mode E `matched_via: pass`. A matching pass with `round: true` likewise has `verify_chain` → `0` but is resolver-ineligible. Independently, recompute valid hashes after omitting `ts` or setting `v: true`; despite matching `entry_hash`, shared envelope verification MUST return `22`, every AFF surface MUST fail closed, and the resolver MUST never run. |
| **performance** | Mode E + `ok next` AFF probe complete within the same bound family as ISR Mode D / `ok next` on the ISR fixture size. |
| **security** | No secret/key/URL in paste, JSON, ledger example, or skill; templating injection-safe; fail-closed on read failure (`absent` holds when mode is on, and `suggest` + `absent` still surfaces the §AFF.9 JSON/warning); Mode E verifies the strict envelope/full chain/provenance before resolving and cannot soften integrity failure under `suggest`; author session cannot append pass with equal ids; `auto_may_start: true` still does not grant Auto; freeze-review-loop skill source bytes contain the MUST NOT `auto_may_start: true` prohibition and do **not** contain an instruction to set it true; mechanical stamp + same-session `freeze_review` without AFF does not emit Auto when mode is `suggest` or `require`; a stale `mechanical_only` stamp (digest ≠ current) does not satisfy Trigger B and does not authorize FRV Auto; a hash-consistent malformed `pass` (missing `ts`, boolean `v`, missing `phase_id`, invalid/boolean `round`, or missing `reviewer_model`) cannot authorize; helper `off` under disabled honesty cannot hold Auto; no network; no model call; no subprocess to a reviewer. |

---

## §AFF.15 — Definition of Done

### AFF-a (this Thinking phase)

- This document exists with `frozen: true`.
- Author `/freeze-review-loop` reached `pass` **without** setting
  `auto_may_start: true`.
- Mechanical `ok review --freeze` stamp written.
- `auto_may_start` absent or not `true`.
- No AFF-b code, no test file, no CLI edit, no honesty schema change, no
  skill edit, no consumer product edit, no hub Main deploy.
- ROADMAP + HANDOVER updated together; NEXT is the adversarial Thinking
  paste (different chat), not AFF-b Auto.
- Feature-branch commit. No merge to `main`.
- Do **not** add AFF-b as an open queue row while AFF-a is WIP
  (`next_regen` `multiple_open_rows` — `next_regen.py:383-384`). Queue AFF-b
  when AFF-a → DONE.

AFF-a is **not** DONE on author freeze-review-loop pass alone. The
adversarial freeze of *this* freeze is THE ONE NEXT STEP. After that pass,
the bootstrap rule in §AFF.7.4 applies: record the different-chat pass in the
artifact before its final restamp, rebind `freeze_review` for the final digest
when AFF-b is queued, but do not append the not-yet-implemented AFF kind.
Then AFF-a → DONE and AFF-b Auto is cleared to start.

### AFF-b (Auto, later)

- Built exactly to §AFF.2–§AFF.14.
- `test_aff_` seven tiers green.
- `/build-verification-review` `pass` then ISR `pass` (kit dogfood
  `require_independent_second_reviewer: require`).
- Kit dogfood config writes `adversarial_freeze: suggest`.
- No model dispatch. No `auto_may_start: true` writer. No consumer
  `require` default.

---

## §AFF.16 — Auto deliverable list (mechanical; AFF-b)

1. `adapters/config.py` — `HONESTY_KEYS`, `ADVERSARIAL_FREEZE_MODES`,
   `HonestyConfig.adversarial_freeze`, parse + derived default.
2. `tools/honesty/types.py` — kind, verdicts, error token, JSON field.
3. `tools/honesty/validate.py` — strict client envelope/type validation,
   append rules + match helpers + genesis forbid-list.
4. `tools/honesty/ledger.py` — strict stored `v`/`ts` envelope verification
   before hash/provenance acceptance; server timestamp fill only on omission.
5. `tools/adversarial_freeze/` — authorization state + status/governance
   surface + Trigger-B `author_loop_complete` + `aff_hold_bypassed` +
   `frv_authorizing_freeze_paths` + `aggregate_adversarial_authorization_states`
   (does not edit `tools/freeze_authorization/resolve.py`).
6. `tools/honesty/status.py` — Mode E, exit `40`, options, `_resolve_mode`.
7. `cli/commands/honesty_status.py` — `--adversarial-freeze` /
   `--artifact-digest`.
8. `tools/governance_hygiene/next_regen.py` — hold + paste template +
   advisory constants.
9. `tools/governance_hygiene/engine.py` — footer (ISR path, not
   `ReadFailure`).
10. `cli/commands/status.py` — JSON key + exit-`2` fold.
11. `tools/optional_feature_tips/surface.py` — off-mode tip.
12. `cursor/skills/adversarial-freeze-review/SKILL.md` + amendments in
    freeze-review-loop, freeze-review, check-ok-thinking.
13. `docs/ADVERSARIAL-FREEZE-REVIEW.md` + CHECK-OK / AGENTS / consumer
    pointers + SPEC §5/§6.2.
14. Kit dogfood `.overseer/config.yaml` explicit `suggest`.
15. `tests/**/test_aff_*.py` — seven tiers, prefix `test_aff_`.

No new argparse top-level command. No FRV `AuthState` extension. No
bornfree-hub files.

### Adversarial-freeze findings ledger (AFF-ADV-r1)

The citations below name the pre-fix AFF-ADV-r1 locations. AFF-r4 resolution
is frozen immediately after the historical findings table.

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| ADV1-B1 | BLOCKER | security / fail-open | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:370-371`, `:487-498`, `:975` | A prior pass remains authorizing after a later same-subject `findings` or `blocked` append because both frozen matchers select only pass/skip entries. The matrix tests only rejection of a lone `findings`, not `pass → findings` or `pass → blocked`. Freeze a last-verdict resolver across all AFF verdicts so a later non-pass revokes an earlier pass for the same subject/digest. |
| ADV1-M1 | MAJOR | consistency / digest binding | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:688-689`, `:842-847`; `tools/freeze_reviewer/artifact.py:119-130` | The artifact SHOULD gain an adversarial Review-record row, while the pass procedure appends a digest-bound ledger entry, but no ordering/rebind rule is frozen. A prose row is inside the digest (only `review_stamp` is excluded), so recording the round after append invalidates AFF and FRV; recording it after the existing mechanical stamp also makes that stamp digest stale. Freeze the exact sequence: record round, restamp current bytes, refresh any required `freeze_review`, then append AFF against the final digest. |
| ADV1-M2 | MAJOR | security / integrity | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:776-783`, `:979`; `tools/honesty/status.py:551-568`; `tools/honesty/ledger.py:31-77` | Mode E is told to read/match entries but is never required to run `verify_chain`; the only broken-chain assertion is for `ok next`. The existing Mode D-shaped status path reads and matches without chain verification, so following that precedent can return exit `0` for a tampered ledger even while Auto-hold correctly fails closed. Require full chain/provenance verification before every Mode E match and add tamper tests for Mode E itself. |
| ADV1-M3 | MAJOR | completeness / public contract | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:770-783`; `tools/honesty/types.py:58-93` | Mode E says only that `HonestyStatusJson` gains an optional dict and names `matched_via: skip`; unlike Modes B–D, it freezes no exact nested fields, nullability, success/miss payloads, or mode-exclusion behavior. AFF-b therefore cannot mechanically implement a stable CLI JSON contract. Freeze the complete `adversarial_freeze` block, including effective digest/path, mode, match hash, `matched_via`, and which other mode blocks must be absent. |
| ADV1-N1 | MINOR | completeness / CLI usage | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:703-714`, `:722-753` | `--artifact-digest` is introduced as Mode E metadata but is absent from the frozen mode-resolution algorithm. The contract therefore permits it to be silently ignored with Mode B/C/D and does not state the outcome for Mode E with a digest but no `--frozen-spec`, even though the matcher requires an exact `frozen_spec`. Add the flag to resolution/usage invariants and freeze these combinations. |
| ADV1-N2 | MINOR | consistency | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:3-6`, `:109-110` | The author-close status said the mechanical stamp was next after the stamp already existed. This round corrects the heading, but the author must rewrite the AFF-r3 resolution when producing the fresh post-fix stamp so the durable review history is not contradictory. |

### AFF-r4 resolution map

| Finding | Resolution |
| --- | --- |
| ADV1-B1 | §AFF.5.1 and §AFF.5.5 freeze one latest-verdict resolver across all four verdicts; pass/skip helpers inspect only its winner. §AFF.14 freezes revocation sequences. |
| ADV1-M1 | §AFF.6.1 and §AFF.7.3–§AFF.7.4 make the Review-record row mandatory before restamp, required FRV rebind, and final AFF append; the bootstrap exception forbids the not-yet-built kind. |
| ADV1-M2 | §AFF.8.3 requires full `verify_chain` chain/provenance validation before Mode E resolution, preserves integrity exits, and §AFF.14 adds Mode E tamper/provenance coverage. |
| ADV1-M3 | §AFF.8.3 freezes the full nested block, top-level nulls, outcome matrix, nullability, and valid-mode exclusion of B/C/D blocks. |
| ADV1-N1 | §AFF.8.1–§AFF.8.2 freeze the complete `--artifact-digest` matrix, usage behavior, digest/path derivation, and mode-resolution pseudocode. |
| ADV1-N2 | The status and AFF-r3 Review-record row now describe the historical pre-ADV stamp accurately; AFF-r4 records the post-fix author pass before restamping. |

### Adversarial-freeze findings ledger (AFF-ADV-r2)

This review was performed in a session different from producer nonce
`aff-a-author-2026-09-19`. The citations name the AFF-r4 bytes reviewed before
this findings record and final mechanical restamp.

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| ADV2-M1 | MAJOR | digest / ordering | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:669-672`; `tools/freeze_authorization/resolve.py:155-158`, `:189-207` | Trigger B declares the author loop complete from FRV state `mechanical_only`, but the current shared resolver computes the current digest and then returns `mechanical_only` solely from the stamp verdict; it never compares the stamp's `artifact_digest` with that current digest. An author edit after stamping can therefore replace the author NEXT with an adversarial paste on stale mechanical evidence. Freeze a trigger-specific fresh-stamp check (or repair the shared state contract deliberately) and add a mutation proving a post-stamp byte edit returns to the author loop until restamped. |
| ADV2-M2 | MAJOR | test honesty / revocation | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:374-380`, `:395-406`, `:1174-1178` | The contract requires every negative review to append `findings`/`blocked`, but the frozen tests require append validation only for a minimal pass and can exercise the revocation matrix with directly constructed entries. A build can reject valid negative bodies at the CLI while every named resolver test stays green, leaving the operational `pass → findings/blocked` revocation path unusable. Require append/round-trip tests for valid `findings` and `blocked` bodies, including their required reviewer/session/posture fields, before running the last-verdict matrix. |
| ADV2-N1 | MINOR | CLI completeness | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:795-808`, `:818-821` | The claimed complete `--artifact-digest` matrix defines readable regular files and absent paths, and defines non-files only when no explicit digest is present. It never decides Mode E for an existing non-regular path (for example a directory) plus a valid explicit digest. Freeze whether that shape is usage, refusal, miss, or an explicit ledger query, and test it. |
| ADV2-N2 | MINOR | consistency | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:225`, `:395-406` | The rejection table calls the recorded `reviewer_model` fields optional, while the normative pass/findings/blocked schema requires a non-empty `reviewer_model`. Use one rule throughout; model inequality may remain only a preference. |
| ADV2-N3 | MINOR | status honesty | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:565-571`, `:984-994` | The shared helper says `absent` is a read-error hold under both `suggest` and `require`, but the active-slice surface freezes a warning only for `suggest + pending`; it does not define `suggest + absent`. Specify the JSON/warning outcome so `ok next` cannot hold on a broken ledger while status/governance-sync silently omit the reason. |

### AFF-r5 resolution map

| Finding | Resolution |
| --- | --- |
| ADV2-M1 | §AFF.7.1 freezes Trigger-B-only `author_loop_complete`: `mechanical_only` counts only when stamp `artifact_digest` equals the current FRV digest. FRV `AuthState` / Auto authorization are unchanged. §AFF.14 e2e requires a post-stamp byte-edit return to the author paste. |
| ADV2-M2 | §AFF.14 unit/integration require `validate_append_body` / CLI append round trips for valid `findings` and `blocked` bodies before last-verdict revocation. Data-integrity revocation rows must use those append-accepted entries. |
| ADV2-N1 | §AFF.8.1–§AFF.8.2 treat existing non-regular `--frozen-spec` + valid `--artifact-digest` as Mode E explicit ledger query (not usage, not refusal). |
| ADV2-N2 | §AFF.2 rejection table and §AFF.5.2 now use one rule: `reviewer_model` is required on pass/findings/blocked; inequality remains preference only. |
| ADV2-N3 | §AFF.9 freezes `adversarial_freeze_gate.state`, the `suggest` + absent warning, and that helper `absent` is not a probe skip. |

### Adversarial-freeze findings ledger (AFF-ADV-r3)

This review was performed in a session different from producer nonce
`aff-a-author-fix-r2-2026-09-20`. The citations name the AFF-r5 bytes reviewed
before this findings record and final mechanical restamp.

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| ADV3-M1 | MAJOR | configuration / availability | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:570-574`, `:648-664`, `:1025-1042` | The shared helper defines `off` for honesty-disabled as “not a hold,” and the status probe skips when honesty is disabled, but Trigger A authorizes only `pass`/eligible `skipped`; its early bypass names resolved mode `off`, not `honesty.enabled: false`. With an explicit/derived `suggest` plus disabled honesty, a conforming implementation can receive helper `off` and still take the “otherwise hold” branch while status omits the gate. Freeze disabled-honesty as a NEXT bypass (or include helper `off` in the non-holding branch) and test both triggers. |
| ADV3-M2 | MAJOR | status honesty / candidate aggregation | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:654-664`, `:1025-1064`; `tools/governance_hygiene/next_regen.py:479-492` | Trigger A probes only candidates FRV treated as authorizing (`substantive`) and requires all of that subset to clear, while §AFF.9 says to probe the slice's freeze candidates generally and exposes one scalar `state` without defining target selection or aggregation. With multiple discovered candidates, status/governance-sync can disagree with `ok next`, or hide which pending/absent candidate holds Auto. Freeze the identical FRV-authorizing subset and deterministic worst-state aggregation (or a per-candidate payload), plus mixed pass/pending/absent tests. |
| ADV3-M3 | MAJOR | security / defensive validation | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:399-410`, `:515-532`; `tools/honesty/ledger.py:48-76` | The append schema requires non-empty `phase_id`, valid `round`, and non-empty `reviewer_model` on pass/findings/blocked, and §AFF.5.5 claims its defensive rules prevent malformed historical lines from authorizing. The eligibility list checks none of those fields. `verify_chain` verifies hashes/provenance but does not re-run kind schema validation, so a hash-consistent malformed `pass` with matching path/digest, posture, role, and unequal sessions can authorize. Add the omitted required-field checks to the resolver and mutation tests over a valid hash chain before claiming defensive fail-closed behavior. |

### AFF-r6 resolution map

| Finding | Resolution |
| --- | --- |
| ADV3-M1 | §AFF.4.3, §AFF.5.6, and §AFF.7.1 freeze `aff_hold_bypassed`: honesty disabled **or** mode `off` bypasses both Trigger A and Trigger B before probing. Helper `off` is never `pending`. §AFF.14 e2e covers disabled honesty under explicit and derived non-off modes. |
| ADV3-M2 | §AFF.5.6 / §AFF.9 freeze `frv_authorizing_freeze_paths` as the shared Trigger A and status/governance-sync subset, plus worst-state rank `absent > pending > skipped > pass`. Scalar JSON `state` is that aggregate. §AFF.14 tests mixed pass/pending/absent against `ok next` parity. |
| ADV3-M3 | §AFF.5.5 eligibility rules 9–11 require non-empty `phase_id`, exact-integer `round` ≥ 1, and non-empty `reviewer_model` on pass/findings/blocked. `verify_chain` enforces the shared envelope but still does not re-run AFF kind schema. §AFF.14 data-integrity/security require hash-consistent malformed-ledger mutations that cannot authorize. |

### Adversarial-freeze findings ledger (AFF-ADV-r4)

The citations below name the AFF-r6 bytes reviewed before this findings record
and final mechanical restamp. AFF-a remains WIP; no `adversarial_freeze` entry
was appended because AFF-b has not created that kind.

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| ADV4-M1 | BLOCKER | security / envelope validation | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:374-376`, `:525-551`; `tools/honesty/ledger.py:48-60` | The frozen envelope requires `v: 1` and `ts`, but the defensive eligibility rules never check either field. `verify_chain` checks only `entry.get("v") != 1`, prev/hash linkage, and the computed hash; it does not require `ts`, so a hash-valid `adversarial_freeze` `pass` with `ts` omitted still passes chain verification and rules 1–11, then authorizes Auto/Mode E. The same comparison also accepts JSON `v: true` as equal to integer `1`; the resolver has no exact-type check. Freeze strict envelope validation (or make `verify_chain` strict) and add hash-valid missing-`ts` / boolean-`v` mutations to the AFF fail-closed matrix. |
| ADV4-M2 | MAJOR | security / type validation | `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:417`, `:545-553`; `tools/honesty/validate.py:319-321` | The contract says `round` is an integer and calls the resolver rule the same as `validate_append_body`, but both the frozen `isinstance(int)` wording and the cited implementation admit JSON `true` because Python `bool` subclasses `int`. A hash-valid pass with `round: true` therefore satisfies the stated defensive rule and can authorize despite being an invalid round. Freeze an exact-integer rule (`type(round) is int`, or equivalent) in append validation and resolver eligibility, and add a boolean-round mutation. |

### AFF-r7 resolution and full ADV1–ADV4 re-derivation map

Every resolution below cites the current frozen contract by `path:line`.
ADV1–ADV3 were re-derived from the named paths rather than presumed closed;
ADV4 is the repaired round. No scope from an earlier repair is removed.

| Finding | Current resolution evidence |
| --- | --- |
| ADV1-B1 | Latest eligible verdict across all four outcomes revokes an older favorable entry, and wrappers inspect only that winner: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:427-433`, `:546-601`; revocation matrix `:1368`. |
| ADV1-M1 | Review-record → final artifact edits → restamp → conditional FRV rebind → actual AFF verdict append is mandatory, with the AFF-a bootstrap prohibition: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:848-896`. |
| ADV1-M2 | Mode E verifies the entire ledger before resolving and preserves integrity exits: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:1088-1103`; tamper coverage `:1368-1370`. |
| ADV1-M3 | Exact Mode E block, types/nullability, mode exclusion, success/miss outcomes, and diagnostic shape are frozen: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:1022-1111`. |
| ADV1-N1 | Digest/path derivation and the full usage matrix, including digest-without-path rejection, are frozen: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:902-952`, `:954-1020`. |
| ADV1-N2 | Current status and Review record distinguish historical stamps from the current repaired round: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:3-17`, `:114-127`. |
| ADV2-M1 | Trigger B requires a fresh mechanical stamp whose recorded digest equals the current FRV digest; it does not alter FRV Auto authorization: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:757-797`; mutation coverage `:1366`. |
| ADV2-M2 | Valid pass/findings/blocked append round trips precede and feed negative revocation assertions: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:427-433`, `:1364-1368`. |
| ADV2-N1 | Existing non-regular path plus explicit valid digest is a confined Mode E ledger query, not usage/refusal: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:915-938`, `:940-952`, `:1014-1017`. |
| ADV2-N2 | `reviewer_model` is required and non-empty for pass/findings/blocked; only model inequality is optional: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:448-470`, `:585-586`. |
| ADV2-N3 | `suggest + absent` is a visible non-failing status/governance warning and never a probe skip: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:1141-1154`; coverage `:1365`, `:1368-1370`. |
| ADV3-M1 | Disabled honesty or resolved `off` bypasses both NEXT triggers; helper `off` never becomes pending: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:349-355`, `:629-635`, `:729-755`, `:757-773`; coverage `:1364-1366`. |
| ADV3-M2 | Trigger A and status share the FRV-substantive candidate subset and deterministic worst-state aggregation `absent > pending > skipped > pass`: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:659-669`, `:739-755`, `:1124-1143`; parity coverage `:1364-1365`. |
| ADV3-M3 | The resolver defensively requires non-empty `phase_id`, exact-integer positive `round`, and non-empty `reviewer_model` after common-envelope verification: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:564-592`; hash-consistent mutation coverage `:1364`, `:1368-1370`. |
| ADV4-M1 | Shared append and chain verification enforce exact integer `v: 1` plus required non-blank stored `ts`; hash-consistent missing-`ts` and boolean-`v` entries fail chain verification with `22` before resolution: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:380-405`, `:1088-1103`, `:1364`, `:1368-1370`; AFF-b implementation locus `:1416-1419`. |
| ADV4-M2 | All append branches and resolver eligibility use `type(round) is int`, explicitly rejecting JSON/Python boolean; the boolean-round AFF mutation remains chain-valid but cannot win or authorize: `docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md:407-413`, `:448-459`, `:479-487`, `:582-592`, `:1364`, `:1368-1370`. |

### Adversarial-freeze confirmation (AFF-ADV-r5)

This review was performed in a session different from producer nonce
`aff-a-author-fix-r4-2026-09-20`. The author Review-record was not trusted.
Live contract holes that AFF-b must close were re-derived from source:
`tools/honesty/ledger.py:50` (`entry.get("v") != 1` admits `True` because
`True == 1`); no stored-`ts` check in `verify_chain` (`:48-60`);
`tools/honesty/validate.py:320`, `:340`, `:379` (`isinstance(round, int)`
admits `True` because `bool` subclasses `int`). The repaired freeze closes
those holes at the layers named below. No new findings. AFF-a bootstrap:
Review-record only; no `adversarial_freeze` append; no FRV rebind (no prior
bound `freeze_review` entry); `auto_may_start` absent.

| ID | Independent confirmation |
| --- | --- |
| ADV4-M1 | Hash-consistent missing/blank/`ts` or boolean `v` cannot reach an AFF resolver or authorizing surface: stored envelope requires `type(v) is int` and non-empty `ts` (`:376-396`); Mode E calls `verify_chain` first and never resolves on nonzero (`:1084-1089`); helper verifies the full chain before resolving (`:635-636`); missing-`ts` / `v: true` mutations with matching `entry_hash` MUST return `22` and MUST NOT run the resolver (`:1360`, `:1364`). Live `True == 1` / missing-`ts` holes remain in current code because AFF-a is spec-only. |
| ADV4-M2 | Boolean `round` cannot pass any round-bearing append kind, the AFF append branch, or AFF resolver eligibility: shared `type(round) is int and round >= 1` replaces every `isinstance(int)` check (`:403-409`) including `verification_evidence` / `independent_second_review` / `freeze_review` / every AFF verdict (`:450`, `:481`); resolver rule 10 uses the same exact-type test (`:578-580`); `round: true` remains chain-valid (`verify_chain` → `0`) and resolver-ineligible (`:1360`, `:1364`). Layer split vs ADV4-M1 is explicit: envelope failures are `22` before resolve; boolean-round is kind-schema defense. |
| ADV3-M1 | Disabled honesty bypasses both NEXT triggers before any AFF probe; helper `off` is never `pending`; status skips (`:345-351`, `:627-631`, `:652-653`, `:725-733`, `:735-738`). e2e coverage `:1362`. Status cannot hold while NEXT skips, or the reverse. |
| ADV3-M2 | Trigger A and status/governance-sync share `frv_authorizing_freeze_paths` and worst-state rank `absent > pending > skipped > pass` (`:655-665`, `:1123-1136`). Mixed-candidate parity is required (`:1360`). |
| ADV3-M3 | Resolver eligibility 9–11 still reject missing `phase_id` / invalid `round` / missing `reviewer_model` after envelope verification (`:560-588`). Not replaced by the ADV4 envelope checks. |
| ADV1-B1 | Latest eligible verdict across all four outcomes; later `findings`/`blocked` revokes (`:423-429`, `:542-548`, `:1364`). Not narrowed. |
| ADV1-M1 | §AFF.7.4 ordering plus AFF-a bootstrap prohibition (`:848`, `:887-892`). This round followed it: Review-record before restamp; no AFF append. |
| ADV1-M2 / ADV1-M3 / ADV1-N1 | Mode E full-chain (`:1084-1089`), exact JSON (`:1018`), digest/path matrix including non-regular+digest (`:909-917`, `:1010-1013`). Not narrowed. |
| ADV2-M1 | Trigger-B fresh-stamp vs current FRV digest; FRV Auto unchanged (`:771`; e2e `:1362`). Not narrowed. |
| ADV2-M2 | Valid `findings`/`blocked` append round trips before revocation matrix (`:1360`, `:1364`). Not narrowed. |
| ADV2-N1 / ADV2-N2 / ADV2-N3 | Non-regular+digest Mode E query (`:1010-1013`); required `reviewer_model` (`:455`); `suggest + absent` visible non-skip (`:1138-1150`). Not narrowed. |
