"""New configuration contract; historical adapter fixtures/tests stay intact."""
from pathlib import Path
import subprocess
import sys
import uuid

import pytest
import yaml

from cli.product_config import normalize
from cli.v1_io import Refusal

KIT = Path(__file__).resolve().parents[2]
IDENTITY = "861dc94a-579c-4980-bcba-bfa10fdd4c17"


def encoded(value):
    return yaml.safe_dump(value, sort_keys=False).encode()


def legacy_config():
    return yaml.safe_load((KIT / "tests/fixtures/config-two-lane.yaml").read_text())


def runtime(root):
    return {"root": str(root), "version": "1.0.0.dev1", "sha256": "a" * 64}


def bounded(root, schema=1, authority="git"):
    value = {"schema": schema, "repo": {"name": "fixture", "id": IDENTITY, "root": str(root)},
             "context": {"lane": "product", "model": "A selected model"},
             "runtime": runtime(root), "vcs": authority}
    if authority == "muse":
        value["muse"] = {"repo_id": "sha256:" + "b" * 64, "store": str(root / ".muse"),
            "runtime": {"python": str(root / "muse-env/bin/python"), "version": "0.2.1rc5", "sha256": "c" * 64}}
    return value


def test_read_only_legacy_inspection_is_unbound_and_preserves_lanes(tmp_path):
    original = legacy_config()
    value = normalize(encoded(original), root=tmp_path)
    assert value.source_schema == "legacy-full"
    assert not value.bound
    assert value.data["repo"]["id"] is None
    assert value.data["runtime"] is None
    assert value.data["context"]["lane"] == "queue"
    assert set(value.data["docs"]["lanes"]) == {"queue", "active"}
    assert value.adapter.docs.lanes["active"].handover == "videos/_active/HANDOVER.md"
    assert not list(tmp_path.iterdir())


def test_every_optional_setting_and_hosted_limits_survive_bind_and_roundtrip(tmp_path):
    original = legacy_config()
    original.update({
        "checkpoints": {"enabled": True, "policy": "policy/custom.yaml", "active_manifest": "docs/manifest.yaml",
                        "progress": "docs/progress.json", "orchestrator": "scripts/check.py", "allow_hand_verified": False},
        "honesty": {"enabled": True, "ledger": "ledger/custom.jsonl", "roles_file": "policy/roles.yaml",
                    "require_verdict_on": ["handoff"], "require_l1_evidence": "require",
                    "require_verification_evidence": "warn", "require_deploy_health": "off",
                    "require_independent_second_reviewer": "warn", "adversarial_freeze": "suggest",
                    "allow_signed_approval": True, "ci_reexecutor": "scripts/reexecute.py", "require_agent_signature": False},
        "modules": {"governance": {"enabled": True}, "checkpoints": {"enabled": True}, "honesty": {"enabled": True}},
        "extensions": [{"id": "custom", "schema_version": 7, "config_path": "policy/extension.yaml"}],
        "governance_gates": {"remind": False, "freeze_review": {"required_before_auto": False},
                             "build_verification": {"required_before_done": True}, "surfaces": ["status"]},
        "model_routing": {"enabled": True, "policy": "policy/models-custom.yaml"},
        "cost_awareness": {"enabled": True, "surfaces": ["status"]},
        "session_bookends": {"enabled": True},
        "workspace": {"constellation_id": "one", "product_order_root": "../workspace", "manifest": "workspace.yaml"},
        "hosted_dashboard": {"enabled": True, "allow_non_loopback": False, "cors_origins": ["https://example.test"],
            "org_allowlist": ["owner/repo"], "sources": {"github_contents": True, "github_meta": True,
            "github_checks_advisory": True, "musehub_read": True}, "enumeration_cap": 12,
            "musehub_hosts": ["muse.example.test"], "musehub_base_url": "https://muse.example.test", "max_doc_bytes": 8192},
        "close_ritual": {"enabled": True, "mode": "prepare_pr", "require_paths": ["docs/NEXT.md"],
            "consumer_verify_script": "scripts/verify.py", "post_land_sync": {"enabled": False,
            "strategy": "ff_only", "require_clean_worktree": True}},
    })
    first = normalize(encoded(original), root=tmp_path, runtime=runtime(tmp_path), bind=True, identity=IDENTITY)
    second = normalize(first.to_bytes(), root=tmp_path, runtime=runtime(tmp_path))
    assert first.bound and second.bound
    for field in set(original) - {"overseer_config_version", "repo", "docs"}:
        assert first.data[field] == original[field] == second.data[field]
    assert first.data == second.data
    assert first.hosted_dashboard.enumeration_cap == 12
    assert first.hosted_dashboard.max_doc_bytes == 8192
    assert first.hosted_dashboard.musehub_base_url == "https://muse.example.test"
    assert any("ignored" in message and "custom" in message for message in first.diagnostics)
    assert all(lane["repo_id"] == IDENTITY for lane in first.data["docs"]["lanes"].values())
    assert any(item["before_path"] == "hosted_dashboard.enumeration_cap" and item["disposition"] == "preserved"
               for item in first.field_map)


@pytest.mark.parametrize(("schema", "authority", "source"), [(1, "git", "bounded-1"), (2, "git", "october-2"), (2, "muse", "october-2")])
def test_bounded_inputs_preserve_exact_bindings_without_runtime_refresh(tmp_path, schema, authority, source):
    original = bounded(tmp_path, schema, authority)
    changed_runtime = {**runtime(tmp_path), "sha256": "d" * 64}
    value = normalize(encoded(original), root=tmp_path, runtime=changed_runtime, bind=True)
    assert value.source_schema == source
    assert value.authority == authority
    assert value.data["repo"]["id"] == IDENTITY
    assert value.data["context"] == original["context"]
    assert value.data["runtime"] == original["runtime"]
    if authority == "muse":
        assert value.data["vcs"]["muse"]["binding"] == original["muse"]


