"""Actual product dispatcher/normalization boundary, independent of legacy main."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

from cli import main, v1
from cli.product_config import normalize
from tests.v1.conftest import KIT, command, seed, status, write_action


@pytest.fixture
def repo(tmp_path):
    root = seed(tmp_path / 'product')
    result = command('-C', root, 'init')
    assert result.returncode == 0, result.stderr
    return root


def test_all_launchers_share_dispatcher_and_global_options(repo):
    source = (KIT / 'cli/bootstrap.py').read_text()
    assert 'from cli.main import main' in source
    assert 'from cli.v1 import main' not in source
    states = []
    for launcher in (KIT/'cli/ok', KIT/'cli/overseer', repo/'.overseer/bin/ok'):
        for args in (('-C', repo, '--json', 'status'), ('status', '--json', '-C', repo)):
            result = command(*args, executable=launcher, cwd=repo)
            assert result.returncode == 0, result.stderr
            states.append(json.loads(result.stdout))
    assert all(state == states[0] for state in states)
    assert states[0]['configuration']['schema'] == 3
    assert not states[0]['migration_required']
    assert command('-C', repo, 'status', '--quiet').stdout == ''


def test_historical_module_is_not_a_second_public_cli(repo):
    result = subprocess.run([str(KIT/'.venv/bin/python'), '-B', '-m', 'cli.legacy_main',
                             '-C', str(repo), 'status'], cwd=KIT, capture_output=True, text=True)
    assert result.returncode == 2 and not result.stdout
    assert 'historical dispatcher; use cli/ok' in result.stderr


def test_invalid_binding_cannot_enter_injected_handler(repo, monkeypatch, capsys):
    config_path = repo / v1.CONFIG
    config = yaml.safe_load(config_path.read_bytes())
    config['repo']['root'] = str(repo.parent)
    config_path.write_text(yaml.safe_dump(config))
    def forbidden(*args, **kwargs):
        pytest.fail('handler was entered before context validation')
    monkeypatch.setattr(v1, 'write_next', forbidden)
    assert main.main(['-C', str(repo), 'next-write', '--repo-id', config['repo']['id'],
        '--branch', 'main', '--lane', 'product', '--model', 'GPT-6 Astra',
        '--action-id', 'DISPATCH', '--action-kind', 'implement', '--expect-next', 'absent',
        '--prompt-file', 'not-read.txt']) == 2
    captured = capsys.readouterr()
    assert not captured.out and 'config_repository_mismatch' in captured.err


def test_git_core_imports_no_muse_or_provider_engine(repo, capsys):
    before = set(sys.modules)
    assert main.main(['-C', str(repo), 'status', '--json']) == 0
    imported = set(sys.modules) - before
    assert not any(name.startswith(('muse', 'adapters.muse_', 'tools.freeze_reviewer.providers'))
                   for name in imported)
    assert json.loads(capsys.readouterr().out)['authority'] == 'git'


@pytest.mark.parametrize('authority,bound', [('git', False), ('muse', False), ('muse', True)])
def test_legacy_and_unavailable_authority_inspection_never_probes_git(tmp_path, monkeypatch, capsys, authority, bound):
    root = tmp_path/'non-git'; root.mkdir(); (root/'.overseer').mkdir()
    config = yaml.safe_load((KIT/'tests/fixtures/config-git-only.yaml').read_bytes())
    config['vcs']['regime'] = 'git-only' if authority == 'git' else 'muse-only'
    config['vcs']['canonical'] = authority
    if authority == 'muse':
        config['vcs']['muse']['main_branch'] = 'main'
    if bound:
        config = normalize(v1.encode(config), root=root, runtime=v1.runtime(), bind=True).data
    (root/v1.CONFIG).write_bytes(v1.encode(config))
    def forbidden(*args, **kwargs):
        pytest.fail('unsupported/unbound authority must not inspect Git')
    monkeypatch.setattr(v1, 'git', forbidden)
    assert main.main(['-C', str(root), 'status', '--json']) == 1
    output = json.loads(capsys.readouterr().out)
    assert output['authority'] == authority and output['ok'] is False
    assert main.main(['-C', str(root), 'next']) == 2
    assert not capsys.readouterr().out


def test_schema2_git_next_stays_byte_exact_across_sync(repo):
    path = repo/v1.NEXT
    meta, prompt = v1.parse_next(path.read_bytes())
    meta.update(schema=2, vcs='git', source_id=None)
    content = b'---\n' + v1.encode(meta) + b'---\n' + prompt.encode()
    path.write_bytes(content)
    assert command('-C', repo, 'next').returncode == 0
    assert command('-C', repo, 'sync').returncode == 0
    assert path.read_bytes() == content


def test_init_dry_run_and_conflicts_do_not_write(tmp_path, repo):
    fresh = seed(tmp_path/'fresh')
    assert command('-C', fresh, 'init', '--hooks', '--dry-run').returncode == 0
    assert not (fresh/'.overseer').exists() and not (fresh/'docs').exists()
    before = (repo/v1.CONFIG).read_bytes()
    for args in (('init', '--lane', 'other'), ('init', '--apply-plan', 'none.json'),
                 ('init', '--migrate', '--dry-run', '--apply-plan', 'none.json'),
                 ('sync', '--only', 'hooks')):
        result = command('-C', repo, *args)
        assert result.returncode == 2 and not result.stdout
    assert (repo/v1.CONFIG).read_bytes() == before


def test_runtime_manifest_covers_reachable_owned_modules_and_resources(tmp_path, monkeypatch):
    paths = set(v1.runtime_files())
    for path in ('cli/main.py', 'cli/product_config.py', 'cli/product_migration.py',
                 'cli/product_bookends.py', 'adapters/config.py', 'adapters/types.py',
                 'tools/hosted_dashboard/config.py', 'cursor/skills/print-next/SKILL.md',
                 'templates/BOOKENDS.instructions.md'):
        assert path in paths
    copied = tmp_path/'runtime'
    for path in paths:
        target = copied/path; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(KIT/path, target)
    monkeypatch.setattr(v1, 'KIT', copied)
    baseline = v1.runtime()['sha256']
    target = copied/'templates/BOOKENDS.instructions.md'
    target.write_bytes(target.read_bytes() + b'\nchanged resource\n')
    assert v1.runtime()['sha256'] != baseline
    baseline = v1.runtime()['sha256']
    (copied/'cli/new_owned_helper.py').write_text('VALUE = 1\n')
    assert v1.runtime()['sha256'] != baseline


def test_repeated_init_refuses_custom_owned_assets(repo):
    launcher = repo/'.overseer/bin/ok'
    custom = launcher.read_bytes() + b'# owner addition\n'
    launcher.write_bytes(custom)
    before = (repo/v1.CONFIG).read_bytes(), (repo/v1.NEXT).read_bytes()
    result = command('-C', repo, 'init')
    assert result.returncode == 2 and 'init_asset_modified' in result.stderr
    assert launcher.read_bytes() == custom
    assert ((repo/v1.CONFIG).read_bytes(), (repo/v1.NEXT).read_bytes()) == before


def test_repeated_init_preserves_preserved_asset_mode(repo):
    launcher = repo/'.overseer/bin/ok'
    launcher.chmod(0o644)
    lock = {'footprint': [{'path': '.overseer/bin/ok', 'origin': 'preserved',
                          'sha256': v1.digest(launcher.read_bytes()), 'source': 'bound-launcher'}]}
    (repo/'.overseer/version.lock').write_bytes(v1.encode(lock))
    result = command('-C', repo, 'init')
    assert result.returncode == 0, result.stderr
    assert launcher.stat().st_mode & 0o777 == 0o644


@pytest.mark.parametrize('regime', ['muse-only', 'muse+git-mirror'])
def test_unavailable_init_authority_refuses_before_git_discovery(tmp_path, monkeypatch, capsys, regime):
    root = tmp_path/'native-only'; root.mkdir(); (root/'.muse').mkdir()
    def forbidden(*args, **kwargs):
        pytest.fail('unsupported Muse init must not probe Git')
    monkeypatch.setattr(v1, 'git', forbidden)
    assert main.main(['-C', str(root), 'init', '--regime', regime]) == 2
    output = capsys.readouterr()
    assert not output.out and 'muse_python_required' in output.err
    assert not (root/'.overseer').exists()
