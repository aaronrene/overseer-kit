# FPR-4 test disposition and selected regression coverage

This is author validation. It does not supply the FPR-5 independent review,
release certification, hosted execution, or an integrated pilot verdict.

The audit in `disposition-audit.json` verifies all **393 original files** against
their FPR-3 SHA-256 values. All remain unchanged. It maps all **324 original test
files**, their fixture/support files, and every one of the **104 historical
failures** to a selected original case or concrete current-contract successor
nodes. Twenty of those historical failed nodes are directly selected again.
The prior **1,391 passed / 104 failed** record is retained without reclassification.
Final raw evidence resolves all 104 mappings: **20 selected originals and their
successors passed**, and **84 current-contract successor mappings passed**.
Across the 393 files, 118 have selected original/current-successor passes, 202
have passing current successors without rerunning their archived contracts, 69
are support files rather than test passes, and four completed bounded-pilot
families remain preserved and were not rerun. Exact case identities and outcomes
are linked through `disposition-final-outcomes.json`.

The initial combined selection recorded **1,159 passed / 11 failed / 0 skipped**
on unchanged opening runtime. `initial-failure-disposition.json` maps all eleven
failures to concrete causes and evidence: five original cases remain selected
after product repairs and six have explicit contract/fixture successors. The
final-runtime affected selection passed **32 cases** with exact collection and
unchanged boundaries. The frozen combined matrix subsequently passed all five
repaired originals and the selected successors for the other six initial failures.
Their raw initial failures remain preserved.

The frozen combined matrix recorded **1,207 passed / 1 failed / 0 skipped**,
with all 1,208 cases executed exactly once on unchanged source and dependencies.
Its failure is the old no-provider-definition-import assertion described below.
Two new successor cases then passed on the same production and dependency
boundary. Lossless collection of the separate closeout selection proves that its
**1,209 current-contract cases** equal the 1,207 passing raw cases plus those two
successors, with no duplicate, missing or extra case. See
`disposition-closeout-coverage.json`. This is combined-plus-affected coverage;
the raw combined result remains failed and is not relabelled green.

`disposition-selection.json` is the immutable initial combined selection.
`disposition-final-selection.json` adds the current app unit cases and explicitly
deselects six preserved tests: the bounded unsupported-command assertion, the
standalone fixture that omits required full Python dependencies, the native
linked-checkout assertion that tracked footprint initialization stays clean,
the mirror fixture whose intended no-content commit adds hidden files, the old
direct-export/implicit-push script assertions, and the old numbered orchestrator
marker and handoff text assertions.
The linked-checkout successor proves that only `version.lock` changes for the new
launcher digest and preserved origins, and retains identity/isolation/freshness
checks. The mirror correction explicitly stages the full hidden footprint before
first approval and proves equal native snapshots and Git trees for the no-content
revision. The original fixture's `code add .` omitted dot-directories, so its later
commit actually added 17 restored hidden files; the product correctly reported a
content change. This is a fixture correction, not a product defect. Its successor
passed in 26.75 seconds on the opening runtime; raw before/after evidence is in
`mirror-delta-results.json` and `mirror-delta-before-diff.json`.
Their replacements and initial failures are named in that file. There are no new
skips, xfails, or testpaths filters.

`disposition-closeout-selection.json` separately adds the seventh explicit
replacement: `test_git_core_imports_no_muse_or_provider_engine`. Restored full
status imports pure provider protocols/dataclass definitions through type
annotations; the old module-prefix assertion conflates those definitions with
provider activity and depends on earlier collection imports. Its original source
and raw failure remain unchanged. The clean-process successor runs actual Git
bootstrap status with local and API reviewer settings, forbids native Muse and
Muse-adapter imports, provider function/construction activity, sockets, and every
subprocess except hardened read-only local Git. It verifies full status, exact
identity and unchanged bytes/modes/mtimes. Both cases passed in the separately
recorded `import-boundary-final-rerun.json`; rationale and full observations are
in `import-boundary.md` and `import-boundary-probes.json`. An earlier runner command
exited 4 on an unavailable `--muse-python` pytest option; its raw record is retained,
and the corrected environment-based invocation changed no product or test source.

The rendered mirror wrapper successor executes a fake bound launcher from a
fixture root containing spaces. It proves missing-launcher refusal, physical-root
selection, literal arguments, sanitized PATH and exit propagation. The native
mirror suite separately exercises isolated targets and explicit fake delivery.
The orchestrator successor checks installed canonical-NEXT/identity/CAS guidance,
separate effects and evidence, configured review gates, explicit skill discovery,
an opt-in review loop and both host skill footprints. RULE #8 and raw legacy docs
tokens are not restored as product requirements.

The missing build-verification reference in the templates was a maintained
guidance gap. Conditional accepted-action/configured-gate guidance now points to
the shipped skill without adding automatic review chains. The original
`test_rendered_templates_include_build_verification_in_dod` stays selected and
passed unchanged. The focused tail check passed eight cases in 3.07 seconds;
its initial new orchestrator assertion failed only because of line wrapping,
then passed after whitespace normalization without another product change.

