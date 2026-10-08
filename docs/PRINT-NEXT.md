# Canonical NEXT in bounded v1

Use `cli/ok -C ROOT next` (or the root's `.overseer/bin/ok`). It reads only
`docs/NEXT.md` for the current action. ROADMAP and HANDOVER summarize the state;
neither is a fallback prompt source. Unknown, stale, foreign, or malformed NEXT
produces a nonzero refusal and no prompt.

NEXT has strict YAML frontmatter for schema, repository UUID/root, branch, base
HEAD, lane, model, action ID, action kind, and prompt SHA-256, followed by the exact
UTF-8 prompt. `next-write` is its single supported publisher. See the repository
README for required expected-context arguments and compare-before-write behavior.

The `governance-sync --print-next` alias and legacy prompt extraction are historical
and not supported by the v1 launcher. On closeout print CURRENT NEXT from disk.
