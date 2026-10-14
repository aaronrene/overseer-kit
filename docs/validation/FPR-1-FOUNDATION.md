# FPR-1 foundation implementation — 2026-10-14

Action `OVERSEER-FULL-PRODUCT-RESTORATION-FOUNDATION-1`, accepted by the owner.
This is focused author implementation evidence, not the combined FPR-4 matrix,
an independent review, a restored-product claim or release authorization.

## Verified opening and scope

Physical cwd and Git root were
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, full HEAD
`521c8df5cf2c57d876cdd44adfd1cbc34063d416`. The tree was clean. This commit's sole
parent was `0b763df6d7c9066582d27b349a731a4ff70a43e2`; its only changes were the
plan, NEXT, ROADMAP and HANDOVER. Bound status/NEXT verified name `overseer-kit`,
UUID `6988dc4a-5f22-454b-9d68-ac5905b383bf`, product lane, GPT-6 Astra and runtime
`b7fa1921fcb586ac6fcf8422f094fe20f9f9a438f64eecdaddd97d347115db95`.
Opening canonical NEXT digest was
`590496d30ba196f670e5c71ceeecf525dbb17f606581172a9e997f24754c11fd`.

All required instructions and the complete restoration plan were read before
implementation. P/M/main matched their pinned tips. Source objects were read
from this worktree. No commands entered the older worktrees, Muse store,
rollback fixture, completed pilot or bounded source-release directory. No remote,
provider, mirror, consumer hook, merge, tag, release or deployment ran.

## Source selection and changed contracts

| Surface | Source and selection | Integrated behavior / acceptance |
| --- | --- | --- |
| Launch, root, runtime, NEXT I/O | B `348e0f323a3b17cd5022a1bfd56fa09a6831c51f`, retained on the integration base | Sanitized launchers and isolated bootstrap now reach `cli.main`; one parser/validated context. `v1.main` is a forwarding test seam, never a bypass. Historical dispatcher execution refuses. |
| NEXT safety | B `capture_context`, `check_context`, `validate_next`, `write_next`, `v1_io` | Preserve after-lock/before-replace checks, exact pinned closing-commit reads, final reader checks, CAS and unborn behavior. Schema-2 Git metadata accepted without changing schema-1 bytes or enabling Muse. |
| Configuration | D `d47291d5d9030de5ebef713da95efa978c4d8c6e` retained `adapters/config.py`, hosted validator, P lane fixtures; M `32254cd939885d9d6f40634997ea5b9c37ea776c` schema-2 binding shape | One `product_config` loader/model; legacy-full, bounded-1, October-2 and schema-3 readers. Complete full settings retained alongside the adapter view, including hosted fields omitted by the older wrapper. Unknowns and contradictions refuse. |
| Init/sync/migration | B confined I/O and identity, D init/migration/footprint classification intent, M compare-before-apply/config-last ordering as reviewed pattern | New `product_migration` adapts these incompatible boundaries. Exact plan/config/asset digests, original-byte backups, per-file replacement, mode checks, protected inventory and explicit resume. No wholesale M runtime/ignore import. |
| Asset ownership | D `footprint`, `sync_classify`, `version_lock` semantics | Preserved origins and custom policies/rules/skills/living docs remain protected. FPR-1 updates only requested bound launcher/bookend assets; full asset expansion is FPR-3. Explicit sync refresh preserves the serialized input schema. |
| Cursor bookends | P `e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504:cursor/hooks/*` event/paste-ready intent; B bound invocation | `sessionStart`/`stop` call the same canonical reader as manual NEXT, with strict event/root/lane/identity/input checks and no writes. P PATH/env discovery, awk parsing, HANDOVER scraping and governance regeneration are replaced. |
| Claude/Codex instructions | Retained skill/AGENTS integrations | Distributed and active print-next skills use canonical entry/close calls; Codex instructions label bookends instruction-triggered. No native lifecycle API or verified host version is claimed. Active native hooks stay disabled. |
| Runtime binding | B source digest extended | All CLI/adapter Python sources, hosted config helpers, launcher shims and distributed Cursor/template/policy resources are included; owned source symlinks refuse. Conventional venv interpreter symlinks remain supported. |

