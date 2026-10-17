import json
import subprocess
from pathlib import Path

import pytest
import yaml

from cli import v1
from cli.v1_io import digest
from tests.v1.conftest import command, seed


def lanes(root):
    path = root/v1.CONFIG
    cfg = yaml.safe_load(path.read_bytes())
    cfg['docs']['lanes']['architecture'] = {'repo_id': cfg['repo']['id'],
        'roadmap': 'ARCH-ROADMAP.md', 'handover': 'ARCH-HANDOVER.md'}
    path.write_text(yaml.safe_dump(cfg))
    return cfg


def writer(root, lane, expected=None, text=None):
    cfg = yaml.safe_load((root/v1.CONFIG).read_bytes())
    path = 'prompt-' + lane + '.txt'
    (root/path).write_text(text or ('Task for ' + lane + '\n'))
    return ['-C', str(root), 'next-write', '--repo-id', cfg['repo']['id'],
            '--branch', v1.branch(root), '--lane', lane, '--model', cfg['context']['model'],
            '--action-id', 'LANE-TASK', '--action-kind', 'implement',
            '--expect-next', expected or digest((root/v1.NEXT).read_bytes()), '--prompt-file', path]


def test_collection_missing_selection_stale_and_bookends(repo):
    lanes(repo)
    result = command('-C', repo, 'next', '--json')
    data = json.loads(result.stdout)
    assert data['selection_required']
    assert not data['lanes']['architecture']['ok']
    assert command(*writer(repo, 'architecture')).returncode == 0
    assert v1.parse_next((repo/v1.NEXT).read_bytes())[0]['schema'] == 3
    before = (repo/v1.NEXT).read_bytes()
    manual = command('-C', repo, 'next', '--lane', 'architecture')
    assert manual.returncode == 0 and 'Other repository lanes' in manual.stdout
    hook = subprocess.run([str(repo/'.cursor/hooks/session-start-next.sh')],
                          input=json.dumps({'lane': 'architecture'}), text=True, capture_output=True, cwd=repo)
    assert hook.returncode == 0, hook.stderr
    assert json.loads(hook.stdout)['additional_context'] == manual.stdout
    v1.git(repo, 'add', v1.NEXT); v1.git(repo, 'commit', '-m', 'closing lanes')
    assert command('-C', repo, 'next', '--lane', 'architecture').returncode == 0
    v1.git(repo, 'commit', '--allow-empty', '-m', 'later work')
    assert command(*writer(repo, 'product')).returncode == 0
    result = json.loads(command('-C', repo, 'next', '--all-lanes', '--json').stdout)
    assert result['lanes']['product']['ok']
    assert not result['lanes']['architecture']['ok']
    assert 'stale_head' in result['lanes']['architecture']['error']
    assert command('-C', repo, 'next', '--lane', 'architecture').returncode == 2


def test_two_repositories_lane_ownership_and_no_fallback(repo, tmp_path):
    config = lanes(repo)
    other = seed(tmp_path/'other')
    assert command('-C', other, 'init').returncode == 0
    lanes(other)
    assert command(*writer(repo, 'architecture')).returncode == 0
    assert command(*writer(other, 'architecture')).returncode == 0
    prior = (other/v1.NEXT).read_bytes()
    (other/v1.NEXT).write_bytes((repo/v1.NEXT).read_bytes())
    assert command('-C', other, 'next', '--lane', 'architecture').returncode == 2
    (other/v1.NEXT).write_bytes(prior)
    config['docs']['lanes']['architecture']['repo_id'] = '00000000-0000-0000-0000-000000000001'
    (repo/v1.CONFIG).write_text(yaml.safe_dump(config))
    assert command('-C', repo, 'next').returncode == 2
    assert command('-C', other, 'next', '--lane', 'architecture').returncode == 0


def test_concurrent_lane_updates_whole_file_cas(repo):
    lanes(repo)
    expected = digest((repo/v1.NEXT).read_bytes())
    workers = [subprocess.Popen([str(v1.KIT/'cli/ok'), *writer(repo, lane, expected)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) for lane in ('product', 'architecture')]
    for worker in workers:
        worker.communicate(timeout=30)
    assert sorted(p.returncode for p in workers) == [0, 2]
    assert command('-C', repo, 'next', '--all-lanes').returncode == 0


@pytest.mark.parametrize('damage', ['extra_body', 'digest', 'undeclared', 'missing_body'])
def test_entire_collection_validated_before_selected_output(repo, damage):
    lanes(repo)
    assert command(*writer(repo, 'architecture')).returncode == 0
    path = repo/v1.NEXT
    raw = path.read_text()
    if damage == 'extra_body':
        raw += '<!-- overseer-next:architecture -->\nConflicting task.\n'
    elif damage == 'digest':
        raw = raw.replace('Task for architecture', 'Tampered architecture')
    elif damage == 'undeclared':
        raw = raw.replace('architecture', 'foreign')
    else:
        raw = raw.replace('<!-- overseer-next:architecture -->\n', '')
    path.write_text(raw)
    result = command('-C', repo, 'next', '--lane', 'product')
    assert result.returncode == 2 and not result.stdout


def test_explicit_batch_updates_only_selected_lanes_with_one_cas(repo):
    cfg = lanes(repo)
    before = (repo/v1.NEXT).read_bytes()
    request = {'lanes': {lane: {'model': 'GPT-6 Astra', 'action_id': 'BATCH',
        'action_kind': 'implement', 'prompt': 'Accepted task for ' + lane + '\n'}
        for lane in ('product', 'architecture')}}
    (repo/'batch.json').write_text(json.dumps(request))
    args = ['-C', repo, 'next-write', '--repo-id', cfg['repo']['id'], '--branch', v1.branch(repo),
            '--expect-next', digest(before), '--batch-file', 'batch.json']
    result = command(*args)
    assert result.returncode == 0, result.stderr
    after = (repo/v1.NEXT).read_bytes()
    assert command(*args).returncode == 2
    assert (repo/v1.NEXT).read_bytes() == after
    data = json.loads(command('-C', repo, 'next', '--all-lanes', '--json').stdout)
    assert all(item['ok'] for item in data['lanes'].values())
    assert all(item['next']['action_id'] == 'BATCH' for item in data['lanes'].values())


@pytest.mark.parametrize('option', ['--vcs', '--base-head', '--action-id', '--action-kind', '--batch-file'])
def test_duplicate_authority_and_publication_selectors_refuse(repo, option):
    before = (repo/v1.NEXT).read_bytes()
    result = command('-C', repo, 'next-write', option, 'one', option, 'two')
    assert result.returncode == 2 and 'duplicate_binding_option' in result.stderr
    assert (repo/v1.NEXT).read_bytes() == before


def test_git_preserves_inactive_muse_settings_without_using_them(repo):
    path = repo/v1.CONFIG
    cfg = yaml.safe_load(path.read_bytes())
    settings = {'main_branch': 'native-main', 'staging_remote': 'retained-staging', 'working_dir': None}
    cfg['vcs']['muse'].update(settings)
    path.write_text(yaml.safe_dump(cfg))
    before = path.read_bytes()
    result = command('-C', repo, 'status', '--json')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['configuration']['vcs']['muse'] == settings
    assert path.read_bytes() == before
    cfg['vcs']['muse']['main_branch'] = {'invalid': True}
    path.write_text(yaml.safe_dump(cfg))
    assert command('-C', repo, 'status').returncode == 2
