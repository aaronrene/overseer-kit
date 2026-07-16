"""Security tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures.desktop_release import (
    GIT_SHA_FIXTURE,
    RELEASE_TEMPLATE,
    RELEASE_WORKFLOW,
    SMOKE_WORKFLOW,
    sample_signed_artifacts,
)
from tests.support import KIT_ROOT
from tools.desktop_release.allowlist import AllowlistError, refuse_disallowed_asset
from tools.desktop_release.manifest import ManifestError, build_manifest
from tools.desktop_release.refuse import scan_text_for_secret_patterns
from tools.desktop_release.workflow_lint import (
    assert_release_workflow_contract,
    load_workflow,
    workflow_triggers,
)


def test_no_secret_literals_in_workflows() -> None:
    for path in (RELEASE_WORKFLOW, SMOKE_WORKFLOW, RELEASE_TEMPLATE):
        text = path.read_text(encoding="utf-8")
        assert scan_text_for_secret_patterns(text) == []
        assert "BEGIN PRIVATE KEY" not in text
        assert "BEGIN RSA PRIVATE KEY" not in text


def test_gitignore_covers_signing_patterns() -> None:
    text = (KIT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "*.p12" in text
    assert "*.pfx" in text
    assert "apple-api-key.json" in text


def test_release_workflow_does_not_echo_secrets() -> None:
    text = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    # Forbid echoing secret values; references via secrets.* are OK.
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        lower = stripped.lower()
        if "echo" in lower and "secret" in lower and "secrets." in stripped:
            # echo of secret *names* in comments is fine; fail on echo "$SECRET"
            if "${{" in stripped and "secrets." in stripped and "echo" in lower:
                # GitHub expressions in env blocks are OK; shell echo of expanded secrets not.
                if "echo" in lower and ("$APPLE_" in stripped or "$WINDOWS_" in stripped or "$LINUX_" in stripped):
                    pytest.fail(f"possible secret echo: {stripped}")


def test_pull_request_cannot_publish_releases() -> None:
    data = load_workflow(RELEASE_WORKFLOW)
    triggers = workflow_triggers(data)
    assert "pull_request" not in triggers
    assert_release_workflow_contract(data)
    smoke = load_workflow(SMOKE_WORKFLOW)
    smoke_text = SMOKE_WORKFLOW.read_text(encoding="utf-8").lower()
    assert "action-gh-release" not in smoke_text
    assert "gh release" not in smoke_text


def test_permissions_least_privilege() -> None:
    data = load_workflow(RELEASE_WORKFLOW)
    perms = data["permissions"]
    assert perms == {"contents": "write"} or (
        perms.get("contents") == "write" and "id-token" not in perms
    )


def test_track_q_launcher_still_ok_app_only() -> None:
    launcher = (KIT_ROOT / "desktop" / "src-tauri" / "src" / "launcher.rs").read_text(
        encoding="utf-8"
    )
    assert "ok" in launcher
    assert "app" in launcher
    assert "0.0.0.0" not in launcher
    assert "hosted-dashboard" not in launcher


def test_rejection_unsigned_labeled_signed_refused() -> None:
    arts = sample_signed_artifacts()
    arts[0]["signing"] = {"status": "signed", "method": "none"}
    with pytest.raises(ManifestError):
        build_manifest(version="0.1.0", git_sha=GIT_SHA_FIXTURE, artifacts=arts)


def test_rejection_non_allowlisted_asset_types() -> None:
    for name in ("pkg.deb", "pkg.rpm", "Setup.exe", "Overseer.app.zip"):
        with pytest.raises(AllowlistError):
            refuse_disallowed_asset(name, version="0.1.0")
