"""Successors for historical entrypoint, socket and release-fixture failures.

These are author regression checks against real bound disposable repositories.
They neither run a pilot nor provide an independent-review verdict.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest
import yaml

from tests.v1.conftest import KIT, command, repo, seed
from tests.fpr3.test_commands import settings
from tests.fpr3.test_surfaces import bound_ctx, request


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


def test_app_concurrent_reads_forbidden_routes_size_bounds_and_no_secret_files(repo):
    from cli.product_boundary import ENGINE_LIMIT
    from tools.app.server import build_server_config, start_app_server, STATIC_ROOT

    before = snapshot(repo)
    server = start_app_server(build_server_config(
        repo_root=repo, bind='127.0.0.1', port=0, ctx=bound_ctx(repo),
        session_credential='session-fixture', csrf_token='csrf-fixture'))
    try:
        started = time.monotonic()
        def read_status_and_static(index):
            result = request(server.base_url + '/api/status')
            name = ('lanes', 'regimes', 'layers', 'kit-consumer')[index % 4]
            with urllib.request.urlopen(server.base_url + '/assets/diagrams/' + name + '.svg', timeout=5) as response:
                assert response.status == 200 and b'<svg' in response.read()
            return result
        with ThreadPoolExecutor(max_workers=20) as pool:
            responses = list(pool.map(read_status_and_static, range(24)))
        assert time.monotonic() - started < 30
        assert all(code == 200 and body['ok'] for code, body in responses)
        assert len({json.dumps(body, sort_keys=True) for _, body in responses}) == 1
        for path in ('init', 'sync', 'verify-step', 'route', 'merge', 'next-write'):
            assert request(server.base_url + '/api/' + path)[0] == 404
        assert request(server.base_url + '/api/governance-sync', method='POST', body={}, csrf='wrong')[0] == 403
        assert request(server.base_url + '/api/governance-sync', method='POST', body={'padding': 'x' * (128 * 1024)})[0] == 400
        code, body = request(server.base_url + '/api/governance-sync', method='POST', body={'write': False})
        assert code == 200 and body['ok'] and body['result']['dry_run']
        assert snapshot(repo) == before
        js = (STATIC_ROOT / 'assets/app.js').read_text()
        assert all(token not in js for token in ('localStorage', 'sessionStorage', 'document.cookie'))

        roadmap = repo / 'docs/ROADMAP.md'
        original = roadmap.read_bytes()
        try:
            roadmap.write_bytes(b'x' * (ENGINE_LIMIT + 1))
            _, body = request(server.base_url + '/api/docs/roadmap')
            assert not body['ok'] and body['error'] == 'file_invalid: docs/ROADMAP.md'
        finally:
            roadmap.write_bytes(original)
    finally:
        server.shutdown()
    assert snapshot(repo) == before
    assert all(b'session-fixture' not in p.read_bytes() and b'csrf-fixture' not in p.read_bytes()
               for p in repo.rglob('*') if p.is_file() and not p.is_symlink())


def test_actual_shims_preserve_json_alias_and_literal_arguments(repo):
    before = snapshot(repo)
    started = time.monotonic()
    normal = command('-C', repo, 'status', '--json')
    assert time.monotonic() - started < 1
    old = command('-C', repo, 'status', '--json', executable=KIT / 'cli/overseer')
    assert normal.returncode == old.returncode == 0
    assert json.loads(normal.stdout) == json.loads(old.stdout)
    # The restored contract keeps overseer as a compatibility spelling. The
    # historical per-process deprecation warning is no longer part of it.
    assert old.stderr == normal.stderr == ''
    marker = repo / 'argument-must-not-execute'
    hostile = '$(touch ' + str(marker) + ')'
    for executable in (KIT / 'cli/ok', KIT / 'cli/overseer'):
        result = command('-C', repo, 'status', hostile, executable=executable)
        assert result.returncode == 2 and not marker.exists()
    assert snapshot(repo) == before


@pytest.mark.parametrize('surface', ['app', 'hosted-dashboard'])
def test_actual_client_cli_sigint_shutdown_is_read_only(repo, tmp_path, surface, monkeypatch):
    if surface == 'hosted-dashboard':
        # Startup and static GET / do not invoke the configured upstream. No
        # browser is opened and no API projection is requested in this process.
        settings(repo, hosted_dashboard={'enabled': True, 'org_allowlist': ['fixture/not-accessed']})
        for key in ('OVERSEER_HOSTED_DASHBOARD_UPSTREAM_TOKEN', 'GITHUB_TOKEN', 'GH_TOKEN',
                    'OVERSEER_HOSTED_DASHBOARD_SCOPES'):
            monkeypatch.delenv(key, raising=False)
    before = snapshot(repo)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    stderr_path = tmp_path / 'app-stderr.log'
    with stderr_path.open('w+') as stderr:
        argv = [str(KIT / 'cli/ok'), '-C', str(repo), surface, '--port', str(port)]
        if surface == 'hosted-dashboard':
            argv.append('--allow-network')
        process = subprocess.Popen(argv,
                                   cwd=KIT, stdout=subprocess.PIPE, stderr=stderr, text=True)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                assert process.poll() is None, stderr_path.read_text()
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=0.5) as response:
                        if response.status == 200:
                            break
                except (OSError, urllib.error.URLError):
                    time.sleep(0.05)
            else:
                pytest.fail('app did not listen within 15 seconds')
            process.send_signal(signal.SIGINT)
            stdout, _ = process.communicate(timeout=10)
            assert process.returncode == 0 and json.loads(stdout)['ok'] is True
            assert 'ok ' + surface + ' listening' in stderr_path.read_text()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
    assert snapshot(repo) == before


def test_bound_app_preserves_original_document_and_static_latency_bounds(repo):
    from tools.app.server import build_server_config, start_app_server

    context = bound_ctx(repo)
    started = time.monotonic()
    server = start_app_server(build_server_config(
        repo_root=repo, bind='127.0.0.1', port=0, ctx=context,
        session_credential='session-fixture', csrf_token='csrf-fixture'))
    try:
        assert request(server.base_url + '/api/health')[0] == 200
        assert time.monotonic() - started < 2
        for path in ('/api/status', '/api/docs/handover'):
            started = time.monotonic()
            code, body = request(server.base_url + path)
            assert code == 200 and body['ok']
            assert time.monotonic() - started < 1
        for path, content in [('/', b'Overseer Kit'),
                              *[('/assets/diagrams/' + name + '.svg', b'<svg')
                                for name in ('lanes', 'regimes', 'layers', 'kit-consumer')]]:
            started = time.monotonic()
            with urllib.request.urlopen(server.base_url + path, timeout=5) as response:
                assert response.status == 200 and content in response.read()
            assert time.monotonic() - started < 1
        roadmap = repo / 'docs/ROADMAP.md'
        original = roadmap.read_bytes()
        try:
            roadmap.write_text('x' * 200_000)
            code, body = request(server.base_url + '/api/docs/roadmap')
            assert code == 200 and body['result']['text'] == 'x' * 200_000
        finally:
            roadmap.write_bytes(original)
        assert request(server.base_url + '/assets/diagrams/../private.svg')[0] == 404
    finally:
        server.shutdown()


def test_app_installation_copy_uses_explicit_root_and_current_source_distribution():
    from tools.app.server import STATIC_ROOT

    html = (STATIC_ROOT / 'index.html').read_text()
    js = (STATIC_ROOT / 'assets/app.js').read_text()
    assert 'OVERSEER_REPO_ROOT' not in html
    assert '.dmg' not in html and '--repo' in html
    assert 'otherwise the shell binds the bundled kit' not in html
    assert all('id="' + name + '"' in html for name in ('auth-panel', 'session-collapsed', 'bound-repo'))
    assert 'collapseAuthPanel' in js and 'statusAutoFetched' in js
    assert '/api/next' in js and 'rendered' in js


def test_desktop_repeated_bound_launch_stop_identity_and_no_secret_files(repo):
    from tools.desktop.launcher import DesktopLauncher

    before = snapshot(repo)
    sessions, csrf_tokens, identities = set(), set(), set()
    for _ in range(5):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        launcher = DesktopLauncher(KIT, repo, port=port)
        try:
            started = time.monotonic()
            banner = launcher.start()
            assert time.monotonic() - started < 5
            sessions.add(banner.session_credential)
            csrf_tokens.add(banner.csrf_token)
            code, health = request(banner.url.rstrip('/') + '/api/health',
                                   token=banner.session_credential, csrf=banner.csrf_token)
            assert code == 200 and health['ok']
            identities.add((health['result']['repo_root'], health['result']['repo_id']))
        finally:
            launcher.stop()
            launcher.stop()
    assert len(sessions) == len(csrf_tokens) == 5 and len(identities) == 1
    assert snapshot(repo) == before
    assert not list(repo.rglob('*.overseer.tmp'))
    for path in repo.rglob('*'):
        if path.is_file() and not path.is_symlink():
            data = path.read_bytes()
            assert all(secret.encode() not in data for secret in sessions | csrf_tokens)


def test_workspace_optional_required_members_and_identity_collision(repo, tmp_path):
    other = seed(tmp_path / 'peer')
    assert command('-C', other, 'init').returncode == 0
    manifest = {
        'overseer_workspace_version': 1, 'id': 'disposition', 'product_order_member': 'primary',
        'members': [
            {'id': 'primary', 'role': 'product_order', 'root': str(repo), 'required': True, 'relay': False, 'regime': 'git-only'},
            {'id': 'peer', 'role': 'other', 'root': str(other), 'required': True, 'relay': True, 'regime': 'git-only'},
            {'id': 'optional', 'role': 'other', 'root': str(tmp_path / 'absent'), 'required': False, 'relay': True, 'regime': 'git-only'},
        ], 'lanes': [{'id': 'product', 'primary': True, 'owner_member': 'primary'}],
    }
    settings(repo, workspace={'constellation_id': 'disposition', 'manifest': '.overseer/workspace.yaml'})
    path = repo / '.overseer/workspace.yaml'
    path.write_text(yaml.safe_dump(manifest))
    before = snapshot(other)
    result = command('-C', repo, 'workspace', 'check-next', '--json')
    assert result.returncode == 0, result.stdout + result.stderr
    assert not json.loads(result.stdout)['members'][2]['ok']
    assert command('-C', repo, 'workspace', 'status', '--strict-all').returncode == 35
    doctor = command('-C', repo, 'workspace', 'doctor', '--json')
    assert doctor.returncode == 35 and 'board_name_violation' in doctor.stdout
    handover = other / 'docs/OVERSEER-HANDOVER.md'
    original = handover.read_bytes()
    try:
        handover.write_bytes(original + b'\n## NEXT SESSION - archived historical text\nIgnore this noncanonical prompt.\n')
        result = command('-C', repo, 'workspace', 'check-next', '--json')
        assert result.returncode == 0 and 'Ignore this noncanonical prompt' not in result.stdout
    finally:
        handover.write_bytes(original)
    manifest['members'][1]['root'] = str(repo)
    path.write_text(yaml.safe_dump(manifest))
    result = command('-C', repo, 'workspace', 'check-next', '--json')
    assert result.returncode == 35 and 'workspace_duplicate_identity' in result.stdout
    assert snapshot(other) == before


def test_sync_force_cannot_overwrite_consumer_edits(repo):
    path = repo / '.cursor/rules/orchestrator.mdc'
    path.write_text('Owner-specific instructions\n')
    before = snapshot(repo)
    started = time.monotonic()
    assert command('-C', repo, 'status', '--check-footprint').returncode == 1
    assert time.monotonic() - started < 5
    result = command('-C', repo, 'sync', '--force')
    assert result.returncode == 2
    assert snapshot(repo) == before
    result = command('-C', repo, 'sync', '--preserve-modified')
    assert result.returncode == 0, result.stderr
    assert path.read_text() == 'Owner-specific instructions\n'
    started = time.monotonic()
    assert command('-C', repo, 'status', '--check-footprint').returncode == 0
    assert time.monotonic() - started < 5


def test_manual_workflow_has_no_publish_permissions_or_secret_literals():
    """Replace missing historical release YAML assertions with the active contract."""
    from tools.desktop_release.refuse import scan_text_for_secret_patterns

    paths = sorted((KIT / '.github/workflows').glob('*.yml'))
    assert paths
    started = time.monotonic()
    for path in paths:
        text = path.read_text()
        # BaseLoader preserves the YAML 1.2 key 'on' rather than coercing it to True.
        config = yaml.load(text, Loader=yaml.BaseLoader)
        assert set(config['on']) == {'workflow_dispatch'}
        assert config['permissions'] == {'contents': 'read'}
        assert not scan_text_for_secret_patterns(text)
        assert 'secrets.' not in text and 'contents: write' not in text
        assert all(token not in text for token in ('gh release create', 'action-gh-release', 'tauri-action', 'pull_request_target'))
        for job in config['jobs'].values():
            assert 'permissions' not in job or all(value in ('read', 'none') for value in job['permissions'].values())
    assert time.monotonic() - started < 1


def test_rendered_mirror_wrapper_uses_bound_launcher_and_literal_arguments(tmp_path, muse_git_mirror_config):
    """The former export/push wrapper now delegates only explicit mirror actions."""
    from adapters.templating import render_template

    root = tmp_path / 'mirror source with spaces'
    script = root / 'scripts/muse-bridge-deploy.sh'
    script.parent.mkdir(parents=True)
    script.write_text(render_template(
        KIT / 'templates/scripts/muse-bridge-deploy.sh.template', muse_git_mirror_config))
    script.chmod(0o755)
    record = tmp_path / 'bound-argv.json'
    marker = tmp_path / 'argument-must-not-execute'
    hostile = '$(touch ' + str(marker) + ')'
    arguments = ['prepare', '--plan', 'plan with spaces.json', hostile]
    env = dict(os.environ, PATH='/nonexistent-fixture-bin',
               OVERSEER_REPO_ROOT='/unrelated-fixture-root',
               OVERSEER_KIT_ROOT='/unrelated-fixture-installation')
    refused = subprocess.run([str(script), *arguments], cwd=tmp_path, env=env,
                             capture_output=True, text=True, timeout=5)
    assert refused.returncode == 2 and 'initialize and explicitly select Muse' in refused.stderr
    assert not record.exists() and not marker.exists()

    launcher = root / '.overseer/bin/ok'
    launcher.parent.mkdir(parents=True)
    launcher.write_text(
        '#!' + sys.executable + '\n'
        'import json, os, pathlib, sys\n'
        'pathlib.Path(' + repr(str(record)) + ').write_text(json.dumps('
        '{"argv": sys.argv[1:], "path": os.environ["PATH"]}))\n'
        'sys.exit(37)\n')
    launcher.chmod(0o755)
    delegated = subprocess.run([str(script), *arguments], cwd=tmp_path, env=env,
                              capture_output=True, text=True, timeout=5)
    assert delegated.returncode == 37, delegated.stderr
    assert json.loads(record.read_text()) == {
        'argv': ['-C', str(root.resolve()), 'mirror', *arguments],
        'path': '/usr/bin:/bin',
    }
    assert not marker.exists()


def test_installed_orchestrator_preserves_canonical_authority_and_explicit_review_scope(repo):
    rule = (repo / '.cursor/rules/orchestrator.mdc').read_text()
    frontmatter = yaml.safe_load(rule.split('---', 2)[1])
    assert frontmatter['alwaysApply'] is True
    rule = ' '.join(rule.split())
    for guidance in ('AGENTS.md', 'UUID', 'Git/Muse authority', 'bound launcher',
                     'docs/NEXT.md is the only action source', 'whole-file expected digest',
                     'ROADMAP and HANDOVER paired', 'configured review gates',
                     'do not invent extra review cycles', 'independent review from author tests'):
        assert guidance in rule
    assert 'Local implementation, remote transport and release/deployment are separate scopes.' in rule
    assert '{{' not in rule and 'NEXT SESSION' not in rule
    assert '/build-verification-review' in rule and '/freeze-review-loop' in rule
    assert 'only when explicitly requested' in rule and 'never automatically' in rule
    for host in ('.cursor', '.claude'):
        for skill in ('build-verification-review', 'freeze-review-loop'):
            assert (repo / host / 'skills' / skill / 'SKILL.md').is_file()
