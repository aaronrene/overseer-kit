"""Fresh full-footprint init retains consumer assets without adopting bindings."""
import json
import stat

import pytest
import yaml

from cli import product_migration, v1
from cli.main import _arguments
from cli.v1_io import Refusal, digest
from tests.v1.conftest import KIT, command, seed


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


@pytest.mark.parametrize('relative,mode', [
    ('.claude/skills/print-next/SKILL.md', 0o755),
    ('.cursor/skills/print-next/SKILL.md', 0o600),
    ('.cursor/rules/orchestrator.mdc', 0o640),
    ('.overseer/policy/model-routing.yaml', 0o600),
    ('policy/model-routing.yaml', 0o755),
    ('.overseer/STANDING-DECISIONS.reference.md', 0o640),
])
def test_fresh_init_preserves_existing_portable_asset_and_owned_mode(tmp_path, relative, mode):
    root = seed(tmp_path/"consumer with 'quote'")
    target = root/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    body = (b'# Consumer-owned policy\n' + (KIT/'policy/model-routing.yaml').read_bytes()
            if relative.endswith('.yaml') else b'Consumer-owned instructions.\n')
    target.write_bytes(body)
    target.chmod(mode)
    (root/'AGENTS.md').write_text('Consumer Codex instructions.\n')
    (root/'ledger.jsonl').write_text('{"owner":"retained"}\n')
    before = snapshot(root)
    preview = command('-C', root, 'init', '--hooks', '--dry-run', '--json')
    assert preview.returncode == 0, preview.stdout + preview.stderr
    assert relative not in json.loads(preview.stdout)['changed']
    assert snapshot(root) == before
    initialized = command('-C', root, 'init', '--hooks', '--json')
    assert initialized.returncode == 0, initialized.stdout + initialized.stderr
    original = before[relative]
    assert snapshot(root)[relative] == original
    lock = yaml.safe_load((root/'.overseer/version.lock').read_bytes())
    row = next(item for item in lock['footprint'] if item['path'] == relative)
    assert row['origin'] == 'preserved'
    assert row['sha256'].removeprefix('sha256:') == digest(body)
    canonical = (root/v1.NEXT).read_bytes()
    for operation in ('init', 'sync'):
        result = command('-C', root, operation, '--hooks', '--json')
        assert result.returncode == 0, result.stdout + result.stderr
        assert snapshot(root)[relative] == original
        assert (root/v1.NEXT).read_bytes() == canonical
    for path in ('AGENTS.md', 'ledger.jsonl'):
        assert snapshot(root)[path] == before[path]
    assert command('-C', root, 'next').returncode == 0


@pytest.mark.parametrize('relative', [
    '.overseer/bin/ok', '.cursor/hooks/session-start-next.sh',
    '.cursor/hooks.json', '.overseer/instructions/bookends.md',
])
def test_fresh_init_still_refuses_unmanaged_operational_binding(tmp_path, relative):
    root = seed(tmp_path/'strict-binding')
    target = root/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b'Existing unmanaged operational binding.\n')
    target.chmod(0o755)
    before = snapshot(root)
    result = command('-C', root, 'init', '--hooks')
    assert result.returncode == 2 and 'init_asset_exists' in result.stderr
    assert snapshot(root) == before
    assert not (root/v1.CONFIG).exists()


@pytest.mark.parametrize('boundary', ['after_lock', 'before_replace'])
@pytest.mark.parametrize('mutation', ['bytes', 'mode'])
def test_preserved_asset_changes_refuse_after_lock_and_before_replace(tmp_path, monkeypatch, boundary, mutation):
    root = seed(tmp_path/'preserved-race')
    target = root/'.claude/skills/print-next/SKILL.md'
    target.parent.mkdir(parents=True)
    target.write_bytes(b'Original owner instructions.\n')
    target.chmod(0o755)
    changed = False

    def mutate():
        nonlocal changed
        if changed:
            return
        changed = True
        if mutation == 'bytes':
            target.write_bytes(b'Concurrent owner instructions.\n')
        else:
            target.chmod(0o600)

    if boundary == 'after_lock':
        original = product_migration.fcntl.flock

        def flock(fd, operation):
            result = original(fd, operation)
            if operation == product_migration.fcntl.LOCK_EX:
                mutate()
            return result

        monkeypatch.setattr(product_migration.fcntl, 'flock', flock)
    else:
        original = product_migration.atomic

        def atomic(*args, **kwargs):
            mutate()
            return original(*args, **kwargs)

        monkeypatch.setattr(product_migration, 'atomic', atomic)
    args = _arguments(['-C', str(root), 'init', '--hooks'])
    with pytest.raises(Refusal, match='init_preserved_asset_changed'):
        v1.initialize(root, args)
    assert changed
    assert not (root/v1.CONFIG).exists()
    assert not (root/'.overseer/version.lock').exists()
    assert not (root/'.overseer/bin/ok').exists()
    assert target.read_bytes() == (b'Concurrent owner instructions.\n' if mutation == 'bytes'
                                   else b'Original owner instructions.\n')
    assert stat.S_IMODE(target.stat().st_mode) == (0o600 if mutation == 'mode' else 0o755)
