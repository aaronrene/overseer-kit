# Independent second reviewer — portable paste (any AI tool)

The kit records and gates the second verdict. It does not run another model.
Open a new chat or a separate verifier runtime; then use the CLI below.

**Not Cursor-only.** Use this in Claude Code, GitHub Copilot, ChatGPT, or any
assistant. A **human** counts as the second verifier.

## Why

After an Auto build, the builder chat must not mark ROADMAP **DONE** alone when
`honesty.require_independent_second_reviewer` is `warn` or `require`. A second
chat (or separate verifier) re-checks the build and records a ledger line. The
kit never opens that chat and never calls a reviewer API.

## Builder: invent a producer session nonce

Before handing off, invent or copy an opaque `producer_session` string (chat /
composer id when the host exposes one; otherwise any human-chosen nonce). Give
that string to the second chat. The kit does not scrape IDE session ids.

## Record (second chat / verifier)

```bash
ok ledger append --kind independent_second_review --stdin <<'EOF'
{
  "kind": "independent_second_review",
  "actor_role": "verifier",
  "actor_session_id": "<THIS_CHAT_SESSION_ID>",
  "phase_id": "<PHASE_ID>",
  "frozen_spec": "docs/archive/phases/PHASE-….md",
  "round": 1,
  "isr_verdict": "pass",
  "producer_session_id": "<BUILDER_PRODUCER_SESSION_NONCE>"
}
EOF
```

`actor_session_id` must differ from `producer_session_id`. Equal ids are refused
(exit `2`).

## Check (Mode D)

```bash
ok honesty-status --independent-second-review PHASE_ID \
  [--producer-session BUILDER_NONCE] [--frozen-spec PATH] [--json]
```

Under `require`, a miss exits `38` with token `missing_independent_second_review`.
Under `warn`, miss warns and exits `0`. Under `off` (default), Mode D may still
run but never fails the match dimension.

## Print NEXT for the second chat

```bash
ok next
# synonym:
ok governance-sync --print-next
```

## Host map

| Host | Record | Check | Instructions |
| --- | --- | --- | --- |
| Any (`ok` CLI) | `ledger append` | Mode D + `ok status` surface | this doc |
| Cursor | same | same | `/independent-second-reviewer` + amended BV rule |
| Claude Code | same | same | `.claude/skills` after `ok sync` |
| Copilot / paste | same | same | this doc |

See frozen contract:
`docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md`.
