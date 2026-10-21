# OK-NEXT-MODEL freeze — the NEXT model line is a recommendation (kit finding F9)

```yaml
phase: OK-NEXT-MODEL-a
outputs:
- id: ok-next-model-freeze
  path: docs/evidence/B02/overseer-next-model-select-20261020/FREEZE.md
  frozen: true
  notes: Single-lane NEXT may name any strictly validated model label; context.model stays the default; F9.
frozen_inputs:
- id: kit-source-head
  path: fix/knowtation-migration-compat-20261020 at 99e2e5bcfd6de0eb45b4f48872653f396aaa9850
  notes: Only docs changed after 30f5cb4 (docs/OVERSEER-HANDOVER.md, docs/ROADMAP.md, docs/reviews/MIGRATION-COMPAT-RC11-INDEPENDENT-REVIEW.md).
- id: installed-runtime
  path: PREPARED-RUNTIMES/knowtation-bornfree-compat-rc11-20261020
  notes: Built from 30f5cb4; runtime sha256 309ac668063f6564f36fa063417210e34c9f40872390f6ad60bae9769631968c. Stays unchanged as rollback.
- id: rc11-rebind-receipt
  path: docs/evidence/B02/overseer-rc11-rebind-20261020/README.md
  notes: Current binding; backups under .overseer/local/rebind-3899dd65.
- id: c2-owner-disposition
  path: docs/evidence/B02/c2-closure-encoding-cross-model-review-20261020/OWNER-DISPOSITION.md
  notes: Revision step must be authored by OpenAI Codex; later review by Claude Opus.
- id: saved-revision-prompt
  path: docs/evidence/B02/c2-closure-encoding-cross-model-review-20261020/NEXT-PROMPT.txt
  notes: sha256 e50ccab8203646b0941675f1a3ab2fcacbe57fd790e3beb4ea867895d5fdebd0; no binding lines; ends with a newline.
- id: superseded-allowlist-freeze
  path: docs/evidence/B02/overseer-next-model-select-20261020/SUPERSEDED-FREEZE-ALLOWLIST.md
  notes: sha256 90324289919c92d5c5782f50056320ef1a78146fcd905dac7723b8ba8a36a15e; the owner rejected the allowlist design on 2026-10-20. Not to be built.
review_stamp:
  gate: mechanical
  reviewed_at: '2026-10-21T00:53:56Z'
  mechanical_verdict: pass
  produced_by: checklist_engine
  provider_kind: rule_engine
  reviewer_mode: agent
  reviewer_model: null
  reviewer_provider: local
  checklist_ids:
  - C1
  - C2
  - C3
  - C4
  - C5
  - C6
  - C7
  - C8
  checklist_source: builtin
  findings_count: 0
  override_applied: false
  kit_version: 1.0.0.dev1
  artifact_digest: sha256:a92f02fb070b686362c35f9001e16b0113e563c1f889f1c4a0df6b6a40f31c1e
```

**Status.** frozen: true. This document is the ground truth for two Auto steps:

- **OK-NEXT-MODEL-b** (kit roadmap N1b): build and test the kit change, and prepare a
  new runtime. It runs in a kit worktree and does not touch Knowtation.
- **OK-NEXT-MODEL-c** (kit roadmap N1c): move Knowtation onto that runtime and publish
  the saved Codex revision prompt. It runs in Knowtation.

Neither step redesigns anything. If anything here is wrong or incomplete, the step
stops and reports; it does not improvise.

**Owner decision (2026-10-20).** The owner chose "recommend, don't force". The model
named in NEXT is a suggestion shown to the person, who picks the model they run in
Cursor, Codex or anywhere else. No config command or per-model list exists. The
allowlist freeze (`SUPERSEDED-FREEZE-ALLOWLIST.md`) is superseded in full, and so is
the earlier `PROMPT-B-AUTO.txt` text.

**Authorship (honest record).** The session that wrote this freeze reports itself as
Anthropic Claude Opus 5.5 running in Cursor. The independent review N1-R must use a
model other than this author and other than the step-b builder.

**What the configured freeze review is.** Knowtation's freeze review is the local
rule engine (`freeze_contract.reviewer.provider: local`). A pass from it is a
mechanical check of this document's shape. It is not an independent semantic review.
Independent review of the built code remains N1-R, before any PR.

**Citation discipline.** Every claim about current behavior below cites file+line in
the kit source at `99e2e5b`. Its `cli/` and `tests/` trees are byte-identical to
`30f5cb4` (section 1). Every review finding against this freeze must also cite
file+line.

**Path notation.** Paths are written relative to `$HOME`, the owner's home directory,
which contains both `knowtation/` and `OVERSEER_KIT/`. Step c verifies that
`$HOME/knowtation` is the physical root recorded as `repo.root` in
`$HOME/knowtation/.overseer/config.yaml` before it uses these names:

