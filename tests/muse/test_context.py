"""Native R1/R2 equivalents through the production bootstrap and shared writer."""
import argparse
import io
import os
import sys
import select
import subprocess
import fcntl

import pytest
import yaml
from cli import v1
from cli.v1_io import digest
from tests.v1.conftest import KIT, command
from tests.muse.test_handoffs import init, commit, publish


def change(root, kind, muse):
    if kind == 'branch':
        muse(root, 'checkout', '-b', 'changed', '--json')
    elif kind == 'head':
        commit(root, muse, 'changed')
    else:
        path = root/v1.CONFIG
        cfg = yaml.safe_load(path.read_bytes())
        if kind == 'config':
            cfg['repo']['name'] = 'changed'
        else:
            cfg['runtime']['sha256'] = '0'*64
        path.write_text(yaml.safe_dump(cfg))


@pytest.mark.parametrize('kind', ['branch', 'head', 'config', 'runtime'])
def test_native_writer_after_lock(muse_root, muse_python, muse, kind):
    root = muse_root
    state = init(root, muse_python)
    (root/'.overseer/local').mkdir()
    (root/'.overseer/local/prompt').write_text('Prepared native action.\n')
    args = ['-C', str(root), 'next-write', '--repo-id', state['repository']['id'],
        '--branch', 'main', '--lane', 'product', '--model', 'GPT-6 Astra',
        '--action-id', 'NATIVE-RACE', '--action-kind', 'implement', '--vcs', 'muse',
        '--base-head', state['head'], '--expect-next', state['next_sha256'],
        '--prompt-file', '.overseer/local/prompt']
    script = '''
import fcntl, os, sys
sys.path.insert(0, sys.argv[1])
from cli import bootstrap
real = fcntl.flock
signal = int(sys.argv[2])
def locked(fd, operation):
    try: real(fd, operation | fcntl.LOCK_NB)
    except BlockingIOError:
        os.write(signal, b'1'); os.close(signal)
        return real(fd, operation)
    raise AssertionError('expected held directory lock')
fcntl.flock = locked
sys.argv = ['bootstrap', *sys.argv[3:]]
raise SystemExit(bootstrap.run())
'''
    before = (root/v1.NEXT).read_bytes()
    fd = os.open(root/'docs', os.O_RDONLY | os.O_DIRECTORY)
    rd, wr = os.pipe()
    worker = None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        worker = subprocess.Popen([str(KIT/'.venv/bin/python'), '-I', '-B', '-c', script,
            str(KIT), str(wr), *args], pass_fds=(wr,), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.close(wr)
        assert select.select([rd], [], [], 30)[0]
        assert os.read(rd, 1) == b'1'
        change(root, kind, muse)
        fcntl.flock(fd, fcntl.LOCK_UN)
        out, err = worker.communicate(timeout=30)
        assert worker.returncode == 2 and not out, err
        assert (root/v1.NEXT).read_bytes() == before
    finally:
        os.close(rd); os.close(fd)
        if worker and worker.poll() is None:
            worker.kill(); worker.communicate()


@pytest.mark.parametrize('reader', ['next', 'status', 'hook'])
@pytest.mark.parametrize('kind', ['branch', 'head', 'config', 'runtime'])
def test_native_reader_final_recheck(muse_root, muse_python, muse, monkeypatch, capsys, reader, kind):
    root = muse_root
    state = init(root, muse_python, '--hooks')
    original = v1.validate_next
    changed = False
    def validate(*args, **kwargs):
        nonlocal changed
        result = original(*args, **kwargs)
        if not changed:
            changed = True
            change(root, kind, muse)
        return result
    monkeypatch.setattr(v1, 'validate_next', validate)
    args = ['-C', str(root), reader]
    if reader == 'hook':
        args += ['--bound-root', str(root), '--bound-id', state['repository']['id'],
            '--binding-path', str(root/'.overseer/bin/ok'), '--hook-path', str(root/'.cursor/hooks/session-start-next.sh')]
        monkeypatch.setattr(sys, 'stdin', io.StringIO('{}'))
    assert v1.main(args) == 2
    assert not capsys.readouterr().out


@pytest.mark.parametrize('kind', ['branch', 'head'])
def test_native_writer_after_fsync(muse_root, muse_python, muse, monkeypatch, kind):
    root = muse_root
    init(root, muse_python)
    original = (root/v1.CONFIG).read_bytes()
    config = yaml.safe_load(original)
    context = v1.capture_context(root, original)
    before = (root/v1.NEXT).read_bytes()
    args = argparse.Namespace(action_id='FSYNC', action_kind='implement', vcs='muse', base_head=context['head'])
    real = os.fsync
    changed = False
    def fsync(fd):
        nonlocal changed
        real(fd)
        if not changed:
            changed = True
            change(root, kind, muse)
    monkeypatch.setattr(os, 'fsync', fsync)
    with pytest.raises(v1.Refusal):
        v1.write_next(root, config, args, 'Native task.\n', expected=digest(before), context=context)
    assert (root/v1.NEXT).read_bytes() == before
