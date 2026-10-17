# FPR-4 repairs and explicit contract replacements

This record separates a reproduced product regression from two changed fixture
contracts. All original tests and raw failures remain intact. The preservation
repair was validated in a newly extracted, disposable source installation while
the initial combined selection continued against the unchanged opening runtime.
**Candidate validation is not a final run on the integration checkout, an
independent FPR-5 review, or release acceptance.** Final integration evidence is
recorded separately in the closing section below.

Opening HEAD was `6289d2823184a63e2968d2c5f6a76abab5818368`; runtime was
`7d38764f026848d7d89d81abedfc62f1de5eefde6443d0032d770c2ff09a20d1`.
The init-only candidate runtime was
`8cc298eee30563542ad530116c401c0b91b8c04ab95b9f823c9245879f34065d`.
[Candidate setup](init-preservation-candidate-setup.json) records the current-HEAD
archive hash, new installation root, conventional venv, exact offline dependency
versions and patch hash
`2898bb55305619e1d379b47a3cc47be862cea11816c656fa004e809823f742bb`.

## Fresh initialization must preserve existing consumer assets

The unchanged
[`test_generated_commands_handle_spaces_and_do_not_overwrite_host_instructions`](../../../tests/fpr1/test_bookends.py)
failed because FPR-3's full footprint includes `.claude/skills/print-next/SKILL.md`,
but fresh `initialize` refused every existing mapped asset except ignore files.
The refusal protected existing bytes while preventing a supported initialization.
Shell quoting was never reached; this was a preservation regression, not an
obsolete host-instruction expectation. The targeted reproduction failed once in
0.24 seconds: [before log](bookend-before.log), [XML](bookend-before.xml).

The selected repair removes existing portable skills, rules, policies and
reference documents from the replacement mapping, keeps their exact bytes and
modes, and records them as `origin: preserved` through the existing footprint
writer. Existing living documents remain preserved, and unrelated instructions
and ledger content are untouched. Fresh collisions with the bound launcher,
registered event hooks, generated bound guidance and executable Muse bridge
wrapper continue to refuse; portable-asset preservation grants no authority to
adopt those operational bindings.

Preserved assets receive captured byte-digest/mode snapshots. The existing write
callback rechecks them after acquiring the directory lock and before every atomic
replacement, refusing drift rather than publishing a stale ownership record.
Configuration remains last in the existing per-file write sequence; this does
not create a filesystem transaction or change authority/CAS protections.

New [preservation regressions](../../../tests/fpr4/test_init_preservation.py) cover
six Claude/Cursor skill, rule, policy and reference paths; owner modes including
executable mode; read-only preview; repeat init/sync; exact lock origins/digests;
four operational collisions; and byte/mode races after lock and before replacement.
Before repair, ten cases failed at the existing refusal and four collision cases
passed: [log](init-preservation-before.log), [XML](init-preservation-before.xml).
The isolated candidate passed all fourteen plus the unchanged original bookend
test: **15 passed in 31.00 seconds**, no errors/skips
([log](init-preservation-candidate.log), [XML](init-preservation-candidate.xml)).
[Structured results](init-preservation-candidate-results.json) retain exact
commands, exit codes, source/test hashes and original-file preservation checks.

## Native import and linked-checkout consequences

The same fresh-init refusal blocked inherited portable skills in
[`test_committed_git_baseline_import_isolated_from_owner_edits`](../../../tests/muse/test_handoffs.py).
It failed in 4.58 seconds on opening source and passed unchanged in 9.96 seconds
on the preservation candidate: [before log](native-import-before.log),
[before XML](native-import-before.xml), [candidate log](native-import-candidate.log),
[candidate XML](native-import-candidate.xml). The original remains a maintained
case; it needs no contract replacement.

The unchanged
[`test_shared_native_stage_is_readonly_and_visible_in_linked_checkout`](../../../tests/muse/test_product.py)
also failed on inherited-skill initialization in 14.92 seconds and passed on the
candidate in 23.16 seconds, with its read-only/shared-stage assertions intact:
[before log](native-stage-before.log), [before XML](native-stage-before.xml),
[candidate log](native-stage-candidate.log), [candidate XML](native-stage-candidate.xml).
It remains selected without replacement.

The original native linked-worktree case also initially failed on an inherited
skill ([before log](native-linked-before.log), [XML](native-linked-before.xml)).
After the candidate repair, initialization succeeded and the original then failed
its earlier `dirty is False` expectation
([candidate log](native-linked-candidate.log), [XML](native-linked-candidate.xml)).
The [exact portable byte/mode comparison](native-linked-candidate-diff.json)
shows only `.overseer/version.lock` changes: the new checkout's bound launcher
digest differs, and inherited assets receive preserved ownership records.
Native dirty status truthfully reports that tracked metadata change.