The selection combines all maintained foundation/authority/product/Muse/FPR-4
directories with 93 complete original files and 49 individual engine nodes from
24 mixed historical files, plus nine app unit selectors. Original engine cases
cover data integrity, security, performance, stress, review/evidence/ledger,
checkpoints, policy/cost routing, adapters, post-land sync, and hosted services.
Passing an old engine algorithm test does not restore an obsolete CLI boundary
or HANDOVER-generated prompt contract.

The audit corrects several overly broad FPR-3 mappings:

- LAC failures include app identity, static UI, concurrency and shutdown, so
  source-site validation alone was insufficient. Current tests exercise those
  bound app outcomes and assert explicit repository/source-install guidance.
- Missing signed-desktop workflow files map to the actual manual-only workflow,
  read-only permissions, absence of publishing steps, secret scanning and actual
  source archive tests. Signing and publishing are not claimed.
- The compatibility `overseer` spelling preserves JSON and literal arguments.
  Its old per-process deprecation warning is explicitly superseded.
- Workspace freshness uses canonical NEXT and optional whole-file pins. Archived
  HANDOVER prompt sections cannot become actionable. Strict board-name failures
  use the current member-error/exit-35 result, and optional-member strictness is
  selected with `workspace status --strict-all`.
- Generic force/promotion is refused. The successor proves that modified
  consumer content survives and `--preserve-modified` records its ownership.

`test_disposition_contracts.py` adds the missing bound successors. Focused checks
retained the original app startup/status/document/static latency budgets, a
200 KB document, 24 concurrent requests with 20 workers, five desktop launch/stop
cycles with distinct ephemeral secrets, CLI status under one second, footprint
checks under five seconds, and workflow scanning under one second. It also
checks restricted routes, request/document size refusal, session-secret
nonpersistence, SIGINT shutdown, canonical workspace reads, and unchanged fixture
bytes. Hosted CLI shutdown requests static `/` only; its configured upstream is
never requested. Separate hosted projection tests use `FixtureUpstream`.

The old LAC health benchmark assumed a path-only unvalidated health response.
Its 200-call/0.25-second threshold is explicitly superseded by current identity
and runtime validation. This audit does not claim that historical threshold
passed. Current bound health, status, document and static budgets are tested.

The selected-original safety audit records all 118 selected historical files.
Provider cases use fake transports or missing-credential refusals. Hosted cases
use loopback sockets and an in-memory upstream. Landing uses fake `gh`/Git
runners, except two local Git data-integrity/e2e families whose real clone,
push, fetch, pull and readback target a newly created `tmp_path/origin.git`.
Checkpoint commands execute copied fixture scripts. Absolute path and URL strings
in security cases are inert input or pre-transport refusals. This was source and
fixture inspection, not a runtime network trace.

Exact focused commands, exit codes and XML references are in
`disposition-results.json`. The first focused run exposed four incorrect new
test expectations; they were corrected against documented current contracts.
The expanded successor run passed nine cases. The subsequent 24-request stress
and legacy budget checks passed four cases, and the expanded workspace check
passed. A separate failing-before check identified a real product defect: the
app UI still advertised signed DMG downloads and ambient repository fallback.
That failure is preserved in `disposition-ui-before.xml`; the final combined run
validated the repair in `combined-final-latency.xml` on runtime
`bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`.
The failed-before and passing-after observations remain separate.

`disposition-runner-audit.json` records the final execution-driver checks. The
driver preserves lossless node IDs, validates JUnit identities using a per-case
SHA-256, and compares the combined selection with the union of actual disjoint
groups. Synthetic checks include class methods, `::` inside IDs, a 160 KB ID,
intentional skips and duplicate collection. Runtime, tests, desktop sources and
locks, validation scripts, packaging inputs, Git state, both Python environments,
and dependency/source hashes are compared before and after every group. Latency
tests run after the concurrent groups, and source-archive determinism runs last.
These recorder checks do not replace the final product suite.

Actual desktop bundler repetition exposed a separate archive-reservation defect.
The repaired script reserves a distinct private directory atomically, then builds
`source.tar.gz` inside it. The selected successor runs the real script twice under
one TMPDIR, checks mode-0700 distinct directories, retained archives, identical
archive/manifest bytes and verified resource modes/runtime. Focused evidence is
in `distribution-bundler-repair.json` and `distribution-bundler-regression.xml`.
The same successor passed in the frozen `combined-final-surfaces.xml` group.
The bundler is outside the product runtime digest, so the final runner also
freezes every `scripts/` file in its packaging-source boundary. Prior synthetic
driver hashes remain recorded separately from that final boundary extension.

Completed bounded pilot/certification evidence stays preserved. No real consumer,
old worktree, live provider, remote publication, native host event delivery, or new
pilot was used by this audit. Required release evidence outside the authorized
FPR-4 fixture work remains pending.
