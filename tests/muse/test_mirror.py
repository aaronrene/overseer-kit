"""Real local Muse/Git objects; all delivery writes are recording stand-ins."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest
import yaml

from cli import v1_mirror as mirror
from cli.v1_io import Refusal, digest
from cli.v1_revision import muse_read
from tests.muse.test_handoffs import init, inventory
from tests.v1.conftest import command, KIT, seed


@pytest.fixture
def case(muse_root, muse_python, muse, tmp_path):
    root = muse_root
    init(root, muse_python)
    (root / 'app.py').write_text('value = 1\n')
    (root / 'data.bin').write_bytes(b'\0\xff\r\n\x01')
    (root / 'script.txt').write_bytes(b'#!/bin/sh\n# A shebang is not executable authority.\n')
    (root / 'run-tool').write_bytes(b'executable without a shebang\n')
    (root / 'run-tool').chmod(0o755)
    (root / 'templates').mkdir()
    (root / 'templates/NEXT.md').write_text('Portable template\n')
    muse(root, 'code', 'add', '.')
    muse(root, 'commit', '-m', 'approved fixture source', '--json')
    state = muse_read(root, str(muse_python))
    plan = {'schema': 1, 'source': {'repo_id': state['repo_id'], 'branch': 'main',
            'revision': state['head'], 'hub_url': 'https://staging.musehub.ai/fixture/source'},
            'destination': {'url': 'https://github.com/fixture/mirror.git', 'repository': 'fixture/mirror',
                'branch': 'muse-mirror', 'base': 'main', 'expected_head': 'absent'},
            'target': str((tmp_path/'bare-mirror').resolve()), 'expected_target': 'absent',
            'executables': ['run-tool']}
    return root, plan


def execute(case, operation='prepare', transport=None):
    root, plan = case
    original = (root/'.overseer/config.yaml').read_bytes()
    return mirror.execute(root, yaml.safe_load(original), original, plan, digest(mirror.packed(plan)), operation, transport)


def prepared(case):
    result = execute(case)
    assert result['ok'], json.dumps(result)
    return result


class Delivery:
    def __init__(self, plan):
        self.plan = plan
        self.head = plan['destination']['expected_head']
        self.calls = []
        self.fail_push = None
        self.fail_pr = False
        self.authoritative = (plan['source']['repo_id'], plan['source']['revision'])
        self.pr = None

    def authority(self, source):
        self.calls.append(('authority', deepcopy(source)))
        return self.authoritative

    def remote_head(self, dest):
        self.calls.append(('remote', deepcopy(dest)))
        return self.head

    def push(self, target, dest, commit):
        self.calls.append(('push', str(target), deepcopy(dest), commit))
        if self.fail_push != 'before':
            self.head = commit
        if self.fail_push:
            raise OSError('interrupted response')

    def ensure_pr(self, target, dest, source, commit):
        self.calls.append(('pr', str(target), deepcopy(dest), deepcopy(source), commit))
        if self.fail_pr:
            raise Refusal('fixture_pr_failure')
        self.pr = 'https://github.com/fixture/mirror/pull/7'
        return self.pr


def test_projection_modes_mapping_and_offline_retry(case):
    root, plan = case
    before = inventory(root)
    result = prepared(case)
    assert result['push'] == result['pr'] == 'not_attempted'
    assert result['authority'] == 'approved_input_not_checked_offline'
    target = Path(plan['target'])
    assert mirror.git(target, 'rev-parse', '--is-bare-repository') == b'true\n'
    paths = mirror.git(target, 'ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines()
    assert 'templates/NEXT.md' in paths and 'docs/ROADMAP.md' in paths
    assert '.overseer/config.yaml' not in paths and 'docs/NEXT.md' not in paths
    assert mirror.git(target, 'show', 'HEAD:data.bin') == b'\0\xff\r\n\x01'
    assert mirror.git(target, 'ls-tree', 'HEAD', 'run-tool').startswith(b'100755 blob ')
    assert mirror.git(target, 'ls-tree', 'HEAD', 'script.txt').startswith(b'100644 blob ')
    record = (root/mirror.RECORD).read_bytes()
    again = prepared(case)
    assert again['export'] == 'no_change_verified' and again['git_head'] == result['git_head']
    assert (root/mirror.RECORD).read_bytes() == record
    now = inventory(root)
    del now[mirror.RECORD]
    assert now == before
    snapshots = inventory(root), inventory(target)
    assert execute(case, 'verify')['ok']
    assert snapshots == (inventory(root), inventory(target))


@pytest.mark.parametrize('change', ['head', 'branch', 'source_id', 'unknown_revision', 'working', 'mode', 'stage'])
def test_source_drift_refused_before_target(case, change, muse):
    root, plan = case
    if change == 'head':
        plan['source']['revision'] = 'sha256:' + '1'*64
    elif change == 'unknown_revision':
        (root/'.muse/refs/heads/main').write_text('sha256:' + '2'*64)
    elif change == 'branch':
        muse(root, 'checkout', '-b', 'feature', '--json')
    elif change == 'source_id':
        plan['source']['repo_id'] = 'sha256:' + '3'*64
    elif change == 'working':
        (root/'app.py').write_text('changed after approval\n')
    elif change == 'mode':
        (root/'run-tool').chmod(0o644)
    elif change == 'stage':
        (root/'app.py').write_text('staged edit\n')
        muse(root, 'code', 'add', 'app.py')
    try:
        result = execute(case)
        assert not result['ok'], result
    except Refusal:
        pass
    assert not Path(plan['target']).exists()


@pytest.mark.parametrize('kind', ['blob', 'commit', 'snapshot'])
def test_missing_objects_refused(case, muse_python, kind):
    root, plan = case
    code = '''import sys
from pathlib import Path
from muse.core.commits import read_commit
from muse.core.snapshots import read_snapshot
from muse.core.object_store import object_path
root=Path(sys.argv[1]);head=sys.argv[2];kind=sys.argv[3]
c=read_commit(root,head);s=read_snapshot(root,c.snapshot_id)
oid={'blob':s.manifest['app.py'],'commit':head,'snapshot':c.snapshot_id}[kind]
object_path(root,oid).unlink()
'''
    subprocess.run([str(muse_python), '-I', '-B', '-c', code, str(root), plan['source']['revision'], kind], check=True)
    assert not execute(case)['ok']
    assert not Path(plan['target']).exists()


@pytest.mark.parametrize('kind', ['same', 'child', 'parent', 'dot_parent', 'alias', 'alias_parent', 'git_worktree', 'foreign', 'empty'])
def test_targets_are_physical_isolated_and_owned(case, tmp_path, kind):
    root, plan = case
    if kind == 'same': target = root
    elif kind == 'child': target = root/'.muse/mirror'
    elif kind == 'parent': target = root.parent
    elif kind == 'dot_parent': target = root/'.muse/..'
    elif kind == 'alias':
        target = tmp_path/'alias'; target.symlink_to(root, target_is_directory=True)
    elif kind == 'alias_parent':
        alias = tmp_path/'alias'; alias.symlink_to(root.parent, target_is_directory=True)
        target = alias/'bare-mirror'
    elif kind == 'git_worktree':
        dev = seed(tmp_path/'git')
        target = tmp_path/'linked'
        subprocess.run(['/usr/bin/git','-C',str(dev),'worktree','add','-b','mirror',str(target)],check=True,capture_output=True)
    else:
        target = Path(plan['target']); target.mkdir()
        if kind == 'foreign': (target/'foreign').write_text('preserve\n')
    plan['target'] = str(target)
    before = inventory(root)
    with pytest.raises(Refusal) if kind in {'same','child','parent','dot_parent','alias','alias_parent'} else __import__('contextlib').nullcontext():
        result = execute(case)
        assert not result['ok']
    assert inventory(root) == before


@pytest.mark.parametrize('kind', ['untracked', 'config', 'hooks', 'ref', 'alternate', 'symlink'])
def test_dirty_stale_or_hooked_owned_target_refused(case, kind):
    root, plan = case
    prepared(case)
    target = Path(plan['target'])
    if kind == 'untracked': (target/'foreign.txt').write_text('must survive\n')
    elif kind == 'config':
        with (target/'config').open('a') as f: f.write('[core]\n hooksPath=/tmp/unsafe\n')
    elif kind == 'hooks':
        (target/'hooks').mkdir(); (target/'hooks/pre-push').write_text('#!/bin/sh\ntouch BAD\n')
    elif kind == 'ref':
        mirror.git(target, 'update-ref', 'refs/heads/foreign', mirror.head(target))
    elif kind == 'alternate':
        (target/'objects/info').mkdir(); (target/'objects/info/alternates').write_text('/unsafe\n')
    elif kind == 'symlink': (target/'objects/alias').symlink_to(root)
    before = inventory(target)
    result = execute(case)
    assert not result['ok']
    assert inventory(target) == before
    assert not (root/'BAD').exists()


def test_inherited_muse_hook_refused_preserved_and_never_run(case):
    root, plan = case
    marker = root.parent/'HOOK_RAN'
    hook = root/'.muse/bridge-hooks.toml'
    hook.write_text('[pre_bridge]\nhooks=[{run="touch ' + str(marker) + '"}]\n')
    before = inventory(root)
    result = execute(case)
    assert not result['ok'] and 'inherited_muse_hooks: .muse/bridge-hooks.toml' in result['error']
    assert inventory(root) == before and not marker.exists()
    assert not Path(plan['target']).exists()


def test_inherited_git_environment_and_global_hooks_disabled(case, tmp_path, monkeypatch):
    hook = tmp_path/'hooks'; hook.mkdir()
    marker = tmp_path/'HOOK_RAN'
    script = hook/'reference-transaction'
    script.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\n'); script.chmod(0o755)
    global_config = tmp_path/'global-config'
    global_config.write_text('[core]\n hooksPath=' + str(hook) + '\n')
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', str(global_config))
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    monkeypatch.setenv('GIT_CONFIG_KEY_0', 'core.hooksPath')
    monkeypatch.setenv('GIT_CONFIG_VALUE_0', str(hook))
    monkeypatch.setenv('GIT_DIR', '/wrong')
    prepared(case)
    assert not marker.exists()


def test_existing_snapshot_local_bindings_and_secrets_are_projected_out(case, muse):
    root, plan = case
    ignore = (root/'.museignore').read_bytes()
    (root/'.museignore').write_text('[global]\npatterns=[]\n[force_track]\npaths=[".env.local"]\n')
    (root/'.env.local').write_text('fixture-local-value\n')
    muse(root, 'code', 'add', 'docs/NEXT.md', '.overseer/config.yaml', '.env.local')
    muse(root, 'commit', '-m', 'legacy local binding fixture', '--json')
    (root/'.museignore').write_bytes(ignore)
    # .museignore was not staged above; the approved tracked copy remains equal.
    state = muse_read(root, yaml.safe_load((root/'.overseer/config.yaml').read_bytes())['muse']['runtime']['python'])
    plan['source']['revision'] = state['head']
    result = prepared(case)
    assert {'docs/NEXT.md', '.overseer/config.yaml', '.env.local'} <= set(result['excluded'])
    assert b'local-value' not in mirror.git(Path(plan['target']), 'show', 'HEAD:templates/NEXT.md')


@pytest.mark.parametrize('kind', ['symlink', 'hardlink', 'unlisted_executable', 'missing_executable', 'unsupported_mode'])
def test_supported_modes_refuse_unsupported_source(case, kind):
    root, plan = case
    if kind == 'symlink':
        (root/'app.py').unlink(); (root/'app.py').symlink_to(root/'data.bin')
    elif kind == 'hardlink':
        os.link(root/'app.py', root/'second.py')
    elif kind == 'unlisted_executable': plan['executables'] = []
    elif kind == 'missing_executable': plan['executables'] += ['unknown']
    elif kind == 'unsupported_mode':
        # This host strips setuid/setgid from fixture files; sticky persists.
        (root/'app.py').chmod(0o1600)
        assert (root/'app.py').stat().st_mode & 0o1000
    assert not execute(case)['ok']
    assert not Path(plan['target']).exists()


@pytest.mark.parametrize('stage', ['before_ref', 'after_ref'])
def test_interrupted_prepare_can_retry(case, stage):
    root, plan = case
    if stage == 'before_ref':
        original = mirror.git
        def fail(target, *args, **kw):
            if args[0] == 'update-ref': raise OSError('interrupted before ref update')
            return original(target, *args, **kw)
        with patch.object(mirror, 'git', side_effect=fail): assert not execute(case)['ok']
    else:
        with patch.object(mirror, 'save_record', side_effect=OSError('interrupted record write')):
            result = execute(case)
        assert not result['ok'] and result['export'] == 'prepared'
        commit = result['git_head']
    result = prepared(case)
    if stage == 'after_ref':
        assert result['git_head'] == commit and result['export'] == 'no_change_verified'
    assert json.loads((root/mirror.RECORD).read_bytes())['last_export']['git_sha'] == result['git_head']


@pytest.mark.parametrize('interruption', ['before', 'after'])
def test_interrupted_push_no_change_retry(case, interruption):
    first = prepared(case)
    transport = Delivery(case[1]); transport.fail_push = interruption
    result = execute(case, 'deliver', transport)
    assert result['export'] == 'no_change_verified'
    assert result['ok'] == (interruption == 'after')
    assert result['push'] == ('pending_retry' if interruption == 'before' else 'verified')
    transport.fail_push = None
    transport.calls.clear()
    result = execute(case, 'deliver', transport)
    assert result['ok'] and result['git_head'] == first['git_head']
    assert sum(c[0] == 'push' for c in transport.calls) == (interruption == 'before')
    assert result['pr'] == 'verified'


def test_pr_failure_preserves_push_and_retries_pr_with_repository_context(case):
    prepared(case)
    transport = Delivery(case[1]); transport.fail_pr = True
    result = execute(case, 'deliver', transport)
    assert not result['ok'] and result['push'] == 'verified' and result['pr'] == 'pending_retry'
    transport.fail_pr = False; transport.calls.clear()
    result = execute(case, 'deliver', transport)
    assert result['ok'] and result['push'] == 'already_delivered'
    assert not any(c[0] == 'push' for c in transport.calls)
    pr = next(c for c in transport.calls if c[0] == 'pr')
    assert pr[1] == case[1]['target'] and pr[2]['repository'] == 'fixture/mirror'


@pytest.mark.parametrize('kind', ['unknown_hub', 'unpushed_source', 'remote_drift', 'source_drift', 'target_drift'])
def test_delivery_requires_current_source_and_expected_remote(case, kind):
    prepared(case)
    transport = Delivery(case[1])
    if kind == 'unknown_hub': transport.authoritative = None
    elif kind == 'unpushed_source': transport.authoritative = (case[1]['source']['repo_id'], 'sha256:'+'7'*64)
    elif kind == 'remote_drift': transport.head = '6'*40
    elif kind == 'source_drift': (case[0]/'app.py').write_text('later edit\n')
    elif kind == 'target_drift': (Path(case[1]['target'])/'foreign').write_text('foreign')
    result = execute(case, 'deliver', transport)
    assert not result['ok'] and not any(c[0] in {'push','pr'} for c in transport.calls)


def test_source_change_during_prepare_refuses_ref_and_can_resume(case):
    root, plan = case
    original = mirror.check_source
    calls = 0
    def changing(*args):
        nonlocal calls
        calls += 1
        if calls == 2: (root/'app.py').write_text('changed mid-export\n')
        return original(*args)
    with patch.object(mirror, 'check_source', side_effect=changing): result = execute(case)
    assert not result['ok'] and mirror.head(Path(plan['target'])) == 'absent'
    (root/'app.py').write_text('value = 1\n')
    prepared(case)


def test_add_change_delete_and_no_content_source_commit(case, muse):
    root, plan = case
    first = prepared(case)
    (root/'data.bin').unlink()
    (root/'app.py').write_text('value = 2\n')
    (root/'new.txt').write_text('addition\n')
    muse(root, 'code', 'add', '.')
    muse(root, 'commit', '-m', 'approved second snapshot', '--json')
    config = yaml.safe_load((root/'.overseer/config.yaml').read_bytes())
    plan['source']['revision'] = muse_read(root, config['muse']['runtime']['python'])['head']
    plan['expected_target'] = first['git_head']
    plan['destination']['expected_head'] = first['git_head']
    second = prepared(case)
    paths = mirror.git(Path(plan['target']), 'ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines()
    assert 'data.bin' not in paths and 'new.txt' in paths
    transport = Delivery(plan); transport.fail_push = 'before'
    assert not execute(case, 'deliver', transport)['ok']
    transport.fail_push = None
    assert execute(case, 'deliver', transport)['ok']
    # New approval with the same bytes retains correspondence through an empty commit.
    muse(root, 'commit', '--allow-empty', '-m', 'new approved source; same projection', '--json')
    plan['source']['revision'] = muse_read(root, config['muse']['runtime']['python'])['head']
    plan['expected_target'] = second['git_head']
    plan['destination']['expected_head'] = second['git_head']
    third = prepared(case)
    assert third['export'] == 'mapped_no_content_change' and third['git_head'] != second['git_head']


def test_concurrent_operators_and_cli_plan_pin(case):
    root, plan = case
    path = '.overseer/local/approved-mirror.json'
    (root/'.overseer/local').mkdir(exist_ok=True)
    raw = mirror.packed(plan); (root/path).write_bytes(raw)
    args = [str(KIT/'cli/ok'), '-C', str(root), 'mirror', 'prepare', '--plan-file', path,
            '--expect-plan', digest(raw), '--json']
    workers = [subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
    results = [p.communicate(timeout=30) for p in workers]
    assert sorted(p.returncode for p in workers) in ([0,2], [0,0])
    successes = [json.loads(out) for p,(out,err) in zip(workers,results) if p.returncode == 0]
    assert successes and len({r['git_head'] for r in successes}) == 1
    before = inventory(root), inventory(Path(plan['target']))
    assert command(*args[1:-1], '--expect-plan', '0'*64).returncode != 0
    assert before == (inventory(root), inventory(Path(plan['target'])))


def test_explicit_pair_binding_prevents_second_target(case):
    prepared(case)
    case[1]['target'] += '-other'
    result = execute(case)
    assert not result['ok'] and 'pair_changed' in result['error']
    assert not Path(case[1]['target']).exists()


def test_network_adapter_argv_and_pr_failure_are_explicit(case, tmp_path):
    root, plan = case
    adapter = mirror.NetworkDelivery('/usr/bin/true')
    target = Path(plan['target'])
    calls = []
    def run(_target, *args):
        calls.append((_target, args))
        return b'[]' if args[1] == 'list' else b''
    with patch.object(adapter, 'gh_run', side_effect=run):
        with pytest.raises(Refusal, match='pr_not_verified'):
            adapter.ensure_pr(target, plan['destination'], plan['source'], 'a'*40)
    assert all(c[0] == target and '--repo' in c[1] and 'fixture/mirror' in c[1] for c in calls)
    with patch.object(mirror, 'git') as git:
        adapter.push(target, plan['destination'], 'a'*40)
    args = git.call_args.args
    assert args == (target, 'push', '--porcelain', 'https://github.com/fixture/mirror.git', 'a'*40+':refs/heads/muse-mirror')


def test_target_ref_change_during_export_is_not_overwritten(case):
    root, plan = case
    original = mirror.check_source
    calls = 0
    moved = None
    def changing(*args):
        nonlocal calls, moved
        calls += 1
        result = original(*args)
        if calls == 2:
            target = Path(plan['target'])
            empty = mirror.git(target, 'mktree', data=b'').decode().strip()
            moved = mirror.git(target, 'commit-tree', empty, data=b'foreign operator\n').decode().strip()
            mirror.git(target, 'update-ref', 'refs/heads/muse-mirror', moved)
        return result
    with patch.object(mirror, 'check_source', side_effect=changing): result = execute(case)
    assert not result['ok'] and 'target_changed' in result['error']
    assert mirror.head(Path(plan['target'])) == moved


@pytest.mark.parametrize('kind', ['foreign', 'bytes', 'mode'])
def test_corrupt_export_projection_cannot_update_ref(case, kind):
    root, plan = case
    original = mirror.tree
    def foreign(target, files):
        copy = deepcopy(files)
        if kind == 'foreign': copy['foreign.txt'] = {'data': 'Zm9yZWlnbg==', 'mode': '100644'}
        elif kind == 'bytes': copy['app.py']['data'] = 'Zm9yZWlnbg=='
        elif kind == 'mode': copy['app.py']['mode'] = '100755'
        return original(target, copy)
    with patch.object(mirror, 'tree', side_effect=foreign): result = execute(case)
    assert not result['ok'] and 'tree_' in result['error']
    assert mirror.head(Path(plan['target'])) == 'absent'


def test_missing_git_blob_invalidates_no_change(case):
    prepared(case)
    target = Path(case[1]['target'])
    oid = mirror.git(target, 'rev-parse', 'HEAD:app.py').decode().strip()
    (target/'objects'/oid[:2]/oid[2:]).unlink()
    assert not execute(case)['ok']


def test_remote_change_immediately_before_push_stops_delivery(case):
    prepared(case)
    transport = Delivery(case[1])
    original = transport.remote_head
    calls = 0
    def moving(dest):
        nonlocal calls
        calls += 1
        if calls == 2: transport.head = 'b'*40
        return original(dest)
    transport.remote_head = moving
    result = execute(case, 'deliver', transport)
    assert not result['ok'] and not any(c[0] in {'push','pr'} for c in transport.calls)


def test_mirror_requires_muse_selection_without_importing_it_in_git_mode(tmp_path):
    root = seed(tmp_path/'git-only')
    assert command('-C', root, 'init').returncode == 0
    (root/'.overseer/local').mkdir(exist_ok=True)
    # Complete but Git-only plan: selection is checked before any Muse operation.
    plan = {'schema':1, 'source':dict(repo_id='sha256:'+'1'*64,branch='main',revision='sha256:'+'2'*64,
            hub_url='https://staging.musehub.ai/fixture/source'),
            'destination':dict(url='https://github.com/fixture/mirror.git',repository='fixture/mirror',
            branch='muse-mirror',base='main',expected_head='absent'),
            'target':str((tmp_path/'target').resolve()),'expected_target':'absent','executables':[]}
    raw = mirror.packed(plan); path = '.overseer/local/plan.json'; (root/path).write_bytes(raw)
    r = command('-C', root, 'mirror', 'prepare', '--plan-file', path, '--expect-plan', digest(raw))
    assert r.returncode == 2 and 'explicit_muse_authority' in r.stderr
    assert not Path(plan['target']).exists()


def test_invalid_cli_plan_and_missing_delivery_executable_refuse_cleanly(case):
    root, plan = case
    path = '.overseer/local/plan.json'; (root/'.overseer/local').mkdir(exist_ok=True)
    for value, op in ((dict(plan, source=None), 'prepare'), (plan, 'deliver')):
        raw = mirror.packed(value); (root/path).write_bytes(raw)
        r = command('-C', root, 'mirror', op, '--plan-file', path, '--expect-plan', digest(raw))
        assert r.returncode == 2 and 'Traceback' not in r.stderr, r.stderr


def test_legacy_git_destination_is_not_silently_replaced(case):
    case[1]['destination']['expected_head'] = 'a'*40
    with pytest.raises(Refusal, match='legacy_destination'):
        execute(case)
    assert not Path(case[1]['target']).exists()


@pytest.mark.parametrize('value', [[], None, {'domain':'code','branch_heads':[]}, {'domain':'midi','branch_heads':{}}])
def test_malformed_authority_observation_is_a_refusal(value):
    from io import BytesIO
    adapter = mirror.NetworkDelivery('/usr/bin/true')
    source = {'hub_url':'https://staging.musehub.ai/fixture/source','branch':'main'}
    with patch('urllib.request.build_opener') as opener:
        opener.return_value.open.return_value = BytesIO(json.dumps(value).encode())
        with pytest.raises(Refusal, match='mirror_authority_'):
            adapter.authority(source)


@pytest.mark.parametrize('raw', [b'malformed\n', b'bad\trefs/heads/muse-mirror\n', b'a'*40+b'\trefs/heads/other\n'])
def test_malformed_git_observation_is_a_refusal(raw):
    adapter = mirror.NetworkDelivery('/usr/bin/true')
    with patch.object(mirror, 'git', return_value=raw):
        with pytest.raises(Refusal, match='remote_response_invalid'):
            adapter.remote_head({'url':'https://github.com/fixture/mirror.git','branch':'muse-mirror'})


def test_malformed_pr_url_is_a_retryable_refusal():
    adapter = mirror.NetworkDelivery('/usr/bin/true')
    dest = {'repository':'fixture/mirror','branch':'muse-mirror','base':'main'}
    with patch.object(adapter, 'gh_run', return_value=json.dumps([
            {'url':42,'headRefOid':'a'*40,'isCrossRepository':False}]).encode()):
        with pytest.raises(Refusal, match='pr_not_verified'):
            adapter.ensure_pr(Path('/'), dest, {}, 'a'*40)


@pytest.mark.parametrize('value', [{}, '', None, False, 0, [None], [{}],
    [{'url': None, 'headRefOid': 'a'*40, 'isCrossRepository': False}],
    [{'url': '', 'headRefOid': 'a'*40, 'isCrossRepository': False}],
    [{'url': 'https://github.com/fixture/mirror/pull/1', 'headRefOid': 'a'*40, 'isCrossRepository': 0}],
    [{'url': 'https://github.com/fixture/mirror/pull/1', 'headRefOid': 'invalid', 'isCrossRepository': False}]])
def test_unknown_pr_state_never_creates_a_pr(value):
    adapter = mirror.NetworkDelivery('/usr/bin/true')
    dest = {'repository':'fixture/mirror','branch':'muse-mirror','base':'main'}
    with patch.object(adapter, 'gh_run', return_value=json.dumps(value).encode()) as gh:
        with pytest.raises(Refusal, match='mirror_pr_'):
            adapter.ensure_pr(Path('/'), dest, {}, 'a'*40)
        assert gh.call_count == 1
        assert gh.call_args.args[1:3] == ('pr', 'list')
