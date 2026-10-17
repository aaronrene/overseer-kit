# FPR-2 authority, controlled mirrors and repository lanes

Owner-accepted action: `OVERSEER-FULL-PRODUCT-RESTORATION-AUTHORITY-2`.
This is focused author implementation evidence for section 8 of the
[restoration plan](../decisions/FULL-PRODUCT-RESTORATION-PLAN.md), not FPR-4
combined validation, independent FPR-5 review or release readiness.

## Opening boundary

The physical cwd and Git top-level matched
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`;
branch `feat/overseer-v1-recovery-20261014`; full opening HEAD
`8c2b642336e29a3a5a781f70f25f4769e6899642`, with sole parent
`521c8df5cf2c57d876cdd44adfd1cbc34063d416`. The worktree was clean.
Bound status and NEXT verified name `overseer-kit`, UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`, product lane, GPT-6 Astra and
runtime `dbe7e93e6797611ac410d4e94f40ba7ea34c4419b1389568b3579d558eb353db`.
Canonical NEXT digest was
`15efa968ea3bcbe6e5f280bd7cd079f68e5d1f3fa1728246259799a01d582e3c`.
The exact FPR-1 closing relationship and disk/committed NEXT passed the bound
reader. All required documents, including the full plan, were read first.

P/M/main matched the supplied pins; repaired B was a committed object. Sources
were read here with `git show`; no older worktree was entered, merged,
cherry-picked or reverted. No preserved Muse history, snapshot, rollback fixture,
bounded pilot or bounded source-release directory was used as a test target.

## Source selection and acceptance map

The [machine source map](fpr2/source-map.json) records immutable pins and exact
versus adapted modules. The active source remains the FPR-1 integration branch.

| Surface | Source/disposition | Focused acceptance |
| --- | --- | --- |
| Native reads | M `v1_revision`, `v1_muse_reader`; normalized backend projection adapted | Explicit Git/Muse selection, nearest VCS boundary, separate native venv, source/store/runtime checks, linked branch identity, read-only dirty/shared-stage reads, no Git fallback |
| Scoped credentials | M tip `v1_git_credential`, exact repaired helper | Real local Git credential protocol with fake gh/token, repeatable challenge metadata, wrong host/path/protocol refusal, no persistent credential config or token diagnostics |
| Mirror/history | M `v1_mirror`, `v1_mirror_reader`, `v1_mirror_history`; mirror config boundary, final/runtime checks and native secret-path projection adapted; history retained | Isolated owned bare targets, path/mode/secret bounds, binary trees, complete bundle/exact delta/two-parent reconciliation, continuation, drift and interrupted correspondence/push/PR retries |
| Local policy/adoption | M policy plus adoption ordering; new `product_authority` adapts to full schema | Exact config backup/rollback, retained settings/NEXT/identity, explicit tracked-binding preservation or separate untracking, old-authority unavailable rollback, expected config/revision and config-last writes |
| Git/native context and NEXT writer | B repaired `v1` and `v1_io` retained through FPR-1 | Captured context, after-lock and before-replace checks, final read rechecks, pinned Git closing reads, whole-file CAS, Muse exact revision with no closing exception |
| Repository lanes | D/P lane intent and normalized FPR-1 owner map; new `product_next` | Strict schema-3 common binding/entry map/prompt bodies, schema-1/2 readers, explicit lane selection, visible missing/stale entries, no cross-repo ownership, concurrent lane writes, batch publication through the same writer |
| Bookends | FPR-1 bound event adapters, selection adapted | Manual and event display use the same service; root/UUID/input checks remain; no consumer hook activation or native host/version claim |
| Upgrade/bridge | D ceremony outcome; new `product_upgrade`; M bridge wrappers | Digest-pinned controlled plan, validated config before apply, retained existing settings, no export/delivery; legacy live-export flags refuse even with `--yes` |
| Legacy Muse adapter | D `rev-parse --abbrev-ref HEAD`, unchanged | Retained adapter tests; P's incompatible branch command was not imported |

The live adapter retains M's known public-staging/GitHub-HTTPS/main-source/SHA-1
limits. Tests supply fake transports; no live mirror/export/delivery, network,
provider, real consumer hook, main merge, push, tag, publication or deployment ran.
The preserved historical dispatcher is not a second entrypoint. Remaining
product commands/app/distribution surfaces belong to FPR-3.

## Test selection and changed contracts

[run-focused.sh](fpr2/run-focused.sh) reproduces the complete focused selection
with the installation's conventional venv and explicit Muse prerequisite. Its
fixtures live under a nonrepository `/private/tmp` parent. Git and native runs
are recorded separately on the same runtime manifest; they are not represented
as a completed FPR-4 full-product matrix.

- Unchanged B `tests/v1/{test_commands,test_context,test_integrity,test_isolation}`
  retain root/runtime/identity, hostile environment, confinement, unborn/closing,
  CAS and the 20 deterministic Git R1/R2 cases. Original D test/support hashes
  remain checked by `test_footprint_digest`.
