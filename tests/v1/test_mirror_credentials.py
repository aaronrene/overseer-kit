"""Exercise Git's credential protocol with a fake gh; never use real secrets."""
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

from cli import v1_mirror as mirror
from cli.v1_io import Refusal


@pytest.fixture
def adapter(tmp_path):
    executable = tmp_path / "gh with ' quotes"
    executable.write_text('#!/bin/sh\n[ "$*" = "auth token --hostname github.com" ] || exit 9\n'
                          'printf "%s\\n" fixture-token-never-a-real-credential\n')
    executable.chmod(0o755)
    return mirror.NetworkDelivery(str(executable.resolve()))


def credential(adapter, request, operation='fill'):
    dest = {'url': 'https://github.com/fixture/mirror.git', 'repository': 'fixture/mirror'}
    return subprocess.run(['/usr/bin/git', *adapter.git_options(dest), 'credential', operation],
                          cwd='/', input=request, env=mirror.env(), capture_output=True, timeout=10)


def test_git_credential_fill_scoped_helper_and_no_persistent_config(adapter, tmp_path):
    request = b'protocol=https\nhost=github.com\npath=fixture/mirror.git\n\n'
    before = {p: p.read_bytes() for p in tmp_path.iterdir()}
    result = credential(adapter, request)
    assert result.returncode == 0, result.stderr
    assert b'password=fixture-token-never-a-real-credential\n' in result.stdout
    assert b'username=x-access-token\n' in result.stdout
    assert result.stderr == b''
    for operation in ('approve', 'reject'):
        assert credential(adapter, request + b'password=fixture-only\n', operation).returncode == 0
    assert {p: p.read_bytes() for p in tmp_path.iterdir()} == before
    assert 'fixture-token' not in repr(adapter.git_options({'url': 'https://github.com/fixture/mirror.git'}))


@pytest.mark.parametrize('payload', [
    b'protocol=http\nhost=github.com\npath=fixture/mirror.git\n\n',
    b'protocol=https\nhost=example.invalid\npath=fixture/mirror.git\n\n',
    b'protocol=https\nhost=github.com\npath=fixture/other.git\n\n',
    b'protocol=https\nhost=github.com\npath=fixture/mirror.git/extra\n\n',
    b'protocol=https\nhost=github.com\n\n',
    b'protocol=https\nhost=github.com:443\npath=fixture/mirror.git\n\n',
])
def test_wrong_credential_scope_never_returns_token(adapter, payload):
    result = credential(adapter, payload)
    assert result.returncode != 0
    assert b'fixture-token' not in result.stdout + result.stderr


def test_credential_failure_hides_gh_output(adapter):
    adapter.gh.write_text('#!/bin/sh\necho fixture-secret-error >&2\necho fixture-secret-token\nexit 1\n')
    result = credential(adapter, b'protocol=https\nhost=github.com\npath=fixture/mirror.git\n\n')
    assert result.returncode != 0 and b'fixture-secret' not in result.stdout + result.stderr


def test_transport_credentials_are_ephemeral_and_redirects_disabled(adapter, monkeypatch):
    monkeypatch.setenv('GIT_TRACE', '/not-used')
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    monkeypatch.setenv('SSH_ASKPASS', '/unapproved-helper')
    monkeypatch.setenv('GIT_ASKPASS', '/unapproved-helper')
    monkeypatch.setenv('GH_DEBUG', 'api')
    dest = {'url': 'https://github.com/fixture/mirror.git', 'repository': 'fixture/mirror', 'branch': 'muse-mirror'}
    with patch.object(mirror.subprocess, 'run') as run:
        run.return_value.returncode = 0
        run.return_value.stdout = b''
        adapter.push(Path('/'), dest, 'a' * 40)
        adapter.remote_head(dest)
    for call in run.call_args_list:
        argv = call.args[0]
        assert 'credential.helper=' in argv and 'credential.useHttpPath=true' in argv
        assert 'http.followRedirects=false' in argv and 'protocol.allow=never' in argv
        assert '--force' not in argv and '--force-with-lease' not in argv
        assert 'GIT_TRACE' not in call.kwargs['env'] and 'GIT_CONFIG_COUNT' not in call.kwargs['env']
        assert 'SSH_ASKPASS' not in call.kwargs['env'] and 'GH_DEBUG' not in call.kwargs['env']
        assert call.kwargs['env']['GIT_ASKPASS'] == '/usr/bin/false'
        assert 'fixture-token' not in repr(call)


@pytest.mark.parametrize('url', ['http://github.com/fixture/mirror.git',
    'https://token@github.com/fixture/mirror.git', 'https://github.com/../mirror.git',
    'https://github.com/fixture/mirror.git?token=secret', 'https://example.invalid/fixture/mirror.git'])
def test_transport_rejects_unscoped_urls(adapter, url):
    with pytest.raises(Refusal, match='credential_destination'):
        adapter.git_options({'url': url})
