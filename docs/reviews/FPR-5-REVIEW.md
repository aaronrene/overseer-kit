# Independent full-product restoration review — FPR-5

**Verdict: FINDINGS. Full-product acceptance and release readiness are blocked.**
The independent review of the fixed FPR-4 source is complete. Six reproduced
implementation defects require bounded repairs. Required Python 3.11, native
host acceptance, platform/distribution decisions and integrated-pilot evidence
also remain open. No production repair or release operation was performed.

The owner explicitly appointed this fresh session and instructed it to proceed.
This session and its review collaborators did not author FPR-4 or participate in
its author validation. Collaborators supplied bounded source/evidence checks;
this document is the single independent verdict, not several review cycles.

## Reviewed identity and preservation

| Binding | Verified value |
| --- | --- |
| Physical cwd / Git top-level | `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014` |
| Branch | `feat/overseer-v1-recovery-20261014` |
| Reviewed commit | `4c62c17cff6c606a5e1ddf565e12353973b3bcad` |
| Sole parent | `6289d2823184a63e2968d2c5f6a76abab5818368` |
| Name / UUID | `overseer-kit` / `6988dc4a-5f22-454b-9d68-ac5905b383bf` |
| Lane / requested model | `product` / GPT-6 Astra, Max reasoning |
| Runtime | `1.0.0.dev1`, `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec` |
| Canonical NEXT SHA-256 | `fa1b65567f773886b6131d679a3c9053ca05d79f5d6e56d1b31e860acfb8a6aa` |
| Review environment | Conventional local `.venv`, Python 3.14.4; separately pinned Muse 0.2.1rc5 for native fixture checks |

The worktree was clean before review. Bound `status` and `next` succeeded, NEXT
equaled its committed bytes, and the single-closing-commit relationship matched.
The runtime was recomputed, not accepted only from config. See
[preflight](fpr5/preflight.json) and [independent accounting](fpr5/evidence/independent-evidence-accounting.json).
The [closing checks](fpr5/closing-checks.json) verify unchanged source, runtime,
preservation hashes and refs after adding this report; the new evidence is
inventoried in [ARTIFACTS.json](fpr5/ARTIFACTS.json).

All **785 manifest entries** match both disk and HEAD, including executable modes:
295 runtime, 436 test, four validation-driver, 40 native, eight packaging and two
requirements entries. All **393 original test/support files** match preserved D,
HEAD and disk. The 343-entry source map and its asserted exact-source relationships
were checked; exactly the recorded six FPR-4 product changes distinguish its final
source from FPR-3. The 144-ref comparison permits only the already completed FPR-4
closing move on this integration branch. This review moves no ref.

Preserved P is `e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`; M is
`32254cd939885d9d6f40634997ea5b9c37ea776c`; main/D is
`d47291d5d9030de5ebef713da95efa978c4d8c6e`; repaired B remains
`348e0f323a3b17cd5022a1bfd56fa09a6831c51f`. Source objects were inspected here.
Older worktrees, Muse history, snapshots, old rollback fixtures, completed pilot
and bounded source-release evidence were not used as test targets. Old review,
certification, rollback/pilot records and disabled hook hashes remain unchanged.

## Actionable findings

P1 denotes a security or repository-authority defect to address before use of the
affected operation. P2 denotes a maintained behavior or distribution-integrity
defect. Every finding below blocks complete acceptance; focused passes do not
waive any finding.

### FPR5-R1 — P1: hosted redirects bypass the host boundary and forward credentials

[tools/hosted_dashboard/http_client.py](../../tools/hosted_dashboard/http_client.py),
lines 39–44 and 86–98, checks the original URL's host, adds a bearer header, then
uses `urllib.request.urlopen` with its default redirect behavior. Redirect targets
are not checked against the allowed hosts and the credential remains attached.

A network-free fixture used the real urllib redirect handler. An allowed
`https://api.github.com/repos/acme/demo` response redirected to
`https://not-allowlisted.invalid/stolen`. The second captured request had
`host_allowed: false` and still carried `Bearer FAKE-REVIEW-TOKEN`. Only synthetic
responses and a fake token were used. No credential was read or sent externally.
The risk requires an upstream redirect; no real redirect incident is claimed.

