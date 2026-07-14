"""Hosted dashboard config block parsing (§HGD.10.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tools.hosted_dashboard.hosts import validate_extra_hosts
from tools.hosted_dashboard.validators import (
    DEFAULT_ORG_ENUMERATION_CAP,
    validate_allowlist,
)

HOSTED_DASHBOARD_KEYS = frozenset(
    {
        "enabled",
        "allow_non_loopback",
        "cors_origins",
        "org_allowlist",
        "sources",
        "enumeration_cap",
        "musehub_hosts",
        "musehub_base_url",
        "max_doc_bytes",
    }
)
SOURCE_KEYS = frozenset(
    {
        "github_contents",
        "github_meta",
        "github_checks_advisory",
        "musehub_read",
    }
)


class HostedDashboardConfigError(ValueError):
    """Fail-closed hosted_dashboard config error."""


@dataclass(frozen=True)
class HostedSourcesConfig:
    github_contents: bool = True
    github_meta: bool = True
    github_checks_advisory: bool = False
    musehub_read: bool = False


@dataclass(frozen=True)
class HostedDashboardConfig:
    """Optional ``hosted_dashboard`` section — default inert."""

    enabled: bool = False
    allow_non_loopback: bool = False
    cors_origins: tuple[str, ...] = ()
    org_allowlist: tuple[str, ...] = ()
    sources: HostedSourcesConfig = field(default_factory=HostedSourcesConfig)
    enumeration_cap: int = DEFAULT_ORG_ENUMERATION_CAP
    musehub_hosts: frozenset[str] = field(default_factory=frozenset)
    musehub_base_url: str | None = None
    max_doc_bytes: int = 2_000_000

    @property
    def allowlist_pairs(self) -> list[tuple[str, str | None]]:
        return validate_allowlist(list(self.org_allowlist))


def default_hosted_dashboard_config() -> HostedDashboardConfig:
    return HostedDashboardConfig()


def parse_hosted_dashboard_config(raw: Any, *, path: str = "<config>") -> HostedDashboardConfig:
    """Parse optional ``hosted_dashboard`` mapping; unknown keys fail closed."""
    if raw is None:
        return default_hosted_dashboard_config()
    if not isinstance(raw, dict):
        raise HostedDashboardConfigError(f"hosted_dashboard must be a mapping ({path})")

    extra = set(raw) - HOSTED_DASHBOARD_KEYS
    if extra:
        raise HostedDashboardConfigError(f"unknown hosted_dashboard keys: {sorted(extra)}")

    enabled = raw.get("enabled", False)
    if not isinstance(enabled, bool):
        raise HostedDashboardConfigError("hosted_dashboard.enabled must be a boolean")

    allow_non_loopback = raw.get("allow_non_loopback", False)
    if not isinstance(allow_non_loopback, bool):
        raise HostedDashboardConfigError("hosted_dashboard.allow_non_loopback must be a boolean")

    cors = raw.get("cors_origins", [])
    if not isinstance(cors, list) or not all(isinstance(x, str) for x in cors):
        raise HostedDashboardConfigError("hosted_dashboard.cors_origins must be a list of strings")

    allowlist = raw.get("org_allowlist", [])
    if not isinstance(allowlist, list) or not all(isinstance(x, str) for x in allowlist):
        raise HostedDashboardConfigError("hosted_dashboard.org_allowlist must be a list of strings")
    try:
        validate_allowlist(allowlist)
    except ValueError as exc:
        raise HostedDashboardConfigError(str(exc)) from exc

    sources = _parse_sources(raw.get("sources"))

    # K7: github baseline sources must remain available when enabled.
    if enabled and not (sources.github_contents and sources.github_meta):
        raise HostedDashboardConfigError(
            "hosted_dashboard.sources.github_contents and github_meta must be true (K7 baseline)"
        )

    enumeration_cap = raw.get("enumeration_cap", DEFAULT_ORG_ENUMERATION_CAP)
    if not isinstance(enumeration_cap, int) or enumeration_cap < 1:
        raise HostedDashboardConfigError("hosted_dashboard.enumeration_cap must be a positive integer")

    muse_hosts_raw = raw.get("musehub_hosts", [])
    if not isinstance(muse_hosts_raw, list):
        raise HostedDashboardConfigError("hosted_dashboard.musehub_hosts must be a list of strings")
    try:
        muse_hosts = validate_extra_hosts([str(x) for x in muse_hosts_raw])
    except ValueError as exc:
        raise HostedDashboardConfigError(str(exc)) from exc

    muse_base = raw.get("musehub_base_url")
    if muse_base is not None and (not isinstance(muse_base, str) or not muse_base.strip()):
        raise HostedDashboardConfigError("hosted_dashboard.musehub_base_url must be a non-empty string or null")

    if sources.musehub_read and not muse_base:
        raise HostedDashboardConfigError(
            "hosted_dashboard.musehub_base_url required when sources.musehub_read is true"
        )

    max_doc = raw.get("max_doc_bytes", 2_000_000)
    if not isinstance(max_doc, int) or max_doc < 1024:
        raise HostedDashboardConfigError("hosted_dashboard.max_doc_bytes must be an integer >= 1024")

    return HostedDashboardConfig(
        enabled=enabled,
        allow_non_loopback=allow_non_loopback,
        cors_origins=tuple(cors),
        org_allowlist=tuple(allowlist),
        sources=sources,
        enumeration_cap=enumeration_cap,
        musehub_hosts=muse_hosts,
        musehub_base_url=muse_base.strip() if isinstance(muse_base, str) else None,
        max_doc_bytes=max_doc,
    )


def _parse_sources(raw: Any) -> HostedSourcesConfig:
    if raw is None:
        return HostedSourcesConfig()
    if not isinstance(raw, dict):
        raise HostedDashboardConfigError("hosted_dashboard.sources must be a mapping")
    extra = set(raw) - SOURCE_KEYS
    if extra:
        raise HostedDashboardConfigError(f"unknown hosted_dashboard.sources keys: {sorted(extra)}")
    values: dict[str, bool] = {}
    for key in SOURCE_KEYS:
        val = raw.get(key, key in {"github_contents", "github_meta"})
        if not isinstance(val, bool):
            raise HostedDashboardConfigError(f"hosted_dashboard.sources.{key} must be a boolean")
        values[key] = val
    return HostedSourcesConfig(
        github_contents=values["github_contents"],
        github_meta=values["github_meta"],
        github_checks_advisory=values["github_checks_advisory"],
        musehub_read=values["musehub_read"],
    )
