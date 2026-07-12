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
CHECKPOINTS_KEYS = frozenset(
    {
        "enabled",
        "policy",
        "active_manifest",
        "progress",
        "orchestrator",
        "allow_hand_verified",
    }
)
HONESTY_KEYS = frozenset(
    {
        "enabled",
        "ledger",
        "roles_file",
        "require_verdict_on",
        "require_l1_evidence",
        "allow_signed_approval",
        "ci_reexecutor",
        "require_agent_signature",
    }
)
MODULES_GOVERNANCE_KEYS = frozenset({"enabled"})
MODULES_CHECKPOINTS_KEYS = frozenset({"enabled"})
MODULES_HONESTY_KEYS = frozenset({"enabled"})
EXTENSION_KEYS = frozenset({"id", "schema_version", "config_path"})
HOOK_NAMES = frozenset({"board_done", "handoff", "register"})
GOVERNANCE_GATES_SURFACES = frozenset({"status", "governance-sync", "handover-paste"})
GOVERNANCE_GATES_KEYS = frozenset(
    {
        "remind",
        "freeze_review",
        "build_verification",
        "surfaces",
    }
)
L1_EVIDENCE_MODES = frozenset({"off", "warn", "require"})


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
class CheckpointsConfig:
    """L1 checkpoint module settings (§K9.2)."""

    enabled: bool = False
    policy: str | None = None
    active_manifest: str | None = None
    progress: str | None = None
    orchestrator: str | None = None
    allow_hand_verified: bool = False


@dataclass(frozen=True)
class HonestyConfig:
    """L2 honesty module settings (§K9.2) — parsed for forward compat; K10 builds CLI."""

    enabled: bool = False
    ledger: str | None = None
    roles_file: str | None = None
    require_verdict_on: frozenset[str] = frozenset({"board_done", "handoff", "register"})
    require_l1_evidence: str = "warn"
    allow_signed_approval: bool = False
    ci_reexecutor: str | None = None
    require_agent_signature: bool = False


@dataclass(frozen=True)
class ModulesConfig:
    """Optional mirror of section enable flags (§K9.2)."""

    governance_enabled: bool = True
    checkpoints_enabled: bool | None = None
    honesty_enabled: bool | None = None


@dataclass(frozen=True)
class GovernanceGatesConfig:
    """Governance gate reminder settings (§KH1.9)."""

    remind: bool = True
    freeze_review_required: bool = True
    build_verification_required: bool = True
    surfaces: frozenset[str] = frozenset(GOVERNANCE_GATES_SURFACES)


@dataclass(frozen=True)
class ExtensionEntry:
    """One extensions[] escape-hatch entry (§K9.2)."""

    id: str
    schema_version: int
    config_path: str


@dataclass(frozen=True)
class OverseerConfig:
    overseer_config_version: int
    repo: RepoConfig
    vcs: VcsConfig
    docs: DocsConfig
    thresholds: ThresholdsConfig
    freeze_contract: FreezeContractConfig
    checkpoints: CheckpointsConfig = CheckpointsConfig()
    honesty: HonestyConfig = HonestyConfig()
    modules: ModulesConfig | None = None
    extensions: tuple[ExtensionEntry, ...] = ()
    extension_warnings: tuple[str, ...] = ()
    governance_gates: GovernanceGatesConfig = GovernanceGatesConfig()


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

    checkpoints, honesty, modules, extensions, extension_warnings = _parse_k9_modules(raw, path)
    if honesty.require_agent_signature and regime == "git-only":
        raise ConfigError(
            "honesty.require_agent_signature is forbidden under git-only",
            path,
            exit_code=26,
        )
    governance_gates = _parse_governance_gates(raw.get("governance_gates"), path)

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
        checkpoints=checkpoints,
        honesty=honesty,
        modules=modules,
        extensions=extensions,
        extension_warnings=extension_warnings,
        governance_gates=governance_gates,
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


def _validate_repo_relative_path(value: str, field: str, path: str) -> None:
    """Reject absolute paths and ``..`` segments in config path fields."""
    text = value.strip()
    if not text:
        raise ConfigError(f"{field} must be a non-empty string", path)
    candidate = Path(text)
    if candidate.is_absolute():
        raise ConfigError(f"{field} must be repo-relative", path)
    if ".." in candidate.parts:
        raise ConfigError(f"{field} must not contain '..' path segments", path)


