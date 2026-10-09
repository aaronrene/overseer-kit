import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from unittest.mock import patch

import pytest
import yaml

from cli import v1
from cli.v1_io import Refusal, digest
from cli.v1_revision import muse_read, revision
from tests.v1.conftest import KIT, command, seed, status
from tests.v1.test_adoption import adoption_args


def init(root, python, *args):
    result = command('-C', root, 'init', '--vcs', 'muse', '--muse-python', python, *args)
    assert result.returncode == 0, result.stderr
    return status(root)


def commit(root, muse, text='first'):
    (root / 'app.py').write_text('value = ' + repr(text) + '\n')
    muse(root, 'code', 'add', '.')
    muse(root, 'commit', '-m', text, '--json')
    return muse(root, 'rev-parse', 'HEAD').stdout.strip()


def publish(root, **overrides):
    cfg = yaml.safe_load((root / v1.CONFIG).read_bytes())
    state = revision(root, cfg)
    (root / '.overseer/local').mkdir(exist_ok=True)
    (root / '.overseer/local/prompt.txt').write_text('Meaningful fixture task.\n')
    values = dict(repo_id=cfg['repo']['id'], branch=state.branch, base_head=state.head,
                  vcs=state.kind, lane=cfg['context']['lane'], model=cfg['context']['model'],
                  action_id='SAME-ACTION', action_kind='implement',
                  expect_next=digest((root / v1.NEXT).read_bytes()), prompt_file='.overseer/local/prompt.txt')
    values.update(overrides)
    return command('-C', root, 'next-write', *[v for k, value in values.items()
        if value is not None for v in ('--'+k.replace('_', '-'), value)])


