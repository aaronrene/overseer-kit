"""Real reviewed Muse reads; stale rc5 bindings are metadata-only fixtures."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from cli import v1
from cli.v1_io import Refusal, digest
from cli.v1_revision import MUSE_RUNTIMES, muse_read, revision
from cli.version_lock import FootprintEntry, compute_lock_digest
from tests.integration.test_legacy_migration_compat import command, snapshot
from tests.muse.test_legacy_native_binding import native, dry, save, apply, controls


@pytest.fixture
def stale_binding(native, muse_python):
    document = save(native, dry(native, muse_python, "--tracked-bindings", "preserve"))
    result = apply(native, document, "--tracked-bindings", "preserve")
    assert result.returncode == 0, result.stderr
    config = yaml.safe_load((native / v1.CONFIG).read_bytes())
    assert config["vcs"]["muse"]["binding"]["runtime"]["version"] == "0.2.1rc11"
    config["vcs"]["muse"]["binding"]["runtime"].update(
        version="0.2.1rc5", sha256=MUSE_RUNTIMES["0.2.1rc5"])
    # The obsolete installation need not exist or execute during rebinding.
    config["runtime"].update(root=str(native.parent / "obsolete-kit"), sha256="a" * 64)
    old_launcher = v1.launcher(native, config["repo"]["id"], runtime_root=config["runtime"]["root"])
    (native / ".overseer/bin/ok").write_bytes(old_launcher)
    lock_path = native / ".overseer/version.lock"
    lock = yaml.safe_load(lock_path.read_bytes())
    for row in lock["footprint"]:
        if row["path"] == ".overseer/bin/ok":
            row["sha256"] = "sha256:" + digest(old_launcher)
    lock["footprint_digest"] = compute_lock_digest([FootprintEntry(**row) for row in lock["footprint"]])
    lock_path.write_bytes(v1.encode(lock))
    (native / v1.CONFIG).write_bytes(v1.encode(config))
    return native


def arguments(root, python):
    config = yaml.safe_load((root / v1.CONFIG).read_bytes())
    state = muse_read(root, str(python))
    return ["adopt", "--rebind-muse-runtime", "--muse-python", str(python),
            "--expect-config", digest((root / v1.CONFIG).read_bytes()),
            "--repo-id", config["repo"]["id"], "--lane", config["context"]["lane"],
            "--model", config["context"]["model"], "--branch", state["branch"],
            "--base-head", state["head"], "--tracked-bindings", "preserve", "--json"]


def preview(root, args):
    result = command(root, *args, "--dry-run")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_real_rc11_rebind_preserves_settings_source_history_and_publishes_separately(stale_binding, muse_python):
    root = stale_binding
    args = arguments(root, muse_python)
    before = snapshot(root)
    before_controls = controls(root)
    original = (root / v1.CONFIG).read_bytes()
    config = yaml.safe_load(original)
    with pytest.raises(Refusal, match="muse_runtime_changed"):
        revision(root, config)
    planned = preview(root, args)
    assert preview(root, args) == planned and snapshot(root) == before
    plan = planned["plan"]
    assert plan["before_binding"]["runtime"]["version"] == "0.2.1rc5"
    assert plan["after_binding"]["runtime"]["version"] == "0.2.1rc11"
    assert set(planned["changed"]) == {
        plan["backup"] + "/" + path for path in (v1.CONFIG, ".overseer/bin/ok", ".overseer/version.lock")
    } | {v1.CONFIG, ".overseer/bin/ok", ".overseer/version.lock"}
    expected = deepcopy(config)
    expected["runtime"] = v1.runtime()
    expected["vcs"]["muse"]["binding"]["runtime"] = muse_read(root, str(muse_python))["runtime"]
    assert plan["normalized_config"] == expected
    result = command(root, *args, "--expect-rebind", planned["rebind_sha256"])
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load((root / v1.CONFIG).read_bytes()) == expected
    after = snapshot(root)
    assert {p: v for p, v in after.items() if p not in planned["changed"]} == {
        p: v for p, v in before.items() if p not in planned["changed"]}
    assert controls(root) == before_controls
    assert (root / plan["backup"] / v1.CONFIG).read_bytes() == original
    assert not (root / v1.NEXT).exists()
    # Repeated apply, with old expected config, refuses.
    assert command(root, *args, "--expect-rebind", planned["rebind_sha256"]).returncode == 2
    state = revision(root, expected)
    prompt = root / ".overseer/local/accepted.txt"
    prompt.write_text("Accepted fixture review only.\n")
    result = command(root, "next-write", "--repo-id", expected["repo"]["id"],
                     "--branch", state.branch, "--vcs", "muse", "--base-head", state.head,
                     "--lane", expected["context"]["lane"], "--model", expected["context"]["model"],
                     "--action-id", "C2-FIXTURE", "--action-kind", "review",
                     "--prompt-file", ".overseer/local/accepted.txt", "--expect-next", "absent")
    assert result.returncode == 0, result.stderr
    fresh = subprocess.run([str(root / ".overseer/bin/ok"), "-C", str(root), "next"],
                           cwd="/", capture_output=True, text=True, timeout=60)
    assert fresh.returncode == 0 and "Accepted fixture review only." in fresh.stdout, fresh.stderr
    status = command(root, "status", "--check-footprint", "--json")
    assert status.returncode == 0, status.stderr
    report = json.loads(status.stdout)
    assert report["footprint_integrity"]["ok"] and report["footprint_coverage"]["ok"]


@pytest.mark.parametrize("change", ["missing_digest", "wrong_digest", "config", "history", "policy",
                                  "head", "branch", "identity", "store", "launcher", "tracked_choice"])
def test_rebind_drift_and_unaccepted_plans_refuse_without_writes(stale_binding, muse_python, muse, change):
    root = stale_binding
    policy = root / ".overseer/policy/rebind-owner.yaml"
    policy.parent.mkdir(exist_ok=True)
    policy.write_text("owner: preserved\n")
    args = arguments(root, muse_python)
    planned = preview(root, args)
    suffix = ["--expect-rebind", planned["rebind_sha256"]]
    if change == "missing_digest":
        suffix = []
    elif change == "wrong_digest":
        suffix[-1] = "0" * 64
    elif change == "config":
        with (root / v1.CONFIG).open("ab") as stream:
            stream.write(b"# concurrent owner edit\n")
    elif change == "history":
        with (root / "docs/FIXTURE-HANDOVER.md").open("ab") as stream:
            stream.write(b"\nnew history\n")
    elif change == "policy":
        policy.write_text("owner: changed\n")
    elif change == "head":
        (root / "app.py").write_text("value = 2\n")
        muse(root, "code", "add", "app.py")
        muse(root, "commit", "-m", "fixture moved", "--json")
    elif change == "branch":
        muse(root, "checkout", "-b", "other", "--json")
    elif change in ("identity", "store"):
        config = yaml.safe_load((root / v1.CONFIG).read_bytes())
        config["vcs"]["muse"]["binding"]["repo_id" if change == "identity" else "store"] = (
            "sha256:" + "b" * 64 if change == "identity" else str(root.parent))
        (root / v1.CONFIG).write_bytes(v1.encode(config))
        args[args.index("--expect-config") + 1] = digest((root / v1.CONFIG).read_bytes())
    elif change == "launcher":
        with (root / ".overseer/bin/ok").open("ab") as stream:
            stream.write(b"# owner custom launcher\n")
    elif change == "tracked_choice":
        at = args.index("--tracked-bindings")
        del args[at:at + 2]
    before = snapshot(root)
    before_controls = controls(root)
    result = command(root, *args, *suffix)
    assert result.returncode == 2, result.stdout + result.stderr
    assert snapshot(root) == before and controls(root) == before_controls


def test_rebind_existing_next_stays_byte_exact(stale_binding, muse_python):
    root = stale_binding
    # Rebinding does not bless or rewrite even an obsolete handoff.
    saved = b"Historical NEXT bytes requiring a separate accepted publication.\n"
    (root / v1.NEXT).write_bytes(saved)
    args = arguments(root, muse_python)
    planned = preview(root, args)
    result = command(root, *args, "--expect-rebind", planned["rebind_sha256"])
    assert result.returncode == 0, result.stderr
    assert (root / v1.NEXT).read_bytes() == saved


def test_rebind_rechecks_owner_edits_under_lock(stale_binding, muse_python, monkeypatch):
    from cli import product_authority, product_migration
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    parsed = v1.parser().parse_args(args + ["--expect-rebind", planned["rebind_sha256"]])
    original_apply = product_migration.apply_mapping
    before = None

    def concurrent_edit(*pos, **kw):
        nonlocal before
        with (root / "docs/FIXTURE-HANDOVER.md").open("ab") as stream:
            stream.write(b"\nOwner change after all plan inputs were read.\n")
        before = snapshot(root)
        return original_apply(*pos, **kw)

    monkeypatch.setattr(product_migration, "apply_mapping", concurrent_edit)
    with pytest.raises(Refusal, match="rebind_protected_changed"):
        product_authority.rebind_muse_runtime(root, parsed)
    assert snapshot(root) == before


def test_rc11_linked_checkout_uses_restored_footprint_contract(tmp_path, muse_python):
    # Reuse the newer contract: the root-bound launcher's tracked lock changes
    # on init and must be reported dirty. The older clean-tree assertion in
    # tests/muse/test_handoffs.py predates the restored footprint.
    from tests.fpr4.test_native_linked_footprint import (
        test_native_linked_checkout_reports_tracked_footprint_change_and_keeps_identity)
    test_native_linked_checkout_reports_tracked_footprint_change_and_keeps_identity(tmp_path, muse_python)


@pytest.mark.parametrize("change,reason", [
    ("version", "muse_version_unsupported"), ("digest", "muse_source_digest_unsupported")])
def test_native_reader_refuses_unreviewed_runtime(muse_root, muse_python, change, reason):
    # Alter only the check's inputs inside a disposable subprocess; the shared
    # installed venv is never patched or downgraded.
    script = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from cli import v1_muse_reader as reader
if sys.argv[3] == 'version':
    reader.importlib.metadata.version = lambda name: '0.2.1rc999'
else:
    reader.MUSE_RUNTIMES['0.2.1rc11'] = '0' * 64
try:
    reader.run(Path(sys.argv[2]), True)
except Exception as exc:
    print(str(exc))
    raise SystemExit(2)
raise SystemExit('unexpected success')
"""
    before = snapshot(muse_root)
    result = subprocess.run([str(muse_python), "-I", "-B", "-c", script,
                             str(v1.KIT), str(muse_root), change],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 2 and reason in result.stdout, result.stderr
    assert snapshot(muse_root) == before
