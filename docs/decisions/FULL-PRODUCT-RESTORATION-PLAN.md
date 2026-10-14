# Full-product restoration plan — FPR-0

Decision date: 2026-10-14. Action: `OVERSEER-FULL-PRODUCT-RESTORATION-ANALYSIS-1`.
Status: analysis complete; implementation requires separate owner acceptance of
canonical FPR-1 NEXT. This is not a restored-product or release-readiness claim.

## 1. Verified boundary and evidence vocabulary

All source comparisons below use committed objects read from the current clean
worktree. No command ran in either older product/recovery worktree. No product
suite, completed review, installation/rollback exercise or pilot ran in FPR-0.
No provider, consumer, network, Muse store or release directory was accessed.

| Opening observation | Verified value |
| --- | --- |
| Physical cwd and Git top-level | `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014` |
| Branch | `feat/overseer-v1-recovery-20261014` |
| Full opening HEAD, called **S** below | `0b763df6d7c9066582d27b349a731a4ff70a43e2` |
| Configured name / checkout UUID | `overseer-kit` / `6988dc4a-5f22-454b-9d68-ac5905b383bf` |
| Lane / model | `product` / `GPT-6 Astra` |
| Runtime digest | `b7fa1921fcb586ac6fcf8422f094fe20f9f9a438f64eecdaddd97d347115db95` |
| Opening status | Clean; bound `status` and `next` both succeeded |
| Canonical NEXT SHA-256 | `4ab789c34f0825363dd2fc289a1b9afb7481edb07f2a25f6e7e1f01999accaab` |
| Closing-commit condition | S has exactly one parent, `3ed3b7d406e4e68186303481b2d32b87abb1d7d3`; its three changed paths are NEXT, ROADMAP and HANDOVER; committed NEXT equals the validated disk bytes |

Read first: [AGENTS](../../AGENTS.md), [ROADMAP](../ROADMAP.md),
[HANDOVER](../OVERSEER-HANDOVER.md), [NEXT](../NEXT.md),
[bounded scope decision](V1-SCOPE-RESET.md) and
[bounded certification](../validation/V1-CERTIFICATION.md).

Immutable source keys used throughout the inventory:

| Key | Committed source and role |
| --- | --- |
| **P** | `feat/overseer-context-isolation` = `e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`: full product, bookends, lanes and historical architecture record |
| **M** | `feat/overseer-v1-recovery` = `32254cd939885d9d6f40634997ea5b9c37ea776c`: optional Muse authority, adoption, controlled mirror/reconciliation, scoped credentials and retained hosted-validation record |
| **B** | `348e0f323a3b17cd5022a1bfd56fa09a6831c51f`: repaired repository-bound implementation, present unchanged in S |
| **D** | `main` = `d47291d5d9030de5ebef713da95efa978c4d8c6e`: reconciled main baseline and full-product code already retained by S |

`P:path`, `M:path`, `B:path` and `D:path` are immutable evidence references, read
with `git show FULL_COMMIT:path` from this worktree. They are not instructions to
visit another worktree. Branch tips matched these pins at the opening and must
be checked again before each later wave. An unexpected move or unrelated dirt is
a stop condition, not permission to chase a newer source. Existing refs other
than this action's expressly authorized current-branch closing commit, worktrees,
Muse history, snapshots, rollback fixtures, pilot and bounded source-release
directory stay preserved.

## 2. How the active product was narrowed

The evidence distinguishes loss of access from loss of implementation:

1. **Moved, not deleted:** D's 535-line `cli/main.py` is byte-identical to
   S's `cli/legacy_main.py`, P's `cli/main.py` and M's `cli/legacy_main.py`.
   The bounded commit `d8f10d8` redirected `cli/main.py` to `cli.v1`; the isolated
   bootstrap imports `cli.v1` directly. Changing only `cli/main.py` cannot restore
   the product. The old parser contains 20 command names, including one alias.
2. **Disconnected:** all P paths under `cli/commands/`, `tools/`, `adapters/`,
   `desktop/` and `tests/` remain in S. Of 633 paths, 627 have identical blobs.
   The six differences are `adapters/muse_only/adapter.py` and five corresponding
   test files; D/S use `rev-parse --abbrev-ref HEAD`, while P uses the incompatible
   `branch --show-current` path. Keep D's compatibility repair. Most full-product
   engines therefore need integration at their boundaries, not restoration of
   missing bodies.
3. **Replaced configuration and public claims:** S's strict five-key bounded
   schema accepts only Git and one lane/model context. The former full config
   survives in `docs/archive/v1/config-before-reset.yaml`; typed parsers, fixtures,
   policies, ledger and version lock remain. The bounded parser rejects the old
   settings rather than using them. README, rules and test selection were narrowed
   to the five-command claim. The 393 original test/support files were preserved;
   default collection no longer exercises most of them.
4. **Disabled bookends:** S's `.cursor/hooks.json` and distributed
   `cursor/hooks/hooks.json` contain empty hook maps; historical scripts exit
   immediately. B can generate bound hooks through explicit `init/sync --hooks`,
   but active installation hooks are not enabled. P's scripts provide useful
   lane presentation and start/end UX, but discover `ok` through environment/PATH,
   scrape YAML with awk, read HANDOVER prompts and invoke governance at closeout.
   Reuse the outcome, not those unsafe resolution/regeneration paths.
5. **Actually deleted or moved on M:** M removes the checked-in `.cursor` hook,
   rule and skill copies and moves `.overseer` config/policy/ledger/version-lock
   files into `docs/archive/v1/legacy-overseer/`. Distributed `cursor/` sources and
   product engines remain. These branch-specific removals must not be imported
   as a new product decision.
6. **Added only on M:** `cli/v1_revision.py`, `v1_muse_reader.py`, `v1_policy.py`,
   `v1_mirror.py`, `v1_mirror_reader.py`, `v1_mirror_history.py`,
   `v1_git_credential.py`, native Muse tests, adoption/credential/artifact tests,
   CI artifact verification and the supported hosted workflow are absent from S.
   M is the source for these capabilities. Its monolithic `v1.py` predates B's
   captured-context/closing-revision fixes and must not replace B wholesale.
7. **Superseded mechanisms:** the bounded decision explicitly retired OCI
   distribution/transaction machinery, native/Mach GSR, UID sole-writer storage,
   identity bridges and packet-chain prerequisites. P's OCI phase document is
   historical design/review evidence, not proof of a committed working runtime.
   Uncommitted work in preserved checkouts is outside FPR-0 evidence. No feature
   inventory entry may infer a working implementation from that material.

The history does not justify calling the full product broken or obsolete. It
shows a deliberate smaller milestone and several incompatible integration
contracts. The present task supersedes that smaller endpoint while retaining its
valid safety work and certification history.

## 3. Integration base and source-selection decision

**Continue on S, after this documentation-only closing commit.** Use its D-derived
full-product modules as the product body and B as the repository/NEXT safety
foundation. Selectively integrate M's authority and mirror modules. P supplies
the historical product contract, bookend UX and lane acceptance intent; most of
its working code is already present through D.

