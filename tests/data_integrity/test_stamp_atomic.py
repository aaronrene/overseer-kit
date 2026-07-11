"""Data-integrity tests for atomic stamp writes (§K5.12)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cli.atomic import WriteFailure
from tests.support import FIXTURES
from tools.freeze_reviewer.artifact import parse_artifact
from tools.freeze_reviewer.stamp import build_stamp, write_stamp
from tools.freeze_reviewer.types import ReviewerSettings


def test_oserror_mid_stamp_preserves_original(tmp_path: Path) -> None:
    path = tmp_path / "freeze.yaml"
    original = (FIXTURES / "freeze-artifact.yaml").read_text(encoding="utf-8")
    path.write_text(original, encoding="utf-8")
    parsed = parse_artifact(path, rel_path="freeze.yaml")
    stamp = build_stamp(
        parsed,
        reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"),
        kit_version="0.1.0",
    )
    with patch("tools.freeze_reviewer.stamp.atomic_write_text", side_effect=WriteFailure(path, OSError("fail"))):
        with pytest.raises(WriteFailure):
            write_stamp(path, parsed, stamp)
    assert path.read_text(encoding="utf-8") == original
