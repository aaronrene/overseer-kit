# FPR-5 bounded repairs — author evidence

The owner-directed successor implements the six findings in the completed
[independent FPR-5 review](../reviews/FPR-5-REVIEW.md). Its original **FINDINGS**
verdict, reproduction scripts, raw failures and inventory remain byte-identical.
This report records implementation and author validation, not independent
adjudication, full-product acceptance or release approval.

## Identity and preserved inputs

Physical root and Git root are
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`;
branch `feat/overseer-v1-recovery-20261014`; name `overseer-kit`; UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`; lane `product`; model GPT-6 Astra,
Max reasoning. Opening HEAD was `4c62c17cff6c606a5e1ddf565e12353973b3bcad` and
computed runtime was
`bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`.

The repaired runtime remains version `1.0.0.dev1`, now SHA-256
**`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`**.
The [source map](fpr5-repairs/source-map.json) records the eight changed production
files and their before/after hashes; the integrated records inventory all 295
runtime files. The repair Git identity is the single local closing commit
containing this report, with the opening HEAD above as its sole parent. Resolve
its full hash with `git log -1 --format=%H -- docs/validation/FPR-5-REPAIRS.md`;
the closing bound readback and owner-facing closeout also identify that commit.

[Opening evidence](fpr5-repairs/opening.json) records the source/runtime files,
dependencies, 144 refs, preserved hashes and all 48 original review/evidence
files. The only initial untracked additions were the expected review report and
`docs/reviews/fpr5/`. Bound entry NEXT validated and named the completed review;
the current owner instruction authorized repairs instead of repeating that task.
The original review files are included unchanged in the repair closing commit.

All 393 historical test/support files and the 420 previously tracked review,
validation and historical-inventory files remain unchanged. The historical
**1,391 passed / 104 failed** baseline, FPR-4 **1,207 passed / one failed** combined
execution and its separate two-pass successor remain historical results. The
new runs below neither rewrite them nor certify their original source again.
Older worktrees, protected refs, Muse history, snapshots, rollback fixtures,
completed bounded pilot and bounded source-release directory were not test targets.

## Repairs and requirement coverage

| Finding | Implemented behavior | Regression evidence |
| --- | --- | --- |
| R1 — redirect credential boundary | The default urllib transport uses its own redirect-refusing handler. No redirected request is sent, including to another allowlisted host or a downgraded scheme. | Real urllib handler chain with synthetic responses across GET/HEAD, redirect codes and destinations; fake credentials and no network. |
| R2 — bound PR target | Every maintained GitHub invocation has an explicit configured repository. Selectors reject options, foreign/malformed URLs and invalid branches; resolved URL/number must match. Checks/merge use the resolved number, and response/remote drift refuses. Existing merge and post-land-sync permissions remain. | Real dispatcher with fake gh: matching/foreign/malformed selectors, branch resolution, contradictory identities, explicit argv repository and changed configured remote. |
| R3 — migration owner collisions | Default migration retains colliding owner bytes, modes and ownership, including unrecorded content, recorded modifications and mode-only changes. Protected paths and exact backups survive config-last partial application and resume; repeat sync retains ownership. | Real legacy migration/apply/resume/sync for rules, both skill trees, policies and references, with bytes/modes/mtime, lock provenance and backup assertions. |
| R4 — desktop resource membership | Verification compares all actual files, directories, links and special entries against approved source/runtime membership. Explicit offline provisioning admits only the conventional interpreter layout and exact pinned local runtime dependencies. | Hidden/excluded/arbitrary extras, empty directories, symlinks, special files, manifest tampering, runtime self-enrollment, deterministic bundling and actual packaged source/bound entrypoints. |
| R5 — repeated multi-lane init | Initialization validates every present NEXT entry using its explicit configured lane and retains the original file. It neither invents missing entries nor selects another task. | Schema-1 NEXT in a multi-lane config and schema-3 collections, preview/apply, missing-lane visibility and invalid unselected-entry refusal. |
| R6 — configured orchestrator planning | Dry-run returns confined argv/cwd/environment with `executed: false`, before any executor call. Selected manifest/policy paths remain confined; no step is marked verified. The read-only executor guard is unchanged. | Real CLI all/step/through plans with/without JSON, read-only snapshots, explicit marker execution, escaped inputs, injected no-execution executor and captured-context drift. |

