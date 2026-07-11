"""Data-integrity tests for review idempotency (§K5.12)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cli.atomic import WriteFailure
from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, pass_provider_factory, run_cli, write_config
from tools.freeze_reviewer.artifact import parse_artifact
from tools.freeze_reviewer.stamp import reference_digest, write_stamp
from tools.freeze_reviewer.types import ReviewerSettings


def _review_pass(path: Path, repo: Path) -> None:
    rel = path.relative_to(repo).as_posix()
    run_cli(
        ["review", "--freeze", rel],
        cwd=repo,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )


@pytest.mark.parametrize(
    "fixture_name",
    ["freeze-artifact.md", "freeze-artifact.yaml"],
)
def test_restamp_digest_stable(tmp_path: Path, fixture_name: str) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    if fixture_name.endswith(".md"):
        target = tmp_path / "docs" / "freeze.md"
        target.parent.mkdir(parents=True)
    else:
        target = tmp_path / "freeze.yaml"
    target.write_text((FIXTURES / fixture_name).read_text(encoding="utf-8"), encoding="utf-8")
    _review_pass(target, tmp_path)
    after_first = target.read_bytes()
    _review_pass(target, tmp_path)
    assert target.read_bytes() == after_first


def test_operator_forced_md_restamp_stable(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    target = tmp_path / "notes.md"
    target.write_text("# operator forced\n", encoding="utf-8")
    _review_pass(target, tmp_path)
    first = target.read_bytes()
    _review_pass(target, tmp_path)
    assert target.read_bytes() == first


def test_whitespace_invariant_digest(tmp_path: Path) -> None:
    loose = tmp_path / "loose.yaml"
    loose.write_text(
        "phase: K5b-test\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n",
        encoding="utf-8",
    )
    parsed_loose = parse_artifact(loose, rel_path="loose.yaml")
    tight = tmp_path / "tight.yaml"
    tight.write_text(
        'phase: "K5b-test"\noutputs:\n  - {id: a, path: docs/a.md, frozen: true}\n',
        encoding="utf-8",
    )
    parsed_tight = parse_artifact(tight, rel_path="tight.yaml")
    assert reference_digest(parsed_loose) == reference_digest(parsed_tight)


def test_dry_run_and_no_stamp_write_zero(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    target = tmp_path / "freeze.yaml"
    target.write_text((FIXTURES / "freeze-artifact.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    rel = target.relative_to(tmp_path).as_posix()
    before = target.read_bytes()
    assert (
        run_cli(
            ["review", "--freeze", rel, "--dry-run"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
        )
        == 0
    )
    assert target.read_bytes() == before
    assert (
        run_cli(
            ["review", "--freeze", rel, "--no-stamp"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
        )
        == 0
    )
    assert target.read_bytes() == before