No FPR-2 authority/mirror/multi-lane activation or FPR-3 command/app surface was
implemented. Preserved engines remain available for later boundary integration;
none is exposed by routing through the historical dispatcher.

## Focused test disposition

The reproducible selection is [run-focused.sh](fpr1/run-focused.sh). All fixtures
use the conventional installation venv and a nonrepository `/private/tmp` parent.
No historical test is modified, removed, skipped or xfailed by FPR-1.

| Concrete tests | Disposition |
| --- | --- |
| `tests/v1/{test_commands,test_context,test_integrity,test_isolation}.py` | All retained and rerun through the integrated launcher/dispatcher, including 20 deterministic R1/R2 cases, concurrent CAS, exact closing commit, unborn, copied runtime/launcher/hook, hostile environment and both A/B directions. |
| Eight retained unit/adapter files listed in the runner | Unchanged supported engine checks, including all 393 original test/support hashes. Adapter passes do not establish Muse CLI authority. |
| `tests/fpr1/test_config.py` | All-settings roundtrip, full hosted values, source-schema readers, lane preservation, strict types/unknowns/duplicate keys, contradictory context/owners/paths, optional module agreement and no Muse import. |
| `tests/fpr1/test_migration.py` | Real-entrypoint lossless legacy/bounded migration, repeatable plan, backups/modes, config/protected/revision drift, partial failure/resume, stale plan, copied/custom launcher, optional assets, explicit runtime refresh and unsupported Muse inspection. |
| `tests/fpr1/test_bookends.py` | Exact manual/start/end output equality, byte/mode/mtime purity, malformed/oversized/duplicate input, wrong roots/lane/identity/event, stale and closing commit, copied/edited hooks, quoted paths, instruction preservation and old B adapter compatibility. |
| `tests/fpr1/test_dispatch.py` | All launchers/global option placement, historical execution refusal, validation before injected handler, unbound/Muse inspection without Git, schema-2 Git NEXT preservation, dry-run purity and runtime resource coverage. |
| `tests/unit/{test_k8_lanes,test_k7_footprint,test_footprint_integrity}.py`; `test_init_migrate.py::test_classify_preserve_shared_unit`; three `test_lt_unit.py::test_session_bookends_*`; `test_lt_integration.py::test_session_bookends_in_resolve_when_enabled` | Relevant unchanged lane/config/footprint/ownership algorithms and bookend-option checks rerun. They do not activate legacy bridge scripts. |
| Remaining `test_init.py`, `test_init_migrate.py`, `test_sync.py`, `test_cli_init_sync_status.py`, `test_migrate_idempotency.py`, `test_pilot_migrate_cycle.py` | Original CLI-injection/`--from-config`/generic-force/promotion contracts preserved as historical evidence. Explicit canonical-config plan/apply and preservation semantics are exercised by new actual-entrypoint tests; generic force no longer promotes living docs. Full-footprint consumers remain FPR-3/4. |
| Remaining `test_lt_*`, `test_print_next*`, old HANDOVER/governance regeneration tests | Scraped/regenerated prompt authority is superseded by canonical manual/event tests. Compaction, status tips and other maintained engine outcomes remain FPR-3/4; they are not declared passing here. |

The historical baseline remains **1,391 passed / 104 failed** and is not rerun or
relabelled green. Original independent FINDINGS, repair evidence, 43-check
installation/rollback exercise, bounded pilot and certification remain intact.
Author collaboration used bounded implementation checks; it is not FPR-5 review.

## Migration operation and limits

Dry-run: `ok -C ROOT init --migrate --dry-run --json`; save its output as a
repository-relative plan file. Apply with `init --migrate --apply-plan FILE
--expect-plan PLAN_SHA256 --expect-config SOURCE_SHA256`. A changed source runtime
requires a newly reviewed dry run with `--refresh-runtime`. Existing bindings and
source selection are never changed implicitly. An absent legacy binding is
proposed in the plan and persisted only by explicit apply.