The explicit [linked-checkout successor](../../../tests/fpr4/test_native_linked_footprint.py)
asserts that sole portable delta, exact retained hashes, preserved origins,
truthful dirty status, distinct checkout UUID/root, shared native source identity,
correct branch/revision, bound NEXT, unchanged primary checkout, and linked
freshness after the primary branch advances. It passed on the candidate in
32.52 seconds: [log](native-linked-successor.log), [XML](native-linked-successor.xml).
The original clean-after-init assertion is retained with an explicit disposition;
dirty reporting and tracked-binding semantics are not weakened to satisfy it.
[Native follow-up results](native-init-followup-results.json) identify both exact
selectors, the replacement, all seven runs and their source/runtime hashes.

## Standalone dependencies: preserve the original, provision the full contract

The unchanged
[`test_fresh_standalone_git_install_without_muse`](../../../tests/v1/test_adoption.py)
provisions only `yaml`, reflecting the earlier bounded runtime. Restored status
now reaches routing/cost/governance/honesty provenance, which imports the declared
`cryptography` dependency. Init succeeded; status failed on the missing package:
**1 failed in 3.42 seconds** ([log](standalone-before.log), [XML](standalone-before.xml)).
This requires a fixture-contract replacement, not a production dependency repair.

The [full-dependency successor](../../../tests/fpr4/test_standalone_dependencies.py)
provisions exactly PyYAML 6.0.3, cryptography 49.0.0, cffi 2.1.0 and pycparser 3.0
offline into a fresh conventional venv. It verifies versions and isolated module
paths, exercises native Ed25519 sign/verify, confirms Muse/pip/pytest are absent,
and runs actual source/bound init/status/next/sync while checking runtime/root
binding and preserved config/NEXT. It passed on the opening integration source:
**1 passed in 6.48 seconds** ([log](standalone-after.log), [XML](standalone-after.xml)).
[Structured dependency results](standalone-results.json) retain exact commands,
pins, hashes and original-test preservation. Same-platform distribution copies
do not establish wheel portability or close the separately unresolved complete
Python 3.11 dependency cell.

## Mirror delta: stage the full native footprint before approval

The original
[`test_add_change_delete_and_no_content_source_commit`](../../../tests/muse/test_mirror.py)
failed in 18.04 seconds ([log](mirror-delta-before.log), [XML](mirror-delta-before.xml)).
Its fixture uses rc5 `code add .`, which omits hidden directories. The later
`commit --allow-empty` therefore adds seventeen previously unstaged portable
skills/policies/reference/lock files. [Native snapshot and Git diff evidence](mirror-delta-before-diff.json)
confirms actual source and projection content changed, so the mirror's `prepared`
result was correct. No mirror production patch is warranted.

The [explicit full-footprint successor](../../../tests/fpr4/test_mirror_full_footprint.py)
stages those hidden portable assets before approving the initial revision, then
reuses the original add/change/delete, fake interrupted-delivery retry and
no-content correspondence assertions unchanged. Additional assertions confirm
the complete hidden footprint is projected, local bindings remain excluded,
final app/addition bytes match, and the final native snapshots and Git trees
are identical. It passed on the opening runtime in **26.75 seconds**:
[log](mirror-delta-successor.log), [XML](mirror-delta-successor.xml),
[exact commands/hashes/disposition](mirror-delta-results.json).
The original fixture and failure remain preserved with an explicit replacement.

## Final integration evidence

The chosen initialization repair was applied to the integration checkout. The
final runtime is `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`;
[complete production delta](production-complete.json) records all six changed
product files, including template/guidance and repeated-bundling repairs.
[Runtime refresh](runtime-refresh.json) preserved all non-runtime settings,
identity, existing NEXT and hooks. All 393 original test/support files remain
byte-identical. No candidate result is relabelled as a final-root result.

The final-root [focused repair run](affected-final.json) passed 32 cases in
124.42 seconds, with no failures/errors/skips and unchanged boundaries. The
[frozen final combined run](combined-final.json) recorded 1,207 passed / 1 failed,
zero errors/skips, exact-once execution and unchanged source/dependencies. All
11 initial failures have passing unchanged-original or explicit successor
coverage in that raw run; [the disposition](initial-failure-disposition.json)
links each exact outcome while preserving original failures.

The final raw failure is the unchanged FPR-1 no-provider-definition-import
assertion. [Clean-process evidence](import-boundary.md) establishes that restored
Git status loads pure definitions without loading native Muse or invoking a
provider. Its explicit additive successor passed two cases in the
[affected final-root run](import-boundary-final-rerun.json) on unchanged production
and dependencies. The raw 1,207/1 result stays separate; it is not rewritten as a
green run. The initial six replacements and this seventh replacement are listed
in the [closeout selection](disposition-closeout-selection.json); original
selectors and hashes remain preserved.

See the [combined report](../FPR-4-COMBINED.md) for group counts, package/native and
new rollback evidence, the unresolved complete Python 3.11 dependency cell,
owner host/platform/pilot/reviewer choices, and exact scope. These are author
checks, not the reserved independent FPR-5 review or release acceptance.
