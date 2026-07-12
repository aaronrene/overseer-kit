# Phase Track P / P0 — Agent identity & signed provenance (Thinking freeze)

Status: **Draft — pending freeze review.** P0 is **spec-only**; the P1 Auto build is gated on a
freeze-review `pass` of this contract. No code lands under P0.

```yaml
phase: TRACK-P-P0
outputs:
  - id: track-p-p0-agent-provenance
    path: docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md
    frozen: true
frozen_inputs:
  - id: k9a-l1-l2-module-freeze
    path: docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md
  - id: honesty-ledger-impl
    path: tools/honesty/ledger.py
  - id: honesty-canonical-hash
    path: tools/honesty/canonical.py
  - id: honesty-validate
    path: tools/honesty/validate.py
  - id: layered-honesty-vision-l3
    path: docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md#24-l3--musehub-substrate-optional-deepen
  - id: muse-social-domain-provenance
    path: https://staging.musehub.ai/gabriel/musehub/issues/6
```

**Downstream edge:** Track P / P1 (Auto build) and the Muse social domain both consume this
provenance schema as ground truth. Per SPEC §6 this is a **mandatory reviewed freeze** before P1
builds. Track P / P0 has no `{step}b` Auto build of its own.

**Review record (§6.2):**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| _pending_ | — | — | Run `/freeze-review-loop`, then `overseer review --freeze` when CLI green. Not cleared until `pass`. |

---

## §P0.0 — Simple summary

Right now the honesty ledger records **what** happened (a verdict passed, an artifact was approved)
and chains entries so history cannot be silently rewritten. It does **not** record **who** produced
each entry in a cryptographically verifiable way. Under `git-only` that identity is "soft" — a
session string an agent can type. The Muse social domain (already Phases 00–02 on the `muse` repo)
solves the same problem for social posts: every post carries `agent_id`, `model_id`, and an Ed25519
signature that traces back to a human owner's root key.

**Track P / P0 freezes one shared primitive: an optional, additive `provenance` envelope on ledger
entries** — the same trust chain the Muse social domain uses. Soft (unsigned) under `git-only`;
hard (Ed25519-signed, Muse-verified) under `muse+git-mirror` / `muse-only`. This is the L3
"signed human/agent identity" row from the vision doc, made concrete and testable.

