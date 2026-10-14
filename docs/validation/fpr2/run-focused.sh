#!/bin/sh
# Explicit local prerequisite; fixtures must be outside all repository parents.
set -eu
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
: "${FPR2_MUSE_PYTHON:?Set the absolute pinned Muse 0.2.1rc5 venv Python}"
exec .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/v1 tests/fpr1 tests/fpr2 tests/muse \
  tests/unit/test_footprint_digest.py tests/unit/test_config.py \
  tests/unit/test_git_only.py tests/unit/test_muse_only.py \
  tests/unit/test_muse_git_mirror.py tests/unit/test_muse_working_dir.py \
  tests/unit/test_path_normalize.py tests/integration/test_adapter_factory.py \
  tests/unit/test_k8_lanes.py tests/unit/test_k7_footprint.py \
  tests/unit/test_footprint_integrity.py \
  tests/unit/test_init_migrate.py::test_classify_preserve_shared_unit \
  tests/unit/test_lt_unit.py::test_session_bookends_default_off \
  tests/unit/test_lt_unit.py::test_session_bookends_unknown_key \
  tests/unit/test_lt_unit.py::test_session_bookends_enabled_non_bool \
  tests/integration/test_lt_integration.py::test_session_bookends_in_resolve_when_enabled \
  --deselect=tests/unit/test_k7_footprint.py::test_rendered_deploy_script_safety_invariants \
  --muse-python "$FPR2_MUSE_PYTHON" \
  --basetemp="${FPR2_FIXTURE_PARENT:-/private/tmp/overseer-fpr2-focused}" \
  --junitxml=docs/validation/fpr2/focused.xml
