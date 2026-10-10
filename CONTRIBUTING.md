# Contributing to Overseer Kit

Overseer Kit v1 is deliberately small: a trusted-host local Git/Muse utility for
repository identity, status, and one canonical NEXT handoff. Read `README.md`,
`docs/decisions/V1-SCOPE-RESET.md`, and `tests/README.md` before changing it.

## Supported scope

The public commands are `status`, `init`, `sync`, `adopt`, `mirror`, `next`, and `next-write`.
Keep repository/root/UUID binding, canonical `docs/NEXT.md`, explicit context
checks, stale-state refusal, deterministic source imports, confined atomic writes,
and living-document preservation intact.

The owner's scope correction requires a per-repository choice of Git/GitHub only
or MuseHub authority with controlled GitHub mirroring. Preserve standalone Git-only
operation without a Muse dependency. Local authority, explicit adoption, controlled
mirroring and combined validation are complete. Start with the [current docs index](docs/README.md),
[Git-only quickstart](docs/GIT-ONLY-QUICKSTART.md), [bridge workflow](MUSE-BRIDGE-WORKFLOW.md),
and [public evidence](docs/validation/V1-PUBLIC-EVIDENCE.md).

Former hosted, desktop, governance, freeze-review, publishing, registry,
receipt, transaction, and orchestration implementations remain historical source.
Do not expose them through the v1 entrypoint or treat their old documentation and
tests as current requirements.

## Development setup

Use a tested Python 3.11 or 3.14 environment:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1-dev.txt
.venv/bin/python -m pytest -q
```

The default pytest collection is the supported matrix in `tests/v1` and
`tests/retained`. Do not delete or rewrite historical tests to obtain a green run.
Changes to Muse integration also require the real `tests/muse` matrix with
`--muse-python /absolute/muse-venv/bin/python`, in addition to the default suite.
The pinned Muse environment is separate and uses tested Python 3.14. See
`tests/README.md`; no skip may conceal an unavailable supported integration check.

## Making a change

1. Start from current `main` on a feature branch.
2. Keep the change within bounded-v1 scope.
3. Add meaningful supported tests when behavior changes.
4. Run the complete supported suite and `git diff --check`.
5. Update `docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` together when status
   changes. Only `docs/NEXT.md`, published through `next-write`, carries an action.
6. Push the feature branch and open a pull request. Never push directly to `main`.

Do not commit checkout-local bindings: `.overseer/config.yaml`, `.overseer/bin/`,
`.overseer/local/`, `docs/NEXT.md`, or `.cursor/`. They contain physical paths and are generated for
each initialized checkout. Do not commit secrets, `.env*`, private keys, consumer
content, or machine-specific run logs.

## Pull request checklist

- The supported suite passes with exact counts reported.
- No supported requirement is skipped or marked expected-failure.
- Runtime files, `VERSION`, and `pyproject.toml` agree when the version changes.
- README and CHANGELOG describe the behavior users actually receive.
- `gitleaks` or an equivalent secret scan finds no new secret.
- The branch contains no checkout-local paths or bindings.
- No consumer, hook, network operation, release, or deployment occurred without
  explicit authorization.

Security reports follow `SECURITY.md`. The MIT license remains in `LICENSE`.