| Name | Value |
| --- | --- |
| `KN` | `$HOME/knowtation` (repository ID `6df95ecb-f668-5cf6-adf1-384baf3e6246`) |
| `KIT_SRC` | `$HOME/OVERSEER_KIT/overseer-kit-knowtation-compat-20261020` |
| `WT` | `$HOME/OVERSEER_KIT/overseer-kit-next-model-select-20261020` (new worktree) |
| `OLD_RT` | `$HOME/OVERSEER_KIT/PREPARED-RUNTIMES/knowtation-bornfree-compat-rc11-20261020` |
| `NEW_RT` | `$HOME/OVERSEER_KIT/PREPARED-RUNTIMES/knowtation-next-model-select-20261020` (new) |
| `RUN` | `$HOME/OVERSEER_KIT/RECOVERY-RUNS/knowtation-next-model-select-20261020` (new) |
| `MUSE_PY` | `$HOME/.local/share/muse/venv/bin/python3.14` |
| `CODEX` | `OpenAI Codex (latest GPT model, high reasoning)` |
| `OPUS` | `Anthropic Claude Opus, thinking enabled` |

---

## 1. Verified starting state (2026-10-20, read-only)

| Item | Value |
| --- | --- |
| Frozen base commit | `99e2e5bcfd6de0eb45b4f48872653f396aaa9850`, the head of `fix/knowtation-migration-compat-20261020` when this freeze was written |
| Commits after `30f5cb4` up to the base | `a7ae00c`, `d96c3e1`, `3254b41`, `99e2e5b`; `git diff --stat 30f5cb4 99e2e5b` lists only the three docs files in the declaration |
| `KIT_SRC` working tree | one untracked file, `docs/reviews/MIGRATION-COMPAT-RC11-R1-SPEC.md`, from a concurrent R-track session. Not part of this work; never touched. The fix branch may keep moving; steps b and c use the pinned commit, not the branch tip |
| Planned names | branch `feat/next-model-select-20261020`, `WT`, `NEW_RT` and `RUN` do not exist |
| Installed runtime | `OLD_RT`, version `1.0.0.dev1`, sha256 `309ac668063f6564f36fa063417210e34c9f40872390f6ad60bae9769631968c` |
| `.overseer/config.yaml` | `72c2f1fcc77dbda449295d050c81378c02a64e87439b383582e8263090a322fd`, mode 0644, tracked binding |
| `.overseer/version.lock` | `0b63a02369088e8707d683dd174df459fc9e7b189e281c9bfed9b8672ab7c89e`, mode 0644 |
| `.overseer/bin/ok` | `0b9ddb50f7078104ecf2c5dd043974bf38e6863babbedbb1df1e7c3c6e1c8f93`, mode 0755 |
| `docs/NEXT.md` | `1279cdeef779e5089b719d3f07229c409657995c7d84dfeddd0c2c9a6cdbc0fd`, mode 0644, schema 2, action `C2-CROSS-MODEL-REVIEW-1` (completed; must not be re-run) |
| Context | lane `product`, model `OPUS`; one declared lane (`docs.lanes.product`) |
| Muse | branch `docs/scooling-brain-pair-relay`, head `sha256:d0eb71ed2001f76763b3eb37c945b86719ea36191dccadd4c4057315a723255f`, runtime 0.2.1rc11 at `MUSE_PY`; staging holds unrelated earlier work |
| Bound checks | `ok next --lane product` valid; `ok status --check-footprint --exit-code` exit 0 |
| Rebind backups present | `.overseer/local/rebind-3899dd654a515543ccd3f82a806f1971acde8e38cc401297a3b75e3548b86560/.overseer/{config.yaml,version.lock,bin/ok}` |
| Migration package present | `.overseer/migrations/78b5ebbc7e899318bbb1b12151cdd4c53154e78973fd7ce45f87adaaa2c6a38f/` |

## 2. Problem, verified in source

- `cli/v1.py:273-274`: with one declared lane, any NEXT whose `model` differs from
  `config.context.model` refuses `next_model_mismatch`. The check is inside
  `validate_next` (`cli/v1.py:262-302`), which runs on publication
  (`cli/v1.py:336`, `cli/product_next.py:209`), on every read
  (`cli/product_next.py:131-132`, `cli/product_next.py:161`) and on existing-config
  init (`cli/v1.py:440-442`).
- `next-write` already requires an explicit `--model` (`cli/main.py:159-163`). The
  `context.model` fallback at `cli/v1.py:323` therefore applies only to callers that
  build arguments in-process.
- Multi-lane NEXT already accepts any model that passes the general label check
  (`cli/v1.py:82-85`, `cli/v1.py:240-241`). Only explicit `--model` expectations are
  compared (`cli/v1.py:207-211`).
