"""Divergent legacy history, exact disposition and retry on disposable objects."""
import base64
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from cli import v1_mirror as mirror
from cli import v1_mirror_history as history
from cli.v1_io import Refusal, digest
from cli.v1_revision import muse_read
from tests.muse.test_handoffs import inventory
from tests.muse.test_mirror import case, execute, Delivery


def legacy(case, tmp_path, before=None, unrelated=False):
    root, plan = case
    config = yaml.safe_load((root / '.overseer/config.yaml').read_bytes())
    files = mirror.check_source(root, config, plan)['files']
    before = deepcopy(files) if before is None else before
    if 'legacy-only' not in before and before.keys() == files.keys():
        before['legacy-only'] = {'data': base64.b64encode(b'reviewed removal\n').decode(), 'mode': '100644'}
    repo = tmp_path / 'history.git'
    repo.mkdir()
    mirror.git(repo, 'init', '--bare', '--template=')
    tree = mirror.tree(repo, before)
    def commit(message, parent=None):
        return mirror.git(repo, 'commit-tree', tree, *(['-p', parent] if parent else []),
                          data=(message + '\n').encode()).decode().strip()
    common = commit('common')
    base = commit('main only', None if unrelated else common)
    tip = common
    for i in range(6):
        tip = commit('mirror only ' + str(i), tip)
    for branch, head in (('main', base), ('muse-mirror', tip)):
        mirror.git(repo, 'update-ref', 'refs/heads/' + branch, head)
    bundle = tmp_path / 'approved.bundle'
    mirror.git(repo, 'bundle', 'create', '--version=2', str(bundle), 'refs/heads/main', 'refs/heads/muse-mirror')
    after = {p: {'sha256': digest(base64.b64decode(v['data'])), 'mode': v['mode']} for p, v in files.items()}
    plan['destination']['expected_head'] = tip
    plan['reconciliation'] = {'bundle': str(bundle), 'bundle_sha256': digest(bundle.read_bytes()),
                              'mirror_head': tip, 'base_head': base,
                              'delta': history.delta(history.manifest(repo, tip), after)}
    return repo


@pytest.fixture
def reconciliation(case, tmp_path):
    legacy(case, tmp_path)
    return case


def prepared(case):
    result = execute(case, 'reconcile')
    assert result['ok'], result
    return result