The changes stay in the existing dispatcher, request boundary, migration,
checkpoint and source-packaging modules. No alternate authority, handoff writer,
provider route or excluded OCI/GSR/sole-writer/identity-bridge mechanism was added.
The resource provisioning command is a local preparation helper, not a platform
installer or dependency downloader; verification requires the same interpreter
and exact local prerequisite bytes. See [distribution contract](../SOURCE-DISTRIBUTION.md).

## Before/after evidence

All four initial requirement runs used the original runtime above, with unchanged
owned production source. Every fixture was newly created under `/private/tmp`,
using the conventional `.venv`, Python 3.14.4 and pinned local dependencies.

| Group | Original source | Candidate result | Evidence |
| --- | --- | --- | --- |
| R1/R2 transport | 89 failed / 5 passed | 94 passed on the identical initial regression file; three valid-branch supplements failed then passed; all 97 pass in final integration | [Transport record](fpr5-repairs/transport/README.md) |
| R3/R5 foundation | 16 failed / 2 passed | Expanded 23-case requirement coverage passes, including final integration | [Foundation record](fpr5-repairs/foundation/README.md) |
| R4 resources | 17 failed / 1 passed | 18 passed; five affected packaging/entrypoint checks passed separately | [Resource record](fpr5-repairs/resources/README.md) |
| R6 orchestrator | 8 failed / 4 passed | 34 passed including existing checkpoint checks; all 14 new cases, including two additional guard cases, pass in final integration | [Before](fpr5-repairs/orchestrator-before-r2/results.log), [after](fpr5-repairs/orchestrator-after-r2/results.log) |

Candidate runtimes are recorded per run and may differ from the final repaired
runtime. A foundation supplement exposed missing protected snapshots for portable
paths outside the former inventory prefixes and a mode-only ownership edge;
its three failures/two passes are preserved alongside the subsequent correction.
One orchestrator candidate had 33 passes/one setup error, and one foundation
candidate had 17 passes/one failure, while another author changed shared runtime
source. The binding guards refused; those runs remain recorded and are not
claimed as stable-source passes. The later orchestrator run passed on stable
source. The initial orchestrator evidence-driver attempt failed before collection
because it treated string paths as Path objects; its corrected invocation has a
new evidence directory. No production guard was relaxed for these setup issues.

The broader transport attempt recorded 110 passes/one preserved historical CLI
fixture failure. That whole-file selection accidentally included an unbound
legacy CLI invocation already mapped to the real bound hosted lifecycle
successor in FPR-4. The failure and its separate successor result remain distinct.
The FPR-3 fake PR-view fixture now supplies the matching URL and PR number that
the real gh JSON response is required to carry; it no longer omits identity while
testing authorized dry-run. Original historical test files remain unchanged.
The foundation affected run recorded 150 passes/one failure: the sole failure is
the already replaced bounded-era assertion that restored commands stay unsupported.
Its 23 new cases and 127 other affected cases pass; final integration uses the
documented current-contract selection. Neither unfiltered attempt is relabelled
green. Three valid Git branch-name cases also caught overstrict candidate syntax
checks; the final guard uses hardened local Git branch validation and preserves
those valid selectors. Their separate candidate failures and passes are retained.

## Integrated validation and closeout

The [new selection](fpr5-repairs/integrated-selection.json) retains the entire
FPR-4 current-contract closeout selection and adds `tests/fpr5`. Shared init,
migration and runtime packaging changes justify this broader affected execution.
All seven preexisting explicit changed-contract replacements remain; there is no
repair-specific deselection, skip or xfail. The existing matrix driver now accepts
an explicit evidence destination so these results cannot overwrite FPR-4.

The [fixed-source combined execution](fpr5-repairs/integrated/repaired-integrated.json)
recorded **1,360 passed / one failed, zero errors/skips**, with all 1,361 collected
cases executed exactly once and identical source/runtime/dependencies throughout.
The failure occurred before provisioning: the new resource-entrypoint case built
an archive while parallel test groups were still writing evidence logs. Archive
verification correctly rejected their changed sizes/hashes. The original archive
case was already deferred; this new archive-dependent case had been omitted from
that scheduling list. [Exact diagnosis](fpr5-repairs/package-race.md) preserves
the failed archive hash, two differing entries and traceback.

