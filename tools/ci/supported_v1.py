"""Run the supported matrix from a source installation, without publication.

Git CI needs no Muse installation. Combined CI explicitly supplies a separate
Muse venv. Combined CI accepts only an exact (version, digest) pair from
cli/v1_revision.py:MUSE_RUNTIMES.
"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

KIT = Path(__file__).resolve().parents[2]
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))
from cli.v1_io import Refusal
from cli.v1_revision import MUSE_RUNTIMES, bounded_run

COMPATIBILITY_TESTS = (
    'tests/integration/test_legacy_migration_compat.py',
    'tests/integration/test_historical_prompt_migration.py',
)
PROBE_TIMEOUT = 60
PROBE_LIMIT = 4096
PROBE = '''import hashlib, importlib.metadata, json, sys
from pathlib import Path
assert sys.prefix != sys.base_prefix
import muse
root = Path(muse.__file__).resolve().parent
assert root.is_relative_to(Path(sys.prefix).resolve())
h = hashlib.sha256()
for p in sorted(root.rglob('*.py')):
    h.update(p.relative_to(root).as_posix().encode() + b'\\0' + p.read_bytes() + b'\\0')
print(json.dumps({'version': importlib.metadata.version('muse'), 'sha256': h.hexdigest()}))
'''
_VERSION = re.compile(r'[0-9A-Za-z.+-]{1,64}\Z')
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def muse_runtime(python):
    """Return (version, sha256) only for an exact reviewed Muse pair.

    Raises ValueError with a fixed reason when the probe fails, the output is
    malformed, or the pair is not in MUSE_RUNTIMES.
    """
    env = {k: v for k, v in os.environ.items()
           if not k.startswith('PYTHON') and not k.startswith('MUSE_')}
    try:
        proc = bounded_run([str(python), '-I', '-B', '-c', PROBE], cwd='/', env=env,
                           timeout=PROBE_TIMEOUT, limit=PROBE_LIMIT)
    except (Refusal, OSError, subprocess.SubprocessError):
        raise ValueError('muse_probe_failed') from None
    if proc.returncode != 0:
        raise ValueError('muse_probe_failed')
    raw = proc.stdout
    try:
        if (not raw.isascii() or raw.count(b'\n') != 1 or not raw.endswith(b'\n')):
            raise ValueError('muse_probe_output_invalid')
        payload = json.loads(raw.decode('ascii'))
        if (not isinstance(payload, dict) or set(payload) != {'version', 'sha256'}
                or not isinstance(payload['version'], str)
                or not isinstance(payload['sha256'], str)
                or not _VERSION.fullmatch(payload['version'])
                or not _SHA256.fullmatch(payload['sha256'])):
            raise ValueError('muse_probe_output_invalid')
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        if str(exc) == 'muse_probe_output_invalid':
            raise
        raise ValueError('muse_probe_output_invalid') from None
    version, sha256 = payload['version'], payload['sha256']
    if version not in MUSE_RUNTIMES:
        raise ValueError('muse_version_unreviewed: ' + version)
    if MUSE_RUNTIMES[version] != sha256:
        raise ValueError('muse_source_digest_unreviewed: ' + version)
    return version, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--muse-python', type=Path)
    parser.add_argument('--junitxml', required=True)
    args = parser.parse_args()
    # Source snapshots and distribution archives must carry hidden CI/policy
    # files. A green suite from an incomplete export is not sufficient.
    required = ('.github/workflows/supported-v1.yml', '.gitignore',
                '.museignore', 'requirements-v1-dev.txt', *COMPATIBILITY_TESTS)
    for relative in required:
        if not (KIT / relative).is_file():
            parser.error('source file missing: ' + relative)
    if Path(sys.prefix).resolve() != KIT / '.venv':
        parser.error('run with this source installation\'s .venv/bin/python')
    command = [sys.executable, '-m', 'pytest', '-q', 'tests/v1', 'tests/fpr1', 'tests/fpr2', 'tests/fpr3']
    command += json.loads((KIT / 'docs/validation/fpr3/retained-selection.json').read_text())
    command += list(COMPATIBILITY_TESTS)
    if args.muse_python:
        python = args.muse_python
        if (not python.is_absolute() or python.parent.name != 'bin'
                or not (python.parent.parent / 'pyvenv.cfg').is_file()
                or python.parent.parent.resolve() == Path(sys.prefix).resolve()):
            parser.error('--muse-python requires a separate absolute venv executable')
        try:
            version, source = muse_runtime(python)
        except ValueError as exc:
            parser.error(str(exc))
        print(f'supported_v1: reviewed Muse {version} {source}', file=sys.stderr)
        command += ['tests/muse', '--muse-python', str(python)]
    command += ['-p', 'no:cacheprovider', '--basetemp', tempfile.mkdtemp(prefix='overseer-ci-'),
                '--junitxml', args.junitxml]
    return subprocess.call(command, cwd=KIT)


if __name__ == '__main__':
    raise SystemExit(main())