This choice follows blob comparisons, not chronology. Starting on P would remove
the Muse command compatibility repair and require reapplying every certified
safety boundary. Starting on M would still leave the full CLI disconnected,
import unwanted footprint removals and lose B's R1/R2 repairs. Starting on D
would discard the repaired binding/NEXT foundation for no product-code gain.

Use a file/function-level source map in each wave. Keep existing module names
where practical; separate the CLI dispatcher, validated context, config
normalization, revision backend and NEXT service only enough to share them.
Adapt existing `cli/commands/*` and `tools/*` entry boundaries to that context.
Do not route user commands to `legacy_main.main`, duplicate the old parser as a
second product, blindly merge M, wholesale revert the scope reset, or rewrite
working engines. Retain legacy source/tests as evidence where contracts change.

The source map must distinguish exact reuse, adapted boundary and superseded
behavior with its replacement acceptance case. Existing tests for old prompt
scraping are evidence of a former contract; they cannot force restoration of a
second NEXT authority. Existing useful algorithm/security tests should remain
tests of the maintained engines.

## 4. Complete capability inventory

Test names below refer to committed files, not newly claimed passing results.
`tests/*/test_X*` means the matching preserved unit, integration, e2e, security,
data-integrity, performance and stress families; the wave's test map must enumerate
the concrete selected files. D is the best source where it is already identical
in S; P is not copied merely to make restoration look larger.