@pytest.mark.parametrize("mutation,reason", [
    (lambda d: d.update(future_setting=True), "unknown_unmapped_settings"),
    (lambda d: d["repo"].update(mysterious=True), "unknown_unmapped_settings"),
    (lambda d: d["vcs"]["git"].update(other_remote="elsewhere"), "unknown_unmapped_settings"),
    (lambda d: d["docs"]["lanes"]["active"].update(future=True), "unknown_unmapped_settings"),
    (lambda d: d["thresholds"].update(future=True), "unknown_unmapped_settings"),
    (lambda d: d["vcs"].update(canonical="muse"), "git-only regime requires"),
    (lambda d: d.update(modules={"checkpoints": {"enabled": True}}), "must equal"),
    (lambda d: d["docs"]["lanes"]["active"].update(handover="QUEUE_HANDOVER.md"), "config_document_alias"),
    (lambda d: d["docs"]["lanes"]["active"].update(repo_id=str(uuid.uuid4())), "config_lane_owner_mismatch"),
    (lambda d: d["docs"].update(roadmap="OTHER.md"), "must match"),
    (lambda d: d["docs"]["lanes"]["active"].update(roadmap="../outside.md"), "config_path_invalid"),
    (lambda d: d["docs"].update(canonical_next="NEXT.md"), "config_canonical_next"),
    (lambda d: d.update(schema=3), "unknown_unmapped_settings"),
    (lambda d: d.update(context={"lane": "active", "model": "same"}), "config_default_lane_conflict"),
    (lambda d: d.update(hosted_dashboard={"sources": {"future": True}}), "unknown hosted_dashboard.sources"),
    (lambda d: d["thresholds"].update(realign_max_commits=True), "config_integer_required"),
    (lambda d: d["freeze_contract"].update(reviewer={"mode": "human", "provider": "unknown"}), "config_reviewer_provider_invalid"),
    (lambda d: d.update(hosted_dashboard={"enumeration_cap": True}), "config_integer_required"),
    (lambda d: d.update(hosted_dashboard={"musehub_hosts": [123]}), "config_hosted_hosts_must_be_strings"),
])
def test_contradictions_and_unmapped_settings_refuse(tmp_path, mutation, reason):
    original = legacy_config()
    mutation(original)
    with pytest.raises(Refusal, match=reason):
        normalize(encoded(original), root=tmp_path, bind=True, runtime=runtime(tmp_path))


@pytest.mark.parametrize("suffix", ["\nrepo: {}\n", "\nworkspace:\n  constellation_id: one\n  constellation_id: two\n", "\nextra: &a {again: *a}\n"])
def test_duplicate_nested_and_recursive_yaml_refuse(tmp_path, suffix):
    with pytest.raises(Refusal, match="duplicate_or_invalid_key|recursive_config_alias|malformed_config"):
        normalize(encoded(legacy_config()) + suffix.encode(), root=tmp_path)


@pytest.mark.parametrize("changed", ["root", "identity", "runtime", "lane", "model"])
def test_existing_binding_never_silently_changes(tmp_path, changed):
    value = bounded(tmp_path)
    options = {"root": tmp_path, "runtime": runtime(tmp_path), "bind": True}
    if changed == "root":
        options["root"] = tmp_path / "elsewhere"
    elif changed == "identity":
        options["identity"] = str(uuid.uuid4())
    elif changed == "runtime":
        options["runtime"] = runtime(tmp_path / "installation")
    else:
        options[changed] = "different"
    with pytest.raises(Refusal):
        normalize(encoded(value), **options)


@pytest.mark.parametrize("field", ["id", "root", "runtime", "context"])
def test_bounded_binding_missing_values_are_not_repaired_implicitly(tmp_path, field):
    value = bounded(tmp_path)
    if field in ("id", "root"):
        value["repo"][field] = None
    else:
        value[field] = None
    with pytest.raises(Refusal):
        normalize(encoded(value), root=tmp_path, bind=True, runtime=runtime(tmp_path))


def test_symlink_policy_and_nondefault_lane_paths_refuse(tmp_path):
    external = tmp_path / "outside"
    external.mkdir()
    (tmp_path / "policy").symlink_to(external, target_is_directory=True)
    value = legacy_config()
    value["model_routing"] = {"enabled": True, "policy": "policy/custom.yaml"}
    with pytest.raises(Refusal, match="config_path_symlink"):
        normalize(encoded(value), root=tmp_path)


def test_linked_muse_working_directory_is_reported_and_binding_requires_pairing(tmp_path):
    value = yaml.safe_load((KIT / "tests/fixtures/config-muse-only.yaml").read_text())
    value["vcs"]["muse"]["working_dir"] = "linked"
    inspected = normalize(encoded(value), root=tmp_path)
    assert inspected.authority == "muse"
    assert "muse_working_dir_requires_explicit_pairing" in inspected.diagnostics
    with pytest.raises(Refusal, match="muse_working_dir_requires_explicit_pairing"):
        normalize(encoded(value), root=tmp_path, bind=True, runtime=runtime(tmp_path))


def test_all_preserved_valid_config_fixtures_load_without_muse_imports(tmp_path):
    paths = sorted((KIT / "tests/fixtures").rglob("config-*.yaml"))
    for path in paths:
        if path.name == "config-governance-gates-bad.yaml":
            continue
        normalize(path.read_bytes(), root=tmp_path)
    script = "import sys; from cli.product_config import normalize; assert not any(k.startswith(('muse.', 'adapters.muse_', 'cryptography')) for k in sys.modules)"
    completed = subprocess.run([sys.executable, "-c", script], cwd=KIT, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