- History: the pin arrived with the v1 rebuild on 2026-10-14 (`d8f10d8`, NEXT meta
  built from `context`). It was kept as an explicit single-lane check in `695444f`,
  which added per-lane models for multi-lane. The only recorded reason is a test
  expectation (`tests/v1/test_commands.py:68-75`, parameter `('model','Other Model')`,
  and `tests/muse/test_handoffs.py:123-131`, parameter `('model', 'Other')`). No
  design decision records why single-lane must pin the model.

## 3. Options compared and decision

| | (A) Recommendation: any strictly validated label | (B) Owner-maintained allowlist (superseded freeze) |
| --- | --- | --- |
| What the owner does to use a new model | Nothing; the agent names it with `next-write --model` | Two `next-models` commands (preview, apply) per new model |
| New config key or command | None | `next_models` key and `ok next-models` command |
| Code size | One condition in `cli/v1.py` plus a label validator | New module, config schema, CLI wiring |
| Hand-edited label in NEXT | Displayed if it passes the strict grammar; `--expect-next` detects any byte change | Displayed if it is another approved label; `--expect-next` detects any byte change |
| Multi-lane behavior | Unchanged | Unchanged without a list |

**Security comparison, corrected.** The superseded freeze called the hand-edit
property of (A) a "concrete defect". That overstated it. `prompt_sha256` covers only
the prompt body (`cli/v1.py:247-248`), and that digest is stored in the same file. Any
process that can rewrite `docs/NEXT.md` can therefore also rewrite the prompt and its
digest, under both designs and under today's pin. The pin only catches a careless
edit of the model line alone. A model label grants no permission: no command reads
it to permit, skip or select any check, write, transport or provider call. Under
every design, the real integrity check on NEXT is `--expect-next` against the digest
that `next-write` reported (`cli/v1.py:276-277`).

**Decision: option (A)**, the owner's choice. It restores "recommend, don't force"
for single-lane repositories, gives single- and multi-lane repositories the same
model freedom, and adds no ongoing steps.

## 4. Security rationale

1. Model labels are routing hints shown to the person. They confer no authority.
   This freeze adds no code path that reads a label to make a decision.
2. Injection is closed by a strict ASCII grammar (5.1) for every single-lane label
   that differs from `context.model`, enforced on write and read in one place (5.2).
   No newline, other line separator, control character, bidirectional override,
   colon, backtick, quote, `#`, `<`, `>`, `$`, `;`, `|` or leading, trailing or double
   space can appear. Such a label can neither start a new line in rendered output
   (`cli/v1.py:305-311`) nor imitate a binding line (`Model: …`,
   `<!-- overseer-next:… -->`). Values arrive as argv (never through a shell) and are
   written only with `yaml.safe_dump` (`cli/v1.py:73-74`).
3. Every other writer and reader check stays as it is (5.4).
4. Threat-model boundary, unchanged: the kit is cooperative against same-user
   processes (`cli/v1_io.py:74-79`). This freeze does not claim more.
5. Pre-existing gap, recorded and not fixed here: the general `label()` check
   (`cli/v1.py:82-85`) admits DEL, C1 controls such as U+0085, U+2028 and
   bidirectional overrides. It still governs `context.model` and multi-lane labels.
   Tightening it would change behavior for existing multi-lane and default labels.
   It is recorded as kit finding **F11 (Low, pre-existing)** for the H1 hardening row.

## 5. WHAT — behavior

### 5.1 Model label grammar

```text
MODEL_LABEL = re.compile(r"[A-Za-z][A-Za-z0-9._,()+/-]*(?: [A-Za-z0-9._,()+/-]+)*\Z")
MODEL_LABEL_MAX = 120
```

`model_label(value)` returns `value` when it is a `str` of 1 to 120 characters that
fully matches `MODEL_LABEL`; otherwise it raises `Refusal("model_label_invalid")`. In
plain terms: ASCII only, first character a letter, single spaces between words, and
the punctuation `. _ , ( ) + / -`. It accepts `CODEX`, `OPUS`, `GPT-6 Astra`,
`Cursor Auto` and `Fixture Reviewer`.

### 5.2 The NEXT model rule (read and write, one place)

In `validate_next`, lines `cli/v1.py:273-274` become exactly:

```python
    if len(config['docs']['lanes']) == 1 and meta['model'] != config['context']['model']:
        model_label(meta['model'])
```

| Lanes declared | NEXT `model` | Result |
| --- | --- | --- |
| 1 | equal to `context.model` | accepted (unchanged; general `label()` only) |
| 1 | different, passes `model_label` | **accepted** (was `next_model_mismatch`) |
| 1 | different, fails `model_label` | refused `model_label_invalid` |
| more than 1 | any | unchanged (general `label()` only) |

The rule lives in `validate_next`, so it governs every path the same way:
single and batch `next-write` (both validate the payload before writing,
`cli/v1.py:336`, `cli/product_next.py:209`), `ok next`, `status` (`next_error`),
`hook`, `governance-sync --print-next` and existing-config `init`. A refused write
leaves `docs/NEXT.md` untouched, because validation runs before the lock and atomic
write (`cli/v1.py:337-348`).

