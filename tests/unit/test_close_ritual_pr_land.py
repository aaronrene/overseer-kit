"""Unit + integration tests for close_ritual pr-land."""

from __future__ import annotations

import json
import subprocess
import unittest
from unittest.mock import patch

from tools.close_ritual.pr_land import (
    EXIT_CHECKS_FAILED,
    EXIT_OK,
    EXIT_UNAUTHORIZED,
    run_pr_land,
)


def _checks_tsv(*rows: tuple[str, str]) -> str:
    return "\n".join(f"{name}\t{state}\t0s\thttps://example.test/{name}" for name, state in rows) + "\n"


class PrLandAuthorizationTests(unittest.TestCase):
    def test_refuses_without_authorization(self) -> None:
        result = run_pr_land("1", authorization="")
        self.assertEqual(result.exit_code, EXIT_UNAUTHORIZED)
        self.assertFalse(result.auto_merge)

    def test_merges_when_green(self) -> None:
        def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
            if cmd[:3] == ["gh", "pr", "view"]:
                return subprocess.CompletedProcess(
                    cmd, 0, stdout=json.dumps({"number": 1, "state": "OPEN"}), stderr=""
                )
            if cmd[:3] == ["gh", "pr", "checks"]:
                return subprocess.CompletedProcess(
                    cmd, 0, stdout=_checks_tsv(("verify", "pass")), stderr=""
                )
            if cmd[:3] == ["gh", "pr", "merge"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            raise AssertionError(cmd)

        result = run_pr_land(
            "1",
            authorization="operator: land after green",
            runner=runner,
            sleep_fn=lambda _s: None,
        )
        self.assertEqual(result.exit_code, EXIT_OK)
        self.assertTrue(result.merged)
        self.assertFalse(result.auto_merge)

    def test_failed_check_exit_2(self) -> None:
        def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
            if cmd[:3] == ["gh", "pr", "view"]:
                return subprocess.CompletedProcess(
                    cmd, 0, stdout=json.dumps({"number": 2, "state": "OPEN"}), stderr=""
                )
            if cmd[:3] == ["gh", "pr", "checks"]:
                return subprocess.CompletedProcess(
                    cmd, 1, stdout=_checks_tsv(("verify", "fail")), stderr=""
                )
            raise AssertionError(cmd)

        result = run_pr_land(
            "2",
            authorization="operator: expect fail",
            runner=runner,
            sleep_fn=lambda _s: None,
        )
        self.assertEqual(result.exit_code, EXIT_CHECKS_FAILED)
        self.assertIn("verify", result.failing)


if __name__ == "__main__":
    unittest.main()
