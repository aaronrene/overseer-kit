"""FPR5-R3/R5 acceptance at the CLI boundary, using disposable repositories."""
from argparse import Namespace
import json
from pathlib import Path
import stat
import subprocess

import pytest
import yaml

from cli import product_migration as migration, v1
from cli.v1_io import digest

KIT = Path(__file__).resolve().parents[2]
COLLISION = ".cursor/rules/build-verification-required.mdc"
OWNER = b"---\nalwaysApply: true\n---\nOwner requires custom offline verification.\n"


def command(root, *args):
    return subprocess.run([str(KIT / "cli/ok"), "-C", str(root), *args],
                          capture_output=True, text=True, timeout=45)


def seed(tmp_path):
    root = tmp_path / "consumer"
    root.mkdir()
    for args in (("init", "--template=", "-b", "main"),
                 ("config", "core.hooksPath", "/dev/null"),
                 ("config", "user.name", "Fixture"),
                 ("config", "user.email", "fixture@example.invalid"),
                 ("commit", "--allow-empty", "-m", "seed")):
        subprocess.run(["/usr/bin/git", "-C", str(root), *args], check=True, capture_output=True)
    return root


def snapshot(path):
    return path.read_bytes(), stat.S_IMODE(path.stat().st_mode), path.stat().st_mtime_ns


def legacy_collision(tmp_path, origin, path=COLLISION):
    root = seed(tmp_path)
    (root / ".overseer").mkdir()
    (root / migration.CONFIG).write_bytes((KIT / "tests/fixtures/config-two-lane.yaml").read_bytes())
    proposed = migration.build_plan(root, Namespace())
    generated = v1.assets(root, proposed["normalized_config"])[path]
    dest = root / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(generated if origin in ("unrecorded-identical", "recorded-mode-only") else OWNER)
    dest.chmod(0o750)
    if origin not in ("unrecorded", "unrecorded-identical"):
        baseline = generated if origin in ("consumer-modified", "recorded-mode-only") else b"Old shipped asset\n"
        entry = dict(path=path, source="fixture", sha256="sha256:" + digest(baseline),
                     origin="preserved" if origin == "preserved" else "kit")
        (root / migration.LOCK).write_text(yaml.safe_dump({"footprint": [entry]}))
    return root


def prepare(root):
    result = command(root, "init", "--migrate", "--dry-run", "--json")
    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    (root / "migration-plan.json").write_text(result.stdout)
    return document


def apply(root, document, *extra):
    return command(root, "init", "--migrate", "--apply-plan", "migration-plan.json",
                   "--expect-plan", document["plan_sha256"], "--expect-config",
                   document["plan"]["source_config_sha256"], "--json", *extra)


@pytest.mark.parametrize("origin", ["unrecorded", "consumer-modified", "both-changed", "preserved",
                                  "unrecorded-identical"])
def test_migration_preserves_colliding_owner_asset_and_repeat_sync(tmp_path, origin):
    root = legacy_collision(tmp_path, origin)
    asset = root / COLLISION
    before = snapshot(asset)
    config_before = snapshot(root / migration.CONFIG)
    lock_before = snapshot(root / migration.LOCK) if (root / migration.LOCK).exists() else None
    document = prepare(root)
    assert snapshot(asset) == before
    result = apply(root, document)
    assert result.returncode == 0, result.stderr + result.stdout
    assert snapshot(asset) == before, "schema migration must retain active owner bytes, mode and mtime"
    assert COLLISION not in {row["path"] for row in document["plan"]["assets"]}
    assert COLLISION in {row["path"] for row in document["plan"]["protected"]}
    lock = yaml.safe_load((root / migration.LOCK).read_bytes())
    entry = next(row for row in lock["footprint"] if row["path"] == COLLISION)
    assert entry["origin"] == "preserved"
    assert entry["sha256"].removeprefix("sha256:") == digest(before[0])
    backup = root / json.loads(result.stdout)["backup"] / "files"
    assert snapshot(backup / COLLISION)[:2] == before[:2]
    assert snapshot(backup / migration.CONFIG)[:2] == config_before[:2]
    if lock_before:
        assert snapshot(backup / migration.LOCK)[:2] == lock_before[:2]
    resumed = apply(root, document, "--resume")
    assert resumed.returncode == 0, resumed.stderr + resumed.stdout
    assert json.loads(resumed.stdout)["changed"] == []
    for extra in (("--dry-run",), (), ()):
        synced = command(root, "sync", "--json", *extra)
        assert synced.returncode == 0, synced.stderr
        assert json.loads(synced.stdout)["changed"] == []
        assert COLLISION in json.loads(synced.stdout)["preserved"]
        assert snapshot(asset) == before


def test_collision_partial_apply_preserves_backup_and_resumes_config_last(tmp_path, monkeypatch):
    root = legacy_collision(tmp_path, "both-changed")
    before = snapshot(root / COLLISION)
    original_config = (root / migration.CONFIG).read_bytes()
    document = prepare(root)
    args = Namespace(dry_run=False, apply_plan="migration-plan.json", resume=False,
                     expect_plan=document["plan_sha256"],
                     expect_config=document["plan"]["source_config_sha256"])
    actual = migration.atomic

    def fail_config(root, path, data, **kwargs):
        if path == migration.CONFIG:
            raise OSError("injected config replacement failure")
        return actual(root, path, data, **kwargs)

    monkeypatch.setattr(migration, "atomic", fail_config)
    result = migration.migrate(root, args)
    assert result["ok"] is False and result["partial"] is True
    assert (root / migration.CONFIG).read_bytes() == original_config
    assert snapshot(root / COLLISION) == before
    monkeypatch.setattr(migration, "atomic", actual)
    result = apply(root, document, "--resume")
    assert result.returncode == 0, result.stderr + result.stdout
    assert json.loads(result.stdout)["changed"] == [migration.CONFIG]
    assert snapshot(root / COLLISION) == before
    assert snapshot(root / json.loads(result.stdout)["backup"] / "files" / COLLISION)[:2] == before[:2]