Plans list before/after fields, exact asset bytes/digests/modes, protected files,
observed branch/head/runtime and exact extracted legacy prompt drafts. Backups
live under `.overseer/migrations/PLAN_SHA256` with a manifest; config is replaced
last. Reuse the same plan/expected digests with `--resume` after partial failure.
Only original or exact planned replacement bytes/modes are accepted. The manifest
also describes explicit quiescent rollback. Per-file atomicity is not a
transaction; post-replace fsync failure may leave complete new bytes and reports
actual completed paths. A changed revision/runtime or owner edit requires a new
reviewed plan. No Git files are silently untracked.

Migration/sync preserve canonical NEXT and living documents. A legacy-only prompt
is a draft requiring operator acceptance and explicit `next-write --expect-next
absent`; extraction grants no action authority and never publishes it. Conflicting
legacy prompts refuse. `origin:preserved` and custom assets are not taken over.
Config and I/O retain bounded file-size checks. Muse configs normalize and report
the native authority limitation; mutation waits for FPR-2 context validation.
A different Muse working directory requires explicit pairing; migration cannot
rebind or invoke Git on its behalf.

Cursor event registration and payload behavior are fixture-tested only. Named
client/version lifecycle delivery remains FPR-4. Claude/Codex guidance is
instruction-triggered, not proof of native automatic events. Hooks were installed
only in newly created disposable repositories; this installation's active
`.cursor/hooks.json` remains unchanged and disabled.


## Development failures and repairs retained in this wave

- Initial bookend fixture setup reported 23 errors / 6 passes: fresh init tried
  opening its advisory-lock directory before creating it. Init now preflights
  paths and creates that directory before locking. The subsequent event run had
  28 passes and one `runtime_changed` refusal while source was still being edited;
  that copied-hook case passed on recheck. No native host success is inferred.
- The first shared-core smoke run had 63 passes / one runtime-change refusal;
  the first dispatcher run had seven passes / two invalid Muse-fixture failures
  / one runtime-change setup error. The Muse fixture lacked its required main
  branch; correcting the fixture yielded ten dispatcher passes. These logs/XML
  remain under `fpr1/`; the stable-source matrix supplies the integrated verdict.
- Config development initially had 29 passes / two test expectation failures:
  one fixture requested forbidden hand verification, and one expected an overly
  narrow recursive-YAML error. Valid fixture/expectation corrections preceded
  the 39-case pass; no validator refusal was waived.
- Author migration checks reproduced omitted unchanged-launcher mode preflight,
  accidental mode change for a preserved launcher, malformed-plan tracebacks and
  JSON-key-order sensitivity despite an unchanged canonical plan digest.
  Regression tests now protect every destination's bytes/mode, refuse preserved
  launcher mode takeover, strictly parse/validate JSON plans and reproduce target
  YAML from preserved source independent of JSON object ordering.
- The first focused collection failed because new and historical config tests
  shared a top-level Python module name. Adding `tests/fpr1/__init__.py` namespaced
  new tests without changing any historical source. The collection log/XML are
  retained as `collection-before-repair.*`.
- Two repeated-init ownership regressions failed before repair: custom launcher
  bytes were replaced and a preserved launcher's mode was reset. Their exact
  failing evidence is `reinit-before.*`; re-init now uses the shared ownership
  classifier. Legacy `sync --only` glob selection is retained for the foundation
  asset set, with no-match and explicit-hook requirements checked before writes.
- Two final unsupported-authority cases failed before repair because fresh Muse
  init attempted Git root discovery before refusing its unavailable authority.
  `authority-before.*` retains the failures. The dispatcher now refuses those
  non-migration init requests before root discovery; no authority is activated.

All repairs belong to this FPR-1 implementation. No extra commit/review wave or
completed certification exercise is used to close these defects.
The initial bookend setup run and config development runs were not redirected
to standalone logs/XML; their raw evidence remains in the author tool transcript.
The counts above preserve that distinction. Saved logs/XML are enumerated in
`fpr1/results.json`; the integrated matrix includes these cases after repair.


## This installation's explicit migration

