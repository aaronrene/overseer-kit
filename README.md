# Overseer Kit

Overseer Kit is a small local command-line tool that keeps one trustworthy next-task
handoff inside each Git or explicitly selected Muse repository. It helps prevent an agent or operator from using
a prompt from the wrong project, branch, lane, or point in history.

[v1.0.0-rc.1](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1) is the published bounded CLI prerelease,
not a stable or complete-product release. Its tag targets
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`; source, CLI and package metadata
still report `1.0.0`. Identify rc.1 by the tag, commit and release manifest,
not by `ok --version` alone.

Git/GitHub-only operation is a permanent supported choice with no Muse installation,
account or migration requirement. Muse authority and controlled GitHub mirroring
are explicit per-repository choices. The kit project's own publication is Muse-first.
See the [publication record](docs/decisions/V1-MUSE-PUBLICATION.md) and
[public evidence](docs/validation/V1-PUBLIC-EVIDENCE.md).

These docs are a separate post-publication follow-up. They do not change the rc.1
tag or archive. The [published installation/rollback guide](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md)
supersedes the historical README and quickstart inside that frozen archive.

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

Start with the exact [rc.1 release](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1) and its five named
attachments. Verify their checksums before extracting the attached source archive
at a fixed physical kit path. Follow the
[installation/rollback guide](docs/releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md)
for the full procedure and the [Git-only quickstart](docs/GIT-ONLY-QUICKSTART.md)
for repository setup.

The tested interpreters are Python 3.11 and 3.14 for Git-only operation; optional
Muse uses a separate Python 3.14 environment. Hosted evidence is Linux and retained
local evidence is macOS arm64. Use a conventional `.venv` at the fixed kit path;
consumer repositories do not install the kit's dependencies. Packaged/editable
Overseer installation, arbitrary newer interpreters and Windows are not established.

For an already verified source checkout at that fixed path:

```sh
cd /absolute/fixed/path/to/overseer-kit
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1.txt
.venv/bin/python -m pip check
./cli/ok --version
```

For development and the supported test suite:

```sh
.venv/bin/python -m pip install -r requirements-v1-dev.txt
.venv/bin/python -m pytest -q
```

Muse is optional and stays in its own conventional venv: The supported integration uses exactly
the pinned Overseer recovery build of Muse `0.2.1rc5` with Python 3.14.
The kit does not install Muse. See the guide for the immutable wheel URL and pins. To run the additional real Muse matrix:

```sh
.venv/bin/python -m pytest -q tests/v1 tests/retained tests/muse \
  --muse-python /absolute/path/to/muse-venv/bin/python
```

The supported CI entrypoint is `tools/ci/supported_v1.py`, run with this source
installation's `.venv/bin/python` and a required `--junitxml PATH`. Supplying
`--muse-python /absolute/muse-venv/bin/python` selects the full Git/Muse/mirror
matrix and checks the exact reviewed rc5 package source digest. Omitting it runs
the permanent Git-only matrix. No CI step publishes or installs hooks.

[Supported v1 CI](.github/workflows/supported-v1.yml) defines Git jobs for
Python 3.11/3.14 and a combined Python 3.14 job on Linux. Three retained hosted
runs each passed **156 / 156 / 289 tests**, with zero reported failures/errors/skips;
their exact heads and links are in the [public evidence index](docs/validation/V1-PUBLIC-EVIDENCE.md).

The combined job uses `MUSE_RC5_RECOVERY_WHEEL_URL` and verifies the recovery wheel
against [the exact artifact contract](tools/ci/muse-rc5-artifact.json).
This is an Overseer recovery build from verified installed bytes, not an upstream
rc5 release or reconstruction of the unavailable original sdist. Keep the immutable
wheel URL and all four recovery digests in the [published guide](docs/releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md).
Do not substitute a moving installer, another rc version or the PyPI package named `muse`.

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
  --base-head REVISION-FROM-STATUS \
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

Release watching needs no Overseer server or OCI registry. The published rc.1
records reviewed Muse source acceptance, its verified GitHub mirror, owner-accepted
PR #86 and the exact release tag. Later documentation has its own source revision
and PR; it must never be substituted into that tag or its five assets.

Review a specific release's notes and exact commit before updating. Stop commands
during source replacement, preserve the previous source/dependency set, and update
only a clean installation at the same physical path. Follow the guide's explicit
inventory and rollback procedure; moving `main` is not a release selection.
After replacing the source, preview and apply sync for each authorized repository:

```sh
KIT_ROOT=/absolute/fixed/path/to/overseer-kit
PROJECT_ROOT=/absolute/path/to/authorized-project
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" sync --dry-run --json
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" sync --json
"$PROJECT_ROOT/.overseer/bin/ok" status --json
"$PROJECT_ROOT/.overseer/bin/ok" next
```

Review the preview before applying sync.

Run `sync` once for each initialized repository. A source change intentionally makes
status/NEXT refuse with `runtime_changed` until that explicit sync updates the runtime
pin. `sync --dry-run` shows the planned managed-file changes first. It preserves the
repository UUID, NEXT, ROADMAP, HANDOVER, and application files.

## Validation and limits

The three retained hosted runs each passed **156 / 156 / 289** tests. Earlier
scoped architecture/build reviews, fixed-path source installation/rollback and the
32-check authorized DINERO pilot remain closed at their original scope. They were
not repeated for this documentation follow-up. No unresolved supported-test failure
is recorded; historical out-of-scope failures remain disclosed in the
[validation record](docs/validation/V1-RECOVERY.md).

Native Muse rc5 clone omitted **19 empty directories** while preserving all **861
file bytes**. Only verified isolated readbacks restored the approved directory
metadata. Do not disable dirty-state checks or copy those directories into an
unrelated project. Muse snapshots do not store POSIX modes; the mirror uses an
explicit ten-path executable policy.

Recovered Muse provenance, private/production Hub operation, general file/mode
fidelity, relocation, untested platforms, packaged/desktop installation and broader
consumer rollout remain limited or unvalidated. The trusted-host design protects
against stale state and ordinary mistakes; it is not a boundary against a malicious
administrator or another process with the same user account.

Historical pre-reset commands remain in `cli/legacy_main.py` for evidence but are
outside the public v1 command surface. Historical test sources remain preserved;
see [test scope](tests/README.md).

The [Muse restoration audit](docs/validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08)
links the historical findings and their bounded restoration disposition. Do not run the historical deploy script to publish this
candidate. OCI remains excluded.
