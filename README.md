# Overseer Kit

Overseer Kit is a small local command-line tool that keeps one trustworthy next-task
handoff inside each Git or explicitly selected Muse repository. It helps prevent an agent or operator from using
a prompt from the wrong project, branch, lane, or point in history.

The Git-based handoff core is locally validated, but intended v1 is incomplete.
The intended product lets each repository choose Git/GitHub only or MuseHub as its
source of truth with a GitHub mirror. The [mirror workflow](MUSE-BRIDGE-WORKFLOW.md)
documents explicit preparation, verification and separately authorized delivery.
Git-only is a permanent supported choice:
no Muse installation, account, or migration is required. R1 implements optional
local Muse handoffs and explicit adoption; R2 adds controlled mirror preparation
and retry. R3 reconciles the source in isolation and validates combined local operation. The source version `1.0.0` is an
unpublished candidate, and its Git-only release is on hold. The behavior described
below is the current implementation, not the completed Muse-first product. See the
[scope decision](docs/decisions/V1-SCOPE-RESET.md) and the complete
[validation record](docs/validation/V1-RECOVERY.md).

## What it does

Each initialized repository receives:

- a persistent UUID and exact physical-root binding in `.overseer/config.yaml`;
- a repository-bound launcher at `.overseer/bin/ok`;
- one canonical handoff in `docs/NEXT.md`;
- small ROADMAP and HANDOVER documents when they do not already exist.

Before printing NEXT, Overseer checks the repository UUID and root, selected VCS branch,
configured lane and model label, action ID and kind, prompt digest, expected NEXT
digest when supplied, and authoritative revision freshness. Muse mode also pins
the Muse repository identity, store, separate Python environment and package source
digest. A copied launcher, copied config, stale
handoff, wrong repository, wrong lane, wrong branch, or stale writer is refused
without printing the prompt.

The public commands are:

| Command | Purpose |
| --- | --- |
| `status` | Show repository, runtime, selected local revision, and NEXT status without changing files. |
| `init` | Give one checkout its identity, exclusions and initial local handoff files. |
| `sync` | Refresh the bound launcher and runtime pin after an explicit kit update. |
| `adopt` | Explicitly change schema/authority, preview exclusions, or restore a preserved config. |
| `mirror` | Prepare or verify a pinned Muse projection offline; explicitly deliver it after separate authorization. |
| `next` | Validate and print the current handoff. It never runs the task. |
| `next-write` | Publish a new handoff with explicit context and the previous NEXT digest. |

## What it does not do

Overseer does not decide what task should come next, execute a prompt, infer that
work is complete, verify which AI model is actually running, or judge whether task
prose is strategically correct. The operator or agent chooses the task and advances
it explicitly with `next-write`.

Local handoff commands and mirror preparation stay offline. Only explicitly
invoked `mirror deliver` observes Hub/GitHub, pushes the verified distribution
commit and creates or verifies its PR. It never merges, releases or deploys.
The kit has no hosted service, registry, background process,
telemetry, automatic updater, transaction system, or OCI machinery. It supports
local Git and Muse code-domain checkouts and linked worktrees. Moving an initialized checkout or moving the kit
installation requires an explicitly reviewed rebind; copying is not migration.

## Prepare the source installation

Use Python 3.11 or newer and keep this checkout at a stable physical path. The kit
uses its own conventional virtual environment; consumer repositories do not install
its Python dependencies.

```sh
cd /absolute/path/to/overseer-kit
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1.txt
./cli/ok --version
```

Install from the latest published `v1.*` release or from a reviewed source checkout.
Do not treat an unreviewed feature branch as an update. Before the first v1 release
is published, only the validated local release candidate is available.

For development and the supported test suite:

```sh
.venv/bin/python -m pip install -r requirements-v1-dev.txt
.venv/bin/python -m pytest -q
```