This violates the hosted allowlist and upstream-credential boundary in restoration
plan sections 4 and 9 and the maintained product-surface contract. Existing
fake-upstream route tests do not exercise the default HTTP redirect chain.

Repair: refuse redirects or validate every hop's scheme/host and credential scope
before any request. A rejected or foreign origin must receive no authorization
header. Record failing-before/passing-after behavior through the actual default
transport, then rerun hosted allowlist, credential, projection and app/hosted
isolation checks. [Reproduction](fpr5/surfaces/repro_redirect.py),
[raw result](fpr5/surfaces/repro_redirect.log).

### FPR5-R2 — P1: a PR selector can override the bound GitHub repository

[cli/product_service.py](../../cli/product_service.py), lines 75–94, pins `GH_REPO`
from the configured remote but forwards caller argv unchanged. The retained
[PR engine](../../tools/close_ritual/pr_land.py), lines 141–174, inserts the supplied
PR selector into `gh pr view`, `checks` and `merge` without validating its repository
or excluding option-shaped values. The returned PR URL is not checked either.

In a disposable checkout configured for `https://github.com/fixture/bound.git`,
actual `cli/ok pr-land` accepted both a foreign PR URL and
`--pr=--repo=foreign/repo`. With explicit fixture authorization and a fake `gh`,
both selectors reached the merge invocation unchanged while `GH_REPO` still named
the bound repository. Both runs returned `merged: true`. This demonstrates the
missing validation at the real CLI boundary; no GitHub call or actual merge ran.

The configured remote is supposed to constrain GitHub transport, as documented in
the product-surface contract and plan sections 4, 6 and 9. An environment default
does not constrain an explicit URL or a command option. The existing approval flags
remain necessary but do not repair this target mismatch.

Repair: validate selectors before transport, reject option-shaped values, and
require any URL and resolved PR identity to belong to the configured host/repository.
Constrain every view/check/merge invocation consistently. Retain explicit merge
and post-land-sync authorization. Rerun real-dispatcher fake-transport cases for
matching, foreign, malformed and drifted identities plus landing/sync checks.
[Reproduction](fpr5/surfaces/repro_cli.py), [raw CLI results](fpr5/surfaces/repro_cli_result.json),
[captured fake transport argv](fpr5/surfaces/fake-gh-calls.jsonl).

### FPR5-R3 — P2: default migration replaces colliding owner assets

[cli/product_migration.py](../../cli/product_migration.py), lines 334–346, places
all generated assets in the update plan and only blocks changed assets whose lock
origin is explicitly `preserved`. Unrecorded owner content and other modified
assets can be classified `both-changed`, then removed from the protected inventory
and replaced by the generated bytes.

The real CLI reproduction starts from the supported legacy two-lane config and
an existing owner `.cursor/rules/build-verification-required.mdc`. The generated
plan classifies it `both-changed`, origin `unrecorded`. Applying the exact generated
plan/config digests exits 0 and replaces the owner rule. Its original bytes survive
in the backup, so this is active-content loss, not unrecoverable deletion. The plan
shows the replacement; the defect is its default takeover instead of the promised
preservation or explicit collision resolution.

Plan section 5 requires preserving user rules/skills/policies by default. The
mapped lossless-migration tests use non-colliding `custom.mdc` paths, and the
colliding-origin test supplies `origin: preserved`; neither covers this case.
Explicit approval of a schema-migration plan should not be the only available
route to overwriting consumer content.

Repair: retain bytes/modes and owner classification for these collisions by
default, or refuse with a specific resolution plan. Ensure apply/resume understands
the protected result rather than requiring every asset to equal kit bytes. Cover
unrecorded and recorded-modified collisions, exact backup, resume and repeat sync.
[Reproduction script](fpr5/repro_foundation.py), [result](fpr5/foundation/foundation-results.json),
[complete CLI transcript](fpr5/foundation/foundation-transcript.json).

### FPR5-R4 — P2: desktop resource verification accepts excluded extra files

[tools/ci/source_package.py](../../tools/ci/source_package.py), lines 124–134,
checks only manifest-listed paths. It does not inspect extra files in the resource
tree. [Tauri configuration](../../desktop/src-tauri/tauri.conf.json), line 7, uses
that verifier before building and lines 28–30 package the resource directory.