def _parse_k9_modules(
    raw: dict[str, Any],
    path: str,
) -> tuple[CheckpointsConfig, HonestyConfig, ModulesConfig | None, tuple[ExtensionEntry, ...], tuple[str, ...]]:
    """Parse optional K9 checkpoints/honesty/modules/extensions (§K9.2)."""
    checkpoints = _parse_checkpoints(raw.get("checkpoints"), path)
    honesty = _parse_honesty(raw.get("honesty"), path)
    modules = _parse_modules(raw.get("modules"), path)
    extensions, extension_warnings = _parse_extensions(raw.get("extensions"), path)

    if modules is not None:
        if modules.governance_enabled is False:
            raise ConfigError("modules.governance.enabled cannot be false", path)
        if modules.checkpoints_enabled is not None and modules.checkpoints_enabled != checkpoints.enabled:
            raise ConfigError(
                "modules.checkpoints.enabled must equal checkpoints.enabled",
                path,
            )
        if modules.honesty_enabled is not None and modules.honesty_enabled != honesty.enabled:
            raise ConfigError(
                "modules.honesty.enabled must equal honesty.enabled",
                path,
            )

    return checkpoints, honesty, modules, extensions, extension_warnings


def _parse_checkpoints(raw_checkpoints: Any, path: str) -> CheckpointsConfig:
    if raw_checkpoints is None:
        return CheckpointsConfig()
    cp_raw = _require_mapping(raw_checkpoints, "checkpoints", path)
    extra = set(cp_raw) - CHECKPOINTS_KEYS
    if extra:
        raise ConfigError(f"unknown checkpoints keys: {sorted(extra)}", path)

    enabled = cp_raw.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ConfigError("checkpoints.enabled must be a boolean", path)

    policy = _optional_str(cp_raw, "policy")
    if policy is not None:
        _validate_repo_relative_path(policy, "checkpoints.policy", path)
    active_manifest = _optional_str(cp_raw, "active_manifest")
    if active_manifest is not None:
        _validate_repo_relative_path(active_manifest, "checkpoints.active_manifest", path)
    progress = _optional_str(cp_raw, "progress")
    if progress is not None:
        _validate_repo_relative_path(progress, "checkpoints.progress", path)
    orchestrator = _optional_str(cp_raw, "orchestrator")
    if orchestrator is not None:
        _validate_repo_relative_path(orchestrator, "checkpoints.orchestrator", path)

    allow_hand = cp_raw.get("allow_hand_verified", False)
    if not isinstance(allow_hand, bool):
        raise ConfigError("checkpoints.allow_hand_verified must be a boolean", path)
    if allow_hand:
        raise ConfigError("checkpoints.allow_hand_verified is forbidden", path)

    if enabled and (policy is None or not policy.strip()):
        raise ConfigError("checkpoints.enabled requires non-empty checkpoints.policy", path)

    return CheckpointsConfig(
        enabled=enabled,
        policy=policy,
        active_manifest=active_manifest,
        progress=progress,
        orchestrator=orchestrator,
        allow_hand_verified=allow_hand,
    )


