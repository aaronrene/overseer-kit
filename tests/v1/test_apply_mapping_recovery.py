"""Recovery-hint behaviour for apply_mapping and the rebind-only caller."""
from __future__ import annotations

import ast
from argparse import Namespace
import fcntl
import time
from pathlib import Path

import pytest

from cli import product_authority, product_migration as migration, v1
from cli.product_authority import REBIND_RECOVERY
from cli.product_migration import DEFAULT_RECOVERY, RECOVERY
from cli.v1_io import Refusal, digest
from tests.integration.test_legacy_migration_compat import snapshot


KIT = Path(__file__).resolve().parents[2]


def _mapping(root, rows):
    mapping = {}
    for path, data in rows:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(b'before-' + path.encode())
        mapping[path] = data
    return mapping


def test_default_partial_message_is_byte_identical(repo, monkeypatch):
    root = repo
    mapping = _mapping(root, [
        ('.overseer/local/r1/a', b'after-a'),
        ('.overseer/local/r1/b', b'after-b'),
    ])
    real = migration.atomic

    def fail(root_arg, path, data, **kwargs):
        if path.endswith('/b'):
            raise OSError('injected')
        return real(root_arg, path, data, **kwargs)

    monkeypatch.setattr(migration, 'atomic', fail)
    with pytest.raises(Refusal) as raised:
        migration.apply_mapping(root, mapping, check_context=lambda: None)
    assert str(raised.value) == (
        'partial_asset_update: .overseer/local/r1/a; OSError; config is last; ' + DEFAULT_RECOVERY)


def test_supplied_hint_leads_the_partial_message(repo, monkeypatch):
    root = repo
    mapping = _mapping(root, [
        ('.overseer/local/r1/a', b'after-a'),
        ('.overseer/local/r1/b', b'after-b'),
    ])
    real = migration.atomic

    def fail(root_arg, path, data, **kwargs):
        if path.endswith('/b'):
            raise OSError('injected')
        return real(root_arg, path, data, **kwargs)

    monkeypatch.setattr(migration, 'atomic', fail)
    hint = 'restore x from y, then preview again'
    with pytest.raises(Refusal) as raised:
        migration.apply_mapping(root, mapping, check_context=lambda: None, recovery=hint)
    assert str(raised.value) == (
        'partial_asset_update: restore x from y, then preview again; reason: OSError; '
        'completed: .overseer/local/r1/a')


@pytest.mark.parametrize('dry_run', [False, True])
@pytest.mark.parametrize('hint', [
    '', 'a' * 257, 'x;y', 'x\ny', 'x\r', '\x1b[31m', 'é', b'x', 7,
])
def test_invalid_hint_refuses_before_any_work(repo, monkeypatch, dry_run, hint):
    root = repo
    mapping = _mapping(root, [('.overseer/local/r1/a', b'after-a')])
    before = snapshot(root)

    def boom(*args, **kwargs):
        raise AssertionError('work started')

    monkeypatch.setattr(migration, '_updates', boom)
    monkeypatch.setattr(fcntl, 'flock', boom)
    with pytest.raises(Refusal, match=r'^recovery_hint_invalid$'):
        migration.apply_mapping(root, mapping, check_context=lambda: None,
                                dry_run=dry_run, recovery=hint)
    assert snapshot(root) == before


def test_hint_at_limit_is_accepted(repo):
    root = repo
    mapping = _mapping(root, [('.overseer/local/r1/a', b'after-a')])
    hint = 'x' * 256
    assert RECOVERY.fullmatch(hint)
    changed = migration.apply_mapping(root, mapping, check_context=lambda: None, recovery=hint)
    assert changed == ['.overseer/local/r1/a']
    assert (root / '.overseer/local/r1/a').read_bytes() == b'after-a'


def test_no_completed_rows_reraises_original_error(repo, monkeypatch):
    root = repo
    mapping = _mapping(root, [('.overseer/local/r1/a', b'after-a')])
    monkeypatch.setattr(migration, 'atomic', lambda *a, **k: (_ for _ in ()).throw(OSError('injected')))
    with pytest.raises(OSError, match='injected'):
        migration.apply_mapping(root, mapping, check_context=lambda: None)


