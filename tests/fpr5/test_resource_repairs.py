"""Prepared desktop resources must contain only approved source/runtime entries."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from tests.v1.conftest import KIT, command, seed
from tools.ci import source_package as package


@pytest.fixture
def resource(tmp_path):
    root = tmp_path / 'resources'
    (root / 'cli').mkdir(parents=True)
    source = root / 'cli/ok'
    source.write_bytes(b'#!/bin/sh\nexit 0\n')
    source.chmod(0o755)
    manifest = {'schema': 1, 'version': 'fixture', 'files': {
        'cli/ok': {'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'size': source.stat().st_size, 'mode': '0755'}}}
    (root / package.MANIFEST).write_text(json.dumps(manifest))
    return root


def test_clean_source_resource_is_accepted(resource):
    assert set(package.verify_tree(resource)['files']) == {'cli/ok'}


@pytest.mark.parametrize('relative', [
    '.overseer/config.yaml', 'docs/NEXT.md', 'tools/.env', 'tools/extra.py',
    'tools/.hidden', '.venv/lib/python3.14/site-packages/unapproved.py',
])
def test_unmanifested_resource_file_is_rejected(resource, relative):
    path = resource / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('synthetic owner data\n')
    with pytest.raises(ValueError):
        package.verify_tree(resource)


@pytest.mark.parametrize('relative', ['.overseer', 'tools/empty-extra', '.venv'])
def test_unapproved_empty_directory_is_rejected(resource, relative):
    (resource / relative).mkdir(parents=True)
    with pytest.raises(ValueError):
        package.verify_tree(resource)


@pytest.mark.parametrize('target', ['cli/ok', 'cli', '/nonexistent/resource-fixture'])
def test_unmanifested_symlink_is_rejected(resource, target):
    (resource / 'extra-link').symlink_to(target)
    with pytest.raises(ValueError):
        package.verify_tree(resource)


def test_manifest_symlink_is_rejected(resource, tmp_path):
    original = resource / package.MANIFEST
    saved = tmp_path / 'manifest.json'
    original.rename(saved)
    original.symlink_to(saved)
    with pytest.raises(ValueError):
        package.verify_tree(resource)


def test_unmanifested_special_file_is_rejected(resource):
    os.mkfifo(resource / 'pipe')
    with pytest.raises(ValueError):
        package.verify_tree(resource)


def test_resource_size_tamper_is_rejected(resource):
    path = resource / package.MANIFEST
    manifest = json.loads(path.read_text())
    manifest['files']['cli/ok']['size'] += 1
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        package.verify_tree(resource)


def test_provisioned_runtime_and_actual_packaged_entrypoints(tmp_path):
    archive = tmp_path / 'source.tar.gz'
    package.build(KIT, archive)
    root = tmp_path / 'resources'
    package.unpack(archive, root)
    report = package.provision_runtime(root)
    assert report['dependencies'] == {
        'PyYAML': '6.0.3', 'cryptography': '49.0.0', 'cffi': '2.1.0', 'pycparser': '3.0'}
    assert (root / '.venv/bin/python3').is_symlink()
    assert not (root / '.venv/bin/pip').exists()
    package.verify_tree(root)
    repository = seed(tmp_path / 'consumer')
    init = command('-C', repository, 'init', '--vcs', 'git', executable=root / 'cli/ok')
    assert init.returncode == 0, init.stdout + init.stderr
    for launcher in (root / 'cli/ok', repository / '.overseer/bin/ok'):
        status = command('-C', repository, 'status', '--json', executable=launcher)
        assert status.returncode == 0, status.stdout + status.stderr
        assert json.loads(status.stdout)['runtime']['root'] == str(root)
    package.verify_tree(root)
    # Runtime allowance does not turn into an unbounded .venv exception.
    extra = root / '.venv/.env'
    extra.write_text('FAKE_TOKEN=fixture\n')
    with pytest.raises(ValueError):
        package.verify_tree(root)
    extra.unlink()
    # Nor can an excluded file enroll itself through the runtime inventory.
    inventory = root / package.RUNTIME_MANIFEST
    body = json.loads(inventory.read_text())
    extra.write_text('FAKE_TOKEN=fixture\n')
    body['entries']['.venv/.env'] = {
        'kind': 'file', 'mode': '0644', 'size': extra.stat().st_size,
        'sha256': hashlib.sha256(extra.read_bytes()).hexdigest()}
    inventory.write_text(json.dumps(body))
    with pytest.raises(ValueError):
        package.verify_tree(root)


def test_existing_unapproved_venv_is_not_enrolled(resource):
    (resource / '.venv').mkdir()
    (resource / '.venv/.env').write_text('FAKE_TOKEN=fixture\n')
    with pytest.raises(ValueError):
        package.provision_runtime(resource)