def _parse_honesty(raw_honesty: Any, path: str) -> HonestyConfig:
    if raw_honesty is None:
        return HonestyConfig()
    h_raw = _require_mapping(raw_honesty, "honesty", path)
    extra = set(h_raw) - HONESTY_KEYS
    if extra:
        raise ConfigError(f"unknown honesty keys: {sorted(extra)}", path)

    enabled = h_raw.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ConfigError("honesty.enabled must be a boolean", path)

    ledger = _optional_str(h_raw, "ledger")
    if ledger is not None:
        _validate_repo_relative_path(ledger, "honesty.ledger", path)
    roles_file = _optional_str(h_raw, "roles_file")
    if roles_file is not None:
        _validate_repo_relative_path(roles_file, "honesty.roles_file", path)
    ci_reexecutor = _optional_str(h_raw, "ci_reexecutor")
    if ci_reexecutor is not None:
        _validate_repo_relative_path(ci_reexecutor, "honesty.ci_reexecutor", path)

    require_l1 = h_raw.get("require_l1_evidence", "warn")
    if not isinstance(require_l1, str) or require_l1 not in L1_EVIDENCE_MODES:
        raise ConfigError("honesty.require_l1_evidence must be off|warn|require", path)

    allow_signed = h_raw.get("allow_signed_approval", False)
    if not isinstance(allow_signed, bool):
        raise ConfigError("honesty.allow_signed_approval must be a boolean", path)

    require_agent_signature = h_raw.get("require_agent_signature", False)
    if not isinstance(require_agent_signature, bool):
        raise ConfigError("honesty.require_agent_signature must be a boolean", path)

    require_verdict_on = _parse_require_verdict_on(h_raw.get("require_verdict_on"), path)

    if enabled and (ledger is None or not ledger.strip()):
        raise ConfigError("honesty.enabled requires non-empty honesty.ledger", path)

    return HonestyConfig(
        enabled=enabled,
        ledger=ledger,
        roles_file=roles_file,
        require_verdict_on=require_verdict_on,
        require_l1_evidence=require_l1,
        allow_signed_approval=allow_signed,
        ci_reexecutor=ci_reexecutor,
        require_agent_signature=require_agent_signature,
    )


def _parse_require_verdict_on(raw_value: Any, path: str) -> frozenset[str]:
    if raw_value is None:
        return frozenset(HOOK_NAMES)
    if not isinstance(raw_value, list):
        raise ConfigError("honesty.require_verdict_on must be a list or null", path)
    if not raw_value:
        raise ConfigError("honesty.require_verdict_on must not be empty", path)
    hooks: set[str] = set()
    for item in raw_value:
        if not isinstance(item, str) or item not in HOOK_NAMES:
            raise ConfigError(
                "honesty.require_verdict_on entries must be board_done|handoff|register",
                path,
            )
        hooks.add(item)
    return frozenset(hooks)


def _parse_modules(raw_modules: Any, path: str) -> ModulesConfig | None:
    if raw_modules is None:
        return None
    m_raw = _require_mapping(raw_modules, "modules", path)
    allowed = {"governance", "checkpoints", "honesty"}
    extra = set(m_raw) - allowed
    if extra:
        raise ConfigError(f"unknown modules keys: {sorted(extra)}", path)

    governance_enabled = True
    if "governance" in m_raw:
        gov_raw = _require_mapping(m_raw["governance"], "modules.governance", path)
        gov_extra = set(gov_raw) - MODULES_GOVERNANCE_KEYS
        if gov_extra:
            raise ConfigError(f"unknown modules.governance keys: {sorted(gov_extra)}", path)
        gov_enabled = gov_raw.get("enabled", True)
        if not isinstance(gov_enabled, bool):
            raise ConfigError("modules.governance.enabled must be a boolean", path)
        governance_enabled = gov_enabled

    checkpoints_enabled: bool | None = None
    if "checkpoints" in m_raw:
        cp_raw = _require_mapping(m_raw["checkpoints"], "modules.checkpoints", path)
        cp_extra = set(cp_raw) - MODULES_CHECKPOINTS_KEYS
        if cp_extra:
            raise ConfigError(f"unknown modules.checkpoints keys: {sorted(cp_extra)}", path)
        value = cp_raw.get("enabled")
        if not isinstance(value, bool):
            raise ConfigError("modules.checkpoints.enabled must be a boolean", path)
        checkpoints_enabled = value

    honesty_enabled: bool | None = None
    if "honesty" in m_raw:
        h_raw = _require_mapping(m_raw["honesty"], "modules.honesty", path)
        h_extra = set(h_raw) - MODULES_HONESTY_KEYS
        if h_extra:
            raise ConfigError(f"unknown modules.honesty keys: {sorted(h_extra)}", path)
        value = h_raw.get("enabled")
        if not isinstance(value, bool):
            raise ConfigError("modules.honesty.enabled must be a boolean", path)
        honesty_enabled = value

    return ModulesConfig(
        governance_enabled=governance_enabled,
        checkpoints_enabled=checkpoints_enabled,
        honesty_enabled=honesty_enabled,
    )