| Capability / best source | Present state and dependencies | Preserved tests / required work |
| --- | --- | --- |
| Automatic start/end NEXT: P `cursor/hooks/*`, B `cli/v1.py:hook_script,assets,main` | Active hooks disabled; B has bound fixture hook support. Depends on canonical NEXT, host event format and validated root/lane. | `tests/*/test_lt_*`, `tests/v1/test_commands.py`, `test_isolation.py`, `test_context.py`. FPR-1 installs owner-selected bound lifecycle adapters, restores both bookends, tests refusal and no regeneration; FPR-2 adds multi-lane presentation. |
| Manual NEXT: B `validate_next`, `rendered`, `write_next`; P/D `tools/print_next` for presentation only | Supported for Git/single context. Old extractor reads HANDOVER and is superseded as an authority. | `tests/v1/{test_commands,test_integrity,test_context}.py`, `tests/*/test_print_next*`. Preserve canonical bytes, digest CAS, stale/context refusal, unborn and exact single-closing-commit exception. |
| Repository identity/runtime: B `cli/ok`, `cli/overseer`, `cli/{bootstrap,v1,v1_io}.py` | Active UUID, physical root and runtime binding; conventional venv symlinks supported. | `tests/v1/test_isolation.py`, `test_context.py`, `test_integrity.py`. Extend the same boundary to every command, app request and lane; no neighboring runtime fallback. |
| Per-repository lanes: D/P `adapters/config.py`, `cli/commands/governance_sync.py`, `tools/workspace`, P bookends | `docs.lanes`, default lane, titles and workspace relay logic retained but disconnected; bounded context has one lane. | `tests/unit/test_k8_lanes.py`, `tests/fixtures/config-two-lane.yaml`, `tests/*/test_workspace*`, `test_lt_*`. FPR-1 preserves all lane settings; FPR-2 exposes explicit selection and one canonical lane collection without cross-repo ownership. |
| Git-only: B plus D `adapters/git_only` | Active bounded workflow; full governance adapter remains. Git-only must not require/import Muse or probe neighboring Muse stores. | `tests/unit/test_git_only.py`, `tests/integration/test_adapter_factory.py`, B isolation tests, M standalone Git install tests. Preserve offline operation and all relevant full-product features. |
| Muse-only: M `v1_revision.py`, `v1_muse_reader.py`; D `adapters/muse_only` compatibility | Native authority absent from active CLI; legacy adapter alone does not establish it. Depends on explicit separate pinned Muse venv/store identity. | M `tests/muse/test_handoffs.py`; D `test_muse_only.py`, `test_muse_working_dir.py`, `test_muse_sync*`. FPR-2 ports native reads/adoption and connects full commands to the selected authority; no Git requirement or fallback. |
| Muse with Git mirror: M `v1_mirror*`; D adapter for full-product governance | Native controlled workflow absent; old adapter/bridge retained. Depends on Muse authority and an explicitly owned isolated bare target. | M `tests/muse/test_mirror.py`, `test_reconciliation.py`; D `test_muse_git_mirror.py`, `test_upgrade_regime*`. Replace export side effects with explicit prepare/reconcile/verify/deliver operations; main export stays refused. |
| Reconciliation, retries, scoped credentials: M `v1_mirror_history.py`, `v1_git_credential.py` at tip | Absent in S. Full bundle/approved delta, exact parent/tree/trailer correspondence, scoped HTTPS helper and remote readback are implemented on M. | M `tests/muse/test_reconciliation.py`, `tests/v1/test_mirror_credentials.py` (39 repaired credential cases recorded). Port the repaired helper, including repeatable challenge metadata; no token storage or ambient helpers. |
| Init and migration: B `initialize`; D `cli/commands/init.py`, `config_gen.py`, `version_lock.py`; M `adopt` patterns | B preserves living docs but cannot parse full config. D supports migration/preserved footprint; M adoption is authority change, not a full legacy-config migration. | `tests/unit/test_init.py`, `test_init_migrate.py`, `tests/data_integrity/test_migrate_idempotency.py`, B commands, M adoption tests. FPR-1 joins these contracts through explicit normalization/dry-run/backup/apply; does not drop old settings. |
| Sync, status, footprint/integrity/drift: D command modules and `cli/{footprint,sync_classify,drift,version_lock}.py`; B binding | B refreshes runtime/launcher only. Full status sections, owned asset sync, hashes, preserved-origin handling and coverage remain disconnected. | `test_cli_init_sync_status.py`, `test_sync.py`, `test_k7_footprint.py`, `test_footprint_integrity*`, `test_lt_*`. FPR-1 unifies safety/config and full asset classification; FPR-3 completes status sections and full footprint. Sync never creates/replaces an existing NEXT. |
| Substrate, Muse sync and optional-feature diagnostics: D `tools/{substrate_health,muse_sync,optional_feature_tips,track_o}` | Retained status warnings, source/mirror synchronization checks, regime readiness and feature tips. Old bridge-sentinel assumptions are not proof of new mirror correspondence. | `test_substrate_health.py`, `test_substrate_status.py`, `test_muse_sync*`, `test_track_o*`, `test_lt_*`. FPR-2 connects authority/mirror diagnostics; FPR-3 restores status/readiness/tips against unified config and verified correspondence, with unknown/offline states explicit. |
| Governance-sync: D `cli/commands/governance_sync.py`, `tools/governance_hygiene/*` | Retained; old engine synthesizes HANDOVER NEXT and `--write` commits/pushes. Depends on lanes, authority adapters, living-doc preservation and explicit effects. | `test_governance_sync*`, `test_governance_idempotency.py`, `test_governance_freshness*`, `test_gsw_*`, `test_gs_paste*`. Restore hygiene/drift/realignment; detach NEXT regeneration. Local write/commit and remote push become separately explicit; `--print-next` uses canonical service. |
| Review / Check OK / escalation: D `cli/commands/{review,check_ok}.py`, `tools/{freeze_reviewer,check_ok,freeze_authorization}` | Engines, local/API provider interface, stamps, human fallback and side-check scaffolding retained. Depends on full config, reviewer labels, credentials only for explicit provider use. | `test_cli_review_freeze.py`, `test_cli_check_ok.py`, `test_review*`, `test_api_review*`, `test_freeze_review_cycle.py`. Restore through one CLI, preserve non-pass/independence semantics and offline local path; no mandated extra restoration review cycles. |
| Workspace/constellation: D `cli/commands/workspace.py`, `tools/workspace/*` | Retained manifest, relay freshness, doctor and strict/optional members. Depends on configured authorized member roots and lanes. | `tests/*/test_workspace*`, `test_cli_workspace.py`. Read explicit members with their own identity/config; never scan siblings, silently import a lane or mutate a member. Relay checks use canonical NEXT service. |
| Verification/checkpoints: D `cli/commands/verify_step.py`, `tools/checkpoints/*` | Retained consumer-owned scripts/manifests, tier selection and bounded execution. | `test_checkpoints*`, evidence/verification tests under `tests/*/test_p_*`. Restore dry-run and explicit execution with confined paths and captured context; no invented PASS. |
| Honesty, evidence and verdict ledger: D `cli/commands/{honesty_status,ledger}.py`, `tools/honesty/*`, `tools/verification_evidence_gate`, `tools/independent_second_reviewer`, `tools/adversarial_freeze` | Retained config modes, producer/session identity, role distinctions and ledger verification. Depends on cryptography where signed evidence is used. | `test_honesty*`, `test_p_*`, `test_isr_*`, `test_aff_*`. Preserve entries and chain verification, append only on explicit action. The user-facing verdict ledger is distinct from excluded infrastructure packet-chain prerequisites. |
| Routing, tiers and cost hints: D `cli/commands/route.py`, `tools/{model_routing,cost_awareness}`, `policy/*` | Retained read-only policy resolution and hints; not exposed. | `test_model_routing*`, `test_cost_awareness*`, tier-policy tests. Restore labels/validation and status hints without changing owner model selection or spending automatically. |
| Landing/closeout: D `cli/commands/{land_check,land_closeout,pr_land}.py`, `tools/{close_ritual,land_closeout}` | Retained verify/prepare probes, authorized wait-for-green merge and optional clean ff-only post-land sync. | `test_close_ritual*`, `test_land_closeout*`, `test_post_land_sync*`. Restore with explicit remote/merge effects, selected authority and NEXT freshness consequences; no auto-merge from hooks/governance. |
| Handover compaction: D `cli/commands/handover_compact.py`, `tools/handover_compact/compact.py` | Retained dated-entry archive/keep bounds and lane selection. | `tests/*/test_lt_*`. Restore dry-run/write, preserve archive, living content and canonical NEXT; replace embedded active prompts with links only during explicit migration. |
| Local app: D `cli/commands/app.py`, `tools/app/*` and static assets | Retained loopback UI, bearer/CSRF/origin checks, health/status/gates/docs/review/governance/honesty/ledger endpoints. Calls old handlers directly, bypassing B. | `tests/*/test_q1_app*`, `test_q2_ok_cli*`. FPR-3 shares bound CLI services, exposes canonical NEXT and selected lane, confines each request, preserves action controls and read-only endpoints. |
| Desktop: D `desktop/*`, `tools/desktop*`, `scripts/bundle-desktop-kit.sh` | Tauri shell and installer/checksum/signature tooling retained; spawns `cli/ok app`, now unavailable. Depends on Rust/Node/toolchains and bundled Python engine. | `tests/*/test_q3_desktop*`, `test_q3_release_desktop*`. Restore launch/health/lifecycle and resource bundle without environment runtime fallback; validate actual supported packaging, not only mocked launchers. |
| Hosted dashboard: D `cli/commands/hosted_dashboard.py`, `tools/hosted_dashboard/*` | Read-only multi-repository viewer retained; its UI is separate from M's hosted CI. Depends on explicit host/org/repo allowlists, viewer/upstream credential boundaries and cache. | `tests/*/test_hosted_dashboard*`. Restore read-only remote projections; a remote NEXT is historical/display data until local binding/freshness validates. No hosted local-action endpoints. |
| Skills/rules/templates: D/P `cursor/`, `.claude/skills/`, `templates/`, `policy/`, `cli/footprint.py`; B binding rules | Distributed skills and many rules remain; five active rules were narrowed. Templates may still embed former prompt/gate assumptions. | `test_skills_footprint.py`, `test_k7_footprint.py`, `test_lt_*`, `test_governance_gates*`. Restore useful guidance and dual skill footprint; make every print-next path invoke the service, remove ambient runtime discovery and automatic review chains. |
| User docs, landing site and examples: D `docs/landing`, `tools/landing`, docs/runbooks; M migration/bridge corrections | Full-product site/docs coexist with bounded README and stale examples. This is a truth-alignment task, not a redesign. | `tests/*/test_landing*`, template/footprint tests. FPR-3 align all active entry docs, examples, screenshots/text and download claims to actual CLI/modes; preserve archives and certification wording. |
| Source distribution, installation and upgrades: B source-install/rollback contract; D footprint/version lock and desktop packaging; M `tools/ci/*`, `.github/workflows/supported-v1.yml`, distribution tests | Local bounded source snapshot exists but is not a full-product package. M pins an optional rc5 recovery artifact and retains hosted results for older source. | M `test_muse_artifact.py`, `test_source_distribution.py`, `test_adoption.py`; B retained 43-check install/rollback record; D migration/footprint/desktop-release tests. FPR-3 produces reproducible local source bundle/manifest and truthful upgrade guide; FPR-4 verifies integrated fresh install, migrations and rollback. No registry prerequisite. |

### Every historical command's disposition

The exact `COMMANDS` set in S `cli/legacy_main.py` is covered here. All maintained
user outcomes are restored; only unsafe or superseded mechanisms change.

