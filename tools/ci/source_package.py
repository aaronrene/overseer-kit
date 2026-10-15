"""Deterministic portable source archives; local preparation, never publication."""
from __future__ import annotations
import argparse
import base64
import gzip
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import sysconfig
import tarfile
import venv

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = 'SOURCE-MANIFEST.json'
RUNTIME_MANIFEST = 'RESOURCE-RUNTIME.json'
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


def _file_row(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('invalid resource file: ' + str(path))
    return {'kind': 'file', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'size': info.st_size, 'mode': f'{stat.S_IMODE(info.st_mode):04o}'}


def _parents(names):
    return {parent.as_posix() for name in names for parent in Path(name).parents
            if parent != Path('.')}


def _members(directory):
    """Enumerate the complete packaged tree without following any links."""
    result = {}
    pending = [directory]
    while pending:
        for path in pending.pop().iterdir():
            name = path.relative_to(directory).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                result[name] = {'kind': 'directory'}
                pending.append(path)
            elif stat.S_ISLNK(mode):
                result[name] = {'kind': 'symlink', 'target': os.readlink(path)}
            elif stat.S_ISREG(mode):
                result[name] = _file_row(path)
            else:
                raise ValueError('special resource entry: ' + name)
    return result


def _local_dependencies(directory):
    """Resolve exact installed prerequisites, never arbitrary runtime extras.

    Verification deliberately requires the same pinned local prerequisites as
    provisioning. A resource inventory cannot approve new dependency paths.
    """
    pins = {}
    for line in (directory / 'requirements-v1.txt').read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([^\s;]+)', line.strip())
        if not match or match[1].lower() in {name.lower() for name in pins}:
            raise ValueError('resource dependencies require unique exact pins')
        pins[match[1]] = match[2]
    if not pins:
        raise ValueError('resource dependencies missing')
    site = Path(sysconfig.get_path('purelib')).resolve(strict=True)
    relative_site = f'.venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages'
    files = {}
    for name, version in pins.items():
        distribution = importlib.metadata.distribution(name)
        if distribution.version != version or not distribution.files:
            raise ValueError('pinned local prerequisite missing: ' + name)
        for item in distribution.files:
            relative = Path(str(item))
            if '__pycache__' in relative.parts or relative.suffix == '.pyc':
                continue
            if (relative.is_absolute() or '..' in relative.parts or
                    any(part.startswith('.') for part in relative.parts) or
                    relative.suffix.lower() in {'.pth', '.pem', '.key', '.p12', '.pfx', '.p8'}):
                raise ValueError('unsafe local dependency entry: ' + str(item))
            original = Path(distribution.locate_file(item))
            if (not original.resolve(strict=True).is_relative_to(site) or
                    any(parent.is_symlink() for parent in original.parents)):
                raise ValueError('local dependency outside installation: ' + str(item))
            row = _file_row(original)
            if item.hash is not None:
                encoded = base64.urlsafe_b64encode(bytes.fromhex(row['sha256'])).rstrip(b'=').decode()
                if item.hash.mode != 'sha256' or item.hash.value != encoded or item.size != row['size']:
                    raise ValueError('local prerequisite RECORD mismatch: ' + str(item))
            elif not (relative.name == 'RECORD' and relative.parent.name.endswith('.dist-info')):
                raise ValueError('unrecorded local prerequisite: ' + str(item))
            row['mode'] = '0755' if int(row['mode'], 8) & 0o111 else '0644'
            target = relative_site + '/' + relative.as_posix()
            if target in files:
                raise ValueError('overlapping local dependencies: ' + target)
            files[target] = (original, row)
    return pins, files


def _interpreter():
    executable = Path(sys._base_executable).resolve(strict=True)
    return {'path': str(executable), 'sha256': hashlib.sha256(executable.read_bytes()).hexdigest(),
            'version': list(sys.version_info[:3])}


def _python_links():
    return {f'.venv/bin/{name}' for name in
            ('python', 'python3', f'python{sys.version_info.major}.{sys.version_info.minor}')}


def _runtime_entries(directory):
    runtime = json.loads((directory / RUNTIME_MANIFEST).read_text())
    pins, dependencies = _local_dependencies(directory)
    if (runtime.get('schema') != 1 or runtime.get('dependencies') != pins or
            runtime.get('interpreter') != _interpreter()):
        raise ValueError('resource runtime prerequisite mismatch')
    entries = runtime['entries']
    files = set(dependencies) | {'.venv/pyvenv.cfg'} | _python_links()
    if set(entries) != files | _parents(files):
        raise ValueError('unapproved runtime membership')
    for name, (_, expected) in dependencies.items():
        if entries[name] != expected:
            raise ValueError('unapproved runtime dependency: ' + name)
    for name in _parents(files):
        if entries[name] != {'kind': 'directory'}:
            raise ValueError('invalid runtime directory: ' + name)
    for name in _python_links():
        row = entries[name]
        path = directory / name
        if (row.get('kind') != 'symlink' or not path.is_symlink() or
                path.resolve(strict=True) != Path(runtime['interpreter']['path'])):
            raise ValueError('invalid runtime interpreter link: ' + name)
    config_path = directory / '.venv/pyvenv.cfg'
    if entries['.venv/pyvenv.cfg'] != _file_row(config_path):
        raise ValueError('runtime configuration mismatch')
    config = dict(line.split(' = ', 1) for line in config_path.read_text().splitlines())
    if (config.get('include-system-site-packages') != 'false' or
            config.get('version') != '.'.join(map(str, sys.version_info[:3])) or
            Path(config.get('executable', '')).resolve() != Path(runtime['interpreter']['path']) or
            Path(config.get('home', '')).resolve() != Path(sys._base_executable).parent.resolve()):
        raise ValueError('runtime configuration is not isolated')
    return entries


def verify_tree(directory):
    directory = directory.absolute()
    if directory.is_symlink() or any(parent.is_symlink() for parent in directory.parents):
        raise ValueError('invalid resource root')
    manifest_row = _file_row(directory / MANIFEST)
    m = json.loads((directory / MANIFEST).read_text())
    if m.get('schema') != 1 or not isinstance(m.get('files'), dict):
        raise ValueError('invalid resource manifest')
    expected = {MANIFEST: manifest_row}
    for name, row in m['files'].items():
        if not eligible(name) or row.get('mode') not in ('0644', '0755'):
            raise ValueError('unsafe resource path or mode: ' + name)
        expected[name] = {'kind': 'file', **row}
    expected.update({name: {'kind': 'directory'} for name in _parents(expected)})
    runtime_path = directory / RUNTIME_MANIFEST
    if runtime_path.exists() or runtime_path.is_symlink():
        expected[RUNTIME_MANIFEST] = _file_row(runtime_path)
        expected.update(_runtime_entries(directory))
    actual = _members(directory)
    if actual.keys() != expected.keys():
        raise ValueError('resource membership mismatch: ' + ', '.join(sorted(actual.keys() ^ expected.keys())))
    for name, row in expected.items():
        if actual[name] != row:
            raise ValueError('resource identity mismatch: ' + name)
    return m


def provision_runtime(directory):
    """Provision a fresh same-interpreter resource venv from local exact pins."""
    directory = directory.absolute()
    verify_tree(directory)
    if (directory / '.venv').exists() or (directory / RUNTIME_MANIFEST).exists():
        raise ValueError('resource runtime must be new')
    pins, dependencies = _local_dependencies(directory)
    venv.EnvBuilder(with_pip=False, symlinks=True).create(directory / '.venv')
    # Keep the conventional interpreter/prefix layout, without activation tools
    # or arbitrary installer products. Only these files and declared packages
    # belong in a desktop resource tree.
    scaffold = {'.venv/pyvenv.cfg'} | _python_links()
    for name, row in _members(directory / '.venv').items():
        if row['kind'] != 'directory' and '.venv/' + name not in scaffold:
            (directory / '.venv' / name).unlink()
    for name, (original, row) in dependencies.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        target.chmod(int(row['mode'], 8))
    for path in sorted((directory / '.venv').rglob('*'), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir() and not path.is_symlink() and not any(path.iterdir()):
            path.rmdir()
    entries = {'.venv': {'kind': 'directory'}}
    entries.update({'.venv/' + name: row for name, row in _members(directory / '.venv').items()})
    report = {'schema': 1, 'dependencies': pins, 'interpreter': _interpreter(), 'entries': entries}
    with (directory / RUNTIME_MANIFEST).open('x') as output:
        output.write(json.dumps(report, sort_keys=True, indent=2) + '\n')
    verify_tree(directory)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    b = sub.add_parser('build'); b.add_argument('--output', type=Path, required=True)
    v = sub.add_parser('verify'); v.add_argument('--archive', type=Path, required=True)
    u = sub.add_parser('unpack'); u.add_argument('--archive', type=Path, required=True); u.add_argument('--destination', type=Path, required=True)
    t = sub.add_parser('verify-tree'); t.add_argument('--directory', type=Path, required=True)
    r = sub.add_parser('provision-runtime'); r.add_argument('--directory', type=Path, required=True)
    a = p.parse_args()
    if a.operation == 'build':
        print(json.dumps(build(ROOT, a.output)))
    elif a.operation == 'verify':
        print(json.dumps({'ok': True, 'files': len(verify(a.archive)['files'])}))
    elif a.operation == 'verify-tree':
        print(json.dumps({'ok': True, 'files': len(verify_tree(a.directory)['files'])}))
    elif a.operation == 'provision-runtime':
        report = provision_runtime(a.directory)
        print(json.dumps({'ok': True, 'dependencies': report['dependencies'],
                          'interpreter': report['interpreter'], 'entries': len(report['entries'])}))
    else:
        unpack(a.archive, a.destination)
        print(json.dumps({'ok': True, 'destination': str(a.destination)}))


if __name__ == '__main__':
    main()
