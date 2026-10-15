"""FPR5-R6: real bound override planning, execution and refusal behavior."""
import json
from pathlib import Path
import shutil

import pytest
import yaml

from tests.v1.conftest import KIT, command, seed
from tests.fpr3.test_commands import settings


@pytest.fixture
def override_repo(tmp_path):
    root = seed(tmp_path / 'override-fixture')
    result = command('-C', root, 'init')
    assert result.returncode == 0, result.stderr
    source = KIT / 'tests/fixtures/checkpoints'
    for directory in ('policy', 'manifests', 'scripts'):
        shutil.copytree(source / directory, root / directory, dirs_exist_ok=True)
    config = yaml.safe_load((source / 'config-checkpoints-enabled.yaml').read_text())
    script = root / 'scripts/override.sh'
    script.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > override-executed\n')
    script.chmod(0o755)
    config['checkpoints']['orchestrator'] = 'scripts/override.sh'
    settings(root, checkpoints=config['checkpoints'], modules=config['modules'])
    return root


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mode, p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}


@pytest.mark.parametrize('selection,mode', [(['--all'], 'all'), (['--step', 'alpha'], 'step'),
                                         (['--through', 'current'], 'through')])
@pytest.mark.parametrize('emit_json', [False, True])
def test_override_preview_returns_plan_without_execution(override_repo, selection, mode, emit_json):
    root = override_repo
    before = snapshot(root)
    flags = selection + ['--manifest', 'manifests/work-unit.yaml', '--policy', 'policy/checkpoints.yaml']
    if emit_json:
        flags.append('--json')
    result = command('-C', root, 'verify-step', *flags, '--dry-run')
    assert result.returncode == 0, result.stderr + result.stdout
    payload = json.loads(result.stdout)
    assert payload['dry_run'] is True and payload['mode'] == mode
    assert payload['steps'] == []  # No invented verified step results.
    plan = payload['plan']
    assert plan['executed'] is False
    assert plan['cwd'] == str(root)
    assert plan['argv'][0] == 'scripts/override.sh'
    assert plan['argv'][1:] == ['--manifest', 'manifests/work-unit.yaml', *selection,
                               '--policy', 'policy/checkpoints.yaml', *(['--json'] if emit_json else [])]
    assert plan['environment'] == {'OVERSEER_REPO_ROOT': str(root)}
    assert not (root / 'override-executed').exists()
    assert snapshot(root) == before


def test_override_explicit_execution_keeps_bound_executor(override_repo):
    result = command('-C', override_repo, 'verify-step', '--all', '--json')
    assert result.returncode == 0, result.stderr + result.stdout
    assert (override_repo / 'override-executed').read_text().splitlines() == ['--all', '--json']


@pytest.mark.parametrize('option', ['--manifest', '--policy'])
@pytest.mark.parametrize('dry_run', [False, True])
def test_override_refuses_escaped_inputs_before_plan_or_execution(override_repo, option, dry_run):
    outside = override_repo.parent / 'outside.yaml'
    outside.write_text('owner: private\n')
    before = snapshot(override_repo)
    result = command('-C', override_repo, 'verify-step', '--all', option, '../outside.yaml',
                     '--json', *(['--dry-run'] if dry_run else []))
    assert result.returncode != 0, result.stdout
    assert not (override_repo / 'override-executed').exists()
    assert snapshot(override_repo) == before


def test_override_preview_rechecks_captured_context(override_repo, monkeypatch):
    from cli.main import ValidatedContext, _arguments
    from cli.product_service import invoke
    from cli.v1_io import Refusal
    from tools.checkpoints import orchestrator
    args = _arguments(['-C', str(override_repo), 'verify-step', '--all', '--dry-run', '--json'])
    context = ValidatedContext.capture(override_repo, args)
    original = orchestrator._is_executable

    def drift(path):
        config = override_repo / '.overseer/config.yaml'
        config.write_bytes(config.read_bytes() + b'\n# changed during planning\n')
        return original(path)

    monkeypatch.setattr(orchestrator, '_is_executable', drift)
    with pytest.raises(Refusal, match='context_changed'):
        invoke(context, args)
    assert not (override_repo / 'override-executed').exists()


def test_override_preview_does_not_delegate_to_executor(override_repo):
    from cli.main import ValidatedContext, _arguments
    from cli.product_service import invoke

    class NoExecution:
        def exec_argv(self, *args, **kwargs):
            pytest.fail('preview invoked an executor')

    args = _arguments(['-C', str(override_repo), 'verify-step', '--all', '--dry-run', '--json'])
    context = ValidatedContext.capture(override_repo, args)
    code, payload = invoke(context, args, script_executor=NoExecution())
    assert code == 0 and payload['plan']['executed'] is False


def test_read_only_script_executor_guard_remains(override_repo):
    from cli.main import ValidatedContext, _arguments
    from cli.product_boundary import engine_boundary
    from cli.v1_io import Refusal
    from tools.checkpoints.executor import SubprocessScriptExecutor
    args = _arguments(['-C', str(override_repo), 'verify-step', '--all', '--dry-run', '--json'])
    context = ValidatedContext.capture(override_repo, args)
    with engine_boundary(context, args, writable=False):
        with pytest.raises(Refusal, match='script_execution_requires_explicit_bound_mutation'):
            SubprocessScriptExecutor().exec_argv(['scripts/override.sh'], cwd=str(override_repo))
    assert not (override_repo / 'override-executed').exists()