| Historical command | Target disposition / wave |
| --- | --- |
| `init` | FPR-1 unified safe init, `--migrate`, dry-run and preserved assets; three history modes completed in FPR-2. Existing living docs never overwritten by generic force. |
| `sync` | FPR-1 runtime/binding and owned footprint sync; FPR-3 full asset set. Preserve `--only`, diff, dry-run and explicit preservation controls; reject contradictory options before writes. |
| `status` | FPR-1 bound identity/runtime/NEXT plus normalized config; FPR-2 authority/lanes/mirror state; FPR-3 governance, footprint, gates, workspace, routing/cost sections. Keep read-only offline default; remote freshness is explicitly unknown until requested. |
| `review` | FPR-3 restore freeze path, local/API/human modes, dry-run/checklist and controlled stamps. |
| `check-ok` | FPR-3 restore scaffold plus review with existing path/topic/scope options. |
| `check-if-ok` | FPR-3 retain deprecated alias to `check-ok`, same behavior; no second implementation. |
| `governance-sync` | FPR-3 restore default dry-run, lane/all-lanes and explicit local updates. `--write` means local apply/commit; remote feature push requires additional `--push`. `--print-next` aliases canonical reader and remains incompatible with writing/all-lanes ambiguity. Document this intentional safety change. |
| `next` | FPR-1 canonical validated reader; FPR-2 explicit lane/all-lanes rendering. Retire HANDOVER scraping, retain manual fallback. |
| `workspace status` | FPR-3 constellation/relay status and `--strict-all`; FPR-2 establishes repository/lane ownership underneath it. |
| `workspace check-next` | FPR-3 relay freshness check with existing lane selection; validate canonical member NEXT, never manufacture one. |
| `workspace doctor` | FPR-3 diagnostics, including board/manifest identity conflicts. |
| `verify-step` | FPR-3 restore step/through-current/all, policy/manifest and dry-run. |
| `honesty-status` | FPR-3 restore hook/artifact/session/evidence gates and truthful verdicts. |
| `ledger append`, `ledger verify`, `ledger show` | FPR-3 restore all three subcommands; preserve JSON/stdin append and recent-entry display, chain checks and existing ledger bytes. |
| `route` | FPR-3 restore position/tier/gate policy resolution and `--validate`. |
| `app` | FPR-3 restore loopback UI on unified services; explicit browser open/bind/port. |
| `hosted-dashboard` | FPR-3 restore read-only viewer and explicit configured network sources; no local mutator reachability. |
| `upgrade-regime` | FPR-2 preserve `muse-only` → `muse+git-mirror` dry-run/apply ceremony and settings. Translate approved mirror setup into M's controlled plan. Old `--live-bridge` must refuse unsafe legacy export and give explicit `mirror deliver` instructions; `--yes` is not new remote authority. |
| `land-check` | FPR-3 restore verify-landed/prepare-PR checks, never merge. |
| `land-closeout` | FPR-3 restore post-merge read-only probe; remote PR enrichment opt-in, no doc/NEXT writes. |
| `pr-land` | FPR-3 preserve required authorization, PR/method/poll/timeout/dry-run and optional clean ff-only sync; never run during FPR-0–3 validation against real remotes. |
| `handover-compact` | FPR-3 restore lane/keep/dry-run/write without touching active canonical prompts. |

`workspace` and `ledger` rows expand their subcommands; they do not add names to
the 20-name historical set. Newer public commands retained are `next-write`,
`adopt`, and `mirror prepare|reconcile|verify|deliver`. `hook` is a restricted
lifecycle adapter entry, not an alternate CLI. `cli/overseer` remains a
compatibility spelling for the same `cli/ok` engine. Global JSON/quiet/verbose/
no-color/version behavior and argument placement are reconciled without allowing
duplicate binding flags or last-option-wins root changes.

## 5. One configuration and migration contract

Use one versioned normalized model and one loader. The target serialized schema
is **schema 3**, avoiding collision with B's schema 1 and M's schema 2. Retain the
full configuration's section names where possible:

| Target field group | Contract |
| --- | --- |
| `repo` | `name`, existing UUID `id`, physical checkout `root`, legacy `root_relative_docs`. UUID identifies this installation/checkout binding, not an inferred global identity or Muse object ID. |
| `runtime` | Physical installation root, source version, deterministic digest of all reachable owned executable modules/resources; ordinary venv interpreter symlinks remain valid. No shell/PATH/env fallback. |
| `context` | Default active lane/model for this checkout, preserved exactly when present; explicit selection may choose another declared lane, never another repository's lane. |
| `vcs` | Legacy `regime`, `canonical`, Git remote/main/mirror/feature-pattern settings and Muse staging/main/working-dir settings. `git-only` implies Git; both Muse regimes imply Muse. Muse has an additional explicit source/store/runtime binding from M. Mirror configuration is independent of authority selection. |
| `docs` | Legacy names, titles, coordination, standing decisions, default lane and complete lane map. Add `canonical_next: docs/NEXT.md`; each lane records this repository's UUID as owner and its own document paths. Existing docs-at-root layouts remain supported. |
| Maintained settings | Preserve `thresholds`, `freeze_contract`, `governance_gates`, `checkpoints`, `honesty`, `modules`, `extensions`, `model_routing`, `cost_awareness`, `session_bookends`, `workspace`, `hosted_dashboard`, `close_ritual` and referenced policy paths/values. Keep extension data and truthful unsupported-extension diagnostics. |

Do not reduce hosted-dashboard settings to the old `HostedDashboardSection`
projection: its parser accepts enumeration caps, MuseHub host/base and document
limits that the older wrapper omits. Preserve the full validated object. Module
flags and section enable flags must agree. An imported deprecated reviewer/model
label stays visible until explicitly mapped, rather than silently selecting a
different model. A normalized adapter view can feed retained engines; it must
come from this one model, not a second independent config load.

Supported inputs are legacy `overseer_config_version: 1`, B schema 1, M schema 2
(Git or Muse) and target schema 3. Read-only inspection can normalize in memory
and report migration requirements. A legacy config with no UUID/root/runtime may
be inspected but cannot execute mutating or authoritative NEXT operations before
explicit binding. Existing B/M bindings remain usable during a staged upgrade
through the compatible loader; a runtime digest mismatch still requires explicit
refresh. FPR-1 must preserve Muse settings even before FPR-2 activates Muse
operations; it must refuse unavailable authority operations rather than use Git.

Migration is `ok -C ROOT init --migrate --dry-run`, then explicit apply of the
same plan with expected config/asset digests and observed context. Authority
changes use `adopt`, not migration or sync. The implementation must:

1. Read source config with duplicate-key detection; classify its exact schema,
   inventory all keys, owned/preserved footprint entries, lane docs, policies,
   ledger, runtime and NEXT. Produce a complete before/after field map and path
   delta. Unknown fields are retained in the source backup and block apply until
   mapped; never drop them as an incidental loader default.
2. Preserve every existing UUID/root/runtime/lane/model/source selection. Assign
   a UUID only where none exists, during explicit initialization. Legacy
   `docs.default_lane` determines its existing default; where no lane existed,
   propose `product` for owner acceptance. Preserve all nondefault lanes and
   their names/titles. Shared document aliases are allowed only for the exact
   declared default pair; conflicting lane ownership/path aliases refuse.
3. Store byte-exact original config and touched owned assets in a digest-named
   local backup with a manifest; preflight every destination, mode and expected
   digest before the first replacement. Preserve user rules/skills and living
   documents by default, including all `origin:preserved` entries. Raw config
   backup preserves comments even if normalized YAML formatting changes.
4. Reuse B's confined no-follow I/O and M's compare-before-apply/adoption ordering.
   Validate captured root/config/runtime/selected revision after lock acquisition
   and immediately before each context-sensitive replacement. Write the new
   config last. Per-file atomicity is not a transaction: report partial progress,
   retain prior bytes and give an idempotent resume or explicit rollback path.
   No registry, generation server or packet protocol is needed.
