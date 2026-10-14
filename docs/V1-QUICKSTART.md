# Bounded v1 source installation

Supported milestone: POSIX Git repositories/worktrees and Python 3.11+ with a
conventional venv. This build was tested offline on Python 3.14.4. Other Python
versions and packaged installation are not yet validated. Ordinary venv Python
symlinks are expected. There is no PATH-Python or neighboring-checkout fallback.

For a normal installation with separately authorized dependency access:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1-dev.txt
```

Runtime-only installations need `requirements-v1.txt`. In this recovery run,
packages were copied offline from the preserved local environment, excluding
editable-package finders and `.pth` files; imports resolve to this checkout.

Initialize a disposable Git repository using this installation's absolute CLI:

```sh
/absolute/kit/cli/ok -C /absolute/fixture init --repo-name fixture
/absolute/kit/cli/ok -C /absolute/fixture status
/absolute/kit/cli/ok -C /absolute/fixture next
/absolute/kit/cli/ok -C /absolute/fixture sync --dry-run
/absolute/kit/cli/ok -C /absolute/fixture sync
```

Init creates a UUID and binds the physical checkout plus runtime location/hash.
It preserves existing ROADMAP and HANDOVER. An existing legacy config is refused;
automatic migration or rebinding is not part of this milestone. A bound launcher
at `.overseer/bin/ok` refuses another repository. `--hooks` is opt-in and exercised
only in disposable fixtures in this task; this development checkout has automatic
hooks disabled. Sync preserves NEXT and documents, repairs executable modes, and
explicitly accepts code changes only from the already-bound installation.

NEXT is canonical `docs/NEXT.md`. See [the writer contract](PRINT-NEXT.md).
No public command executes prompts, publishes, merges, or contacts providers.
The former command surface remains in `cli/legacy_main.py` as historical source.
Do not use it as a way around v1 repository checks.

Run the complete supported suite:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
```

Independent review, clean installation/current-previous rollback, and a separately
authorized consumer pilot remain outstanding. This is not a release announcement.