A complete current-source fixture verified successfully. Adding synthetic
`.overseer/config.yaml`, `docs/NEXT.md` and `tools/.env` still verified successfully.
All three additions are unmanifested and individually rejected by `eligible()`.
The exact locked local Tauri dependencies confirm recursive directory walking
includes hidden files and copies each discovered file. Therefore a contaminated
resource directory can pass the guard and include these excluded files in a
bundle. No real secret, native build or contaminated release was involved.

This violates source/distribution exclusions in plan sections 6 and 9 and
SOURCE-DISTRIBUTION.md lines 16–18. Archive verification itself rejects archive
membership tampering; the defect is the separate prepared-tree check.

Repair: validate actual packaged membership and reject excluded/unapproved extras.
Define intended provisioned `.venv` dependencies explicitly instead of treating
all extras as harmless or excluding the runtime indiscriminately. Rerun clean
resource preparation, extras/hidden-files refusal, deterministic bundling and
packaged entrypoint checks. [Probe](fpr5/authority/probe_resource_membership.py),
[result](fpr5/authority/resource-membership.json),
[locked dependency evidence](fpr5/authority/tauri-resource-path.json).

### FPR5-R5 — P2: repeated initialization refuses valid multi-lane repositories

[cli/v1.py](../../cli/v1.py), line 435, validates existing NEXT with an empty
`argparse.Namespace()`. [selected_lane](../../cli/product_next.py), lines 64–73,
requires explicit selection when multiple lanes exist. The init path discards the
caller's lane at this validation point.

After ordinary initialization, adding a valid owned `architecture` lane leaves
`next --lane product` successful. Both `init --dry-run` and
`init --dry-run --lane product` then exit 2 with
`refused: next_lane_selection_required`. The single-lane control succeeds and
NEXT remains byte-identical. This prevents the promised repeat-init/idempotency
behavior for a supported configuration; the safe refusal does not damage data.

Repair: validate existing present entries using their explicit configured lanes,
while preserving missing-lane visibility and existing NEXT bytes. Do not silently
choose another task or rewrite lane entries. Cover schema-1-to-multi-lane and
schema-3 collections, both preview and apply, together with init preservation.
Affected requirements: plan sections 4, 5 and 9, multi-lane and migration/idempotency.
[Result and transcript](fpr5/foundation/foundation-results.json).

### FPR5-R6 — P2: configured checkpoint orchestrator has no working dry-run

[tools/checkpoints/orchestrator.py](../../tools/checkpoints/orchestrator.py),
lines 190–197 and 577–586, selects a configured consumer override and calls its
executor even for dry-run. The bound service correctly marks that request read-only;
[executor.py](../../tools/checkpoints/executor.py), lines 44–50, then refuses it.

A fresh bound fixture with enabled checkpoints and an executable
`checkpoints.orchestrator` runs `verify-step --all --dry-run --json` through the
actual CLI. It exits 2 with `script_execution_requires_explicit_bound_mutation`
instead of returning a plan. The marker script was not executed. The refusal
guard is doing its job; the override route omits the required planning path.

Repair: return a bounded no-execution plan before invoking the override executor.
Keep the dry-run mutation guard. Validate override planning and explicit execution,
built-in verification, manifest confinement and current-context checks.
Affected requirements: plan sections 4 and 9 and the product contract's documented
`--dry-run` planning behavior with maintained settings enabled.
[Reproduction](fpr5/surfaces/repro_cli.py), [raw result](fpr5/surfaces/repro_cli_result.json).

## Architecture and maintained capability assessment

The integration strategy is coherent: one isolated source bootstrap reaches one
registry; normalized config feeds a captured repository/runtime/authority context;
retained engines run within request-local guards. This retains B's captured
context, pinned Git closing reads, final read rechecks and confined CAS writes.
Native Muse reads remain an explicitly bound backend, not an inferred fallback.
Whole-file lane CAS and per-entry freshness prevent one lane silently refreshing
another. No architectural expansion or excluded OCI/GSR/sole-writer/identity-bridge
or packet machinery is needed to address the findings.

No public `legacy_main` bypass or active HANDOVER prompt regeneration was found.
The legacy dispatcher refuses. Manual, hook, workspace and app NEXT paths use the
canonical service. Hook adapters remain read-only; migration's legacy extraction
produces proposals only. Adoption is explicit, tracked Git bindings are retained,
and controlled mirrors use separate owned bare targets. FPR5-R1/R2 identify limits
in the claimed external host/repository confinement; they do not imply an implicit
authority switch or a remote operation during this review.

