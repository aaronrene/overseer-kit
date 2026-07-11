"""Security tests — artifact injection cannot invoke shell (§K5.12)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cli.kit_root import kit_root
from tests.support import git_status_runner, pass_provider_factory, run_cli, write_config


def test_artifact_shell_metacharacters_no_shell(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    artifact = tmp_path / "docs" / "evil.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "# evil\n\n```yaml\nphase: x\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n```\n\n$(rm -rf /)\n",
        encoding="utf-8",
    )
    with patch("adapters.runner.subprocess.run") as mocked:
        code = run_cli(
            ["review", "--freeze", "docs/evil.md"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
        )
        assert mocked.call_count == 0 or all("rm -rf" not in str(call) for call in mocked.call_args_list)
    assert code in {0, 7, 8}
