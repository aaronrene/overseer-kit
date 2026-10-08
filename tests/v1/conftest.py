from pathlib import Path
import json
import os
import subprocess

import pytest

KIT = Path(__file__).resolve().parents[2]
OK = KIT / 'cli/ok'


def command(*args, cwd=None, env=None, executable=OK, input=None):
    return subprocess.run([str(executable), *map(str, args)], cwd=cwd or KIT,
                          env=dict(os.environ, **(env or {})), input=input,
                          capture_output=True, text=True, timeout=20)


def seed(path):
    path.mkdir()
    for args in (['init', '-b', 'main'], ['config', 'user.name', 'Fixture'],
                 ['config', 'user.email', 'fixture@example.invalid'],
                 ['-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-m', 'seed']):
        subprocess.run(['/usr/bin/git', '-C', str(path), *args], check=True, capture_output=True)
    return path.resolve()


@pytest.fixture
def repo(tmp_path):
    root = seed(tmp_path / 'similar-kit')
    result = command('-C', root, 'init', '--hooks')
    assert result.returncode == 0, result.stderr
    return root


@pytest.fixture
def pair(repo, tmp_path):
    other = seed(tmp_path / 'similar-kit-copy')
    result = command('-C', other, 'init', '--hooks')
    assert result.returncode == 0, result.stderr
    for root in (repo, other):
        write_action(root, 'Unique content for ' + root.name + '\n')
    return repo, other


def status(root):
    result = command('-C', root, 'status', '--json')
    assert result.returncode == 0, result.stderr + result.stdout
    return json.loads(result.stdout)


def write_action(root, prompt, **overrides):
    state = status(root)
    (root / 'prompt.txt').write_text(prompt)
    values = dict(repo_id=state['repository']['id'], branch='main', lane='product',
                  model='GPT-6 Astra', action_id='SAME-ACTION', action_kind='implement',
                  expect_next=state['next_sha256'], prompt_file='prompt.txt')
    values.update(overrides)
    args = [x for key, val in values.items() for x in ('--' + key.replace('_', '-'), val)]
    result = command('-C', root, 'next-write', *args)
    if not overrides:
        assert result.returncode == 0, result.stderr
    return result
