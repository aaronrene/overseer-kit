# FPR-3 — maintained product surfaces

Scope: accepted canonical FPR-3 action, local implementation and focused disposable
checks only. Opening physical root and Git top-level were
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, full HEAD
`695444fb5f8261391f5c273807129c13dc8db1fd`, sole parent
`8c2b642336e29a3a5a781f70f25f4769e6899642`. Configured name `overseer-kit`, UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`, product lane, GPT-6 Astra, selected Git
and the installation's runtime matched; the opening tree was clean. Bound NEXT
validated FPR-3. Opening hashes/refs are retained in [opening](fpr3/opening.json)
and [ref inventory](fpr3/opening-refs.txt).

Committed sources were read from this integration checkout's objects, without
entering older worktrees: P `e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`,
M `32254cd939885d9d6f40634997ea5b9c37ea776c`,
D `d47291d5d9030de5ebef713da95efa978c4d8c6e`, and repaired B
`348e0f323a3b17cd5022a1bfd56fa09a6831c51f`. The integration branch remains the
base; other refs, Muse history, snapshots, rollback fixtures, completed pilot and
bounded source-release directory are preserved.

## Implementation and source disposition

The single registry exposes all 20 historical command names plus four foundation/
authority commands and all maintained subcommands. The [registry](fpr3/command-registry.json)
records concrete options. No public path invokes `legacy_main`.

| Source / retained engine | Integration boundary and changed mechanisms |
| --- | --- |
| D/P `cli/commands`, freeze reviewer, Check OK, checkpoints, honesty/ledger, routing/cost, compaction | `product_commands`, `product_service` and request-local `product_boundary` share captured full config and final rechecks. Confined writes use whole-file CAS and serialize on the repository directory. API/remote effects are explicit. |
| D/P governance hygiene parsing/drift/queue/anchors | `product_governance` uses selected native/Git observations, labels cached/offline remote facts, and applies paired summaries with a local commit. NEXT regeneration, implicit branch switching/push and live export are superseded. |
| D/P workspace manifests/board diagnostics | Explicit members validate their own root/UUID/runtime/authority/lane and canonical NEXT. Required/optional members and strict mode remain; relays use whole-file digest pins. |
| D/P landing/check/merge/post-land engines | Canonical NEXT freshness and pinned authority replace old HANDOVER land markers. Remote merge requires authorization and an explicit transport; optional local main transition needs `--post-land-sync`. Only fake transports are checked here. |
| D/P footprint/version-lock algorithms; B/FPR-1 migration | Full rules, dual skills, policies and controlled bridge assets are owned/classified. Preserved origins and living documents remain. Runtime digest covers restored engines and static assets. |
| D app/desktop/hosted | Local app invokes the bound services, with auth/CSRF/origin/path checks and canonical NEXT. Desktop verifies health UUID/root/runtime. Hosted routes remain read-only, enforce allowlists and label remote NEXT display-only. |
| M artifact/source verifier, CI driver/workflow, distribution tests | Imported selectively; manual-only CI is prepared but not run remotely. Source packing adds deterministic hash/size/mode manifests, explicit resource preparation and no installed runtime/local binding in the archive. |
| P/D rules, skills, templates, site and runbooks | Canonical NEXT links replace active HANDOVER prompt recipes; no automatic review chain or new signed-release claim. Existing archives/certification stay historical evidence. |

Per-file source provenance is in `fpr3/source-disposition.json`. Maintained outcome
notes are in [product surfaces](../FPR-3-PRODUCT-SURFACES.md) and
[source distribution](../SOURCE-DISTRIBUTION.md).

## Tests, prerequisites and disposition

The [test map](fpr3/test-disposition.json) enumerates **all 393 original test/support
files and all 104 historical failures**, with requirement, retained source,
replacement cases, mechanism changes and explicit pending FPR-4 status. Original
files retain their exact hashes. The 1,391-pass/104-failure baseline is not changed
into a passing claim. No maintained capability is excluded merely because its old
fixture injected an unbound CLI or scraped a HANDOVER prompt. The 33-file
[retained selection](fpr3/retained-selection.json) exercises unchanged useful
algorithms/security contracts; changed entrypoint contracts have actual CLI/app
replacement tests.

Focused checks use this installation's conventional `.venv`, disposable roots
under `/private/tmp`, the preinstalled pinned Muse rc5 interpreter, fake providers/
upstreams/transports and real loopback sockets. No real consumer, hook/provider,
remote/export/delivery/fetch/push/main merge/tag/signing/publication/deployment ran.
Socket escalation is confined to local test services. Completed bounded review,
installation/rollback and pilot were not repeated. These are author checks;
FPR-4 combined validation and FPR-5 independent final review remain pending.

The final surface/artifact/native selection passed **70 tests in 154.56 seconds**,
with no failures/errors/skips. The 33-file retained selection passed **314 tests**.
The boundary rerun had 79 passes and two old footprint assertions; both assertions
were corrected to the expanded asset contract and passed in the final selection.
Across the recorded runs, 529 distinct cases have passing latest outcomes. This
aggregate is not a single final matrix. Initial failures remain retained.

The closing hosted/parser selection passed **73 tests in 58.69 seconds**. Its
preceding 34-test run exposed the historical public `build_parser` import; that
factory now delegates to the same unified registry. The original security test
passes unchanged, alongside all real-entrypoint command checks.

The atomic reader now retries an inode unlinked by concurrent atomic replacement
while still refusing hardlinks. Config/NEXT retain the 128 KiB bound; migration
records and engine assets have a separate 16 MiB bound. Two FPR-1 partial/selector
expectations now include the full footprint and lock behavior; the no-match case
uses a genuinely absent asset selector. Muse fixture staging explicitly includes
portable hidden assets because rc5 recursive staging omits dot-directories.

The final native `cargo build --locked --offline` passed using the explicitly
installed Rust 1.88 compiler. Package/Cargo/Tauri identities agree on
`1.0.0-dev.1`, the native spelling of source `1.0.0.dev1`. Resource preparation
produced identical archives; its own offline-provisioned venv launched the actual
CLI and authenticated desktop child. [Resource evidence](fpr3/resource-launch.json)
binds that focused snapshot and runtime; it is not a GUI/signing or FPR-4 claim.
[Runtime refresh](fpr3/runtime-refresh.json) records the installation change with
all settings, UUID/root/lane/model, NEXT bytes and disabled hooks preserved.

The existing installation's `status --check-footprint` truthfully reports
`ok: false`: 21 paths differ from retained footprint records, the model-routing
policy lacks an old lock record, and the standing-decisions reference has drift.
Only runtime/launcher refresh was selected; no forced full sync or hook activation
was run. The [closing record](fpr3/closing-precommit.json) lists the exact paths.
Fresh full-footprint installation/preservation cases pass in disposable fixtures;
this does not clear the existing installation's separate asset/lock drift.

Detailed run results and failures are recorded in `fpr3/results.json` and the
adjacent logs/XML. Initial failures are retained, including the missing honesty
arguments, loopback sandbox denial, native hidden-asset staging and the
full-footprint migration-plan size issue. A toolchain/prerequisite failure is not
a pass or a skip. Native compilation, Python launcher checks and source-manifest
verification are separate facts.

Owner decisions remain automatic host/client versions beyond the tested event
contract, any broader native remote scope, claimed platforms/distribution/signing,
the later integrated pilot and the independent final reviewer. No release readiness
is claimed by this wave.
