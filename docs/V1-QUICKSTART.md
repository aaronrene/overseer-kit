# Bounded v1 source installation

The [certified bounded milestone](validation/V1-CERTIFICATION.md) covers
repository-bound source v1 for local POSIX Git repositories/worktrees under the
trusted-host model, validated on Python 3.14.4, with `status`, `init`, `sync`,
`next` and `next-write`. Python 3.11+ is the source prerequisite, not a validated
version matrix. Other Python versions, other platforms and packaged installation
are outside this certification. Ordinary venv Python
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

The independent review is complete; R1/R2 repair evidence is recorded in
[validation](validation/V1-RECOVERY.md). Clean source installation and
current-to-previous-to-current rollback passed in disposable fixtures; see the
[reproduction and limits](validation/V1-RECOVERY.md#clean-source-installation-and-rollback--2026-10-14).
The owner-authorized [newly created test-repository pilot](validation/V1-RECOVERY.md#newly-created-test-repository-pilot--2026-10-14)
passed one local documentation handoff cycle without consumer hooks or network
access. It does not validate an existing consumer's operational workflow. Any
other consumer repository or further pilot work still needs owner authorization.
The separate [final adjudication](validation/V1-CERTIFICATION.md) certifies only
the bounded claim above, preserving the independent FINDINGS verdict and author
repair evidence. Release or distribution requires a separate owner decision;
certification grants no release, merge, push, publication or deployment authority.

The validated rollback procedure replaces committed source at the **same physical
installation root**, while retaining its conventional `.venv`. Stop commands using
that installation during source replacement. Before explicit refresh, bound
commands refuse with `runtime_changed`; run that installation's `sync --dry-run`
and then `sync` for the bound repository to accept the changed runtime. UUID,
physical root, living documents and NEXT remain intact. Restore current source at
that same root and repeat the explicit refresh to recover. Sync from a different
installation path refuses, including when its code is identical; automatic
rebinding is outside the contract.

This is trusted-host source maintenance with per-file, rerunnable sync, not an
atomic installation switch or a packaged upgrade facility. The tested previous
build retains known R1/R2 concurrency findings; successful rollback does not clear
them. No packages were downloaded for this validation.