The reviewed plan digest was
`953ffa6a9364ae6ebdd6e7e23fdd8d708955c17f84c3005270ced4d8a0fede1e`, against original
config SHA-256 `1a4586251142fbbab8d6035599992ac99e19db8dc557b0304d792c1851a2d7f9`.
Only `.overseer/config.yaml` changed; all 48 protected paths matched. The resulting
schema-3 config SHA-256 is
`329947f35c21969a4ae7304b93eeff6084966e20f29d778e5aca0f595cbf007c`, with runtime
`84cb854b69b36c13bfe1ca2e9e3e7644324543d2983070bd026dcaf1e9865106`.
UUID, physical repository/runtime roots, product lane and GPT-6 Astra are unchanged.
Bound `status` and digest-checked `next` succeeded after migration and before
successor publication. Canonical NEXT still had the exact opening digest.

The original config backup is byte-identical to opening HEAD's committed config
at `.overseer/migrations/953ffa6a9364ae6ebdd6e7e23fdd8d708955c17f84c3005270ced4d8a0fede1e/files/.overseer/config.yaml`.
Its manifest is retained locally. Only this local backup directory was added to
`.gitignore`; tracked config, launcher and NEXT remain tracked. No hook was
installed here. [Exact invocation/result](fpr1/installation-migration.json)
records an initial operator typo in the expected plan digest: it correctly
refused before mutation. The corrected digest applied successfully; this was an
input error, not a product repair or waived failure.

After the final refusal guard, explicit bound `sync --dry-run` and `sync`
changed only the runtime binding. [Refresh evidence](fpr1/installation-refresh.json)
records preserved identity, all settings and the original NEXT bytes. Final
config SHA-256 is
`a8a59cde1625b373670bf7116c8a564ab691bf72c5e304b8c1d9aa41fc0ba32a`;
final runtime SHA-256 is
`dbe7e93e6797611ac410d4e94f40ba7ea34c4419b1389568b3579d558eb353db`.
The [final runtime manifest](fpr1/runtime-manifest.json) lists all 111 bound files;
the pre-guard manifest is also retained. Bound status and expected-digest NEXT
readback both passed after refresh.

## Final focused verdict and closeout

The integrated matrix passed **315 tests in 268.39 seconds**, with no failures,
errors or skips: [log](fpr1/focused.log), [XML](fpr1/focused.xml). This includes the
supported B suite, deterministic R1/R2, concurrent CAS, unborn/exact closing
commit, copied launchers/hooks, two-repository isolation and the new configuration,
migration, dispatch and event cases. A prior integrated run passed 307 tests;
its evidence remains as `integrated-before-final-fixes.*`.

The only product-source edit after the 315-case run was the two-line early
unsupported-init-authority refusal. The full dispatcher and command selection
then passed **58 tests in 47.49 seconds** on the final runtime, including both
new refusal regressions: [log](fpr1/final-dispatch.log),
[XML](fpr1/final-dispatch.xml). These runs cover 317 distinct passing cases;
they are not represented as a single 317-case run on the final source.
The runner now selects all 317. [Structured results](fpr1/results.json) retain
both source digests and all saved development failures.

Shell syntax and modified documentation links passed. Staged whitespace checks
passed for source, tests, documentation and structured evidence. The unfiltered
check reports only trailing whitespace emitted by pytest in preserved raw failure
logs/XML; those transcripts are retained verbatim rather than rewritten.

All 400 opening test/support files (including the 393 historical files from D)
remain byte-identical. Source refs and preserved review/rollback/pilot artifacts
were checked unchanged. The earlier certification, 104 historical failures and
unverified host/version delivery remain separate limits. No full restoration,
FPR-4 validation, FPR-5 review or release-readiness claim is made.

The single closing feature commit includes this evidence, paired summaries and
the canonical FPR-2 successor. Successor publication uses the bound `next-write`
with explicit current context and the opening NEXT digest; no migration, sync,
hook or summary creates an alternative pending prompt. Publication/readback
details are in [successor evidence](fpr1/successor.json). The final post-commit
readback verifies the exact committed NEXT and one-parent closing relationship.