| Maintained command/settings group | Traced production boundary and review result |
| --- | --- |
| `init`, `sync`; all supported config schemas, paths, optional sections and ownership | `product_config` / `product_migration` / `v1.initialize`; finite/unique config, preservation, config-last, plan digests, partial resume reviewed; R3/R5 remain. |
| `status`, `next`, `next-write`, restricted `hook`; lane/model/UUID/runtime | `ValidatedContext`, `v1`, `product_next`, `product_bookends`; captured-context and closing-read safety regressions, exact closing revisions, whole-file CAS and lane ownership pass focused checks. |
| `adopt`, `mirror prepare/reconcile/verify/deliver`, `upgrade-regime`; Git and both Muse regimes | Explicit native binding, retained settings, config-last restore, target ownership, native projection, exact bundle/delta/parents, retries and scoped credentials reviewed; 47-case focused run below. |
| `governance-sync`; docs/lanes/thresholds | Bound default local observation; explicit paired-summary write/local commit; separate push authorization; canonical `--print-next`; no automatic task regeneration. |
| `review`, `check-ok`, `check-if-ok`; freeze/provider/fallback and configured gates | Bound artifact/checklist and stamping route; local/API/human outcomes and explicit provider permission; mechanical results remain distinct from independent semantic review. |
| `workspace status/check-next/doctor`; manifest and pins | Explicit member roots, own UUID/config/runtime/authority, canonical NEXT and optional digest pins; visible optional errors/strict mode, no member writes. |
| `verify-step`; checkpoints/modules/orchestrator/policy/progress | Bound scripts/manifests and captured context; built-in checks retained; R6 affects the configured override's preview. |
| `honesty-status`, `ledger append/verify/show`; honesty/roles/evidence/extensions | Retained evidence/signature/hash-chain engines and configured paths; append alone receives write authority; infrastructure packet machinery is not restored. |
| `route`; model routing, tiers and cost | Read-only policy validation and hints; no provider invocation or automatic spending. |
| `land-check`, `land-closeout`, `pr-land`; close ritual and optional post-land sync | Explicit local verification, separately authorized remote enrichment/merge, separately selected post-land sync; R2 leaves remote target binding incomplete. |
| `handover-compact`; selected documents/keep count | Preview and explicit confined archive/write; canonical NEXT protected. |
| `app`, desktop; auth/CSRF/origin/document/static/lifecycle | Bound shared services and health identity; local script/child evidence only, no GUI or native-host delivery claim; R4 affects prepared resource membership. |
| `hosted-dashboard`; full validated host/org/repo/cap/size settings | Read-only routes and display-only remote NEXT; restored allowlists and viewer/upstream separation reviewed; R1 affects transport redirects. |
| Source installation, compatible update/rollback, distributed skills/rules/templates | Deterministic archive and manifest, explicit fixed-root refresh/config backup/restore reviewed; original FPR-4 install/build claims remain limited to recorded environments. |

This is a combined source/evidence assessment, not a claim that every option or
platform was independently executed again. The detailed
[command/endpoint trace](fpr5/surfaces/coverage-notes.txt) identifies source paths
and the original validation's HTTP coverage limitation.

## Historical failures and explicit replacements

The [independent row reconciliation](fpr5/evidence/independent-historical-rows.json)
contains all **104** historical failure identities, original categories and mapped
raw case IDs. Their distribution remains 68 socket denials, 16 missing-cryptography
cases, nine path/fixture cases and 11 other failures. Twenty original failing nodes
have later passing executions; 84 have explicit passing successor mappings. This
does not turn the preserved **1,391 passed / 104 failed** baseline into a green run.

The [semantic map](fpr5/evidence/independent-semantic-replacement-map.json) assesses
each historical failure row and all seven explicit deselected-node replacements
against source assertions, and inventories/reconciles all 393 original files.
It preserves excerpts,
source hashes and specific successor names. The seven replacement decisions are:

