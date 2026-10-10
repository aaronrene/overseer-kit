> **Historical pre-reset product.** This document describes the pre-reset historical product.
> Its legacy commands are not exposed by the bounded-v1 entrypoint. Do not use it
> as current onboarding. See the [root README](../README.md) and [current docs index](README.md).

# Adversarial freeze review — portable paste (any AI tool)

The kit records and gates the adversarial freeze verdict. It does not run
another model. Open a **different chat** from the author freeze-review-loop
session (prefer a different model); then use the CLI below.

**Not Cursor-only.** Use this in Claude Code, GitHub Copilot, ChatGPT, or any
assistant. A **human** counts as the adversarial reviewer.

## Why

After author freeze-review-loop pass (and mechanical stamp), Auto must not
start when `honesty.adversarial_freeze` is `suggest` or `require` until an
attack-posture review tries to **kill** the freeze and records a digest-bound
`adversarial_freeze` ledger line (or, under `suggest` only, an owner `skip`).

This is **not** ISR (post-Auto build check) and **not** FRV `freeze_review`
(verify claimed close). Attack posture is a separate ledger kind.

## Author: invent a producer session nonce

Before handing off, invent or copy an opaque `producer_session` nonce into the
handover NEXT block. Give that string to the adversarial chat. The kit does
not scrape IDE session ids.

## Review-record / restamp / rebind / append transaction

For every completed adversarial round, exact order:

1. Decide `pass|findings|blocked` **without** appending yet.
2. Write the Review-record row; finish all freeze-artifact edits.
3. `ok review --freeze <artifact>` — mechanical pass; stamp digest equals
   current FRV `artifact_digest` **D**.
4. If Auto needs FRV authorization, append `freeze_review` for the same path
   and digest **D**; verify the ledger.
5. Append `adversarial_freeze` with the actual verdict and digest **D**;
   verify again.
6. Do not edit the freeze artifact after step 5.

## Record (adversarial chat / verifier)

```bash
ok ledger append --kind adversarial_freeze --stdin <<'EOF'
{
  "kind": "adversarial_freeze",
  "actor_role": "verifier",
  "actor_session_id": "<THIS_CHAT_SESSION_ID>",
  "phase_id": "<PHASE_ID>",
  "frozen_spec": "docs/archive/phases/PHASE-….md",
  "round": 1,
  "aff_verdict": "pass",
  "aff_posture": "attack",
  "artifact_digest": "sha256:<64_lowercase_hex>",
  "producer_session_id": "<AUTHOR_PRODUCER_SESSION_NONCE>",
  "reviewer_model": "thinking-high"
}
EOF
```

`actor_session_id` must differ from `producer_session_id`. Equal ids are
refused (exit `2`). On findings/blocked, append that verdict — never omit a
negative append to preserve an older pass.

## Operator skip (suggest only)

```bash
ok ledger append --kind adversarial_freeze --stdin <<'EOF'
{
  "kind": "adversarial_freeze",
  "actor_role": "owner",
  "actor_session_id": "<OWNER_SESSION>",
  "phase_id": "<PHASE_ID>",
  "frozen_spec": "docs/archive/phases/PHASE-….md",
  "round": 1,
  "aff_verdict": "skip",
  "artifact_digest": "sha256:<64_lowercase_hex>"
}
EOF
```

Skip authorizes only under `suggest`. Under `require` it is inert.

## Check (Mode E)

```bash
ok honesty-status --adversarial-freeze PHASE_ID \
  --frozen-spec PATH [--artifact-digest DIGEST] \
  [--producer-session AUTHOR_NONCE] [--json]
```

Derived default when the key is absent: `suggest` if
`freeze_contract.human_escalation` contains `security`, else `off`.
`require` is never derived.

Under `require`, a miss exits `40` with token `missing_adversarial_freeze`.
Under `suggest`, miss warns and exits `0`. Under `off`, Mode E emits the
block with no ledger match.

## Print NEXT for the adversarial chat

```bash
ok next
```

When AFF is pending, `ok next` emits Thinking + the attack-posture paste.

## Host map

| Host | Record | Check | Instructions |
| --- | --- | --- | --- |
| Any (`ok` CLI) | `ledger append` | Mode E + `ok status` surface | this doc |
| Cursor | same | same | `/adversarial-freeze-review` |
| Claude Code | same | same | `.claude/skills` after `ok sync` |
| Copilot / paste | same | same | this doc |

See frozen contract:
`docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md`.
