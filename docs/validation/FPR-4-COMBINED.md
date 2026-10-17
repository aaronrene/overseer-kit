# FPR-4 — integrated validation and bounded repairs

This action performs the owner-accepted local section-9 validation. It does not
perform FPR-5, repeat bounded certification, or authorize release. The required
Python 3.11 dependency cell, named host/platform acceptance, new integrated pilot
and independent reviewer remain separate unresolved requirements. A passing
fixture selection does not resolve them.

## Recorded boundary

Physical cwd and Git top-level:
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`.
Branch: `feat/overseer-v1-recovery-20261014`. Clean opening HEAD:
`6289d2823184a63e2968d2c5f6a76abab5818368`, whose sole predecessor is
`695444fb5f8261391f5c273807129c13dc8db1fd`. Bound `status` and `next` validated
`overseer-kit`, UUID `6988dc4a-5f22-454b-9d68-ac5905b383bf`, product lane,
GPT-6 Astra and FPR-4. Opening runtime was
`7d38764f026848d7d89d81abedfc62f1de5eefde6443d0032d770c2ff09a20d1`;
opening NEXT SHA-256 was
`0b6ef939df67ff2a2f5a4321c7787f56a4d0e804e7b433c30eccde162295dfb0`.
[Opening record](fpr4/opening.json) includes the Git tree, complete runtime file
hashes, dependency versions, refs and preserved evidence hashes.

P `e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`, M
`32254cd939885d9d6f40634997ea5b9c37ea776c`, main
`d47291d5d9030de5ebef713da95efa978c4d8c6e` and repaired B
`348e0f323a3b17cd5022a1bfd56fa09a6831c51f` were verified here as committed objects.
The FPR-3 source map remains the implementation provenance; this wave's bounded
changes and before/after results are recorded separately below. No older
worktree, preserved Muse history, snapshot, completed pilot, rollback fixture or
bounded source-release directory was used as a test target.

## Combined selection and historical disposition

The [case audit](fpr4/disposition-audit.json) accounts for all **393 original
test/support files**, including 324 test files, and **all 104 historical failures**.
Original files retain their hashes. Its concrete selected nodes replace changed
entrypoint, configuration, prompt-authority and lifecycle contracts; retained
algorithms and cross-cutting security/integrity/performance/stress families remain
selected. The original **1,391 passed / 104 failed** report is unchanged.

The [initial selection](fpr4/disposition-selection.json) and
[frozen final-run selection](fpr4/disposition-final-selection.json) are explicit.
The [current-contract closeout selection](fpr4/disposition-closeout-selection.json)
adds the separately verified clean-process import successor and its explicit
original-node deselection; it does not rewrite the raw final run. No required
capability is removed through skip/xfail. Bounded-era assertions that reject
restored commands and provision a YAML-only standalone runtime remain unchanged
with their recorded failures; actual maintained-command/effect checks and a fresh
full-pinned-dependency/no-Muse installation replace those contracts. A linked
native checkout now truthfully reports its changed tracked footprint lock as
dirty. The mirror no-content fixture must stage the restored hidden portable
assets before its first approval; otherwise its later snapshot really changes.
Explicit successors preserve the requirements and prove these corrected inputs.
The other two replacements cover the current bound mirror wrapper instead of
legacy export/automatic push, and canonical/configured review semantics instead
of numbered rules and unexpanded historical prompt markers. All six initial original
nodes remain byte-identical and their failures are retained. A seventh explicit
replacement follows the final run: full Git status may load pure provider type
definitions while remaining independent of native Muse and provider actions.
Its fresh-process successor blocks native imports, provider calls, network and
all subprocesses except hardened read-only local Git. The original import-prefix
assertion and its failed result remain intact; see
[exact imports and guarded evidence](fpr4/import-boundary.md).
The [standalone comparison](fpr4/standalone-results.json) retains failing-before
and passing-after evidence without altering the original test.

Reproduction uses this installation's conventional venv:

```sh
.venv/bin/python -B scripts/fpr4_matrix.py --name new-combined-run \
  --selection docs/validation/fpr4/disposition-closeout-selection.json \
  --muse-python /absolute/separate/pinned/muse/venv/bin/python