Existing consumers are unaffected: every NEXT that today's runtime accepts in a
single-lane repository has `model == context.model`, so the new branch never runs for
it. `next_model_mismatch` is no longer raised anywhere.

### 5.3 Recording and display

- NEXT stores the label unchanged in its frontmatter `model:` field (`cli/v1.py:73-74`).
- `ok next` shows it on the existing `Model: <label>` line (`cli/v1.py:305-311`). Text
  and JSON output shapes are unchanged.
- `context.model` stays the saved default. `adopt` and the Muse rebind still require
  `--model` to equal it (`cli/product_authority.py:81-83`, `cli/product_authority.py:176-178`).
  No command changes it, and none needs to.
- A label hand-changed to another valid label is displayed, as it is in multi-lane
  repositories today. `ok next --expect-next <digest reported by next-write>` refuses
  `next_digest_mismatch` on any byte change (`cli/v1.py:276-277`). Knowtation's
  receipt records the published digest for that purpose.

### 5.4 Retained checks (unchanged code paths)

Only `cli/v1.py:273-274` changes inside the NEXT reader and writer. Each of these
stays byte-identical in behavior, and the section 7 regression tests re-assert them:

- repository identity and root (`cli/v1.py:269-272`) and launcher binding
  (`cli/v1.py:124-133`);
- branch and lane (`cli/v1.py:269-272`, `cli/product_next.py:60-71`);
- Muse authority and source (`cli/v1.py:266-267`), explicit `--vcs muse` and current
  `--base-head` (`cli/v1.py:326-333`), and stale head (`cli/v1.py:278-301`);
- expected NEXT digest (`cli/product_next.py:93-94`, `cli/v1.py:276-277`);
- prompt validation, binding-line rejection and lane-delimiter rejection
  (`cli/v1.py:252-259`, `cli/product_next.py:89-91`);
- expectations for `--repo-id`, `--branch`, `--lane`, `--model`, `--action-id` and
  `--action-kind` (`cli/v1.py:207-211`);
- context recheck, the advisory `docs/` lock and the atomic CAS write
  (`cli/v1.py:337-348`);
- duplicate selector refusal (`cli/main.py:145-154`) and the explicit-model
  requirement (`cli/main.py:159-163`).

## 6. HOW — exact files (kit, branch `feat/next-model-select-20261020`)

| File | Change |
| --- | --- |
| `cli/v1.py` | After `TOKEN` (line 27) add `MODEL_LABEL` and `MODEL_LABEL_MAX` (5.1). After `label()` (lines 82-85) add `model_label(value)` with a docstring that states 5.1 and the single-lane rule in 5.2. Replace lines 273-274 with the two lines in 5.2. No other change. |
| `tests/v1/test_commands.py` | Line 69: remove only the `('model','Other Model'), ` parameter from `test_writer_binding_checks`. The reader parametrization at line 79 stays unchanged, because that is an expectation check. |
| `tests/muse/test_handoffs.py` | Line 123: remove only the `('model', 'Other'), ` parameter from `test_muse_writer_rejects_wrong_context_without_writes`. |
| `tests/v1/test_next_model_suggestion.py` | New: tiers 1–7 for Git (section 7), with module and function docstrings. |
| `tests/muse/test_next_model_suggestion_muse.py` | New: Muse end-to-end and rebind tests (section 7, tier 3). |
| `docs/NEXT-MODEL-SELECTION.md` | New operator note: the model line is a recommendation, the 5.2 table, the grammar, the hand-edit residual and `--expect-next`, and rollback behavior on an older runtime (section 10). |
| `docs/reviews/OK-NEXT-MODEL-FREEZE.md` | Byte copy of this file after its review stamp. |
| `docs/ROADMAP.md`, `docs/OVERSEER-HANDOVER.md` | Paired update in step b's commit 2 (section 8). |

Not changed: any other `cli/` file, `cursor/`, `templates/`, `policy/`, `adapters/`,
`tools/`, the kit's own `docs/NEXT.md`, and `docs/validation/` (historical records,
including `docs/validation/FPR-2-AUTHORITY.md:117-118`). Shipped consumer assets
therefore stay identical. `cli/v1.py` is already in the runtime digest
(`cli/v1.py:28-43`), so the runtime digest changes and a new runtime is required.

The two existing test edits above are the only edits to existing tests. If any other
existing test fails because of the 5.2 change, step b stops and reports. It does not
edit that test.

## 7. Tests — seven-tier matrix (synthetic fixtures only)