| Preserved original expectation | Independent assessment of its replacement |
| --- | --- |
| Bounded CLI rejects restored commands (`test_unsupported_commands_cannot_run`) | Valid scope change. Real help/registry and effect-refusal checks, together with actual maintained-command tests, replace an unconditional unsupported-command rule. Help alone would not establish functionality. |
| Standalone Git needs only YAML (`test_fresh_standalone_git_install_without_muse`) | Valid full-dependency fixture change. Successor provisions the exact declared dependencies into its own venv, checks actual crypto operation and absent Muse/pip/pytest, then exercises source and bound entrypoints. This is same-interpreter evidence, not cp311 compatibility. |
| Linked native initialization remains clean (`test_native_linked_worktree_own_branch_and_checkout_identity`) | Valid truthful-status correction. Successor demonstrates the sole portable delta is the footprint lock, preserves primary checkout/source identity and independent UUID/branch/NEXT behavior, and reports the actual dirt. |
| Intended no-content mirror revision (`test_add_change_delete_and_no_content_source_commit`) | Valid fixture correction. Successor stages hidden portable files before approval, retains the original delta/retry assertions, and proves equal native snapshots and Git trees for the no-content revision. |
| Rendered bridge performs direct export/automatic push (`test_rendered_deploy_script_safety_invariants`) | Valid explicit-effects replacement. Actual wrapper root/literal-argument/PATH/refusal behavior plus native projection/target/current-source/delivery tests preserve controlled distribution without restoring the excluded live-export route. |
| Orchestrator contains historical rule numbers and raw HANDOVER placeholders (`test_footprint_includes_orchestrator_rule`) | Valid semantic guidance replacement. Installed guidance checks canonical NEXT, identity/CAS, paired summaries, configured gates, separate effects, explicit review loops and both host skill footprints. |
| Git status imports no provider-prefixed definitions (`test_git_core_imports_no_muse_or_provider_engine`) | Valid definition-versus-activity correction. The two clean-process successors prohibit native imports, actual provider activity, external sockets and non-read-only subprocesses, while checking complete status and unchanged files under local/API settings. The raw original failure remains failed. |

**Coverage accounting is accurate, but mapping a passing case is not proof of
every maintained behavior.** The independent semantic audit identified five
historical app rows whose replacements omit successful current HTTP review/gates/
ledger/honesty/status-parity outcomes. Their underlying CLI tests bypass the
HTTP body-to-argv adapters. A separate reviewer supplement now supplies those
current-contract outcomes; it does not rewrite FPR-4 or claim all obsolete output
shapes remain requirements. R3 also demonstrates a migration-preservation edge
that the existing non-colliding fixtures did not cover. Therefore the accounting
does not negate the implementation findings or establish complete restoration.

## Reconciled run results and reviewer verification

| Evidence | Actual result and limit |
| --- | --- |
| FPR-4 initial combined run | 1,159 passed / 11 failed, zero errors/skips; preserved failure record. |
| FPR-4 frozen final combined run | **1,207 passed / one failed**, zero errors/skips; 1,208 distinct exact-once executions, exit 1. The failed provider-import-prefix assertion remains in the raw log/XML. |
| FPR-4 affected import successor | **Two passed** separately on unchanged production/runtime/dependencies. The first incorrectly supplied pytest-option invocation exited 4 before collection and remains recorded. |
| FPR-4 closeout selection | Exactly **1,209 distinct passing current-contract cases** across the preceding passing outcomes. This is not another combined execution and not an all-green combined result. |
| FPR-4 other focused evidence | 32 repaired-source cases and 13 compatible/bounded rollback checks are separate runs, not added to the combined count. Earlier fixtures, repairs, interruptions and package failures remain preserved. |
| FPR-5 foundation selection | **41 passed**, zero failures/errors/skips, 146.30 seconds. Captured-context/closing-read regressions, lanes/CAS/ownership and affected migration drift/partial-resume checks. [Command](fpr5/foundation/focused-command.json), [log](fpr5/foundation/focused.log), [JUnit](fpr5/foundation/focused.xml). |
| FPR-5 authority selection | **47 passed**, zero failures/errors/skips, 118.571 seconds. Two adoption concurrency/config-last, 39 scoped-credential, five native adopt/upgrade/projection/reconciliation/fake-delivery, one archive traversal case. [Command](fpr5/authority/focused-command.json), [results](fpr5/authority/results.json), [JUnit](fpr5/authority/focused.xml). |
| FPR-5 HTTP supplement | **Six successful HTTP requests**, with current CLI/status parity, gates parity, local no-execution review preview, ledger show/verify, and matching synthetic honesty evidence. Non-Git fixture-file bytes/modes/mtimes are unchanged. [Script](fpr5/surfaces/http_functional_supplement-r4.py), [raw result](fpr5/surfaces/http_functional_supplement-r4.json). This is a separate reviewer fixture exercise, not six pytest cases or a pilot. |
| FPR-5 finding probes | Six undesirable behaviors reproduced on unchanged production; their scripts assert/record the defects. A probe exiting successfully means reproduction succeeded, not that the product passed its requirement. |