```

This command reproduces the current-contract selection. The recorded frozen
final run used `disposition-final-selection.json` and its captured test hashes,
before the additive import successor.

The runner executes one selection in disjoint file groups, followed by isolated
latency checks and the source-archive case. Lossless collection records and JUnit
node identities prove every selected case ran exactly once. Each group uses a
new nonrepository `/private/tmp` fixture parent. The runner refuses to overwrite
prior evidence and records exact argv, exit status, source/runtime hashes, test
sources, native/packaging inputs, validation scripts, Python/Muse dependencies,
logs and JUnit results. Boundary comparisons require the same source and
dependency set before and after every group. `scripts/fpr4_run.py` also supports
the same explicit selection serially. Real
loopback sockets require the local execution permission demonstrated here; the
initial sandbox denial and successful bounded escalation are both retained.
Providers/upstreams are fake; Git/Muse object and local repository operations
are confined to newly created fixtures. No external network/provider operation
or actual remote delivery was used.

## Section-9 evidence matrix

| Required group | Evidence and acceptance boundary |
| --- | --- |
| Three modes and independent identity | Native pinned Muse rc5 plus Git fixtures; explicit Git-only/Muse-only/mirror selection, UUID/runtime binding, dirty/shared-stage and no-fallback cases. New composition cases keep two repositories active with different defaults and overlapping lanes in each mode. |
| Lanes and workspace | Whole-file collection CAS, independent lane freshness/ownership, missing/stale lanes, explicit workspace required/optional members and UUID collisions; nested and linked boundaries remain isolated. |
| Manual and automatic bookends | Canonical manual/start/stop equality and read-only snapshots, wrong/malformed/copied inputs, Git exact closing commit and Muse exact-revision rules, schema compatibility and context races. Cursor event fixtures and instruction-triggered Codex reads do not establish named-client native delivery. |
| Full workflow and settings | Actual dispatcher/help/subcommands, full status/governance/review/Check OK/checkpoints/ledger/routing/landing/compaction; full-settings preservation and fake provider/transport outcomes. No public legacy dispatcher or regenerated handoff is selected. |
| App, desktop and hosted controls | Auth/CSRF/origin/path/identity controls; concurrent reads, document/static size and latency bounds, session-secret nonpersistence, repeated desktop child shutdown, actual app/hosted CLI SIGINT and hosted write refusal. Hosted lifecycle starts without making an upstream request. |
| Legacy migrations | Full-settings two-lane migration, byte-exact backup/semantic preservation, explicit prompt draft acceptance and publication, preserved rules/policies/ledger, contradictory inputs and partial-resume cases. |
| Bounded migrations | Schema-1 Git and schema-2 native/config migration, explicit adopt/restore and tracked-binding preservation/refusal; no silent untracking or authority inference. |
| Mirrors, reconciliation and credentials | Pinned native objects and isolated Git targets; complete bundles/deltas, exclusions/modes/dotfiles/parents, correspondence/CAS, retries and scoped credential challenge protocol with fake credentials/transports. |
| Fresh source installation | Frozen deterministic source archive, complete file/mode manifest, unpack/repack equality, no local bindings/secrets/venv/fallback, advertised launchers and real authenticated app/desktop child from its own fresh venv. |
| Upgrade and rollback | New fixed-root previous FPR-2 → integrated current → previous → current; full settings/two lanes/docs/NEXT preserved. Separate B schema-1 → schema-3 cycle proves old-runtime refusal until byte-exact matching configuration is restored. Existing bounded exercise is untouched. |
| Environment and native build | Python 3.14.4 with exact declared dependencies and pinned Muse 0.2.1rc5; local macOS arm64 Rust 1.88 locked/offline native build. Python 3.11.15 full matrix remains blocked by absent pinned cffi 2.1.0 cp311 backend. |
| New integrated pilot | **Not run.** Owner project/host/authority selection and authorization remain pending; no fixture result is labelled a pilot. The completed bounded pilot is preserved. |

[Composition evidence](fpr4/composition-results.json) and
[distribution/environment notes](fpr4/distribution-notes.md) give concrete paths,
commands, hashes and limits. The rollback script is
`scripts/fpr4_rollback.py`; its recorded source commits distinguish compatible
previous FPR-2 from repaired bounded B. No R1/R2-defective predecessor is relabelled
safe by operability checks.

## Failures, repairs and final result

The complete initial selection ran **1,170 cases: 1,159 passed, 11 failed,
zero errors/skips**, in 2,835.21 seconds. Its opening runtime stayed unchanged:
[record](fpr4/combined-first.json), [raw log](fpr4/combined-first.log),
[JUnit](fpr4/combined-first.xml). This is a recorded failing run, not a final
product verdict. The frozen final-run selection includes added regressions and the six
initial explicit replacements; it collected and executed **1,208 cases**.

The shared initialization regression refused preexisting portable skills,
rules, policies and references when the full footprint was restored. The repair
preserves their exact bytes/modes, records consumer ownership, and rechecks their
snapshots after locking and before replacement. Operational launcher/hook/bound
instruction collisions still refuse. Existing context, confinement, freshness
and whole-file CAS checks remain in force. Before/candidate evidence and the
native import/worktree consequences are in [repair details](fpr4/repairs.md).

The handover template now includes its configured path. Both summary templates
and the orchestrator again point to maintained build-verification skills when
the accepted action or configured gates require them. Review loops stay explicit,
and author checks do not become independent review. The unchanged original
template guidance test passes after this repair. App guidance now
describes source installation and an explicit desktop repository instead of an
unvalidated signed installer and environment fallback. Both defects have retained
failing-before evidence. These changes do not establish installer or host
acceptance.

Fresh package/native preparation also exposed repeated desktop bundling failure:
BSD `mktemp` left a nonterminal-X template literal, and the next invocation
collided with the earlier archive. The repaired script atomically reserves a
private directory and keeps the archive inside. An actual repeated-script
regression uses the same TMPDIR and proves distinct private directories,
identical archive/manifests/runtime and preservation of both archives. The
standalone script is included in the final matrix's packaging hash boundary.

The [complete production delta](fpr4/production-complete.json) records six
changed product files and the final bound runtime
`bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`.
[Explicit runtime refresh](fpr4/runtime-refresh.json) preserved every non-runtime
setting, UUID/root/lane/model, exact existing NEXT and hook files. Only the
launcher was selected for sync; no full-footprint overwrite or hook activation
was performed. Existing installation footprint drift remains separately visible.

The final focused repair selection passed **32 cases**, no failures/errors/skips,
in 124.42 seconds, with exact collection and unchanged source/dependency boundaries
([record](fpr4/affected-final.json), [JUnit](fpr4/affected-final.xml)). The
subsequent bundler regression passed one case plus five separately recorded direct
checks. The new final-runtime rollback exercise passed **13 checks**
([record](fpr4/rollback-final.json)). These are separate runs, never summed into
the combined result.

The repaired source artifact has SHA-256
`fd6b5ebe0fcd87156f15d610a6b8e76beec1ac469ce07b2958a8e5fa961010cd` and a
1,220-file manifest with SHA-256
`f1297351f0d0e1bd6e4dd6481193d36a6708bb2ddf488e62643864216a70a1b8`.
Fresh own-venv Python 3.14 entrypoints, complete unchanged footprint,
authenticated app/desktop child and shutdown, exact resource runtime and the
locked/offline native build passed; see the [distribution summary](fpr4/distribution-summary.json).
The archive freezes the repaired production/test/driver files; reporting and
validation logs continued afterward, so final outcome evidence lives here.
The Python 3.11 affected template rerun passes, but its complete dependency and
Git matrix remains unresolved. Earlier package failures, the interrupted
redundant run and the temporary-directory workaround remain in the evidence.

The final combined run recorded **1,207 passed / 1 failed, zero errors/skips**
([record](fpr4/combined-final.json)). Every case ran exactly once; the complete
production/runtime, test, script, native, packaging, interpreter, dependency,
Muse and ref boundaries stayed unchanged across all eight groups. Their results:

| Group | Passed | Failed | Errors/skips |
| --- | ---: | ---: | ---: |
| Git foundation | 195 | 0 | 0 |
| FPR-1 foundation | 117 | 1 | 0 |
| FPR-2/3/4 product surfaces | 91 | 0 | 0 |
| Native mirrors and reconciliation | 101 | 0 | 0 |
| Other native authority | 60 | 0 | 0 |
| Retained engines and cross-cutting families | 611 | 0 | 0 |
| Isolated latency and lifecycle | 31 | 0 | 0 |
| Deferred source archive | 1 | 0 | 0 |

The raw run exits 1 and is **not green**. Its sole failed original assertion
forbids any provider-definition import; restored full status succeeds but loads
pure type definitions through `cli.context`. The initial monolithic run had
preloaded those modules during collection, so its pass did not establish a clean
import boundary. No production repair or import preloading was used to hide the
failure. After the freeze ended, the portable successor was added and passed
**2 cases in 6.97 seconds**, exit 0, with exact execution and unchanged production,
Muse and dependencies ([record](fpr4/import-boundary-final-rerun.json),
[JUnit](fpr4/import-boundary-final-rerun.xml)). It tests local and API settings,
actual isolated bootstrap, complete status identity/fields, no native Muse or
provider/network actions, and unchanged repository bytes/modes/mtimes.

The first affected invocation incorrectly supplied pytest's native-only
`--muse-python` option without selecting native conftest; it exited 4 before
collection ([log](fpr4/import-boundary-final.log)). The corrected invocation
supplied the same pinned interpreter through `FPR2_MUSE_PYTHON` for dependency
recording. Both attempts remain preserved; this was an operator command error.
The final [outcome audit](fpr4/disposition-final-outcomes.json) maps raw and
supplemental cases separately to all historical rows and initial failures. All
104 rows have passing current-contract coverage: 20 selected originals plus
successors, and 84 explicit successor mappings. The 393-file inventory comprises
118 selected-original/successor families, 202 successor-covered archived
contracts, 69 support files, and four preserved completed-pilot families. All
11 initial failures have passing repaired-original or explicit replacement
evidence in the final raw run.
The [lossless closeout collection proof](fpr4/disposition-closeout-coverage.json)
verifies that the **1,209-case current-contract selection** equals exactly the
1,207 raw passing cases plus the two explicit successors, without duplicates,
missing cases or the excluded failed original. This is coverage assembled from
recorded runs, not a second all-green combined execution. Only the additive test
changed executable test sources; the later tests/README edit documents this
selection and changes no test behavior.
The original historical baseline and all failed raw outcomes remain unchanged.

[Closing artifact equivalence](fpr4/distribution-closeout-equivalence.json)
compares every production/package file with the exercised artifact. Later
successor tests and reporting do not change that production installation/native
build claim. Development failures and missing prerequisites remain alongside
passing outcomes.

## Owner choices and successor boundary

[Owner choices](fpr4/owner-choices.json) remain pending for named automatic
client/version guarantees, platform/distribution acceptance, the new disposable
pilot and the independent FPR-5 reviewer. The proposed pilot is a new noncritical
Git-only project under `/private/tmp`, instruction-triggered Codex bookends and
fake remote transports; it has not been authorized or run. Native GUI sessions,
signing/notarization/installers, Windows, new hosted CI and live providers are not
claimed. The pinned Python 3.11 dependency failure is an unresolved required
matrix cell, not a platform scope reduction.

The [closing source audit](fpr4/closing-source.json) verifies all 393 original
files, preserved historical records/hooks, all 144 precommit refs, non-runtime
settings and final bound runtime. After the frozen matrix, one executable test
was added and tests/README plus reporting documents were updated; production,
runtime, drivers and dependencies remained unchanged. The sole FPR-5
successor was published through the bound writer with explicit current context
and the expected opening NEXT digest ([publication](fpr4/next-publication.json));
its precommit readback validated. The local closing commit and postcommit bound
readback are reported at closeout; no FPR-5 execution is part of this action.

All collaborators in this action supplied author implementation/validation work.
None counts as the independent final reviewer. FPR-5 is the single successor:
one independent review of fixed integrated source and this evidence, bounded
repairs if needed, one final adjudication, then a separate owner release decision.
Unresolved required evidence prevents release readiness. No release, merge,
push, publication, signing or deployment authority follows from FPR-4 or FPR-5.
