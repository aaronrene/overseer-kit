"""Reviewed-runtime matrix: CI probe agreement and the FPR-4 mirror successor."""
import time

import pytest

from cli.v1_revision import MUSE_RUNTIMES, muse_read
from tests.fpr4.test_mirror_full_footprint import (
    test_full_footprint_mirror_delta_and_identical_native_snapshot as _mirror_successor)
from tests.muse.conftest import rebind_pair
from tools.ci import supported_v1


def test_fpr4_mirror_successor_under_probed_runtime(tmp_path, muse_python):
    _mirror_successor(tmp_path, muse_python)


def test_ci_probe_matches_reader_runtime(muse_runtime, muse_root):
    started = time.monotonic()
    assert supported_v1.muse_runtime(muse_runtime.python) == (
        muse_runtime.version, muse_runtime.sha256)
    runtime = muse_read(muse_root, str(muse_runtime.python))['runtime']
    assert runtime['version'] == muse_runtime.version
    assert runtime['sha256'] == muse_runtime.sha256
    assert MUSE_RUNTIMES[muse_runtime.version] == muse_runtime.sha256
    assert time.monotonic() - started < 15


def test_rebind_runtimes_are_current_and_single_other(muse_runtime, rebind_runtimes, monkeypatch):
    current, stale = rebind_runtimes
    assert current == muse_runtime.version
    assert stale in MUSE_RUNTIMES
    assert stale != current
    assert rebind_pair('0.2.1rc5') == ('0.2.1rc5', '0.2.1rc11')
    assert rebind_pair('0.2.1rc11') == ('0.2.1rc11', '0.2.1rc5')
    monkeypatch.setitem(MUSE_RUNTIMES, '0.2.1rc999', '0' * 64)
    with pytest.raises(AssertionError, match='exactly one other reviewed Muse runtime is required'):
        rebind_pair('0.2.1rc11')
