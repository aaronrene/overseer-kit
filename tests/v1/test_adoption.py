"""Git-only migration and protocol refusals require no Muse installation."""
import argparse
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest
import yaml

from cli import v1
from cli.v1_io import Refusal, digest
from cli.v1_policy import muse_ignore
from cli.v1_revision import MUSE_VERSION, muse_read
from tests.v1.conftest import command, seed, status
from tests.v1.test_commands import fingerprint


def adoption_args(root, **changes):
    cfg = yaml.safe_load((root / v1.CONFIG).read_bytes())
    values = dict(vcs='git', expect_config=digest((root / v1.CONFIG).read_bytes()),
                  repo_id=cfg['repo']['id'], branch='main', base_head=v1.head(root),
                  lane=cfg['context']['lane'], model=cfg['context']['model'])
    values.update(changes)
    return [item for key, value in values.items() if value is not None
            for item in ('--' + key.replace('_', '-'), value)]


def test_git_without_muse_and_no_automatic_conversion(repo):
    # A broken Muse marker and poisoned installation variables never cause a
    # configured Git checkout to load Muse or reinterpret its revision.
    (repo / '.muse').mkdir()
    (repo / '.muse/HEAD').write_text('invalid Muse metadata')
    env = dict(PATH='/usr/bin:/bin', MUSE_REPO_ROOT='/missing',
               MUSE_WORKTREE='/missing', MUSE_PYTHON='/missing')
    before = fingerprint(repo)
    for cmd in ('status', 'next'):
        r = command('-C', repo, cmd, env=env)
        assert r.returncode == 0, r.stderr
    assert fingerprint(repo) == before
    assert status(repo)['vcs'] == 'git'
    r = command('-C', repo, 'init', '--vcs', 'muse')
    assert r.returncode == 2 and 'explicit_adopt' in r.stderr


def test_mixed_init_requires_explicit_selection(tmp_path):
    root = seed(tmp_path / 'mixed')
    (root / '.muse').mkdir()
    r = command('-C', root, 'init')
    assert r.returncode == 2 and 'explicit_vcs_selection' in r.stderr
    assert not (root / v1.CONFIG).exists()
    assert command('-C', root, 'init', '--vcs', 'git').returncode == 0


def test_nearest_muse_boundary_cannot_use_parent_git(repo):
    child = repo / 'child'
    (child / '.muse').mkdir(parents=True)
    r = command('next', cwd=child)
    assert r.returncode != 0 and not r.stdout


def test_schema_one_explicit_upgrade_and_exact_config_rollback(repo):
    path = repo / v1.CONFIG
    cfg = yaml.safe_load(path.read_bytes())
    cfg['schema'] = 1
    path.write_text('# preserved comment\n' + yaml.safe_dump(cfg))
    original = path.read_bytes()
    docs = {p: (repo / p).read_bytes() for p in (v1.NEXT, 'docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md')}
    (repo / 'edited.txt').write_bytes(b'Uncommitted owner edit\x00')
    before = fingerprint(repo)
    args = adoption_args(repo)
    r = command('-C', repo, 'adopt', *args, '--dry-run', '--json')
    assert r.returncode == 0, r.stderr
    assert fingerprint(repo) == before
    plan = json.loads(r.stdout)
    r = command('-C', repo, 'adopt', *args)
    assert r.returncode == 0, r.stderr
    assert (repo / plan['backup']).read_bytes() == original
    assert status(repo)['repository']['id'] == cfg['repo']['id']
    assert all((repo / p).read_bytes() == data for p, data in docs.items())
    rollback = adoption_args(repo, vcs=None, restore_config=plan['backup'])
    assert command('-C', repo, 'adopt', *rollback).returncode == 0
    assert path.read_bytes() == original
    assert (repo / 'edited.txt').read_bytes() == b'Uncommitted owner edit\x00'
    assert all((repo / p).read_bytes() == data for p, data in docs.items())
    assert command('-C', repo, 'next').returncode == 0


@pytest.mark.parametrize('change', [dict(expect_config='0'*64), dict(repo_id='foreign'),
    dict(lane='architecture'), dict(model='Other'), dict(branch='wrong'), dict(base_head='0'*40)])
def test_adoption_expected_context_and_cas(repo, change):
    before = fingerprint(repo)
    r = command('-C', repo, 'adopt', *adoption_args(repo, **change))
    assert r.returncode != 0
    assert fingerprint(repo) == before


def test_tracked_local_files_are_reported_without_untracking(repo):
    subprocess.run(['/usr/bin/git', '-C', str(repo), 'add', '-f', v1.NEXT], check=True)
    before = fingerprint(repo)
    r = command('-C', repo, 'adopt', *adoption_args(repo), '--dry-run', '--json')
    assert r.returncode == 1
    assert json.loads(r.stdout)['tracked_local']['git'] == [v1.NEXT]
    assert command('-C', repo, 'adopt', *adoption_args(repo)).returncode == 2
    assert fingerprint(repo) == before
    assert v1.NEXT in v1.git(repo, 'ls-files')


