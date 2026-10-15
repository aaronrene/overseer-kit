# FPR5-R3 and FPR5-R5 author repair evidence

These are bounded repair-author results, not independent adjudication or release
acceptance. The original FINDINGS verdict, reproduction scripts, raw failures
and historical test files remain unchanged. The starting source is
`4c62c17cff6c606a5e1ddf565e12353973b3bcad`, runtime
`bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`.

## Repairs

R3 retains unrecorded, preserved and recorded-modified portable assets during
schema migration, including owner executable modes and content identical to the
kit. The proposed updates omit those assets, the protected inventory captures
their exact bytes/modes, and the existing footprint writer records
`origin: preserved`. Collision paths outside the usual rules/skills directories
are explicitly protected too. Exact operational-launcher validation remains.

The same reviewed plan backs up owner collision bytes/modes as well as the old
configuration and modified lock. Apply/resume recomputes classification from the
reviewed originals and saved originals after partial progress; protected owner
assets need not equal kit bytes. The existing confinement, digest expectations,
captured-context checks, directory lock, config-last writes and partial-progress
report remain. Repeated resume and ordinary sync retain owner assets and can be
no-ops. The operation is still per-file atomic, not a filesystem transaction.

R5 parses existing canonical NEXT and validates every present entry with its own
explicit configured lane. A schema-1 NEXT remains schema 1 when more lanes are
configured. A schema-3 collection retains every existing entry and prompt.
Initialization selects no task, adds no missing lane entry and rewrites no NEXT
bytes. The ordinary NEXT reader still displays missing lanes. An unselected
entry with a wrong branch still refuses initialization before writes.

## Evidence and reproduction

All runs use this installation's conventional `.venv` (Python 3.14.4), with
bytecode and pytest plugin autoload disabled, cacheprovider disabled, and fresh
fixtures under `/private/tmp`. Every `*-command.json` contains exact argv,
environment overrides, fixture parent, observed runtime and owned source hashes.
Use a new fixture parent and new output filenames when repeating a command.
No provider, external network, real consumer, live hook, delivery or pilot ran.

| Run | Result and meaning |
| --- | --- |
| `before` | 16 failed / 2 passed among the initial 18 requirement cases, on unchanged original production and runtime. The two passing cases are collision drift refusals. |
| `candidate-after` | 17 passed / 1 failed. The failure is a captured-context refusal during concurrent runtime modification by another authorized repair; owned foundation files were unchanged. Start/end runtime values are recorded. |
| `candidate-portability` | 3 failed / 2 passed on the first candidate: additional cases exposed missing protected snapshots for root policy/reference paths and a recorded owner mode-only change. The correction is included in the repaired source. These are candidate failures, not relabelled original-source results. |
| `after-integrated` | 150 passed / 1 failed in 457.55 seconds, zero errors/skips: all 23 new requirement cases and 127 affected cases pass. The sole failure is the preserved obsolete command-scope assertion below. Complete affected migration, lane, init-preservation, captured-context and command files were included. |

The integrated invocation includes the preserved historical
`tests/v1/test_commands.py::test_unsupported_commands_cannot_run` assertion in
its raw output. Its expectation that restored commands remain unsupported was
already replaced under FPR-4's documented current contract. It is not changed or
treated as a new repair requirement. The root repair's current-contract combined
selection separately applies the previously documented replacement.

The root closeout records the final complete runtime after any other agent's
subsequent transport correction; this run records its own source/runtime
boundary and does not borrow the later digest.
Runtime remained
`0e0260d272063e4572cabe8bda19f3bafd7d23500936ab1a879024cbdc8143a5`
throughout `after-integrated`; owned source/test hashes were also unchanged.

The five additional portability cases extend the initial regression file; its
exact before/after hashes and original 18-case execution remain recorded.
`results.json` distinguishes original baseline, intermediate candidate results,
and repaired-source results instead of summing overlapping executions.

The declared Python 3.11 cell, named automatic host/version acceptance,
platform/distribution decisions and separately authorized new integrated pilot
remain outside these fixture results. One final independent adjudication and a
separate owner release decision remain reserved.