- Imported M `tests/v1/test_adoption.py` retains useful adoption, response bounds
  and standalone-Git checks, adapted for normalized schema and explicit Muse
  preservation. M's blanket Git untracking/ignore requirement is intentionally
  replaced by retained tracked Git bindings; the assertion now checks that
  adoption preserves them. Config-last and concurrent input checks remain. Inactive Muse settings survive
  Git adoption in the full normalized data; only the legacy Git adapter projection
  clears their active interpretation.
- M `test_mirror_credentials.py` is retained, including repaired challenge cases.
  M `tests/muse/{test_handoffs,test_mirror,test_reconciliation}` use real local
  native/Git objects and fake delivery, with config accesses updated to the one
  normalized model. The Git-import fixture explicitly chooses exclusions rather
  than assuming Git initialization silently ignores bindings.
- New `tests/muse/test_context.py` covers native lock-wait, fsync and final-reader
  context changes. `test_product.py` covers schema-2 native migration, explicit
  mirror-mode initialization, controlled upgrade, source-switch collection reset,
  tracked preservation, native lanes and shared-stage read purity.
- New `tests/fpr2/test_lanes.py` covers whole-file concurrency, batch publication,
  stale/missing lane visibility, map/body/digest errors, event/manual equality,
  repository ownership and duplicate authority/publication selectors.
- FPR-1's two unavailable-init-authority expectations now expect the precise
  missing Muse Python prerequisite. Its fake schema-2 Muse migration test now
  expects native prerequisite refusal while asserting config preservation and
  no Git calls. Real native migration replaces the former deferred-activation
  behavior. Other FPR-1 tests remain selected.
- The same retained eight supported config/path/adapter tests and FPR-1 focused
  lane/footprint/bookend-option files remain selected, except the explicitly
  superseded `test_k7_footprint.py::test_rendered_deploy_script_safety_invariants`.
  That unchanged historical assertion requires native git-export and automatic
  push. It failed in the recorded broad run; the focused runner explicitly
  deselects it, with `test_bound_bridge_wrapper_uses_controlled_offline_service`
  replacing its public route through actual offline prepare/verify, foreign-cwd
  root binding, legacy-flag refusal and unapproved-delivery refusal. No maintained
  requirement is waived by this disposition. M's source-distribution
  and artifact-verifier tests remain FPR-3 inputs; they were not imported as an
  unimplemented distribution claim.

The historical **1,391 passed / 104 failed** baseline remains unresolved and was
not rerun or relabelled green. The bounded independent FINDINGS verdict,
certification, installation/rollback exercise and completed pilot remain intact;
none was repeated. No skip/xfail grants a missing product requirement.

## Prerequisites and development failures

The explicit local native prerequisite is
`/Users/aaronrenecarvajal/.local/share/muse/venv/bin/python`, Python 3.14.4,
Muse 0.2.1rc5. Its package-source SHA-256 is
`7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92`, matching M's
committed recovery pin. The fixture prerequisite verifies version and source
hash before use. Nothing was fetched or installed. Tests create new native stores;
the prerequisite's installed package is read-only input.

Retained development records under `fpr2/` distinguish initial failures from
final evidence:

- Git smoke: 55 passes / 3 failures. Two were the changed unavailable-Muse
  contract; one exposed missing single-lane model enforcement, which was fixed.
- First native/mirror/credential run: 70 passes / 29 failures / 72 setup errors.
  Most native setup errors had one cause: init treated Muse's existing ignore
  file as an unmanaged launcher collision. Init now preserves and extends its
  rules. Native recheck passed 14 before a concurrent author source edit caused
  a correct runtime-change refusal; that run is not a final-source verdict.
- Focused Git/R1/R2/lane/adoption run: 54 passes / one fixture cwd failure. The
  hook correctly refused a foreign cwd; the new fixture now runs at its root.
- Product checks: five passes / one actual upgrade defect. Regime-only apply
  omitted required mirror settings. Upgrade now derives missing settings from
  the approved plan, preserves existing ones, and validates before replacement.
- Development native and supported runs were explicitly interrupted to finish
  that repair and batch publication. Their interruption/teardown traces remain;
  they do not count as completed passing suites.
- The focused lane/native-product/migration recheck then passed 15 cases. Final
  stable-source suite results and any later repairs are recorded below and in
  `fpr2/results.json`.

Two additional boundary checks failed before repair and now pass in
[four focused repair cases](fpr2/repairs.log), with [JUnit evidence](fpr2/repairs.xml):

- Sync could inherit an identical branch/HEAD after fixture Git metadata moved
  to its parent. Physical Git top-level is now rechecked during captured context
  and migration checks. [Failing evidence](fpr2/boundary-before.log).
- M's projection excluded `.env` paths but could distribute a force-tracked PEM
  blob. It now also applies the pinned native built-in secret-path policy,
  covering PEM, key, p12/pfx and envrc paths without trusting force-track.
  [Failing evidence](fpr2/secret-before.log). Fixture secrets are fake strings.

