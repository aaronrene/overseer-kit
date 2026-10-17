# FPR-5 acceptance closeout packet — manual delivery scope, 2026-10-17

**Revised scope prepared for one independent acceptance decision; acceptance and
release remain pending.** The owner now selects the existing features, browser
and manual repository-bound NEXT workflow. Actual Cursor sessionStart/stop and
client-level restored/forwarded conversation protection are **DEFERRED**, not
passed. Shared chat-history behavior remains **UNRESOLVED**. The upstream vendor
request is **OPTIONAL / UNSENT**, not a prerequisite for this delivery.

Implementation, all six repairs, both FPR-OPS-1 investigations/captures, the
bounded Cursor-integration pass and FPR-OPS-2 dependency repair remain complete.
No completed tests, experiments, pilots or reviews are rerun. No final review,
vendor contact or release is started by this documentation-only revision.

## Exact candidate and authority

The [owner-approved manual delivery scope](../decisions/FPR-5-MANUAL-DELIVERY-SCOPE.md)
and current [acceptance scope](FPR-5-ACCEPTANCE.md) govern this packet. They
supersede automatic-host and client-protection prerequisites in the earlier
[restoration plan](../decisions/FULL-PRODUCT-RESTORATION-PLAN.md) and
[owner closeout](../decisions/FPR-5-OWNER-CLOSEOUT.md). Earlier decisions, reports,
inventories and original findings remain historical evidence. The implemented
product and all other retained requirements remain; the old bounded snapshot
is not substituted for this candidate.

The closing owner-clarification documentation commit is the review candidate.
Its parent/base is `a1751f84604f634521020c93c67050d9127bd6b1`, the original
scope-reconciliation closing commit (whose parent was
`f5e945c8832efe6ec12ca60f3735f329b1901203`). Canonical NEXT records the new base and
its bound reader validates the closing commit. At appointment, record the full
closing commit plus the runtime/native identities below in the reviewer record.
Only the scope documents, paired summaries, optional-request status annotation,
summary lock rows and canonical NEXT change. No host/guard build manifest or
vendor response is required for the revised claim. No new release archive or
binary is assembled; historical artifact digests keep their original meaning.

| Identity | Value |
| --- | --- |
| Physical/Git root | `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014` |
| Name / UUID | `overseer-kit` / `6988dc4a-5f22-454b-9d68-ac5905b383bf` |
| Branch / lane | `feat/overseer-v1-recovery-20261014` / `product` |
| Packet opening commit | `d6d6b92d0f10c58a41e25678835f2436b1a5f827`; sole parent `829dc3352c6510cd5623afa72a032de868a05f3f` |
| Reconciliation opening commit | `be54c121253fd7d5fd5228b822f9b88ee377692b`; sole parent `c247186f139c7916a38030ff25fba30f5aa94576` |
| Cursor-integration pass opening commit | `4efbeb2d38c2ab43568fe455355bf7081fbe3095`; sole parent `be54c121253fd7d5fd5228b822f9b88ee377692b` |
| Six-repair source commit | `2e8ec694def9be4a0faa4a994bf2fff3f212ab23` |
| Last production delta | Native window configuration recorded in `7ee9a372e478ad251c17d8e8fd1a4118811c01b2`; subsequent commits change only documentation/evidence and summary locks |
| Python runtime | `1.0.0.dev1`, SHA-256 `cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774` |
| Native configuration | `desktop/src-tauri/tauri.conf.json`, SHA-256 `d65242ef9ca4be228e791d7596bd2a60ff90ba200445c0d5dbf58229c5eecab6` |
| Recorded observed binary | SHA-256 `a515148a94ffebb88e7520fb194bc0287967484896c44900e6d7ab4e7b364551`; historical observation, not a claim of present binary availability |
| Original independent verdict | **FINDINGS**, preserved in [FPR-5 review](../reviews/FPR-5-REVIEW.md); author repairs do not replace it |

