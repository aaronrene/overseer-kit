"""Muse end-to-end and rebind coverage for single-lane NEXT model recommendation.

Tier 3 (end-to-end) plus the Muse regression named in freeze section 7. Synthetic
fixtures only; requires --muse-python. Does not read Knowtation or credentials.
"""
from __future__ import annotations

import json
import subprocess

import pytest
import yaml

from cli import v1
from cli.v1_io import digest
from cli.v1_revision import MUSE_RUNTIMES, revision
from cli.version_lock import FootprintEntry, compute_lock_digest
from tests.integration.test_legacy_migration_compat import (
    MANUAL_HOOKS, command as mig_command, legacy_config, seed_legacy)
from tests.muse.test_handoffs import commit, init, publish
from tests.muse.test_legacy_native_binding import MIRROR_VCS, apply, dry, save
from tests.muse.test_runtime_rebind import arguments, preview
from tests.v1.conftest import command

CODEX = 'OpenAI Codex (latest GPT model, high reasoning)'


@pytest.fixture
def native(muse_root, muse):
    """Disposable native Muse+mirror fixture; identical to test_legacy_native_binding."""
    root = muse_root
    seed_legacy(root, config=legacy_config(vcs=MIRROR_VCS), git=False)
    (root / '.cursor/hooks.json').write_bytes(MANUAL_HOOKS)
    for args in (('init', '-b', 'main'), ('config', 'user.name', 'Fixture'),
                 ('config', 'user.email', 'fixture@example.invalid'),
                 ('add', '.overseer/config.yaml', '.cursor/rules/owner-custom.mdc'),
                 ('-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'mirror seed')):
        subprocess.run(['/usr/bin/git', '-C', str(root), *args], check=True, capture_output=True)
    (root / 'app.py').write_text('value = 1\n')
    muse(root, 'code', 'add', 'app.py')
    muse(root, 'commit', '-m', 'native seed', '--json')
    return root


@pytest.fixture
def stale_binding(native, muse_python, rebind_runtimes):
    """Metadata-only stale partner from rebind_runtimes; not a Muse install."""
    current, stale = rebind_runtimes
    document = save(native, dry(native, muse_python, '--tracked-bindings', 'preserve'))
    result = apply(native, document, '--tracked-bindings', 'preserve')
    assert result.returncode == 0, result.stderr
    config = yaml.safe_load((native / v1.CONFIG).read_bytes())
    assert config['vcs']['muse']['binding']['runtime']['version'] == current
    config['vcs']['muse']['binding']['runtime'].update(
        version=stale, sha256=MUSE_RUNTIMES[stale])
    config['runtime'].update(root=str(native.parent / 'obsolete-kit'), sha256='a' * 64)
    old_launcher = v1.launcher(native, config['repo']['id'], runtime_root=config['runtime']['root'])
    (native / '.overseer/bin/ok').write_bytes(old_launcher)
    lock_path = native / '.overseer/version.lock'
    lock = yaml.safe_load(lock_path.read_bytes())
    for row in lock['footprint']:
        if row['path'] == '.overseer/bin/ok':
            row['sha256'] = 'sha256:' + digest(old_launcher)
    lock['footprint_digest'] = compute_lock_digest(
        [FootprintEntry(**row) for row in lock['footprint']])
    lock_path.write_bytes(v1.encode(lock))
    (native / v1.CONFIG).write_bytes(v1.encode(config))
    return native


def test_muse_e2e_publish_codex_then_default(muse_root, muse_python, muse):
    """End-to-end Muse: publish CODEX with explicit vcs/base-head, then default successor."""
    root = muse_root
    init(root, muse_python)
    commit(root, muse, 'seed')
    r = publish(root, model=CODEX)
    assert r.returncode == 0, r.stderr
    shown = command('-C', root, 'next')
    assert shown.returncode == 0, shown.stderr
    assert f'Model: {CODEX}' in shown.stdout
    cfg = yaml.safe_load((root / v1.CONFIG).read_bytes())
    default = cfg['context']['model']
    r2 = publish(root, model=default)
    assert r2.returncode == 0, r2.stderr
    shown2 = command('-C', root, 'next')
    assert shown2.returncode == 0, shown2.stderr
    assert f'Model: {default}' in shown2.stdout


def test_muse_rebind_then_publish_codex(stale_binding, muse_python):
    """End-to-end Muse rebind: apply rebind, publish CODEX, read via bound launcher from cwd=/."""
    root = stale_binding
    args = arguments(root, muse_python)
    planned = preview(root, args)
    result = mig_command(root, *args, '--expect-rebind', planned['rebind_sha256'])
    assert result.returncode == 0, result.stderr
    cfg = yaml.safe_load((root / v1.CONFIG).read_bytes())
    state = revision(root, cfg)
    prompt = root / '.overseer/local/codex.txt'
    prompt.parent.mkdir(exist_ok=True)
    prompt.write_text('Codex after rebind\n')
    written = command(
        '-C', root, 'next-write',
        '--repo-id', cfg['repo']['id'], '--branch', state.branch,
        '--vcs', 'muse', '--base-head', state.head,
        '--lane', cfg['context']['lane'], '--model', CODEX,
        '--action-id', 'CODEX-AFTER-REBIND', '--action-kind', 'review',
        '--prompt-file', '.overseer/local/codex.txt', '--expect-next', 'absent')
    assert written.returncode == 0, written.stderr
    fresh = subprocess.run(
        [str(root / '.overseer/bin/ok'), '-C', str(root), 'next'],
        cwd='/', capture_output=True, text=True, timeout=60)
    assert fresh.returncode == 0, fresh.stderr
    assert f'Model: {CODEX}' in fresh.stdout
    footprint = command('-C', root, 'status', '--check-footprint', '--json')
    assert footprint.returncode == 0, footprint.stderr
    report = json.loads(footprint.stdout)
    assert report['footprint_integrity']['ok'] and report['footprint_coverage']['ok']


def test_muse_codex_requires_explicit_vcs_and_base_head(muse_root, muse_python, muse):
    """Security Muse regression: CODEX without --vcs/--base-head refuses explicitly."""
    root = muse_root
    init(root, muse_python)
    commit(root, muse, 'seed')
    before = (root / v1.NEXT).read_bytes()
    r = publish(root, model=CODEX, vcs=None, base_head=None)
    assert r.returncode == 2 and not r.stdout
    assert 'muse_writer_requires_explicit_vcs_and_base_head' in r.stderr
    assert (root / v1.NEXT).read_bytes() == before
    for field, value in (('lane', 'wrong'), ('repo_id', 'wrong'), ('branch', 'wrong')):
        before = (root / v1.NEXT).read_bytes()
        refused = publish(root, **{field: value})
        assert refused.returncode == 2 and not refused.stdout
        assert (root / v1.NEXT).read_bytes() == before
