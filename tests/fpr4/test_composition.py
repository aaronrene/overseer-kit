"""Combined FPR-4 fixture contracts; event adapters are not native host delivery."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml

from cli import product_bookends, v1
from cli.product_config import OPTIONAL
from cli.v1_io import digest
from tests.v1.conftest import KIT, command, seed, status


def success(result):
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mode,
                                           p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


@pytest.fixture(scope='session')
def composition_muse_python(request):
    value = request.config.getoption('--muse-python', default=None) or os.environ.get('FPR2_MUSE_PYTHON')
    assert value, 'Native composition requires --muse-python or FPR2_MUSE_PYTHON; missing prerequisites must fail'
    path = Path(value)
    assert path.is_absolute() and path.exists()
    probe = subprocess.run([str(path), '-I', '-B', '-c',
        "import hashlib,importlib.metadata,pathlib,muse; "
        "p=pathlib.Path(muse.__file__).resolve().parent; h=hashlib.sha256(); "
        "[h.update(str(f.relative_to(p)).encode()+b'\\0'+f.read_bytes()+b'\\0') for f in sorted(p.rglob('*.py'))]; "
        "print(importlib.metadata.version('muse')); print(h.hexdigest())"],
        capture_output=True, text=True, timeout=20)
    success(probe)
    assert probe.stdout.splitlines() == ['0.2.1rc5', '7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92']
    return path


def native(python, root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('MUSE_', 'GIT_', 'PYTHON'))}
    env.update(PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
               GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
               GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
    return success(subprocess.run([str(python.parent/'muse'), '-C', str(root), *args],
        env=env, capture_output=True, text=True, timeout=30))


def configure_lanes(root):
    path = root/v1.CONFIG
    cfg = yaml.safe_load(path.read_bytes())
    for lane in ('product', 'architecture'):
        cfg['docs']['lanes'].setdefault(lane, {'repo_id': cfg['repo']['id'],
            'roadmap': lane + '/ROADMAP.md', 'handover': lane + '/HANDOVER.md'})
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    return cfg


def publish_args(root, lanes, label, expected=None):
    state = status(root)
    request = {'lanes': {lane: {'model': state['configuration']['context']['model'],
        'action_id': label, 'action_kind': 'implement',
        'prompt': f'{root.name}: accepted {lane} task {label}.\n'} for lane in lanes}}
    local = root/'.overseer/local'
    local.mkdir(exist_ok=True)
    path = local/(label + '.json')
    path.write_text(json.dumps(request))
    args = ['-C', str(root), 'next-write', '--repo-id', state['repository']['id'],
            '--branch', state['branch'], '--expect-next', expected or state['next_sha256'],
            '--batch-file', str(path.relative_to(root))]
    if state['vcs'] == 'muse':
        args.extend(['--vcs', 'muse', '--base-head', state['head']])
    return args


@pytest.mark.parametrize('regime', ['git-only', 'muse-only', 'muse+git-mirror'])
def test_two_active_repositories_lanes_bookends_cas_and_revision(tmp_path, request, regime):
    python = request.getfixturevalue('composition_muse_python') if regime != 'git-only' else None
    roots = []
    for index, default in enumerate(('product', 'architecture')):
        root = tmp_path/f'{regime}-repository-{index}'
        if python:
            root.mkdir()
            native(python, root, 'init', '--domain', 'code', '--json')
        else:
            root = seed(root)
        args = ['-C', root, 'init', '--regime', regime, '--lane', default,
                '--model', f'Fixture model {index}', '--hooks']
        if python:
            args += ['--muse-python', python]
        if regime == 'muse+git-mirror':
            args += ['--muse-staging-remote', f'https://staging.musehub.ai/fixture/source-{index}',
                     '--mirror-branch', f'mirror-{index}']
        success(command(*args))
        configure_lanes(root)
        success(command(*publish_args(root, ('product', 'architecture'), f'INITIAL-{index}')))
        roots.append(root)
    first, second = roots
    states = [status(root) for root in roots]
    assert states[0]['repository']['id'] != states[1]['repository']['id']
    assert states[0]['configuration']['context'] != states[1]['configuration']['context']
    if python:
        assert all(not (root/'.git').exists() for root in roots)
        assert states[0]['source_id'] != states[1]['source_id']
    else:
        assert all(not (root/'.muse').exists() for root in roots)

    before = [snapshot(root) for root in roots]
    for root, foreign in ((first, second), (second, first)):
        unselected = success(command('-C', root, 'next', '--json'))
        assert json.loads(unselected.stdout)['selection_required'] is True
        for lane in ('product', 'architecture'):
            manual = success(command('-C', root, 'next', '--lane', lane))
            assert root.name in manual.stdout and foreign.name not in manual.stdout
            for event, relative in product_bookends.EVENT_PATHS.items():
                payload = json.dumps({'workspace_roots': [str(root)], 'lane': lane, 'event': event})
                event_result = success(command(executable=root/relative, cwd=root, input=payload))
                assert json.loads(event_result.stdout) == {'additional_context': manual.stdout,
                                                         'followup_message': manual.stdout}
                wrong = command(executable=root/relative, cwd=root,
                                input=json.dumps({'workspace_roots': [str(foreign)], 'lane': lane}))
                assert wrong.returncode == 2 and not wrong.stdout
        assert command('-C', root, 'next', '--lane', 'absent').returncode == 2
    assert [snapshot(root) for root in roots] == before

    expected = digest((first/v1.NEXT).read_bytes())
    competing = [publish_args(first, (lane,), 'RACE-'+lane, expected) for lane in ('product', 'architecture')]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda args: command(*args), competing))
    assert sorted(result.returncode for result in results) == [0, 2]
    assert 'stale_write' in next(result.stderr for result in results if result.returncode)
    assert snapshot(second) == before[1]
    success(command(*publish_args(first, ('product', 'architecture'), 'BEFORE-REVISION')))
    if python:
        (first/'app.py').write_text('value = 1\n')
        native(python, first, 'code', 'add', 'app.py')
        native(python, first, 'commit', '-m', 'new native revision', '--json')
    else:
        v1.git(first, 'add', v1.NEXT)
        v1.git(first, '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'exact closing commit')
        for lane in ('product', 'architecture'):
            success(command('-C', first, 'next', '--lane', lane))
        v1.git(first, '-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-m', 'later work')
    for lane in ('product', 'architecture'):
        stale = command('-C', first, 'next', '--lane', lane)
        assert stale.returncode == 2 and 'stale_head' in stale.stderr
    success(command(*publish_args(first, ('product',), 'CURRENT-PRODUCT')))
    collection = json.loads(success(command('-C', first, 'next', '--all-lanes', '--json')).stdout)
    assert collection['lanes']['product']['ok']
    assert not collection['lanes']['architecture']['ok']
    assert snapshot(second) == before[1]


def test_nested_and_linked_git_checkouts_keep_independent_context(tmp_path):
    root = seed(tmp_path/'outer')
    success(command('-C', root, 'init', '--hooks'))
    linked = tmp_path/'linked'
    v1.git(root, 'worktree', 'add', '-b', 'linked', str(linked))
    success(command('-C', linked, 'init', '--lane', 'architecture', '--hooks'))
    nested = seed(root/'nested')
    success(command('-C', nested, 'init', '--model', 'Nested model', '--hooks'))
    roots = [root, linked, nested]
    for checkout in roots:
        configure_lanes(checkout)
        success(command(*publish_args(checkout, ('product', 'architecture'), 'BOUND-CHECKOUT')))
    assert len({status(checkout)['repository']['id'] for checkout in roots}) == 3
    before = [snapshot(checkout) for checkout in roots]
    for checkout in roots:
        success(command('-C', checkout, 'next', '--lane', 'architecture', cwd=nested))
    # An inherited parent launcher may never treat an initialized nested checkout
    # as its own cwd, while explicit target selection continues to work.
    refused = command('next', '--lane', 'architecture', executable=root/'.overseer/bin/ok', cwd=nested)
    assert refused.returncode == 2 and not refused.stdout
    assert [snapshot(checkout) for checkout in roots] == before
    v1.git(linked, '-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-m', 'linked advance')
    assert command('-C', linked, 'next', '--lane', 'architecture').returncode == 2
    success(command('-C', root, 'next', '--lane', 'architecture'))
    success(command('-C', nested, 'next', '--lane', 'architecture'))


def full_optional_settings():
    return {
        'checkpoints': {'enabled': True, 'policy': 'policy/custom.yaml', 'active_manifest': 'docs/manifest.yaml',
                        'progress': 'docs/progress.json', 'orchestrator': 'scripts/check.py', 'allow_hand_verified': False},
        'honesty': {'enabled': True, 'ledger': 'ledger/custom.jsonl', 'roles_file': 'policy/roles.yaml',
                    'require_verdict_on': ['handoff'], 'require_l1_evidence': 'require',
                    'require_verification_evidence': 'warn', 'require_deploy_health': 'off',
                    'require_independent_second_reviewer': 'warn', 'adversarial_freeze': 'suggest',
                    'allow_signed_approval': True, 'ci_reexecutor': 'scripts/reexecute.py', 'require_agent_signature': False},
        'modules': {'governance': {'enabled': True}, 'checkpoints': {'enabled': True}, 'honesty': {'enabled': True}},
        'extensions': [{'id': 'custom', 'schema_version': 7, 'config_path': 'policy/extension.yaml'}],
        'governance_gates': {'remind': False, 'freeze_review': {'required_before_auto': False},
                           'build_verification': {'required_before_done': True}, 'surfaces': ['status']},
        'model_routing': {'enabled': True, 'policy': 'policy/models-custom.yaml'},
        'cost_awareness': {'enabled': True, 'surfaces': ['status']}, 'session_bookends': {'enabled': True},
        'workspace': {'constellation_id': 'one', 'product_order_root': '../workspace', 'manifest': 'workspace.yaml'},
        'hosted_dashboard': {'enabled': True, 'allow_non_loopback': False, 'cors_origins': ['https://example.test'],
            'org_allowlist': ['owner/repo'], 'sources': {'github_contents': True, 'github_meta': True,
            'github_checks_advisory': True, 'musehub_read': True}, 'enumeration_cap': 12,
            'musehub_hosts': ['muse.example.test'], 'musehub_base_url': 'https://muse.example.test', 'max_doc_bytes': 8192},
        'close_ritual': {'enabled': True, 'mode': 'prepare_pr', 'require_paths': ['docs/NEXT.md'],
            'consumer_verify_script': 'scripts/verify.py', 'post_land_sync': {'enabled': False,
            'strategy': 'ff_only', 'require_clean_worktree': True}},
    }


def test_full_legacy_settings_preservation_and_explicit_prompt_acceptance(tmp_path):
    root = seed(tmp_path/'legacy-all-settings')
    (root/'.overseer').mkdir()
    original = yaml.safe_load((KIT/'tests/fixtures/config-two-lane.yaml').read_bytes())
    optional = full_optional_settings()
    assert set(optional) == OPTIONAL
    original.update(optional)
    (root/v1.CONFIG).write_text(yaml.safe_dump(original, sort_keys=False))
    accepted = 'Accepted legacy fixture instruction.\n'
    preserved = {'QUEUE_HANDOVER.md': '### Paste-ready prompt\n```text\n'+accepted+'```\n',
        'QUEUE_ROADMAP.md': '# Owner roadmap\n', 'videos/_active/HANDOVER.md': '# Active handover\n',
        'videos/_active/ROADMAP.md': '# Active roadmap\n', '.cursor/rules/custom.mdc': 'Owner rule\n',
        '.claude/skills/custom/SKILL.md': 'Owner skill\n', 'policy/custom.yaml': 'owner: policy\n',
        'policy/roles.yaml': 'owner: roles\n', 'policy/extension.yaml': 'owner: extension\n',
        'policy/models-custom.yaml': 'owner: model policy\n', 'ledger/custom.jsonl': '{"owner":true}\n'}
    for path, body in preserved.items():
        target = root/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    original_bytes = (root/v1.CONFIG).read_bytes()
    before = snapshot(root)
    dry = success(command('-C', root, 'init', '--migrate', '--dry-run', '--json'))
    assert snapshot(root) == before
    document = json.loads(dry.stdout)
    assert document['plan']['legacy_prompt_drafts'][0]['text'] == accepted
    (root/'plan.json').write_text(dry.stdout)
    args = ['-C', root, 'init', '--migrate', '--apply-plan', 'plan.json', '--expect-plan',
            document['plan_sha256'], '--expect-config', digest(original_bytes), '--json']
    applied = json.loads(success(command(*args)).stdout)
    after = yaml.safe_load((root/v1.CONFIG).read_bytes())
    for field in set(original)-{'overseer_config_version', 'repo', 'docs'}:
        assert after[field] == original[field]
    assert after['schema'] == 3 and after['context']['lane'] == 'queue'
    assert all(lane['repo_id'] == after['repo']['id'] for lane in after['docs']['lanes'].values())
    assert (root/applied['backup']/'files'/v1.CONFIG).read_bytes() == original_bytes
    assert all((root/path).read_text() == body for path, body in preserved.items())
    assert not (root/v1.NEXT).exists()
    assert command('-C', root, 'next', '--lane', 'queue').returncode == 2
    # Only this explicit accepted publication creates canonical authority.
    (root/'accepted.txt').write_text(accepted)
    success(command('-C', root, 'next-write', '--repo-id', after['repo']['id'], '--branch', 'main',
        '--lane', 'queue', '--model', after['context']['model'], '--action-id', 'ACCEPTED-LEGACY',
        '--action-kind', 'implement', '--expect-next', 'absent', '--prompt-file', 'accepted.txt'))
    success(command('-C', root, 'next', '--lane', 'queue'))
    assert command('-C', root, 'next', '--lane', 'active').returncode == 2
    before_sync = snapshot(root)
    success(command('-C', root, 'sync', '--dry-run', '--json'))
    assert snapshot(root) == before_sync
