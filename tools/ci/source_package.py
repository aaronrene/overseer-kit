"""Deterministic portable source archives; local preparation, never publication."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = 'SOURCE-MANIFEST.json'
DIRECTORIES = {'adapters', 'cli', 'tools', 'cursor', 'policy', 'templates', 'desktop', 'scripts', 'tests', 'docs', '.github'}
FILES = {'VERSION', 'README.md', 'LICENSE', 'LICENSE.md', 'SECURITY.md', 'AGENTS.md', 'pyproject.toml',
         'requirements-v1.txt', 'requirements-v1-dev.txt', '.gitignore', '.museignore'}


def eligible(relative):
    p = Path(relative)
    if not p.parts or p.is_absolute() or '..' in p.parts or str(p) != relative:
        return False
    if p.parts[0] not in DIRECTORIES and relative not in FILES:
        return False
    if relative == 'docs/NEXT.md':
        return False
    if any(x in {'.git', '.muse', '.overseer', '.venv', '__pycache__', 'node_modules', 'target', 'resources', '.pytest_cache'}
           or x.endswith('.egg-info') for x in p.parts):
        return False
    if p.name.startswith('.env') or p.suffix.lower() in {'.pyc', '.pyo', '.pem', '.key', '.p12', '.pfx', '.p8'}:
        return False
    if p.name == 'apple-api-key.json' or 'private' in p.name.lower():
        return False
    return True


def source_files(root):
    if (root / MANIFEST).is_file() and not (root / '.git').exists():
        names = list(json.loads((root / MANIFEST).read_text())['files'])
    else:
        result = subprocess.run(['/usr/bin/git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                                check=True, capture_output=True)
        names = result.stdout.decode().split('\0')
    result = {}
    for name in sorted(set(names)):
        if not eligible(name):
            continue
        p = root / name
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents if parent != root.parent):
            raise ValueError('source symlink: ' + name)
        if not p.is_file() or p.stat().st_nlink != 1:
            raise ValueError('source file missing or not regular: ' + name)
        result[name] = p
    required = ['cli/ok', 'cli/bootstrap.py', 'tools/app/static/index.html',
                'tools/hosted_dashboard/static/index.html', '.github/workflows/supported-v1.yml',
                'tools/ci/muse_artifact.py', 'cursor/skills/print-next/SKILL.md', 'templates/ROADMAP.template.md']
    for name in required:
        if name not in result:
            raise ValueError('required source missing: ' + name)
    return result


def manifest(root):
    return {'schema': 1, 'version': (root / 'VERSION').read_text().strip(),
            'kind': 'local-source-preparation', 'release_ready': False,
            'files': {name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                             'mode': '0755' if p.stat().st_mode & 0o111 else '0644', 'size': p.stat().st_size}
                      for name, p in source_files(root).items()}}


def build(root, output):
    root, output = root.resolve(strict=True), output.absolute()
    if output.exists() or output.is_symlink() or output.is_relative_to(root):
        raise ValueError('output must be a new path outside source')
    m = manifest(root)
    payload = json.dumps(m, indent=2, sort_keys=True).encode() + b'\n'
    with output.open('xb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w') as tar:
        for name in sorted([*m['files'], MANIFEST]):
            data = payload if name == MANIFEST else (root / name).read_bytes()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644 if name == MANIFEST else int(m['files'][name]['mode'], 8)
            info.mtime = info.uid = info.gid = 0
            info.uname = info.gname = ''
            tar.addfile(info, io.BytesIO(data))
    verify(output)
    return {'archive': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'manifest_sha256': hashlib.sha256(payload).hexdigest(), 'files': len(m['files'])}


def verify(archive):
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        if len(members) > 20000 or sum(m.size for m in members) > 256 * 1024 * 1024:
            raise ValueError('archive bounds exceeded')
        names = [m.name for m in members]
        if len(names) != len(set(names)) or MANIFEST not in names:
            raise ValueError('duplicate paths or absent manifest')
        if any(not m.isfile() or m.mode not in (0o644, 0o755) or (m.name != MANIFEST and not eligible(m.name)) or m.size > 32 * 1024 * 1024 for m in members):
            raise ValueError('unsafe archive member')
        m = json.load(tar.extractfile(MANIFEST))
        if m.get('schema') != 1 or set(names) != set(m['files']) | {MANIFEST}:
            raise ValueError('manifest membership mismatch')
        for entry in members:
            if entry.name == MANIFEST:
                continue
            row = m['files'][entry.name]
            if (entry.mode != int(row['mode'], 8) or entry.size != row['size'] or
                    hashlib.sha256(tar.extractfile(entry).read()).hexdigest() != row['sha256']):
                raise ValueError('manifest mismatch: ' + entry.name)
    return m


def unpack(archive, destination):
    verify(archive)
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination must be new')
    destination.mkdir(parents=True)
    with tarfile.open(archive, 'r:gz') as tar:
        tar.extractall(destination, filter='data')


def verify_tree(directory):
    m = json.loads((directory / MANIFEST).read_text())
    for name, row in m['files'].items():
        if not eligible(name):
            raise ValueError('unsafe resource path')
        p = directory / name
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents) or not p.is_file() or p.stat().st_nlink != 1:
            raise ValueError('invalid resource file: ' + name)
        if hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256'] or (p.stat().st_mode & 0o777) != int(row['mode'], 8):
            raise ValueError('resource identity mismatch: ' + name)
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    b = sub.add_parser('build'); b.add_argument('--output', type=Path, required=True)
    v = sub.add_parser('verify'); v.add_argument('--archive', type=Path, required=True)
    u = sub.add_parser('unpack'); u.add_argument('--archive', type=Path, required=True); u.add_argument('--destination', type=Path, required=True)
    t = sub.add_parser('verify-tree'); t.add_argument('--directory', type=Path, required=True)
    a = p.parse_args()
    if a.operation == 'build':
        print(json.dumps(build(ROOT, a.output)))
    elif a.operation == 'verify':
        print(json.dumps({'ok': True, 'files': len(verify(a.archive)['files'])}))
    elif a.operation == 'verify-tree':
        print(json.dumps({'ok': True, 'files': len(verify_tree(a.directory)['files'])}))
    else:
        unpack(a.archive, a.destination)
        print(json.dumps({'ok': True, 'destination': str(a.destination)}))


if __name__ == '__main__':
    main()
