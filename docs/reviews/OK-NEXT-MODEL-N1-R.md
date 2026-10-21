# Independent review — OK-NEXT-MODEL N1-R

**Verdict: PASS.** No blocking mismatch with the freeze. The Knowtation install matches the N1c receipt's runtime and rebind plan.

- Reviewer: Grok 4.7, in this Cursor chat on 2026-10-21. This chat did not build N1b. It is not build-verification round 2 (session `cursor-grok-4.7-bv-r2-2026-10-21T19:01:34Z`, also Grok 4.7). The freeze author recorded itself as Anthropic Claude Opus 5.5. The handover asked for a model other than Grok 4.7; this review records that overlap so the owner can discard it if a different model family is required.
- Range: `99e2e5bcfd6de0eb45b4f48872653f396aaa9850..de711aec04396d9fd5c79b18f37eb672689e24fd` on `feat/next-model-select-20261020`. Ten files, +1711/−38. This review commit is docs only and is not part of that range.
- Freeze: `/Users/aaronrenecarvajal/knowtation/docs/evidence/B02/overseer-next-model-select-20261020/FREEZE.md`, sha256 `3d521241c0610a6ca278074cfb7bce06e75760735b3b13b2a3af4b93733ad70e` (43,499 bytes). `docs/reviews/OK-NEXT-MODEL-FREEZE.md` is a byte copy.
- Method: read-only comparison of the diff to freeze sections 5–9 and 13, recomputation of the prepared runtime digest, and a read-only check of the Knowtation install. Thirty-one `model_label` unit tests were re-run here (31 passed). The section 7 group was not re-run; build-verification round 2 remains the recorded group run. No code edits, pushes, pull requests, merges, installs, Muse changes, or edits to Knowtation, Born Free, or the compat worktree.

## 1. Commit shape

| Commit | Parent | Files | Matches |
| --- | --- | --- | --- |
| `6a04ce18ad53a2fb1e3704f89935fdf7163fe67a` | `99e2e5b…` | `cli/v1.py`, the two existing test edits, two new test modules, `docs/NEXT-MODEL-SELECTION.md`, the pre-amendment freeze copy | Freeze section 6 commit 1. Roadmap and handover are absent. |
| `1571b921be817d5b68f7dfa60fcfe91409a11ff3` | `6a04ce1…` | `docs/ROADMAP.md`, `docs/OVERSEER-HANDOVER.md` | Section 8 commit 2. |
| `29db9e267ded73bc127e2da9867f3c15a8dca25f` | `1571b92…` | `cli/v1_io.py`, `tests/v1/test_next_model_suggestion.py` | Section 13 commit 3. The stress test body is unchanged; only `test_stable_hard_link_still_refused` is added. |
| `ef24c6547abda5b3c43455e64973e26e3c703db9` | `29db9e2…` | freeze copy, roadmap, handover | Section 13 commit 4. |
| `b299b98…`, `de711ae…` | docs only | roadmap and handover | Later closeouts. No runtime files. |

`git diff 29db9e2..de711ae -- cli tests` is empty. No other `cli/` file changes in the range. `next_model_mismatch` is not raised anywhere under `cli/` or `tests/`.

## 2. Single-lane model rule

`cli/v1.py:28-29` is the freeze 5.1 grammar, including `MODEL_LABEL_MAX = 120`. `model_label` at `cli/v1.py:90-98` returns the same string or raises `model_label_invalid`. The docstring states the grammar and the single-lane rule.

`cli/v1.py:286-287` is the freeze 5.2 replacement: one lane and a model other than `context.model` calls `model_label`; it no longer raises `next_model_mismatch`. `parse_next` still runs general `label()` on `model` first (`cli/v1.py:253-254`). `write_next` validates at `cli/v1.py:349` before the advisory lock and `atomic` write at `cli/v1.py:354-358`. Batch publication validates each payload through the same function (`cli/product_next.py:209`). Reads, including `governance-sync --print-next`, go through `display` (`cli/product_governance.py:92-94`, `cli/product_next.py:161`). Existing-config `init` validates current entries at `cli/v1.py:454-455`.

`context.model` is still the stored default. Adopt and rebind still require `--model` to equal it (`cli/product_authority.py:176-178`). The operator note `docs/NEXT-MODEL-SELECTION.md` states the recommendation, the 5.2 table, the grammar, hand edits with `--expect-next`, and older-runtime `next_model_mismatch` rollback.

The two existing test edits remove only the writer `model` parameters (`tests/v1/test_commands.py:68-70`, `tests/muse/test_handoffs.py:123-125`). The reader expectation at `tests/v1/test_commands.py:78-80` still includes `model`.

## 3. Replace-window edit

`atomic()` is unchanged (`cli/v1_io.py:98-141`). `confined()` still walks parents (`cli/v1_io.py:31-39`). On the final component it uses `os.lstat` at most three times (`cli/v1_io.py:41-52`): a missing path returns, a symlink raises `path_symlink`, a non-regular file raises `path_not_regular`, `st_nlink == 1` returns, and any other link count retries. The fourth observation is the refusal `path_not_regular`. Other `OSError` values are not caught.

`read()` keeps `O_RDONLY | O_NOFOLLOW | O_NONBLOCK` and three attempts (`cli/v1_io.py:67-90`). A non-regular file or an over-limit size raises `file_invalid` on that observation. Link count 1 is read. Link count 0 or greater than 1 closes the descriptor and retries. Three ending zeros stay `file_changed_during_read`. Three ending extra links stay `file_invalid`. A hard link that remains is refused by `confined()` as `path_not_regular`, which is what `test_stable_hard_link_still_refused` asserts (`tests/v1/test_next_model_suggestion.py:284-301`).