5. Preserve existing canonical NEXT byte-for-byte on config/runtime-only
   migration. For a legacy HANDOVER-only prompt, offer exact extracted text as a
   draft, validate its task/context with the operator, and publish once through
   `next-write` with expected `absent`. Do not infer permission from an old fence.
   Archive/replace old active fence sections with canonical links only in the
   explicit migration plan; preserve the rest of the living documents. Multiple
   conflicting active prompts block automatic migration.
6. Reject contradictions before mutation: UUID/root/launcher mismatch; unexpected
   runtime origin; scalar/dict schema collision; regime/canonical disagreement;
   unknown/duplicate keys; unsafe path/alias; conflicting default lane/model;
   copied Muse store/runtime binding; unapproved external working directory;
   changed config/assets/revision; competing NEXT documents. No silent rebind,
   auto-untrack, history deletion, credential copying or settings reset.
7. Keep relocation separate from upgrade. A root/installation move requires an
   explicit reviewed rebind plan identifying old/new roots and expected UUID,
   backups and newly validated NEXT; a mere `sync` cannot authorize it. FPR does
   not require an automatic cross-machine identity bridge.

Legacy Muse `working_dir` may identify a linked checkout. Resolve it explicitly
against the named repository and source/store identity, never against an ambient
parent. If it differs from the governed physical root, require an explicit
pairing in the migration plan and prove the adapters cannot write elsewhere.
Do not erase it or silently move living docs to make migration pass.

### NEXT storage and lane compatibility

`docs/NEXT.md` is the sole canonical handoff document. Keep schema-1 single-lane
Git documents readable without rewriting them; preserve M's schema-2 explicit
authority/source-ID semantics. FPR-2 adds schema-3 multi-lane encoding in this
same file: one common repository/source binding, a strict frontmatter entry map
keyed by lane, and one uniquely delimited prompt body per lane. Each entry has
branch, base revision, model, action ID/kind and prompt digest. Validate exact
map/body correspondence, unique safe lane IDs and all prompt digests before
rendering. Reuse B's entry validation and rendering; do not build a second writer.

`next-write --lane L` updates one entry with whole-file expected-digest CAS;
explicit batch publication can refresh several owner-selected lanes atomically.
Unchanged entries retain their original revision and can become stale. A commit
in lane A does not silently certify lane B. Hooks show the explicitly selected
lane and a labelled status list for other configured lanes; absent selection in
a multi-lane session surfaces labelled validated entries and asks the operator
to choose before action. Missing/stale lanes remain visible as refusals, not
quietly skipped or replaced by the default lane. All lanes are owned by the
current UUID; workspace members validate independently.

Git retains the certified tracked-NEXT option and exact single-closing-commit
exception using one captured full commit ID and byte-exact committed NEXT.
Source/mirror distribution must exclude machine-bound config/launchers/NEXT by
projection, not by silently untracking source history. Do not copy M's blanket
ignore/adoption policy onto B's tracked-NEXT installation.

For Muse, use M's explicit checkout-local NEXT behavior: publish against the exact
current authoritative revision after the work commit; the next Muse commit makes
that handoff stale. Do not pretend a Git mirror commit refreshes it or invent a
Muse closing-commit exception. Existing tracked local-binding files are reported
and require an explicit preservation/untracking decision before Muse adoption;
the migration does not delete them. Configuration-only migration keeps them
unchanged. Runtime exclusions and distribution filters remain separate policies.

## 6. One CLI and automatic handoff

`cli/ok` stays the single supported launcher. Keep B's sanitized shell, isolated
Python bootstrap and installation-prefix validation, then call one command
dispatcher. The bootstrap itself must change; a new `cli/main.py` behind an
unchanged `from cli.v1 import main` would be a false restoration.

Every handler receives the same validated repository/config/runtime/revision/lane
context. Refuse duplicate global binding options and config paths outside the
canonical config. Preserve legacy test injection at the engine layer; it must
not bypass production context validation. Lazily load optional engines so a
Git-only read does not require Muse, provider credentials, desktop or hosted
packages. Expand the runtime manifest when commands become reachable; hashing
only B's original nine files would leave restored code outside its binding.

Automatic bookends are **read-only calls to that same NEXT service**. The start
adapter runs on session start, and the closeout adapter runs after the final local
handoff/closing commit. They output a validated paste-ready action or a bounded
refusal, never a guessed task. They must not run governance-sync, mutate docs,
rebase stale prompts or regenerate from HANDOVER/ROADMAP. Session input includes
explicit root/lane where available; reject foreign workspace roots, multiple
ambiguous roots, copied hooks, malformed/oversized input and stale context.

P provides committed native Cursor `sessionStart`/`stop` event evidence. Its
Claude Code footprint contains skills, not proven native session lifecycle
hooks; this checkout's AGENTS instructions likewise do not establish a Codex
native event API. Therefore:

- FPR-1 must restore Cursor automatic bookends using B's bound execution and
  P's useful presentation, with fixture event checks. Install only on explicitly
  selected disposable repositories until real use is authorized.
- Preserve Claude/Codex skill/instruction integrations and require their session
  entry/close instructions to invoke bound `ok next`. An instruction-triggered
  display must be labelled as such; it is not evidence of native hook delivery.
- Any chat tool advertised as supporting **automatic** bookends must have both
  event adapters demonstrated in FPR-4 on a named supported client version.
  If the owner's required tool lacks a usable lifecycle interface, that is an
  explicit unresolved support choice/release blocker, never a silent manual-only
  substitute for the promised outcome. No host events or APIs are invented from
  memory during this offline analysis.

Manual `ok -C ROOT next [--lane L]` remains available in every mode, including
hosts without lifecycle support. Hook failure may let the host session continue,
but cannot output an actionable fallback prompt or claim the bookend succeeded.
The existing read recheck and writer-after-lock/before-replace repairs apply to
both manual and automatic paths and later to Muse revision captures.

Governance engines may propose work in a report, but only explicitly accepted
text passed to `next-write` becomes the pending action. `governance-sync --write`
applies local summary changes; separate `--push` requests remote transport. No
hook, app refresh, review result or status command acquires implicit push/merge
authority. Retained review policies remain configurable product capabilities;
they do not create recurring independent review gates for this restoration.

## 7. Muse authority and controlled mirror design

Each repository independently selects Git or Muse. Presence of `.muse`, a sibling
checkout, an old bridge sentinel or a configured Git remote cannot select an
authority. Git-only never launches Muse. Muse-only never needs Git. In mixed
checkouts, Muse branch/head/source ID determine NEXT freshness and governance;
Git state is reported only as mirror state. Use M's nearest-VCS-boundary discovery,
separate pinned venv reader, bounded output/time, store/source identity checks and
read-only stage behavior. Apply B's captured revision and final output rechecks
to this backend too.

Port the tip M credential fix and reconciliation code together with their tests.
Retain these concrete invariants from `v1_mirror*`:

- An explicit digest-bound plan names source ID/main revision, physical target,
  destination repository/distribution branch/base, expected target/remote heads,
  executable-mode policy and, when needed, an exact legacy history delta.