def _parse_governance_gates(raw_gates: Any, path: str) -> GovernanceGatesConfig:
    """Parse optional ``governance_gates`` section (§KH1.9)."""
    if raw_gates is None:
        return GovernanceGatesConfig()
    gates_raw = _require_mapping(raw_gates, "governance_gates", path)
    extra = set(gates_raw) - GOVERNANCE_GATES_KEYS
    if extra:
        raise ConfigError(f"unknown governance_gates keys: {sorted(extra)}", path)

    remind = gates_raw.get("remind", True)
    if not isinstance(remind, bool):
        raise ConfigError("governance_gates.remind must be a boolean", path)

    freeze_required = True
    if "freeze_review" in gates_raw:
        freeze_raw = _require_mapping(gates_raw["freeze_review"], "governance_gates.freeze_review", path)
        freeze_extra = set(freeze_raw) - {"required_before_auto"}
        if freeze_extra:
            raise ConfigError(
                f"unknown governance_gates.freeze_review keys: {sorted(freeze_extra)}",
                path,
            )
        value = freeze_raw.get("required_before_auto", True)
        if not isinstance(value, bool):
            raise ConfigError(
                "governance_gates.freeze_review.required_before_auto must be a boolean",
                path,
            )
        freeze_required = value

    build_required = True
    if "build_verification" in gates_raw:
        build_raw = _require_mapping(
            gates_raw["build_verification"],
            "governance_gates.build_verification",
            path,
        )
        build_extra = set(build_raw) - {"required_before_done"}
        if build_extra:
            raise ConfigError(
                f"unknown governance_gates.build_verification keys: {sorted(build_extra)}",
                path,
            )
        value = build_raw.get("required_before_done", True)
        if not isinstance(value, bool):
            raise ConfigError(
                "governance_gates.build_verification.required_before_done must be a boolean",
                path,
            )
        build_required = value

    surfaces: frozenset[str] = frozenset(GOVERNANCE_GATES_SURFACES)
    if "surfaces" in gates_raw:
        raw_surfaces = gates_raw["surfaces"]
        if not isinstance(raw_surfaces, list) or not raw_surfaces:
            raise ConfigError("governance_gates.surfaces must be a non-empty list", path)
        parsed: set[str] = set()
        for item in raw_surfaces:
            if not isinstance(item, str) or item not in GOVERNANCE_GATES_SURFACES:
                raise ConfigError(
                    "governance_gates.surfaces entries must be status|governance-sync|handover-paste",
                    path,
                )
            parsed.add(item)
        surfaces = frozenset(parsed)

    return GovernanceGatesConfig(
        remind=remind,
        freeze_review_required=freeze_required,
        build_verification_required=build_required,
        surfaces=surfaces,
    )


def _parse_extensions(
    raw_extensions: Any,
    path: str,
) -> tuple[tuple[ExtensionEntry, ...], tuple[str, ...]]:
    if raw_extensions is None:
        return (), ()
    if not isinstance(raw_extensions, list):
        raise ConfigError("extensions must be a list", path)

    entries: list[ExtensionEntry] = []
    warnings: list[str] = []
    for index, item in enumerate(raw_extensions):
        prefix = f"extensions[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{prefix} must be a mapping", path)
        extra = set(item) - EXTENSION_KEYS
        if extra:
            raise ConfigError(f"unknown {prefix} keys: {sorted(extra)}", path)
        ext_id = item.get("id")
        if not isinstance(ext_id, str) or not ext_id.strip():
            raise ConfigError(f"{prefix}.id must be a non-empty string", path)
        schema_version = item.get("schema_version")
        if not isinstance(schema_version, int):
            raise ConfigError(f"{prefix}.schema_version must be an integer", path)
        config_path = item.get("config_path")
        if not isinstance(config_path, str) or not config_path.strip():
            raise ConfigError(f"{prefix}.config_path must be a non-empty string", path)
        _validate_repo_relative_path(config_path, f"{prefix}.config_path", path)
        entries.append(
            ExtensionEntry(id=ext_id.strip(), schema_version=schema_version, config_path=config_path)
        )
        warnings.append(
            f"extensions[{index}] id={ext_id!r} schema_version={schema_version} ignored (v1 registry empty)"
        )
    return tuple(entries), tuple(warnings)
