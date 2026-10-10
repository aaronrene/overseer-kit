# Canonical NEXT in bounded v1

Use `cli/ok -C ROOT next` (or the root's `.overseer/bin/ok`). It reads only
`docs/NEXT.md` for the current action. ROADMAP and HANDOVER summarize the state;
neither is a fallback prompt source. Unknown, stale, foreign, or malformed NEXT
produces a nonzero refusal and no prompt.

NEXT has strict YAML frontmatter for schema, repository UUID/root, branch, base
HEAD, lane, model, action ID, action kind, and prompt SHA-256, followed by the exact
UTF-8 prompt. `next-write` is its single supported publisher. See the repository
README for required expected-context arguments and compare-before-write behavior.

Schema 2 adds `vcs` (`git` or `muse`) and `source_id` (the Muse repository ID, or
null for Git). Existing schema-1 NEXT is accepted only with Git authority. The
base revision belongs to the selected backend; a Git mirror revision never
substitutes for a Muse revision. Muse writers require explicit `--vcs muse` and
`--base-head REVISION` as well as the existing context and prior NEXT digest.

Commit application work before publishing ignored NEXT. A later Muse commit
always makes NEXT stale. The legacy Git exception for one closing commit that
contains the exact tracked NEXT bytes remains supported; newly ignored NEXT
does not use it. Adopting a different backend preserves NEXT bytes but refuses
them until explicitly republished for the new authority. No task is inferred.

The former synchronization alias and legacy prompt extraction are historical
and not supported by the v1 launcher. On closeout print CURRENT NEXT from disk.