The HTTP supplement's earlier attempts are retained. Two reviewer-fixture setup
assumptions were corrected: a legacy reviewer field was a string rather than a
mapping, and the synthetic ledger verdict needed a bare hexadecimal artifact
digest. The corrected third attempt then reached actual server startup and hit
the sandbox's loopback bind denial before any HTTP request. The fourth attempt
used a new fixture, the same unchanged production and the granted loopback
permission; all six requests passed. Provider selection was local, data and
credentials were synthetic, non-loopback connections were blocked, and no
external provider/network request occurred. These are fixture/environment
corrections, not product repairs or waived failures.

Reproduction uses the conventional venv and new `/private/tmp` fixture parents.
[Evidence instructions](fpr5/README.md) provide a relocation wrapper for the
preserved scripts and exact focused selections. The reviewed production, tests,
config, NEXT and old evidence remain unchanged. Only this review report and its
new evidence are added; no ref, commit or successor prompt is published by review.

## Required evidence and owner decisions still open

1. **Complete declared Python 3.11 cell:** the locally available pinned cffi 2.1.0
   cp311 backend is missing. FPR-4's actual status/dependency and collection
   failures remain unresolved. Unaffected template/core passes and Python 3.14
   success do not close it. Supply the correct pinned local prerequisite and
   execute the complete declared cell; do not narrow the platform claim silently.
2. **Named automatic hosts and versions:** select the required clients/versions,
   then establish their real start/end delivery. Cursor event fixtures and this
   session's instruction-triggered Codex bookends do not demonstrate native
   lifecycle acceptance. No additional host API or manual-only substitute is
   inferred by this review.
3. **Platform/distribution acceptance:** select the claims and targets. Preserved
   local macOS arm64 source installation, app/desktop-child and locked/offline
   Rust build evidence remains distinct from native GUI acceptance, signed or
   notarized installers, Windows, new hosted CI, publication and live providers.
   Those unselected capabilities are not silently promoted to supported claims.
4. **New integrated pilot:** select and separately authorize a noncritical project
   and host/authority combination. The proposed new local Git-only project with
   instruction-triggered bookends and fake transports has not been authorized or
   run. The old bounded pilot is complete and must not be repeated or relabelled.

Reviewer appointment is now satisfied by the owner's explicit direction in this
session. Expanded private/production Muse transports, hosts, source branches or
Git object formats remain an optional owner scope decision, not an inferred
restoration requirement. The current bounded transport contract is retained.

The existing installation's separately reported footprint/lock drift is also
preserved; a clean Git checkout and matching runtime do not establish that all
installed consumer assets are current. This review did not force sync or activate
hooks. Native provider success, real-consumer migrations, sustained/multi-user
operation and malicious same-UID/root protection are not established here.

## Repair and final decision boundary

Preserve this FINDINGS verdict and all raw reproduction/results. Bounded repairs
should add requirement-level regressions, record failing-before/passing-after
results, and rerun affected integrated checks on an explicitly recorded repaired
source/runtime. If shared changes invalidate additional combined evidence,
expand that affected selection accordingly. No repair may erase the original
failure or reuse a prior digest as if production had not changed.

After the complete repaired source/evidence and required acceptance evidence are
ready, reserve **one final independent adjudication**, followed by **one separate
owner release decision**. Do not start per-wave review cycles. Architecture or
scope expansion, if needed, returns to the owner; the six findings themselves
can be addressed within the selected architecture. This review is complete but
does not grant repair authors the right to certify their own adjudication, and
neither review acceptance nor this verdict authorizes release, merge, push,
signing, publication or deployment.

Canonical NEXT remains preserved as the fixed input to this now-completed review.
It must not be presented as a new pending FPR-5 review. Any accepted follow-up
publication must use the sole bound `next-write` service with current explicit
context and the expected prior digest.