def test_adoption_failure_before_config_keeps_old_binding(repo):
    cfg, original = v1.config_for(repo, argparse.Namespace(bound_id=None))
    args = v1.parser().parse_args(['adopt', *adoption_args(repo)])
    real = v1.atomic
    def fail_config(root, relative, *a, **kw):
        if relative == v1.CONFIG:
            raise OSError('injected before config replacement')
        return real(root, relative, *a, **kw)
    # Force an actual configuration delta.
    cfg['schema'] = 1
    (repo / v1.CONFIG).write_bytes(v1.encode(cfg))
    original = (repo / v1.CONFIG).read_bytes()
    args.expect_config = digest(original)
    with patch('cli.v1.atomic', side_effect=fail_config), pytest.raises(OSError):
        v1.adopt(repo, cfg, original, args)
    assert (repo / v1.CONFIG).read_bytes() == original
    assert command('-C', repo, 'next').returncode == 0


def test_adoption_does_not_overwrite_concurrent_ignore_edit(repo):
    cfg, original = v1.config_for(repo, argparse.Namespace(bound_id=None))
    args = v1.parser().parse_args(['adopt', *adoption_args(repo)])
    real = v1.ignore_assets
    def edit_after_read(root, **kwargs):
        mapping = real(root, **kwargs)
        (root/'.gitignore').write_text('# concurrent owner edit\n')
        return mapping
    with patch('cli.v1.ignore_assets', side_effect=edit_after_read):
        with pytest.raises(Refusal, match='stale_write'):
            v1.adopt(repo, cfg, original, args)
    assert (repo/'.gitignore').read_text() == '# concurrent owner edit\n'
    assert (repo/v1.CONFIG).read_bytes() == original


def test_ignore_policy_preserves_rules_comments_and_templates(repo):
    raw = b'# owner comment\n[global]\npatterns = ["old", "!docs/NEXT.md"]\n[domain.code]\npatterns = ["!docs/NEXT.md", "build/"]\n'
    updated = muse_ignore(raw)
    assert b'# owner comment' in updated and b'"old", "!docs/NEXT.md"' in updated
    assert muse_ignore(updated) == updated
    for path in ('templates/NEXT.template.md', 'docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md'):
        assert not v1.local_path(path)


@pytest.mark.parametrize('raw', [b'not valid toml', b'[global]\npatterns = "bad"',
    b'[force_track]\npaths=["docs/NEXT.md"]'])
def test_invalid_or_forced_local_museignore_refuses_without_changes(repo, raw):
    (repo / '.museignore').write_bytes(raw)
    before = fingerprint(repo)
    assert command('-C', repo, 'adopt', *adoption_args(repo)).returncode != 0
    assert fingerprint(repo) == before


@pytest.mark.parametrize('payload', [b'', b'not json', b'{}', b'[]',
    b'{"root":"a","root":"b"}', b'x' * (2*1024*1024+1)])
def test_bad_muse_response_has_no_git_fallback(tmp_path, payload):
    venv = tmp_path / '.venv'
    (venv / 'bin').mkdir(parents=True)
    (venv / 'pyvenv.cfg').write_text('fixture')
    with patch('cli.v1_revision.bounded_run', return_value=subprocess.CompletedProcess([], 0, payload, b'')):
        with pytest.raises(Refusal, match='muse_'):
            muse_read(tmp_path, str(venv / 'bin/python'))


@pytest.mark.parametrize('failure', [FileNotFoundError(), subprocess.TimeoutExpired('muse reader', 15)])
def test_missing_and_timeout_muse_never_fall_back(tmp_path, failure):
    venv = tmp_path / '.venv'
    (venv / 'bin').mkdir(parents=True)
    (venv / 'pyvenv.cfg').write_text('fixture')
    with patch('cli.v1_revision.bounded_run', side_effect=failure):
        with pytest.raises(type(failure)):
            muse_read(tmp_path, str(venv / 'bin/python'))


@pytest.mark.parametrize('code,timeout,reason', [
    ('import time; time.sleep(30)', 0.1, 'timeout'),
    ('import os; os.write(1, b"x" * 3000000)', 5, 'too_large')])
def test_reader_process_output_and_time_are_bounded(tmp_path, code, timeout, reason):
    import sys
    from cli.v1_revision import bounded_run
    with pytest.raises(Refusal, match=reason):
        bounded_run([sys.executable, '-I', '-c', code], cwd=tmp_path, env={}, timeout=timeout)


def test_fresh_standalone_git_install_without_muse(tmp_path):
    import shutil
    import venv
    from tests.v1.conftest import KIT
    installation = tmp_path/'standalone-kit'
    for relative in v1.RUNTIME_FILES:
        target = installation/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(KIT/relative, target)
    venv.EnvBuilder(with_pip=False, symlinks=True).create(installation/'.venv')
    python = installation/'.venv/bin/python3'
    site = Path(subprocess.check_output([str(python), '-I', '-c',
        'import sysconfig; print(sysconfig.get_paths()["purelib"])'], text=True).strip())
    # Seed only the pinned runtime dependency offline; no editable finder or
    # site packages from the development environment are inherited.
    shutil.copytree(Path(yaml.__file__).parent, site/'yaml')
    r = subprocess.run([str(python), '-I', '-c',
        'import importlib.util; assert importlib.util.find_spec("muse") is None'], capture_output=True)
    assert r.returncode == 0
    root = seed(tmp_path/'standalone-project')
    launcher = installation/'cli/ok'
    for args in (('init',), ('status',), ('next',), ('sync',)):
        r = command('-C', root, *args, executable=launcher, env={'PATH':'/usr/bin:/bin'})
        assert r.returncode == 0, r.stderr
    assert yaml.safe_load((root/v1.CONFIG).read_bytes())['vcs'] == 'git'
