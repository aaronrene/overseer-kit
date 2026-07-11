"""`.overseer/config.yaml` schema validation — fail-closed on unknown version/regime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from adapters.errors import ConfigError

SUPPORTED_CONFIG_VERSION = 1
SUPPORTED_REGIMES = frozenset({"muse+git-mirror", "muse-only", "git-only"})
SUPPORTED_CANONICAL = frozenset({"muse", "git"})
REVIEWER_MODES = frozenset({"agent", "human"})
REVIEWER_PROVIDERS = frozenset({"local", "api"})
REVIEWER_FALLBACK = frozenset({"human"})
HUMAN_ESCALATION_TOKENS = frozenset({"security", "irreversible", "real_money", "gates_tier3"})
DEFAULT_REVIEWER_MODEL = "thinking-high"
DEFAULT_REVIEWER_PROVIDER = "local"
DEFAULT_REVIEWER_FALLBACK = "human"
REVIEWER_MAPPING_KEYS = frozenset({"mode", "model", "provider", "fallback"})


@dataclass(frozen=True)
class GitConfig:
    remote: str
    main_branch: str
    mirror_branch: str | None
    feature_branch_pattern: str


@dataclass(frozen=True)
class MuseConfig:
    staging_remote: str | None
    main_branch: str | None
    working_dir: str | None = None


@dataclass(frozen=True)
class LaneDocsConfig:
    """One handover + roadmap pair (K8 multi-lane)."""

    handover: str
    roadmap: str
    handover_title: str
    roadmap_title: str


@dataclass(frozen=True)
class DocsConfig:
    handover: str
    roadmap: str
    coordination: str | None
    standing_decisions: str
    handover_title: str
    roadmap_title: str
    default_lane: str | None = None
    lanes: dict[str, LaneDocsConfig] | None = None


@dataclass(frozen=True)
class ThresholdsConfig:
    realign_max_commits: int
    drift_warn_only: bool


@dataclass(frozen=True)
class ReviewerConfig:
    mode: str
    model: str
    provider: str
    fallback: str


@dataclass(frozen=True)
class FreezeContractConfig:
    enabled: bool
    reviewer: ReviewerConfig
    human_escalation: list[str]


@dataclass(frozen=True)
class RepoConfig:
    name: str
    root_relative_docs: str


@dataclass(frozen=True)
class VcsConfig:
    regime: str
    canonical: str
    git: GitConfig
    muse: MuseConfig


@dataclass(frozen=True)
class OverseerConfig:
    overseer_config_version: int
    repo: RepoConfig
    vcs: VcsConfig
    docs: DocsConfig
    thresholds: ThresholdsConfig
    freeze_contract: FreezeContractConfig


def load_config(path: Path) -> OverseerConfig:
    """Parse and validate config; raise ``ConfigError`` on any violation."""
    path = path.resolve()
    if not path.is_file():
        raise ConfigError("config file missing", str(path))

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read config: {exc}", str(path)) from exc

    try:
        raw = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"unparseable YAML: {exc}", str(path)) from exc

    if not isinstance(raw, dict):
        raise ConfigError("config root must be a mapping", str(path))

    return _validate_config(raw, str(path))


def _require_mapping(data: Any, field: str, path: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ConfigError(f"{field} must be a mapping", path)
    return data


def _require_str(data: dict[str, Any], field: str, path: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field} must be a non-empty string", path)
    return value


def _optional_str(data: dict[str, Any], field: str) -> str | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"{field} must be a string or null")
    return value


def _validate_config(raw: dict[str, Any], path: str) -> OverseerConfig:
    version = raw.get("overseer_config_version")
    if not isinstance(version, int):
        raise ConfigError("overseer_config_version must be an integer", path)
    if version != SUPPORTED_CONFIG_VERSION:
        raise ConfigError(
            f"unsupported overseer_config_version {version} "
            f"(supported: {SUPPORTED_CONFIG_VERSION})",
            path,
        )

    repo_raw = _require_mapping(raw.get("repo"), "repo", path)
    repo = RepoConfig(
        name=_require_str(repo_raw, "name", path),
        root_relative_docs=_require_str(repo_raw, "root_relative_docs", path),
    )

    vcs_raw = _require_mapping(raw.get("vcs"), "vcs", path)
    regime = _require_str(vcs_raw, "regime", path)
    if regime not in SUPPORTED_REGIMES:
        raise ConfigError(
            f"unsupported vcs.regime {regime!r} (supported: {sorted(SUPPORTED_REGIMES)})",
            path,
        )

    canonical = _require_str(vcs_raw, "canonical", path)
    if canonical not in SUPPORTED_CANONICAL:
        raise ConfigError(f"unsupported vcs.canonical {canonical!r}", path)

    git_raw = _require_mapping(vcs_raw.get("git"), "vcs.git", path)
    muse_raw = _require_mapping(vcs_raw.get("muse"), "vcs.muse", path)

    git = GitConfig(
        remote=_require_str(git_raw, "remote", path),
        main_branch=_require_str(git_raw, "main_branch", path),
        mirror_branch=_optional_str(git_raw, "mirror_branch"),
        feature_branch_pattern=_require_str(git_raw, "feature_branch_pattern", path),
    )
    muse = MuseConfig(
        staging_remote=_optional_str(muse_raw, "staging_remote"),
        main_branch=_optional_str(muse_raw, "main_branch"),
        working_dir=_optional_str(muse_raw, "working_dir"),
    )
    _validate_muse_working_dir_shape(muse.working_dir, path)

    _validate_regime_fields(regime, canonical, git, muse, path)

    docs_raw = _require_mapping(raw.get("docs"), "docs", path)
    lanes = _parse_lanes(docs_raw.get("lanes"), path)
    default_lane = _optional_str(docs_raw, "default_lane")
    handover = _require_str(docs_raw, "handover", path)
    roadmap = _require_str(docs_raw, "roadmap", path)
    handover_title = _optional_str(docs_raw, "handover_title") or "Overseer Handover"
    roadmap_title = _optional_str(docs_raw, "roadmap_title") or "Roadmap"
    _validate_lanes_config(
        lanes=lanes,
        default_lane=default_lane,
        handover=handover,
        roadmap=roadmap,
        handover_title=handover_title,
        roadmap_title=roadmap_title,
        path=path,
    )
    docs = DocsConfig(
        handover=handover,
        roadmap=roadmap,
        coordination=_optional_str(docs_raw, "coordination"),
        standing_decisions=_require_str(docs_raw, "standing_decisions", path),
        handover_title=handover_title,
        roadmap_title=roadmap_title,
        default_lane=default_lane,
        lanes=lanes,
    )

    thresholds_raw = _require_mapping(raw.get("thresholds"), "thresholds", path)
    realign_max = thresholds_raw.get("realign_max_commits")
    if not isinstance(realign_max, int) or realign_max < 1:
        raise ConfigError("thresholds.realign_max_commits must be a positive integer", path)
    drift_warn = thresholds_raw.get("drift_warn_only")
    if not isinstance(drift_warn, bool):
        raise ConfigError("thresholds.drift_warn_only must be a boolean", path)
    thresholds = ThresholdsConfig(
        realign_max_commits=realign_max,
        drift_warn_only=drift_warn,
    )

    freeze_raw = _require_mapping(raw.get("freeze_contract"), "freeze_contract", path)
    enabled = freeze_raw.get("enabled")
    if not isinstance(enabled, bool):
        raise ConfigError("freeze_contract.enabled must be a boolean", path)
    reviewer = _parse_reviewer_config(freeze_raw.get("reviewer"), path)
    escalation = freeze_raw.get("human_escalation")
    if not isinstance(escalation, list) or not all(isinstance(x, str) for x in escalation):
        raise ConfigError("freeze_contract.human_escalation must be a list of strings", path)
    _validate_human_escalation(list(escalation), path)

    return OverseerConfig(
        overseer_config_version=version,
        repo=repo,
        vcs=VcsConfig(regime=regime, canonical=canonical, git=git, muse=muse),
        docs=docs,
        thresholds=thresholds,
        freeze_contract=FreezeContractConfig(
            enabled=enabled,
            reviewer=reviewer,
            human_escalation=list(escalation),
        ),
    )


def _validate_muse_working_dir_shape(working_dir: str | None, path: str) -> None:
    """Fail closed on absolute / ``..`` working_dir values (§K6.5.1)."""
    if working_dir is None:
        return
    text = working_dir.strip()
    if not text:
        raise ConfigError("vcs.muse.working_dir must be a non-empty string or null", path)
    candidate = Path(text)
    if candidate.is_absolute():
        raise ConfigError("vcs.muse.working_dir must be relative to the install root", path)
    if ".." in candidate.parts:
        raise ConfigError("vcs.muse.working_dir must not contain '..' path segments", path)


def _validate_human_escalation(tokens: list[str], path: str) -> None:
    for token in tokens:
        if token not in HUMAN_ESCALATION_TOKENS:
            raise ConfigError(
                f"unknown freeze_contract.human_escalation token {token!r}",
                path,
            )


def _parse_reviewer_config(raw_reviewer: Any, path: str) -> ReviewerConfig:
    """Parse nested reviewer mapping or legacy string (§K5.3)."""
    if isinstance(raw_reviewer, str):
        if raw_reviewer not in REVIEWER_MODES:
            raise ConfigError(
                f"freeze_contract.reviewer legacy string must be agent|human, got {raw_reviewer!r}",
                path,
            )
        return ReviewerConfig(
            mode=raw_reviewer,
            model=DEFAULT_REVIEWER_MODEL,
            provider=DEFAULT_REVIEWER_PROVIDER,
            fallback=DEFAULT_REVIEWER_FALLBACK,
        )

    reviewer_raw = _require_mapping(raw_reviewer, "freeze_contract.reviewer", path)
    extra = set(reviewer_raw) - REVIEWER_MAPPING_KEYS
    if extra:
        raise ConfigError(
            f"unknown freeze_contract.reviewer keys: {sorted(extra)}",
            path,
        )

    mode = _require_str(reviewer_raw, "mode", path)
    if mode not in REVIEWER_MODES:
        raise ConfigError(f"freeze_contract.reviewer.mode must be agent|human", path)

    if mode == "agent":
        # §K5.3: all required fields for agent mode must be present; missing → 2.
        for field_name in ("model", "provider", "fallback"):
            if field_name not in reviewer_raw:
                raise ConfigError(
                    f"freeze_contract.reviewer.{field_name} is required when mode is agent",
                    path,
                )
        model = reviewer_raw["model"]
        provider = reviewer_raw["provider"]
        fallback = reviewer_raw["fallback"]
        if not isinstance(model, str) or not model.strip():
            raise ConfigError("freeze_contract.reviewer.model must be a non-empty string", path)
        if provider not in REVIEWER_PROVIDERS:
            raise ConfigError("freeze_contract.reviewer.provider must be local|api", path)
        if fallback not in REVIEWER_FALLBACK:
            raise ConfigError("freeze_contract.reviewer.fallback must be human", path)
    else:
        # Human mode: model/provider/fallback optional; unused at runtime (§K5.2 step 6).
        model = reviewer_raw.get("model", DEFAULT_REVIEWER_MODEL)
        provider = reviewer_raw.get("provider", DEFAULT_REVIEWER_PROVIDER)
        fallback = reviewer_raw.get("fallback", DEFAULT_REVIEWER_FALLBACK)
        if not isinstance(model, str) or not model.strip():
            model = DEFAULT_REVIEWER_MODEL
        if provider not in REVIEWER_PROVIDERS:
            provider = DEFAULT_REVIEWER_PROVIDER
        if fallback not in REVIEWER_FALLBACK:
            fallback = DEFAULT_REVIEWER_FALLBACK

    return ReviewerConfig(
        mode=mode,
        model=model,
        provider=provider,
        fallback=fallback,
    )


def _parse_lanes(raw_lanes: Any, path: str) -> dict[str, LaneDocsConfig] | None:
    """Parse optional ``docs.lanes`` mapping (§K8)."""
    if raw_lanes is None:
        return None
    if not isinstance(raw_lanes, dict):
        raise ConfigError("docs.lanes must be a mapping", path)
    lanes: dict[str, LaneDocsConfig] = {}
    for lane_name, lane_raw in raw_lanes.items():
        if not isinstance(lane_name, str) or not lane_name.strip():
            raise ConfigError("docs.lanes keys must be non-empty strings", path)
        lane_map = _require_mapping(lane_raw, f"docs.lanes.{lane_name}", path)
        lanes[lane_name.strip()] = LaneDocsConfig(
            handover=_require_str(lane_map, "handover", path),
            roadmap=_require_str(lane_map, "roadmap", path),
            handover_title=_optional_str(lane_map, "handover_title") or "Overseer Handover",
            roadmap_title=_optional_str(lane_map, "roadmap_title") or "Roadmap",
        )
    return lanes


def _validate_lanes_config(
    *,
    lanes: dict[str, LaneDocsConfig] | None,
    default_lane: str | None,
    handover: str,
    roadmap: str,
    handover_title: str,
    roadmap_title: str,
    path: str,
) -> None:
    """Fail closed on inconsistent multi-lane docs config (§K8)."""
    if lanes is None:
        if default_lane is not None:
            raise ConfigError("docs.default_lane requires docs.lanes", path)
        return
    if not lanes:
        raise ConfigError("docs.lanes must not be empty when present", path)
    if not default_lane or not default_lane.strip():
        raise ConfigError("docs.default_lane is required when docs.lanes is set", path)
    default_lane = default_lane.strip()
    if default_lane not in lanes:
        raise ConfigError(
            f"docs.default_lane {default_lane!r} is not a key in docs.lanes",
            path,
        )
    default = lanes[default_lane]
    if handover != default.handover or roadmap != default.roadmap:
        raise ConfigError(
            "docs.handover and docs.roadmap must match docs.lanes[default_lane]",
            path,
        )
    if handover_title != default.handover_title or roadmap_title != default.roadmap_title:
        raise ConfigError(
            "docs.handover_title and docs.roadmap_title must match docs.lanes[default_lane]",
            path,
        )


def resolve_lane_docs(config: OverseerConfig, lane: str | None) -> LaneDocsConfig:
    """Return the handover/roadmap pair for ``lane`` or the default lane (§K8)."""
    docs = config.docs
    if docs.lanes is None:
        if lane is not None:
            raise ConfigError("docs.lanes is not configured; --lane is not supported")
        return LaneDocsConfig(
            handover=docs.handover,
            roadmap=docs.roadmap,
            handover_title=docs.handover_title,
            roadmap_title=docs.roadmap_title,
        )
    name = (lane or docs.default_lane or "").strip()
    if name not in docs.lanes:
        known = ", ".join(sorted(docs.lanes))
        raise ConfigError(f"unknown lane {name!r} (configured: {known})")
    return docs.lanes[name]


def list_configured_lanes(config: OverseerConfig) -> tuple[str, ...]:
    """Return sorted lane names; single implicit lane when ``docs.lanes`` is absent."""
    if config.docs.lanes is None:
        return ("default",)
    return tuple(sorted(config.docs.lanes))


def _validate_regime_fields(
    regime: str,
    canonical: str,
    git: GitConfig,
    muse: MuseConfig,
    path: str,
) -> None:
    if regime == "git-only":
        if canonical != "git":
            raise ConfigError("git-only regime requires vcs.canonical: git", path)
        if muse.staging_remote is not None or muse.main_branch is not None:
            raise ConfigError("git-only regime requires muse fields to be null", path)
        return

    if regime == "muse-only":
        if canonical != "muse":
            raise ConfigError("muse-only regime requires vcs.canonical: muse", path)
        if not muse.main_branch:
            raise ConfigError("muse-only regime requires vcs.muse.main_branch", path)
        return

    if regime == "muse+git-mirror":
        if canonical != "muse":
            raise ConfigError("muse+git-mirror regime requires vcs.canonical: muse", path)
        if not muse.main_branch:
            raise ConfigError("muse+git-mirror regime requires vcs.muse.main_branch", path)
        if not muse.staging_remote:
            raise ConfigError("muse+git-mirror regime requires vcs.muse.staging_remote", path)
        if not git.mirror_branch:
            raise ConfigError("muse+git-mirror regime requires vcs.git.mirror_branch", path)
