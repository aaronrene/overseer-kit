"""Record a fresh, offline FPR-5 author check without changing historical evidence."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cli.v1 import runtime, runtime_files


def boundary():
    return {
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'runtime': runtime(),
        'runtime_files': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                          for p in runtime_files()},
        'python': sys.version, 'executable': sys.executable, 'prefix': sys.prefix,
        'dependencies': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('selection', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    output = ROOT / 'docs/validation/fpr5-repairs' / args.name
    output.mkdir(parents=True, exist_ok=False)
    fixtures = Path(tempfile.mkdtemp(prefix='overseer-fpr5-repair-', dir='/private/tmp'))
    selection = args.selection[1:] if args.selection[:1] == ['--'] else args.selection
    argv = [sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
            '--basetemp', str(fixtures / 'tests'), '--junitxml', str(output / 'results.xml'), *selection]
    overrides = {'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
                 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_OPTIONAL_LOCKS': '0',
                 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'}
    env = dict(os.environ, **overrides)
    for key in ('PYTEST_ADDOPTS', 'PYTEST_PLUGINS'):
        env.pop(key, None)
    record = {'kind': 'FPR-5 repair author validation, not independent adjudication',
              'argv': argv, 'cwd': str(ROOT), 'environment_overrides': overrides,
              'before': boundary()}
    (output / 'command.json').write_text(json.dumps(record, indent=2) + '\n')
    started = time.monotonic()
    with (output / 'results.log').open('w') as log:
        result = subprocess.run(argv, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    record.update(exit_code=result.returncode, seconds=time.monotonic()-started, after=boundary())
    (output / 'command.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'exit_code': result.returncode,
                      'seconds': record['seconds']}))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
