"""Unit tests for review CLI argument parsing (§K5.12)."""

from __future__ import annotations

import pytest

from adapters.errors import ConfigError
from cli.main import build_parser, main


def test_review_help_exits_zero() -> None:
    assert main(["review", "--help"]) == 0


def test_missing_freeze_exits_usage() -> None:
    assert main(["review"]) == 1


def test_unknown_review_flag_exits_usage() -> None:
    assert main(["review", "--freeze", "docs/x.md", "--write-vcs"]) == 1


def test_vendor_model_slug_rejected() -> None:
    from cli.kit_root import kit_root
    from tools.freeze_reviewer.labels import is_vendor_slug, validate_reviewer_model

    assert is_vendor_slug("gpt-4o")
    with pytest.raises(ConfigError):
        validate_reviewer_model("gpt-4o", kit_root())


def test_mode_human_with_provider_not_usage() -> None:
  # Parser accepts; not a USAGE conflict per contract
    parser = build_parser()
    args = parser.parse_args(
        ["review", "--freeze", "docs/x.md", "--mode", "human", "--provider", "api", "--model", "thinking-high"]
    )
    assert args.mode == "human"
    assert args.provider == "api"