Fixtures: the Git single-lane `repo` fixture (`tests/v1/conftest.py:27-32`; its
`context.model` is `GPT-6 Astra` and `write_action` is at `tests/v1/conftest.py:51-62`);
the multi-lane helper pattern from `tests/fpr2/test_lanes.py:13-19`; and the real-Muse
fixtures (`--muse-python "$MUSE_PY"`; `muse_root`, `muse` and `stale_binding`,
`tests/muse/test_runtime_rebind.py:18-40`). No test reads Knowtation, a vault, private
configuration or credentials. Every new test module and test function has a docstring.

1. **Unit.** `model_label` accepts `CODEX`, `OPUS`, `GPT-6 Astra`, `Cursor Auto` and
   a 120-character label, returning the same object. It refuses non-`str` values
   (`None`, `1`, `b"x"`) and the whole security table in tier 7 with
   `model_label_invalid`. `MODEL_LABEL_MAX == 120`.
2. **Integration** (`repo` fixture, `cli/ok` subprocess):
   - `next-write --model CODEX` exits 0. `ok next` shows `Model: OpenAI Codex (latest
     GPT model, high reasoning)`, and `ok next --json` reports `next.model == CODEX`.
   - `ok next --model CODEX` exits 0. `ok next --model 'GPT-6 Astra'` refuses
     `expected_model_mismatch`.
   - A single-lane `--batch-file` entry with model CODEX publishes. An entry with
     `Codex  Two` (double space) refuses `model_label_invalid`, and NEXT is unchanged.
   - `init` (existing config) and `sync --hooks` exit 0 with a CODEX NEXT present,
     leaving NEXT bytes unchanged.
   - A default label outside the strict grammar still works. Initialize a fresh
     seeded repository with `init --model 'Modèle par défaut'` (it passes the general
     `label()`). Publishing with that exact model exits 0; publishing `--model
     'Modèle 2'` refuses `model_label_invalid`.
   - Multi-lane is unchanged. With two lanes (the `tests/fpr2/test_lanes.py:13-19`
     pattern), a lane entry with model `Modèle` publishes and reads as valid.
3. **End-to-end.**
   - Git (`repo` fixture): publish CODEX. Read it from a fresh process with cwd `/`
     through `.overseer/bin/ok`. Publish the default-model successor with the
     reported `--expect-next`, then read again. `status --json` exits 0 (the
     assertion of `tests/v1/conftest.py:45-48`).
   - Muse, in `tests/muse/test_next_model_suggestion_muse.py`, on `muse_root` after an
     init and one Muse commit: publish CODEX with explicit `--vcs muse --base-head`
     and read it. Publish the default-model successor and read it.
   - Muse rebind, on `stale_binding`: preview and apply `adopt --rebind-muse-runtime`
     exactly as `tests/muse/test_runtime_rebind.py:58-80` does. Then publish CODEX
     with explicit `--vcs muse --base-head --expect-next absent`. A fresh process
     with cwd `/`, through `.overseer/bin/ok next`, shows `Model: <CODEX>`.
     `status --check-footprint --json` reports footprint integrity and coverage ok.
4. **Stress.**
   - 50 alternating CODEX/default publications on `repo`, each with the exact prior
     `--expect-next`. After each one `ok next` is valid and shows the model just
     written.
   - 20 iterations of two `next-write` processes, started together with the same
     `--expect-next`, one naming CODEX and one the default (the pattern of
     `tests/v1/test_integrity.py:65-78`). Each iteration ends with sorted exit codes
     `[0, 2]`, the loser's stderr containing `stale_write`, NEXT's model equal to the
     winner's, and no `docs/.NEXT.md.*` temporary files.
5. **Data-integrity.**
   - A successful CODEX write changes only `docs/NEXT.md` in a full-tree byte-and-mode
     fingerprint (the `fingerprint` helper pattern at `tests/v1/test_commands.py:13-15`).
   - A refused invalid-label write changes nothing: NEXT bytes and mode,
     `.overseer/config.yaml`, `.overseer/version.lock` and `.overseer/bin/ok` stay
     byte-identical, with no temporary files.
   - The published `prompt_sha256` equals the SHA-256 of the prompt file, and the
     prompt body rendered by `ok next` equals the file content.
   - `status --json` exits 0 after both.
6. **Performance.** Ten `ok next` reads of a CODEX NEXT complete in under 10 s (the
   bound of `tests/v1/test_integrity.py:81-84`). 100,000 in-process `model_label`
   calls on CODEX complete in under 1.0 s.