- Prepare/reconcile/verify are offline. Only a new dedicated bare repository or
  the engine's exact owned target is eligible; refuse overlap with source/store/
  runtime, existing worktrees, inherited hooks/config/alternates and foreign refs.
  Do not native-export into the active repository or directly into Git main.
- Projection verifies native objects, snapshot/working-byte correspondence,
  explicit executable modes, staged/dirty-source restrictions and path bounds.
  Exclude secrets and machine-local binding files while retaining required CI
  dotfiles, product assets and templates. The integrated config/NEXT paths must
  be included in the exclusion policy without deleting source data.
- Reconcile accepts the reviewed bounded complete bundle, exact approved delta,
  base and mirror heads; validates ancestry/tree/modes and records both parents
  on the initial reconciliation. Later snapshots use the intended single-parent
  continuation. A changed base/tree is not permission for an automatic merge.
- Preserve target CAS, one local correspondence record and source/plan trailers.
  Recover interruption by verifying exact tree/parents/trailers, not by trusting
  a previous success flag. Re-observe remote heads on delivery/retry; resolve a
  lost push response by readback and reuse only the exact matching PR. Refuse
  drift, ambiguous PRs or unverified authority. Report partial outcomes honestly.
- Delivery alone may use explicitly approved network transport. Retain M's
  ephemeral GitHub HTTPS credential helper scoped to one repository path,
  reset inherited helpers, disable redirects, ignore store/erase and accept only
  the repaired bounded challenge metadata. Tokens stay out of argv, URLs,
  configs, evidence, correspondence records and diagnostics.

M's real transport is explicitly limited to public staging MuseHub JSON refs and
GitHub HTTPS, with source branch `main`; its Git mirror implementation is SHA-1
specific and has bounded bundle/projection sizes. These are known limits, not a
generic production/private provider claim. Preserve them until an owner selects
and authorizes a broader destination/provider contract. Full configuration may
retain other branch/provider settings, but incompatible delivery must refuse
with a precise limitation instead of relabelling the repository or exporting to
main. No live transport is needed to implement or fixture-validate this design.

`upgrade-regime` preserves the outcome of adding optional Git distribution while
Muse stays authoritative. It reuses migration/owned-footprint work and produces
the controlled mirror plan; it does not revive the old live-export shell route.

## 8. Exactly three implementation waves

These are implementation boundaries with focused author checks, not review-only
handoffs. No evidence establishes a need for additional implementation waves or
independent reviews between them. Current authorization stops after FPR-0; an
accepted FPR-1 prompt authorizes only its stated local scope. Later work continues
under accepted wave prompts, without a separate architecture/review stage.

### FPR-1 — unified foundation and automatic NEXT

**Exact inputs:** this plan/closing commit; B/S `cli/{ok,overseer,bootstrap,main,
v1,v1_io,digest}.py` as applicable; D `cli/{legacy_main,context,args,config_gen,
paths,docs_paths,footprint,footprint_writes,sync_classify,version_lock}.py`,
`adapters/config.py`, init/sync/status engines; P `cursor/hooks/*` presentation;
M adoption/ignore logic as reviewed patterns only, not a wholesale runtime import.
Pinned config fixtures, all B tests including `test_context.py`, D migration/
footprint/lane tests and P bookend tests are the acceptance inputs.

**Outputs:** one dispatcher reached by both shims/bootstrap; shared validated
context and normalized schema-3 loader; explicit legacy/bounded migration with
dry-run/digest checks/backups; preserved lanes/settings; safe init/sync/status;
unchanged single-lane NEXT compatibility and repaired CAS; automatic canonical
Cursor start/end adapters plus truthful other-host instructions; runtime manifest
covering newly reachable code; updated focused tests and migration/CLI notes.
Do not expose unfinished commands as working: the complete registry lands by
FPR-3; no public path invokes `legacy_main` meanwhile.

**Acceptance:** exercise actual `cli/ok`, alias and bound launcher in disposable
Git repositories A/B with hostile cwd/PATH/Python/Git environment; duplicate flags,
copied launchers/hooks, physical alias/path escape and identity/runtime mismatch
refuse. Preserve UUID, docs, existing NEXT, full configuration including optional
fields, lane map and custom assets across both migration inputs and retry. Test
expected-config drift and partial replacement recovery. Rerun B's meaningful
binding/CAS/unborn/closing-commit/R1/R2 tests against the integrated dispatcher;
add migration contract cases only where absent. Start and end read the same NEXT,
do not write, and refuse a stale or foreign prompt. Git-only core does not import
Muse or require provider credentials. Unsupported authority remains explicit.

**Local commit boundary:** one coherent feature commit `feat: unify product CLI,
configuration and canonical bookends`, including focused evidence, paired
summaries and its canonical successor. If a mechanical defect forces an extra
repair commit, keep it in this wave with focused evidence, not a new review action.
Refresh this installation's runtime binding explicitly when implementation changes
require it; preserve identity/NEXT and publish the successor through the writer.
No consumers, providers/network, mirror, main merge, release or deployment.

### FPR-2 — authority, mirrors and repository lanes

**Exact inputs:** accepted FPR-1 commit; M `cli/v1_revision.py`, `v1_muse_reader.py`,
`v1_policy.py`, `v1_mirror.py`, `v1_mirror_reader.py`, `v1_mirror_history.py`,
`v1_git_credential.py`, authority/adopt portions of `v1.py`, controlled bridge
refusal scripts/templates; M `tests/muse/*`, `tests/v1/test_adoption.py`,
`test_mirror_credentials.py`; D lane config/adapters/upgrade-regime ceremony and
workspace ownership logic. Reuse D's Muse branch compatibility, not P's regression.

**Outputs:** all three history modes through one CLI/config; explicit authority
adopt/rollback; isolated prepare/reconcile/verify/deliver service; scoped helper;
unified upgrade-regime; canonical multi-lane NEXT collection and ownership;
repository-independent selection and status; explicit limits for native runtime,
transport, tracked local bindings and freshness; ported tests with source map.

**Acceptance:** two or more disposable repositories with different authorities,
UUIDs and lanes; Muse-only without Git and Git-only without Muse; mixed checkout
uses selected authority; native linked worktree identity and dirty/shared-stage
reads remain correct and side-effect free. Repeat R1/R2-equivalent captured-state
checks for Muse, entry CAS/stale lane and whole-file concurrent lane writes.
Exercise mirror target overlap/ownership, mode/secret exclusion, complete bundle
delta/parent checks, base drift, interrupted record/push/PR retries and scoped
challenge credentials with fake transports/tokens only. Git tracked-NEXT migration
is not silently subjected to M's ignore policy. Old unsafe bridge flags refuse.

**Local commit boundary:** one coherent feature commit `feat: integrate Muse
authority, controlled mirrors and repository lanes`, tests/evidence/paired
summaries/successor included. Runtime/Muse source pins are recorded; no live export,
delivery, provider access or independent review handoff occurs.

### FPR-3 — remaining product commands and surfaces

**Exact inputs:** accepted FPR-2 commit; retained D/P command/engine inventory in
section 4 (prefer current identical blobs); app/desktop/hosted source and assets;
`cursor/`, policies, templates, docs and landing site; M artifact/source verifier,
CI driver/workflow and distribution tests; B install/rollback requirements.

