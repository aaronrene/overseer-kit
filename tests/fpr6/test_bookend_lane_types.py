"""Malformed transport assertions must refuse; these are not native host events."""
import json

import pytest

from cli.product_bookends import EVENT_PATHS
from tests.fpr1.test_bookends import bookend_repo, invoke, snapshot


@pytest.mark.parametrize("event", list(EVENT_PATHS))
@pytest.mark.parametrize("lane", [[], {}], ids=["array", "object"])
def test_unhashable_lane_refuses_without_traceback_or_writes(bookend_repo, event, lane):
    before = snapshot(bookend_repo)
    result = invoke(bookend_repo, event, json.dumps({"lane": lane}))
    assert result.returncode == 2, result.stderr
    assert result.stdout == ""
    assert result.stderr == "refused: hook_lane_mismatch\n"
    assert snapshot(bookend_repo) == before
