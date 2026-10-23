"""Unit and security coverage for the portable Muse CI probe."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

import pytest

from cli.v1_revision import MUSE_RUNTIMES
from tools.ci import supported_v1


def _fake_python(tmp_path, script, *, mode=0o755, name='python'):
    root = tmp_path / 'venv'
    bindir = root / 'bin'
    bindir.mkdir(parents=True)
    (root / 'pyvenv.cfg').write_text('home = /usr\n')
    path = bindir / name
    path.write_text('#!/bin/sh\n' + script)
    path.chmod(mode)
    return path


def _emit(version, sha256):
    payload = json.dumps({'version': version, 'sha256': sha256})
    return f"printf '%s\\n' '{payload}'\n"


def test_allowlist_is_the_three_reviewed_pairs():
    assert MUSE_RUNTIMES['0.2.1rc5'] == '7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92'
    assert MUSE_RUNTIMES['0.2.1rc11'] == 'c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe'
    assert MUSE_RUNTIMES['0.2.1rc13'] == '8b6667bd475355a955563ddeb1b98444c671cd13f73a1decba6ce227039709ba'
    assert set(MUSE_RUNTIMES) == {'0.2.1rc5', '0.2.1rc11', '0.2.1rc13'}
    from cli.v1_revision import MUSE_VERSION
    assert MUSE_VERSION == '0.2.1rc5'


@pytest.mark.parametrize('version,sha256', list(MUSE_RUNTIMES.items()))
def test_probe_accepts_each_exact_reviewed_pair(tmp_path, version, sha256):
    python = _fake_python(tmp_path, _emit(version, sha256))
    assert supported_v1.muse_runtime(python) == (version, sha256)


@pytest.mark.parametrize('version', ['0.2.1rc999', '0.2.1rc12', '0.2.1rc14'])
def test_probe_refuses_unreviewed_version(tmp_path, version):
    python = _fake_python(tmp_path, _emit(version, 'a' * 64))
    with pytest.raises(ValueError, match=r'^muse_version_unreviewed: ' + version.replace('.', r'\.') + r'$'):
        supported_v1.muse_runtime(python)


@pytest.mark.parametrize('version,sha256', [
    ('0.2.1rc11', MUSE_RUNTIMES['0.2.1rc5']),
    ('0.2.1rc5', MUSE_RUNTIMES['0.2.1rc11']),
    ('0.2.1rc13', MUSE_RUNTIMES['0.2.1rc5']),
    ('0.2.1rc13', MUSE_RUNTIMES['0.2.1rc11']),
    ('0.2.1rc5', MUSE_RUNTIMES['0.2.1rc13']),
    ('0.2.1rc11', MUSE_RUNTIMES['0.2.1rc13']),
])
def test_probe_refuses_cross_paired_digest(tmp_path, version, sha256):
    python = _fake_python(tmp_path, _emit(version, sha256))
    with pytest.raises(ValueError, match=r'^muse_source_digest_unreviewed: ' + version + r'$'):
        supported_v1.muse_runtime(python)


@pytest.mark.parametrize('body', [
    '',
    "printf 'a\\nb\\n'\n",
    "printf 'not-json'\n",
    "printf '[]\\n'\n",
    "printf '%s' '{\"version\":\"0.2.1rc5\",\"sha256\":\"" + MUSE_RUNTIMES['0.2.1rc5'] + "\"}'\n",  # no newline
    "printf '%s\\n' '{\"version\":\"0.2.1rc5\",\"sha256\":\"" + MUSE_RUNTIMES['0.2.1rc5'] +
    "\",\"extra\":1}'\n",
    "printf '%s\\n' '{\"version\":\"0.2.1rc5\"}'\n",
    "printf '%s\\n' '{\"version\":\"0.2.1rc5\",\"sha256\":\"" + MUSE_RUNTIMES['0.2.1rc5'].upper() + "\"}'\n",
    "printf '%s\\n' '{\"version\":\"0.2.1rc5\",\"sha256\":\"" + 'a' * 63 + "\"}'\n",
    "printf '%s\\n' '{\"version\":1,\"sha256\":\"" + 'a' * 64 + "\"}'\n",
    "printf '%s\\n' '{\"version\":\"0.2.1 rc5\",\"sha256\":\"" + 'a' * 64 + "\"}'\n",
    "printf '\\xc3\\xa9\\n'\n",
])
def test_probe_refuses_malformed_output(tmp_path, body):
    python = _fake_python(tmp_path, body)
    with pytest.raises(ValueError, match=r'^muse_probe_output_invalid$'):
        supported_v1.muse_runtime(python)


@pytest.mark.parametrize('case', ['exit1', 'not_exec'])
def test_probe_refuses_failed_interpreter(tmp_path, case):
    if case == 'exit1':
        python = _fake_python(tmp_path, 'exit 1\n')
    else:
        python = _fake_python(tmp_path, _emit('0.2.1rc5', MUSE_RUNTIMES['0.2.1rc5']), mode=0o644)
    with pytest.raises(ValueError, match=r'^muse_probe_failed$'):
        supported_v1.muse_runtime(python)


def test_main_selection_includes_compatibility_tests(monkeypatch, tmp_path):
    captured = {}

    def fake_call(command, cwd=None):
        captured['command'] = list(command)
        return 0

    monkeypatch.setattr(supported_v1.subprocess, 'call', fake_call)
    monkeypatch.setattr(supported_v1.tempfile, 'mkdtemp', lambda prefix='': str(tmp_path / 'base'))
    monkeypatch.setattr(supported_v1.sys, 'prefix', str(supported_v1.KIT / '.venv'))
    monkeypatch.setattr(supported_v1.sys, 'executable', str(supported_v1.KIT / '.venv/bin/python'))
    monkeypatch.setattr(sys, 'argv', ['supported_v1.py', '--junitxml', str(tmp_path / 'out.xml')])
    assert supported_v1.main() == 0
    command = captured['command']
    retained = json.loads(
        (supported_v1.KIT / 'docs/validation/fpr3/retained-selection.json').read_text())
    base = [supported_v1.sys.executable, '-m', 'pytest', '-q',
            'tests/v1', 'tests/fpr1', 'tests/fpr2', 'tests/fpr3']
    assert command[:len(base)] == base
    assert command[len(base):len(base) + len(retained)] == retained
    assert command[len(base) + len(retained):len(base) + len(retained) + 2] == list(
        supported_v1.COMPATIBILITY_TESTS)
    assert 'tests/muse' not in command


def test_main_refuses_unreviewed_runtime_before_pytest(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(supported_v1.subprocess, 'call', lambda *a, **k: called.append(1) or 0)
    monkeypatch.setattr(supported_v1.sys, 'prefix', str(supported_v1.KIT / '.venv'))
    monkeypatch.setattr(supported_v1.sys, 'executable', str(supported_v1.KIT / '.venv/bin/python'))
    python = _fake_python(tmp_path, _emit('0.2.1rc999', 'a' * 64))
    monkeypatch.setattr(sys, 'argv', [
        'supported_v1.py', '--muse-python', str(python), '--junitxml', str(tmp_path / 'out.xml')])
    with pytest.raises(SystemExit) as raised:
        supported_v1.main()
    assert raised.value.code == 2
    assert called == []


def test_main_refuses_missing_compatibility_test(tmp_path, monkeypatch, capsys):
    kit = tmp_path / 'kit'
    for relative in ('.github/workflows/supported-v1.yml', '.gitignore', '.museignore',
                     'requirements-v1-dev.txt',
                     'tests/integration/test_legacy_migration_compat.py',
                     'docs/validation/fpr3/retained-selection.json'):
        path = kit / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[]' if relative.endswith('.json') else 'x\n')
    (kit / '.venv').mkdir()
    monkeypatch.setattr(supported_v1, 'KIT', kit)
    monkeypatch.setattr(supported_v1.sys, 'prefix', str(kit / '.venv'))
    monkeypatch.setattr(sys, 'argv', ['supported_v1.py', '--junitxml', str(tmp_path / 'out.xml')])
    with pytest.raises(SystemExit) as raised:
        supported_v1.main()
    assert raised.value.code == 2
    assert 'source file missing: tests/integration/test_historical_prompt_migration.py' in (
        capsys.readouterr().err)


def test_ci_probe_and_reader_share_one_allowlist():
    from cli import v1_revision
    assert supported_v1.MUSE_RUNTIMES is v1_revision.MUSE_RUNTIMES
    assert not hasattr(supported_v1, 'MUSE_SOURCE_SHA256')


def test_probe_output_is_bounded(tmp_path):
    python = _fake_python(tmp_path, 'dd if=/dev/zero bs=1M count=8 2>/dev/null\n')
    started = time.monotonic()
    with pytest.raises(ValueError, match=r'^muse_probe_failed$'):
        supported_v1.muse_runtime(python)
    assert time.monotonic() - started < 5


def test_probe_timeout_is_bounded(tmp_path, monkeypatch):
    pid_file = tmp_path / 'pid'
    python = _fake_python(tmp_path, f'echo $$ > {pid_file}; exec sleep 30\n')
    monkeypatch.setattr(supported_v1, 'PROBE_TIMEOUT', 1)
    started = time.monotonic()
    with pytest.raises(ValueError, match=r'^muse_probe_failed$'):
        supported_v1.muse_runtime(python)
    assert time.monotonic() - started < 5
    pid = int(pid_file.read_text().strip())
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_probe_runs_interpreter_without_shell(tmp_path, monkeypatch):
    parent = tmp_path / 'a b $(touch PWNED)'
    parent.mkdir()
    version, sha256 = next(iter(MUSE_RUNTIMES.items()))
    python = _fake_python(parent, _emit(version, sha256))
    calls = []
    real = supported_v1.subprocess.Popen

    def spy(argv, **kwargs):
        calls.append((argv, kwargs))
        return real(argv, **kwargs)

    # bounded_run uses subprocess.Popen from cli.v1_revision
    import cli.v1_revision as revision
    monkeypatch.setattr(revision.subprocess, 'Popen', spy)
    assert supported_v1.muse_runtime(python) == (version, sha256)
    assert len(calls) == 1
    argv, kwargs = calls[0]
    assert isinstance(argv, list)
    assert argv[0] == str(python)
    assert argv[1:] == ['-I', '-B', '-c', supported_v1.PROBE]
    assert 'shell' not in kwargs


def test_probe_environment_excludes_python_and_muse_variables(tmp_path, monkeypatch):
    version, sha256 = next(iter(MUSE_RUNTIMES.items()))
    script = f'''
if [ -n "$PYTHONPATH" ] || [ -n "$MUSE_FIXTURE" ]; then
  echo bad
  exit 1
fi
{_emit(version, sha256)}
'''
    python = _fake_python(tmp_path, script)
    monkeypatch.setenv('PYTHONPATH', '/nonexistent')
    monkeypatch.setenv('MUSE_FIXTURE', '1')
    assert supported_v1.muse_runtime(python) == (version, sha256)