## 4. Tests against section 7

The new modules cover the seven tiers: unit accepts and the security table (`tests/v1/test_next_model_suggestion.py:41-93`); integration including batch, init/sync, a default label outside the strict grammar, and multi-lane `Modèle` (`:100-201`); Git end-to-end from cwd `/` (`:208-225`); 50 alternating publications and the concurrent writers (`:232-282`); fingerprint, refused-write identity, prompt digest, and status (`:308-370`); the ten-read and 100,000-call bounds (`:377-391`); the next-write rejection table, the hand edit, and retained writer refusals (`:398-501`). Muse publish, rebind, and the explicit `--vcs`/`--base-head` refusal are in `tests/muse/test_next_model_suggestion_muse.py:70-134`.

This chat re-ran the three unit tests: 31 passed in 0.03s. Build-verification round 2 records the section 7 group as 817 passed, 8 failed, 2 errors, with the same failure and error IDs as `RECOVERY-RUNS/knowtation-next-model-select-20261020/runtime.json`, including a pass of the concurrent writer test. That group was not repeated here.

## 5. Runtime and Knowtation install

Prepared runtime `runtime()` recomputed from `PREPARED-RUNTIMES/knowtation-next-model-select-20261020` is sha256 `559e1635299830b4d4c814dceac2acc7b89413a1a33929ae1cb3faa276ba52a7`, version `1.0.0.dev1`. `cli/v1.py` and `cli/v1_io.py` in that tree match commit `29db9e2`. The pre-BV1 directory is still present and was not deleted. `runtime.json` records commit `29db9e2`, parent `1571b92…`, and superseded runtime `1762a406…`. `build-verification.json` records verdict `pass`, round 2, and frozen-spec sha256 `3d521241…`.

N1c receipt `knowtation/docs/evidence/B02/overseer-next-model-select-20261020/README.md` names rebind plan `d94b35798932e783552163ba97f7afc5795d10d351955c5284dbf8589026f322`. Re-hashing the plan object in both `rebind-apply.json` and `rebind-preview.json` with the kit's sorted JSON digest produces that same value. The plan is `same-source-runtime-rebind`, context model `Anthropic Claude Opus, thinking enabled`, bindings equal, tracked choice `preserve`, NEXT preserved, before runtime `309ac668…`, after runtime `559e1635…`, and exactly the six freeze 9.1 paths.

Live Knowtation, read through its bound launcher:

- Repository `6df95ecb-f668-5cf6-adf1-384baf3e6246`, root `/Users/aaronrenecarvajal/knowtation`, branch `docs/scooling-brain-pair-relay`, head `sha256:d0eb71ed…`.
- `ok status --check-footprint --exit-code` exits 0. Runtime root and sha256 are the section 13 runtime above. Footprint integrity and coverage are ok.
- `context.model` is still `Anthropic Claude Opus, thinking enabled`.
- Config sha256 `c5a7997b5f162d8682d31c1daca8d16f86159f23acd18b91c0e27d0265a65494` equals the apply result. Against the rebind backup, config differs only at `runtime.root` and `runtime.sha256`. The launcher differs only on the runtime path in its `exec` line. The lock differs only in the `.overseer/bin/ok` row sha256 and `footprint_digest`.
- Backup `.overseer/local/rebind-72c2f1fc…/.overseer/` holds config `72c2f1fc…` mode 0644, lock `0b63a023…` mode 0644, and launcher `0b9ddb50…` mode 0755.
- The identical N1c entry is present in `docs/KNOWTATION-ROADMAP.md`, `docs/KNOWTATION-OVERSEER-HANDOVER.md`, and `docs/NEXT-BROWSER-PRIVATE-VAULT.md`. A later product entry sits above it.

Canonical `docs/NEXT.md` is now sha256 `0cd54fd9e88e4a86a5b1d2da7d5b047728226a3696fb17c476cd12ee5feeb9f2`, action `C5-OWNER-DECISION`, model `OpenAI Codex (latest GPT model, high reasoning)`. That is later product publication. The N1c publication `3a878755…` (`C2-PROPOSAL-REVISION-1`) remains the receipt's recorded write. The installed runtime is what lets this later Codex label be read in a single-lane repository.

## 6. Notes that do not block

1. `test_stress_concurrent_codex_and_default_writers` retries when both writers exit 0 (`tests/v1/test_next_model_suggestion.py:274-275`) instead of requiring `[0, 2]` on every attempt, which is the sentence in freeze section 7. Section 13 told step b2 to leave that test unchanged, including the in-flight exit-0 assertion at line 268, and round 2 passed it. Both-success is the pre-existing same-UID advisory-lock race described on `cli/v1_io.py:103-106`. The test still requires a later `stale_write` conflict and refuses `path_not_regular`.
2. A model whose only character is U+2028 is refused `label_invalid` by `label()` (`cli/v1.py:84-86`) because `str.strip` removes it, so `model_label_invalid` is not the first code. The freeze names `model_label_invalid` for every table value other than the C0 controls and the U+0085 encoder case. The value is still refused, stdout is empty, and NEXT is unchanged (`tests/v1/test_next_model_suggestion.py:414-422`). The hand edit `Codex` + U+2028 + `Lane: other` is `model_label_invalid` (`:430-439`). Tightening `label()` remains F11.
3. That stress test checks that the published model is one of the two labels (`:272-273`). It does not compare it with the winning process's argument. Section 13 left the test as built.

## 7. Bookend

This worktree's `.overseer/bin/ok -C` this root `next --lane product` refuses `launcher_repository_mismatch` (`cli/v1.py:139-140`). The launcher is bound to `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-publication-20261017`. That binding is outside the reviewed diff. This review does not rewrite the kit's `docs/NEXT.md`.
