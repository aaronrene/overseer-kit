"""Deterministic R1/R2 regressions using only disposable Git repositories."""
import json
import os
import select
import subprocess
import sys

import fcntl
import pytest
import yaml

from cli import v1
from tests.v1.conftest import KIT, command, status, write_action


def git(root, *args):
    return v1.git(root, *args)


def change_context(root, change):
    if change == 'branch':
        git(root, 'switch', '-c', 'changed')
    elif change == 'head':
        git(root, 'commit', '--allow-empty', '-m', 'concurrent work')
    else:
        path = root / v1.CONFIG
        config = yaml.safe_load(path.read_bytes())
        if change == 'config':
            config['repo']['name'] = 'changed repository name'
        else:
            assert change == 'runtime'
            config['runtime']['sha256'] = '0' * 64
        path.write_bytes(v1.encode(config))


@pytest.mark.parametrize('change', ['branch', 'head', 'config', 'runtime'])
def test_writer_rechecks_context_after_real_lock_wait(repo, change):
    state = status(repo)
    path = repo / v1.NEXT
    before = path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_ino
    (repo / 'prompt.txt').write_text('Prepared before the context changed.\n')
    args = ['-C', str(repo), 'next-write', '--repo-id', state['repository']['id'],
            '--branch', state['branch'], '--lane', 'product', '--model', 'GPT-6 Astra',
            '--action-id', 'WAITING-WRITER', '--action-kind', 'implement',
            '--expect-next', state['next_sha256'], '--prompt-file', 'prompt.txt']
    # The wrapper observes a real busy flock, signals the parent, then performs
    # the real blocking call. No sleeps, product hooks or mocked Git outcomes.
    script = '''
import fcntl, os, sys
sys.path.insert(0, sys.argv[1])
from cli import bootstrap
signal_fd = int(sys.argv[2])
real_flock = fcntl.flock
def observed_flock(fd, operation):
    try:
        real_flock(fd, operation | fcntl.LOCK_NB)
    except BlockingIOError:
        os.write(signal_fd, b'waiting')
        os.close(signal_fd)
        return real_flock(fd, operation)
    raise AssertionError('fixture must hold the directory lock')
fcntl.flock = observed_flock
sys.argv = ['bootstrap', *sys.argv[3:]]
raise SystemExit(bootstrap.run())
'''
    lock_fd = os.open(repo / 'docs', os.O_RDONLY | os.O_DIRECTORY)
    signal_read, signal_write = os.pipe()
    worker = None
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        worker = subprocess.Popen(
            [str(KIT / '.venv/bin/python'), '-I', '-B', '-c', script,
             str(KIT), str(signal_write), *args], pass_fds=(signal_write,),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        os.close(signal_write)
        signal_write = None
        assert select.select([signal_read], [], [], 15)[0], 'writer did not reach lock'
        assert os.read(signal_read, 7) == b'waiting'
        assert worker.poll() is None
        change_context(repo, change)
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        stdout, stderr = worker.communicate(timeout=15)
        assert worker.returncode == 2, (stdout, stderr)
        assert not stdout
        assert 'context_changed' in stderr or 'runtime_changed' in stderr
        assert (path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_ino) == before
        assert not list(path.parent.glob('.NEXT.md.*'))
    finally:
        os.close(lock_fd)
        os.close(signal_read)
        if signal_write is not None:
            os.close(signal_write)
        if worker is not None and worker.poll() is None:
            worker.kill()
            worker.communicate(timeout=5)


def closing_commit(root):
    git(root, 'add', v1.NEXT)
    git(root, 'commit', '-m', 'publish NEXT')
    return v1.head(root)


def test_reader_cannot_mix_parent_and_blob_revisions(repo, monkeypatch, capsys):
    h0 = v1.head(repo)
    write_action(repo, 'Candidate A\n')
    candidate_a = (repo / v1.NEXT).read_bytes()
    write_action(repo, 'Candidate B\n')
    candidate_b = (repo / v1.NEXT).read_bytes()
    (repo / v1.NEXT).write_bytes(candidate_a)
    h1 = closing_commit(repo)
    (repo / v1.NEXT).write_bytes(candidate_b)
    before = command('-C', repo, 'next')
    assert before.returncode == 2 and 'next_stale_head' in before.stderr
    real_git = v1.git
    lookups = []

    def advance_after_parent_lookup(root, *args, **kwargs):
        result = real_git(root, *args, **kwargs)
        if args[0] in ('rev-list', 'show'):
            lookups.append(args)
        if args[0] == 'rev-list':
            assert result.split() == [h1, h0]
            real_git(root, 'add', v1.NEXT)
            real_git(root, 'commit', '-m', 'second closing commit')
        return result

    with monkeypatch.context() as patch:
        patch.setattr(v1, 'git', advance_after_parent_lookup)
        code = v1.main(['-C', str(repo), 'next'])
    captured = capsys.readouterr()
    assert code == 2, captured
    assert not captured.out and 'next_stale_head' in captured.err
    assert lookups == [('rev-list', '--parents', '-n', '1', h1),
                       ('show', h1 + ':' + v1.NEXT)]
    after = command('-C', repo, 'next')
    assert after.returncode == 2 and 'next_stale_head' in after.stderr
    assert (repo / v1.NEXT).read_bytes() == candidate_b


@pytest.mark.parametrize('reader', ['next', 'status', 'hook'])
@pytest.mark.parametrize('change', ['branch', 'head', 'config', 'runtime'])
def test_reader_rechecks_context_before_output(repo, monkeypatch, capsys, reader, change):
    state = status(repo)
    closing_commit(repo)
    real_git = v1.git
    changed = False

    def change_after_blob_lookup(root, *args, **kwargs):
        nonlocal changed
        result = real_git(root, *args, **kwargs)
        if args[0] == 'show':
            assert not changed
            changed = True
            change_context(root, change)
        return result

    args = ['-C', str(repo), reader, '--json']
    if reader == 'hook':
        args += ['--bound-root', str(repo), '--bound-id', state['repository']['id'],
                 '--binding-path', str(repo / '.overseer/bin/ok'),
                 '--hook-path', str(repo / '.cursor/hooks/session-start-next.sh')]
        import io
        monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(b'{}')))
    monkeypatch.setattr(v1, 'git', change_after_blob_lookup)
    code = v1.main(args)
    captured = capsys.readouterr()
    assert changed
    assert code == 2, captured
    assert not captured.out
    assert 'context_changed' in captured.err or 'runtime_changed' in captured.err