7. **Security.**
   - Reject table, refused by `model_label` with `model_label_invalid`: empty, `" x"`,
     `"x "`, `"a  b"`, `\n`, `\r`, `\t`, NUL, DEL, U+0085, U+2028, U+202E, `Modèle`,
     `1abc`, `-x`, 121 characters, `Model: x`, `a:b`, three backticks,
     `<!-- overseer-next:x -->`, `<x>`, `$(id)`, `a;b`, `a|b`, both quote characters
     and `#x`.
   - Through `next-write --model=<value>` on `repo`, for every table value except
     empty and NUL (argv cannot carry them): exit 2, empty stdout, NEXT unchanged.
     The stderr refusal is asserted as follows:
     - `label_invalid` for the C0 values `\n`, `\r` and `\t`, which `cli/v1.py:82-85`
       refuses first;
     - no specific code for U+0085, which PyYAML does not round-trip (verified
       2026-10-20: `safe_dump` then `safe_load` of `a\x85b` returns `a b`), so the
       decoded value differs from the request and a different refusal fires first;
       this encoder behavior belongs to F11;
     - `model_label_invalid` for all other values.
   - Hand edits to a valid CODEX NEXT, re-encoded with `v1.encode` so the frontmatter
     and prompt digest stay valid:
     - model changed to `Codex\u2028Lane: other` refuses `model_label_invalid` on
       `ok next` and `ok next --json`; `status --json` exits 1 with that refusal in
       `next_error`;
     - model changed to `OpenAI Codex` is displayed, but `ok next --expect-next
       <published digest>` refuses `next_digest_mismatch`.
   - Regression with a CODEX NEXT present: `next-write` still refuses a wrong
     `--repo-id`, `--branch` and `--lane`, `--action-id bad/action`, `--action-kind
     deploy`, a stale `--expect-next`, an absolute `--prompt-file` (`path_invalid`)
     and a prompt containing a `Model:` or `Lane:` line. NEXT is unchanged each time.
   - Muse regression: the remaining `test_muse_writer_rejects_wrong_context_without_writes`
     parameters still refuse. The new Muse module asserts that CODEX without `--vcs`
     or `--base-head` refuses `muse_writer_requires_explicit_vcs_and_base_head`.

**Runs (step b, from `WT`, with `WT/.venv/bin/python3 -m pytest`, `-p no:cacheprovider`
and a disposable `--basetemp "$(mktemp -d)"`):**

- Baseline before any edit, at `99e2e5b`: `tests/v1`, `tests/fpr1`, `tests/fpr2`,
  `tests/fpr3`, `tests/fpr4`, `tests/fpr5`,
  `tests/integration/test_legacy_migration_compat.py`,
  `tests/performance/test_print_next_perf.py`, and `tests/muse` with `--muse-python
  "$MUSE_PY"`. Record pass, fail and error counts and every failure ID.
- After the change: the two new modules plus the same groups. Any failure absent
  from the baseline is a stop condition. Baseline failures are reported unchanged and
  never relabelled.
- Then run `/build-verification-review` against this freeze from a separate chat.
  DONE only on pass.

## 8. Step b — build and a new prepared runtime (kit only)

```sh
git -C "$KIT_SRC" worktree add -b feat/next-model-select-20261020 "$WT" 99e2e5bcfd6de0eb45b4f48872653f396aaa9850
cp -a "$KIT_SRC/.venv" "$WT/.venv"
```

A separate worktree keeps `KIT_SRC`, where R-track work happens, untouched. Then
implement and test. Make **commit 1** in `WT` containing exactly the section 6 code,
test and docs files except ROADMAP and HANDOVER. It is a local commit only.

Prepare the runtime from commit 1, with `git -C "$WT" status --porcelain` empty (the
archive tool includes untracked files):

```sh
mkdir "$RUN"
"$WT/.venv/bin/python3" -I -B "$WT/tools/ci/source_package.py" build --output "$RUN/source.tar.gz"
"$WT/.venv/bin/python3" -I -B "$WT/tools/ci/source_package.py" unpack --archive "$RUN/source.tar.gz" --destination "$NEW_RT"
cp -a "$OLD_RT/.venv" "$NEW_RT/.venv"
"$NEW_RT/.venv/bin/python3" -I -B -c "import yaml, cryptography"
```

The `.venv` copy is the same method used for `OLD_RT`. Write `RUN/runtime.json` with:

- the commit 1 SHA and its parent (must be `99e2e5b…`);
- the archive sha256, manifest sha256 and file count;
- the `NEW_RT` runtime sha256, computed by importing `cli.v1` from `NEW_RT` and
  calling `runtime()`;
- the baseline and after test counts.

Write `RUN/build-verification.json` with the build verification verdict, its round,
its reviewer session and model, and its ledger reference. `OLD_RT` is never modified.

**Commit 2** (docs only): update the kit's `docs/ROADMAP.md` and
`docs/OVERSEER-HANDOVER.md` together. Record N1a pass with this freeze's sha256, and
N1b built with the commit 1 SHA and runtime digest. Name N1c (Knowtation install) as
next, then N1-R, and queue F11 for H1. Docs are not runtime files, so `NEW_RT` still
matches commit 1. No push, PR, merge or release. Step b does not read or write
anything in `KN` except this freeze.

## 9. Step c — moving Knowtation onto the new runtime

**Entry checks** (stop on any failure):