Only validation scheduling changed: both archive cases now wait for all parallel
evidence writers. The first runner's exact bytes are retained in
[the original driver copy](fpr5-repairs/fpr4_matrix-before-resource-deferral.py).
The [affected two-case rerun](fpr5-repairs/integrated/repaired-packages.json)
passed **two cases, zero failures/errors/skips**, on unchanged production,
tests, native sources, runtime and dependencies. The driver itself is the only
source-boundary difference, recorded explicitly. No product guard or test
assertion changed to obtain this pass.

[Coverage reconciliation](fpr5-repairs/coverage.json) establishes **1,361 distinct
selected cases with passing evidence**, including all 152 new requirement cases.
This is coverage across the combined run and affected rerun, **not a second
all-green combined execution**. The raw failure remains in its log/XML. The final
Git-only, native authority, mirror, surfaces, migration, lane, context, packaging,
security, latency and integrity outcomes use the declared current contracts.

Reproduce with the conventional venv, the pinned local Muse prerequisite and a
new evidence prefix/destination (loopback permission is needed):

```sh
.venv/bin/python3 -B scripts/fpr4_matrix.py --name new-repair-validation \
  --selection docs/validation/fpr5-repairs/integrated-selection.json \
  --muse-python /Users/aaronrenecarvajal/.local/share/muse/venv/bin/python \
  --evidence-dir /private/tmp/NEW-fpr5-evidence
```

Shell syntax, edited source/document whitespace, original evidence, historical
test and ref checks pass. The unfiltered staged whitespace check reports trailing
spaces in raw pytest failure logs/XML; those bytes remain preserved. All other
staged files pass the separate whitespace check, with both results recorded.
[Closeout evidence](fpr5-repairs/closeout.json) records the explicit bound runtime
refresh and successor publication. Narrow `sync --only launcher` preserves the
unchanged launcher and all installed assets; it refreshes the runtime config and
the preserved ROADMAP/HANDOVER hashes in the footprint lock. It does not claim
that the installation's unrelated footprint drift is resolved or activate hooks.
ROADMAP and HANDOVER are updated together. Only bound `next-write` publishes the
acceptance-decisions stop, using explicit context and the original NEXT digest
`fa1b65567f773886b6131d679a3c9053ca05d79f5d6e56d1b31e860acfb8a6aa`.

## Outstanding acceptance and decision boundary

- The complete Python 3.11 dependency/matrix cell remains unresolved: the pinned
  cffi 2.1.0 cp311 backend was unavailable in the recorded local prerequisites.
  No substitute binary/version or network download was used. Python 3.14 passes
  do not establish Python 3.11 support.
- The owner must select named automatic hosts/client versions before real
  lifecycle acceptance. Cursor event fixtures and instruction-triggered Codex
  bookends are not evidence of native host start/end delivery.
- The owner must select platform/distribution claims and targets before dependent
  acceptance work. Source installation, app/desktop-child and prior offline
  macOS build evidence remain distinct from native GUI, signed/notarized
  installers, Windows, new hosted CI and publication.
- The new integrated pilot still needs a concrete noncritical target,
  host/authority combination and separate authorization. It was not run. The
  completed bounded pilot is preserved and is not queued again.

Repairs proceed independently of those choices. Once the complete repaired source
and required acceptance evidence are available, reserve **one final independent
adjudication**, followed by **one separate owner release decision**. These repair
authors and collaborators cannot certify their own work. Expanded private or
production Muse transports remain an optional explicit scope decision; the
existing bounded transport contract remains in place.

No external network/provider, real consumer/hook, live delivery/export,
working-repository fetch/push, main merge, tag, signing, publication or deployment
was performed. Isolated tests exercised local Git transfers between disposable
repositories under `/private/tmp`; no external remote or protected repository
was targeted. Loopback fixture permission is solely for required local
HTTP/lifecycle tests.
