"""Built-in L1 orchestrator algorithm (§K9.5)."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from adapters.config import CheckpointsConfig, OverseerConfig
from cli.atomic import WriteFailure, atomic_write_text
from cli.paths import PathEscapeError, confine_path, repo_relative
from tools.checkpoints.advance import compute_advance
from tools.checkpoints.artifact_hash import parse_artifact_sha256
from tools.checkpoints.argv_builder import build_verify_argv
from tools.checkpoints.executor import ExecResult, ScriptExecutor, SubprocessScriptExecutor
from tools.checkpoints.overrides import canonical_overrides_json
from tools.checkpoints.schema import (
    CheckpointSchemaError,
    load_manifest,
    load_policy,
    manifest_to_yaml,
    merge_overrides,
    render_progress,
    resolve_template_steps,
)
from tools.checkpoints.types import (
    ErrorToken,
    ManifestState,
    StepState,
    VerifyMode,
    VerifyStepJson,
    VerifyStepResult,
)


@dataclass
class VerifyStepOptions:
    """CLI options for verify-step."""

    manifest: str | None = None
    step_id: str | None = None
    through_current: bool = False
    verify_all: bool = False
    policy: str | None = None
    dry_run: bool = False
    emit_json: bool = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _step_json_entries(
    template_steps: list[str],
    manifest: ManifestState,
    selected: list[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for step_id in template_steps:
        if step_id not in selected:
            continue
        state = manifest.steps.get(step_id, StepState())
        entries.append(
            {
                "id": step_id,
                "verified": state.verified,
                "artifact_sha256": state.artifact_sha256,
            }
        )
    return entries


def _result(
    *,
    exit_code: int,
    mode: VerifyMode | None,
    dry_run: bool,
    manifest_rel: str | None,
    steps: list[dict[str, Any]],
    error: ErrorToken,
) -> VerifyStepResult:
    payload = VerifyStepJson(
        ok=exit_code == 0,
        exit_code=exit_code,
        mode=mode,
        dry_run=dry_run,
        manifest=manifest_rel,
        steps=steps,
        error=error,
    )
    return VerifyStepResult(exit_code=exit_code, json_payload=payload)


def _resolve_mode(options: VerifyStepOptions) -> VerifyMode | None:
    if options.step_id is not None:
        return "step"
    if options.through_current:
        return "through"
    if options.verify_all:
        return "all"
    return None


def _validate_usage(options: VerifyStepOptions) -> VerifyStepResult | None:
    selectors = [
        options.step_id is not None,
        options.through_current,
        options.verify_all,
    ]
    if sum(1 for x in selectors if x) != 1:
        return _result(
            exit_code=1,
            mode=_resolve_mode(options),
            dry_run=options.dry_run,
            manifest_rel=options.manifest,
            steps=[],
            error="usage",
        )
    return None


def _select_through_current(
    template_steps: list[str],
    manifest: ManifestState,
) -> tuple[list[str] | None, VerifyStepResult | None]:
    """Return selected steps or a refusal result."""
    unverified = [sid for sid in template_steps if not manifest.steps[sid].verified]
    if not unverified:
        return [], None
    first_unverified = unverified[0]
    current_index = template_steps.index(manifest.current_step)
    first_index = template_steps.index(first_unverified)
    if first_index > current_index:
        return None, _result(
            exit_code=11,
            mode="through",
            dry_run=False,
            manifest_rel=None,
            steps=[],
            error="step_order",
        )
    end_index = current_index
    return template_steps[first_index : end_index + 1], None


def _is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def run_verify_step(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: VerifyStepOptions,
    executor: ScriptExecutor | None = None,
    write_manifest: Callable[[Path, str], None] | None = None,
    write_progress: Callable[[Path, str], None] | None = None,
) -> VerifyStepResult:
    """Execute the built-in verify-step orchestrator."""
    exec_runner = executor or SubprocessScriptExecutor()
    manifest_writer = write_manifest or (
        lambda path, text: atomic_write_text(path, text)
    )
    progress_writer = write_progress or (
        lambda path, text: atomic_write_text(path, text)
    )
    mode = _resolve_mode(options)
    dry_run = options.dry_run

    usage_result = _validate_usage(options)
    if usage_result is not None:
        usage_result.json_payload.dry_run = dry_run
        return usage_result

    checkpoints = config.checkpoints
    if not checkpoints.enabled:
        return _result(
            exit_code=4,
            mode=mode,
            dry_run=dry_run,
            manifest_rel=None,
            steps=[],
            error="refused",
        )

    if checkpoints.orchestrator:
        return _run_consumer_override(
            config=config,
            repo_root=repo_root,
            options=options,
            mode=mode,
            executor=exec_runner,
        )

    manifest_rel, manifest_path, manifest_code = _resolve_manifest_path(
        repo_root, checkpoints, options.manifest
    )
    if manifest_code is not None:
        return _result(
            exit_code=manifest_code,
            mode=mode,
            dry_run=dry_run,
            manifest_rel=manifest_rel,
            steps=[],
            error="config" if manifest_code == 2 else "refused",
        )

    policy_rel, policy_path, policy_code = _resolve_policy_path(
        repo_root, checkpoints, options.policy
    )
    if policy_code is not None:
        return _result(
            exit_code=policy_code,
            mode=mode,
            dry_run=dry_run,
            manifest_rel=manifest_rel,
            steps=[],
            error="config" if policy_code == 2 else "refused",
        )

    try:
        policy = load_policy(policy_path)
        manifest = load_manifest(manifest_path)
        template_steps = resolve_template_steps(policy, manifest)
    except CheckpointSchemaError:
        return _result(
            exit_code=2,
            mode=mode,
            dry_run=dry_run,
            manifest_rel=manifest_rel,
            steps=[],
            error="config",
        )

    merged_overrides = merge_overrides(policy, manifest.template_id)

    if mode == "step":
        assert options.step_id is not None
        if options.step_id not in template_steps:
            return _result(
                exit_code=2,
                mode=mode,
                dry_run=dry_run,
                manifest_rel=manifest_rel,
                steps=[],
                error="config",
            )
        selected = [options.step_id]
    elif mode == "through":
        selected, refuse = _select_through_current(template_steps, manifest)
        if refuse is not None:
            refuse.json_payload.manifest = manifest_rel
            refuse.json_payload.dry_run = dry_run
            return refuse
        assert selected is not None
        if not selected:
            return _result(
                exit_code=0,
                mode=mode,
                dry_run=dry_run,
                manifest_rel=manifest_rel,
                steps=[],
                error=None,
            )
    else:
        selected = list(template_steps)

    if dry_run:
        for step_id in selected:
            order_refuse = _check_step_order(
                template_steps,
                manifest,
                step_id,
                selected,
                mode=mode,
                dry_run=True,
                manifest_rel=manifest_rel,
            )
            if order_refuse is not None:
                return order_refuse
            script_refuse = _check_script_path(
                repo_root, policy, step_id, mode, manifest_rel, template_steps, manifest, selected
            )
            if script_refuse is not None:
                script_refuse.json_payload.dry_run = True
                return script_refuse
        return _result(
            exit_code=0,
            mode=mode,
            dry_run=True,
            manifest_rel=manifest_rel,
            steps=_step_json_entries(template_steps, manifest, selected),
            error=None,
        )

    for step_id in selected:
        order_refuse = _check_step_order(
            template_steps,
            manifest,
            step_id,
            selected,
            mode=mode,
            dry_run=dry_run,
            manifest_rel=manifest_rel,
        )
        if order_refuse is not None:
            return order_refuse

        step_def = policy.steps[step_id]
        try:
            script_path = confine_path(repo_root, step_def.verify_script)
        except PathEscapeError:
            return _result(
                exit_code=4,
                mode=mode,
                dry_run=dry_run,
                manifest_rel=manifest_rel,
                steps=_step_json_entries(template_steps, manifest, selected),
                error="refused",
            )
        if not _is_executable(script_path):
            return _result(
                exit_code=4,
                mode=mode,
                dry_run=dry_run,
                manifest_rel=manifest_rel,
                steps=_step_json_entries(template_steps, manifest, selected),
                error="refused",
            )

        script_rel = repo_relative(repo_root, script_path)
        argv = build_verify_argv(
            verify_script=script_rel,
            manifest_rel=manifest_rel or "",
            step_id=step_id,
            policy_rel=policy_rel or "",
        )

        overrides_path: Path | None = None
        env = {
            "OVERSEER_REPO_ROOT": str(repo_root.resolve()),
            "OVERSEER_CHECKPOINT_PLACEHOLDER_TOKENS": json.dumps(
                policy.placeholder_tokens, ensure_ascii=False
            ),
        }
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                delete=False,
                suffix=".json",
            ) as handle:
                handle.write(canonical_overrides_json(merged_overrides))
                overrides_path = Path(handle.name)
            env["OVERSEER_CHECKPOINT_OVERRIDES_PATH"] = str(overrides_path.resolve())

            exec_result = exec_runner.exec_argv(
                argv,
                cwd=str(repo_root.resolve()),
                env=env,
            )
        finally:
            if overrides_path is not None:
                try:
                    overrides_path.unlink(missing_ok=True)
                except OSError:
                    pass

        if exec_result.exit_code != 0:
            result = _result(
                exit_code=10,
                mode=mode,
                dry_run=dry_run,
                manifest_rel=manifest_rel,
                steps=_step_json_entries(template_steps, manifest, selected),
                error="verify_fail",
            )
            if exec_result.stderr:
                result.stderr_extra = exec_result.stderr.decode("utf-8", errors="replace")
            return result

        sha = parse_artifact_sha256(exec_result.stdout)
        manifest.steps[step_id].verified = True
        manifest.steps[step_id].verified_at = _utc_now_iso()
        manifest.steps[step_id].artifact_sha256 = sha

        verified_map = {sid: manifest.steps[sid].verified for sid in template_steps}
        manifest.current_step = compute_advance(
            template_steps,
            step_id,
            verified_map,
            manifest.current_step,
        )

        try:
            manifest_writer(manifest_path, manifest_to_yaml(manifest))
            if checkpoints.progress:
                progress_path = _confine_optional(repo_root, checkpoints.progress)
                if progress_path is not None:
                    progress_writer(
                        progress_path,
                        render_progress(manifest, template_steps),
                    )
        except (WriteFailure, OSError):
            return _result(
                exit_code=5,
                mode=mode,
                dry_run=dry_run,
                manifest_rel=manifest_rel,
                steps=_step_json_entries(template_steps, manifest, selected),
                error="io",
            )

    return _result(
        exit_code=0,
        mode=mode,
        dry_run=dry_run,
        manifest_rel=manifest_rel,
        steps=_step_json_entries(template_steps, manifest, selected),
        error=None,
    )


def _confine_optional(repo_root: Path, user_path: str) -> Path | None:
    try:
        return confine_path(repo_root, user_path)
    except PathEscapeError:
        return None


def _resolve_manifest_path(
    repo_root: Path,
    checkpoints: CheckpointsConfig,
    manifest_arg: str | None,
) -> tuple[str | None, Path | None, int | None]:
    rel = manifest_arg or checkpoints.active_manifest
    if rel is None or not str(rel).strip():
        return None, None, 2
    try:
        path = confine_path(repo_root, rel)
    except PathEscapeError:
        return rel, None, 4
    if not path.is_file():
        return rel, None, 4
    return repo_relative(repo_root, path), path, None


def _resolve_policy_path(
    repo_root: Path,
    checkpoints: CheckpointsConfig,
    policy_arg: str | None,
) -> tuple[str | None, Path | None, int | None]:
    rel = policy_arg or checkpoints.policy
    if rel is None or not str(rel).strip():
        return None, None, 2
    try:
        path = confine_path(repo_root, rel)
    except PathEscapeError:
        return rel, None, 4
    if not path.is_file():
        return rel, None, 4
    return repo_relative(repo_root, path), path, None


def _check_step_order(
    template_steps: list[str],
    manifest: ManifestState,
    step_id: str,
    selected: list[str],
    *,
    mode: VerifyMode | None,
    dry_run: bool,
    manifest_rel: str | None,
) -> VerifyStepResult | None:
    """Refuse when a prior template step is not verified (§K9.5 step 6a)."""
    step_index = template_steps.index(step_id)
    selected_index = selected.index(step_id)
    earlier_in_run = set(selected[:selected_index])
    for prior_id in template_steps[:step_index]:
        if manifest.steps[prior_id].verified:
            continue
        if prior_id in earlier_in_run:
            continue
        return _result(
            exit_code=11,
            mode=mode,
            dry_run=dry_run,
            manifest_rel=manifest_rel,
            steps=_step_json_entries(template_steps, manifest, selected),
            error="step_order",
        )
    return None


def _check_script_path(
    repo_root: Path,
    policy,
    step_id: str,
    mode: VerifyMode | None,
    manifest_rel: str | None,
    template_steps: list[str],
    manifest: ManifestState,
    selected: list[str],
) -> VerifyStepResult | None:
    step_def = policy.steps[step_id]
    try:
        script_path = confine_path(repo_root, step_def.verify_script)
    except PathEscapeError:
        return _result(
            exit_code=4,
            mode=mode,
            dry_run=True,
            manifest_rel=manifest_rel,
            steps=_step_json_entries(template_steps, manifest, selected),
            error="refused",
        )
    if not _is_executable(script_path):
        return _result(
            exit_code=4,
            mode=mode,
            dry_run=True,
            manifest_rel=manifest_rel,
            steps=_step_json_entries(template_steps, manifest, selected),
            error="refused",
        )
    return None


def _run_consumer_override(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: VerifyStepOptions,
    mode: VerifyMode | None,
    executor: ScriptExecutor,
) -> VerifyStepResult:
    """Invoke consumer orchestrator override (§K9.5)."""
    orchestrator_rel = config.checkpoints.orchestrator
    assert orchestrator_rel
    try:
        script_path = confine_path(repo_root, orchestrator_rel)
    except PathEscapeError:
        return _result(
            exit_code=4,
            mode=mode,
            dry_run=options.dry_run,
            manifest_rel=options.manifest,
            steps=[],
            error="refused",
        )
    if not _is_executable(script_path):
        return _result(
            exit_code=4,
            mode=mode,
            dry_run=options.dry_run,
            manifest_rel=options.manifest,
            steps=[],
            error="refused",
        )
    argv = [repo_relative(repo_root, script_path)]
    # Pass through verify-step flags after script name.
    if options.manifest:
        argv.extend(["--manifest", options.manifest])
    if options.step_id:
        argv.extend(["--step", options.step_id])
    if options.through_current:
        argv.append("--through")
        argv.append("current")
    if options.verify_all:
        argv.append("--all")
    if options.policy:
        argv.extend(["--policy", options.policy])
    if options.dry_run:
        argv.append("--dry-run")
    if options.emit_json:
        argv.append("--json")

    env = {"OVERSEER_REPO_ROOT": str(repo_root.resolve())}
    exec_result = executor.exec_argv(
        argv,
        cwd=str(repo_root.resolve()),
        env=env,
    )
    if options.emit_json:
        # Override must emit JSON; pass through stdout unchanged via stderr_extra hack — CLI handles.
        return VerifyStepResult(
            exit_code=exec_result.exit_code,
            json_payload=VerifyStepJson(
                ok=exec_result.exit_code == 0,
                exit_code=exec_result.exit_code,
                mode=mode,
                dry_run=options.dry_run,
                manifest=options.manifest,
                steps=[],
                error=None if exec_result.exit_code == 0 else "refused",
            ),
            stderr_extra=exec_result.stderr.decode("utf-8", errors="replace"),
        )
    return VerifyStepResult(
        exit_code=exec_result.exit_code,
        json_payload=VerifyStepJson(
            ok=exec_result.exit_code == 0,
            exit_code=exec_result.exit_code,
            mode=mode,
            dry_run=options.dry_run,
            manifest=options.manifest,
            steps=[],
            error=None,
        ),
    )
