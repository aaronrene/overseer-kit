"""Actual repeated desktop resource preparation under one shared TMPDIR."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from cli.v1 import runtime, runtime_files
from tests.v1.conftest import KIT
from tools.ci.source_package import MANIFEST, build, source_files, unpack, verify_tree


def test_repeated_resource_bundle_reserves_distinct_private_archives(tmp_path):
    # Evidence files may still change in the integration checkout. Copy exact
    # source bytes once before exercising the real script's two package builds.
    frozen = tmp_path / 'frozen-source'
    frozen.mkdir()
    entries = {}
    for name, original in source_files(KIT).items():
        target = frozen / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        mode = 0o755 if original.stat().st_mode & 0o111 else 0o644
        target.chmod(mode)
        data = target.read_bytes()
        entries[name] = {'sha256': hashlib.sha256(data).hexdigest(),
                         'size': len(data), 'mode': f'{mode:04o}'}
    (frozen / MANIFEST).write_text(json.dumps({'schema': 1, 'files': entries}))
    archive = tmp_path / 'fixture-source.tar.gz'
    build(frozen, archive)
    installation = tmp_path / 'installation'
    unpack(archive, installation)
    subprocess.run([sys.executable, '-m', 'venv', '--without-pip',
                    str(installation / '.venv')], check=True, capture_output=True)

    scratch = tmp_path / 'same-tmpdir'
    scratch.mkdir()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('PYTHON', 'GIT_')) and key != 'VIRTUAL_ENV'}
    env.update(PATH='/usr/bin:/bin', TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE='1')
    expected_runtime = runtime()['sha256']
    paths = runtime_files()
    outputs = []
    for name in ('resource-a', 'resource-b'):
        destination = tmp_path / name
        result = subprocess.run([str(installation / 'scripts/bundle-desktop-kit.sh'),
                                 str(destination)], cwd=tmp_path, env=env,
                                capture_output=True, text=True, timeout=120)
        assert result.returncode == 0, result.stdout + result.stderr
        outputs.append(json.loads(result.stdout.splitlines()[0]))
        verify_tree(destination)
        resource_digest = hashlib.sha256(b''.join(
            name.encode() + b'\0' + (destination / name).read_bytes() + b'\0'
            for name in paths)).hexdigest()
        assert resource_digest == expected_runtime
        assert (destination / MANIFEST).read_bytes() == (tmp_path / 'resource-a' / MANIFEST).read_bytes()

    archives = [Path(item['archive']) for item in outputs]
    assert archives[0].parent != archives[1].parent
    assert all(path.is_file() and path.parent.parent == scratch for path in archives)
    assert all(path.parent.stat().st_mode & 0o777 == 0o700 for path in archives)
    assert outputs[0]['sha256'] == outputs[1]['sha256']
    assert outputs[0]['manifest_sha256'] == outputs[1]['manifest_sha256']
