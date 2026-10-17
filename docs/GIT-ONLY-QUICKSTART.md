# Git-only source quickstart

Use the installation's conventional `.venv` with `requirements-v1.txt`.
From the installation, select an existing local repository explicitly:

```sh
./cli/ok -C /absolute/project init --vcs git
./cli/ok -C /absolute/project status
./cli/ok -C /absolute/project next
./cli/ok -C /absolute/project app
```

Git is the selected local revision authority; remote state is unknown offline.
Muse is not required or probed. `docs/NEXT.md` is canonical; HANDOVER and ROADMAP
summarize progress. Publish an accepted task only with explicit-context,
expected-digest `next-write`. Use `--help` for its required fields.

Existing installs use explicit reviewed migration or runtime refresh, preserving
identity/settings/NEXT. See [product operations](FPR-3-PRODUCT-SURFACES.md) and
[source upgrades/rollback](SOURCE-DISTRIBUTION.md). Automatic host-version delivery,
combined validation and independent review remain pending; no release claim follows.
