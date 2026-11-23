"""Initialization preserves large living documents without widening control reads.

The paired ROADMAP/HANDOVER existence check is the only initialize read that
uses the existing 16 MiB asset reader. Configuration, NEXT, and the default
control reader stay at 128 KiB. Symlink, non-regular, and hard-link refusals
stay in front of any binding write.
"""
import os
import stat

import pytest

from cli.product_migration import ASSET_LIMIT, read as read_asset
from cli.v1_io import LIMIT, Refusal, read
from tests.v1.conftest import KIT, command, seed

DOCUMENTS = ('docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md')


def unbound(tmp_path):
    """Create a seeded Git repository with no Overseer binding."""
    root = seed(tmp_path / 'consumer')
    (root / 'docs').mkdir()
    return root


def files(root):
    """Capture modes, link counts, and bytes, excluding Git metadata."""
    result = {}
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if '.git' in relative.parts:
            continue
        info = path.lstat()
        if path.is_symlink():
            body = os.readlink(path)
        elif stat.S_ISREG(info.st_mode):
            body = path.read_bytes()
        else:
            body = None
        result[relative.as_posix()] = (info.st_mode, info.st_nlink, body)
    return result


def refused_without_writes(root, reason):
    """Require the exact refusal and no partial binding or other write."""
    before = files(root)
    result = command('-C', root, 'init', '--vcs', 'git')
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr == f'refused: {reason}\n'
    assert result.stdout == ''
    assert files(root) == before
    assert not (root / '.overseer/bin/ok').exists()
    assert not (root / '.overseer/version.lock').exists()
    return result


def test_paired_loop_is_the_only_asset_read():
    """The compatibility alias is confined to the paired-document loop."""
    source = (KIT / 'cli/v1.py').read_text()
    body = source[source.index('def initialize'):source.index('\ndef parser')]
    assert 'from cli.product_migration import read as read_asset' in body
    assert body.count('read_asset(') == 1
    assert 'if read_asset(root, path, missing=True) is None:' in body
    assert 'if read(root, path, missing=True) is None:' not in body
    assert (KIT / 'cli/v1_io.py').read_text().split('LIMIT = ', 1)[1].startswith('128 * 1024')
    policy = (KIT / 'cli/product_migration.py').read_text()
    assert 'ASSET_LIMIT = 16 * 1024 * 1024' in policy
    assert 'limit=LIMIT if relative in (CONFIG, NEXT) else ASSET_LIMIT' in policy


@pytest.mark.parametrize('relative,size', list(zip(DOCUMENTS, (386993, 505458))))
@pytest.mark.parametrize('mode', [0o644, 0o600])
def test_init_preserves_large_document_independently(tmp_path, relative, size, mode):
    """Each living document initializes alone, with its bytes and mode kept."""
    root = unbound(tmp_path)
    path = root / relative
    body = b'# Existing document\n' + b'x' * (size - 20)
    assert len(body) == size
    path.write_bytes(body)
    path.chmod(mode)
    result = command('-C', root, 'init', '--vcs', 'git')
    assert result.returncode == 0, result.stderr
    assert path.read_bytes() == body
    assert stat.S_IMODE(path.stat().st_mode) == mode
    assert command('-C', root, 'next').returncode == 0


@pytest.mark.parametrize('relative', DOCUMENTS)
def test_init_accepts_exact_asset_boundary(tmp_path, relative):
    """A document of exactly 16 MiB remains readable and unchanged."""
    root = unbound(tmp_path)
    path = root / relative
    body = b'x' * ASSET_LIMIT
    path.write_bytes(body)
    path.chmod(0o600)
    result = command('-C', root, 'init', '--vcs', 'git')
    assert result.returncode == 0, result.stderr
    assert path.read_bytes() == body
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


@pytest.mark.parametrize('relative', DOCUMENTS)
def test_init_refuses_over_asset_boundary_before_binding(tmp_path, relative):
    """One byte past the existing asset limit refuses before any binding write."""
    root = unbound(tmp_path)
    (root / relative).write_bytes(b'x' * (ASSET_LIMIT + 1))
    refused_without_writes(root, f'file_invalid: {relative}')


def test_init_creates_both_missing_documents(tmp_path):
    """Missing paired documents are still created with their existing templates."""
    root = unbound(tmp_path)
    result = command('-C', root, 'init', '--vcs', 'git')
    assert result.returncode == 0, result.stderr
    assert (root / DOCUMENTS[0]).read_bytes() == b'# Roadmap\n\nCurrent action: docs/NEXT.md.\n'
    assert (root / DOCUMENTS[1]).read_bytes() == b'# Handover\n\nRead current action with `ok next`.\n'
    assert all(stat.S_IMODE((root / path).stat().st_mode) == 0o644 for path in DOCUMENTS)


def guard_reason(kind, relative):
    """Return the existing refusal for this document shape.

    A symlink at a configured living-document path is rejected by the config
    path guard before the generic symlink refusal. Directories, fifos, and
    hard links remain path_not_regular.
    """
    if kind != 'symlink':
        return 'path_not_regular'
    field = 'roadmap' if relative.endswith('ROADMAP.md') else 'handover'
    return f'config_path_symlink: docs.lanes.product.{field}'


@pytest.mark.parametrize('relative', DOCUMENTS)
@pytest.mark.parametrize('kind', ['symlink', 'directory', 'fifo', 'hardlink'])
def test_init_retains_document_file_guards(tmp_path, relative, kind):
    """Existing symlink, directory, fifo, and hard-link refusals still stop init."""
    reason = guard_reason(kind, relative)
    root = unbound(tmp_path)
    target = root / relative
    donor = root / 'donor'
    donor.write_bytes(b'preserve donor\n')
    if kind == 'symlink':
        target.symlink_to(donor)
    elif kind == 'directory':
        target.mkdir()
    elif kind == 'fifo':
        os.mkfifo(target)
    else:
        os.link(donor, target)
    refused_without_writes(root, reason)


@pytest.mark.parametrize('relative', ('.overseer/config.yaml', 'docs/NEXT.md'))
def test_init_retains_small_control_limits(tmp_path, relative):
    """Configuration and NEXT still refuse one byte past 128 KiB."""
    assert LIMIT == 128 * 1024
    assert ASSET_LIMIT == 16 * 1024 * 1024
    root = unbound(tmp_path)
    path = root / relative
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(b'x' * (LIMIT + 1))
    refused_without_writes(root, f'file_invalid: {relative}')


@pytest.mark.parametrize('relative', ('.overseer/config.yaml', 'docs/NEXT.md', 'unrelated.txt'))
def test_control_and_default_reader_boundaries_remain_exact(tmp_path, relative):
    """The default reader and the config/NEXT exceptions stay at 128 KiB."""
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    body = b'x' * LIMIT
    path.write_bytes(body)
    assert read(tmp_path, relative) == body
    if relative != 'unrelated.txt':
        assert read_asset(tmp_path, relative) == body
    path.write_bytes(body + b'x')
    with pytest.raises(Refusal, match='^file_invalid:'):
        read(tmp_path, relative)
    if relative != 'unrelated.txt':
        with pytest.raises(Refusal, match='^file_invalid:'):
            read_asset(tmp_path, relative)
