"""Explicit native Muse binding for unbound legacy-full migration (real Muse).

The fixture is a disposable Muse checkout with a Git mirror working tree that
tracks local Cursor/Overseer paths, legacy kit provenance, living documents
above 128 KiB and custom bridge assets. Native authority, regime, branch,
settings and tracked bindings must survive; nothing applies on drift.
"""
from __future__ import annotations

import json
import subprocess

import pytest
import yaml

from cli import product_migration as migration, v1
from cli.v1_io import digest
from cli.v1_revision import muse_read
from tests.integration.test_legacy_migration_compat import (
    BIG_HANDOVER, BIG_ROADMAP, LEGACY_KIT, MANUAL_HOOKS, command, legacy_config, seed_legacy, snapshot)

MIRROR_VCS = {"regime": "muse+git-mirror", "canonical": "muse",
              "git": {"remote": "origin", "main_branch": "main", "mirror_branch": "muse-mirror",
                      "feature_branch_pattern": "feat/{slug}"},
              "muse": {"staging_remote": "staging", "main_branch": "main"}}


@pytest.fixture
def native(muse_root, muse):
    root = muse_root
    seed_legacy(root, config=legacy_config(vcs=MIRROR_VCS), git=False)
    (root / ".cursor/hooks.json").write_bytes(MANUAL_HOOKS)
    for args in (("init", "-b", "main"), ("config", "user.name", "Fixture"),
                 ("config", "user.email", "fixture@example.invalid"),
                 ("add", ".overseer/config.yaml", ".cursor/rules/owner-custom.mdc"),
                 ("-c", "core.hooksPath=/dev/null", "commit", "-m", "mirror seed")):
        subprocess.run(["/usr/bin/git", "-C", str(root), *args], check=True, capture_output=True)
    (root / "app.py").write_text("value = 1\n")
    muse(root, "code", "add", "app.py")
    muse(root, "commit", "-m", "native seed", "--json")
    return root


def controls(root):
    names = (".git/HEAD", ".git/index", ".muse/HEAD")
    return {name: digest((root / name).read_bytes()) for name in names if (root / name).exists()}


def dry(root, python, *extra):
    return command(root, "init", "--migrate", "--dry-run", "--json", "--model", "Fixture Reviewer",
                   "--muse-python", python, *extra)


def save(root, result):
    (root / ".overseer/local").mkdir(parents=True, exist_ok=True)
    (root / ".overseer/local/plan.json").write_text(result.stdout)
    return json.loads(result.stdout)


def apply(root, document, *extra):
    return command(root, "init", "--migrate", "--apply-plan", ".overseer/local/plan.json",
                   "--expect-plan", document["plan_sha256"],
                   "--expect-config", document["plan"]["source_config_sha256"], "--json", *extra)


def test_unbound_preview_stays_inapplicable_without_explicit_binding(native):
    result = command(native, "init", "--migrate", "--dry-run", "--json")
    assert result.returncode == 0, result.stderr
    planned = json.loads(result.stdout)["plan"]
    assert planned["apply_supported"] is False
    assert planned["context"]["unavailable"] == "muse_binding_required"


def test_tracked_local_bindings_require_explicit_preserve(native, muse_python):
    before = snapshot(native)
    result = dry(native, muse_python)
    assert result.returncode == 2 and "tracked_local_bindings" in result.stderr
    assert snapshot(native) == before


