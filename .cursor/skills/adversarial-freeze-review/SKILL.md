---
name: adversarial-freeze-review
description: >-
  Adversarial freeze review — different chat from the author tries to kill the
  freeze before Auto. Records adversarial_freeze ledger verdict. Kit
  records/gates only; does not run another model.
---

# Adversarial freeze review

Invoke: **`/adversarial-freeze-review`**.

The kit records and gates the adversarial verdict. It does not run another
model. Open a new chat (prefer a different model); then use the CLI below.

Portable paste (any host): `docs/ADVERSARIAL-FREEZE-REVIEW.md`.

## Four review kinds (do not collapse)

| Kind | Posture | Session |
| --- | --- | --- |
| freeze-review-loop | Improve until clean | Same (author) |
| independent freeze review (`freeze_review`) | Verify claimed close | Different chat recommended |
| **adversarial freeze** (this skill) | **Try to kill** the spec | **Different chat**, prefer different model |
| independent second reviewer (ISR) | Re-check the *build* | Different chat from builder |

## Process (frozen)

1. Confirm this session is **not** the author freeze-review-loop session. If
   it is, stop. Do **not** append pass. Do **not** start Auto.
2. Attack posture: try to kill the spec. Re-read the freeze + frozen_inputs.
   Do not trust the author Review-record.
3. Cite every finding `path:line`.
4. For every completed verdict, execute the transaction in exact order: write
   the Review-record row; complete artifact edits; restamp and establish final
   digest `D`; rebind required FRV `freeze_review` to `D`; then append the
   actual AFF verdict against `D` as the final binding operation.
5. On pass: append `adversarial_freeze` with `aff_verdict: pass`,
   `aff_posture: attack`, this session as `actor_session_id`, and the author
   nonce as `producer_session_id`. On findings/blocked: append that negative
   verdict, never pass; the latest-verdict rule revokes any older pass for the
   same subject/digest.
6. Any later freeze-artifact edit restarts the full transaction. Never claim
   that an AFF append repaired a stale FRV binding.
7. Never merge to `main`. Never call a model via the kit CLI.

## Append (pass example)

```bash
ok ledger append --kind adversarial_freeze --stdin <<'EOF'
{
  "kind": "adversarial_freeze",
  "actor_role": "verifier",
  "actor_session_id": "<THIS_CHAT_SESSION_ID>",
  "phase_id": "<PHASE_ID>",
  "frozen_spec": "<FROZEN_SPEC_PATH>",
  "round": 1,
  "aff_verdict": "pass",
  "aff_posture": "attack",
  "artifact_digest": "sha256:<64_lowercase_hex>",
  "producer_session_id": "<AUTHOR_PRODUCER_SESSION_NONCE>",
  "reviewer_model": "thinking-high"
}
EOF
```

## Check

```bash
ok honesty-status --adversarial-freeze PHASE_ID \
  --frozen-spec PATH [--artifact-digest DIGEST] \
  [--producer-session AUTHOR_NONCE] [--json]
```
