# Overseer Kit

Overseer Kit helps people and AI assistants carry development work across sessions:
keep a roadmap, hand over the next task, review changes, verify completed work and
keep each project's instructions tied to the right repository. It includes reusable
policies, templates, assistant rules and skills, a command-line tool, a local browser
app and a desktop launcher. Git works on its own; native Muse support is optional.

## What the kit includes

| Capability | What it does |
| --- | --- |
| Planning and handover | Keeps ROADMAP and HANDOVER summaries together, with one canonical NEXT file containing the saved task and recommended model for each declared work lane. |
| Project identity and continuity | Checks the physical project, repository ID, branch, revision, lane and prompt digest before displaying a task. Rejects missing, stale or mismatched context. |
| Policies and model guidance | Supplies configurable decision tiers, review and test policies, model labels, routing and cost hints. The owner selects the actual model; routing does not dispatch one. |
| Review and verification | Provides freeze review, Check OK, local/API/human review modes, configured verification steps and evidence/readiness checks. Mechanical checks and independent review remain distinct. |
| Evidence records | Records and verifies an evidence ledger with hash-chain, role and signature checks. |
| Multiple projects and lanes | Shows explicitly configured workspace members and their lane status, missing prerequisites and stale prompts without silently switching projects. |
| Git and optional Muse | Supports Git-only, Muse-only and Muse with controlled Git mirroring, plus explicit authority changes and pull-request landing checks. Remote delivery and merging are separate authorized actions. |
| Installation and maintenance | Provides source packaging, initialization, template/policy updates, migration that preserves owner content, backups and guarded rollback. |
| App and assistant interfaces | Uses one `cli/ok` service for the CLI, local browser app and desktop launcher. Includes assistant rules/skills and opt-in Cursor event adapters. The hosted dashboard is a separate read-only surface. |

## Everyday workflow

1. Select the project and lane; read its bound NEXT prompt and saved model.
2. Work on the approved task, using the configured review and verification steps.
3. Keep ROADMAP and HANDOVER summaries current and record the relevant evidence.
4. Explicitly publish the actual next task with `next-write`, or a completion stop
   when nothing remains, then read the validated prompt again after closeout.

`docs/NEXT.md` is the single handoff authority. HANDOVER and ROADMAP are paired
summaries, not alternative prompt sources. Only explicit `next-write` publishes
accepted text with the expected whole-file digest and current context. Hooks and
app refresh never generate tasks. A displayed prompt does not execute work or
enforce an assistant vendor's tool permissions.

## Local use

Use this installation's conventional `.venv`, with the pinned requirements in
`requirements-v1.txt` (and `requirements-v1-dev.txt` for tests). Source runtime
bindings include reachable engines and assets. No neighboring installation,
ambient Python path or native identity bridge supplies a fallback.

```sh
./cli/ok -C /absolute/project status
./cli/ok -C /absolute/project next --lane product
./cli/ok -C /absolute/project governance-sync --dry-run
./cli/ok -C /absolute/project check-ok --topic example --dry-run
./cli/ok -C /absolute/project app --bind 127.0.0.1 --port 8765
```

These examples assume an initialized project. For manual session entry and
closeout, use the selected project's bound reader:

```sh
/absolute/project/.overseer/bin/ok -C /absolute/project next --lane product
```

The browser's **Next / Handover** NEXT control uses the same validated reader.
See [manual prompt display](docs/PRINT-NEXT.md) for the complete workflow.
Initialization uses `./cli/ok -C /absolute/project init --vcs git`; installation
into existing projects remains on hold pending a separately selected target and
installation scope.

## Commands and documentation

The maintained commands include init, sync, status, next, next-write, review,
Check OK (`check-if-ok` is an alias), governance-sync, workspace status/check-next/
doctor, verify-step, honesty-status, ledger append/verify/show, route, app,
hosted-dashboard, adopt, mirror prepare/reconcile/verify/deliver, upgrade-regime,
land-check, land-closeout, pr-land and handover-compact. Every command has `--help`.
Local mutation, provider/remote access and release are separate operations.

- [Product operations and changed contracts](docs/FPR-3-PRODUCT-SURFACES.md)
- [Authority, mirrors and repository lanes](docs/FPR-2-AUTHORITY-AND-LANES.md)
- [Source packaging, upgrade and rollback](docs/SOURCE-DISTRIBUTION.md)
- [Desktop source launcher](desktop/README.md)
- [Test selection and historical disposition](tests/README.md)
- [Contributing](CONTRIBUTING.md) and [security reporting](SECURITY.md)

## Current delivery status

The approved manual workflow is complete. The broader maintained kit received
[independent manual-delivery acceptance](docs/reviews/FPR-5-MANUAL-ACCEPTANCE.md)
at source `97f052949146c3cf337478927e6d345e353d2063`, followed by the owner's
[local source release](docs/releases/FPR-5-MANUAL-LOCAL-RELEASE.md), version
`1.0.0.dev1`. Recorded validation includes integrated checks, fixture installation,
migration and rollback, a local workflow pilot and owner-observed desktop use.
The [manual prompt-display closeout](docs/validation/CURRENT-PROMPT-DISPLAY.md)
completed the session instructions using the existing reader and writer.

Acceptance is limited to the recorded macOS source environments and explicit
manual workflow. Live providers, production mirror delivery, Windows/Linux
qualification and real-consumer migration are not established. Existing-project
installation remains on hold; it requires target-specific inspection, preservation
of owner files and history, backups, rollback and validated project binding.

Cursor start/end event adapters are available through explicitly selected
`init/sync --hooks`, but automatic Cursor events remain unverified. Codex and Claude
integrations are instruction-triggered. Vendor execution protection remains
unqualified and shared-chat behavior unresolved; these are outside the completed
manual scope. No signed full-product installer, hosted deployment or public
release is established by this branch. Earlier installers are historical artifacts.
