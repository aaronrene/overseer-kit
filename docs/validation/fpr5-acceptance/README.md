# FPR-5 remaining acceptance evidence

This directory records owner-authorized acceptance work and one native startup
repair. It is author evidence, not independent adjudication or release approval.
The current conclusions and remaining requirements are in
[FPR-5-ACCEPTANCE.md](../FPR-5-ACCEPTANCE.md). Earlier review and repair inventories
remain unchanged in their original directories.

- `authorization.json` and `source-preparation.json` identify the owner scope and
  original frozen 1,483-file source archive. Preparation predates the later owner
  authorization; its then-pending permissions are historical.
- `acquire_cffi.py`, `acquisition-1.json`, `acquisition-2.json` and the exact PyPI
  metadata preserve the narrowly authorized download, initial DNS failure and
  verified wheel hash. The wheel remains local at its recorded temporary path.
- Python preparation/selection records identify the exact interpreter and
  dependencies, all 1,196 required Git cases, and the explicit separation of
  real-native Muse cases assigned to Python 3.14.
- `initial-collection/` retains the interrupted ENOSPC collection attempt.
  `matrix/` retains the complete serial group's raw records, lossless collection
  identities, logs and XML. No failed run is relabelled as a green run.
- Targeted fixture setup and rerun records distinguish installing the expected
  consumer footprint from any production repair, and identify the one native
  configuration change used by affected package checks.
- `pilot/` contains the safe durable subset of the disposable integrated local
  workflow. Its inventory also identifies externally retained backups.
- `host-platform/` separates original native launch failure, the repaired
  candidate build/window/shutdown observations, and unresolved actual Cursor
  lifecycle and rendered GUI evidence. Host profiles, caches and native binaries
  are retained externally; they are not committed here.
- `verify_preservation.py` verifies original evidence, tests, runtime, protected
  refs and the sole authorized native delta. It accepts the new acceptance
  closing commit only when its sole parent is the original repair closing commit.
- `next-prompt.txt` is the input to bound digest-checked publication. Only
  `docs/NEXT.md` is the canonical current action.
- `ARTIFACTS.json` inventories the final durable evidence by bytes, modes and
  SHA-256, excluding itself to avoid a circular hash.

Raw failures and incomplete attempts are intentional evidence. In particular,
the pilot's ENOSPC-interrupted record is incomplete but remains valid JSON; no
missing command results are inferred. Passing fixture cleanup removed only new
rebuildable test trees after complete raw evidence was saved. Older worktrees,
the completed older pilot and Muse history were not cleanup targets.
