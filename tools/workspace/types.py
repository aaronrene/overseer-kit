"""Shared types and exit codes for multi-repo workspace lanes (§MR.7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

EXIT_WORKSPACE_RELAY = 35
EXIT_CONFIG = 2
EXIT_USAGE = 1
EXIT_OK = 0

WORKSPACE_ROLES = frozenset(
    {"product_order", "ownership", "enrichment", "edge", "kit", "other"}
)
SUPPORTED_REGIMES = frozenset({"muse+git-mirror", "muse-only", "git-only"})
FORBIDDEN_IDENTITY_KEYS = frozenset(
    {
        "x-user-id",
        "x_user_id",
        "userid",
        "user_id",
        "wallet",
        "email",
        "bearer",
        "token",
        "password",
        "secret",
        "api_key",
        "apikey",
    }
)

RelayState = Literal[
    "not_configured",
    "ok",
    "stale_relay",
    "ambiguous_primary",
    "missing_primary",
    "missing_member",
    "error",
]

ManifestSource = Literal[
    "config_manifest",
    "product_order_root",
    "local_workspace",
    "env_override",
    "home_index",
]


class NextRole(str, Enum):
    PRIMARY = "primary"
    RELAY = "relay"
    PRODUCT_RELAY = "product_relay"
    LANE_TIP = "lane_tip"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class WorkspaceMemberConfig:
    """One member row from ``workspace.yaml``."""

    id: str
    role: str
    root_raw: str
    regime: str | None
    required: bool
    relay: bool
    handover: str | None = None
    roadmap: str | None = None
    relay_lanes: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkspaceLaneConfig:
    """One constellation lane."""

    id: str
    primary: bool
    owner_member: str | None


@dataclass(frozen=True)
class WorkspaceManifest:
    """Validated constellation manifest (§MR.4.1)."""

    version: int
    id: str
    product_order_member: str
    strict_markers: bool
    strict_board_names: bool
    members: tuple[WorkspaceMemberConfig, ...]
    lanes: tuple[WorkspaceLaneConfig, ...]
    source_path: Path
    manifest_source: ManifestSource

    def member(self, member_id: str) -> WorkspaceMemberConfig | None:
        for row in self.members:
            if row.id == member_id:
                return row
        return None

    def product_order(self) -> WorkspaceMemberConfig:
        for row in self.members:
            if row.role == "product_order":
                return row
        raise KeyError("product_order member missing")

    def primary_lane(self) -> WorkspaceLaneConfig:
        for lane in self.lanes:
            if lane.primary:
                return lane
        raise KeyError("primary lane missing")


@dataclass(frozen=True)
class NextBlock:
    """One marked session block extracted from a handover."""

    role: NextRole
    lane: str | None
    status: str
    product_order: str | None
    tip_hash: str | None
    heading: str
    heading_line: int
    body: str
    fence: str | None
    step_id: str | None
    model: str | None
    authority: str | None
    unmarked: bool = False


@dataclass(frozen=True)
class MemberBoardPaths:
    """Resolved handover/roadmap paths for one member."""

    member_id: str
    root: Path | None
    present: bool
    handover_path: Path | None
    roadmap_path: Path | None
    handover_basename: str | None
    roadmap_basename: str | None
    handover_title: str | None
    roadmap_title: str | None
    regime: str | None
    role: str
    relay: bool
    required: bool
    member_status: Literal["ok", "absent", "missing_required", "error"]
    board_name_violation: bool = False
    error: str | None = None


@dataclass(frozen=True)
class FreshnessFinding:
    """One freshness / marker integrity finding."""

    code: RelayState
    message: str
    relay_path: str | None = None
    primary_path: str | None = None


@dataclass(frozen=True)
class CheckNextResult:
    """Outcome of ``ok workspace check-next``."""

    exit_code: int
    state: RelayState
    ok: bool
    lane: str
    findings: tuple[FreshnessFinding, ...]
    primary: dict[str, Any] | None = None
    relays: tuple[dict[str, Any], ...] = ()
    messages: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkspaceStatusReport:
    """Structured ``ok workspace status`` payload."""

    configured: bool
    ok: bool
    state: RelayState
    constellation_id: str | None
    product_order_member: str | None
    manifest_source: ManifestSource | None
    manifest_path: str | None
    authoritative_handover: str | None
    members: tuple[dict[str, Any], ...]
    lanes: tuple[dict[str, Any], ...]
    check_next: dict[str, Any] | None
    warnings: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "ok": self.ok,
            "state": self.state,
            "constellation_id": self.constellation_id,
            "product_order_member": self.product_order_member,
            "manifest_source": self.manifest_source,
            "manifest_path": self.manifest_path,
            "authoritative_handover": self.authoritative_handover,
            "members": list(self.members),
            "lanes": list(self.lanes),
            "check_next": self.check_next,
            "warnings": list(self.warnings),
            "diagnostics": list(self.diagnostics),
        }


@dataclass(frozen=True)
class DoctorFinding:
    """One doctor diagnostic."""

    code: str
    message: str
    member_id: str | None = None
    path: str | None = None


@dataclass(frozen=True)
class DoctorReport:
    """Outcome of ``ok workspace doctor``."""

    configured: bool
    findings: tuple[DoctorFinding, ...]
    ok: bool

    def to_json(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "ok": self.ok,
            "findings": [
                {
                    "code": f.code,
                    "message": f.message,
                    "member_id": f.member_id,
                    "path": f.path,
                }
                for f in self.findings
            ],
        }


@dataclass
class WorkspaceLoadError(Exception):
    """Config/manifest load failure (maps to exit 2)."""

    message: str
    citation: str | None = None
    exit_code: int = EXIT_CONFIG

    def __str__(self) -> str:  # pragma: no cover - trivial
        if self.citation:
            return f"{self.message} ({self.citation})"
        return self.message
