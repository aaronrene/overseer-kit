---
schema: 1
repo_id: 6988dc4a-5f22-454b-9d68-ac5905b383bf
repo_root: /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014
branch: feat/overseer-v1-recovery-20261014
base_head: 3ed3b7d406e4e68186303481b2d32b87abb1d7d3
lane: product
model: GPT-6 Astra
action_id: OVERSEER-FULL-PRODUCT-RESTORATION-ANALYSIS-1
action_kind: plan
prompt_sha256: 9eaa0a190b8611d1862d05e0b0302cf2ff6f24726b89077905dd10430eea07bb
---
Reasoning: Max
Role: Principal product architect and repository historian

Perform FPR-0: a read-only, evidence-based reconciliation of the complete
Overseer Kit before any restoration implementation. The goal is one precise
integration plan that restores the maintained product features without losing
the certified repository/NEXT safety work and without creating another long
sequence of review cycles.

Start by verifying physical cwd, Git top-level, branch, full HEAD, configured
name, repository UUID and clean working-tree state. The canonical NEXT must
validate as the single closing documentation commit whose predecessor is
`3ed3b7d406e4e68186303481b2d32b87abb1d7d3`. Stop on mismatch, unexpected dirt,
or moved source refs. Read AGENTS.md, docs/ROADMAP.md,
docs/OVERSEER-HANDOVER.md, docs/NEXT.md,
docs/decisions/V1-SCOPE-RESET.md and
docs/validation/V1-CERTIFICATION.md before analysis.

Inspect committed Git objects only for these preserved lines:

- Full product, automatic session bookends and repository-lane work:
  `feat/overseer-context-isolation` at
  `e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`.
- Newer optional Muse revision authority, controlled mirror, reconciliation,
  hosted validation and scoped credential work:
  `feat/overseer-v1-recovery` at
  `32254cd939885d9d6f40634997ea5b9c37ea776c`.
- Certified repository-bound runtime, canonical NEXT and concurrency repairs:
  `feat/overseer-v1-recovery-20261014` at the verified current HEAD, with the
  repaired implementation at
  `348e0f323a3b17cd5022a1bfd56fa09a6831c51f`.
- Reconciled main baseline:
  `d47291d5d9030de5ebef713da95efa978c4d8c6e`.

Do not enter, modify or execute commands in the worktrees attached to the first
two branches. Preserve every existing worktree, ref, Muse history, recovery
snapshot, rollback fixture, pilot and the local bounded source-release directory.
Do not merge or cherry-pick during FPR-0.

Create `docs/decisions/FULL-PRODUCT-RESTORATION-PLAN.md` containing:

1. A short account of how the active product was narrowed, distinguishing code
   that was deleted, moved, disconnected, superseded or added on another branch.
2. A complete user-visible capability inventory. For each capability, record
   its best committed source, present state, dependencies, preserved tests and
   required restoration work. Include automatic start/end NEXT display; manual
   NEXT fallback; per-repository identity and lanes; Git-only, Muse-only and
   Muse-with-Git-mirror modes; isolated mirror/reconciliation and scoped
   credentials; initialization, migration, sync and status; governance-sync;
   review and Check OK; workspace; verification/honesty/ledger; routing; landing
   helpers; handover compaction; local app, desktop and hosted dashboard; skills,
   rules, templates, documentation, source distribution and upgrades. Inventory
   the full historical command list in `cli/legacy_main.py` and state the intended
   disposition of every command.
3. An evidence-backed choice of integration base. Do not select a branch merely
   because it is newest. Explain how the full product, October Muse work and
   bounded safety changes will be combined without a blind merge, a wholesale
   revert or a rewrite of already working code.
4. One target configuration and migration design supporting both the legacy full
   configuration and the bounded repository-bound configuration. Preserve UUID,
   physical root, runtime binding, lane ownership, selected revision authority,
   living documents and canonical NEXT. Define explicit refusal behavior for
   contradictions; do not silently rebind or discard settings.
5. One target CLI and automatic-handoff design. There must be one supported
   `cli/ok`, not a public full CLI hidden behind `legacy_main.py`. Supported chat
   tools must surface validated NEXT at session start and end; manual `ok next`
   remains the fallback. Hooks must read the same canonical NEXT and must not
   regenerate a competing prompt from HANDOVER or ROADMAP.
6. One target Muse design: each repository independently selects Git or Muse as
   authority; Muse-to-Git mirroring remains isolated and operator-controlled;
   direct unsafe main export stays refused; reconciliation, retry behavior and
   scoped credentials use the newest preserved implementation where sound.
7. A minimal execution roadmap with exactly three implementation waves unless
   evidence proves a different grouping materially safer:
   - FPR-1: unified CLI/config/migration, repository safety and automatic NEXT.
   - FPR-2: Muse authority, mirror/reconciliation and per-repository lanes.
   - FPR-3: remaining maintained product commands, app surfaces, templates and
     truthful user documentation.
   Give each wave exact inputs, outputs, acceptance checks and local commit
   boundaries. Avoid review-only handoffs between waves.
8. A combined FPR-4 validation matrix covering all three history modes, multiple
   repositories and lanes, automatic/manual NEXT, cross-repository isolation,
   legacy and bounded migrations, installation, upgrade/rollback and one
   noncritical end-to-end pilot. Reuse valid evidence and tests; rerun only what
   the integrated product requires.
9. A single FPR-5 independent final review boundary after the complete integrated
   build and combined validation. Use one review, bounded repair evidence if it
   finds defects, one final adjudication and one owner release decision. Do not
   schedule repeated architecture, adversarial, freeze or independent reviews for
   each implementation wave unless a specific irreversible/security boundary is
   proven and documented.
10. A risk register limited to real integration risks, unresolved owner choices
    and facts that cannot be established from preserved local evidence. Include a
    clear definition of "complete" that prevents another reduced subset from
    being presented as the full product.

The plan must treat preserved working code as the default source and explain any
decision not to restore a user-visible capability. OCI registries, native/Mach
GSR, UID sole-writer storage, historical identity bridges and packet chains are
not required mechanisms. Preserve any unique user outcome they provided through
the simpler integrated design; do not restore those mechanisms without an
explicit owner decision.

This action is analysis and documentation only. Do not edit product source,
tests, configuration, hooks, templates or release artifacts. Do not run the
completed bounded review, supported/historical suites, installation/rollback
exercise or pilot. Do not access consumers, providers or network; do not push,
mirror, merge, tag, publish, release or deploy.

After the plan is internally consistent, update ROADMAP and HANDOVER together
only where the evidence requires refinement. Publish exactly one canonical FPR-1
implementation prompt through this installation's bound `next-write`, using the
then-current context and expected prior NEXT digest. Make one local
documentation-only closing commit containing the plan, paired summaries and
canonical NEXT. Local implementation remains unauthorized until that prompt is
separately accepted by the owner.

Return in chat: the chosen integration base, the three implementation waves,
the combined validation and single-review boundary, all unresolved owner choices,
the local commit ID, and the validated paste-ready FPR-1 prompt. Do not call the
product restored or release-ready during FPR-0.
