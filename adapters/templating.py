"""Token substitution for governance doc templates — fixed key set, fail-closed."""

from __future__ import annotations

import re
from pathlib import Path

from adapters.config import OverseerConfig
from adapters.errors import ConfigError

TOKEN_PATTERN = re.compile(r"\{\{([a-z][a-z0-9_.]*)\}\}")

ALLOWED_TOKENS: frozenset[str] = frozenset(
    {
        "repo.name",
        "repo.root_relative_docs",
        "docs.handover",
        "docs.roadmap",
        "docs.coordination",
        "docs.standing_decisions",
        "docs.handover_path",
        "docs.roadmap_path",
        "docs.coordination_path",
        "docs.standing_decisions_path",
        "vcs.regime",
        "vcs.canonical",
        "vcs.git.remote",
        "vcs.git.main_branch",
        "vcs.git.mirror_branch",
        "vcs.git.feature_branch_pattern",
        "vcs.muse.staging_remote",
        "vcs.muse.main_branch",
    }
)


def build_token_map(config: OverseerConfig) -> dict[str, str]:
    """Build the substitution map from a validated ``OverseerConfig``."""
    docs_root = config.repo.root_relative_docs.rstrip("/")
    coordination = config.docs.coordination or ""
    standing = config.docs.standing_decisions

    def rel(doc: str) -> str:
        return f"{docs_root}/{doc}"

    return {
        "repo.name": config.repo.name,
        "repo.root_relative_docs": docs_root,
        "docs.handover": config.docs.handover,
        "docs.roadmap": config.docs.roadmap,
        "docs.coordination": coordination,
        "docs.standing_decisions": standing,
        "docs.handover_path": rel(config.docs.handover),
        "docs.roadmap_path": rel(config.docs.roadmap),
        "docs.coordination_path": rel(coordination) if coordination else "",
        "docs.standing_decisions_path": rel(standing),
        "vcs.regime": config.vcs.regime,
        "vcs.canonical": config.vcs.canonical,
        "vcs.git.remote": config.vcs.git.remote,
        "vcs.git.main_branch": config.vcs.git.main_branch,
        "vcs.git.mirror_branch": config.vcs.git.mirror_branch or "",
        "vcs.git.feature_branch_pattern": config.vcs.git.feature_branch_pattern,
        "vcs.muse.staging_remote": config.vcs.muse.staging_remote or "",
        "vcs.muse.main_branch": config.vcs.muse.main_branch or "",
    }


def substitute_tokens(
    text: str,
    token_map: dict[str, str],
    *,
    fail_on_unknown: bool = True,
) -> str:
    """Replace ``{{token}}`` placeholders using only keys present in ``token_map``."""
    unknown: set[str] = set()

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in ALLOWED_TOKENS:
            unknown.add(key)
            return match.group(0)
        if key not in token_map:
            unknown.add(key)
            return match.group(0)
        return token_map[key]

    result = TOKEN_PATTERN.sub(replacer, text)
    if fail_on_unknown and unknown:
        keys = ", ".join(sorted(unknown))
        raise ConfigError(f"unknown or unmapped template token(s): {keys}")
    return result


def render_template(template_path: Path, config: OverseerConfig) -> str:
    """Read a template file and return token-substituted content."""
    path = template_path.resolve()
    if not path.is_file():
        raise ConfigError("template file missing", str(path))
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read template: {exc}", str(path)) from exc
    return substitute_tokens(raw, build_token_map(config))
