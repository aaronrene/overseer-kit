#!/bin/sh
# Offline, disposable compatibility selection. See docs/MUSE-RC8-COMPATIBILITY.md.
set -eu
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo 'usage: check-muse-compatibility.sh MUSE_VENV_PYTHON OUTPUT_DIR [--collect-only]' >&2
  exit 2
fi
ROOT=$(CDPATH= cd -P -- "$(dirname -- "$0")/.." && pwd -P)
MUSE_PYTHON=$1
OUTPUT=$2
COLLECT=${3:-}
if [ -n "$COLLECT" ] && [ "$COLLECT" != '--collect-only' ]; then
  echo 'only --collect-only is accepted as the third argument' >&2
  exit 2
fi
cd "$ROOT"
PYTHONDONTWRITEBYTECODE=1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONDONTWRITEBYTECODE PYTEST_DISABLE_PLUGIN_AUTOLOAD
.venv/bin/python3 -I -B -c '
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from tools.ci.supported_v1 import muse_runtime
p = Path(sys.argv[1])
if not p.is_absolute() or p.parent.name != "bin" or not (p.parent.parent / "pyvenv.cfg").is_file() or p.parent.parent.resolve() == Path(sys.prefix).resolve():
    raise SystemExit("requires a separate absolute Muse venv interpreter")
out = Path(sys.argv[2])
if not out.is_absolute() or out.exists():
    raise SystemExit("OUTPUT_DIR must be a new absolute disposable directory")
print("Exact Muse pair:", *muse_runtime(p))
' "$MUSE_PYTHON" "$OUTPUT"
mkdir "$OUTPUT"
# Keep the incomplete YAML-only historical fixture separate; its full-dependency
# successor below proves standalone Git-only operation without Muse installed.
# The one explicit mirror deselection has the full-footprint successor selected
# below; see the independent replacement map in docs/reviews/FPR-5-REVIEW.md.
exec .venv/bin/python3 -B -m pytest -q -p no:cacheprovider \
  tests/v1/test_supported_v1.py \
  tests/unit/test_config.py tests/unit/test_git_only.py tests/unit/test_muse_only.py \
  tests/unit/test_muse_git_mirror.py tests/unit/test_muse_working_dir.py \
  tests/integration/test_adapter_factory.py \
  tests/fpr4/test_standalone_dependencies.py \
  tests/muse/test_reader_api_compatibility.py tests/muse/test_rc8_compatibility.py \
  tests/muse/test_legacy_native_binding.py tests/muse/test_runtime_rebind.py \
  tests/muse/test_next_model_suggestion_muse.py tests/muse/test_mirror.py \
  tests/muse/test_reviewed_runtime_matrix.py \
  --deselect=tests/muse/test_mirror.py::test_add_change_delete_and_no_content_source_commit \
  tests/muse/test_handoffs.py::test_muse_only_unborn_commit_freshness_and_offline_readonly \
  tests/muse/test_handoffs.py::test_legacy_stage_is_not_silently_deleted_by_read \
  tests/muse/test_product.py::test_forced_native_secret_paths_do_not_enter_projection \
  tests/muse/test_product.py::test_native_stage_visibility_matches_reviewed_checkout_layout \
  --muse-python "$MUSE_PYTHON" --basetemp "$OUTPUT/fixtures" \
  --junitxml "$OUTPUT/results.xml" ${COLLECT:+"$COLLECT"}