Muse is optional and stays in its own conventional venv: The supported integration uses exactly
Muse `0.2.1rc5` with Python 3.14 or newer. The kit itself still supports Python
3.11 or newer and does not install Muse. To run the additional real Muse matrix:

```sh
.venv/bin/python -m pytest -q tests/v1 tests/retained tests/muse \
  --muse-python /absolute/path/to/muse-venv/bin/python
```

The supported CI entrypoint is `tools/ci/supported_v1.py`, run with this source
installation's `.venv/bin/python` and a required `--junitxml PATH`. Supplying
`--muse-python /absolute/muse-venv/bin/python` selects the full Git/Muse/mirror
matrix and checks the exact reviewed rc5 package source digest. Omitting it runs
the permanent Git-only matrix. No CI step publishes or installs hooks.

`.github/workflows/supported-v1.yml` defines Git jobs for Python 3.11/3.14 and the
combined job for Python 3.14 on Linux. Hosted execution is not yet evidenced.
The combined job needs repository variable `MUSE_RC5_URL` pointing to a retained
HTTPS archive whose SHA-256 is
`1a17ee8792e423927ff07ac96c85de0016bc7f79ebacc4e8a8e5073b436f2ea6`.
It fails if the variable or exact archive is unavailable. Staging's moving
installer now selects rc11; its rc5 release URL returned 404 during R3. Do not
substitute another version or the unverified PyPI package named `muse`.
R3's fresh local environment used a wheel reconstructed from verified installed
rc5 files plus freshly installed dependencies; this is not proof that the original
upstream archive can be installed on a clean host. Artifact availability, hosted
CI, and Linux/3.11 execution remain release prerequisites. See the exact
[validation results](docs/validation/V1-RECOVERY.md).

Muse rc5's recursive `code add .` can omit a new dot-directory. Explicitly stage
`.github/workflows/supported-v1.yml` when preparing this source, and compare the
actual committed manifest before using it as a distribution or CI input.

## Add one repository

Use the repository's absolute path. Initialization preserves existing ROADMAP and
HANDOVER files and refuses an existing unmanaged launcher.

```sh
./cli/ok -C /absolute/path/to/project init \
  --vcs git \
  --repo-name PROJECT-NAME \
  --lane product \
  --model 'GPT-6 Astra'
```

Automatic editor hooks are off by default. Keep them off unless you deliberately
review and authorize hook installation for that repository.

For an already prepared Muse checkout, select `--vcs muse --muse-python
/absolute/path/to/muse-venv/bin/python`. An uninitialized mixed checkout requires
an explicit choice. An existing Git binding remains Git even if Muse metadata
appears later. `init` and `sync` never change its authority. See
[adoption and rollback](docs/MIGRATE-EXISTING-REPO.md) before changing modes.

## Daily use

From an initialized repository:

```sh
./.overseer/bin/ok status
./.overseer/bin/ok next
```

`status --json` is useful for automation. A dirty repository is reported but does
not by itself invalidate NEXT. A changed branch, a later authoritative commit, altered prompt,
wrong identity, or changed runtime does invalidate it. Exit codes are 0 for success,
1 when `status` can report identity but NEXT is invalid, and 2 for refusal or usage
errors.

Muse freshness uses its own branch and revision, regardless of a nearby Git HEAD.
Publication is always `not_checked_offline` on these local commands; a valid local
NEXT says nothing about MuseHub acceptance or GitHub delivery. Muse dirty state
compares regular working files with the branch snapshot and reports a nonempty
shared stage as dirty. R1 does not certify executable modes, symlinks, or a separate
per-worktree Muse staging index.

Use the expectation options when resuming a previously read handoff:

```sh
./.overseer/bin/ok next \
  --repo-id UUID-FROM-STATUS \
  --branch BRANCH-FROM-STATUS \
  --lane product \
  --model 'GPT-6 Astra' \
  --action-id EXPECTED-ACTION \
  --action-kind implement \
  --expect-next DIGEST-FROM-STATUS
```