@pytest.mark.parametrize('change', ['branch', 'head'])
def test_writer_rechecks_context_after_candidate_fsync(repo, monkeypatch, capsys, change):
    state = status(repo)
    path = repo / v1.NEXT
    before = path.read_bytes()
    (repo / 'prompt.txt').write_text('Prepared before fsync.\n')
    real_fsync = os.fsync
    changed = False

    def change_after_fsync(fd):
        nonlocal changed
        real_fsync(fd)
        if not changed:
            changed = True
            change_context(repo, change)

    monkeypatch.setattr(os, 'fsync', change_after_fsync)
    code = v1.main(['-C', str(repo), 'next-write', '--repo-id', state['repository']['id'],
                    '--branch', state['branch'], '--lane', 'product', '--model', 'GPT-6 Astra',
                    '--action-id', 'FSYNC-WRITER', '--action-kind', 'implement',
                    '--expect-next', state['next_sha256'], '--prompt-file', 'prompt.txt'])
    captured = capsys.readouterr()
    assert changed
    assert code == 2 and not captured.out, captured
    assert 'context_changed' in captured.err
    assert path.read_bytes() == before
    assert not list(path.parent.glob('.NEXT.md.*'))


def test_context_checks_keep_successful_reads_read_only(repo):
    closing_commit(repo)

    def snapshot():
        return {str(p.relative_to(repo)): (p.read_bytes(), p.stat().st_mode, p.stat().st_mtime_ns)
                for p in repo.rglob('*') if p.is_file()}

    before = snapshot()
    for reader in ('next', 'status', 'next', 'status'):
        result = command('-C', repo, reader, '--json')
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)['ok']
    assert snapshot() == before  # Includes Git metadata, modes and mtimes.