**Technical summary:** add an optional `provenance` object to non-genesis ledger entry bodies,
carrying `agent_id`, `model_id`, and optional `sig` (Ed25519 over the entry's chain hash). Extend
`compute_entry_hash` to exclude `provenance.sig` so a signature can cover the chain position without
altering it. Add a `honesty.require_agent_signature` config flag (default `false`; only meaningful
under a Muse-backed regime) and new exit codes for signature failures. Backward-compatible with the
frozen v1 ledger: existing unsigned entries verify unchanged.

---

## §P0.1 — Scope

**In scope (freeze only):**

- The `provenance` entry envelope schema (§P0.3).
- Canonical-hash + signature rule so signatures are verifiable and chain-stable (§P0.4).
- `honesty.require_agent_signature` config flag + regime interaction (§P0.5).
- Exit-code additions for signature/provenance failures (§P0.6).
- git-only (soft) vs Muse (hard) capability tiers (§P0.7).
- Seven-tier test matrix the P1 build must satisfy (§P0.8).
- Shared-schema contract note for the Muse social domain (§P0.9).

**Out of scope (explicit non-goals — prevent creep):**

- **Any social network features in the kit** — no feeds, timelines, posts, DMs, follows. Those live
  in the Muse social domain and in Schooling as a consumer UI. The kit only supplies the provenance
  schema.
- **Key management / mnemonic storage / HD derivation implementation** — the kit *verifies* and
  *records* signatures; Muse owns key custody and derivation. Under git-only the kit never generates
  or holds private keys.
- **Model routing (P-route) and verification-evidence capture (P-evidence)** — deferred; not part of
  P0. May be freezed as later P slices if prioritized.
- **A live "deployment gate"** — named as a future candidate only; not scoped here.
- **Making any of this required under `git-only`** — K7 guardrail: no core governance feature may be
  MuseHub-only, and equally, signed identity must never be *mandatory* for the git-only baseline.

---

## §P0.2 — What exists now (verified, do not redesign)

From `tools/honesty/` (K9a/K10, frozen):

| Element | Current shape |
| --- | --- |
| Entry envelope | `{ v: 1, ts, kind, prev_hash, entry_hash, ... }` |
| Chain hash | `entry_hash = sha256(canonical_json(body \ {entry_hash}))` (`canonical.py`) |
| Entry kinds | `genesis, task_assigned, verdict, dispute_opened, overseer_ruling, approval_recorded, board_advance, hook_check` |
| Actor roles | `owner, overseer, producer, verifier` |
| Verdict fields | `actor_role=verifier, actor_session_id, artifact_sha256, passed, evidence.reexecuted[]` |
| Verify | `verify_chain` walks `prev_hash`→`entry_hash`; any mismatch → exit `22` |
| Existing L2 exit codes | `20`? reserved · `21` approval integrity · `22` ledger broken · `23` role violation · `24` evidence-free |

P0 **must not** change genesis, the chain-walk algorithm's structure, existing kinds, or existing
exit-code meanings. It only **adds** an optional envelope and new failure codes.

---

## §P0.3 — The `provenance` envelope (frozen schema)

Optional object on **any non-genesis** entry body. Genesis entries MUST NOT carry `provenance`
(consistent with genesis field restrictions in `validate.py`).

```
provenance:
  agent_id:   str            # required when provenance present; e.g. "cursor-agent", "claude-code"
  model_id:   str            # required when provenance present; e.g. "gpt-5.6", "claude-opus-4-8"
  human_ref:  str | null     # optional owner handle/DID the agent key derives from (Muse)
  sig:        str | null     # optional "ed25519:<base64>" over the entry chain hash (§P0.4)
  pubkey:     str | null     # optional "ed25519:<base64>" agent public key (or resolved via Muse)
```

Rules:

1. When `provenance` is present, `agent_id` and `model_id` MUST be non-empty strings.
2. `sig` and `pubkey` are optional under `git-only` (soft identity). When one is present, both MUST
   be present.
3. `provenance` is permitted on all non-genesis kinds. For `verdict` and `approval_recorded` (the
   spend/authority-bearing kinds), a Muse-backed regime MAY require a valid `sig` (§P0.5).
4. Unknown keys inside `provenance` fail closed (exit `2`) — mirrors the strict-key discipline used
   for config parsing.

---

## §P0.4 — Canonical hash & signature rule (frozen)

To let a signature cover the entry's chain position without changing that position:

1. **Chain hash excludes the signature.** `compute_entry_hash` is extended to strip **both**
   `entry_hash` **and** `provenance.sig` before canonicalization. Because stripping an absent nested
   key is a no-op, **every existing unsigned entry hashes identically** — the v1 chain is unbroken.
2. **Signature domain.** `sig = ed25519_sign(agent_privkey, utf8(entry_hash_hex))`. The signature
   signs the lowercase hex `entry_hash` string (the chain position), so verification needs only the
   entry itself plus the public key.
3. **Verification.** `verify` recomputes `entry_hash` (excluding `sig`), then, when `sig` present,
   checks `ed25519_verify(pubkey, entry_hash_hex, sig)`. `pubkey` comes from the entry (git-only) or
   is resolved via Muse's key registry / HD derivation from `human_ref` (Muse regimes).
4. **Version stays `v: 1`.** This is a purely additive envelope; no `v` bump. The frozen validator's
   `v == 1` rule is unchanged.

---

## §P0.5 — Config flag & regime interaction (frozen)

Add to the `honesty:` config block (additive; default preserves current behavior):

```yaml
honesty:
  require_agent_signature: false   # default false
  # when true AND regime is muse-backed: verdict + approval_recorded entries
  #   MUST carry a valid provenance.sig, else append refuses (exit 25/26).
  # under git-only: setting true is a config error (26) — signed identity is a
  #   Muse capability; the git-only baseline must never hard-require it (K7 guardrail).
```

| Regime | `require_agent_signature` | Behavior |
| --- | --- | --- |
| `git-only` | `false` (only valid value) | Provenance optional + unsigned allowed; `true` → config error `26` |
| `muse+git-mirror` / `muse-only` | `false` (default) | Provenance optional; signatures verified when present |
| `muse+git-mirror` / `muse-only` | `true` | `verdict` + `approval_recorded` MUST carry valid `sig`; else refuse |

---

## §P0.6 — Exit codes (frozen additions; non-overlapping)

| Code | Meaning | Where |
| --- | --- | --- |
| `2` | Malformed `provenance` (missing `agent_id`/`model_id`, unknown key, sig/pubkey only one present) | `ledger append`, `verify` |
| `25` | `provenance.sig` present but signature verification fails | `ledger verify`, `honesty-status` |
| `26` | Signature required but absent (regime + `require_agent_signature`), or `require_agent_signature: true` under `git-only` | `ledger append`, config load |

Existing codes `10–11`, `20–24` are unchanged. `verify_chain` still returns `22` for chain breakage;
signature failure is the distinct code `25` so operators can tell "history tampered" from "identity
unverifiable" apart.

---

## §P0.7 — Capability tiers (frozen)

| Capability | `git-only` | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Record `agent_id` / `model_id` | Yes (soft) | Yes |
| Ed25519 `sig` on entries | Optional; verified if `pubkey` embedded | Yes; verified via Muse key registry / HD derivation |
| `require_agent_signature: true` | **Refused** (config error `26`) | Allowed |
| Ledger custody | File in git | Content-addressed + signed (Muse) |

This is the vision doc's L3 row (§2.4) made concrete. Baseline honesty (L0–L2) remains fully usable
on plain GitHub; signatures are the optional Muse deepen.

---

## §P0.8 — Seven-tier test matrix (P1 build must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | `provenance` schema validation (present/absent, required fields, strict keys); `compute_entry_hash` excludes `sig`; unsigned legacy entry hashes unchanged; ed25519 sign/verify round-trip |
| **integration** | `ledger append` with/without provenance; `ledger verify` flags bad sig as `25`; `require_agent_signature` gate on verdict/approval |
| **e2e** | Full cycle: assign → signed verdict → signed approval → `verify` green; git-only unsigned cycle still green |
| **stress** | Large ledger with mixed signed/unsigned entries verifies within bound |
| **data-integrity** | Re-verify twice is deterministic; tampering with body flips `22`; tampering with `sig` flips `25`; excising `sig` does not change `entry_hash` |
| **performance** | Signature verification over N entries bounded (< documented ceiling) |
| **security** | No private key ever read/stored by the kit; malformed sig rejected, not executed; `human_ref`/`pubkey` treated as opaque data; no injection via provenance strings; git-only cannot be forced to hold keys |

---

## §P0.9 — Shared-schema contract with the Muse social domain (informative)

The Muse social domain (`gabriel/musehub` issue #6) signs every post with an Ed25519 key derived
from a human root via HD derivation, and records `agent_id` + `model_id` on agent posts. **The
`provenance` envelope frozen here is deliberately the same shape** so that:

- An agent's honesty-ledger verdict and its social post share one identity + signature model.
- The social graph's trust chain and the kit's ledger trust chain resolve keys the same way (Muse
  key registry / `human_ref` derivation).
- Schooling's social page (a consumer UI over Muse's `GET /api/social/{handle}`) inherits verifiable
  agent provenance without the kit implementing any social feature.

The kit remains governance/honesty-only. Social protocol = Muse; social UI = Schooling.

---

## §P0.10 — Close-out (execute only when P0 marked DONE)

1. Freeze-review `pass` recorded in the Review record table above.
2. ROADMAP Track P row: P0 → **DONE**; add **P1 (Auto build)** row against this contract.
3. Handover NEXT flips to **Track P / P1 (Auto build)** with paste-ready prompt + governance gates.
4. Governance sync: ROADMAP + handover in the same commit (SD-17).
