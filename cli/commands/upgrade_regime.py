"""``ok upgrade-regime`` CLI command (§O2.7)."""

from __future__ import annotations

from argparse import Namespace

from cli.context import CliContext
from cli.output import CommandReport
from tools.upgrade_regime.ceremony import run_upgrade_regime


def run_upgrade_regime_command(args: Namespace, ctx: CliContext) -> int:
    """Execute Stage 3 ``muse-only`` → ``muse+git-mirror`` ceremony."""
    code, upgrade = run_upgrade_regime(args, ctx)
    report = CommandReport()
    report.data.update(upgrade.to_payload())
    for err in upgrade.errors:
        ctx.output.error(err)
        report.errors.append(err)
    for warn in upgrade.warnings:
        ctx.output.warn(warn)
        report.add_warning(warn)

    if ctx.output.json_mode:
        payload = report.to_payload()
        if report.errors:
            payload["errors"] = list(report.errors)
        ctx.output.emit_json(payload)
    else:
        if code == 0 and not upgrade.errors:
            if upgrade.start_state == "complete-upgrade" and not upgrade.live_bridge_invoked:
                ctx.output.emit("already upgraded (idempotent)")
            elif upgrade.dry_run and not upgrade.apply:
                ctx.output.emit("dry-run: no files written")
                ctx.output.emit(f"start_state: {upgrade.start_state}")
                ready = "yes" if upgrade.ready_for_live_bridge else "no"
                ctx.output.emit(f"ready_for_live_bridge: {ready}")
                ctx.output.emit(upgrade.next_live_step)
                ctx.output.emit(upgrade.hard_stop_c8)
            else:
                ctx.output.emit("upgrade-regime complete through C5")
                ready = "yes" if upgrade.ready_for_live_bridge else "no"
                ctx.output.emit(f"ready_for_live_bridge: {ready}")
                if not upgrade.ready_for_live_bridge and upgrade.ready_for_footprint:
                    ctx.output.emit("footprint ready; configure git remote before --live-bridge (G8)")
                ctx.output.emit(upgrade.hard_stop_c8)
    return code