def test_refusal_reason_is_preserved_with_hint(repo, monkeypatch):
    root = repo
    mapping = _mapping(root, [
        ('.overseer/local/r1/a', b'after-a'),
        ('.overseer/local/r1/b', b'after-b'),
    ])
    calls = {'n': 0}

    def check():
        calls['n'] += 1
        # 1: initial lock check; 2: before_replace for row 1; 3: before_replace for row 2.
        if calls['n'] >= 3:
            raise Refusal('stale_write: x')

    with pytest.raises(Refusal) as raised:
        migration.apply_mapping(root, mapping, check_context=check,
                                recovery='restore x from y, then preview again')
    assert str(raised.value) == (
        'partial_asset_update: restore x from y, then preview again; reason: stale_write: x; '
        'completed: .overseer/local/r1/a')


def test_rebind_recovery_template():
    hint = REBIND_RECOVERY.format(backup='.overseer/local/rebind-' + '0' * 64)
    assert hint == (
        'restore .overseer/bin/ok, .overseer/version.lock, then '
        '.overseer/config.yaml from each copy present in '
        '.overseer/local/rebind-' + '0' * 64 + '/, then preview again')
    assert len(hint) == 211
    assert RECOVERY.fullmatch(hint)


def test_hint_survives_many_completed_paths(repo, monkeypatch):
    root = repo
    rows = [(f'.overseer/local/stress/{i:03d}', f'after-{i}'.encode()) for i in range(500)]
    mapping = _mapping(root, rows)
    real = migration.atomic
    hint = 'restore x from y, then preview again'

    def fail(root_arg, path, data, **kwargs):
        if path.endswith('/499'):
            raise OSError('injected')
        return real(root_arg, path, data, **kwargs)

    monkeypatch.setattr(migration, 'atomic', fail)
    started = time.monotonic()
    with pytest.raises(Refusal) as raised:
        migration.apply_mapping(root, mapping, check_context=lambda: None, recovery=hint)
    message = str(raised.value)
    assert message.startswith('partial_asset_update: ' + hint + '; reason: OSError; completed: ')
    assert hint in message[:300]
    assert time.monotonic() - started < 10


def test_only_rebind_supplies_a_recovery_hint():
    calls = []
    for path in sorted((KIT / 'cli').glob('*.py')):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name != 'apply_mapping':
                continue
            keywords = {kw.arg for kw in node.keywords if kw.arg}
            # Find enclosing function for rebind check
            calls.append((path.name, keywords))
    assert len(calls) == 5
    with_recovery = [c for c in calls if 'recovery' in c[1]]
    assert len(with_recovery) == 1
    # Confirm it is inside rebind_muse_runtime
    source = (KIT / 'cli/product_authority.py').read_text()
    tree = ast.parse(source)
    found = False
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'rebind_muse_runtime':
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    name = func.id if isinstance(func, ast.Name) else getattr(func, 'attr', None)
                    if name == 'apply_mapping':
                        assert any(kw.arg == 'recovery' for kw in child.keywords)
                        found = True
    assert found


def test_sync_partial_message_unchanged(tmp_path, monkeypatch):
    root = tmp_path / 'sync'
    root.mkdir()
    import subprocess
    subprocess.run(['/usr/bin/git', 'init', '-b', 'main', str(root)], check=True, capture_output=True)
    from tests.v1.conftest import command
    assert command('-C', root, 'init').returncode == 0
    original = (root / migration.CONFIG).read_bytes()
    from cli.product_config import normalize
    config = normalize(original, root=root, runtime=v1.runtime()).data
    args = Namespace(hooks=True, only=None, preserve_modified=False, diff=False, dry_run=False)
    dry = migration.sync(root, config, original, Namespace(
        hooks=True, only=None, preserve_modified=False, diff=False, dry_run=True))
    changed = dry['changed']
    before = snapshot(root)
    actual = migration.atomic

    def fail_second(root_arg, path, data, **kwargs):
        if path.endswith('session-end-closeout.sh'):
            raise OSError('injected')
        return actual(root_arg, path, data, **kwargs)

    monkeypatch.setattr(migration, 'atomic', fail_second)
    with pytest.raises(Refusal) as raised:
        migration.sync(root, config, original, args)
    after = snapshot(root)
    completed = ','.join(p for p in changed if after.get(p) != before.get(p))
    assert str(raised.value) == (
        'partial_asset_update: ' + completed + '; OSError; config is last; ' + DEFAULT_RECOVERY)
