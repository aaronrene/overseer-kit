# Overseer Kit

Overseer Kit provides repository-bound governance for Git and optional native Muse
projects. One `cli/ok` serves the CLI, local loopback app and desktop launcher.
The hosted dashboard is a separate read-only projection.

This branch implements full-product restoration. Focused author checks do not
establish release readiness: combined FPR-4 validation, independent FPR-5 review
and an owner release decision remain required. Historical bounded certification
applies only to its recorded source and claim.

Use this installation's conventional `.venv`, with the pinned requirements in
`requirements-v1.txt` (and `requirements-v1-dev.txt` for tests). Source runtime
bindings include reachable engines and assets. No neighboring installation,
ambient Python path or native identity bridge supplies a fallback.

```sh
./cli/ok -C /absolute/project init --vcs git
./cli/ok -C /absolute/project status
./cli/ok -C /absolute/project next --lane product
./cli/ok -C /absolute/project governance-sync --dry-run
./cli/ok -C /absolute/project check-ok --topic example --dry-run
./cli/ok -C /absolute/project app --bind 127.0.0.1 --port 8765
```

`docs/NEXT.md` is the single handoff authority. `next` validates identity, selected
lane, model, revision and prompt digest before display. HANDOVER and ROADMAP are
paired summaries. Only explicit `next-write` publishes accepted text with expected
whole-file digest and current context. Hooks and app refresh never generate tasks.

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
- [Restoration plan](docs/decisions/FULL-PRODUCT-RESTORATION-PLAN.md)
- [Test selection and historical disposition](tests/README.md)

Cursor start/end event adapters are available through explicitly selected
`init/sync --hooks`. Named host-version delivery is pending FPR-4. Codex and Claude
integrations are instruction-triggered; no native automatic lifecycle guarantee
is inferred. No signed full-product installer, hosted deployment or published
release is established by this branch. Earlier installers are historical artifacts.
