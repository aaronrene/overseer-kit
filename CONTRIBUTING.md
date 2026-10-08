# Contributing to Overseer Kit

Overseer Kit v1 is deliberately small: a trusted-host local Git utility for
repository identity, status, and one canonical NEXT handoff. Read `README.md`,
`docs/decisions/V1-SCOPE-RESET.md`, and `tests/README.md` before changing it.

## Supported scope

The public commands are `status`, `init`, `sync`, `next`, and `next-write`.
Keep repository/root/UUID binding, canonical `docs/NEXT.md`, explicit context
checks, stale-state refusal, deterministic source imports, confined atomic writes,
and living-document preservation intact.

The owner's scope correction requires a per-repository choice of Git/GitHub only
or MuseHub authority with controlled GitHub mirroring. Preserve standalone Git-only
operation without a Muse dependency. Muse restoration is pending; use the validation
audit as the design baseline rather than reactivating the entire legacy CLI.

Former hosted, desktop, governance-sync, freeze-review, publishing, registry,
receipt, transaction, and orchestration implementations remain historical source.
Do not expose them through the v1 entrypoint or treat their old documentation and
tests as current requirements.

## Development setup

Use Python 3.11 or newer:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1-dev.txt
.venv/bin/python -m pytest -q
```

The default pytest collection is the supported matrix in `tests/v1` and
`tests/retained`. Do not delete or rewrite historical tests to obtain a green run.

## Making a change

1. Start from current `main` on a feature branch.
2. Keep the change within bounded-v1 scope.
3. Add meaningful supported tests when behavior changes.
4. Run the complete supported suite and `git diff --check`.
5. Update `docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` together when status
   changes. Only `docs/NEXT.md`, published through `next-write`, carries an action.
6. Push the feature branch and open a pull request. Never push directly to `main`.

Do not commit checkout-local bindings: `.overseer/config.yaml`, `.overseer/bin/`,
`docs/NEXT.md`, or `.cursor/`. They contain physical paths and are generated for
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