- this file's sha256 equals the one step a reported;
- `RUN/runtime.json` exists and its commit's parent is `99e2e5b…`;
- `RUN/build-verification.json` records verdict `pass`;
- `NEW_RT` exists and its computed `runtime()` equals the recorded digest.

**Preflight** (stop on any difference from section 1): check the digests of config,
lock, launcher, NEXT and the prompt file; the Muse branch and head; and that
`ok status --check-footprint --exit-code` exits 0. Copy `.overseer/config.yaml`,
`.overseer/version.lock`, `.overseer/bin/ok` and `docs/NEXT.md` into `RUN/before/`.

Record a byte-and-mode snapshot of these paths:

- every path that `ok status --json` lists under `preserved_inventory`;
- `.gitignore`, `.museignore`, `.cursor/hooks.json` and `AGENTS.md`;
- `.overseer/honesty/VERDICT-LEDGER.jsonl`.

Every snapshot path must be byte- and mode-identical after 9.2 and after 9.3.

**9.1 Rebind dry run**, from the new runtime:

```sh
"$NEW_RT/cli/ok" -C "$KN" adopt --rebind-muse-runtime \
  --muse-python "$MUSE_PY" \
  --repo-id 6df95ecb-f668-5cf6-adf1-384baf3e6246 \
  --branch docs/scooling-brain-pair-relay \
  --base-head sha256:d0eb71ed2001f76763b3eb37c945b86719ea36191dccadd4c4057315a723255f \
  --lane product --model 'Anthropic Claude Opus, thinking enabled' \
  --expect-config 72c2f1fcc77dbda449295d050c81378c02a64e87439b383582e8263090a322fd \
  --tracked-bindings preserve --dry-run --json > "$RUN/rebind-preview.json"
```

Accept the preview only if all of these hold:

- `operation` is `same-source-runtime-rebind` and `context` is `{lane: product, model: OPUS}`;
- `before_binding == after_binding` (Muse rc11 unchanged);
- `before_runtime` is `OLD_RT`/`309ac668…`, and `after_runtime` is `NEW_RT` with the
  digest from `RUN/runtime.json`;
- `assets` are exactly these six paths:
  - `.overseer/local/rebind-72c2f1fcc77dbda449295d050c81378c02a64e87439b383582e8263090a322fd/.overseer/{config.yaml,bin/ok,version.lock}`
    (absent before; equal to the current bytes after);
  - `.overseer/bin/ok`, `.overseer/version.lock` and `.overseer/config.yaml`;
- the normalized config differs from the current config only at `runtime.root` and
  `runtime.sha256`;
- the launcher differs only in the runtime path, and the lock differs only in the
  launcher row's sha256 and `footprint_digest`;
- NEXT is reported as preserved (`cli/product_authority.py:130`), and
  `tracked_binding_choice` is `preserve`.

**9.2 Apply:** repeat 9.1 without `--dry-run`, adding `--expect-rebind <rebind_sha256>`.
Save the output to `RUN/rebind-apply.json`. Then, from fresh processes with cwd `/` and
with cwd `$TMPDIR`, check two things:

- `"$KN/.overseer/bin/ok" -C "$KN" status --check-footprint --exit-code` exits 0 with
  runtime `NEW_RT`;
- `ok next --lane product` output is byte-identical to its preflight output.

**9.3 Publish the saved prompt** (verify prompt file sha256 `e50ccab8…` first):

```sh
"$KN/.overseer/bin/ok" -C "$KN" next-write \
  --repo-id 6df95ecb-f668-5cf6-adf1-384baf3e6246 --branch docs/scooling-brain-pair-relay \
  --lane product --model 'OpenAI Codex (latest GPT model, high reasoning)' \
  --action-id C2-PROPOSAL-REVISION-1 --action-kind plan --vcs muse \
  --base-head sha256:d0eb71ed2001f76763b3eb37c945b86719ea36191dccadd4c4057315a723255f \
  --expect-next 1279cdeef779e5089b719d3f07229c409657995c7d84dfeddd0c2c9a6cdbc0fd \
  --prompt-file docs/evidence/B02/c2-closure-encoding-cross-model-review-20261020/NEXT-PROMPT.txt
```

Read it back from fresh processes with cwd `/` and with cwd `$TMPDIR` using
`ok next --lane product`. The output must show:

- `Model: OpenAI Codex (latest GPT model, high reasoning)`;
- action `C2-PROPOSAL-REVISION-1` and kind `plan`;
- `prompt_sha256` `e50ccab8…`.

Then `ok next --lane product --model 'OpenAI Codex (latest GPT model, high
reasoning)' --expect-next <new digest>` must exit 0, and `status
--check-footprint --exit-code` must exit 0.

The later Opus review (`C2-CROSS-MODEL-REVIEW-2`) is published by the Codex session
with `--model 'Anthropic Claude Opus, thinking enabled'`. No config change happens at
any point.

**9.4 Receipt and handoffs.** Write `README.md` beside this freeze. It records:

