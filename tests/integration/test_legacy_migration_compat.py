"""Legacy-full migration compatibility: kit provenance, living-document bounds
and preserved consumer assets, exercised through the product CLI.

Fixtures are synthetic and disposable. Each scenario mirrors one demonstrated
consumer shape: an inert ``kit`` provenance section, living documents above
the 128 KiB config/NEXT bound, custom bridge assets recorded as preserved, and
an old automatic hook registration replaced by an empty manual registration.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest
import yaml

from cli import product_migration as migration, v1
from cli.product_config import normalize
from cli.v1_io import LIMIT, Refusal, digest
from cli.version_lock import FootprintEntry, compute_lock_digest

KIT = Path(__file__).resolve().parents[2]
LEGACY_KIT = {
    "source_path": "../legacy-kit-checkout",
    "pinned_version": "0.1.0",
    "install_status": "live_k6",
    "notes": "Installed by the legacy kit.\nCustom bridge assets are preserved by design.\n",
}
OLD_HOOKS = (b'{\n  "version": 1,\n  "hooks": {\n    "sessionStart": [\n'
             b'      {"command": ".cursor/hooks/session-start-next.sh", "failClosed": false}\n'
             b'    ]\n  }\n}\n')
MANUAL_HOOKS = b'{\n  "version": 1,\n  "hooks": {}\n}\n'
BIG_ROADMAP = ("# Fixture roadmap\n" + "r" * 180_000 + "\n").encode()
BIG_HANDOVER = ("# Fixture handover\n" + "h" * 380_000 + "\n").encode()


def command(root, *args):
    return subprocess.run([str(KIT / "cli/ok"), "-C", str(root), *map(str, args)],
                          capture_output=True, text=True, timeout=60)


def legacy_config(**overrides):
    config = {
        "overseer_config_version": 1,
        "repo": {"name": "fixture-legacy", "root_relative_docs": "docs"},
        "thresholds": {"realign_max_commits": 50, "drift_warn_only": True},
        "freeze_contract": {"enabled": True,
                            "reviewer": {"mode": "agent", "model": "thinking-high",
                                         "provider": "local", "fallback": "human"},
                            "human_escalation": ["security", "irreversible"]},
        "vcs": {"regime": "git-only", "canonical": "git",
                "git": {"remote": "origin", "main_branch": "main", "mirror_branch": None,
                        "feature_branch_pattern": "feat/{slug}"},
                "muse": {"staging_remote": None, "main_branch": None}},
        "docs": {"handover": "FIXTURE-HANDOVER.md", "roadmap": "FIXTURE-ROADMAP.md",
                 "handover_title": "Fixture Handover", "roadmap_title": "Fixture Roadmap",
                 "coordination": "FIXTURE-COORDINATION.md",
                 "standing_decisions": "FIXTURE-COORDINATION.md"},
        "kit": dict(LEGACY_KIT),
        "session_bookends": {"enabled": True},
        "honesty": {"enabled": True, "ledger": ".overseer/honesty/VERDICT-LEDGER.jsonl",
                    "require_verification_evidence": "warn"},
    }
    config.update(overrides)
    return config


def write_lock(root, rows):
    entries = [FootprintEntry(**row) for row in rows]
    lock = {"lock_version": 1, "kit_version": "0.1.0", "config_version": 1,
            "installed_at": "2026-07-26T12:46:56Z", "synced_at": "2026-10-01T14:44:10Z",
            "footprint_digest": compute_lock_digest(entries), "footprint": rows}
    (root / migration.LOCK).write_bytes(yaml.safe_dump(lock, sort_keys=False).encode())


def seed_legacy(root, *, config=None, git=True):
    """Knowtation-shaped legacy consumer with custom assets and an old lock."""
    root.mkdir(parents=True, exist_ok=True)
    files = {
        "docs/FIXTURE-ROADMAP.md": BIG_ROADMAP,
        "docs/FIXTURE-HANDOVER.md": BIG_HANDOVER,
        "docs/FIXTURE-COORDINATION.md": b"# Coordination\n",
        "MUSE-BRIDGE-WORKFLOW.md": b"# Owner bridge workflow (custom)\n",
        "scripts/muse-bridge-deploy.sh": b"#!/bin/sh\n# owner deploy bridge (custom)\nexit 0\n",
        ".cursor/hooks.json": OLD_HOOKS,
        ".cursor/hooks/session-start-next.sh": b"#!/bin/sh\nok next\n",
        ".cursor/rules/orchestrator.mdc": b"legacy kit rule\n",
        ".cursor/rules/owner-custom.mdc": b"owner rule\n",
        ".overseer/honesty/VERDICT-LEDGER.jsonl": b'{"verdict":"pass"}\n',
        ".gitignore": b"data/\n",
    }
    for path, body in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    (root / "scripts/muse-bridge-deploy.sh").chmod(0o755)
    (root / ".cursor/hooks/session-start-next.sh").chmod(0o755)
    (root / migration.CONFIG).write_bytes(v1.encode(config or legacy_config()))
    write_lock(root, [
        {"path": ".cursor/hooks.json", "source": "cursor/hooks/hooks.json",
         "sha256": "sha256:" + digest(OLD_HOOKS), "origin": "kit"},
        {"path": ".cursor/hooks/session-start-next.sh", "source": "cursor/hooks/session-start-next.sh",
         "sha256": "sha256:" + digest(files[".cursor/hooks/session-start-next.sh"]), "origin": "kit"},
        {"path": ".cursor/rules/orchestrator.mdc", "source": "cursor/rules/orchestrator.mdc",
         "sha256": "sha256:" + digest(files[".cursor/rules/orchestrator.mdc"]), "origin": "kit"},
        {"path": "MUSE-BRIDGE-WORKFLOW.md", "source": "templates/MUSE-BRIDGE-WORKFLOW.md",
         "sha256": "sha256:" + digest(b"kit template\n"), "origin": "preserved"},
        {"path": "docs/FIXTURE-HANDOVER.md", "source": "consumer",
         "sha256": "sha256:" + digest(b"older handover\n"), "origin": "preserved"},
        {"path": "docs/FIXTURE-ROADMAP.md", "source": "consumer",
         "sha256": "sha256:" + digest(b"older roadmap\n"), "origin": "preserved"},
        {"path": "scripts/muse-bridge-deploy.sh", "source": "templates/scripts/muse-bridge-deploy.sh.template",
         "sha256": "sha256:" + digest(b"kit bridge template\n"), "origin": "preserved"},
    ])
    if git:
        for args in (("init", "-b", "main"), ("config", "user.name", "Fixture"),
                     ("config", "user.email", "fixture@example.invalid"),
                     ("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "seed")):
            subprocess.run(["/usr/bin/git", "-C", str(root), *args], check=True, capture_output=True)
    return root


@pytest.fixture
def legacy(tmp_path):
    return seed_legacy((tmp_path / "legacy").resolve())


def snapshot(root):
    return {p.relative_to(root).as_posix(): (digest(p.read_bytes()), p.stat().st_mode & 0o7777)
            for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts}


def plan(root, *extra):
    result = command(root, "init", "--migrate", "--dry-run", "--json", "--model", "Fixture Model", *extra)
    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    (root / ".overseer/local").mkdir(parents=True, exist_ok=True)
    (root / ".overseer/local/plan.json").write_text(result.stdout)
    return document


def apply(root, document, *extra):
    return command(root, "init", "--migrate", "--apply-plan", ".overseer/local/plan.json",
                   "--expect-plan", document["plan_sha256"],
                   "--expect-config", document["plan"]["source_config_sha256"], "--json", *extra)


def publish(root):
    """First canonical NEXT through the bound writer; legacy fixtures have none."""
    config = yaml.safe_load((root / migration.CONFIG).read_bytes())
    (root / ".overseer/local/prompt.txt").write_text("Fixture follow-up task.\n")
    result = command(root, "next-write", "--repo-id", config["repo"]["id"], "--branch", "main",
                     "--lane", "product", "--model", config["context"]["model"],
                     "--action-id", "FIXTURE-1", "--action-kind", "review",
                     "--prompt-file", ".overseer/local/prompt.txt", "--expect-next", "absent")
    assert result.returncode == 0, result.stderr


def healthy(root):
    status = command(root, "status", "--json", "--check-footprint", "--exit-code")
    data = json.loads(status.stdout)
    assert status.returncode == 0, json.dumps({k: data.get(k) for k in (
        "next_error", "footprint_integrity", "footprint_coverage", "drift")})
    return data


# --- legacy kit provenance -------------------------------------------------

def test_legacy_kit_metadata_is_mapped_visible_and_inert(legacy):
    before = snapshot(legacy)
    first, second = plan(legacy), plan(legacy)
    assert first == second
    planned = first["plan"]
    assert planned["apply_supported"] is True
    assert planned["normalized_config"]["legacy_kit"] == LEGACY_KIT
    assert "kit" not in planned["normalized_config"]
    mapped = {row["before_path"]: row for row in planned["field_map"] if row["before_path"]}
    for key, value in LEGACY_KIT.items():
        assert mapped["kit." + key]["after_path"] == "legacy_kit." + key
        assert mapped["kit." + key]["after"] == value
    assert any(d.startswith("legacy_kit_metadata_preserved") for d in planned["diagnostics"])
    # The dry run is read-only apart from the operator-written plan input.
    after = snapshot(legacy)
    after.pop(".overseer/local/plan.json")
    assert after == before
    result = apply(legacy, first)
    assert result.returncode == 0, result.stderr + result.stdout
    migrated = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    assert migrated["schema"] == 3 and migrated["legacy_kit"] == LEGACY_KIT
    # The provenance pointer never selects a runtime or source.
    assert migrated["runtime"] == v1.runtime()
    status = command(legacy, "status", "--json", "--check-footprint")
    assert json.loads(status.stdout)["configuration"]["legacy_kit"] == LEGACY_KIT


@pytest.mark.parametrize("value", [
    ["not", "a", "mapping"],
    {"notes": {"nested": "mapping"}},
    {"notes": ["list"]},
    {"notes": "bell\x07character"},
    {"bad key": "x"},
    {"notes": "x" * 16_385},
])
def test_invalid_legacy_kit_metadata_refuses_without_dropping(tmp_path, value):
    root = seed_legacy((tmp_path / "invalid").resolve(), config=legacy_config(kit=value))
    before = snapshot(root)
    result = command(root, "init", "--migrate", "--dry-run", "--json")
    assert result.returncode == 2 and "config_legacy_kit_invalid" in result.stderr
    assert snapshot(root) == before


def test_legacy_kit_key_names_are_schema_specific(tmp_path):
    root = seed_legacy((tmp_path / "names").resolve())
    raw = legacy_config()
    raw["legacy_kit"] = raw.pop("kit")
    with pytest.raises(Refusal, match="unknown_unmapped_settings"):
        normalize(v1.encode(raw), root=root)
    schema3 = normalize(v1.encode(legacy_config()), root=root, runtime=v1.runtime(), bind=True,
                        identity="5f1e7f0c-5a8e-4a43-9d6b-0b3a1d2f8c11").data
    assert normalize(v1.encode(schema3), root=root).data["legacy_kit"] == LEGACY_KIT
    schema3["kit"] = schema3.pop("legacy_kit")
    with pytest.raises(Refusal, match="unknown_unmapped_settings"):
        normalize(v1.encode(schema3), root=root)


# --- living-document bounds -------------------------------------------------

def test_living_documents_above_config_bound_migrate_and_report_healthy(legacy):
    assert len(BIG_ROADMAP) > LIMIT and len(BIG_HANDOVER) > LIMIT
    document = plan(legacy)
    result = apply(legacy, document)
    assert result.returncode == 0, result.stderr + result.stdout
    assert (legacy / "docs/FIXTURE-ROADMAP.md").read_bytes() == BIG_ROADMAP
    assert (legacy / "docs/FIXTURE-HANDOVER.md").read_bytes() == BIG_HANDOVER
    lock = {row["path"]: row for row in yaml.safe_load((legacy / migration.LOCK).read_bytes())["footprint"]}
    for path, body in (("docs/FIXTURE-ROADMAP.md", BIG_ROADMAP), ("docs/FIXTURE-HANDOVER.md", BIG_HANDOVER)):
        assert lock[path]["origin"] == "preserved"
        assert lock[path]["sha256"] == "sha256:" + digest(body)
    publish(legacy)
    data = healthy(legacy)
    assert data["footprint_integrity"]["ok"] and data["footprint_coverage"]["ok"]


def test_config_and_next_keep_the_small_bound(legacy):
    from cli.product_footprint import with_lock
    raw = legacy_config()
    raw["kit"]["notes"] = "n" * 16_000
    padded = v1.encode(raw) + b"#" + b"p" * LIMIT + b"\n"
    (legacy / migration.CONFIG).write_bytes(padded)
    result = command(legacy, "init", "--migrate", "--dry-run", "--json")
    assert result.returncode == 2 and ("file_invalid" in result.stderr or "file_too_large" in result.stderr)
    with pytest.raises(Refusal, match="file_invalid|file_too_large"):
        migration.read(legacy, migration.CONFIG)
    (legacy / "docs").mkdir(exist_ok=True)
    (legacy / migration.NEXT).write_bytes(b"x" * (LIMIT + 1))
    with pytest.raises(Refusal, match="file_invalid|file_too_large"):
        migration.read(legacy, migration.NEXT)
    # The lock writer itself reads living documents with the asset bound.
    (legacy / migration.NEXT).unlink()
    (legacy / migration.CONFIG).write_bytes(v1.encode(legacy_config()))
    config = normalize(read_config(legacy), root=legacy, runtime=v1.runtime(), bind=True,
                       identity="5f1e7f0c-5a8e-4a43-9d6b-0b3a1d2f8c11").data
    lock = yaml.safe_load(with_lock(legacy, {}, config)[migration.LOCK])
    assert {row["path"] for row in lock["footprint"]} >= {"docs/FIXTURE-HANDOVER.md", "docs/FIXTURE-ROADMAP.md"}


def read_config(root):
    return (root / migration.CONFIG).read_bytes()


def test_living_document_above_asset_bound_refuses(legacy):
    path = legacy / "docs/FIXTURE-HANDOVER.md"
    with path.open("wb") as stream:
        stream.truncate(migration.ASSET_LIMIT + 1)
    result = command(legacy, "init", "--migrate", "--dry-run", "--json")
    assert result.returncode == 2 and ("file_invalid" in result.stderr or "file_too_large" in result.stderr)
    assert not (legacy / ".overseer/migrations").exists()


# --- custom-asset preservation ---------------------------------------------

def test_custom_assets_and_manual_hook_registration_are_preserved(legacy):
    custom = {p: (legacy / p).read_bytes() for p in (
        "MUSE-BRIDGE-WORKFLOW.md", "scripts/muse-bridge-deploy.sh", ".cursor/rules/owner-custom.mdc",
        ".cursor/hooks/session-start-next.sh", ".gitignore", ".overseer/honesty/VERDICT-LEDGER.jsonl")}
    (legacy / ".cursor/hooks.json").write_bytes(MANUAL_HOOKS)
    document = plan(legacy)
    planned = document["plan"]
    classes = {row["path"]: row["classification"] for row in planned["classification"]}
    # Git-only regimes do not generate bridge assets; Muse fixtures classify them.
    assert classes.get("MUSE-BRIDGE-WORKFLOW.md") in (None, "preserved")
    assert classes.get("scripts/muse-bridge-deploy.sh") in (None, "preserved")
    assert classes[".cursor/rules/orchestrator.mdc"] == "kit-updated"
    changed = {row["path"] for row in planned["assets"]}
    assert not changed & (set(custom) | {".cursor/hooks.json"})
    assert "legacy_kit_asset_consumer_owned: .cursor/hooks.json" in planned["diagnostics"]
    result = apply(legacy, document)
    assert result.returncode == 0, result.stderr + result.stdout
    for path, body in custom.items():
        assert (legacy / path).read_bytes() == body
    assert (legacy / "scripts/muse-bridge-deploy.sh").stat().st_mode & 0o777 == 0o755
    assert (legacy / ".cursor/hooks.json").read_bytes() == MANUAL_HOOKS
    lock = {row["path"]: row for row in yaml.safe_load((legacy / migration.LOCK).read_bytes())["footprint"]}
    assert lock[".cursor/hooks.json"]["origin"] == "preserved"
    assert lock[".cursor/hooks.json"]["sha256"] == "sha256:" + digest(MANUAL_HOOKS)
    assert lock[".cursor/hooks.json"]["source"] == "cursor/hooks/hooks.json"
    # An untouched legacy hook script stays a verifiable kit record.
    assert lock[".cursor/hooks/session-start-next.sh"]["origin"] == "kit"
    for path in ("MUSE-BRIDGE-WORKFLOW.md", "scripts/muse-bridge-deploy.sh"):
        assert lock[path]["origin"] == "preserved"
    publish(legacy)
    status = healthy(legacy)
    assert status["drift"]["status"] == "current"


def test_unchanged_legacy_hook_registration_is_not_relabelled(legacy):
    document = plan(legacy)
    assert not any(d.startswith("legacy_kit_asset_consumer_owned") for d in document["plan"]["diagnostics"])
    assert apply(legacy, document).returncode == 0
    lock = {row["path"]: row for row in yaml.safe_load((legacy / migration.LOCK).read_bytes())["footprint"]}
    assert lock[".cursor/hooks.json"]["origin"] == "kit"
    assert (legacy / ".cursor/hooks.json").read_bytes() == OLD_HOOKS


def test_hook_registration_edit_after_review_refuses_before_mutation(legacy):
    (legacy / ".cursor/hooks.json").write_bytes(MANUAL_HOOKS)
    document = plan(legacy)
    (legacy / ".cursor/hooks.json").write_bytes(OLD_HOOKS)
    before = snapshot(legacy)
    result = apply(legacy, document)
    assert result.returncode != 0
    assert snapshot(legacy) == before
    assert not (legacy / ".overseer/migrations").exists()


def test_muse_python_is_refused_for_git_authority(legacy):
    result = command(legacy, "init", "--migrate", "--dry-run", "--muse-python", "/usr/bin/python3")
    assert result.returncode == 2 and "git_does_not_use_muse_python" in result.stderr
