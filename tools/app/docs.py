"""Living-doc reads for the app API (§Q0.7.3)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import OverseerConfig, load_config
from adapters.errors import ConfigError
from cli.digest import sha256_hex
from cli.docs_paths import living_doc_abs
from cli.paths import is_within_repo, repo_relative, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.app.envelope import ApiEnvelope, engine_failure, engine_success


def read_living_doc(
    *,
    repo_root: Path,
    config: OverseerConfig,
    doc_name: str,
) -> ApiEnvelope:
    """Read a configured living doc with path confinement."""
    try:
        abs_path = living_doc_abs(repo_root, config, doc_name)
    except ConfigError as exc:
        return engine_failure(exit_code=2, error="config", result={"message": str(exc)})

    if not is_within_repo(repo_root, abs_path):
        return engine_failure(exit_code=4, error="path", result=None)

    if not abs_path.is_file():
        return engine_failure(exit_code=4, error="missing", result=None)

    raw = abs_path.read_bytes()
    rel = repo_relative(repo_root, abs_path)
    return engine_success(
        {
            "path": rel,
            "text": raw.decode("utf-8"),
            "sha256": sha256_hex(raw),
        }
    )


def read_roadmap(*, repo_root: Path, config: OverseerConfig) -> ApiEnvelope:
    """Return the configured ROADMAP living doc."""
    return read_living_doc(repo_root=repo_root, config=config, doc_name=config.docs.roadmap)


def read_handover(*, repo_root: Path, config: OverseerConfig) -> ApiEnvelope:
    """Return the configured HANDOVER living doc."""
    return read_living_doc(repo_root=repo_root, config=config, doc_name=config.docs.handover)


def load_repo_config(repo_root: Path, config_arg: str | None = None) -> tuple[OverseerConfig | None, ApiEnvelope | None]:
    """Load config or return a refusal envelope."""
    config_path = resolve_config_path(repo_root, config_arg)
    if not is_within_repo(repo_root, config_path):
        return None, engine_failure(exit_code=4, error="config", result=None)
    try:
        return load_config(config_path), None
    except ConfigError as exc:
        return None, engine_failure(exit_code=2, error="config", result={"message": format_config_error(exc, repo_root)})


def resolve_app_repo(cwd: Path, repo_arg: str | None) -> Path:
    """Resolve repo root for app handlers."""
    return resolve_repo_root(cwd=cwd, repo_arg=repo_arg, command="app")
