# FPR-5 independent review evidence

The [single review verdict](../FPR-5-REVIEW.md) is authoritative for this review.
These files preserve the reviewer's original probes, raw outputs, focused runs,
and independent reconciliation of the existing FPR-4 records. They do not modify
FPR-4 results or constitute release approval.

The fixed source is `4c62c17cff6c606a5e1ddf565e12353973b3bcad`, with runtime
`bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`.
The original nonrepository fixture parent was
`/private/tmp/overseer-fpr5-review.jTlE9P`. Raw files retain those original paths.
Only scripts and evidence are retained here; disposable repository copies,
pytest caches, installed runtimes and generated fake executables are excluded.
The scripts regenerate those fixtures. [ARTIFACTS.json](ARTIFACTS.json) records
the retained evidence hashes; [closing-checks.json](closing-checks.json) records
source/ref/preservation checks after adding the report.

## Reproduction

Run from the reviewed repository using its conventional `.venv`. The wrapper
creates a new `/private/tmp` directory automatically and prints its location:

```sh
.venv/bin/python3 -I -B docs/reviews/fpr5/reproduce.py redirect
```

[reproduce.py](reproduce.py) relocates preserved scripts without changing the
original evidence. It refuses a different HEAD/runtime or changed tracked source.
`--repo` can select the same
reviewed source in another local checkout with its conventional venv;
`--output /private/tmp/NEW-DIRECTORY` selects a nonexistent fixture directory.
Do not rerun a raw hardcoded-path script into its occupied original fixture.
For repaired-source validation, adapt the raw probe and explicitly record the
new commit, runtime and dependency boundary rather than reusing these identities.

| Case | Scope / expected result on the reviewed source |
| --- | --- |
| `redirect` | R1: real urllib redirect handling with synthetic responses and a fake token; no sockets. Prints the disallowed second host and forwarded fake authorization. |
| `commands` | R2/R6: real dispatcher, fake `gh`, configured marker script; records unbound selectors reaching fake merge and a dry-run refusal without marker execution. |
| `foundation` | R3/R5: supported legacy migration collision and valid multi-lane repeated init; records the undesirable results and complete CLI transcripts. |
| `resources` | R4: prepared source-resource copy and three synthetic excluded extras; records that verification accepts all three. |
| `http` | Six actual loopback HTTP requests, synthetic credentials/evidence, local review preview, parity and non-Git file snapshot checks. Needs permission to bind `127.0.0.1`; all non-loopback outbound connections are blocked. No live provider. |
| `accounting` | Read-only reconciliation of manifests, source objects, raw XML, historical failures, refs and counts. |
| `semantics` | Accounting plus source excerpts and reviewer assessments for 104 historical failures, seven replacements, and an inventory of all 393 original files. |
| `foundation-tests` | The exact preserved 41-case focused selection, with a new pytest fixture/cache/log/XML destination. |
| `authority-tests` | The exact preserved 47-case selection, including the pinned local Muse prerequisite. |

A finding probe's exit 0 means that its reproduction completed; it does not mean
the product met the requirement. Read its recorded assertions/outcomes. The
wrapper writes `reproduction.json` with actual arguments, runtime, worktree status, log
paths and exit status. No wrapper run overwrites the original review outputs.

The exact original pytest arguments and environment overrides are recorded in
[foundation/focused-command.json](foundation/focused-command.json) and
[authority/focused-command.json](authority/focused-command.json). The authority
selection requires the locally pinned Muse interpreter at
`/Users/aaronrenecarvajal/.local/share/muse/venv/bin/python`; do not silently
substitute a different prerequisite or fetch one. The Python 3.11 dependency cell
remains unresolved regardless of these Python 3.14 results.

## Reading intermediate evidence

The original HTTP script and `-r2` runs contain reviewer-fixture setup errors.
`-r3` corrected the fixture and encountered the sandbox's loopback bind denial.
`-r4` ran in a new fixture with loopback permission and passed all six requests.
All four scripts, logs and JSON results are preserved. None repaired production.

The semantic map, `evidence-review-findings.json`, and `coverage-notes.txt` were
produced before the final HTTP supplement. Their suggested HTTP evidence finding
describes the original FPR-4 selection. The final report incorporates the separate
successful supplement and does not retain it as a seventh implementation finding.
Other intermediate subreview notes use local labels; the report's FPR5-R1 through
FPR5-R6 identifiers and severities are the consolidated independent verdict.

Original FPR-4 failures remain in `docs/validation/fpr4`; the review's references
and row mappings point to that preserved evidence. The 1,207-pass/one-failure
combined execution and separate two-pass successor run must not be relabelled as
an all-green combined execution. None of the fixture checks is a new integrated
pilot, native GUI/host acceptance, external delivery, or release action.

The relocation wrapper was smoke-checked with `redirect` in a second fresh parent.
Its [command/result](wrapper-smoke.json) and [raw log](wrapper-smoke.log) are
preserved separately. This verifies the helper and repeats R1's synthetic probe;
it adds no new pytest cases to the reported counts.