[Original packet source verification](fpr5-closeout/source-and-evidence.json)
compared its entry checkout to the final-candidate record: **295 runtime, 440
test, 40 native, ten packaging, four validation-driver and two requirements
entries match**. Among
the 1,483 recorded source archive members, only ROADMAP and HANDOVER differ at
packet entry, reflecting later documentation. New evidence files were added
after the old archive; this is not a claim that the full checkout equals that
archive or that an updated release artifact has been built.
The latest [repair closeout](fpr5-legacy-repair/closeout.json) retains the same
791 source/test/native/packaging/driver/requirements entries and runtime.
This pass changes documentation and summary lock rows only. Older
packet/summary hashes attest their historical revisions, not this edited packet.

## Exact proposed claim and exclusions

The target is the selected **macOS 15.7.2 arm64 source installation**, maintained
CLI, local browser app, actual desktop and local read-only hosted surface;
Git-only, Muse-only and Muse-with-Git-mirror modes; Python 3.11.15 and 3.14.4 Git
cells plus Python 3.14 with pinned Muse 0.2.1rc5. Identity, lanes, settings,
canonical NEXT, installation, migration, update and rollback remain required.

The supported workflow uses explicit bound `ok -C ROOT next` reads after
selecting the repository/lane and checking returned identity/context, with
`next-write` publication using explicit context and the expected prior digest.
Instruction bookends are manual coordination, not native lifecycle evidence or
client-wide execution protection. The existing browser is sufficient.

The owner's subsequent clarification retains automatic prompt display as a
convenience. Before each new task, the agent or operator must explicitly retrieve
fresh repository-bound NEXT and check its identity/context; use that result,
not an earlier displayed, restored or forwarded instruction. Stop on refusal
or wrong context. An agent's fresh validated read does not require an additional
button click; this is per task, not per message. Existing implementation and
hook settings, including disabled hooks, are preserved. No automatic-freshness
fix, client code change, hook activation or client-wide enforcement is claimed.

The supportable **current status** is completed author implementation/repair,
validation, local integrated workflow and owner-observed desktop evidence,
submitted with the custody limits below. Independent acceptance is pending.
The original FINDINGS verdict and full automatic-pilot nonacceptance remain.

The exact **revised acceptance claim proposed to the single non-author** is:

> The frozen source candidate identified by the review commit and retained
> runtime/native digests satisfies the owner-selected manual delivery scope:
> maintained CLI, local browser app, actual desktop and local read-only hosted
> surface on macOS 15.7.2 arm64; Git-only, Muse-only and Muse-with-Git-mirror modes;
> Python 3.11.15 and 3.14.4 Git cells and Python 3.14 with pinned Muse 0.2.1rc5;
> identity, lanes, settings and explicit repository-bound canonical NEXT;
> source install, migration, update, rollback and the completed local integrated
> workflow. The six original findings are resolved on the recorded evidence.
> Acceptance uses surviving curated records and historical owner desktop
> observation with explicit custody limits. Actual Cursor sessionStart/stop,
> their automatic-pilot continuity, and client-level restored/forwarded task
> protection are deferred and unverified/unqualified, not passed. Shared
> chat-history behavior remains unresolved. This claim does not certify the
> former automatic full-product contract or authorize release or consumer rollout.

This is a proposed verdict, **not current certification**. The adjudicator may
accept or block it based on the retained requirements and evidence sufficiency.
No missing original has been identified as indispensable to this limited claim;
that submission basis does not predetermine the independent verdict.

No Windows/Linux qualification, signed/notarized native installer, new hosted CI,
live provider/private production Muse transport, live delivery, real-consumer
migration, sustained multi-user use or malicious same-UID/root protection is
claimed. Read-only hosted fixtures remain distinct from live upstream acceptance.
The legacy installation's limited handoff binding and installation-footprint
drift remain separately scoped rollout conditions. The optional vendor request
and future automatic integration require separately authorized work and supply
no current acceptance evidence.

## Requirement-to-evidence map