def inventory(root):
    return {str(p.relative_to(root)): (digest(p.read_bytes()), p.stat().st_mode)
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


def test_muse_only_unborn_commit_freshness_and_offline_readonly(muse_root, muse_python, muse):
    root = muse_root
    initial = init(root, muse_python)
    assert initial['head'] == 'unborn' and initial['vcs'] == 'muse'
    head = commit(root, muse)
    r = command('-C', root, 'next')
    assert r.returncode == 2 and 'next_stale_head' in r.stderr and not r.stdout
    assert publish(root).returncode == 0
    (root / '.muse/.muse-tmp-preserve').write_text('native CLI startup would clean this')
    (root / '.muse/bridge-hooks.toml').write_text('[hooks]\npre_export="touch SHOULD_NOT_RUN"\n')
    # Invalid network endpoints and env overrides must be irrelevant to local reads.
    env = dict(HTTP_PROXY='http://127.0.0.1:1', HTTPS_PROXY='http://127.0.0.1:1',
               MUSE_REPO_ROOT='/wrong', MUSE_WORKTREE='/wrong', PYTHONPATH='/wrong')
    before = inventory(root)
    for cmd in ('status', 'next'):
        r = command('-C', root, cmd, '--json', env=env)
        assert r.returncode == 0, r.stderr
        assert json.loads(r.stdout)['head'] == head
        assert json.loads(r.stdout)['publication'] == 'not_checked_offline'
    assert inventory(root) == before
    assert not (root / 'SHOULD_NOT_RUN').exists()
    assert status(root)['dirty'] is False
    (root / 'app.py').write_text('edited but not committed\n')
    assert status(root)['dirty'] is True
    assert command('-C', root, 'next').returncode == 0


def test_mixed_authority_uses_only_muse_revision(muse_root, muse_python, muse):
    root = muse_root
    subprocess.run(['/usr/bin/git', '-C', str(root), 'init', '-b', 'git-main'], check=True, capture_output=True)
    init(root, muse_python)
    commit(root, muse)
    assert publish(root).returncode == 0
    subprocess.run(['/usr/bin/git', '-C', str(root), '-c', 'user.name=Fixture', '-c',
        'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null',
        'commit', '--allow-empty', '-m', 'unrelated Git revision'], check=True, capture_output=True)
    assert status(root)['branch'] == 'main'
    assert command('-C', root, 'next').returncode == 0
    commit(root, muse, 'second')
    r = command('-C', root, 'next')
    assert r.returncode == 2 and 'stale_head' in r.stderr


def test_native_linked_worktree_own_branch_and_checkout_identity(muse_root, muse_python, muse, tmp_path):
    root = muse_root
    init(root, muse_python)
    commit(root, muse)
    assert publish(root).returncode == 0
    linked = (tmp_path / 'linked').resolve()
    muse(root, 'worktree', 'add', 'linked', 'main', '-b', 'lane-two', '--path', str(linked), '--json')
    original = inventory(root)
    other = init(linked, muse_python, '--lane', 'architecture')
    assert other['branch'] == 'lane-two'
    assert other['source_id'] == status(root)['source_id']
    assert other['repository']['id'] != status(root)['repository']['id']
    assert status(linked)['dirty'] is False
    assert publish(linked).returncode == 0
    assert command('next', cwd=linked, executable=linked/'.overseer/bin/ok').returncode == 0
    assert inventory(root) == original
    # Advance the shared primary branch. The linked lane's ref stays current.
    commit(root, muse, 'primary advanced')
    assert command('-C', linked, 'next').returncode == 0
    assert command('-C', root, 'next').returncode != 0


@pytest.mark.parametrize('field,value', [('lane', 'wrong'), ('model', 'Other'),
    ('repo_id', 'wrong'), ('branch', 'wrong'), ('base_head', 'sha256:'+'0'*64),
    ('vcs', 'git'), ('vcs', None), ('base_head', None)])
def test_muse_writer_rejects_wrong_context_without_writes(muse_root, muse_python, field, value):
    init(muse_root, muse_python)
    before = (muse_root / v1.NEXT).read_bytes()
    r = publish(muse_root, **{field:value})
    assert r.returncode == 2 and not r.stdout
    assert (muse_root / v1.NEXT).read_bytes() == before


@pytest.mark.parametrize('binding', [v1.CONFIG, v1.NEXT, '.overseer/bin/ok'])
def test_copied_muse_bindings_refused(muse_root, muse_python, muse, tmp_path, binding):
    init(muse_root, muse_python)
    other = (tmp_path / 'same-name').resolve()
    other.mkdir()
    muse(other, 'init', '--domain', 'code', '--json')
    init(other, muse_python)
    shutil.copyfile(muse_root/binding, other/binding)
    r = command('next', cwd=other, executable=other/'.overseer/bin/ok')
    assert r.returncode != 0 and not r.stdout


@pytest.mark.parametrize('broken', ['missing_python', 'runtime_pin', 'missing_object', 'malformed_head', 'detached', 'bad_ref', 'wrong_source', 'unregistered_pointer'])
def test_muse_missing_or_malformed_state_refuses(muse_root, muse_python, muse, broken):
    root = muse_root
    init(root, muse_python)
    head = commit(root, muse)
    assert publish(root).returncode == 0
    cfg_path = root / v1.CONFIG
    cfg = yaml.safe_load(cfg_path.read_bytes())
    if broken == 'missing_python':
        cfg['muse']['runtime']['python'] = str(muse_python.parent/'missing-python')
    elif broken == 'runtime_pin':
        cfg['muse']['runtime']['sha256'] = '0'*64
    elif broken == 'wrong_source':
        cfg['muse']['repo_id'] = 'sha256:'+'0'*64
    elif broken == 'missing_object':
        from cli.v1_revision import muse_read
        # Delete only a disposable fixture commit object, retaining its ref.
        matches = [p for p in (root/'.muse/objects').rglob('*') if p.is_file()
                   and (p.parent.name+p.name) == head.split(':')[1]]
        assert len(matches) == 1
        matches[0].unlink()
    elif broken == 'malformed_head':
        (root/'.muse/HEAD').write_text('unparseable')
    elif broken == 'detached':
        (root/'.muse/HEAD').write_text('commit: '+head+'\n')
    elif broken == 'bad_ref':
        (root/'.muse/refs/heads/main').write_text('not-an-oid')
    else:
        store = root.with_name('unregistered-store')
        shutil.move(root/'.muse', store)
        (root/'.muse').write_text('musestore: '+str(store)+'\n')
    cfg_path.write_text(yaml.safe_dump(cfg))
    before = inventory(root)
    for cmd in ('status', 'next'):
        r = command('-C', root, cmd)
        assert r.returncode == 2 and not r.stdout
    assert inventory(root) == before


def test_changed_revision_during_write_refused(muse_root, muse_python):
    root = muse_root
    init(root, muse_python)
    cfg = yaml.safe_load((root/v1.CONFIG).read_bytes())
    state = revision(root, cfg)
    from dataclasses import replace
    args = argparse.Namespace(action_id='STALE', action_kind='implement', vcs='muse', base_head=state.head)
    before = (root/v1.NEXT).read_bytes()
    with patch('cli.v1.revision', side_effect=[state, replace(state, head='sha256:'+'1'*64)]):
        with pytest.raises(Refusal, match='context_changed'):
            v1.write_next(root, cfg, args, 'Task.\n', expected=digest(before))
    assert (root/v1.NEXT).read_bytes() == before


def test_explicit_adoption_preserves_identity_docs_edits_and_rollback(muse_root, muse_python, muse):
    root = muse_root
    subprocess.run(['/usr/bin/git', '-C', str(root), 'init', '-b', 'main'], check=True, capture_output=True)
    assert command('-C', root, 'init', '--vcs', 'git').returncode == 0
    commit(root, muse)
    (root/'app.py').write_text('owner uncommitted edit\n')
    (root/'untracked.txt').write_bytes(b'owner untracked\x00')
    before = inventory(root)
    original = (root/v1.CONFIG).read_bytes()
    state = muse_read(root, str(muse_python))
    args = adoption_args(root, vcs='muse', muse_python=str(muse_python), base_head=state['head'])
    plan = command('-C', root, 'adopt', *args, '--dry-run', '--json')
    assert plan.returncode == 0, plan.stderr
    assert inventory(root) == before
    backup = json.loads(plan.stdout)['backup']
    assert command('-C', root, 'adopt', *args).returncode == 0
    assert (root/backup).read_bytes() == original
    assert yaml.safe_load((root/v1.CONFIG).read_bytes())['repo'] == yaml.safe_load(original)['repo']
    assert command('-C', root, 'next').returncode == 2
    assert publish(root).returncode == 0
    assert status(root)['vcs'] == 'muse'
    # Roll back even when the selected Muse runtime is unavailable.
    cfg = yaml.safe_load((root/v1.CONFIG).read_bytes())
    cfg['muse']['runtime']['python'] = str(muse_python.parent/'missing-python')
    (root/v1.CONFIG).write_text(yaml.safe_dump(cfg))
    args = adoption_args(root, vcs=None, restore_config=backup)
    assert command('-C', root, 'adopt', *args).returncode == 0
    assert (root/v1.CONFIG).read_bytes() == original
    # The Muse NEXT is preserved and therefore rejected until Git next-write.
    assert command('-C', root, 'next').returncode == 2
    assert publish(root).returncode == 0
    assert status(root)['vcs'] == 'git'
    after = inventory(root)
    for path in before:
        if path not in (v1.NEXT, '.gitignore', '.museignore'):
            assert before[path] == after[path], path


def test_tracked_muse_binding_blocks_adoption_and_snapshot_excludes_new_local_files(muse_root, muse_python, muse):
    root = muse_root
    # Existing tracked NEXT requires explicit source cleanup, not an ignore-only promise.
    (root/'docs').mkdir()
    (root/v1.NEXT).write_text('old imported local binding\n')
    commit(root, muse)
    (root/v1.NEXT).unlink()
    r = command('-C', root, 'init', '--vcs', 'muse', '--muse-python', muse_python)
    assert r.returncode == 2 and 'tracked_local_bindings' in r.stderr
    # Explicit fixture cleanup creates a new snapshot; history remains intact.
    muse(root, 'code', 'add', '.')
    muse(root, 'commit', '-m', 'remove tracked local binding', '--json')
    init(root, muse_python)
    (root/'.overseer/local').mkdir()
    (root/'.overseer/local/config-backup.yaml').write_text('local backup fixture\n')
    (root/'.cursor/hooks').mkdir(parents=True)
    (root/'.cursor/hooks/local.sh').write_text('#!/bin/sh\nexit 0\n')
    (root/'templates').mkdir()
    (root/'templates/NEXT.template.md').write_text('portable template\n')
    commit(root, muse, 'safe snapshot')
    files = json.loads(muse(root, 'ls-files', '--json').stdout)['files']
    paths = [item['path'] for item in files]
    assert not any(v1.local_path(p) for p in paths)
    assert 'templates/NEXT.template.md' in paths
    assert 'docs/ROADMAP.md' in paths and 'docs/OVERSEER-HANDOVER.md' in paths


def test_committed_git_baseline_import_isolated_from_owner_edits(tmp_path, muse, muse_python):
    source = seed(tmp_path/'git-source')
    assert command('-C', source, 'init').returncode == 0
    (source/'app.py').write_text('committed = True\n')
    for args in (('add', '.'), ('-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'reviewed baseline')):
        subprocess.run(['/usr/bin/git', '-C', str(source), *args], check=True, capture_output=True)
    (source/'app.py').write_text('owner dirty edit\n')
    (source/'untracked.txt').write_text('owner untracked edit\n')
    before = inventory(source)
    imported = (tmp_path/'isolated-import').resolve()
    imported.mkdir()
    muse(imported, 'bridge', 'git-import', str(source), '--target', str(imported), '--branch', 'main', '--json')
    # Import creates history, not a populated working tree. Materialize only
    # the reviewed imported manifest in this disposable destination.
    manifest = json.loads(muse(imported, 'ls-files', '--json').stdout)['files']
    paths = [item['path'] for item in manifest]
    committed = subprocess.check_output(['/usr/bin/git', '-C', str(source), 'ls-files', '-z']).decode().rstrip('\0').split('\0')
    assert sorted(paths) == sorted(committed)
    muse(imported, 'restore', '--source', 'main', *paths, '--json')
    for path in paths:
        assert (imported/path).read_bytes() == subprocess.check_output(
            ['/usr/bin/git', '-C', str(source), 'show', 'HEAD:'+path])
    assert (imported/'app.py').read_text() == 'committed = True\n'
    assert not (imported/'untracked.txt').exists()
    assert not (imported/v1.CONFIG).exists() and not (imported/v1.NEXT).exists()
    state = init(imported, muse_python)
    assert state['repository']['id'] != yaml.safe_load((source/v1.CONFIG).read_bytes())['repo']['id']
    assert command('-C', imported, 'next').returncode == 0
    assert inventory(source) == before


def test_muse_concurrent_cas_and_foreign_lane_read(muse_root, muse_python):
    root = muse_root
    state = init(root, muse_python)
    (root/'.overseer/local').mkdir()
    for name in ('a', 'b'):
        (root/'.overseer/local'/name).write_text('Concurrent task '+name+'\n')
    args = [str(KIT/'cli/ok'), '-C', str(root), 'next-write', '--repo-id', state['repository']['id'],
            '--branch', state['branch'], '--base-head', state['head'], '--vcs', 'muse',
            '--lane', 'product', '--model', 'GPT-6 Astra', '--action-id', 'RACE',
            '--action-kind', 'implement', '--expect-next', state['next_sha256']]
    workers = [subprocess.Popen(args+['--prompt-file', '.overseer/local/'+name],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE) for name in ('a','b')]
    for proc in workers:
        proc.communicate(timeout=20)
    assert sorted(proc.returncode for proc in workers) == [0, 2]
    assert command('-C', root, 'next', '--lane', 'other').returncode == 2
    assert command('-C', root, 'next', '--vcs', 'git').returncode == 2
    assert command('-C', root, 'next').returncode == 0


def test_legacy_stage_is_not_silently_deleted_by_read(muse_root, muse_python):
    init(muse_root, muse_python)
    stage = muse_root/'.muse/code/stage.json'
    stage.parent.mkdir(exist_ok=True)
    stage.write_bytes(b'\x81legacy stage must survive')
    before = inventory(muse_root)
    assert command('-C', muse_root, 'status').returncode == 2
    assert inventory(muse_root) == before


def test_muse_branch_change_invalidates_next(muse_root, muse_python, muse):
    init(muse_root, muse_python)
    commit(muse_root, muse)
    assert publish(muse_root).returncode == 0
    muse(muse_root, 'checkout', '-b', 'other-branch', '--json')
    r = command('-C', muse_root, 'next')
    assert r.returncode == 2 and 'branch_mismatch' in r.stderr and not r.stdout


def test_adoption_reports_existing_muse_snapshot_binding(muse_root, muse_python, muse):
    root = muse_root
    init(root, muse_python)
    ignores = (root/'.museignore').read_bytes()
    (root/'.museignore').write_text('[global]\npatterns=[]\n')
    muse(root, 'code', 'add', 'docs/NEXT.md')
    muse(root, 'commit', '-m', 'fixture legacy tracked binding', '--json')
    (root/'.museignore').write_bytes(ignores)
    state = muse_read(root, str(muse_python))
    args = adoption_args(root, vcs='muse', muse_python=str(muse_python), base_head=state['head'])
    before = inventory(root)
    r = command('-C', root, 'adopt', *args, '--dry-run', '--json')
    assert r.returncode == 1, r.stderr
    assert json.loads(r.stdout)['tracked_local']['muse'] == ['docs/NEXT.md']
    assert command('-C', root, 'adopt', *args).returncode == 2
    assert inventory(root) == before
