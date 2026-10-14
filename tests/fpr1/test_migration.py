"""Schema migration acceptance through the product CLI plus injected failures."""
from argparse import Namespace
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from cli import product_migration as migration, v1
from cli.v1_io import Refusal, digest

KIT = Path(__file__).resolve().parents[2]


def command(root, *args):
    return subprocess.run([str(KIT / "cli/ok"), "-C", str(root), *args],
                          capture_output=True, text=True, timeout=30)


@pytest.fixture
def legacy(tmp_path):
    root = tmp_path / "legacy"
    root.mkdir()
    for args in (("init", "-b", "main"), ("config", "user.name", "Fixture"),
                 ("config", "user.email", "fixture@example.invalid"),
                 ("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "seed")):
        subprocess.run(["/usr/bin/git", "-C", str(root), *args], check=True, capture_output=True)
    (root / ".overseer").mkdir()
    config = (KIT / "tests/fixtures/config-two-lane.yaml").read_bytes()
    (root / migration.CONFIG).write_bytes(config)
    for path in ("QUEUE_HANDOVER.md", "QUEUE_ROADMAP.md", "videos/_active/HANDOVER.md",
                 "videos/_active/ROADMAP.md", ".cursor/rules/custom.mdc", ".overseer/policy/custom.yaml"):
        dest = root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("Owner content: " + path + "\n")
    return root


def options(**values):
    return Namespace(dry_run=values.get("dry_run", True), apply_plan=values.get("apply_plan"),
        expect_plan=values.get("expect_plan"), expect_config=values.get("expect_config"),
        resume=values.get("resume", False), lane=None, model=None, repo_name=None,
        regime=None, hooks=False, bound_id=None, refresh_runtime=values.get("refresh_runtime", False))


def prepare(root):
    result = command(root, "init", "--migrate", "--dry-run", "--json")
    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    (root / "migration-plan.json").write_text(result.stdout)
    args = options(dry_run=False, apply_plan="migration-plan.json",
                   expect_plan=document["plan_sha256"], expect_config=document["plan"]["source_config_sha256"])
    return document, args


def apply_cli(root, document, *extra):
    return command(root, "init", "--migrate", "--apply-plan", "migration-plan.json",
        "--expect-plan", document["plan_sha256"], "--expect-config",
        document["plan"]["source_config_sha256"], "--json", *extra)


def test_legacy_plan_is_read_only_deterministic_and_lossless(legacy):
    before = {p.relative_to(legacy): p.read_bytes() for p in legacy.rglob("*") if p.is_file() and ".git" not in p.parts}
    first = command(legacy, "init", "--migrate", "--dry-run", "--json")
    second = command(legacy, "init", "--migrate", "--dry-run", "--json")
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert first.stdout == second.stdout
    assert before == {p.relative_to(legacy): p.read_bytes() for p in legacy.rglob("*") if p.is_file() and ".git" not in p.parts}
    document, _ = prepare(legacy)
    result = apply_cli(legacy, document)
    assert result.returncode == 0, result.stderr + result.stdout
    config = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    assert config["schema"] == 3
    assert config["context"]["lane"] == "queue"
    assert set(config["docs"]["lanes"]) == {"queue", "active"}
    assert config["freeze_contract"]["reviewer"]["model"] == "thinking-high"
    assert config["repo"]["root_relative_docs"] == "."
    assert not (legacy / migration.NEXT).exists()
    for path, body in before.items():
        if str(path) != migration.CONFIG:
            assert (legacy / path).read_bytes() == body
    result_data = json.loads(result.stdout)
    backup = legacy / result_data["backup"]
    assert (backup / "files" / migration.CONFIG).read_bytes() == before[Path(migration.CONFIG)]
    assert json.loads((backup / "manifest.json").read_text())["per_file_atomic_only"] is True
    again = apply_cli(legacy, document, "--resume")
    assert again.returncode == 0, again.stderr + again.stdout
    assert json.loads(again.stdout)["changed"] == []


def test_bounded_migration_preserves_uuid_next_and_launch_binding(tmp_path):
    root = tmp_path / "bounded"
    root.mkdir()
    subprocess.run(["/usr/bin/git", "init", "-b", "main", str(root)], check=True, capture_output=True)
    result = command(root, "init")
    assert result.returncode == 0, result.stderr
    config = yaml.safe_load((root / migration.CONFIG).read_bytes())
    bounded = {"schema": 1, "repo": {k: config["repo"][k] for k in ("name", "id", "root")},
               "context": config["context"], "runtime": config["runtime"], "vcs": "git"}
    original = b"# preserve this comment\n" + v1.encode(bounded)
    (root / migration.CONFIG).write_bytes(original)
    (root / migration.CONFIG).chmod(0o600)
    next_bytes = (root / migration.NEXT).read_bytes()
    document, _ = prepare(root)
    result = apply_cli(root, document)
    assert result.returncode == 0, result.stderr + result.stdout
    assert (root / migration.NEXT).read_bytes() == next_bytes
    assert (root / migration.CONFIG).stat().st_mode & 0o777 == 0o600
    migrated = yaml.safe_load((root / migration.CONFIG).read_bytes())
    assert migrated["repo"]["id"] == bounded["repo"]["id"]
    assert subprocess.run([str(root / ".overseer/bin/ok"), "next"], cwd=root,
                          capture_output=True, text=True).returncode == 0


@pytest.mark.parametrize("mutation", ["config", "living", "mode", "head"])
def test_plan_drift_refuses_before_mutation(legacy, mutation):
    document, _ = prepare(legacy)
    if mutation == "config":
        with (legacy / migration.CONFIG).open("ab") as stream:
            stream.write(b"\n# changed after review\n")
    elif mutation == "living":
        (legacy / "QUEUE_HANDOVER.md").write_text("Changed after review\n")
    elif mutation == "mode":
        (legacy / migration.CONFIG).chmod(0o600)
    else:
        subprocess.run(["/usr/bin/git", "-C", str(legacy), "-c", "core.hooksPath=/dev/null",
                        "commit", "--allow-empty", "-m", "moved"], check=True, capture_output=True)
    result = apply_cli(legacy, document)
    assert result.returncode != 0
    assert not (legacy / ".overseer/migrations").exists()
    assert not (legacy / migration.LAUNCHER).exists()


def test_partial_replacement_keeps_old_config_and_resumes(legacy, monkeypatch):
    document, args = prepare(legacy)
    original = (legacy / migration.CONFIG).read_bytes()
    actual = migration.atomic

    def fail_config(root, path, data, **kwargs):
        if path == migration.CONFIG:
            raise OSError("injected replacement failure")
        return actual(root, path, data, **kwargs)

    monkeypatch.setattr(migration, "atomic", fail_config)
    result = migration.migrate(legacy, args)
    assert result["ok"] is False and result["partial"] is True
    assert result["completed"] == [migration.LAUNCHER]
    assert (legacy / migration.CONFIG).read_bytes() == original
    monkeypatch.setattr(migration, "atomic", actual)
    args.resume = True
    result = migration.migrate(legacy, args)
    assert result["ok"] is True
    assert result["changed"] == [migration.CONFIG]
    assert (legacy / result["backup"] / "files" / migration.CONFIG).read_bytes() == original


def test_after_lock_context_change_refuses_without_replacement(legacy, monkeypatch):
    _, args = prepare(legacy)
    actual = migration.fcntl.flock

    def change_after_lock(fd, mode):
        actual(fd, mode)
        subprocess.run(["/usr/bin/git", "-C", str(legacy), "checkout", "-b", "other"],
                       check=True, capture_output=True)

    monkeypatch.setattr(migration.fcntl, "flock", change_after_lock)
    result = migration.migrate(legacy, args)
    assert result["ok"] is False
    assert result["completed"] == []
    assert not (legacy / migration.LAUNCHER).exists()


def test_before_replace_context_change_refuses_candidate(legacy, monkeypatch):
    _, args = prepare(legacy)
    actual = migration.atomic

    def change_before_replace(root, path, data, **kwargs):
        if path == migration.LAUNCHER:
            prior = kwargs["before_replace"]

            def changed():
                (root / "QUEUE_HANDOVER.md").write_text("concurrent owner edit\n")
                prior()

            kwargs["before_replace"] = changed
        return actual(root, path, data, **kwargs)

    monkeypatch.setattr(migration, "atomic", change_before_replace)
    result = migration.migrate(legacy, args)
    assert result["ok"] is False and result["partial"] is False
    assert "protected_asset_changed" in result["error"]
    assert not (legacy / migration.LAUNCHER).exists()


def test_symlink_preflight_does_not_start_backup(legacy, tmp_path):
    document, _ = prepare(legacy)
    outside = tmp_path / "outside"
    outside.mkdir()
    (legacy / ".overseer/bin").symlink_to(outside, target_is_directory=True)
    result = apply_cli(legacy, document)
    assert result.returncode != 0
    assert not (legacy / ".overseer/migrations").exists()
    assert list(outside.iterdir()) == []


def test_legacy_prompt_is_exact_draft_only_and_conflicts_refuse(legacy):
    draft = "Model: preserved historical label\nDo the old task.\n"
    (legacy / "QUEUE_HANDOVER.md").write_text("History stays.\n### Paste-ready prompt\n\n```text\n" + draft + "```\n")
    document, _ = prepare(legacy)
    assert document["plan"]["legacy_prompt_drafts"][0]["text"] == draft
    assert not (legacy / migration.NEXT).exists()
    (legacy / "videos/_active/HANDOVER.md").write_text("### Paste-ready prompt\n```text\nConflicting task.\n```\n")
    result = command(legacy, "init", "--migrate", "--dry-run")
    assert result.returncode != 0 and "conflicting_legacy_prompts" in result.stderr


def test_unknown_setting_and_hook_install_refuse(legacy):
    result = command(legacy, "init", "--migrate", "--dry-run", "--hooks")
    assert result.returncode != 0 and "existing_repository_hooks" in result.stderr
    with (legacy / migration.CONFIG).open("ab") as stream:
        stream.write(b"unknown_feature: true\n")
    result = command(legacy, "init", "--migrate", "--dry-run")
    assert result.returncode != 0 and "unknown_unmapped_settings" in result.stderr


def test_preserved_origin_and_custom_assets_are_classified_without_takeover(legacy):
    path = ".cursor/hooks.json"
    (legacy / path).write_text("custom hooks\n")
    (legacy / migration.LOCK).write_text(yaml.safe_dump({"footprint": [
        {"path": path, "source": "cursor/hooks/hooks.json", "sha256": digest(b"custom hooks\n"), "origin": "preserved"}]}))
    rows = migration.classify_assets(legacy, {path: b"new hooks\n"}, {})
    assert rows[0]["classification"] == "preserved"


def test_expected_plan_digest_refuses_tampered_document(legacy):
    document, _ = prepare(legacy)
    document["plan"]["diagnostics"].append("unreviewed edit")
    (legacy / "migration-plan.json").write_text(json.dumps(document))
    result = apply_cli(legacy, document)
    assert result.returncode != 0 and "plan_digest_mismatch" in result.stderr
    assert not (legacy / ".overseer/migrations").exists()


def test_custom_launcher_is_not_taken_over(legacy):
    document, _ = prepare(legacy)
    config = document["plan"]["normalized_config"]
    (legacy / ".overseer/bin").mkdir()
    custom = v1.launcher(legacy, config["repo"]["id"]) + b"# owner customization\n"
    (legacy / migration.LAUNCHER).write_bytes(custom)
    result = command(legacy, "init", "--migrate", "--dry-run")
    assert result.returncode != 0 and "launcher_binding_conflict" in result.stderr
    assert (legacy / migration.LAUNCHER).read_bytes() == custom


def test_referenced_optional_assets_are_in_the_digest_plan(legacy):
    raw = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    raw.update({"honesty": {"enabled": True, "ledger": "custom/ledger.jsonl", "roles_file": "custom/roles.yaml"},
                "model_routing": {"enabled": True, "policy": "custom/models.yaml"},
                "extensions": [{"id": "owner", "schema_version": 1, "config_path": "custom/extension.yaml"}]})
    (legacy / migration.CONFIG).write_bytes(v1.encode(raw))
    for path in ("custom/ledger.jsonl", "custom/roles.yaml", "custom/models.yaml", "custom/extension.yaml"):
        target = legacy / path
        target.parent.mkdir(exist_ok=True)
        target.write_text("preserved\n")
    document, _ = prepare(legacy)
    protected = {entry["path"]: entry for entry in document["plan"]["protected"]}
    for path in ("custom/ledger.jsonl", "custom/roles.yaml", "custom/models.yaml", "custom/extension.yaml"):
        assert protected[path]["sha256"] == digest(b"preserved\n")
    (legacy / "custom/ledger.jsonl").write_text("concurrent ledger append\n")
    assert apply_cli(legacy, document).returncode != 0


def test_runtime_refresh_is_explicit_and_sync_does_not_migrate_schema(legacy):
    document, _ = prepare(legacy)
    assert apply_cli(legacy, document).returncode == 0
    current = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    bounded = {"schema": 1, "repo": {k: current["repo"][k] for k in ("name", "id", "root")},
               "context": current["context"], "runtime": {**current["runtime"], "sha256": "0" * 64}, "vcs": "git"}
    (legacy / migration.CONFIG).write_bytes(v1.encode(bounded))
    plan, _ = prepare(legacy)
    assert plan["plan"]["apply_supported"] is False
    assert apply_cli(legacy, plan).returncode != 0
    refreshed = command(legacy, "init", "--migrate", "--dry-run", "--refresh-runtime", "--json")
    assert refreshed.returncode == 0, refreshed.stderr
    assert json.loads(refreshed.stdout)["plan"]["apply_supported"] is True
    result = command(legacy, "sync", "--json")
    assert result.returncode == 0, result.stderr
    after = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    assert after["schema"] == 1
    assert after["repo"] == bounded["repo"]
    assert after["runtime"] == v1.runtime()
    assert not (legacy / migration.NEXT).exists()


def test_october_muse_plan_preserves_authority_and_never_calls_git_revision(legacy, monkeypatch):
    original = {"schema": 2, "repo": {"name": "muse-fixture", "id": "861dc94a-579c-4980-bcba-bfa10fdd4c17", "root": str(legacy)},
        "context": {"lane": "product", "model": "Selected"}, "runtime": v1.runtime(), "vcs": "muse",
        "muse": {"repo_id": "sha256:" + "b" * 64, "store": str(legacy / ".muse"),
            "runtime": {"python": str(legacy / "muse-env/bin/python"), "version": "0.2.1rc5", "sha256": "c" * 64}}}
    (legacy / migration.CONFIG).write_bytes(v1.encode(original))

    def forbidden(*args, **kwargs):
        pytest.fail("Muse migration selected Git revision")

    monkeypatch.setattr(v1, "branch", forbidden)
    monkeypatch.setattr(v1, "head", forbidden)
    before = (legacy / migration.CONFIG).read_bytes()
    with pytest.raises(Refusal, match='muse_python_requires_separate_venv'):
        migration.migrate(legacy, options())
    assert (legacy / migration.CONFIG).read_bytes() == before
    from cli.product_config import normalize
    config = normalize(before, root=legacy).data
    assert config["vcs"]["canonical"] == "muse"
    assert config["vcs"]["muse"]["binding"] == original["muse"]


def test_sync_partial_asset_failure_is_explicit(tmp_path, monkeypatch):
    root = tmp_path / "sync"
    root.mkdir()
    subprocess.run(["/usr/bin/git", "init", "-b", "main", str(root)], check=True, capture_output=True)
    assert command(root, "init").returncode == 0
    original = (root / migration.CONFIG).read_bytes()
    from cli.product_config import normalize
    config = normalize(original, root=root, runtime=v1.runtime()).data
    args = Namespace(hooks=True, only=None, preserve_modified=False, diff=False, dry_run=False)
    actual = migration.atomic

    def fail_second(root, path, data, **kwargs):
        if path.endswith("session-end-closeout.sh"):
            raise OSError("injected")
        return actual(root, path, data, **kwargs)

    monkeypatch.setattr(migration, "atomic", fail_second)
    with pytest.raises(Refusal, match="partial_asset_update"):
        migration.sync(root, config, original, args)
    assert (root / migration.CONFIG).read_bytes() == original
    monkeypatch.setattr(migration, "atomic", actual)
    assert migration.sync(root, config, original, args)["ok"] is True


def test_unchanged_launcher_mode_remains_in_preflight(legacy):
    document, _ = prepare(legacy)
    assert apply_cli(legacy, document).returncode == 0
    config = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    bounded = {"schema": 1, "repo": {k: config["repo"][k] for k in ("name", "id", "root")},
               "context": config["context"], "runtime": config["runtime"], "vcs": "git"}
    (legacy / migration.CONFIG).write_bytes(v1.encode(bounded))
    document, _ = prepare(legacy)
    assert migration.LAUNCHER not in {row["path"] for row in document["plan"]["assets"]}
    assert migration.LAUNCHER in {row["path"] for row in document["plan"]["protected"]}
    (legacy / migration.LAUNCHER).chmod(0o644)
    result = apply_cli(legacy, document)
    assert result.returncode != 0
    assert yaml.safe_load((legacy / migration.CONFIG).read_bytes())["schema"] == 1


@pytest.mark.parametrize("mutation", [lambda p: p.update(assets=[None]),
    lambda p: p.update(normalized_config=None), lambda p: p.update(normalized_config={}),
    lambda p: p.update(protected=[{"path": "bad"}])])
def test_malformed_reviewed_plan_refuses_without_traceback(legacy, mutation):
    document, _ = prepare(legacy)
    mutation(document["plan"])
    document["plan_sha256"] = digest(migration._json(document["plan"]))
    (legacy / "migration-plan.json").write_text(json.dumps(document))
    result = apply_cli(legacy, document)
    assert result.returncode == 2
    assert "refused:" in result.stderr and "Traceback" not in result.stderr
    assert not (legacy / ".overseer/migrations").exists()


def test_canonical_json_plan_order_does_not_change_yaml_candidate(legacy):
    document, _ = prepare(legacy)
    (legacy / "migration-plan.json").write_bytes(migration._json(document))
    result = apply_cli(legacy, document)
    assert result.returncode == 0, result.stderr + result.stdout


def test_preserved_launcher_mode_is_not_promoted_by_migration(legacy):
    document, _ = prepare(legacy)
    config = document["plan"]["normalized_config"]
    body = v1.launcher(legacy, config["repo"]["id"])
    (legacy / ".overseer/bin").mkdir()
    (legacy / migration.LAUNCHER).write_bytes(body)
    (legacy / migration.LAUNCHER).chmod(0o644)
    (legacy / migration.LOCK).write_text(yaml.safe_dump({"footprint": [{"path": migration.LAUNCHER,
        "source": "owned", "sha256": digest(body), "origin": "preserved"}]}))
    result = command(legacy, "init", "--migrate", "--dry-run")
    assert result.returncode == 2 and "preserved_asset_requires_resolution" in result.stderr
    assert (legacy / migration.LAUNCHER).stat().st_mode & 0o777 == 0o644


def test_explicit_sync_upgrades_exact_bounded_hooks_only(tmp_path):
    root = tmp_path / "bounded-hooks"
    root.mkdir()
    subprocess.run(["/usr/bin/git", "init", "-b", "main", str(root)], check=True, capture_output=True)
    assert command(root, "init", "--hooks").returncode == 0
    next_bytes = (root / migration.NEXT).read_bytes()
    for path, data in migration._bounded_hook_assets(root).items():
        (root / path).write_bytes(data)
    result = command(root, "sync", "--hooks", "--only", "hooks", "--json")
    assert result.returncode == 0, result.stderr
    assert (root / migration.NEXT).read_bytes() == next_bytes
    assert "--event sessionStart" in (root / ".cursor/hooks/session-start-next.sh").read_text()
    config = root / ".cursor/hooks.json"
    custom = config.read_bytes() + b"\n"
    config.write_bytes(custom)
    refused = command(root, "sync", "--hooks")
    assert refused.returncode == 2 and "sync_asset_modified" in refused.stderr
    assert config.read_bytes() == custom


@pytest.mark.parametrize("body", ["plan:\n  context: 2026-10-14\n", '{"plan": {}, "plan": {}}', '{"plan": NaN}'])
def test_plan_input_is_strict_finite_unique_json(legacy, body):
    document, _ = prepare(legacy)
    (legacy / "migration-plan.json").write_text(body)
    result = apply_cli(legacy, document)
    assert result.returncode == 2
    assert "refused: migration_plan_" in result.stderr and "Traceback" not in result.stderr
    assert not (legacy / ".overseer/migrations").exists()


def _sync_fixture(tmp_path):
    root = tmp_path / "sync-selection"
    root.mkdir()
    subprocess.run(["/usr/bin/git", "init", "-b", "main", str(root)], check=True, capture_output=True)
    result = command(root, "init", "--hooks")
    assert result.returncode == 0, result.stderr
    return root


def test_sync_glob_selects_only_available_scripts_with_read_only_diff(tmp_path):
    root = _sync_fixture(tmp_path)
    old = migration._bounded_hook_assets(root)
    for path, body in old.items():
        (root / path).write_bytes(body)
    next_bytes = (root / migration.NEXT).read_bytes()
    result = command(root, "sync", "--hooks", "--only", ".cursor/hooks/session-*.sh",
                     "--dry-run", "--diff", "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    selected = {".cursor/hooks/session-start-next.sh", ".cursor/hooks/session-end-closeout.sh"}
    assert set(report["changed"]) == selected
    assert set(report["diff"]) == selected
    assert all("--event" in value for value in report["diff"].values())
    assert all((root / path).read_bytes() == body for path, body in old.items())
    result = command(root, "sync", "--hooks", "--only", ".cursor/hooks/session-*.sh", "--json")
    assert result.returncode == 0, result.stderr
    assert set(json.loads(result.stdout)["changed"]) == selected
    assert (root / ".cursor/hooks.json").read_bytes() == old[".cursor/hooks.json"]
    assert (root / migration.NEXT).read_bytes() == next_bytes


@pytest.mark.parametrize("selector", [".cursor/hooks/*.sh", ".overseer/instructions/*", "*"])
def test_sync_hook_glob_requires_explicit_hook_selection(tmp_path, selector):
    root = _sync_fixture(tmp_path)
    before = {path: (root / path).read_bytes() for path in migration.HOOKS}
    result = command(root, "sync", "--only", selector)
    assert result.returncode == 2 and "sync_hooks_requires_explicit_hooks" in result.stderr
    assert all((root / path).read_bytes() == body for path, body in before.items())


def test_sync_unmatched_selection_refuses_before_runtime_refresh(tmp_path):
    root = _sync_fixture(tmp_path)
    config = yaml.safe_load((root / migration.CONFIG).read_bytes())
    config["runtime"]["sha256"] = "0" * 64
    original = v1.encode(config)
    (root / migration.CONFIG).write_bytes(original)
    result = command(root, "sync", "--only", "launcher", "--only", "policy/*.yaml")
    assert result.returncode == 2 and "sync_only_no_matches" in result.stderr
    assert (root / migration.CONFIG).read_bytes() == original


def test_sync_glob_preserves_origin_and_explicit_custom_settings(tmp_path):
    root = _sync_fixture(tmp_path)
    start = ".cursor/hooks/session-start-next.sh"
    end = ".cursor/hooks/session-end-closeout.sh"
    old = migration._bounded_hook_assets(root)
    (root / start).write_bytes(old[start])
    custom = old[end] + b"# owner customization\n"
    (root / end).write_bytes(custom)
    (root / migration.LOCK).write_text(yaml.safe_dump({"footprint": [{"path": start,
        "source": "cursor/hooks/session-start-next.sh", "sha256": digest(old[start]), "origin": "preserved"}]}))
    refused = command(root, "sync", "--hooks", "--only", ".cursor/hooks/*.sh")
    assert refused.returncode == 2 and "sync_asset_modified" in refused.stderr
    result = command(root, "sync", "--hooks", "--only", ".cursor/hooks/*.sh", "--preserve-modified", "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert set(report["preserved"]) == {start, end}
    assert report["changed"] == []
    assert (root / start).read_bytes() == old[start]
    assert (root / end).read_bytes() == custom
