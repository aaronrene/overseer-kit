"""FPR-4 successor: clean bootstrap, no native Muse or provider/network actions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml

KIT = Path(os.environ.get('FPR4_KIT', Path(__file__).resolve().parents[2]))

PROBE = r'''
import contextlib
import importlib.abc
import importlib.util
import inspect
import io
import json
import pathlib
import runpy
import sys

kit, repo = map(pathlib.Path, sys.argv[1:])
assert sys.flags.isolated and pathlib.Path(sys.prefix).resolve() == kit / '.venv'
assert importlib.util.find_spec('muse') is None
forbidden_imports = []
provider_calls = []
definition_calls = []
network_events = []
processes = []

class NoNativeMuse(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'muse' or fullname.startswith(('muse.', 'adapters.muse_')):
            forbidden_imports.append(fullname)
            raise AssertionError('native Muse import attempted: ' + fullname)

def no_provider_actions(frame, event, arg):
    module = frame.f_globals.get('__name__', '')
    if (event == 'call' and module.startswith('tools.freeze_reviewer.providers')
            and frame.f_code.co_name == '__create_fn__'
            and frame.f_code.co_filename == '<string>'
            and frame.f_back.f_globals.get('__name__') == 'dataclasses'):
        definition_calls.append(module + '.__create_fn__')
        return
    # Class/module definitions are metadata; dataclass compilation is excepted
    # above only when called directly by the standard-library dataclasses module.
    # Every actual provider constructor, factory, method or function is barred.
    if (event == 'call' and module.startswith('tools.freeze_reviewer.providers')
            and frame.f_code.co_flags & inspect.CO_NEWLOCALS):
        provider_calls.append(module + '.' + frame.f_code.co_qualname)
        raise AssertionError('provider action attempted: ' + provider_calls[-1])

def offline_audit(event, args):
    if event.startswith('socket.') and event != 'socket.__new__':
        network_events.append(event)
        raise AssertionError('network operation attempted: ' + event)
    if event == 'subprocess.Popen':
        executable, argv, cwd, env = args
        processes.append(list(argv) if not isinstance(argv, str) else argv)
        assert executable == '/usr/bin/git', ('unexpected executable', executable)
        assert isinstance(argv, (list, tuple)), 'shell process forbidden'
        # Status may inspect only this fixture, using the hardened local Git path.
        assert len(argv) >= 8 and argv[:7] == ['/usr/bin/git', '-c', 'core.fsmonitor=false',
                            '-c', 'core.hooksPath=/dev/null', '-C', str(repo)]
        assert (argv[7] in {'rev-parse', 'status'} or
                argv[7:] == ['symbolic-ref', '--quiet', '--short', 'HEAD']), argv
    if event in {'os.system', 'os.posix_spawn', 'os.posix_spawnp', 'os.exec'}:
        raise AssertionError('unexpected process operation: ' + event)

sys.meta_path.insert(0, NoNativeMuse())
sys.addaudithook(offline_audit)
sys.setprofile(no_provider_actions)
before = set(sys.modules)
assert not any(name.startswith(('cli', 'adapters', 'tools.freeze_reviewer.providers')) for name in before)
sys.argv = [str(kit/'cli/bootstrap.py'), '-C', str(repo), 'status', '--json']
captured = io.StringIO()
with contextlib.redirect_stdout(captured):
    bootstrap = runpy.run_path(str(kit/'cli/bootstrap.py'), run_name='fpr4_bootstrap_probe')
    result = bootstrap['run']()
sys.setprofile(None)
assert result == 0, captured.getvalue()
state = json.loads(captured.getvalue())
assert state['authority'] == 'git'
assert not forbidden_imports and not provider_calls and not network_events
imported = sorted(set(sys.modules) - before)
assert not any(name == 'muse' or name.startswith(('muse.', 'adapters.muse_')) for name in imported)
assert 'tools.freeze_reviewer.engine' not in imported
print(json.dumps({'state': state, 'imported': imported,
    'provider_modules': [n for n in imported if n.startswith('tools.freeze_reviewer.providers')],
    'provider_calls': provider_calls, 'forbidden_imports': forbidden_imports,
    'network_events': network_events, 'processes': processes,
    'definition_calls': definition_calls}, sort_keys=True))
'''


def _inventory(root):
    return {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(),
            p.stat().st_mode & 0o777, p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


@pytest.mark.parametrize('reviewer', ['local', 'api'])
def test_git_full_status_clean_bootstrap_is_offline_without_native_muse(tmp_path, reviewer):
    root = tmp_path/'git-only product'
    root.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0',
               GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
               OVERSEER_REVIEW_API_KEY='fake-fpr4-key',
               OVERSEER_REVIEW_API_URL='https://review.fixture.invalid')
    for args in (['init', '-b', 'main'], ['config', 'user.name', 'Fixture'],
                 ['config', 'user.email', 'fixture@example.invalid'],
                 ['-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-m', 'seed']):
        subprocess.run(['/usr/bin/git', '-C', str(root), *args], env=env,
                       check=True, capture_output=True, text=True)
    initialized = subprocess.run([str(KIT/'cli/ok'), '-C', str(root), 'init'],
                                 env=env, capture_output=True, text=True, timeout=30)
    assert initialized.returncode == 0, initialized.stderr
    config_path = root/'.overseer/config.yaml'
    config = yaml.safe_load(config_path.read_bytes())
    config['freeze_contract']['reviewer'] = dict(mode='agent', provider=reviewer,
                                               model='thinking-high', fallback='human')
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    head = subprocess.check_output(['/usr/bin/git', '-C', str(root), 'rev-parse', 'HEAD'],
                                   env=env, text=True).strip()
    before = _inventory(root)
    completed = subprocess.run([str(KIT/'.venv/bin/python'), '-I', '-B', '-c', PROBE,
                                str(KIT), str(root)], cwd=tmp_path, env=env,
                               capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    payload = json.loads(completed.stdout)
    state = payload['state']
    assert state['repository']['id'] == config['repo']['id']
    assert state['repository']['root'] == str(root)
    assert state['branch'] == 'main'
    assert state['head'] == head
    assert state['substrate']['state'] == 'bound_git'
    assert state['muse_sync']['state'] == 'not_applicable'
    assert state['readiness']['remote'] == 'not_checked_offline'
    for key in ('footprint_integrity', 'footprint_coverage', 'governance', 'governance_gates',
                'model_routing', 'cost_awareness', 'optional_feature_tips',
                'verification_evidence_gate', 'independent_second_reviewer_gate',
                'adversarial_freeze_gate'):
        assert key in state
    assert _inventory(root) == before
    (tmp_path/'probe-result.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
