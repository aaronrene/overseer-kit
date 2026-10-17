# FPR-5 repair author evidence

Start with [the repair report](../FPR-5-REPAIRS.md). These are new author results;
the original independent review, its FINDINGS verdict and raw evidence remain
unchanged in `docs/reviews/FPR-5-REVIEW.md` and `docs/reviews/fpr5/`.

- `opening.json`: verified initial root, repository identity, HEAD/runtime,
  dependencies, original review inventory, historical hashes and all 144 refs.
- `source-map.json`: exact eight production repairs and final runtime identity.
- `transport/`, `foundation/`, `resources/`: requirement-level failing-before,
  candidate and affected results, with local readmes and all raw failures.
- `orchestrator-before*/`, `orchestrator-after*/`: original-source and candidate
  checkpoint results. The initial harness error and interrupted-source setup
  error remain preserved separately from the stable targeted pass.
- `integrated-selection.json` and `integrated/`: the complete 1,361-case current
  contract selection and raw collection/command/boundary/log/JUnit evidence.
- `package-race.md`, `package-race-diagnosis.json` and
  `fpr4_matrix-before-resource-deferral.py`: exact failed archive evidence and
  the original driver that scheduled one archive case alongside evidence writers.
- `package-rerun-selection.json`: the two archive-dependent cases rerun after
  correcting only the validation schedule.
- `coverage.json`: 1,360 passes/one failure in the combined execution, followed
  by two affected passes on unchanged production/tests/dependencies; all 1,361
  selected cases have passing evidence across these separate runs. This is not
  a relabelled all-green combined execution.
- `closeout.json`: commands and assertions for narrow bound runtime refresh,
  preserved assets/hooks, explicit-context NEXT publication and bound readback.
- `ARTIFACTS.json`: SHA-256, size and mode for every new evidence file except
  itself, plus companion source/tests/contracts and published repository state.

Candidate runtime digests differ where the evidence says so. The repaired
runtime is `cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.
The closing feature commit has sole parent
`4c62c17cff6c606a5e1ddf565e12353973b3bcad`; resolve its exact hash using
`git log -1 --format=%H -- docs/validation/FPR-5-REPAIRS.md`.

Preservation can be checked before commit with
`.venv/bin/python3 -I -B scripts/fpr5_preservation.py`, or immediately after the
single closing commit with `--closing-commit`. No report here supplies independent
certification, Python 3.11 acceptance, named-host acceptance, additional platform
claims, a new pilot or release authority.
