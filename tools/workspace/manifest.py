"""Load and validate ``.overseer/workspace.yaml`` (§MR.4)."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from adapters.config import OverseerConfig, load_config
from adapters.errors import ConfigError
from tools.workspace.types import (
    FORBIDDEN_IDENTITY_KEYS,
    SUPPORTED_REGIMES,
    WORKSPACE_ROLES,
    ManifestSource,
    WorkspaceLaneConfig,
    WorkspaceLoadError,
    WorkspaceManifest,
    WorkspaceMemberConfig,
)

_ENV_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
_SECRETISH = re.compile(
    r"(?i)(password|secret|token|api[_-]?key|bearer\s+[A-Za-z0-9._\-]+|"
    r"https?://[^/\s]+:[^@/\s]+@)"
)


def expand_root(raw: str, *, environ: dict[str, str] | None = None, home: Path | None = None) -> str:
    """Expand ``${ENV}`` / ``${ENV:-default}`` and leading ``~`` (§MR.4.3)."""
    env = environ if environ is not None else dict(os.environ)
    home_path = home if home is not None else Path.home()

    def _repl(match: re.Match[str]) -> str:
        key = match.group(1)
        default = match.group(2)
        if key in env and env[key] != "":
            return env[key]
        if default is not None:
            return default
        return ""

    expanded = _ENV_REF.sub(_repl, raw.strip())
    if expanded.startswith("~"):
        expanded = str(home_path) + expanded[1:]
    return expanded


def resolve_member_root(
    raw: str,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
) -> Path | None:
    """Resolve member root to an absolute path, or ``None`` when empty after expand."""
    text = expand_root(raw, environ=environ, home=home).strip()
    if not text:
        return None
    return Path(text).expanduser().resolve()


def _walk_forbid_identity(node: Any, path: str) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_l = str(key).strip().lower().replace("-", "_")
            if key_l in FORBIDDEN_IDENTITY_KEYS or "secret" in key_l or "password" in key_l:
                raise WorkspaceLoadError(
                    f"forbidden identity/secret key in manifest: {key}",
                    citation=path,
                )
            if isinstance(value, str) and _SECRETISH.search(value):
                raise WorkspaceLoadError(
                    f"secret-shaped value rejected at {key}",
                    citation=path,
                )
            _walk_forbid_identity(value, path)
    elif isinstance(node, list):
        for item in node:
            _walk_forbid_identity(item, path)
    elif isinstance(node, str) and _SECRETISH.search(node):
        raise WorkspaceLoadError("secret-shaped string rejected in manifest", citation=path)


def validate_manifest_dict(
    raw: dict[str, Any],
    *,
    source_path: Path,
    manifest_source: ManifestSource,
    expected_constellation_id: str | None = None,
) -> WorkspaceManifest:
    """Validate workspace.yaml mapping; fail closed on schema violations."""
    path = str(source_path)
    _walk_forbid_identity(raw, path)

    version = raw.get("overseer_workspace_version")
    if version != 1:
        raise WorkspaceLoadError(
            f"unsupported overseer_workspace_version {version!r} (supported: 1)",
            citation=path,
        )

    constellation_id = raw.get("id")
    if not isinstance(constellation_id, str) or not constellation_id.strip():
        raise WorkspaceLoadError("workspace id must be a non-empty string", citation=path)
    constellation_id = constellation_id.strip()
    if expected_constellation_id and constellation_id != expected_constellation_id:
        raise WorkspaceLoadError(
            f"manifest id {constellation_id!r} != constellation_id "
            f"{expected_constellation_id!r}",
            citation=path,
        )

    product_order_member = raw.get("product_order_member")
    if not isinstance(product_order_member, str) or not product_order_member.strip():
        raise WorkspaceLoadError("product_order_member must be a non-empty string", citation=path)
    product_order_member = product_order_member.strip()

    strict_markers = raw.get("strict_markers", True)
    if not isinstance(strict_markers, bool):
        raise WorkspaceLoadError("strict_markers must be a boolean", citation=path)

    strict_board_names = raw.get("strict_board_names", True)
    if not isinstance(strict_board_names, bool):
        raise WorkspaceLoadError("strict_board_names must be a boolean", citation=path)

    members_raw = raw.get("members")
    if not isinstance(members_raw, list) or not members_raw:
        raise WorkspaceLoadError("members must be a non-empty list", citation=path)

    members: list[WorkspaceMemberConfig] = []
    seen_ids: set[str] = set()
    product_order_count = 0
    for idx, row in enumerate(members_raw):
        if not isinstance(row, dict):
            raise WorkspaceLoadError(f"members[{idx}] must be a mapping", citation=path)
        mid = row.get("id")
        if not isinstance(mid, str) or not mid.strip():
            raise WorkspaceLoadError(f"members[{idx}].id must be a non-empty string", citation=path)
        mid = mid.strip()
        if mid in seen_ids:
            raise WorkspaceLoadError(f"duplicate member id {mid!r}", citation=path)
        seen_ids.add(mid)

        role = row.get("role")
        if role not in WORKSPACE_ROLES:
            raise WorkspaceLoadError(
                f"members[{idx}].role must be one of {sorted(WORKSPACE_ROLES)}",
                citation=path,
            )
        if role == "product_order":
            product_order_count += 1

        root_raw = row.get("root")
        if not isinstance(root_raw, str):
            raise WorkspaceLoadError(f"members[{idx}].root must be a string", citation=path)

        required = row.get("required", True)
        if not isinstance(required, bool):
            raise WorkspaceLoadError(f"members[{idx}].required must be a boolean", citation=path)

        relay = row.get("relay", False)
        if not isinstance(relay, bool):
            raise WorkspaceLoadError(f"members[{idx}].relay must be a boolean", citation=path)
        if role == "product_order" and relay:
            raise WorkspaceLoadError("product_order member must have relay: false", citation=path)

        regime = row.get("regime", None)
        if regime is not None and regime not in SUPPORTED_REGIMES:
            raise WorkspaceLoadError(
                f"members[{idx}].regime must be muse+git-mirror|muse-only|git-only|null",
                citation=path,
            )
        if regime is None and required:
            raise WorkspaceLoadError(
                f"members[{idx}].regime null only allowed when required: false",
                citation=path,
            )

        handover = row.get("handover")
        roadmap = row.get("roadmap")
        if handover is not None and not isinstance(handover, str):
            raise WorkspaceLoadError(f"members[{idx}].handover must be string or null", citation=path)
        if roadmap is not None and not isinstance(roadmap, str):
            raise WorkspaceLoadError(f"members[{idx}].roadmap must be string or null", citation=path)

        relay_lanes_raw = row.get("relay_lanes", [])
        if relay_lanes_raw is None:
            relay_lanes_raw = []
        if not isinstance(relay_lanes_raw, list) or not all(
            isinstance(x, str) for x in relay_lanes_raw
        ):
            raise WorkspaceLoadError(
                f"members[{idx}].relay_lanes must be a list of strings",
                citation=path,
            )

        members.append(
            WorkspaceMemberConfig(
                id=mid,
                role=str(role),
                root_raw=root_raw,
                regime=regime,
                required=required,
                relay=relay,
                handover=handover,
                roadmap=roadmap,
                relay_lanes=tuple(relay_lanes_raw),
            )
        )

    if product_order_count != 1:
        raise WorkspaceLoadError(
            f"exactly one product_order member required (got {product_order_count})",
            citation=path,
        )
    po = next(m for m in members if m.role == "product_order")
    if po.id != product_order_member:
        raise WorkspaceLoadError(
            f"product_order_member {product_order_member!r} does not match "
            f"product_order member id {po.id!r}",
            citation=path,
        )

    lanes_raw = raw.get("lanes")
    if not isinstance(lanes_raw, list) or not lanes_raw:
        raise WorkspaceLoadError("lanes must be a non-empty list", citation=path)

    lanes: list[WorkspaceLaneConfig] = []
    primary_count = 0
    lane_ids: set[str] = set()
    for idx, row in enumerate(lanes_raw):
        if not isinstance(row, dict):
            raise WorkspaceLoadError(f"lanes[{idx}] must be a mapping", citation=path)
        lid = row.get("id")
        if not isinstance(lid, str) or not lid.strip():
            raise WorkspaceLoadError(f"lanes[{idx}].id must be a non-empty string", citation=path)
        lid = lid.strip()
        if lid in lane_ids:
            raise WorkspaceLoadError(f"duplicate lane id {lid!r}", citation=path)
        lane_ids.add(lid)
        primary = row.get("primary", False)
        if not isinstance(primary, bool):
            raise WorkspaceLoadError(f"lanes[{idx}].primary must be a boolean", citation=path)
        if primary:
            primary_count += 1
        owner = row.get("owner_member")
        if owner is not None and (not isinstance(owner, str) or not owner.strip()):
            raise WorkspaceLoadError(
                f"lanes[{idx}].owner_member must be a string or null",
                citation=path,
            )
        if isinstance(owner, str):
            owner = owner.strip()
            if owner not in seen_ids:
                raise WorkspaceLoadError(
                    f"lanes[{idx}].owner_member {owner!r} is not a member id",
                    citation=path,
                )
        lanes.append(
            WorkspaceLaneConfig(
                id=lid,
                primary=primary,
                owner_member=owner if isinstance(owner, str) else None,
            )
        )

    if primary_count != 1:
        raise WorkspaceLoadError(
            f"exactly one primary lane required (got {primary_count})",
            citation=path,
        )

    return WorkspaceManifest(
        version=1,
        id=constellation_id,
        product_order_member=product_order_member,
        strict_markers=strict_markers,
        strict_board_names=strict_board_names,
        members=tuple(members),
        lanes=tuple(lanes),
        source_path=source_path.resolve(),
        manifest_source=manifest_source,
    )


def load_manifest_file(
    path: Path,
    *,
    manifest_source: ManifestSource,
    expected_constellation_id: str | None = None,
) -> WorkspaceManifest:
    """Read and validate a workspace.yaml file."""
    if not path.is_file():
        raise WorkspaceLoadError(f"workspace manifest missing: {path}", citation=str(path))
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorkspaceLoadError(f"unparseable workspace manifest: {exc}", citation=str(path)) from exc
    if not isinstance(raw, dict):
        raise WorkspaceLoadError("workspace manifest root must be a mapping", citation=str(path))
    return validate_manifest_dict(
        raw,
        source_path=path,
        manifest_source=manifest_source,
        expected_constellation_id=expected_constellation_id,
    )


def discover_manifest(
    config: OverseerConfig,
    repo_root: Path,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
) -> WorkspaceManifest | None:
    """Discover workspace manifest from member config pointer (§MR.4.2).

    Returns ``None`` when ``workspace:`` is absent (single-repo only).
    """
    ws = config.workspace
    if ws is None:
        return None

    env = environ if environ is not None else dict(os.environ)
    home_path = home if home is not None else Path.home()
    expected_id = ws.constellation_id

    # §MR.3.3 — env override replaces product_order path when set (checked early
    # so fixtures/CI can force a reviewed remapped file). Still validate id.
    env_manifest = env.get("OVERSEER_WORKSPACE_MANIFEST", "").strip()

    candidates: list[tuple[Path, ManifestSource]] = []
    if ws.manifest:
        candidates.append((Path(expand_root(ws.manifest, environ=env, home=home_path)), "config_manifest"))
    if ws.product_order_root:
        po_root = Path(expand_root(ws.product_order_root, environ=env, home=home_path))
        candidates.append((po_root / ".overseer" / "workspace.yaml", "product_order_root"))
    local = repo_root / ".overseer" / "workspace.yaml"
    if local.is_file():
        candidates.append((local, "local_workspace"))
    if env_manifest:
        candidates.append((Path(expand_root(env_manifest, environ=env, home=home_path)), "env_override"))
    home_idx = home_path / ".overseer" / "workspaces" / f"{expected_id}.yaml"
    candidates.append((home_idx, "home_index"))

    # Prefer env_override when set even if earlier candidates exist (§MR.3.3).
    if env_manifest:
        path = Path(expand_root(env_manifest, environ=env, home=home_path))
        return load_manifest_file(
            path,
            manifest_source="env_override",
            expected_constellation_id=expected_id,
        )

    for path, source in candidates:
        if path.is_file():
            return load_manifest_file(
                path,
                manifest_source=source,
                expected_constellation_id=expected_id,
            )

    raise WorkspaceLoadError(
        f"workspace configured (constellation_id={expected_id!r}) but no manifest found",
        citation=str(repo_root / ".overseer" / "config.yaml"),
    )


def load_member_config(root: Path) -> OverseerConfig:
    """Load a peer member's ``.overseer/config.yaml``."""
    cfg = root / ".overseer" / "config.yaml"
    try:
        return load_config(cfg)
    except ConfigError as exc:
        raise WorkspaceLoadError(str(exc), citation=str(cfg)) from exc