**Outputs:** every historical command/subcommand and maintained outcome reachable
through `cli/ok`; full status/hygiene/review/Check OK/workspace/verification/honesty/
ledger/routing/cost/landing/compaction; loopback app and desktop sharing the bound
services; read-only hosted dashboard; truthful rules/skills/templates/site/runbooks;
reproducible local source package with hash/mode manifest and local upgrade/
rollback instructions. Legacy main is historical only. No product documentation
directs users to it. Separate local, remote and release actions in CLI help/UI.

**Acceptance:** concrete registry/help/options coverage for all 20 historical
names plus new commands; exercise engines through the real dispatcher/app service,
not only direct legacy imports. Relevant preserved algorithm/security tests pass
or have explicit replacement cases for changed contracts. Assert all handoff
surfaces use canonical NEXT and all mutation paths share identity/runtime checks.
Check app auth/CSRF/origin/path controls, hosted write refusal/allowlists, desktop
launcher/bundle identity, full settings preservation and source artifact inclusion/
exclusion. Audit examples/download claims and ensure dependency declarations
include the full feature needs. Produce a test-disposition map for every original
test family and the 104 baseline failures before combined validation.

**Local commit boundary:** one coherent feature commit `feat: restore maintained
product commands and application surfaces`, including focused evidence, paired
summaries and FPR-4 successor. Build artifacts may be prepared locally during the
authorized wave; no publish/sign/tag/deploy or automatic installer/network fetch.

## 9. FPR-4 — one combined validation matrix

Run after all three waves on one recorded integrated source/digest. Use disposable
fixtures under a nonrepository parent; keep every existing rollback fixture and
pilot untouched. Focused wave checks prevent local defects; FPR-4 proves their
composition. Record exact source/runtime/dependency versions, commands, exit
codes, selected test map and failures. A missing dependency, socket permission
or toolchain is unresolved evidence, never a green skip or silent scope reduction.

| Matrix group | Cases and required evidence |
| --- | --- |
| Three modes × repository identity | Git-only, Muse-only and Muse+Git mirror, each initialized and used with an independently selected UUID/root/runtime. At least two repositories active in one session, distinct defaults and overlapping lane names; worktrees and nested boundaries included. Git-only runs without Muse installed; Muse-only runs without Git initialization. |
| Lanes / workspace | Product and another lane per fixture; explicit selection, missing/ambiguous/stale lane, ownership collision, docs-at-root and nested paths; workspace required/optional member behavior. No cross-root mutations or silent default substitution. |
| Automatic / manual NEXT | Start and end on each advertised automatic host/version, manual fallback on all hosts, exact prompt/digest equality, refusal on foreign/malformed/stale context, no governance regeneration. Git unborn/exact closing commit and Muse exact-revision freshness; schema 1/2 compatibility and schema-3 lane collection; concurrent CAS/context changes. |
| Full workflow parity | Actual CLI registry, status/sync/governance, review/Check OK, checkpoints/evidence/ledger/routing, landing/compaction and app/desktop/hosted surfaces. Exercise enabled and disabled module settings, local/API fake provider errors and human fallback. No command may pass only through `legacy_main` or hidden direct imports. |
| Isolation and effects | Wrong cwd/root/UUID/runtime/authority, copied launcher/hook/config, unsafe paths, unexpected env, hostile arguments, wrong lane, app/desktop target mismatch, hosted write routes and credential exposure. All read-only commands/automatic bookends remain read-only. Remote operations require the explicit operation/authorization. |
| Legacy migrations | Full legacy fixture with every maintained section, two lanes, custom policies/docs/skills/rules, ledger and preserved footprint; missing UUID; HANDOVER-only prompt; contradictory inputs. Before/after byte and semantic maps, explicit prompt acceptance, idempotency/partial-failure recovery and no settings loss. No real consumer migration is inferred. |
| Bounded migrations | B schema 1 tracked Git NEXT and M schema 2 Git/Muse checkout-local NEXT; source/runtime update, authority adopt and restore. Preserve UUID/root/lane/docs/NEXT/config extras; tracked-binding conflicts refuse until explicitly resolved. |
| Mirror / reconciliation / credentials | Offline real native objects and isolated Git target; fresh mirror and approved divergent legacy bundle; tree/modes/exclusions/dotfiles/parents/delta; interrupted prepare/record/push/PR and changed base/source/remote. Fake transport asserts readback and scoped credential protocol. Live provider success is a separate fact requiring authorization if claimed. |
| Fresh install / source distribution | Build and unpack the complete source artifact at a new fixture installation root; verify manifest, executable modes, product assets/templates/CI dotfiles, absence of secrets/runtime-local bindings and no neighboring-runtime fallback. Run the actual advertised entry points, app and desktop launch. Do not replace the bounded source-release directory. |
| Upgrade / rollback | Full legacy → integrated, B bounded → integrated, and integrated current → preserved compatible previous → current at a fixed root. Quiescent commands, explicit refresh and backed-up schema restoration; compare UUID/docs/lanes/NEXT/settings. Old runtime must refuse unknown schema until explicit rollback restores its matching config. Existing R1/R2-defective previous build is never relabelled safe. |
| Environment / packaging | Minimum intended source matrix: POSIX Python 3.11 and 3.14 Git core, Python 3.14 with pinned Muse rc5; full Python dependencies including cryptography where required. Validate local app sockets and desktop/toolchain build on each platform actually claimed. Windows/native signing and new hosted runs require explicit scope/authorization; old cross-platform copy is not proof. |
| One noncritical integrated pilot | A separately selected new disposable project, not the completed bounded pilot: initialize/migrate, select authority/lanes, automatic start, status/governance local update, Check OK/review, one verification and ledger record, app/desktop readback, mirror preparation where selected, explicit NEXT and automatic end/manual readback. Local closing commit and rollback/readback evidence. Simulate remote landing/delivery unless separately authorized; report that limit. |

**Reuse, do not recertify by repetition:** preserve the original independent
FINDINGS verdict, 20 deterministic B repair cases, 173 supported passes, 43
installation/rollback checks, completed bounded pilot and certification. They
justify choosing B and define regressions, but do not certify changed code.
Rerun the B behaviors reached by the new dispatcher/config/revision/writer, not
the completed bounded certification process or its old pilot.

M records final local Git 3.11/3.14 **156 passes** and combined Muse **289 passes**
after the scoped-helper fix (`M:docs/validation/V1-RECOVERY.md`, credential repair
section). Its recorded hosted jobs passed **117 Git / 225 combined** for earlier
source; the reconciliation section explicitly binds the prior hosted pass to
`2d689a8398002ce667743ac7fefd12291b8973bf`. These are retained reports inspected
offline, not freshly verified remote runs and not a hosted pass for M's tip or
the integrated product. Reuse artifact pins/verifiers and relevant tests, not
their old overall verdicts or stale CI documentation wording.

