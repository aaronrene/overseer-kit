"""Run the supported matrix from a source installation, without publication.

Git CI needs no Muse installation. Combined CI explicitly supplies a separate
Muse venv and verifies the exact package sources used for integration validation.
"""
from pathlib import Path
import argparse
import subprocess
import sys

KIT = Path(__file__).resolve().parents[2]
MUSE_SOURCE_SHA256 = '7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--muse-python', type=Path)
    parser.add_argument('--junitxml', required=True)
    args = parser.parse_args()
    # Source snapshots and distribution archives must carry hidden CI/policy
    # files. A green suite from an incomplete export is not sufficient.
    for relative in ('.github/workflows/supported-v1.yml', '.gitignore',
                     '.museignore', 'requirements-v1-dev.txt'):
        if not (KIT / relative).is_file():
            parser.error('source file missing: ' + relative)
    if Path(sys.prefix).resolve() != KIT / '.venv':
        parser.error('run with this source installation\'s .venv/bin/python')
    command = [sys.executable, '-m', 'pytest', '-q', 'tests/v1', 'tests/retained']
    if args.muse_python:
        python = args.muse_python
        if (not python.is_absolute() or python.parent.name != 'bin'
                or not (python.parent.parent / 'pyvenv.cfg').is_file()
                or python.parent.parent.resolve() == Path(sys.prefix).resolve()):
            parser.error('--muse-python requires a separate absolute venv executable')
        probe = '''from pathlib import Path
import hashlib, importlib.metadata, sys
import muse
assert sys.prefix != sys.base_prefix
assert importlib.metadata.version('muse') == '0.2.1rc5'
root = Path(muse.__file__).resolve().parent
assert root.is_relative_to(Path(sys.prefix).resolve())
h = hashlib.sha256()
for p in sorted(root.rglob('*.py')):
    h.update(p.relative_to(root).as_posix().encode() + b'\\0' + p.read_bytes() + b'\\0')
assert h.hexdigest() == sys.argv[1], 'Muse package source differs from reviewed rc5'
'''
        subprocess.run([str(python), '-I', '-B', '-c', probe, MUSE_SOURCE_SHA256], check=True)
        command += ['tests/muse', '--muse-python', str(python)]
    command += ['-p', 'no:cacheprovider', '--junitxml', args.junitxml]
    return subprocess.call(command, cwd=KIT)


if __name__ == '__main__':
    raise SystemExit(main())
