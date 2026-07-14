"""Unit tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

import json

import pytest

from cli.main import COMMANDS
from tools.hosted_dashboard.auth import generate_viewer_token
from tools.hosted_dashboard.bind import DEFAULT_PORT, validate_bind_address
from tools.hosted_dashboard.config import HostedDashboardConfigError, parse_hosted_dashboard_config
from tools.hosted_dashboard.envelope import build_meta, health_success
from tools.hosted_dashboard.handlers import is_track_q_act_path, match_repo_route
from tools.hosted_dashboard.hosts import host_allowed
from tools.hosted_dashboard.parsers import never_invent_done_on_garbage, parse_document_derived_gates
from tools.hosted_dashboard.scopes import refuse_write_scopes
from tools.hosted_dashboard.sources import SOURCE_IDS, is_known_source_id
from tools.hosted_dashboard.validators import validate_allowlist, valid_owner_repo_segment


def test_hosted_dashboard_registered() -> None:
    assert "hosted-dashboard" in COMMANDS


def test_default_port_8766() -> None:
    assert DEFAULT_PORT == 8766


@pytest.mark.parametrize(
    ("bind", "allow", "expected"),
    [
        ("127.0.0.1", False, "127.0.0.1"),
        ("localhost", False, "127.0.0.1"),
        ("::1", False, "::1"),
        ("0.0.0.0", False, None),
        ("0.0.0.0", True, "0.0.0.0"),
        ("192.168.1.1", False, None),
    ],
)
def test_bind_refuse_without_allow_non_loopback(bind: str, allow: bool, expected: str | None) -> None:
    assert validate_bind_address(bind, allow_non_loopback=allow) == expected


def test_viewer_token_entropy() -> None:
    token = generate_viewer_token()
    assert len(token) >= 32


def test_empty_allowlist_validates() -> None:
    assert validate_allowlist([]) == []


def test_allowlist_shape() -> None:
    pairs = validate_allowlist(["acme/kit", "acme"])
    assert pairs == [("acme", "kit"), ("acme", None)]


def test_owner_repo_validators() -> None:
    assert valid_owner_repo_segment("acme")
    assert not valid_owner_repo_segment("../etc")
    assert not valid_owner_repo_segment("a/b")


def test_write_scope_refuse() -> None:
    assert refuse_write_scopes(["contents:write"]) == "write_scope_refused"
    assert refuse_write_scopes(["contents:read"]) is None
    assert refuse_write_scopes(None) is None


def test_upstream_host_allowlist() -> None:
    assert host_allowed("api.github.com")
    assert host_allowed("raw.githubusercontent.com")
    assert not host_allowed("evil.example")
    assert not host_allowed("127.0.0.1")
    assert not host_allowed("169.254.169.254")


def test_envelope_authoritative_local() -> None:
    meta = build_meta(source_id="github_contents", ref="main", content_sha256="abc")
    assert meta["authoritative_workflow"] == "local"
    health = health_success().to_dict()
    assert health["result"] == {"status": "ok", "mode": "hosted-read-only"}


def test_parser_never_invents_done_on_garbage() -> None:
    result = never_invent_done_on_garbage("!!! Status: definitely DONE somehow ???")
    assert result.ok is False
    assert all(p["status"] != "DONE" for p in result.phases)
    assert result.phases == []


def test_parser_reads_build_status_rows() -> None:
    text = "| **Alpha** | Auto | **DONE** |\n| **Beta** | Auto | **WIP** |\n"
    result = parse_document_derived_gates(roadmap_text=text, handover_text=None)
    assert result.ok is True
    assert {"id": "Alpha", "status": "DONE"} in result.phases


def test_config_unknown_key_refuse() -> None:
    with pytest.raises(HostedDashboardConfigError):
        parse_hosted_dashboard_config({"enabled": False, "surprise": True})


def test_source_id_closed_vocabulary() -> None:
    assert is_known_source_id("github_contents")
    assert not is_known_source_id("arbitrary_s3")
    assert "musehub_read" in SOURCE_IDS


def test_track_q_paths_detected() -> None:
    assert is_track_q_act_path("/api/review/freeze")
    assert is_track_q_act_path("/api/governance-sync")
    assert not is_track_q_act_path("/api/org/summary")


def test_repo_route_match() -> None:
    assert match_repo_route("/api/repos/acme/kit/roadmap") == ("acme", "kit", "roadmap")
    assert match_repo_route("/api/repos/acme/kit/unknown") is None
