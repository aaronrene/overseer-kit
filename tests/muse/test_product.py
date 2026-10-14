"""FPR-2 normalized configuration and controlled upgrade entrypoints."""
import json
from copy import deepcopy

import pytest
import yaml
from cli import v1
from cli.v1_io import digest
from tests.v1.conftest import command
from tests.v1.test_adoption import adoption_args
from tests.muse.test_handoffs import init, commit, publish, inventory
from tests.muse.test_mirror import case
from tests.fpr2.test_lanes import lanes


def test_upgrade_controlled_plan_preserves_settings_and_never_exports(case):
    root, plan = case
    cfgpath = root/v1.CONFIG
    original = yaml.safe_load(cfgpath.read_bytes())
    body = json.dumps(plan).encode()
    path = '.overseer/local/plan.json'
    (root/path).parent.mkdir(exist_ok=True)
    (root/path).write_bytes(body)
    before = inventory(root)
    args = ['-C', root, 'upgrade-regime', '--plan-file', path, '--expect-plan', digest(body)]
    preview = command(*args, '--dry-run', '--json')
    assert preview.returncode == 0, preview.stderr
    assert inventory(root) == before
    for extra in (['--live-bridge'], ['--live-bridge', '--yes']):
        result = command(*args, *extra)
        assert result.returncode == 2 and 'unsafe_legacy_live_export' in result.stderr
        assert inventory(root) == before
    assert command(*args, '--apply', '--expect-config', digest(cfgpath.read_bytes())).returncode == 0
    updated = yaml.safe_load(cfgpath.read_bytes())
    expected = deepcopy(original); expected['vcs']['regime'] = 'muse+git-mirror'
    expected['vcs']['muse']['staging_remote'] = plan['source']['hub_url']
    expected['vcs']['git']['mirror_branch'] = plan['destination']['branch']
    assert updated == expected
    from pathlib import Path
    assert not Path(plan['target']).exists()
    for p, value in before.items():
        if p != v1.CONFIG:
            assert inventory(root)[p] == value
    for operation in ('prepare', 'verify'):
        result = command('-C', root, 'mirror', operation, '--plan-file', path, '--expect-plan', digest(body))
        assert result.returncode == 0, result.stderr + result.stdout
    result = command('-C', root, 'mirror', 'deliver', '--plan-file', path, '--expect-plan', digest(body))
    assert result.returncode == 2 and 'allow_network' in result.stderr


def test_muse_schema2_migration_preserves_native_binding_and_next(muse_root, muse_python):
    root = muse_root
    init(root, muse_python)
    cfgpath = root/v1.CONFIG
    cfg = yaml.safe_load(cfgpath.read_bytes())
    old = {'schema': 2, 'repo': {k: cfg['repo'][k] for k in ('name', 'id', 'root')},
           'context': cfg['context'], 'runtime': cfg['runtime'], 'vcs': 'muse',
           'muse': cfg['vcs']['muse']['binding']}
    cfgpath.write_text('# bounded Muse config\n' + yaml.safe_dump(old))
    original = cfgpath.read_bytes()
    next_bytes = (root/v1.NEXT).read_bytes()
    dry = command('-C', root, 'init', '--migrate', '--dry-run', '--json')
    assert dry.returncode == 0, dry.stderr
    result = json.loads(dry.stdout)
    assert result['plan']['apply_supported']
    planpath = '.overseer/plan.json'
    (root/planpath).write_text(dry.stdout)
    apply = command('-C', root, 'init', '--migrate', '--apply-plan', planpath,
        '--expect-plan', result['plan_sha256'], '--expect-config', digest(original))
    assert apply.returncode == 0, apply.stderr
    updated = yaml.safe_load(cfgpath.read_bytes())
    assert updated['schema'] == 3 and updated['vcs']['muse']['binding'] == old['muse']
    assert (root/v1.NEXT).read_bytes() == next_bytes
    assert command('-C', root, 'next').returncode == 0


def test_explicit_preserve_tracked_muse_bindings_keeps_history(muse_root, muse_python, muse):
    root = muse_root
    init(root, muse_python)
    ignore = (root/'.museignore').read_bytes()
    (root/'.museignore').write_text('[global]\npatterns=[]\n')
    muse(root, 'code', 'add', 'docs/NEXT.md')
    muse(root, 'commit', '-m', 'tracked local fixture', '--json')
    (root/'.museignore').write_bytes(ignore)
    state = v1.revision(root, yaml.safe_load((root/v1.CONFIG).read_bytes()))
    args = adoption_args(root, vcs='muse', base_head=state.head, tracked_bindings='preserve')
    before = (root/v1.NEXT).read_bytes()
    result = command('-C', root, 'adopt', *args)
    assert result.returncode == 0, result.stderr
    assert (root/v1.NEXT).read_bytes() == before
    assert v1.revision(root, yaml.safe_load((root/v1.CONFIG).read_bytes())).head == state.head
    assert 'docs/NEXT.md' in v1.revision(root, yaml.safe_load((root/v1.CONFIG).read_bytes())).tracked_local


def test_native_lanes_commit_stales_untouched_entry(muse_root, muse_python, muse):
    root = muse_root
    init(root, muse_python)
    lanes(root)
    assert publish(root, lane='architecture').returncode == 0
    assert command('-C', root, 'next', '--lane', 'architecture').returncode == 0
    commit(root, muse)
    assert publish(root, lane='product').returncode == 0
    data = json.loads(command('-C', root, 'next', '--all-lanes', '--json').stdout)
    assert data['lanes']['product']['ok']
    assert 'next_stale_head' in data['lanes']['architecture']['error']


