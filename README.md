# Overseer Kit

Overseer Kit is a small local command-line tool that keeps one trustworthy next-task
handoff inside each Git repository. It helps prevent an agent or operator from using
a prompt from the wrong project, branch, lane, or point in history.

The Git-based handoff core is locally validated, but intended v1 is incomplete.
The owner requires MuseHub as the source of truth with GitHub mirroring; restoration
has been audited and is not implemented yet. The source version `1.0.0` is an
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

Before printing NEXT, Overseer checks the repository UUID and root, Git branch,
configured lane and model label, action ID and kind, prompt digest, expected NEXT
digest when supplied, and Git freshness. A copied launcher, copied config, stale
handoff, wrong repository, wrong lane, wrong branch, or stale writer is refused
without printing the prompt.

The public commands are:

| Command | Purpose |
| --- | --- |
| `status` | Show repository, runtime, Git, and NEXT status without changing files. |
| `init` | Give one Git checkout its identity and initial local handoff files. |
| `sync` | Refresh the bound launcher and runtime pin after an explicit kit update. |
| `next` | Validate and print the current handoff. It never runs the task. |
| `next-write` | Publish a new handoff with explicit context and the previous NEXT digest. |

## What it does not do

Overseer does not decide what task should come next, execute a prompt, infer that
work is complete, verify which AI model is actually running, or judge whether task
prose is strategically correct. The operator or agent chooses the task and advances
it explicitly with `next-write`.

The bounded v1 does not push, pull, fetch, merge, release, deploy, modify application
code, or contact a network. It has no hosted service, registry, background process,
telemetry, automatic updater, transaction system, or OCI machinery. It supports
local Git checkouts and worktrees. Moving an initialized checkout or moving the kit
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

## Add one repository

Use the repository's absolute path. Initialization preserves existing ROADMAP and
HANDOVER files and refuses an existing unmanaged launcher.

```sh
./cli/ok -C /absolute/path/to/project init \
  --repo-name PROJECT-NAME \
  --lane product \
  --model 'GPT-6 Astra'
```

Automatic editor hooks are off by default. Keep them off unless you deliberately
review and authorize hook installation for that repository.

## Daily use

From an initialized repository:

```sh
./.overseer/bin/ok status
./.overseer/bin/ok next
```

`status --json` is useful for automation. A dirty repository is reported but does
not by itself invalidate NEXT. A changed branch, a later Git commit, altered prompt,
wrong identity, or changed runtime does invalidate it. Exit codes are 0 for success,
1 when `status` can report identity but NEXT is invalid, and 2 for refusal or usage
errors.

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
