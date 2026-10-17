"""Full-product successor to the preserved YAML-only bounded-install fixture."""
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import subprocess
import sysconfig
import venv

from cli import v1
from tests.v1.conftest import KIT, command, seed


def test_fresh_full_dependency_git_install_without_muse(tmp_path):
    installation = tmp_path/'standalone-kit'
    for relative in v1.RUNTIME_FILES:
        target = installation/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(KIT/relative, target)
    requirement_bytes = (KIT/'requirements-v1.txt').read_bytes()
    (installation/'requirements-v1.txt').write_bytes(requirement_bytes)
    pins = {}
    for line in requirement_bytes.decode().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([^\s;]+)', line)
        assert match, 'Standalone fixture requires explicit exact dependency pins'
        name, version = match.groups()
        assert name not in pins
        pins[name] = version
    assert pins == {'PyYAML': '6.0.3', 'cryptography': '49.0.0', 'cffi': '2.1.0', 'pycparser': '3.0'}

    venv.EnvBuilder(with_pip=False, symlinks=True).create(installation/'.venv')
    python = installation/'.venv/bin/python3'
    destination_site = Path(subprocess.check_output([str(python), '-I', '-B', '-c',
        'import sysconfig; print(sysconfig.get_paths()["purelib"])'], text=True).strip())
    source_site = Path(sysconfig.get_paths()['purelib']).resolve()
    assert source_site != destination_site.resolve()
    # Provision precisely the installed distributions named by the checked-in
    # pins, including native extensions and metadata, with no resolver/network.
    # This is an offline same-interpreter fixture, not a wheel-portability claim.
    for name, version in pins.items():
        distribution = importlib.metadata.distribution(name)
        assert distribution.version == version
        assert distribution.files
        for relative in distribution.files:
            relative = Path(str(relative))
            assert not relative.is_absolute() and '..' not in relative.parts
            source = Path(distribution.locate_file(relative)).resolve()
            assert source.is_relative_to(source_site)
            if '__pycache__' in relative.parts or relative.suffix == '.pyc':
                continue
            assert source.is_file()
            target = destination_site/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    probe_script = '''
import importlib.metadata, importlib.util, json, pathlib, sys, sysconfig
import yaml, cryptography, cffi, pycparser
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
site = pathlib.Path(sysconfig.get_paths()['purelib']).resolve()
assert importlib.util.find_spec('muse') is None
assert importlib.util.find_spec('pip') is None
assert importlib.util.find_spec('pytest') is None
for module in (yaml, cryptography, cffi, pycparser):
    assert pathlib.Path(module.__file__).resolve().is_relative_to(site)
key = Ed25519PrivateKey.generate()
key.public_key().verify(key.sign(b'isolated fixture'), b'isolated fixture')
print(json.dumps({'versions': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
                  'site': str(site), 'paths': sys.path}))
'''
    probe = subprocess.run([str(python), '-I', '-B', '-c', probe_script],
        cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert probe.returncode == 0, probe.stderr
    environment = json.loads(probe.stdout)
    assert environment['versions'] == pins
    assert not any(str(source_site) in path or str(KIT) in path for path in environment['paths'])

    root = seed(tmp_path/'standalone-project')
    launcher = installation/'cli/ok'
    env = {'PATH': '/usr/bin:/bin', 'PYTHONPATH': '/unavailable/ambient/packages',
           'MUSE_PYTHON': '/unavailable/muse/python', 'MUSE_REPO_ROOT': '/unavailable/muse'}
    initialized = command('-C', root, 'init', '--vcs', 'git', executable=launcher, env=env)
    assert initialized.returncode == 0, initialized.stdout + initialized.stderr
    assert not (root/'.muse').exists()
    config_before = (root/v1.CONFIG).read_bytes()
    next_before = (root/v1.NEXT).read_bytes()
    for executable in (launcher, root/'.overseer/bin/ok'):
        for operation in ('status', 'next', 'sync'):
            result = command('-C', root, operation, '--json', executable=executable, env=env)
            assert result.returncode == 0, result.stdout + result.stderr
            report = json.loads(result.stdout)
            if operation in ('status', 'next'):
                assert report['vcs'] == 'git'
                assert report['runtime']['root'] == str(installation)
                assert report['repository']['root'] == str(root)
    assert (root/v1.CONFIG).read_bytes() == config_before
    assert (root/v1.NEXT).read_bytes() == next_before
    assert (installation/'requirements-v1.txt').read_bytes() == requirement_bytes
