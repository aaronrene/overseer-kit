# Native initialization composition follow-up

The unchanged original cases failed on the opening integrated source because
fresh initialization refused inherited portable skills. The already proposed
init-preservation patch addresses that product defect. These checks use new
disposable native fixtures and the newly extracted HEAD candidate installation;
no preserved Muse history or live product source was changed.

| Case | Opening source | Isolated candidate |
| --- | --- | --- |
| `test_committed_git_baseline_import_isolated_from_owner_edits` | Failed on `init_asset_exists` in 4.58s | Original passed unchanged in 9.96s |
| `test_shared_native_stage_is_readonly_and_visible_in_linked_checkout` | Failed on `init_asset_exists` in 14.92s | Original passed unchanged in 23.16s |
| `test_native_linked_worktree_own_branch_and_checkout_identity` | Failed on `init_asset_exists` in 15.51s | Init succeeds; original then fails its `dirty is False` assertion in 25.64s |
| Explicit full-footprint linked successor | Requires the preservation repair | Passed in 32.52s |

The linked checkout's sole portable byte/mode change is
`.overseer/version.lock`. Its root-bound launcher has a different hash because
the new checkout has its own UUID/root binding. Existing portable assets retain
their exact bytes/modes while their lock rows become `origin: preserved`.
The exact comparison is in `native-linked-candidate-diff.json`. The native
reader correctly reports the resulting tracked metadata change as dirty; hiding
it or altering tracked-binding semantics would be an incorrect repair.

The explicit successor is
`tests/fpr4/test_native_linked_footprint.py::test_native_linked_checkout_reports_tracked_footprint_change_and_keeps_identity`.
It checks that exact lock-only delta, preserved hashes/origins, truthful dirty
status, distinct checkout UUID/root, shared native source identity, correct
linked branch/revision, bound canonical NEXT, unchanged primary checkout, and
linked freshness after the primary branch advances. The existing clean assertion
belongs to the earlier bounded footprint contract; the original is retained
unchanged with its failure and is explicitly deselected from the final maintained
selection in favor of this successor. The Git-baseline import and shared-stage
originals remain selected and need no fixture replacement.

`native-init-followup-results.json` records exact commands, source/runtime/patch
hashes, original preservation and all seven exit codes. Adjacent before/candidate/
successor log/XML files retain failures and passes. Candidate proof remains
separate from the later final integrated matrix. These are author checks, not an
independent review, host lifecycle acceptance or selected pilot.