@pytest.mark.parametrize("path,origin", [
    (".claude/skills/print-next/SKILL.md", "unrecorded"),
    (".overseer/policy/model-routing.yaml", "unrecorded"),
    ("policy/model-routing.yaml", "unrecorded"),
    (".overseer/STANDING-DECISIONS.reference.md", "unrecorded"),
    (COLLISION, "recorded-mode-only"),
])
def test_portable_collisions_and_owner_mode_only_change_stay_protected(tmp_path, path, origin):
    root = legacy_collision(tmp_path, origin, path)
    before = snapshot(root / path)
    document = prepare(root)
    assert path in {row["path"] for row in document["plan"]["protected"]}
    assert path not in {row["path"] for row in document["plan"]["assets"]}
    result = apply(root, document)
    assert result.returncode == 0, result.stderr + result.stdout
    assert snapshot(root / path) == before
    assert snapshot(root / json.loads(result.stdout)["backup"] / "files" / path)[:2] == before[:2]
    result = command(root, "sync", "--json")
    assert result.returncode == 0, result.stderr
    assert path in json.loads(result.stdout)["preserved"]
    assert snapshot(root / path) == before


@pytest.mark.parametrize("change", ["bytes", "mode"])
def test_collision_drift_refuses_before_backup_or_apply(tmp_path, change):
    root = legacy_collision(tmp_path, "unrecorded")
    document = prepare(root)
    if change == "bytes":
        (root / COLLISION).write_bytes(OWNER + b"Concurrent owner edit\n")
    else:
        (root / COLLISION).chmod(0o600)
    before = snapshot(root / COLLISION)
    result = apply(root, document)
    assert result.returncode == 2
    assert snapshot(root / COLLISION) == before
    assert not (root / ".overseer/migrations").exists()
    assert not (root / migration.LAUNCHER).exists()


def multi_lane(tmp_path, schema):
    root = seed(tmp_path)
    result = command(root, "init")
    assert result.returncode == 0, result.stderr
    cfg = yaml.safe_load((root / migration.CONFIG).read_bytes())
    cfg["docs"]["lanes"]["architecture"] = dict(repo_id=cfg["repo"]["id"],
        handover="ARCH-HANDOVER.md", roadmap="ARCH-ROADMAP.md")
    (root / migration.CONFIG).write_text(yaml.safe_dump(cfg))
    if schema == 3:
        (root / "prompt.txt").write_text("Maintain architecture.\n")
        result = command(root, "next-write", "--repo-id", cfg["repo"]["id"],
            "--branch", "main", "--lane", "architecture", "--model", cfg["context"]["model"],
            "--action-id", "ARCH", "--action-kind", "maintain", "--prompt-file", "prompt.txt",
            "--expect-next", digest((root / migration.NEXT).read_bytes()))
        assert result.returncode == 0, result.stderr
        cfg["docs"]["lanes"]["security"] = dict(repo_id=cfg["repo"]["id"],
            handover="SECURITY-HANDOVER.md", roadmap="SECURITY-ROADMAP.md")
        (root / migration.CONFIG).write_text(yaml.safe_dump(cfg))
    assert v1.parse_next((root / migration.NEXT).read_bytes())[0]["schema"] == schema
    return root


@pytest.mark.parametrize("schema", [1, 3])
@pytest.mark.parametrize("preview", [False, True])
@pytest.mark.parametrize("selection", [(), ("--lane", "product")])
def test_repeat_init_preserves_present_lanes_and_missing_visibility(tmp_path, schema, preview, selection):
    root = multi_lane(tmp_path, schema)
    before = {path: snapshot(root / path) for path in (migration.NEXT, migration.CONFIG,
        "docs/ROADMAP.md", "docs/OVERSEER-HANDOVER.md")}
    result = command(root, "init", "--json", *(('--dry-run',) if preview else ()), *selection)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["changed"] == []
    assert before == {path: snapshot(root / path) for path in before}
    displayed = command(root, "next", "--all-lanes", "--json")
    assert displayed.returncode == 0, displayed.stderr
    lanes = json.loads(displayed.stdout)["lanes"]
    assert lanes["product"]["ok"]
    assert lanes["architecture"]["ok"] is (schema == 3)
    if schema == 3:
        assert lanes["security"]["ok"] is False
        assert "next_lane_missing" in lanes["security"]["error"]


@pytest.mark.parametrize("preview", [False, True])
def test_repeat_init_validates_unselected_present_lane(tmp_path, preview):
    root = multi_lane(tmp_path, 3)
    path = root / migration.NEXT
    data = path.read_bytes().replace(b"architecture:\n    branch: main", b"architecture:\n    branch: foreign")
    assert data != path.read_bytes()
    path.write_bytes(data)
    before = snapshot(path)
    result = command(root, "init", "--lane", "product", *(('--dry-run',) if preview else ()))
    assert result.returncode == 2 and "next_branch_mismatch" in result.stderr
    assert snapshot(path) == before