The **1,391 passed / 104 failed** historical baseline remains unchanged by FPR-0:
68 socket denials, 16 missing-cryptography cases, nine path/fixture failures and
11 other failures. FPR-3 maps each to restored requirement, changed contract or
excluded mechanism. FPR-4 reruns all restored/reachable requirements and relevant
cross-cutting tests once as a combined selection. Fix real product/fixture
failures; add explicit successor tests for changed contracts. Keep obsolete
tests archived with reasons rather than hiding required failures via testpaths,
skips or xfails. Repeat only failures/affected checks after repairs, expanding
again only when changed shared code invalidates earlier combined evidence.

## 10. FPR-5 — single independent final boundary

After the integrated build and combined matrix, hand one fixed source/digest,
source-selection map, complete capability/command inventory, migration report,
test-disposition map, failures/limits and pilot/install/rollback evidence to one
independent final reviewer. The reviewer assesses architecture, implementation,
security boundaries and completeness in one review. Independence must be real;
the implementation author cannot certify their own final review as independent.

If defects are found, preserve that verdict, perform bounded repairs with
failing-before/passing-after or equivalent concrete evidence, and rerun only
affected integrated checks. Then perform **one final adjudication** of the
complete evidence, followed by **one owner release decision**. An unresolved
finding blocks release; it does not automatically start architecture/adversarial/
freeze review cycles for each wave. If repairs expand the promised architecture
or scope, return that specific decision to the owner instead of silently adding
another review program.

No irreversible operation is necessary inside the three local waves. Scoped
credentials, local migration and remote delivery are security-sensitive, but
their implementations can be developed and tested with fixtures before this
single review. Actual remote delivery/main merge/signing/publication/deployment
remain separate explicitly authorized operations, not hidden wave acceptance
steps. FPR-5 does not itself grant release permission.

## 11. Risk register and unresolved owner choices

| Real risk or unknown | Resolution / decision boundary |
| --- | --- |
| Three config/CLI contracts; old handlers bypass binding or reload incomplete config | FPR-1 shared normalized context; FPR-3 route every handler/app request through it. Mandatory all-section migration and real-entrypoint tests. |
| M would regress B reader/writer concurrency and tracked-NEXT behavior | Keep B's captured context, exact closing revision and final rechecks; port Muse behind it, separate projection exclusions from local tracking. Preserve R1/R2 regression evidence. |
| Legacy governance/skills/workspace/app can create or display a competing prompt | Remove active regen/scraping calls, preserve draft/history outcomes, assert canonical service use across all entry points. |
| Multi-lane updates race or imply freshness across unrelated work | One file CAS, explicit lane ownership/entry revision, no automatic refresh of other lanes; test stale entries and batch publication. |
| Optional runtime/artifact and platform prerequisites may be unavailable locally | M pins Muse rc5 and its recovery source/artifact, but FPR-0 did not inspect external fixture directories or fetch anything. Later record availability; missing prerequisites block the associated claim, not all offline work. |
| Historic green subsets conceal failures in restored engines/dependencies/UI | Full test-disposition map and combined required-feature selection; actual app sockets/desktop build, not only unit mocks; no skip-based completion. |
| Partial config/asset update or rollback with an incompatible schema | Digest plan/backup, preflight, config-last writes, explicit matching-config rollback and resume evidence. No transactional guarantee beyond what is tested. |
| Delivery restrictions are narrower than full legacy settings | Keep settings, refuse unsupported actual delivery. Owner must choose any broader private/production provider, non-main source branch or SHA-256 Git requirement before it becomes a release promise. |
| Preserved local refs do not establish remote freshness, delivery success, native host compatibility or sustained/multi-user use | State each as unverified; do not contact providers or extrapolate from old records. Validate only when selected and authorized. |

The unresolved owner choices are limited to the following; none is a reason to
reopen the base/config architecture or to perform implementation during FPR-0:

1. **Automatic host support:** which named Cursor, Claude Code and/or Codex client
   versions must carry a native automatic start/end guarantee. Proposed minimum
   is the preserved Cursor event contract; retain other skills/instructions.
   A requested additional automatic host becomes a completion requirement, not
   an unannounced manual-only downgrade. Select before host acceptance in FPR-4.
2. **Remote Muse scope:** retain the proven public staging/GitHub HTTPS/main-source
   transport, or explicitly require private/production MuseHub, additional hosts,
   source branches or Git object formats. The default plan restores the preserved
   transport; expanded trust/credential contracts need a concrete owner choice.
3. **Release/platform and distribution claim:** source installation plus local
   app/desktop/hosted functionality is required; choose native installer target
   platforms, signing/notarization, any new hosted CI/provider demonstration and
   public destination/version before promising their release availability.
   Prepare reusable local source distribution regardless; no OCI mechanism is
   required. No remote execution/publication is authorized now.
4. **Integrated pilot and reviewer:** select/authorize one noncritical disposable
   project and host/authority combination for FPR-4, and appoint an independent
   FPR-5 reviewer. Default pilot proposal is a newly created local project with
   fake remote transports, preserving the prior completed pilot. Broader consumer
   access is a separate explicit decision.

Individual legacy installations may need explicit conflict resolutions (for
example a tracked local NEXT before Muse adoption or a differing `working_dir`).
Those are migration-plan choices presented with exact before/after evidence,
not authority to infer their answers in this repository. Existing feature policy
values remain untouched until then.

### Definition of complete

The complete integrated build must deliver every maintained outcome and command
in section 4 through the one supported CLI and its real app surfaces, in the
declared supported modes, with automatic bookends on every advertised automatic
host and manual NEXT everywhere. Configuration/migrations retain identity, root,
runtime, authority, all lanes/settings, living docs and canonical NEXT. Isolation,
controlled mirrors/credentials, source install/update/rollback and the full-flow
pilot must have combined evidence. Documentation and defaults must describe those
actual behaviors. Every original test family/failure has a truthful disposition;
no required restored capability is excluded merely to obtain a passing subset.

The independent final review, bounded repairs if any, final adjudication and
owner release decision are required before release readiness. A missing command,
hidden `legacy_main` path, manual-only substitute for a promised automatic host,
mock-only app claim or unresolved required matrix cell prevents that claim.

Only these mechanisms are deliberately not restored: OCI registries/receipts/
generation protocols, native/Mach GSR, UID sole-writer storage, historical identity
bridges and infrastructure packet chains. Preserve their user outcomes through
ordinary bound installations, confined atomic writes/CAS, isolated targets,
explicit migration/backup, deterministic source hashes, honest evidence and
operator-controlled release. Malicious same-UID/root protection is not claimed.
No evidence found a unique maintained user command that requires those mechanisms;
if later evidence does, preserve the outcome and present the specific owner
decision rather than silently omitting the capability or restoring the machinery.

## 12. FPR-0 closeout

Only this decision, paired ROADMAP/HANDOVER summaries and canonical NEXT change.
No source, test, configuration, hook, template or release-artifact modification
is part of FPR-0. Recheck source refs/identity and documentation consistency, then
publish exactly one FPR-1 prompt through the current bound `next-write`, using
the current context and opening NEXT digest recorded above. Make one local
documentation-only closing commit and validate the actual on-disk NEXT after it.
The prompt remains pending until separately accepted by the owner.
