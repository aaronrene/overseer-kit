# NEXT model line is a recommendation

In a repository with one declared lane, the `Model:` line in `docs/NEXT.md` is a
recommendation shown to the person who picks the model in Cursor, Codex, or
anywhere else. It is not a permission, and no command reads it to permit, skip,
or select a check, write, transport, or provider call.

`context.model` remains the saved default. `adopt` and Muse rebind still require
`--model` to equal that default. Publishing a different label does not change
the config.

## Single-lane rule

| Lanes declared | NEXT `model` | Result |
| --- | --- | --- |
| 1 | equal to `context.model` | accepted (general `label()` only) |
| 1 | different, passes `model_label` | accepted |
| 1 | different, fails `model_label` | refused `model_label_invalid` |
| more than 1 | any | unchanged (general `label()` only) |

The rule lives in `validate_next`, so it covers `next-write` (single and batch),
`ok next`, `status` (`next_error`), `hook`, `governance-sync --print-next`, and
existing-config `init`.

## Grammar

```text
MODEL_LABEL = re.compile(r"[A-Za-z][A-Za-z0-9._,()+/-]*(?: [A-Za-z0-9._,()+/-]+)*\Z")
MODEL_LABEL_MAX = 120
```

ASCII only, first character a letter, single spaces between words, and the
punctuation `. _ , ( ) + / -`. Examples: `CODEX`, `OPUS`, `GPT-6 Astra`,
`Cursor Auto`, `OpenAI Codex (latest GPT model, high reasoning)`.

## Hand edits and `--expect-next`

A hand-edited model label that still passes `model_label` is displayed, the same
as in multi-lane repositories today. Integrity against an unexpected rewrite is
`--expect-next <digest reported by next-write>`, which refuses
`next_digest_mismatch` on any byte change. A label that fails the grammar is
refused on every read and write.

## Rollback on an older runtime

An older runtime that still pins single-lane NEXT to `context.model` refuses
`next_model_mismatch` when NEXT names a different label. Status reports that as
`next_error` and exits 1. That is fail-closed and expected. Do not restore old
NEXT bytes for a completed action. Publish a successor through the restored
runtime's `next-write` with `--model` equal to `context.model` and
`--expect-next <current digest>`.