The first ten rows below retain author validation for the recorded source. They
are not independent final acceptance. [FPR-4 section-9 mapping](FPR-4-COMBINED.md#section-9-evidence-matrix),
[FPR-5 repaired coverage](fpr5-repairs/coverage.json) and the final-candidate
comparison provide the cross-source chain; older runs are not relabelled current.

| Required outcome | Evidence and present disposition |
| --- | --- |
| Three authorities and independent repository identity | FPR-4 three-mode composition and repaired integrated native groups: pinned native Muse, Git fixtures, distinct UUID/root/runtime and no fallback. Local author evidence recorded; no live transport claim. |
| Lanes, workspace membership and canonical NEXT | Explicit lane ownership/freshness, collection CAS, nested/linked boundaries, wrong/copy/stale context refusals; R5 repairs repeat init. This is repository service coverage, not proof of editor conversation restoration. |
| Manual NEXT and adapter contract | Real bound reader/writer and read-only event fixtures; exact closing-revision and context races. Manual reads pass. Actual Cursor events are deferred from this delivery, not satisfied by fixtures or Codex instructions. |
| Maintained CLI workflows/settings | Real dispatcher, local governance, review/Check OK, checkpoints/ledger/routing/landing/compaction; fake provider/transport coverage and R2/R6 repairs. See command map below. |
| App, desktop and hosted controls | FPR-4 auth/CSRF/origin/path/identity/lifecycle coverage, original reviewer HTTP supplement, R1/R4 repairs; later native startup/quit and owner rendering evidence. No live upstream request is required or claimed. |
| Full legacy migration | Settings/lanes/docs/ledger/owner assets, backups, partial resume and collision protection; R3 failing-before/passing-after and new pilot migration evidence. No real-consumer migration performed. |
| Bounded migration and authority adoption | Schema-1 Git and schema-2 native/config transitions, exact matching restore and tracked-binding preservation/refusal. Recorded FPR-4/repair native cases. |
| Mirrors/reconciliation/credentials | Native objects plus isolated Git target, bundle/delta/exclusion/parent/CAS/retry checks and scoped fake transport/credentials. Permission to execute live delivery is absent. |
| Fresh source install and resource integrity | FPR-4 package/entrypoint evidence plus R4 actual membership verification and the separate repaired-package rerun; complete dependency preparation and final-candidate affected package cases. No new binary release assembled here. |
| Upgrade/rollback | FPR-4 13-check compatible/bounded cycle plus new pilot repaired-to-parent-runtime-to-current cycle. Parent defects remain known; rollback operability does not certify that older build. |
| Complete environment cells | Python 3.14/native: **1,361 distinct cases with passing evidence**, from 1,360 passes/one scheduling failure plus two-case rerun. Python 3.11: **1,196 distinct passing cases**, from 1,195 passes/one setup failure plus corrected-prerequisite rerun; two package cases cover the native configuration delta. Do not add overlapping counts or call either original execution all-green. |
| Local integrated pilot workflow | [RESULTS.json](fpr5-acceptance/pilot/RESULTS.json): local workflow passed and remains submitted for the revised scope. Actual host events are absent and deferred; original full automatic-pilot acceptance stays false. Historical project state is recorded; its temporary project is now unavailable. |
| Actual native desktop | [Owner observation](fpr5-interactive/observations/owner-observation-desktop-0pkcm8sj/user-observation.json): rendered app, bound pilot and both canonical action blocks; normal quit. Screenshot originals are unavailable; retain the observation's provenance and limits. |
| Actual Cursor sessionStart / stop | **DEFERRED / NOT VERIFIED**, excluded from this delivery. The keychain-gated isolated attempt and forced cleanup remain failures/incomplete evidence. No repeat launch or permission change is authorized. |
| Client restored/forwarded conversation protection | **DEFERRED / UNQUALIFIED**, excluded from this delivery. Shared chat-history behavior remains **UNRESOLVED**; no wrong-project write or historical cause was established. |
| Final adjudication / owner release | Neither performed. One non-author adjudication after required evidence/dispositions, then a separate owner release decision. |

The unchanged historical **1,391 passed / 104 failed** baseline and all raw
subsequent failures remain. [Disposition accounting](fpr4/disposition-closeout-coverage.json)
and the [independent semantic map](../reviews/fpr5/evidence/independent-semantic-replacement-map.json)
describe replacements; selection accounting alone cannot certify behavior.

## Complete command inventory

The actual bound `--help` read confirms all **20 historical command names** are
registered, plus `next-write`, `adopt`, `mirror` and restricted `hook`. The
[enumeration record](fpr5-closeout/command-inventory.json) proves presence only;
the behavior evidence is the retained/repaired integrated selection and these
requirement families. No hidden legacy dispatcher is selected.

| Commands / subcommands | Evidence family and boundary |
| --- | --- |
| `status`, `init`, `sync` | Foundation/context/full settings/migration/footprint; R3 owner collision and R5 repeat-init regressions. |
| `next`, `next-write`, restricted `hook` | Canonical reader/CAS writer, revision/lane/identity and scripted adapter parity. Host-native delivery remains unverified. |
| `adopt`, `upgrade-regime` | Native authority/config-last adoption/restore, migration and explicit upgrade plans. |
| `mirror prepare/reconcile/verify/deliver` | Native export and isolated Git correspondence, controlled fake transports; real delivery prohibited. |
| `review`, `check-ok`, alias `check-if-ok` | Retained local/API-fake/human paths, freeze/checklist/gate settings, pilot local review. Blocked human review is not a pass. |
| `governance-sync`, `handover-compact` | FPR-3/4 configured docs, local update/compaction and preserved NEXT; canonical publication is separate. |
| `workspace status/check-next/doctor` | Member identity, required/optional membership and canonical relay diagnostics. Does not own editor chat selection. |
| `verify-step` | Built-in checkpoints and R6 configured dry-run/no-execution plan, explicit execution and confinement. |
| `honesty-status`, `ledger append/verify/show` | Retained honesty/evidence/gate/chain checks, reviewer HTTP supplement and pilot accurate append/read/verify. |
| `route` | Retained routing/tier/gate-policy resolution and validation; no model dispatched by enumeration. |
| `app`, `hosted-dashboard` | Actual local HTTP/desktop-child/auth/control/read-only boundaries and R1 redirect refusal; live upstream unclaimed. |
| `land-check`, `land-closeout`, `pr-land` | Retained explicit-effect/fake-gh cases and R2 configured repository/response identity. No actual merge or delivery. |

## Six findings: evidence prepared for the final non-author

All six remain subject to that final adjudication. This table reports repairs;
it does not change the original review verdict.

| Finding | Repair / direct evidence |
| --- | --- |
| R1 hosted redirects | Default transport refuses redirects; [transport before/after](fpr5-repairs/transport/README.md), 97 final transport cases shared with R2. |
| R2 PR target binding | Explicit configured repository, selector/response validation and drift refusal; same transport record and [source map](fpr5-repairs/source-map.json). |
| R3 owner collisions | Preserve owner bytes/modes/classification, backups and resume; [foundation evidence](fpr5-repairs/foundation/README.md), 23 final cases shared with R5. |
| R4 resource membership | Exact source/runtime tree membership and provisioned dependency admission; [resource evidence](fpr5-repairs/resources/README.md), 18 cases plus affected entrypoints. |
| R5 multi-lane repeat init | Explicit validation of each present lane, no invented entry or rewrite; foundation evidence above. |
| R6 orchestrator dry-run | Confined no-execution planning, unchanged executor mutation guard; [before](fpr5-repairs/orchestrator-before-r2/results.log) and [after](fpr5-repairs/orchestrator-after-r2/results.log), 14 new cases within final integration. |

## Reconciled outcomes and current dispositions

The completed source investigation demonstrated propagation from seeded shared
routes. The later distinct-route custom-editor persistence/restore cycle kept
the routes separate. Its explicitly injected membership mismatch reached actual
client `thread/resume` preparation/dispatch with the retained thread cwd.
Backend acceptance, effective sandbox grants, turn/tool execution and wrong-root
writes were not observed. This informed the now-deferred guard proposal, not a historical
causal finding. Neither investigation is an outstanding action.

The dependency repair installed 190 exact approved local files only into the
stable checkout's venv. Its source, interpreter, external Python targets and
global wrapper were preserved; focused preparation/validation and rollback
rehearsal are complete. The missing-cryptography failure is historical. Preserve
the [verified backup and guarded rollback](FPR-5-LEGACY-CLI-REPAIR.md#verified-rollback);
do not rerun repair or rollback.

The prior gate identifiers are retained with explicit new dispositions. B1/B2
are deferred exclusions, not prerequisites or passes. B3's submission basis is
recorded; B4 and B5 remain the two required decisions.

| Gate | Current disposition / remaining action | Completion criterion |
| --- | --- | --- |
| B1 — FPR-OPS-1 task/host admission | **DEFERRED / UNQUALIFIED** for this delivery. Vendor request optional and unsent. No supported contract, adapter, guard build or external response required now. | Exclude client-wide restored/forwarded protection from the accepted claim. Shared chat-history behavior remains unresolved; historical cause remains unknown. Future qualification needs separate scope and evidence. |
| B2 — actual automatic host events and dependent pilot | **DEFERRED / NOT VERIFIED** for this delivery. Retain the completed local workflow evidence and original full automatic-pilot nonacceptance. | Exclude actual sessionStart/stop and their automatic workflow continuity from this claim. No native receipts, new launch or pilot rerun required now. |
| B3 — FPR-EVID-1 claim/evidence disposition | **Submission basis recorded:** surviving curated records with their stated limits. No additional approval or original acquisition queued. | Report historical owner observation, not missing screenshot pixels, restored unredacted logs or a live old fixture. Final sufficiency belongs to B4; any indispensable gap must name its exact retained claim/artifact. |
| B4 — one final non-author adjudication | Pending owner appointment in a fresh non-author session; do not start in this scope-change action. Use the closing commit, runtime/native identities, revised claim and brief below. | One recorded ACCEPTED/BLOCKED verdict on every retained requirement, R1–R6, manual workflow and custody sufficiency. Preserve original FINDINGS and explicit B1/B2 deferrals. No author self-certification. |
| B5 — owner release decision | After successful B4, present the exact accepted candidate/claim for a separate release disposition. | Owner identifies version/artifact/destination and permitted effects, or holds. Acceptance alone authorizes no publication, main merge, signing, deployment or consumer rollout. |

**Rollout conditions, not reopened candidate/dependency work:** the repaired
legacy CLI supports root selection and config-path confinement, but not modern
UUID/branch/digest assertions, canonical `next-write`, or identity comparison of
its extracted handover fence. Before any separately authorized existing-consumer
rollout, the installation owner must select a modern bound runtime (or separately
scope a legacy source change), name each target, preserve configuration/history
and rollback, and establish correct root/UUID/branch/lane/revision/digest readback
and mismatched-context refusal. Do not redirect the global wrapper now. The
candidate's fixture migration/install evidence is already complete; no existing
consumer is an acceptance fixture. Likewise, classify and resolve the intended
target's owned-asset/lock drift during that explicit rollout; owner assets and
NEXT must survive, and remaining drift must be disclosed. Updating the two
summary lock rows here is not a full sync. Neither rollout condition is cured
by clean Git state, and neither justifies another dependency repair or pilot.

FPR-OPS-1 is not established as an Overseer, Cursor, Codex, restart or owner
defect. The owner did not deliberately open duplicates. The dependency failure
does not explain shared chat display. A guard can address unsafe admission
without proving or preventing every historical route-selection mechanism.

## Deferred host guard proposal — historical design boundary

The following proposal is retained for optional future work, not as an acceptance
obligation or pending task for this delivery. It was inferred from the completed
traces; the prior bounded pass found no justified repository repair under that
interface. No guard was implemented. Separate authorization and a supported
host contract would be needed before future implementation.

| Boundary | Exact work and acceptance obligation |
| --- | --- |
| This repository can implement | Reuse physical-root/UUID, authority branch/revision and canonical NEXT checks in `cli/v1.py`, `cli/v1_revision.py` and the dispatcher. Once the host contract is agreed, expose/validate a versioned binding record and adapt `cli/product_bookends.py` to consume required trusted context at the agreed entry point. Refuse the repository's own affected operation on missing, stale, ambiguous or mismatched context; preserve manual NEXT and existing CAS/lane behavior. Add only newly affected disposable checks. Repository checks must match the frozen host contract; they cannot manufacture its trust. If no new adapter is required, document that with the agreed contract rather than adding speculative machinery. |
| Client / extension host owner must implement | Derive an explicitly selected repository from actual window membership, including physical root, UUID, branch/revision, host identity and membership generation. An outer directory or multi-root window must not silently select its first root. Hydrate authoritative thread/task metadata, compare bindings before resume for work, stream-owner acquisition and turn submission, and permit only labelled read-only inspection when invalid. Never rewrite cwd or widen roots to force a match. |
| Client protocol / execution-owner owner must implement | Carry a host-issued sender-context token for forwarded requests; validate the actual sender and current task at the execution owner. Recheck at turn/steer and tool dispatch. Invalidate on root, revision, membership, thread or owner changes. A mismatched viewer cannot redirect, stop or gain authority over an unrelated correctly bound owner. Intentional cross-project work requires explicit new binding. |
| Joint completion evidence | Identify exact host/protocol/owner and adapter builds; demonstrate matching-context operation, wrong/missing/stale binding refusal, multi-root ambiguity, linked worktree and symlink handling, drift from admission to dispatch, and follower/owner isolation at the effective enforcement boundary. An outgoing mock request alone is insufficient to prove backend/tool refusal. Evidence must be confined to separately authorized new guard behavior, without repeating the completed experiments or using real consumers. |

Current hooks accept empty input and optional root assertions, and generated
hooks use `failClosed: false`; they supply NEXT presentation, not task-execution
admission ([source investigation](FPR-5-HANDOFF-RELIABILITY.md#source-trace-and-the-limits-of-each-link)).
NEXT wording, a hook flag or a repository-only comparison cannot supply trusted
host tokens or stop unrelated client/backend tools. Do not patch installed client
bundles. Assign those changes to their source/protocol owners; contacting them
or sending evidence externally requires separate authorization.

## Historical bounded Cursor-integration pass outcome

**No new repository repair is justified for the demonstrated mismatch with the
available host interface.** This is a scoped implementation decision based on
the existing findings, not a claim that every possible future host interface
is incapable of supporting a repair. No installed client source was accessed
again and no experiment, functional test or general review was run.

| Protection / missing control | Existing code and result |
| --- | --- |
| Overseer's own project and installation | `cli/v1.py:108–140,162–204` binds physical root, launcher location, project UUID and runtime, then detects changed configuration/revision. These protections already exist. |
| Canonical task read/publication | `cli/v1.py:262–301,314–349` validates root/identity/authority/branch/lane and freshness, with explicit expected digest and context rechecks. `cli/main.py:210–237` uses the same display service and recheck for hooks. These are not new repairs. |
| Hook transport | `cli/product_bookends.py:103–159` validates the bound hook and any supplied root/identity/lane/event assertions. Empty input remains compatible. Lines 33–41 generate `failClosed: false`; lines 162–167 return presentation text, not execution authority. Existing `tests/fpr1/test_bookends.py` covers this contract; it was read, not rerun. |
| Client task admission and tool execution | The saved capture reaches client resume dispatch without an Overseer admission call. There is no supported trusted window/task/sender token or mandatory client-tool veto available to this repository in the recorded interface. An invented token, mandatory optional fields or a hook toggle would not establish the required protection. |

The two repository files pinned by the prior investigation (`cli/v1.py` and
`cli/product_bookends.py`) still match its recorded hashes. No source, browser,
tests, dependencies, runtime binding or hook configuration changed. No new
behavioral pass is claimed; document links, request consistency, permitted file
scope, summary lock rows and canonical NEXT are the mechanical closing checks.

The [external request](../decisions/FPR-OPS-1-CLIENT-CHANGE-REQUEST.md) identifies
extension-host selection, renderer resume/turn admission and actual execution-owner
enforcement separately, with exact recorded versions, synthetic observations,
limitations and completion criteria. It does not allege proven backend escape,
wrong-root writes or a Cursor restoration cause. No recipient has been contacted
and no supported implementation commitment or fixed build is available in the
existing evidence. Future repository adapter work is conditional on that contract,
not a task to repeat while waiting.

## Surviving evidence and unavailable originals

[Availability/disposition details](fpr5-closeout/evidence-availability.json)
verify the curated copies against the prior inventories:

- The 40 interactive records survive: **34 byte-identical copies and six
  deliberately redacted logs**. Redacted lines cannot now be re-read from their
  unavailable original paths; redaction metadata remains.
- The 79 host/platform copied records survive: 77 byte-identical and two
  redacted. Binary/profile/cache trees were explicitly outside the durable copy.
- The pilot's 28 curated records survive, including raw failed attempts and the
  deliberately invalid ENOSPC-truncated JSON. Its temporary project and external
  backup trees cannot now be inspected at the recorded root.
- Both original owner screenshots are absent at recorded paths. The committed
  observation, copied NEXT text/comparison, hashes and normal-quit record survive.
  This supports reporting an owner observation, not a new independent visual
  inspection. No screenshot or original is reconstructed.

The disappearance cause is unknown. No deleted-original claim is based solely
on the reported restart. Under the no-repeat instruction, continue with explicit
custody limits; if a later readiness assessment requires an unavailable original,
identify that exact claim and evidence gap before any new acquisition or test.

The following evidence would be required only to qualify the **deferred**
automatic/client-protection claims in a future scope. It is not indispensable
to the revised manual delivery claim and is not queued for acquisition:

| Claim still awaiting evidence | Exact missing evidence and disposition |
| --- | --- |
| Project-safe restored/forwarded task execution | Supported host/task binding contract and identified client/owner builds, plus evidence of effective mismatch refusal through execution (B1). The existing capture stops at request dispatch and cannot supply this. Deferred; an external implementation path is optional future work, not a delivery prerequisite. |
| Actual automatic Cursor start/end and complete integrated workflow | Two real native-event receipts showing correct canonical action/context and their link to the completed workflow (B2). They were never established and are now **DEFERRED / NOT VERIFIED**. Any future qualification must separately scope the required continuity evidence. |

The unavailable screenshots would be indispensable to a new pixel inspection;
unredacted logs/incident-time state to a stronger causal claim; the live old
fixture to a fresh inspection of that historical environment. None of those is
asserted in the proposed custody-limited claim. The owner observation, copied
NEXT comparison, quit record and curated workflow records remain the submission
evidence. No additional original-artifact acquisition is justified in this pass.
The final reviewer may still identify a precise indispensable gap; that is not
permission to reconstruct or rerun anything.

## Concrete next action

The documentation scope reconciliation is complete. The owner appoints **one
independent non-author session** to execute the revised brief below. Until that
appointment, stop; do not run review from the author/coordinator session. No
vendor response, automatic event receipt, new pilot, original reconstruction or
extra readiness-review cycle is a prerequisite for appointment. The reviewer
still decides the sufficiency of all retained evidence.
The owner appoints that fresh reviewer by supplying the prepared canonical NEXT
review prompt to it. The author/coordinator stops after preparing this handoff.

After an ACCEPTED verdict, the owner makes the separate release decision for
that exact candidate and limited claim. A BLOCKED verdict must name the precise
retained requirement/evidence gap for an owner-scoped response; it does not
silently reintroduce deferred requirements or authorize rerunning completed work.
The prepared vendor request stays optional and unsent.

## Brief for ONE final non-author adjudication — pending appointment

**Appointment gate:** the owner appoints one non-author after this documentation
handoff, by supplying the prepared review prompt to the fresh session. Recording
the workflow decision is not review execution or author self-appointment. Read the
closing source commit through validated NEXT and record its full Git identity,
the retained runtime/native digests and the explicit B1/B2 exclusions. No future
host manifest or guard/event evidence is required for this revised claim.

**Reviewer:** one fresh GPT-6 Astra / High session whose reviewer authored neither
the implementation, six repairs nor this scope closeout. Read AGENTS.md and
validated NEXT for location and authority. The current owner scope overrides
historical automatic-host prerequisites; earlier bounded-v1 certification is
not certification of the current candidate.

**Inputs:** this packet and exact revised claim; the
[manual delivery decision](../decisions/FPR-5-MANUAL-DELIVERY-SCOPE.md), closing
commit/diff and retained component identities; the
[original product definition](../decisions/FULL-PRODUCT-RESTORATION-PLAN.md#definition-of-complete)
with the explicit current deferrals; [original FINDINGS](../reviews/FPR-5-REVIEW.md),
[six-repair evidence](FPR-5-REPAIRS.md),
[combined requirement mapping](FPR-4-COMBINED.md#section-9-evidence-matrix),
[selected acceptance](FPR-5-ACCEPTANCE.md),
[desktop observation](FPR-5-INTERACTIVE.md),
[historical owner closeout](../decisions/FPR-5-OWNER-CLOSEOUT.md), both OPS1 reports,
OPS2 repair/rollback and the custody records above. The optional external request
supplies context only, not proof of protection or a required vendor response.
Counts, raw failures and changed-contract dispositions remain separate.

**Task:** adjudicate the revised manual delivery claim once using read-only source
and surviving evidence. Decide R1–R6 individually and all retained environment,
authority, command, surface, manual NEXT, installation/migration/rollback and
local-workflow requirements. Decide custody sufficiency. Distinguish repaired
legacy CLI startup from modern consumer binding. Confirm B1/B2 are excluded
and unverified/unqualified, and shared chat-history behavior remains unresolved.
Do not rerun completed tests, experiments, pilots, failed launches or the general
architecture/build review. Owner choices and author validation are not independent
findings; a scope deferral is not a pass.

**Required output:** one reviewer-attributed record tied to the closing source
commit and component digests; verdict **ACCEPTED** or **BLOCKED**; R1–R6 and
retained requirement-to-evidence decisions; explicit deferrals and custody limits.
Every blocker names the retained requirement, exact evidence gap, responsible
component and completion criterion. If an absent original is indispensable,
identify its claim/artifact without reconstructing it or launching acquisition.
Preserve the original FINDINGS and all raw failures. No additional general review
cycle, author self-certification or publication permission. A successful verdict
proceeds only to the owner's separate release decision.

**Restrictions:** no real profiles/accounts, keychain/privacy changes, installed
client/global/consumer mutation, hooks, provider/network access, live export or
delivery, fetch/push, main merge, tags, signing or deployment. Read-only source
and committed evidence inspection, with only the review record and necessary
bound handoff maintenance written after appointment. Do not infer broader
authority from this brief.

## Closeout discipline

This pass changes only the manual scope decision, acceptance scope and packet,
paired summaries, optional-request status annotation, two summary lock rows and
bound NEXT. Original report bodies/review, failures, inventories, source/tests,
dependency pins and disabled hooks remain unchanged. The user's no-repeat
instruction overrides the standing pre-feature-commit suite rerun. Verify only
document/link/whitespace consistency, allowed changes, preservation, summary lock
rows and bound NEXT publication/readback. No behavioral test or review runs.

Preserve old worktrees, protected refs and Muse history. Publish NEXT through
bound `next-write` with explicit context and prior digest as the prepared review
brief for the owner's fresh non-author session; the author must stop. The
clarification's local documentation closing commit uses
`a1751f84604f634521020c93c67050d9127bd6b1` as sole parent, followed by validated
NEXT readback. ROADMAP/HANDOVER summarize; canonical NEXT carries the pending
action. No vendor contact, network/provider work, release or rollout is authorized.
