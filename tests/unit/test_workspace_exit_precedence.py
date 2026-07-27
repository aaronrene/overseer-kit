"""Unit tests for status exit precedence with workspace relay (§MR.7.2)."""

from __future__ import annotations

from cli.commands.status import _exit_code_from_conditions


def test_exit_precedence_includes_workspace_relay() -> None:
    assert (
        _exit_code_from_conditions(
            config_error=False,
            integrity=None,
            drift_status="ok",
            use_exit_code=True,
            workspace_ok=False,
        )
        == 35
    )
    # 6 beats 35
    assert (
        _exit_code_from_conditions(
            config_error=False,
            integrity="mismatch",
            drift_status="ok",
            use_exit_code=True,
            workspace_ok=False,
        )
        == 6
    )
    # 2 beats 35
    assert (
        _exit_code_from_conditions(
            config_error=True,
            integrity=None,
            drift_status="ok",
            use_exit_code=True,
            workspace_ok=False,
        )
        == 2
    )
    # 35 beats 3
    assert (
        _exit_code_from_conditions(
            config_error=False,
            integrity=None,
            drift_status="behind",
            use_exit_code=True,
            workspace_ok=False,
        )
        == 35
    )