## Publish the next handoff

Store the new prompt in a regular UTF-8 file inside the consumer repository, then
run the kit installation's writer. All context fields and the current raw NEXT
digest are required:

```sh
/absolute/path/to/overseer-kit/cli/ok -C /absolute/path/to/project next-write \
  --repo-id UUID-FROM-STATUS \
  --branch CURRENT-BRANCH \
  --lane product \
  --model 'GPT-6 Astra' \
  --action-id TASK-1 \
  --action-kind implement \
  --expect-next DIGEST-FROM-STATUS \
  --prompt-file prompt.txt
```

Action kinds are `plan`, `implement`, `review`, `maintain`, and `stop`. Use `stop`
when no executable task is queued. The writer compares the previous digest, locks
cooperating writers briefly, writes a unique temporary file, flushes it, and replaces
NEXT atomically. It changes no other consumer document.

Muse writers additionally require `--vcs muse --base-head CURRENT-MUSE-REVISION`.
Use `--base-head unborn` before the first commit. Commit application work first,
then publish ignored NEXT against the new revision. Git accepts the same explicit
revision options; its legacy tracked-NEXT closing-commit exception remains supported.

## Simple update notifications

Overseer deliberately does not check the internet in the background. The simplest
notification system is GitHub's existing release watcher:

1. Open the repository on GitHub.
2. Select **Watch → Custom → Releases**.
3. GitHub will notify you when a maintainer publishes a new release.

This needs no Overseer server or OCI registry. Maintainers should increment
`VERSION`, update `CHANGELOG.md`, tag the tested commit, and publish a GitHub Release
only when a build is ready for users. A version in the source tree is not itself a
published release; verify that the matching GitHub Release exists before updating.
For the intended Muse-first release, accept the reviewed source in MuseHub first,
then verify its GitHub mirror before tagging and announcing that same version.
That restored publication procedure remains pending; this is the required order.

Users can also check manually, with no changes to their working files:

```sh
git -C /absolute/path/to/overseer-kit fetch --tags origin
git -C /absolute/path/to/overseer-kit status --short --branch
git -C /absolute/path/to/overseer-kit log --oneline HEAD..origin/main
```

Review the release notes before updating. After bounded v1 is released on `main`, a
clean source installation can update explicitly:

```sh
git -C /absolute/path/to/overseer-kit pull --ff-only
/absolute/path/to/overseer-kit/cli/ok -C /absolute/path/to/project sync --dry-run
/absolute/path/to/overseer-kit/cli/ok -C /absolute/path/to/project sync
```

Run `sync` once for each initialized repository. A source change intentionally makes
status/NEXT refuse with `runtime_changed` until that explicit sync updates the runtime
pin. `sync --dry-run` shows the planned managed-file changes first. It preserves the
repository UUID, NEXT, ROADMAP, HANDOVER, and application files.

## Validation and limits

Bounded v1 passed architecture and completed-build review, clean dependency
installation, current/previous rollback, 77 supported tests, and 32 checks in an
authorized DINERO consumer pilot. That pilot preserved all existing consumer files
and its preexisting uncommitted edit while keeping automatic hooks disabled.

Validation used Python 3.14.4 on Darwin arm64 and a fixed-path source installation.
It does not establish packaged installation, other-platform compatibility,
concurrent commands during source replacement, or automatic migration/rebinding.
The trusted-host design protects against stale state and ordinary mistakes; it is
not a security boundary against a malicious administrator or process with the same
user account.

Historical pre-reset commands remain in `cli/legacy_main.py` for evidence but are
outside the public v1 command surface. Historical test sources remain preserved;
see [test scope](tests/README.md).

The [Muse restoration audit](docs/validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08)
records verified reuse, bridge defects, authority and handoff design, and the
remaining milestones. Do not run the historical deploy script to publish this
candidate. OCI remains excluded.
