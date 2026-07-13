"""Policy and manifest loaders (§K9.3 / §K9.4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.checkpoints.ids import is_valid_step_id
from tools.checkpoints.types import ManifestState, PolicyState, StepDef, StepState


class CheckpointSchemaError(ValueError):
    """Raised when policy or manifest shape is invalid."""


def load_policy(path: Path) -> PolicyState:
    """Load and validate ``policy/checkpoints.yaml``."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CheckpointSchemaError(f"cannot read policy: {exc}") from exc
    except yaml.YAMLError as exc:
        raise CheckpointSchemaError(f"unparseable policy YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise CheckpointSchemaError("policy root must be a mapping")

    version = raw.get("version")
    if not isinstance(version, int) or version != 1:
        raise CheckpointSchemaError("policy version must be integer 1")

    tokens_raw = raw.get("placeholder_tokens", [])
    if tokens_raw is None:
        tokens_raw = []
    if not isinstance(tokens_raw, list) or not all(isinstance(x, str) for x in tokens_raw):
        raise CheckpointSchemaError("placeholder_tokens must be a list of strings")
    placeholder_tokens = list(tokens_raw)

    steps_raw = raw.get("steps")
    if not isinstance(steps_raw, dict):
        raise CheckpointSchemaError("policy steps must be a mapping")
    steps: dict[str, StepDef] = {}
    for step_id, step_raw in steps_raw.items():
        if not is_valid_step_id(step_id):
            raise CheckpointSchemaError(f"invalid step_id {step_id!r}")
        if not isinstance(step_raw, dict):
            raise CheckpointSchemaError(f"step {step_id!r} must be a mapping")
        verify_script = step_raw.get("verify_script")
        if verify_script is not None and not isinstance(verify_script, str):
            raise CheckpointSchemaError(f"step {step_id!r} verify_script must be a string")
        description = step_raw.get("description")
        if description is not None and not isinstance(description, str):
            raise CheckpointSchemaError(f"step {step_id!r} description must be a string")
        steps[step_id] = StepDef(
            verify_script=verify_script or "",
            description=description,
        )

    templates_raw = raw.get("templates")
    if not isinstance(templates_raw, dict):
        raise CheckpointSchemaError("policy templates must be a mapping")
    templates: dict[str, list[str]] = {}
    for template_id, template_raw in templates_raw.items():
        if not is_valid_step_id(template_id):
            raise CheckpointSchemaError(f"invalid template_id {template_id!r}")
        if not isinstance(template_raw, dict):
            raise CheckpointSchemaError(f"template {template_id!r} must be a mapping")
        steps_list = template_raw.get("steps")
        if not isinstance(steps_list, list) or not steps_list:
            raise CheckpointSchemaError(f"template {template_id!r} steps must be a non-empty list")
        for sid in steps_list:
            if not isinstance(sid, str) or not is_valid_step_id(sid):
                raise CheckpointSchemaError(f"invalid step id in template {template_id!r}")
        templates[template_id] = list(steps_list)

    overrides_raw = raw.get("overrides") or {}
    if not isinstance(overrides_raw, dict):
        raise CheckpointSchemaError("overrides must be a mapping")
    overrides_default = overrides_raw.get("default") or {}
    if not isinstance(overrides_default, dict):
        raise CheckpointSchemaError("overrides.default must be a mapping")
    overrides_by_template: dict[str, dict[str, Any]] = {}
    for key, value in overrides_raw.items():
        if key == "default":
            continue
        if not isinstance(value, dict):
            raise CheckpointSchemaError(f"overrides.{key} must be a mapping")
        overrides_by_template[key] = dict(value)

    return PolicyState(
        version=version,
        placeholder_tokens=placeholder_tokens,
        steps=steps,
        templates=templates,
        overrides_default=dict(overrides_default),
        overrides_by_template=overrides_by_template,
        source_path=str(path),
    )


def load_manifest(path: Path) -> ManifestState:
    """Load and validate active manifest."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CheckpointSchemaError(f"cannot read manifest: {exc}") from exc
    except yaml.YAMLError as exc:
        raise CheckpointSchemaError(f"unparseable manifest YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise CheckpointSchemaError("manifest root must be a mapping")

    schema_version = raw.get("schema_version")
    if not isinstance(schema_version, int) or schema_version != 1:
        raise CheckpointSchemaError("manifest schema_version must be integer 1")

    template_id = raw.get("template_id")
    if not isinstance(template_id, str) or not is_valid_step_id(template_id):
        raise CheckpointSchemaError("manifest template_id invalid")

    slug = raw.get("slug")
    if not isinstance(slug, str) or not slug.strip():
        raise CheckpointSchemaError("manifest slug must be a non-empty string")

    current_step = raw.get("current_step")
    if not isinstance(current_step, str) or not is_valid_step_id(current_step):
        raise CheckpointSchemaError("manifest current_step invalid")

    meta = raw.get("meta") or {}
    if not isinstance(meta, dict):
        raise CheckpointSchemaError("manifest meta must be a mapping")

    steps_raw = raw.get("steps")
    if not isinstance(steps_raw, dict):
        raise CheckpointSchemaError("manifest steps must be a mapping")
    steps: dict[str, StepState] = {}
    for step_id, step_raw in steps_raw.items():
        if not isinstance(step_raw, dict):
            raise CheckpointSchemaError(f"manifest step {step_id!r} must be a mapping")
        verified = step_raw.get("verified", False)
        if not isinstance(verified, bool):
            raise CheckpointSchemaError(f"manifest step {step_id!r} verified must be boolean")
        verified_at = step_raw.get("verified_at")
        if verified_at is not None and not isinstance(verified_at, str):
            raise CheckpointSchemaError(f"manifest step {step_id!r} verified_at must be string or null")
        artifact_sha256 = step_raw.get("artifact_sha256")
        if artifact_sha256 is not None and not isinstance(artifact_sha256, str):
            raise CheckpointSchemaError(
                f"manifest step {step_id!r} artifact_sha256 must be string or null"
            )
        steps[step_id] = StepState(
            verified=verified,
            verified_at=verified_at,
            artifact_sha256=artifact_sha256,
        )

    return ManifestState(
        schema_version=schema_version,
        template_id=template_id,
        slug=slug,
        current_step=current_step,
        steps=steps,
        meta=dict(meta),
        source_path=str(path),
    )


def resolve_template_steps(policy: PolicyState, manifest: ManifestState) -> list[str]:
    """Resolve ordered template list ``T``; raise on missing template or bad refs."""
    if manifest.template_id not in policy.templates:
        raise CheckpointSchemaError(f"unknown template_id {manifest.template_id!r}")
    template_steps = policy.templates[manifest.template_id]
    for step_id in template_steps:
        step_def = policy.steps.get(step_id)
        if step_def is None or not step_def.verify_script.strip():
            raise CheckpointSchemaError(
                f"template step {step_id!r} missing from policy.steps or empty verify_script"
            )
    if manifest.current_step not in template_steps:
        raise CheckpointSchemaError("manifest current_step not in template")
    for step_id in template_steps:
        if step_id not in manifest.steps:
            raise CheckpointSchemaError(f"manifest missing step {step_id!r}")
    return template_steps


def merge_overrides(policy: PolicyState, template_id: str) -> dict[str, Any]:
    """Shallow merge overrides.default then template-specific."""
    merged = dict(policy.overrides_default)
    if template_id in policy.overrides_by_template:
        merged.update(policy.overrides_by_template[template_id])
    return merged


def manifest_to_yaml(manifest: ManifestState) -> str:
    """Serialize manifest for atomic write."""
    data: dict[str, Any] = {
        "schema_version": manifest.schema_version,
        "template_id": manifest.template_id,
        "slug": manifest.slug,
        "current_step": manifest.current_step,
        "meta": manifest.meta,
        "steps": {},
    }
    for step_id, state in manifest.steps.items():
        data["steps"][step_id] = {
            "verified": state.verified,
            "verified_at": state.verified_at,
            "artifact_sha256": state.artifact_sha256,
        }
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def render_progress(manifest: ManifestState, template_steps: list[str]) -> str:
    """Deterministic PROGRESS.md renderer (§K9.4)."""
    lines = [
        f"# Progress — {manifest.slug}",
        "",
        f"Template: `{manifest.template_id}`",
        f"Current step: `{manifest.current_step}`",
        "",
        "## Steps",
        "",
    ]
    for step_id in template_steps:
        state = manifest.steps.get(step_id)
        if state is None:
            mark = "?"
        elif state.verified:
            mark = "✓"
        else:
            mark = "·"
        lines.append(f"- [{mark}] `{step_id}`")
    lines.append("")
    return "\n".join(lines)
