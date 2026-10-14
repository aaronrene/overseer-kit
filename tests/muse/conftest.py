"""Opt-in real Muse matrix: selecting this directory requires a Muse venv."""
import os
from pathlib import Path
import subprocess

import pytest


def pytest_addoption(parser):
    parser.addoption('--muse-python', help='Absolute Python in a separate Muse 0.2.1rc5 venv')


@pytest.fixture(scope='session')
def muse_python(request):
    value = request.config.getoption('--muse-python')
    if not value:
        pytest.fail('Real Muse matrix requires --muse-python; Git-only matrix is tests/v1 + tests/retained')
    path = Path(value)
    assert path.is_absolute() and path.exists()
    probe = subprocess.run([str(path), '-I', '-B', '-c',
        "import hashlib,importlib.metadata,pathlib,muse; "
        "p=pathlib.Path(muse.__file__).resolve().parent; h=hashlib.sha256(); "
        "[h.update(str(f.relative_to(p)).encode()+b'\\0'+f.read_bytes()+b'\\0') for f in sorted(p.rglob('*.py'))]; "
        "print(importlib.metadata.version('muse')); print(h.hexdigest())"],
        capture_output=True, text=True, timeout=15)
    assert probe.returncode == 0, probe.stderr
    assert probe.stdout.splitlines() == ['0.2.1rc5', '7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92']
    return path


@pytest.fixture
def muse(muse_python):
    def run(root, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith(('MUSE_', 'GIT_', 'PYTHON'))}
        env.update(PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_GLOBAL='/dev/null',
                   GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='Fixture',
                   GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_NAME='Fixture',
                   GIT_COMMITTER_EMAIL='fixture@example.invalid')
        result = subprocess.run([str(muse_python.parent / 'muse'), '-C', str(root), *args],
                                env=env, text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
        return result
    return run


@pytest.fixture
def muse_root(tmp_path, muse):
    root = (tmp_path / 'muse-only').resolve()
    root.mkdir()
    muse(root, 'init', '--domain', 'code', '--json')
    return root
