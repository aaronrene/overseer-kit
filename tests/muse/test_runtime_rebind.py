"""Real reviewed Muse reads; the stale binding is a metadata-only fixture naming the other reviewed runtime."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import pytest
import yaml

from cli import product_authority, product_migration, v1
from cli.product_authority import REBIND_RECOVERY
from cli.v1_io import Refusal, digest
from cli.v1_revision import MUSE_RUNTIMES, muse_read, revision
from cli.version_lock import FootprintEntry, compute_lock_digest
from tests.integration.test_legacy_migration_compat import command, snapshot
from tests.muse.test_legacy_native_binding import native, dry, save, apply, controls


CONFIG = v1.CONFIG
LAUNCHER = '.overseer/bin/ok'
LOCK = '.overseer/version.lock'
LIVE = (LAUNCHER, LOCK, CONFIG)


@pytest.fixture
def stale_binding(native, muse_python, rebind_runtimes):
    current, stale = rebind_runtimes
    document = save(native, dry(native, muse_python, "--tracked-bindings", "preserve"))
    result = apply(native, document, "--tracked-bindings", "preserve")
    assert result.returncode == 0, result.stderr
    config = yaml.safe_load((native / v1.CONFIG).read_bytes())
    assert config["vcs"]["muse"]["binding"]["runtime"]["version"] == current
    config["vcs"]["muse"]["binding"]["runtime"].update(
        version=stale, sha256=MUSE_RUNTIMES[stale])
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


def expected_config(root, muse_python):
    config = yaml.safe_load((root / v1.CONFIG).read_bytes())
    expected = deepcopy(config)
    expected["runtime"] = v1.runtime()
    expected["vcs"]["muse"]["binding"]["runtime"] = muse_read(root, str(muse_python))["runtime"]
    return expected


def follow_hint(root, backup, planned):
    modes = {row['path']: row['before']['mode'] for row in planned['plan']['assets']}
    for live in LIVE:
        src = root / backup / live
        if src.is_file():
            shutil.copyfile(src, root / live)
            if live in modes and modes[live] is not None:
                (root / live).chmod(modes[live])


def inject_fail(monkeypatch, fail_path, *, after=False):
    real = product_migration.atomic

    def wrapper(root, path, data, **kwargs):
        if path == fail_path:
            if after:
                real(root, path, data, **kwargs)
            raise OSError('injected')
        return real(root, path, data, **kwargs)

    monkeypatch.setattr(product_migration, 'atomic', wrapper)


def parse_apply(root, args, rebind_sha256):
    return v1.parser().parse_args(args + ["--expect-rebind", rebind_sha256])


def test_real_rebind_preserves_settings_source_history_and_publishes_separately(
        stale_binding, muse_python, rebind_runtimes):
    current, stale = rebind_runtimes
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
    assert plan["before_binding"]["runtime"]["version"] == stale
    assert plan["after_binding"]["runtime"]["version"] == current
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
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    parsed = parse_apply(root, args, planned["rebind_sha256"])
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


def test_linked_checkout_uses_restored_footprint_contract(tmp_path, muse_python):
    # Reuse the newer contract: the root-bound launcher's tracked lock changes
    # on init and must be reported dirty. The older clean-tree assertion in
    # tests/muse/test_handoffs.py predates the restored footprint.
    from tests.fpr4.test_native_linked_footprint import (
        test_native_linked_checkout_reports_tracked_footprint_change_and_keeps_identity)
    test_native_linked_checkout_reports_tracked_footprint_change_and_keeps_identity(tmp_path, muse_python)


@pytest.mark.parametrize("change,reason", [
    ("version", "muse_version_unsupported"), ("digest", "muse_source_digest_unsupported")])
def test_native_reader_refuses_unreviewed_runtime(muse_root, muse_python, muse_runtime, change, reason):
    # Alter only the check's inputs inside a disposable subprocess; the shared
    # installed venv is never patched or downgraded.
    assert '0.2.1rc999' not in MUSE_RUNTIMES
    script = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from cli import v1_muse_reader as reader
if sys.argv[3] == 'version':
    reader.importlib.metadata.version = lambda name: '0.2.1rc999'
else:
    reader.MUSE_RUNTIMES[sys.argv[4]] = '0' * 64
try:
    reader.run(Path(sys.argv[2]), True)
except Exception as exc:
    print(str(exc))
    raise SystemExit(2)
raise SystemExit('unexpected success')
"""
    before = snapshot(muse_root)
    result = subprocess.run([str(muse_python), "-I", "-B", "-c", script,
                             str(v1.KIT), str(muse_root), change, muse_runtime.version],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 2 and reason in result.stdout, result.stderr
    assert snapshot(muse_root) == before


_INTERRUPT = {
    'before_backup_launcher': {
        'fail': None,  # filled from backup
        'kind': 'backup_launcher',
        'completed': lambda b: [b + '/' + CONFIG],
        'live': (),
        'mismatch': False,
    },
    'before_backup_lock': {
        'kind': 'backup_lock',
        'completed': lambda b: [b + '/' + CONFIG, b + '/' + LAUNCHER],
        'live': (),
        'mismatch': False,
    },
    'before_launcher': {
        'kind': 'launcher',
        'completed': lambda b: [b + '/' + CONFIG, b + '/' + LAUNCHER, b + '/' + LOCK],
        'live': (),
        'mismatch': False,
    },
    'before_lock': {
        'kind': 'lock',
        'completed': lambda b: [b + '/' + CONFIG, b + '/' + LAUNCHER, b + '/' + LOCK, LAUNCHER],
        'live': (LAUNCHER,),
        'mismatch': True,
    },
    'before_config': {
        'kind': 'config',
        'completed': lambda b: [b + '/' + CONFIG, b + '/' + LAUNCHER, b + '/' + LOCK, LAUNCHER, LOCK],
        'live': (LAUNCHER, LOCK),
        'mismatch': True,
    },
    'after_config': {
        'kind': 'after_config',
        'completed': lambda b: [b + '/' + CONFIG, b + '/' + LAUNCHER, b + '/' + LOCK,
                               LAUNCHER, LOCK, CONFIG],
        'live': (LAUNCHER, LOCK, CONFIG),
        'mismatch': False,
    },
}


def _fail_path(kind, backup):
    return {
        'backup_launcher': backup + '/' + LAUNCHER,
        'backup_lock': backup + '/' + LOCK,
        'launcher': LAUNCHER,
        'lock': LOCK,
        'config': CONFIG,
        'after_config': CONFIG,
    }[kind]


@pytest.mark.parametrize('point', list(_INTERRUPT))
def test_interrupted_rebind_reports_backup_restore_and_recovers(
        stale_binding, muse_python, monkeypatch, point):
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    backup = planned['plan']['backup']
    info = _INTERRUPT[point]
    original = {live: (root / live).read_bytes() for live in LIVE}
    original_modes = {live: (root / live).stat().st_mode & 0o7777 for live in LIVE}
    before = snapshot(root)
    before_controls = controls(root)
    inject_fail(monkeypatch, _fail_path(info['kind'], backup), after=point == 'after_config')
    with pytest.raises(Refusal) as raised:
        product_authority.rebind_muse_runtime(root, parse_apply(root, args, planned['rebind_sha256']))
    message = str(raised.value)
    hint = REBIND_RECOVERY.format(backup=backup)
    expected_completed = info['completed'](backup)
    assert message == (
        "partial_asset_update: " + hint + "; reason: OSError; completed: " +
        ",".join(expected_completed))
    assert "rerun explicit sync" not in message
    for live in LIVE:
        if live in info['live']:
            assert (root / live).read_bytes() != original[live]
        else:
            assert (root / live).read_bytes() == original[live]
            assert ((root / live).stat().st_mode & 0o7777) == original_modes[live]
    if info['mismatch']:
        status = subprocess.run([str(root / LAUNCHER), '-C', str(root), 'status', '--json'],
                                cwd='/', capture_output=True, text=True, timeout=60)
        assert status.returncode == 2 and 'runtime_installation_mismatch' in status.stderr
        fresh = command(root, *args, '--dry-run')
        assert fresh.returncode == 2 and 'rebind_custom_launcher_requires_resolution' in fresh.stderr
    follow_hint(root, backup, planned)
    restored = snapshot(root)
    assert {p: v for p, v in restored.items() if not p.startswith(backup + '/')} == {
        p: v for p, v in before.items() if not p.startswith(backup + '/')}
    assert controls(root) == before_controls
    again = preview(root, args)
    expected_changed = {LAUNCHER, LOCK, CONFIG}
    for path in LIVE:
        copy = backup + '/' + path
        if not (root / copy).is_file():
            expected_changed.add(copy)
    assert set(again['changed']) == expected_changed
    result = command(root, *args, '--expect-rebind', again['rebind_sha256'])
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load((root / CONFIG).read_bytes()) == again['plan']['normalized_config']
    for path in LIVE:
        assert (root / backup / path).read_bytes() == original[path]
    assert not (root / v1.NEXT).exists()


def test_interruption_before_first_write_changes_nothing(stale_binding, muse_python, monkeypatch):
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    backup = planned['plan']['backup']
    before = snapshot(root)
    inject_fail(monkeypatch, backup + '/' + CONFIG)
    with pytest.raises(OSError, match='injected'):
        product_authority.rebind_muse_runtime(root, parse_apply(root, args, planned['rebind_sha256']))
    assert snapshot(root) == before


def test_rebind_plan_shape_unchanged(stale_binding, muse_python):
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    assert set(planned['plan']) == {
        'operation', 'repository', 'source_config_sha256', 'context', 'branch', 'head',
        'before_binding', 'after_binding', 'before_runtime', 'after_runtime',
        'normalized_config', 'assets', 'protected', 'tracked_local', 'tracked_binding_choice',
        'next', 'backup'}
    assert preview(root, args) == planned


def test_concurrent_live_edit_is_reported_before_restore(stale_binding, muse_python, monkeypatch):
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    backup = planned['plan']['backup']
    real = product_migration.atomic

    def concurrent(root_arg, path, data, **kwargs):
        result = real(root_arg, path, data, **kwargs)
        if path == LAUNCHER:
            with (root / LOCK).open('ab') as stream:
                stream.write(b'# concurrent\n')
        return result

    monkeypatch.setattr(product_migration, 'atomic', concurrent)
    with pytest.raises(Refusal) as raised:
        product_authority.rebind_muse_runtime(root, parse_apply(root, args, planned['rebind_sha256']))
    message = str(raised.value)
    hint = REBIND_RECOVERY.format(backup=backup)
    completed = [backup + '/' + CONFIG, backup + '/' + LAUNCHER, backup + '/' + LOCK, LAUNCHER]
    assert message == (
        "partial_asset_update: " + hint + "; reason: stale_write: .overseer/version.lock; completed: " +
        ",".join(completed))
    mismatched = []
    for row in planned['plan']['assets']:
        if row['path'] not in LIVE:
            continue
        live = digest((root / row['path']).read_bytes())
        if live != row['before']['sha256'] and live != row['after']:
            mismatched.append(row['path'])
    assert mismatched == [LOCK]
    assert (root / LOCK).read_bytes().endswith(b'# concurrent\n')


def test_partial_rebind_message_has_no_absolute_paths_or_controls(
        stale_binding, muse_python, monkeypatch, tmp_path):
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    backup = planned['plan']['backup']
    inject_fail(monkeypatch, CONFIG)
    with pytest.raises(Refusal) as raised:
        product_authority.rebind_muse_runtime(root, parse_apply(root, args, planned['rebind_sha256']))
    message = str(raised.value)
    assert str(root) not in message
    assert str(tmp_path) not in message
    assert '/Users/' not in message
    assert all(32 <= ord(ch) <= 126 for ch in message)
    assert '\n' not in message and '\r' not in message and '\x1b' not in message
    import re
    assert re.fullmatch(r'\.overseer/local/rebind-[0-9a-f]{64}', backup)


def test_repeated_interruption_converges(stale_binding, muse_python, monkeypatch):
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    backup = planned['plan']['backup']
    before = snapshot(root)
    before_controls = controls(root)
    original = {live: (root / live).read_bytes() for live in LIVE}
    for _ in range(2):
        inject_fail(monkeypatch, CONFIG)
        with pytest.raises(Refusal):
            product_authority.rebind_muse_runtime(
                root, parse_apply(root, args, planned['rebind_sha256']))
        follow_hint(root, backup, planned)
        planned = preview(root, args)
        backup = planned['plan']['backup']
    result = command(root, *args, '--expect-rebind', planned['rebind_sha256'])
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load((root / CONFIG).read_bytes()) == planned['plan']['normalized_config']
    for path in LIVE:
        assert (root / backup / path).read_bytes() == original[path]
    mapping_paths = {backup + '/' + path for path in LIVE} | set(LIVE)
    after = snapshot(root)
    assert {p: v for p, v in after.items() if p not in mapping_paths} == {
        p: v for p, v in before.items() if p not in mapping_paths}
    assert controls(root) == before_controls
    assert not (root / v1.NEXT).exists()


def test_cli_interrupted_rebind_shows_restore_hint_and_recovers(stale_binding, muse_python):
    assert os.geteuid() != 0
    started = time.monotonic()
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    backup = planned['plan']['backup']
    hint = REBIND_RECOVERY.format(backup=backup)
    before = snapshot(root)
    before_controls = controls(root)
    overseer = root / '.overseer'
    try:
        overseer.chmod(0o555)
        result = command(root, *args, '--expect-rebind', planned['rebind_sha256'])
    finally:
        overseer.chmod(0o755)
    assert result.returncode == 2
    completed = ",".join([backup + '/' + CONFIG, backup + '/' + LAUNCHER,
                          backup + '/' + LOCK, LAUNCHER])
    full = "partial_asset_update: " + hint + "; reason: PermissionError; completed: " + completed
    assert result.stderr == "refused: " + full[:300] + "\n"
    assert "rerun explicit sync" not in result.stderr
    status = subprocess.run([str(root / LAUNCHER), '-C', str(root), 'status', '--json'],
                            cwd='/', capture_output=True, text=True, timeout=60)
    assert status.returncode == 2 and 'runtime_installation_mismatch' in status.stderr
    fresh = command(root, *args, '--dry-run')
    assert fresh.returncode == 2 and 'rebind_custom_launcher_requires_resolution' in fresh.stderr
    follow_hint(root, backup, planned)
    restored = snapshot(root)
    assert {p: v for p, v in restored.items() if not p.startswith(backup + '/')} == {
        p: v for p, v in before.items() if not p.startswith(backup + '/')}
    assert controls(root) == before_controls
    again = preview(root, args)
    assert set(again['changed']) == {LAUNCHER, LOCK, CONFIG}
    applied = command(root, *args, '--expect-rebind', again['rebind_sha256'])
    assert applied.returncode == 0, applied.stderr
    assert yaml.safe_load((root / CONFIG).read_bytes()) == again['plan']['normalized_config']
    status = command(root, 'status', '--check-footprint', '--json')
    report = json.loads(status.stdout)
    assert report['footprint_integrity']['ok'] and report['footprint_coverage']['ok'], status.stdout
    assert time.monotonic() - started < 180
