"""Recovery packaging guards run in the Git-only environment without Muse."""
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile

import pytest

from tools.ci import muse_artifact as artifact


@pytest.fixture
def payload(tmp_path):
    files = {'muse/__init__.py': b'VERSION = "0.2.1rc5"\n',
             'muse/data.bin': b'\x00\xffpayload',
             artifact.DIST + '/METADATA': b'Name: muse\nVersion: 0.2.1rc5\n',
             artifact.DIST + '/WHEEL': b'original generator\n'}
    manifest = {n: {'sha256': artifact.sha(b), 'size': len(b)} for n, b in files.items()}
    source = hashlib.sha256(b'__init__.py\0' + files['muse/__init__.py'] + b'\0').hexdigest()
    lock = {'origin': 'Local recovery, not an upstream release',
            'package_source_sha256': source,
            'payload_manifest_sha256': artifact.sha(artifact.json_bytes(manifest)),
            'original_sdist_sha256': '1' * 64}
    for name, raw in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return tmp_path, files, manifest, lock


def test_rebuild_independent_of_order_time_mode_and_roundtrip(payload):
    root, files, manifest, lock = payload
    expected = artifact.artifacts(files, lock)
    for name in files:
        (root / name).chmod(0o600)
        os.utime(root / name, (1_800_000_000, 1_800_000_000))
    actual = artifact.read_installed(root, manifest)
    artifact.validate_payload(actual, manifest, lock['package_source_sha256'])
    assert artifact.artifacts(dict(reversed(list(actual.items()))), lock) == expected
    recovered = artifact.read_archive(expected[artifact.SOURCE_NAME], manifest)
    assert artifact.artifacts(recovered, lock) == expected
    with zipfile.ZipFile(io.BytesIO(expected[artifact.WHEEL_NAME])) as wheel:
        provenance = json.loads(wheel.read(artifact.DIST + '/OVERSEER_RECOVERY.json'))
        assert provenance['upstream_release'] is False
        assert provenance['original_sdist_recovered'] is False
        assert provenance['recovery_source_archive_sha256'] == artifact.sha(expected[artifact.SOURCE_NAME])
        for name, digest, size in csv.reader(io.StringIO(wheel.read(artifact.DIST + '/RECORD').decode())):
            if name.endswith('/RECORD'):
                assert digest == size == ''
            else:
                raw = wheel.read(name)
                assert int(size) == len(raw)
                assert digest == 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('=')


@pytest.mark.parametrize('path', ['muse/__init__.py', 'muse/data.bin', artifact.DIST + '/METADATA'])
def test_changed_source_data_or_metadata_refuses(payload, path):
    _, files, manifest, lock = payload
    files[path] += b'changed'
    with pytest.raises(ValueError, match='payload differs'):
        artifact.validate_payload(files, manifest, lock['package_source_sha256'])


def test_added_installed_code_refuses_but_generated_bytecode_is_ignored(payload):
    root, files, manifest, _ = payload
    (root / 'muse/cache.pyc').write_bytes(b'generated')
    assert artifact.read_installed(root, manifest) == files
    (root / 'muse/extra.py').write_bytes(b'unreviewed')
    with pytest.raises(ValueError, match='extra payload'):
        artifact.read_installed(root, manifest)


def test_linked_input_refuses(payload):
    root, _, manifest, _ = payload
    (root / 'muse/data.bin').unlink()
    (root / 'muse/data.bin').symlink_to('__init__.py')
    with pytest.raises(ValueError, match='linked input'):
        artifact.read_installed(root, manifest)


def test_source_pin_drift_refuses(payload):
    _, files, manifest, _ = payload
    with pytest.raises(ValueError, match='source differs'):
        artifact.validate_payload(files, manifest, '0' * 64)


def test_duplicate_archive_entries_refuse(payload):
    _, files, manifest, _ = payload
    raw = io.BytesIO(artifact.archive_bytes(files))
    with zipfile.ZipFile(raw, 'a') as archive, pytest.warns(UserWarning):
        archive.writestr('muse/data.bin', b'duplicate')
    with pytest.raises(ValueError, match='paths differ'):
        artifact.read_archive(raw.getvalue(), manifest)


def test_manifest_tamper_refuses(tmp_path, monkeypatch):
    (tmp_path / 'muse-rc5-artifact.json').write_text(json.dumps({'payload_manifest_sha256': '0' * 64}))
    (tmp_path / 'muse-rc5-source-files.json').write_text('{}')
    monkeypatch.setattr(artifact, 'HERE', tmp_path)
    with pytest.raises(ValueError, match='manifest digest'):
        artifact.contract()


@pytest.mark.parametrize('changed', ['wheel', 'source'])
def test_cli_rejects_artifact_substitution_before_output(payload, monkeypatch, changed):
    root, files, manifest, lock = payload
    built = artifact.artifacts(files, lock)
    lock['artifacts'] = {n: artifact.sha(b) for n, b in built.items()}
    monkeypatch.setattr(artifact, 'contract', lambda: (lock, manifest))
    name = artifact.WHEEL_NAME if changed == 'wheel' else artifact.SOURCE_NAME
    path = root / name
    path.write_bytes(built[name] + b'tampered')
    output = root / 'output'
    args = (['verify', '--wheel', str(path)] if changed == 'wheel' else
            ['rebuild', '--source-archive', str(path), '--output-dir', str(output)])
    monkeypatch.setattr('sys.argv', ['muse_artifact.py', *args])
    with pytest.raises(SystemExit) as error:
        artifact.main()
    assert error.value.code == 1
    assert not output.exists()


def test_committed_contract_matches_supported_runtime_pin():
    lock, manifest = artifact.contract()
    assert len(manifest) == 388
    assert all(name.startswith(('muse/', artifact.DIST + '/')) for name in manifest)
    # Keep the runtime's independent installed-source check aligned with the
    # artifact pin while the Git-only job imports no Muse package.
    from tools.ci.supported_v1 import MUSE_SOURCE_SHA256
    assert lock['package_source_sha256'] == MUSE_SOURCE_SHA256
    assert lock['artifacts'][artifact.WHEEL_NAME] != lock['r3_reconstructed_wheel_sha256']