def test_exact_110_path_delta_divergent_histories_modes_and_exclusions(case, muse, muse_python, tmp_path):
    root, plan = case
    for i in range(31):
        (root / f'change-{i}').write_text('approved change\n')
    additions = [f'new-{i}' for i in range(45)] + ['.github/workflows/fixture.yml']
    for path in additions:
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('approved addition\n')
    muse(root, 'code', 'add', '.', '.github/workflows/fixture.yml')
    muse(root, 'commit', '-m', '110 path source', '--json')
    plan['source']['revision'] = muse_read(root, str(muse_python))['head']
    config = yaml.safe_load((root / '.overseer/config.yaml').read_bytes())
    before = deepcopy(mirror.check_source(root, config, plan)['files'])
    for path in additions:
        del before[path]
    for i in range(31):
        before[f'change-{i}']['data'] = base64.b64encode(b'old change\n').decode()
    before['run-tool']['mode'] = '100644'
    for prefix, count in (('.cursor/local-', 24), ('.overseer/legacy-', 8)):
        for i in range(count):
            before[prefix + str(i)] = {'data': base64.b64encode(b'old local binding\n').decode(), 'mode': '100644'}
    legacy(case, tmp_path, before)
    delta = plan['reconciliation']['delta']
    assert len(delta) == 110
    assert sum(v['before'] is None for v in delta.values()) == 46
    assert sum(v['after'] is None for v in delta.values()) == 32
    first = prepared(case)
    target = Path(plan['target'])
    parents = mirror.expected_parents(plan)
    assert mirror.git(target, 'show', '-s', '--format=%P', 'HEAD').decode().strip().split() == parents
    for parent in parents:
        mirror.git(target, 'merge-base', '--is-ancestor', parent, first['git_head'])
    assert mirror.git(target, 'rev-list', '--left-right', '--count', parents[1] + '...' + parents[0]) == b'1\t6\n'
    paths = mirror.git(target, 'ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines()
    assert not any(p.startswith(('.cursor/', '.overseer/')) for p in paths)
    assert mirror.git(target, 'ls-tree', 'HEAD', 'run-tool').startswith(b'100755 ')
    before_retry = inventory(root), inventory(target)
    assert prepared(case)['git_head'] == first['git_head']
    assert execute(case, 'verify')['ok']
    assert (inventory(root), inventory(target)) == before_retry


@pytest.mark.parametrize('change', ['mirror_head', 'base_head', 'bundle_hash', 'bundle_ref', 'corrupt_pack',
                                  'missing_delta', 'changed_delta', 'foreign_target', 'empty_target'])
def test_reconciliation_refuses_unreviewed_inputs(reconciliation, change):
    root, plan = reconciliation
    r = plan['reconciliation']
    if change in ('mirror_head', 'base_head'):
        r[change] = 'a' * 40
        plan['destination']['expected_head'] = r['mirror_head']
    elif change == 'bundle_hash': r['bundle_sha256'] = 'a' * 64
    elif change in ('bundle_ref', 'corrupt_pack'):
        path = Path(r['bundle'])
        data = path.read_bytes()
        data = data.replace(b'refs/heads/main', b'refs/heads/other') if change == 'bundle_ref' else data[:-10]
        path.write_bytes(data); r['bundle_sha256'] = digest(data)
    elif change == 'missing_delta': r['delta'] = {}
    elif change == 'changed_delta': next(iter(r['delta'].values()))['before'] = 'a' * 64
    else:
        Path(plan['target']).mkdir()
        if change == 'foreign_target': (Path(plan['target']) / 'keep').write_text('original')
    before = inventory(root)
    assert not execute(reconciliation, 'reconcile')['ok']
    assert inventory(root) == before
    if change not in ('foreign_target', 'empty_target'):
        assert not Path(plan['target']).exists()


def test_unrelated_history_is_refused(case, tmp_path):
    legacy(case, tmp_path, unrelated=True)
    result = execute(case, 'reconcile')
    assert not result['ok'] and result['error'] == 'mirror_history_unrelated_heads'
    assert not Path(case[1]['target']).exists()


def test_reconciliation_requires_explicit_operation(reconciliation):
    assert not execute(reconciliation, 'prepare')['ok']
    assert not Path(reconciliation[1]['target']).exists()
    reconciliation[1]['destination']['expected_base'] = 'a' * 40
    with pytest.raises(Refusal, match='reconciliation_head_mismatch'):
        execute(reconciliation, 'reconcile')
    assert not Path(reconciliation[1]['target']).exists()


@pytest.mark.parametrize('point', ['import', 'before_ref', 'after_ref'])
def test_interrupted_reconciliation_recovers_exact_correspondence(reconciliation, point):
    if point == 'import':
        with patch.object(history, 'verify_history', side_effect=OSError('fixture interruption')):
            assert not execute(reconciliation, 'reconcile')['ok']
        assert not Path(reconciliation[1]['target']).exists()
    elif point == 'before_ref':
        original = mirror.git
        def fail(target, *args, **kwargs):
            if args[0] == 'update-ref': raise OSError('fixture interruption')
            return original(target, *args, **kwargs)
        with patch.object(mirror, 'git', side_effect=fail):
            assert not execute(reconciliation, 'reconcile')['ok']
    else:
        with patch.object(mirror, 'save_record', side_effect=OSError('fixture interruption')):
            interrupted = execute(reconciliation, 'reconcile')
        assert not interrupted['ok']
    result = prepared(reconciliation)
    if point == 'after_ref': assert result['git_head'] == interrupted['git_head']
    assert prepared(reconciliation)['git_head'] == result['git_head']


class LegacyDelivery(Delivery):
    def __init__(self, plan):
        super().__init__(plan)
        self.base = plan['reconciliation']['base_head']

    def remote_head(self, dest):
        if dest['branch'] == dest['base']:
            self.calls.append(('base', deepcopy(dest)))
            return self.base
        return super().remote_head(dest)


@pytest.mark.parametrize('point', ['initial', 'before_push', 'after_push'])
def test_live_base_drift_stops_write_or_reports_partial_result(reconciliation, point):
    prepared(reconciliation)
    transport = LegacyDelivery(reconciliation[1])
    original = transport.remote_head
    count = 0
    def changing(dest):
        nonlocal count
        if dest['branch'] == dest['base']:
            count += 1
            if count == {'initial': 1, 'before_push': 2, 'after_push': 3}[point]:
                transport.base = 'a' * 40
        return original(dest)
    transport.remote_head = changing
    result = execute(reconciliation, 'deliver', transport)
    assert not result['ok'] and result['error'] == 'mirror_remote_base_drift'
    assert not any(c[0] == 'pr' for c in transport.calls)
    assert sum(c[0] == 'push' for c in transport.calls) == (point == 'after_push')


def test_reconciled_delivery_retry_and_later_single_parent(reconciliation, muse, muse_python):
    root, plan = reconciliation
    first = prepared(reconciliation)
    transport = LegacyDelivery(plan)
    transport.fail_push = 'before'
    assert execute(reconciliation, 'deliver', transport)['push'] == 'pending_retry'
    transport.fail_push = 'after'
    assert execute(reconciliation, 'deliver', transport)['push'] == 'verified'
    transport.calls.clear()
    assert execute(reconciliation, 'deliver', transport)['push'] == 'already_delivered'
    assert not any(c[0] == 'push' for c in transport.calls)
    muse(root, 'commit', '--allow-empty', '-m', 'later source', '--json')
    plan['source']['revision'] = muse_read(root, str(muse_python))['head']
    plan['expected_target'] = plan['destination']['expected_head'] = first['git_head']
    # A later reviewed plan can pin an advanced PR base without rewriting the
    # immutable origin binding or adding a second parent to subsequent exports.
    plan['destination']['expected_base'] = first['git_head']
    later = execute(reconciliation)
    assert later['ok'], later
    assert mirror.git(Path(plan['target']), 'show', '-s', '--format=%P', later['git_head']).decode().strip() == first['git_head']
    transport = LegacyDelivery(plan)
    assert not execute(reconciliation, 'deliver', transport)['ok']
    assert not any(c[0] in ('push', 'pr') for c in transport.calls)
    transport.base = first['git_head']
    assert execute(reconciliation, 'deliver', transport)['ok']


@pytest.mark.parametrize('kind', ['swapped', 'missing', 'extra'])
def test_correspondence_refuses_substituted_parents(reconciliation, kind):
    result = prepared(reconciliation)
    plan = reconciliation[1]
    target = Path(plan['target'])
    parents = mirror.expected_parents(plan)
    parents = parents[::-1] if kind == 'swapped' else parents[:1] if kind == 'missing' else parents + [
        mirror.git(target, 'merge-base', *parents).decode().strip()]
    tree = mirror.git(target, 'rev-parse', 'HEAD^{tree}').decode().strip()
    message = mirror.git(target, 'cat-file', 'commit', 'HEAD').split(b'\n\n', 1)[1]
    commit = mirror.git(target, 'commit-tree', tree, *[v for p in parents for v in ('-p', p)], data=message).decode().strip()
    mirror.git(target, 'update-ref', 'refs/heads/muse-mirror', commit, result['git_head'])
    refused = execute(reconciliation, 'verify')
    assert not refused['ok'] and refused['error'] == 'mirror_commit_parent_mismatch'


def test_changed_base_tree_is_not_an_automatic_merge(reconciliation, tmp_path):
    root, plan = reconciliation
    repo = tmp_path / 'history.git'
    empty = mirror.git(repo, 'mktree', data=b'').decode().strip()
    r = plan['reconciliation']
    base = mirror.git(repo, 'commit-tree', empty, '-p', r['base_head'], data=b'different base\n').decode().strip()
    mirror.git(repo, 'update-ref', 'refs/heads/main', base)
    bundle = Path(r['bundle'])
    mirror.git(repo, 'bundle', 'create', '--version=2', str(bundle), 'refs/heads/main', 'refs/heads/muse-mirror')
    r.update(base_head=base, bundle_sha256=digest(bundle.read_bytes()))
    result = execute(reconciliation, 'reconcile')
    assert not result['ok'] and result['error'] == 'mirror_history_base_tree_differs'
    assert not Path(plan['target']).exists()


@pytest.mark.parametrize('path', ['config', 'overseer-mirror.json'])
def test_executable_target_metadata_refused(reconciliation, path):
    prepared(reconciliation)
    target = Path(reconciliation[1]['target'])
    (target / path).chmod(0o755)
    before = inventory(target)
    result = execute(reconciliation, 'verify')
    assert not result['ok'] and result['error'] == 'mirror_target_unsafe_path'
    assert inventory(target) == before