def test_native_binding_migrates_preserving_authority_history_and_assets(native, muse_python, muse):
    state = muse_read(native, str(muse_python))
    before_controls = controls(native)
    custom = {p: (native / p).read_bytes() for p in (
        "MUSE-BRIDGE-WORKFLOW.md", "scripts/muse-bridge-deploy.sh", ".cursor/hooks.json",
        ".cursor/rules/owner-custom.mdc", ".gitignore")}
    result = dry(native, muse_python, "--tracked-bindings", "preserve")
    assert result.returncode == 0, result.stderr
    document = save(native, result)
    planned = document["plan"]
    assert planned["apply_supported"] is True
    config = planned["normalized_config"]
    assert config["vcs"]["regime"] == "muse+git-mirror" and config["vcs"]["canonical"] == "muse"
    assert config["vcs"]["git"] == MIRROR_VCS["git"]
    assert config["vcs"]["muse"]["staging_remote"] == "staging"
    assert config["vcs"]["muse"]["main_branch"] == "main"
    assert config["vcs"]["muse"]["binding"] == {k: state[k] for k in ("repo_id", "store", "runtime")}
    assert config["legacy_kit"] == LEGACY_KIT
    assert planned["context"]["source_id"] == state["repo_id"]
    assert planned["context"]["head"] == state["head"] and planned["context"]["branch"] == state["branch"]
    assert "native_muse_binding_added: " + state["repo_id"] in planned["diagnostics"]
    assert any(d.startswith("tracked_local_bindings_preserved: git=") for d in planned["diagnostics"])
    classes = {row["path"]: row["classification"] for row in planned["classification"]}
    assert classes["MUSE-BRIDGE-WORKFLOW.md"] == classes["scripts/muse-bridge-deploy.sh"] == "preserved"
    assert not {row["path"] for row in planned["assets"]} & set(custom)
    # Apply repeats the explicit tracked-binding choice.
    refused = apply(native, document)
    assert refused.returncode == 2 and "tracked_local_bindings" in refused.stderr
    assert not (native / ".overseer/migrations").exists()
    applied = apply(native, document, "--tracked-bindings", "preserve")
    assert applied.returncode == 0, applied.stderr + applied.stdout
    migrated = yaml.safe_load((native / migration.CONFIG).read_bytes())
    assert migrated["vcs"] == config["vcs"] and migrated["schema"] == 3
    for path, body in custom.items():
        assert (native / path).read_bytes() == body
    assert (native / "docs/FIXTURE-ROADMAP.md").read_bytes() == BIG_ROADMAP
    assert (native / "docs/FIXTURE-HANDOVER.md").read_bytes() == BIG_HANDOVER
    assert controls(native) == before_controls
    after = muse_read(native, str(muse_python))
    assert (after["repo_id"], after["branch"], after["head"]) == (state["repo_id"], state["branch"], state["head"])
    (native / ".overseer/local/prompt.txt").write_text("Native fixture review.\n")
    published = command(native, "next-write", "--repo-id", migrated["repo"]["id"], "--branch", state["branch"],
                        "--vcs", "muse", "--base-head", state["head"], "--lane", "product",
                        "--model", "Fixture Reviewer", "--action-id", "NATIVE-1", "--action-kind", "review",
                        "--prompt-file", ".overseer/local/prompt.txt", "--expect-next", "absent")
    assert published.returncode == 0, published.stderr
    fresh = subprocess.run([str(native / ".overseer/bin/ok"), "-C", str(native), "next", "--lane", "product"],
                           cwd="/", capture_output=True, text=True, timeout=60)
    assert fresh.returncode == 0, fresh.stderr
    assert "Model: Fixture Reviewer" in fresh.stdout and "Native fixture review." in fresh.stdout
    status = command(native, "status", "--json", "--check-footprint", "--exit-code")
    data = json.loads(status.stdout)
    assert status.returncode == 0, json.dumps({k: data.get(k) for k in (
        "next_error", "footprint_integrity", "footprint_coverage", "drift")})
    assert data["vcs"] == "muse" and data["source_id"] == state["repo_id"]


def test_native_head_change_after_review_refuses_before_mutation(native, muse_python, muse):
    document = save(native, dry(native, muse_python, "--tracked-bindings", "preserve"))
    (native / "app.py").write_text("value = 2\n")
    muse(native, "code", "add", "app.py")
    muse(native, "commit", "-m", "moved after review", "--json")
    before = snapshot(native)
    result = apply(native, document, "--tracked-bindings", "preserve")
    assert result.returncode != 0
    assert snapshot(native) == before
    assert not (native / ".overseer/migrations").exists()


def test_apply_refuses_a_different_muse_python(native, muse_python, tmp_path):
    document = save(native, dry(native, muse_python, "--tracked-bindings", "preserve"))
    other = tmp_path / "other-env/bin/python3"
    result = apply(native, document, "--tracked-bindings", "preserve", "--muse-python", str(other))
    assert result.returncode == 2 and "muse_python_plan_mismatch" in result.stderr
    assert not (native / ".overseer/migrations").exists()


def test_existing_binding_is_not_rebound_by_migration(native, muse_python):
    document = save(native, dry(native, muse_python, "--tracked-bindings", "preserve"))
    assert apply(native, document, "--tracked-bindings", "preserve").returncode == 0
    result = dry(native, muse_python, "--tracked-bindings", "preserve")
    assert result.returncode == 2 and "muse_binding_exists" in result.stderr