- every before/after digest and the rebind plan digest;
- the NEXT digest published in 9.3;
- the step b commit, runtime and verification references;
- rollback (section 10).

Prepend one identical entry to `docs/KNOWTATION-ROADMAP.md`,
`docs/KNOWTATION-OVERSEER-HANDOVER.md` and `docs/NEXT-BROWSER-PRIVATE-VAULT.md`. Its
Single NEXT is the Codex revision. Do no Git or Muse staging or commit in Knowtation.
Never run `git add -A`, `git add .` or `muse code add .` there (kit finding F10).

## 10. Rollback (newest first)

Restore files with an atomic copy idiom, for example
`cp SRC DST.restore && chmod MODE DST.restore && mv -f DST.restore DST`. Verify each
backup's sha256 before using it, and restore the config last. Never follow a "rerun
explicit sync" message (`cli/product_migration.py:336`, finding F2); restore from the
backup and prepare a fresh preview instead.

0. **If interrupted:**
   - during 9.2: restore the paths named in `partial_asset_update` from
     `.overseer/local/rebind-72c2f1fc…/.overseer/` (config last);
   - during 9.3: `atomic` either replaced NEXT or did not (`cli/v1.py:345-346`).
1. **Undo this rebind.** From
   `.overseer/local/rebind-72c2f1fcc77dbda449295d050c81378c02a64e87439b383582e8263090a322fd/.overseer/`
   restore, in this order:
   - `bin/ok` (0755, `0b9ddb50…`);
   - `version.lock` (0644, `0b63a023…`);
   - `config.yaml` (0644, `72c2f1fc…`).

   The backup modes equal the originals, so F3 has no effect here. `ok status
   --check-footprint --exit-code` must then report runtime `OLD_RT` with footprint
   integrity and coverage ok.

   If NEXT names CODEX at that point, the old runtime's `ok next` refuses
   `next_model_mismatch`. Status reports that refusal as `next_error` and exits 1
   (`cli/main.py:229-231`). This is fail-closed and expected. Do not restore the old
   NEXT bytes: that action is completed and must not be re-run. Instead, the owner
   publishes a successor through the restored runtime's `next-write` with `--model
   OPUS --expect-next <current digest>`; the writer parses but does not model-check
   the prior NEXT (`cli/product_next.py:92-96`). Status returns to exit 0 after that.
2. **Then the rc11 rebind:** restore from
   `.overseer/local/rebind-3899dd654a515543ccd3f82a806f1971acde8e38cc401297a3b75e3548b86560/.overseer/`
   as its receipt describes (config `3899dd65…` last). This works only with Muse back
   on rc5.
3. **Then the original migration package:** use the guarded rollback, or restore by
   hand from `$HOME/OVERSEER_KIT/RECOVERY-RUNS/knowtation-compat-20261020/real-backup/files/`
   using the digests and modes in `real-package/manifest.json` (config last). The
   in-repository package is `.overseer/migrations/78b5ebbc…/`.

Kit side: the branch, `WT`, `NEW_RT` and `RUN` are local and kept. Deleting any of
them needs owner approval (kit row C1).

## 11. Stop conditions

Stop, write nothing further and report the exact state and rollback position if any
of these occur.

**Step b:**

- this file's sha256 differs from the one step a reported, or its review stamp is
  not `pass`;
- commit `99e2e5bcfd6de0eb45b4f48872653f396aaa9850` is missing, or
  `git diff --stat 30f5cb4 99e2e5b` lists anything beyond the three docs files;
- any planned name already exists;
- a required change falls outside section 6, or the spec is ambiguous;
- any existing test other than the two section 6 edits needs a change;
- any new test fails, any baseline-passing test fails, or a required tier cannot run
  (for example the real-Muse prerequisite);
- `/build-verification-review` is not `pass`;
- the parent of commit 1 is not `99e2e5b…`, or `git -C "$WT" status --porcelain` is
  non-empty before the runtime build.

**Step c:**

- an entry check fails;
- any section 1 Knowtation value differs at start (including the Muse head, or NEXT
  no longer being `1279cdee…`). The ledger digest is excluded;
- the 9.1 preview differs in any respect;
- any refusal occurs during 9.2–9.3;
- status is not exit 0, or readback differs, after any step;
- a protected snapshot path changes.

**Both steps:**

- an action would need any of: a push, PR, merge, release, deployment or provider
  call; a Knowtation commit or staging; a broad `add`; vault or secret access;
- an action would edit the kit's own `NEXT.md`, `KIT_SRC`, other worktrees or `OLD_RT`.

## 12. Not in scope

The following are out of scope:

- C2 content, format approval and C5 authorization;
- fixes for F1–F8, F10 and F11;
- the BornFree runtime (blocked on D1);
- N1-R and the stacked PR (a Tier 3 merge);
- any change to multi-lane behavior, to `context.model` handling or to the general
  `label()` check.
