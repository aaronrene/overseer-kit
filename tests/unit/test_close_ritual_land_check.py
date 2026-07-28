"""Unit tests for close_ritual land-check."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from adapters.config import load_config
from tools.close_ritual.land_check import run_land_check


def _minimal_config_yaml(tmp_path: Path, *, close_ritual: str) -> Path:
    cfg = tmp_path / ".overseer" / "config.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(
        f"""
overseer_config_version: 1
repo:
  name: fixture
  root_relative_docs: "."
vcs:
  regime: git-only
  canonical: git
  git:
    remote: origin
    main_branch: main
    mirror_branch: null
    feature_branch_pattern: "feat/{{slug}}"
  muse:
    staging_remote: null
    main_branch: null
    working_dir: null
docs:
  handover: OVERSEER_HANDOVER.md
  roadmap: ROADMAP.md
  standing_decisions: ROADMAP.md
thresholds:
  realign_max_commits: 50
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security]
{close_ritual}
""",
        encoding="utf-8",
    )
    return cfg


class CloseRitualLandCheckTests(unittest.TestCase):
    def test_close_ritual_disabled_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cfg_path = _minimal_config_yaml(
                tmp_path,
                close_ritual="close_ritual:\n  enabled: false\n  require_paths: []\n",
            )
            config = load_config(cfg_path)
            result = run_land_check(config, tmp_path)
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(result.auto_merge)

    def test_verify_landed_pass_when_matching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            init = subprocess.run(
                ["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True, text=True
            )
            if init.returncode != 0:
                self.skipTest(f"git init unavailable: {init.stderr}")
            subprocess.run(
                ["git", "config", "user.email", "t@example.com"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "t"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )
            doc = tmp_path / "BOARD.json"
            doc.write_text('{"ok": true}\n', encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "init"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )

            cfg_path = _minimal_config_yaml(
                tmp_path,
                close_ritual=(
                    "close_ritual:\n"
                    "  enabled: true\n"
                    "  mode: verify_landed\n"
                    "  require_paths:\n"
                    "    - BOARD.json\n"
                ),
            )
            config = load_config(cfg_path)
            from unittest.mock import patch

            from tools.governance_freshness import GovernanceFreshnessReport

            ok_fresh = GovernanceFreshnessReport(
                state="not_applicable", message="patched", remediation=None
            )
            with patch(
                "tools.close_ritual.land_check.check_governance_freshness",
                return_value=ok_fresh,
            ):
                result = run_land_check(config, tmp_path)
            self.assertEqual(result.exit_code, 0, msg=result.messages)
            self.assertTrue(result.landed)
            self.assertFalse(result.auto_merge)

    def test_verify_landed_fail_on_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            init = subprocess.run(
                ["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True, text=True
            )
            if init.returncode != 0:
                self.skipTest(f"git init unavailable: {init.stderr}")
            subprocess.run(
                ["git", "config", "user.email", "t@example.com"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "t"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )
            doc = tmp_path / "BOARD.json"
            doc.write_text('{"ok": true}\n', encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "init"],
                cwd=tmp_path,
                check=True,
                capture_output=True,
            )
            doc.write_text('{"ok": false}\n', encoding="utf-8")

            cfg_path = _minimal_config_yaml(
                tmp_path,
                close_ritual=(
                    "close_ritual:\n"
                    "  enabled: true\n"
                    "  mode: verify_landed\n"
                    "  require_paths:\n"
                    "    - BOARD.json\n"
                ),
            )
            config = load_config(cfg_path)
            result = run_land_check(config, tmp_path)
            self.assertEqual(result.exit_code, 1)
            self.assertFalse(result.landed)


if __name__ == "__main__":
    unittest.main()