def test_shared_native_stage_is_readonly_and_visible_in_linked_checkout(muse_root, muse_python, muse, tmp_path):
    root = muse_root
    init(root, muse_python)
    commit(root, muse)
    linked = (tmp_path/'linked-stage').resolve()
    muse(root, 'worktree', 'add', 'linked-stage', 'main', '-b', 'linked', '--path', str(linked), '--json')
    init(linked, muse_python)
    (root/'app.py').write_text('shared stage edit\n')
    muse(root, 'code', 'add', 'app.py')
    before = inventory(root), inventory(linked)
    for checkout in (root, linked):
        response = command('-C', checkout, 'status', '--json')
        assert json.loads(response.stdout)['dirty'] is True
    assert before == (inventory(root), inventory(linked))


def test_fresh_mirror_mode_uses_explicit_native_selection(muse_root, muse_python):
    root = muse_root
    result = command('-C', root, 'init', '--regime', 'muse+git-mirror', '--muse-python', muse_python,
        '--muse-staging-remote', 'https://staging.musehub.ai/fixture/source', '--mirror-branch', 'muse-mirror')
    assert result.returncode == 0, result.stderr
    state = json.loads(command('-C', root, 'status', '--json').stdout)
    assert state['vcs'] == 'muse'
    assert state['configuration']['vcs']['regime'] == 'muse+git-mirror'
    assert not (root/'.git').exists()


def test_authority_switch_collection_requires_explicit_reset(muse_root, muse_python):
    import subprocess
    root = muse_root
    init(root, muse_python)
    lanes(root)
    assert publish(root, lane='architecture').returncode == 0
    subprocess.run(['/usr/bin/git', '-C', str(root), 'init', '-b', 'main'], check=True, capture_output=True)
    assert command('-C', root, 'adopt', *adoption_args(root, vcs='git')).returncode == 0
    old = (root/v1.NEXT).read_bytes()
    cfg = yaml.safe_load((root/v1.CONFIG).read_bytes())
    assert cfg['vcs']['muse']['main_branch'] == 'main'
    request = {'lanes': {'product': {'model': cfg['context']['model'], 'action_id': 'NEW-AUTHORITY',
               'action_kind': 'plan', 'prompt': 'Explicit Git task.\n'}}}
    (root/'.overseer/local/batch.json').write_text(json.dumps(request))
    args = ['-C', root, 'next-write', '--repo-id', cfg['repo']['id'], '--branch', 'main',
            '--batch-file', '.overseer/local/batch.json', '--expect-next', digest(old)]
    assert command(*args).returncode == 2
    assert (root/v1.NEXT).read_bytes() == old
    result = command(*args, '--reset-authority')
    assert result.returncode == 0, result.stderr
    data = json.loads(command('-C', root, 'next', '--all-lanes', '--json').stdout)
    assert data['lanes']['product']['ok']
    assert not data['lanes']['architecture']['ok']


@pytest.mark.parametrize('secret', ['fixture.pem', '.envrc', 'fixture.p12'])
def test_forced_native_secret_paths_do_not_enter_projection(case, muse, secret):
    from pathlib import Path
    from cli.v1_revision import muse_read
    from tests.muse.test_mirror import prepared
    from cli import v1_mirror
    root, plan = case
    saved = (root/'.museignore').read_bytes()
    (root/'.museignore').write_text('[global]\npatterns=[]\n[force_track]\npaths=[' + json.dumps(secret) + ']\n')
    (root/secret).write_text('fake-sensitive-fixture-value\n')
    muse(root, 'code', 'add', secret)
    muse(root, 'commit', '-m', 'forced historical secret fixture', '--json')
    (root/'.museignore').write_bytes(saved)
    cfg = yaml.safe_load((root/v1.CONFIG).read_bytes())
    plan['source']['revision'] = muse_read(root, cfg['vcs']['muse']['binding']['runtime']['python'])['head']
    result = prepared(case)
    assert secret in result['excluded']
    assert secret not in v1_mirror.git(Path(plan['target']), 'ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines()


def test_bound_bridge_wrapper_uses_controlled_offline_service(case):
    import subprocess
    from cli import v1_mirror
    root, plan = case
    script = root/'scripts/muse-bridge-deploy.sh'
    script.parent.mkdir()
    script.write_bytes((v1.KIT/'scripts/muse-bridge-deploy.sh').read_bytes())
    script.chmod(0o755)
    assert script.read_bytes() == (v1.KIT/'templates/scripts/muse-bridge-deploy.sh.template').read_bytes()
    path = '.overseer/local/bridge-plan.json'
    (root/path).parent.mkdir(exist_ok=True)
    raw = json.dumps(plan).encode(); (root/path).write_bytes(raw)
    args = ['--plan-file', path, '--expect-plan', digest(raw)]
    for operation in ('prepare', 'verify'):
        # An unrelated cwd cannot select another repository through the wrapper.
        result = subprocess.run([str(script), operation, *args], cwd=v1.KIT,
                                text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr + result.stdout
        assert json.loads(result.stdout)['push'] == 'not_attempted'
    before = inventory(root)
    for argv in (['deliver', *args], ['--live-bridge'], ['--no-push']):
        result = subprocess.run([str(script), *argv], cwd=v1.KIT, text=True, capture_output=True, timeout=30)
        assert result.returncode == 2
        assert inventory(root) == before
