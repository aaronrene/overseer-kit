"""Living-doc path joins and ``root_relative_docs`` normalization (§K6.5.2)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import OverseerConfig
from adapters.errors import ConfigError


def normalize_docs_root(root_relative_docs: str) -> str:
    """Return stripped docs-root; ``\".\"`` is the only repo-root sentinel."""
    return root_relative_docs.strip()


def join_docs_rel(root_relative_docs: str, doc_name: str) -> str:
    """Join docs root and filename into a repo-relative POSIX path.

    When ``root_relative_docs`` is exactly ``\".\"`` (after strip), return the bare
    ``doc_name`` (never ``./name`` or ``/name``).
    """
    root = normalize_docs_root(root_relative_docs)
    if not root:
        raise ConfigError("repo.root_relative_docs must be a non-empty string")
    if root == ".":
        return doc_name
    return f"{root.rstrip('/')}/{doc_name}"


def living_doc_destinations(config: OverseerConfig) -> frozenset[str]:
    """Return footprint destination paths for configured living docs (all lanes)."""
    docs_root = config.repo.root_relative_docs
    docs: set[str] = set()
    if config.docs.lanes is None:
        docs.add(join_docs_rel(docs_root, config.docs.handover))
        docs.add(join_docs_rel(docs_root, config.docs.roadmap))
    else:
        for lane in config.docs.lanes.values():
            docs.add(join_docs_rel(docs_root, lane.handover))
            docs.add(join_docs_rel(docs_root, lane.roadmap))
    if config.docs.coordination:
        docs.add(join_docs_rel(docs_root, config.docs.coordination))
    return frozenset(docs)


def lane_living_doc_abs(
    repo_root: Path,
    config: OverseerConfig,
    lane_docs: LaneDocsConfig,
    doc_name: str,
) -> Path:
    """Absolute path to a lane living doc under ``repo_root``."""
    return repo_root / join_docs_rel(config.repo.root_relative_docs, doc_name)


def living_doc_abs(repo_root: Path, config: OverseerConfig, doc_name: str) -> Path:
    """Absolute path to a living doc under ``repo_root``."""
    return repo_root / join_docs_rel(config.repo.root_relative_docs, doc_name)


def validate_muse_working_dir(repo_root: Path, working_dir: str | None) -> Path | None:
    """Resolve ``vcs.muse.working_dir`` inside ``repo_root``; raise ``ConfigError`` on escape.

    Returns the absolute Muse cwd, or ``None`` when ``working_dir`` is unset (install root).
    Escape / absolute-outside-root → ``ConfigError`` (CLI maps to exit ``2``).
    """
    if working_dir is None:
        return None
    text = working_dir.strip()
    if not text:
        raise ConfigError("vcs.muse.working_dir must be a non-empty string or null")
    candidate = Path(text)
    if candidate.is_absolute():
        raise ConfigError("vcs.muse.working_dir must be relative to the install root")
    if ".." in candidate.parts:
        raise ConfigError("vcs.muse.working_dir must not contain '..' path segments")
    root = repo_root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ConfigError("vcs.muse.working_dir escapes install root") from exc
    return resolved
