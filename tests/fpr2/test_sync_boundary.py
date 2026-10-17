"""A changed Git boundary must not inherit an identical parent branch/revision."""
import os

import yaml

from cli import v1


def test_sync_rechecks_physical_git_boundary_after_fsync(repo, monkeypatch, capsys):
    config_path = repo/v1.CONFIG
    config = yaml.safe_load(config_path.read_bytes())
    config['runtime']['sha256'] = '0'*64
    config_path.write_text(yaml.safe_dump(config))
    before = config_path.read_bytes()
    real = os.fsync
    changed = False
    def fsync(fd):
        nonlocal changed
        real(fd)
        if not changed:
            changed = True
            # Same native Git metadata, same branch and full HEAD, new top-level.
            (repo/'.git').rename(repo.parent/'.git')
    monkeypatch.setattr(os, 'fsync', fsync)
    result = v1.main(['-C', str(repo), 'sync', '--json'])
    assert changed
    assert result == 2, capsys.readouterr()
    assert config_path.read_bytes() == before
