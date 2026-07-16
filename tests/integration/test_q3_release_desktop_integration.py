"""Integration tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

from tests.fixtures.desktop_release import (
    BUNDLE_SCRIPT,
    GIT_SHA_FIXTURE,
    RELEASE_TEMPLATE,
    RELEASE_WORKFLOW,
    SMOKE_WORKFLOW,
    sample_signed_artifacts,
)
from tools.desktop_release.allowlist import refuse_disallowed_asset
from tools.desktop_release.constants import BUNDLE_ALLOWLIST_DIRS, BUNDLE_ALLOWLIST_FILES
from tools.desktop_release.manifest import build_manifest
from tools.desktop_release.workflow_lint import (
    assert_release_workflow_contract,
    assert_smoke_workflow_contract,
    assert_workflow_text_clean,
    load_workflow,
    workflow_references_secret_names,
)


def test_release_workflow_parses_and_contracts() -> None:
    data = load_workflow(RELEASE_WORKFLOW)
    assert_release_workflow_contract(data)
    assert_workflow_text_clean(RELEASE_WORKFLOW)
    text = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    assert "macos-latest" not in text
    assert "softprops/action-gh-release" in text
    found = workflow_references_secret_names(text)
    assert "APPLE_CERTIFICATE" in found
    assert "WINDOWS_CERTIFICATE" in found
    assert "LINUX_SIGNING_KEY" in found
    assert "APPLE_API_KEY" in found
    assert "APPLE_API_KEY_ID" in found
    assert "APPLE_API_ISSUER" in found


def test_smoke_workflow_no_release_publish() -> None:
    data = load_workflow(SMOKE_WORKFLOW)
    assert_smoke_workflow_contract(data)
    assert_workflow_text_clean(SMOKE_WORKFLOW)


def test_template_exists_and_references_secrets() -> None:
    assert RELEASE_TEMPLATE.is_file()
    text = RELEASE_TEMPLATE.read_text(encoding="utf-8")
    assert "APPLE_CERTIFICATE" in text
    assert "APPLE_API_KEY" in text
    assert "WINDOWS_CERTIFICATE" in text
    assert "LINUX_SIGNING_KEY" in text
    assert_workflow_text_clean(RELEASE_TEMPLATE)


def test_bundle_script_closed_allowlist() -> None:
    text = BUNDLE_SCRIPT.read_text(encoding="utf-8")
    assert "bundle-desktop-kit" in BUNDLE_SCRIPT.name or BUNDLE_SCRIPT.name.endswith(".sh")
    for dirname in BUNDLE_ALLOWLIST_DIRS:
        assert dirname in text
    for filename in BUNDLE_ALLOWLIST_FILES:
        assert filename in text
    assert ".env" not in text
    assert "*.p12" not in text
    assert "resources/kit" in text


def test_manifest_from_fixture_names() -> None:
    doc = build_manifest(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=sample_signed_artifacts(),
    )
    names = {a["filename"] for a in doc["artifacts"]}
    assert any(n.endswith(".dmg") for n in names)
    assert any(n.endswith(".msi") for n in names)
    assert any(n.endswith(".AppImage") for n in names)


def test_publish_allowlist_rejects_deb_rpm() -> None:
    for bad in ("pkg.deb", "pkg.rpm", "setup-unsigned.exe", "App.app.zip"):
        try:
            refuse_disallowed_asset(bad, version="0.1.0")
            raise AssertionError(f"expected refuse for {bad}")
        except Exception as exc:  # AllowlistError
            assert "allowlist" in str(exc).lower() or "not on allowlist" in str(exc)
