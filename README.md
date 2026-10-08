# Overseer Kit — bounded v1 recovery

A local CLI for repository identity, status, and one validated next action.
Bounded v1 local validation is complete, including the authorized DINERO manual
pilot. The build remains `1.0.0.dev1`; no release or broader rollout was performed.
Read [scope](docs/decisions/V1-SCOPE-RESET.md) and
[verification](docs/validation/V1-RECOVERY.md).

Use a conventional Python 3.11+ environment in this checkout:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1-dev.txt
./cli/ok --version
./cli/ok -C /absolute/disposable/repo init
./cli/ok -C /absolute/disposable/repo status
./cli/ok -C /absolute/disposable/repo next
./cli/ok -C /absolute/disposable/repo sync
.venv/bin/python -m pytest -q
```

The supported runtime is this source checkout with its own `.venv`. Normal venv
Python symlinks are allowed. The launcher uses isolated Python and has no PATH or
neighboring-checkout fallback. Consumer `.overseer/bin/ok` launchers bind an exact
physical repository root and UUID to an absolute installation. A copied config,
NEXT, or bound launcher fails closed. `-C` must name a Git root; without it the
current working directory selects its containing Git repository. A bound launcher
refuses a cwd belonging to another repository unless `-C` explicitly names its
own repository. Symlink aliases of a root resolve to the same physical identity.

`init` assigns the UUID once. It preserves existing ROADMAP/HANDOVER documents.
It refuses legacy configuration; migration is an explicit maintainer operation,
not an automatic identity rewrite. `sync` refreshes the launcher and the version
and source digest pin in config, preserving NEXT and living documents. It never
changes repository identity or switches installations. Moved checkouts need an
explicitly reviewed config/launcher rebind; copying is not a supported migration.
`--hooks` on init/sync installs read-only Cursor hooks; use only disposable
fixtures during this milestone. User hook configurations should be reviewed before
opting into replacement. No hook searches PATH, environment overrides, or peers.

Only `docs/NEXT.md` carries the current action and prompt. `next` validates its
UUID/root, current branch, configured lane/model, action ID grammar, action kind,
prompt digest, and Git freshness before printing. Optional `--repo-id`, `--branch`,
`--lane`, `--model`, `--action-id`, `--action-kind`, and `--expect-next` check caller
expectations. Use these when resuming a previously read action. Printed binding
fields are generated from validated metadata, never extracted from prose.

Publish a prompt stored in a regular, confined UTF-8 repository file:

```sh
./cli/ok -C /absolute/disposable/repo next-write \
  --repo-id UUID-FROM-STATUS --branch main --lane product \
  --model 'GPT-6 Astra' --action-id TASK-1 --action-kind implement \
  --expect-next DIGEST-FROM-STATUS --prompt-file prompt.txt
```

Kinds: `plan`, `implement`, `review`, `maintain`, `stop`. The writer only changes
NEXT, compares the prior raw SHA-256 (`absent` for a missing NEXT), serializes
cooperating writers with a short advisory directory lock, fsyncs a unique sibling
temporary file, and replaces atomically. No journal or recovery state is created.
Keep binding labels out of prompt prose. A write anchors to the current Git HEAD;
NEXT remains valid through one non-merge commit containing those exact bytes.
Any later commit requires a deliberate refresh. Config and NEXT are ordinary
owner-managed files; digests detect mistakes, not malicious owner edits.

`status` reports repository and runtime identity even when NEXT is invalid. Exit
codes: 0 success, 1 status with invalid NEXT, 2 refusal/usage/error. Refused `next`
and hooks emit no prompt. Hooks consume optional Cursor `workspace_roots` and
refuse foreign or ambiguous roots. No command executes the next action or performs
network, push, merge, release, deployment, or automatic branch changes.

Historical pre-reset commands remain as source in `cli/legacy_main.py` and their
modules, but are outside this command surface. Historical tests remain intact;
see [test scope](tests/README.md). Architecture review, completed-build finding
closure, clean installation/rollback and the authorized DINERO pilot are complete;
the [validation record](docs/validation/V1-RECOVERY.md) describes the evidence and
limits. DINERO hooks remain disabled. Other consumers need their own authorization.

NEXT checks repository binding, declared context and freshness. The operator or
agent still chooses the task text and advances it through `next-write` when work
finishes. The CLI does not infer task completion or verify which AI model is
actually running. Reading a stop action means no executable task is queued.
