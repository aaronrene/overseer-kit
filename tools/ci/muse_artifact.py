"""Reproduce or verify the explicitly local Muse rc5 recovery distribution.

No upstream release is claimed. This stdlib-only tool neither installs nor
downloads anything. The reviewed manifest covers source, data and metadata.
"""
import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

HERE = Path(__file__).resolve().parent
DIST = 'muse-0.2.1rc5.dist-info'
SOURCE_NAME = 'muse-0.2.1rc5-overseer-recovery1-source.zip'
WHEEL_NAME = 'muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def contract():
    lock = json.loads((HERE / 'muse-rc5-artifact.json').read_bytes())
    raw = (HERE / 'muse-rc5-source-files.json').read_bytes()
    if sha(raw) != lock['payload_manifest_sha256']:
        raise ValueError('reviewed payload manifest digest differs')
    return lock, json.loads(raw)


def validate_payload(files, manifest, source_sha256):
    if files.keys() != manifest.keys():
        raise ValueError('payload paths differ from reviewed manifest')
    source = hashlib.sha256()
    for name, expected in sorted(manifest.items()):
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or str(path) != name
                or not name.startswith(('muse/', DIST + '/'))):
            raise ValueError('invalid payload path: ' + name)
        raw = files[name]
        if len(raw) != expected['size'] or sha(raw) != expected['sha256']:
            raise ValueError('payload differs: ' + name)
        if name.startswith('muse/') and name.endswith('.py'):
            source.update(name[5:].encode() + b'\0' + raw + b'\0')
    if source.hexdigest() != source_sha256:
        raise ValueError('package source differs from reviewed rc5')


def read_installed(root, manifest):
    files = {}
    for name in manifest:
        path = root / name
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('linked input: ' + name)
        files[name] = path.read_bytes()
    # Installation-generated metadata/bytecode are not distribution inputs.
    # Do not silently omit added package code or data.
    observed = {p.relative_to(root).as_posix() for p in (root / 'muse').rglob('*')
                if p.is_file() and p.suffix != '.pyc'}
    if observed != {n for n in manifest if n.startswith('muse/')}:
        raise ValueError('installed package has missing or extra payload files')
    return files


def read_archive(raw, manifest):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(manifest):
            raise ValueError('source archive paths differ from reviewed manifest')
        for info in archive.infolist():
            if info.file_size != manifest[info.filename]['size']:
                raise ValueError('source archive entry size differs')
        return {name: archive.read(name) for name in names}


def archive_bytes(files):
    # Stored entries avoid zlib/version-dependent compression; metadata/order
    # never depend on wall clock, filesystem mode, umask, host or source mtime.
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, raw)
    return output.getvalue()


def artifacts(files, lock):
    source = archive_bytes(files)
    wheel_files = dict(files)
    wheel_files[DIST + '/WHEEL'] = (
        'Wheel-Version: 1.0\nGenerator: overseer-rc5-recovery-1\n'
        'Root-Is-Purelib: true\nBuild: 1overseerrecovery\nTag: py3-none-any\n'
    ).encode()
    wheel_files[DIST + '/OVERSEER_RECOVERY.json'] = json_bytes({
        'origin': lock['origin'], 'upstream_release': False,
        'version': '0.2.1rc5', 'build': '1overseerrecovery',
        'source_sha256': lock['package_source_sha256'],
        'payload_manifest_sha256': lock['payload_manifest_sha256'],
        'recovery_source_archive_sha256': sha(source),
        'original_sdist_sha256_recorded_by_pip': lock['original_sdist_sha256'],
        'original_sdist_recovered': False,
    })
    record = io.StringIO()
    writer = csv.writer(record, lineterminator='\n')
    for name, raw in sorted(wheel_files.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('=')
        writer.writerow([name, 'sha256=' + digest, len(raw)])
    writer.writerow([DIST + '/RECORD', '', ''])
    wheel_files[DIST + '/RECORD'] = record.getvalue().encode()
    return {SOURCE_NAME: source, WHEEL_NAME: archive_bytes(wheel_files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    rebuild = commands.add_parser('rebuild')
    inputs = rebuild.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--installed-root', type=Path)
    inputs.add_argument('--source-archive', type=Path)
    rebuild.add_argument('--output-dir', type=Path, required=True)
    verify = commands.add_parser('verify')
    verify.add_argument('--wheel', type=Path, required=True)
    args = parser.parse_args()
    try:
        lock, manifest = contract()
        if args.command == 'verify':
            if args.wheel.name != WHEEL_NAME or sha(args.wheel.read_bytes()) != lock['artifacts'][WHEEL_NAME]:
                raise ValueError('wheel name/digest differs from reviewed recovery artifact')
            print('Verified exact local rc5 recovery wheel; not an upstream release.')
            return
        if args.installed_root:
            files = read_installed(args.installed_root.resolve(), manifest)
        else:
            raw = args.source_archive.read_bytes()
            if sha(raw) != lock['artifacts'][SOURCE_NAME]:
                raise ValueError('recovery source archive digest differs')
            files = read_archive(raw, manifest)
        validate_payload(files, manifest, lock['package_source_sha256'])
        built = artifacts(files, lock)
        if {name: sha(raw) for name, raw in built.items()} != lock['artifacts']:
            raise ValueError('rebuilt artifact digests differ from reviewed contract')
        args.output_dir.mkdir(parents=True, exist_ok=False)
        for name, raw in built.items():
            (args.output_dir / name).write_bytes(raw)
        print(json.dumps({name: sha(raw) for name, raw in built.items()}, indent=2))
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