The broader candidate runs were interrupted before these fixes; their raw logs
remain as `before-final-repairs-*`. They are not passing suite verdicts. The complete selections below run after both fixes on one recorded source digest.
The native selection then exposed a Git-adoption settings conflict: the historical
adapter rejected retained inactive Muse values. The normalized data now preserves
those values while its Git adapter projection leaves them inactive. The bound
wrapper also supplies its explicit physical root. Three targeted adoption/wrapper
cases passed; affected config/adoption/native cases are rerun on the final digest.
The complete-run and final affected-run digests are recorded separately.

## Installation and limits

[Explicit bound sync evidence](fpr2/installation-refresh.json) records dry-run
and apply. Only `.overseer/config.yaml` runtime binding changes; UUID, physical
root, product lane/model, all other settings, launcher and existing NEXT remain
unchanged. The [runtime manifest](fpr2/runtime-manifest.json) covers newly reachable
modules and bridge scripts. This installation remains Git-only; no authority
adoption or untracking was performed here. Active consumer hooks stay disabled.

Migration/adoption/sync use per-file atomic writes and final context checks,
not a cross-file transaction. Failed partial application retains backups and
reports paths; explicit retry/rollback remains necessary. Trusted-host limits
and the B caveat about observed changes versus change-and-reversion remain.
A differing external Muse working directory requires an explicit pairing decision;
settings are preserved and unsupported operations refuse. Native host delivery,
other platforms/Python versions, live provider behavior and complete product
surfaces are not established by this wave.

Remaining owner choices are the plan's named automatic host versions, any broader
Muse transport requirements, platform/distribution/release claims and the FPR-4
pilot/FPR-5 independent reviewer. No new choice was needed for this local wave;
fixture preservation choices were explicit. No release authority follows.

## Final verdict and closeout

[Structured results](fpr2/results.json) record **559 distinct maintained passing
cases** across the broad selections and the final affected reruns. This is not
a claim of one 559-case run on the final runtime. There are no unresolved focused
maintained-case failures or skips; the explicitly superseded historical exporter
assertion remains a recorded failure with its replacement above.

| Recorded run | Result | Runtime / evidence |
| --- | --- | --- |
| Complete Git/foundation/focused retained selection | 397 passed / one superseded legacy-export assertion failed | `13d5e7d0…3c93c9d`; [log](fpr2/git.log), [XML](fpr2/git.xml) |
| Complete native handoff/context/product selection | 57 passed / one inactive-settings adoption defect failed | Same digest; [log](fpr2/native-handoffs.log), [XML](fpr2/native-handoffs.xml); repaired below |
| Complete native mirror/reconciliation selection | 102 passed; zero failures/errors/skips | Same digest; [log](fpr2/native-mirrors.log), [XML](fpr2/native-mirrors.xml) |
| Final affected foundation/config/migration/adoption/lane/footprint selection | 169 passed; zero failures/errors/skips; one explicit historical-route deselection | `1becd740…40ed51`; [log](fpr2/affected-git.log), [XML](fpr2/affected-git.xml) |
| Final affected native handoff/adoption/product/wrapper selection | 41 passed; zero failures/errors/skips | Final digest; [log](fpr2/affected-native.log), [XML](fpr2/affected-native.xml) |

The [exact final source delta](fpr2/final-source-delta.json) reconstructs the broad
selection digest from the final files: only the normalized Git adapter's handling
of inactive Muse settings and the two bridge wrapper root arguments changed.
Affected config/adoption/native tests and real wrapper execution pass afterward.
No further owned runtime source changed. Final runtime is
`1becd740f9cb24ae722df5c135215eb4508407069705bc1116d1f2fd1f40ed51`, version
`1.0.0.dev1`; final config SHA-256 is recorded in the refresh artifact. The final
sync preserved every non-runtime setting and existing NEXT against opening HEAD.

[Preservation evidence](fpr2/preservation.json) matched all 393 historical test/
support hashes and checked all 406 opening test/support files. Only the test
README and the two explained FPR-1 expectations changed. Preserved review,
certification, rollback/pilot records, launcher and disabled hook bytes match.
The full ref map is retained before closing; source pins were rechecked unchanged.
AST and shell syntax checks and modified-document links pass. Raw failure logs
and XML are kept verbatim, including pytest-emitted trailing whitespace; source
and authored-document whitespace checks exclude those raw transcripts.

The one authorized feature commit includes focused evidence, paired ROADMAP and
HANDOVER updates, and canonical FPR-3 action
`OVERSEER-FULL-PRODUCT-RESTORATION-SURFACES-3`, GPT-6 Astra, Max reasoning. Its
publication uses the bound `next-write` with current explicit context and prior
NEXT digest `15efa968ea3bcbe6e5f280bd7cd079f68e5d1f3fa1728246259799a01d582e3c`.
Publication and precommit readback are recorded in [successor evidence](fpr2/successor.json).
Postcommit validation checks the exact disk/committed bytes and sole-parent
closing relationship. FPR-3 remains pending owner acceptance; this wave does not
claim complete-product restoration or release readiness.
