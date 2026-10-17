# FPR-4 clean-process Git status import boundary

Author validation on fixed runtime `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`; this is not FPR-5 independent review. The original assertion remains unchanged. The frozen combined matrix's failure must remain visible separately from subsequent successor coverage. No runtime repair is required by this finding.

## Preserved failure

The original `tests/fpr1/test_dispatch.py::test_git_core_imports_no_muse_or_provider_engine` succeeds at full Git `status --json` but fails its module-prefix assertion when run alone: [log](import-boundary-before.log), [JUnit](import-boundary-before.xml), **1 failed in 3.74s**.

```sh
PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider tests/fpr1/test_dispatch.py::test_git_core_imports_no_muse_or_provider_engine --basetemp=/private/tmp/overseer-fpr4-import-boundary-before --junitxml=docs/validation/fpr4/import-boundary-before.xml > docs/validation/fpr4/import-boundary-before.log 2>&1
```

Its `set(sys.modules)` delta depends on previous test collection/imports. Passing in the initial monolithic run did not prove a clean-process boundary. The candidate never preloads the provider package to avoid this assertion.

## Actual imports and preserved behavior

FPR-3 restored full-status sections. `cli.product_status.sections` imports `cli.commands.route.routing_policy_status`, which imports `cli.context.CliContext`. That context's `ReviewProvider` type import loads package exports and definitions. Exactly these provider modules load:

- `tools.freeze_reviewer.providers`
- `tools.freeze_reviewer.providers.api_client`
- `tools.freeze_reviewer.providers.api_prompt`
- `tools.freeze_reviewer.providers.api_response`
- `tools.freeze_reviewer.providers.base`
- `tools.freeze_reviewer.providers.model_hint`

They define protocols, dataclasses, transport and provider methods. The provider engine is not imported; no provider is instantiated, selected, probed or invoked. `tools.honesty.muse_registry` is the only Muse-named imported helper: it defines a protocol and a null registry without importing native Muse. Neither `muse` nor `adapters.muse_*` loads. Exact complete module inventories, subprocess argument lists and runtime/identity observations are retained in [probe evidence](import-boundary-probes.json).

The FPR-1 bounded-status expectation that no provider definition module ever loads has changed with full-product status. The maintained behavior remains Git-only installation without native Muse, offline inspection without provider or remote actions, complete full-status observations, correct repository identity, and read-only inspection.

## Candidate successor

Candidate file: `/private/tmp/overseer-fpr4-import-candidate/test_import_boundary.py`. Proposed final selector: `tests/fpr4/test_import_boundary.py::test_git_full_status_clean_bootstrap_is_offline_without_native_muse`, parameterized for `local` and `api` reviewer settings. It stayed outside the repository until the combined-run source freeze ended, then was promoted byte-for-byte.

Each case creates a new disposable Git repository and enters the actual `cli/bootstrap.py` boundary in a fresh isolated conventional-venv Python process. No product modules are loaded before the guard. Native Muse is absent from the environment. A meta-path guard rejects native Muse and Muse-adapter imports. Profiling rejects provider function, factory, constructor and method execution; the sole exception is CPython's generated `__create_fn__` invoked directly by the standard-library `dataclasses` module to define methods, with exact filename/caller checks. No general callable or annotation bypass is present. Socket activity and all process launches except the hardened local Git read path are rejected. Dummy API configuration and credentials ensure that API availability is not the reason activity is avoided.

The assertions require full-status sections, exact repository UUID/root/branch/head, Git substrate and no-applicable Muse sync, offline readiness, and unchanged file bytes, permissions and modification times throughout the complete disposable repository. Audit records show only local `rev-parse`, `status` and read-only `symbolic-ref` calls, with empty native-import, provider-call and network-event lists.

Portable candidate validation: [log](import-boundary-candidate-portable.log), [JUnit](import-boundary-candidate-portable.xml), **2 passed in 7.65s**. Candidate hash and exact observations are recorded in [probe evidence](import-boundary-probes.json).

```sh
FPR4_KIT=/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014 PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider /private/tmp/overseer-fpr4-import-candidate/test_import_boundary.py --basetemp=/private/tmp/overseer-fpr4-import-boundary-candidate-portable --junitxml=docs/validation/fpr4/import-boundary-candidate-portable.xml > docs/validation/fpr4/import-boundary-candidate-portable.log 2>&1
```

Earlier candidate-only harness development logs are preserved: [first](import-boundary-candidate-first.log) identified dataclass method-generation metadata; [second](import-boundary-candidate-second.log) identified an incorrect candidate assertion using `revision.branch` instead of the real top-level `branch`; [initial passing candidate](import-boundary-candidate.log) passed both cases before making path discovery portable and narrowing process/callable guards. These are test-development observations, not additional production failures or final evidence.

## Final affected validation

The promoted [successor](../../../tests/fpr4/test_import_boundary.py) passed
**2 cases in 6.97 seconds**, exit 0, through the recorded runner:
[record](import-boundary-final-rerun.json), [log](import-boundary-final-rerun.log),
[JUnit](import-boundary-final-rerun.xml). Exact collection and source/dependency
boundaries passed. Production, native/packaging inputs, Muse and Python dependencies
match the frozen combined run; only the new test was added.

```sh
FPR2_MUSE_PYTHON=/Users/aaronrenecarvajal/.local/share/muse/venv/bin/python .venv/bin/python -B scripts/fpr4_run.py --name import-boundary-final-rerun --selection docs/validation/fpr4/import-boundary-final-selection.json
```

The earlier `import-boundary-final` invocation exited 4 before collection because
it passed `--muse-python` to pytest without selecting the native conftest which
registers that option. Its [raw log](import-boundary-final.log) remains preserved;
the corrected command above records the same pinned Muse through the environment.
This command correction changed no product/test/runner source.

The final raw combined result remains 1,207 passed / 1 failed; these two later
successor passes are separate affected evidence. The seventh explicit original
node deselection appears only in the separate closeout selection. No new review
cycle or remote/provider run is implied.
