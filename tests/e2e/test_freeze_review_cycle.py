"""End-to-end freeze review lifecycle (§K5.12)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    findings_provider_factory,
    git_status_runner,
    pass_provider_factory,
    run_cli,
    seed_freeze_repo,
)
from tools.freeze_reviewer.types import Finding


def test_full_freeze_review_cycle(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    runner = git_status_runner()

    assert (
        run_cli(
            ["review", "--freeze", rel, "--dry-run"],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
        )
        == 0
    )
    assert "review_stamp:" not in artifact.read_text(encoding="utf-8")

    assert (
        run_cli(
            ["review", "--freeze", rel],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
        )
        == 0
    )
    stamped = artifact.read_text(encoding="utf-8")
    assert "review_stamp:" in stamped

    assert (
        run_cli(
            ["review", "--freeze", rel],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
        )
        == 0
    )
    assert artifact.read_text(encoding="utf-8") == stamped

    artifact.write_text(stamped + "\n# edited\n", encoding="utf-8")
    findings = [
        Finding(
            check="C3",
            severity="MAJOR",
            category="consistency",
            path=rel,
            line=1,
            message="edited",
        ).with_citation()
    ]
    code = run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=findings_provider_factory(findings),
    )
    assert code == 7
    assert all("commit" not in call[0].lower() for call in runner.calls)
