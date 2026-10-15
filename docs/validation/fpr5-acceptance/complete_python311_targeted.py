"""Fixture prerequisite correction and affected final-candidate package evidence.

Run only after the original complete serial collection finishes. Original
evidence is immutable; these records do not relabel that run as all green.
"""
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
INSTALL = OUT / 'python3.11-installation'
ROOT = Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
EVIDENCE = OUT / 'targeted'
REPORT_PATH = OUT / 'python311-targeted-reconciliation.json'
RUNTIME = 'cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774'
CONFIG = 'desktop/src-tauri/tauri.conf.json'
TWIN = 'tests/security/test_p_deploy_security.py::test_twin_skill_paths_exist'
PACKAGES = [
    'tests/fpr3/test_package.py::test_actual_package_deterministic_manifest_modes_and_resource_bundle',
    'tests/fpr5/test_resource_repairs.py::test_provisioned_runtime_and_actual_packaged_entrypoints',
]
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PIP_NO_INDEX='1', UV_OFFLINE='1',
           GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
for key in ('FPR2_MUSE_PYTHON', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS', 'PYTHONPATH', 'PYTHONHOME'):
    ENV.pop(key, None)
sys.path.insert(0, str(INSTALL))
from cli import v1
from scripts.fpr4_run import snapshot

REPORT = {
    'kind': 'Prerequisite-corrected and affected final-candidate Python3.11 evidence',
    'author_validation': True,
    'independent_adjudication': False,
    'original_run_relabelled': False,
    'original_source_head': '2e8ec694def9be4a0faa4a994bf2fff3f212ab23',
    'runtime_sha256': RUNTIME,
    'no_new_requirement_waivers': True,
    'commands': [], 'reruns': [],
    'disk_minimum_before_bytes': 500 * 1024 * 1024,
    'disk_floor_during_bytes': 250 * 1024 * 1024,
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save():
    REPORT_PATH.write_text(json.dumps(REPORT, indent=2) + '\n')

def write_new(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

def inventory(paths, root=INSTALL):
    result = {}
    for name in sorted(paths):
        p = root / name
        s = p.lstat()
        if stat.S_ISLNK(s.st_mode):
            result[name] = {'kind': 'symlink', 'target': os.readlink(p)}
        elif stat.S_ISREG(s.st_mode):
            result[name] = {'kind': 'file', 'sha256': sha(p.read_bytes()),
                            'mode': stat.S_IMODE(s.st_mode), 'size': s.st_size}
        elif stat.S_ISDIR(s.st_mode):
            result[name] = {'kind': 'directory', 'mode': stat.S_IMODE(s.st_mode)}
        else:
            raise AssertionError('unexpected filesystem kind: ' + str(p))
    return result

def source_snapshot(names):
    source = inventory(names)
    dependencies = inventory(p.relative_to(INSTALL).as_posix()
                             for p in (INSTALL / '.venv').rglob('*'))
    return {'source_count': len(source), 'source_members': source,
            'source_manifest_sha256': sha((INSTALL / 'SOURCE-MANIFEST.json').read_bytes()),
            'venv_members': dependencies, 'boundary': snapshot(),
            'git_status': subprocess.check_output(
                ['/usr/bin/git', '-C', str(INSTALL), 'status', '--porcelain=v1'],
                env=ENV, text=True)}

def command(argv, *, tag):
    p = subprocess.run(list(map(str, argv)), cwd=INSTALL, env=ENV,
                       capture_output=True, text=True, timeout=90)
    row = {'tag': tag, 'argv': list(map(str, argv)), 'cwd': str(INSTALL),
           'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    REPORT['commands'].append(row)
    save()
    if p.returncode:
        raise RuntimeError('command failed: ' + tag)
    return json.loads(p.stdout)

def run_case(name, nodeid):
    free = shutil.disk_usage(OUT).free
    if free < REPORT['disk_minimum_before_bytes']:
        raise RuntimeError('insufficient disk before ' + name + ': ' + str(free))
    selection_path = EVIDENCE / (name + '-selection.json')
    write_new(selection_path, {'selected': [nodeid], 'deselected': [], 'expected_count': 1})
    argv = [str(INSTALL / '.venv/bin/python'), '-I', '-B',
            str(INSTALL / 'scripts/fpr4_run.py'), '--name', name,
            '--selection', str(selection_path), '--evidence-dir', str(EVIDENCE)]
    row = {'name': name, 'nodeid': nodeid, 'argv': argv, 'free_before': free}
    REPORT['reruns'].append(row)
    save()
    with (EVIDENCE / (name + '-driver.log')).open('xb') as log:
        p = subprocess.Popen(argv, cwd=INSTALL, env=ENV, stdout=log,
                             stderr=subprocess.STDOUT, start_new_session=True)
        while p.poll() is None:
            time.sleep(2)
            if shutil.disk_usage(OUT).free < REPORT['disk_floor_during_bytes']:
                row['disk_stop'] = True
                os.killpg(p.pid, signal.SIGINT)
                try:
                    p.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGTERM)
                    p.wait(timeout=15)
                break
    row['exit_code'] = p.returncode
    record_path = EVIDENCE / (name + '.json')
    record = json.loads(record_path.read_text()) if record_path.exists() else {}
    row['record'] = str(record_path)
    row['result'] = {k: record.get(k) for k in (
        'ok', 'results', 'boundary_unchanged', 'exact_collection_executed_once', 'nonpassing')}
    if record.get('ok'):
        fixture = Path(record['fixture_parent'])
        assert fixture.parent == Path('/private/tmp')
        assert fixture.name.startswith('overseer-fpr4-' + name + '-')
        assert fixture.is_dir() and not fixture.is_symlink()
        shutil.rmtree(fixture)
        row['passing_fixture_reclaimed'] = str(fixture)
    row['free_after'] = shutil.disk_usage(OUT).free
    save()
    print(json.dumps({'finished': name, 'result': row['result'], 'free': row['free_after']}), flush=True)
    return record

def outcomes(record_path):
    record = json.loads(record_path.read_text())
    collection = json.loads(Path(record['collection_file']).read_text())['cases']
    by_hash = {x['node_sha256']: x['nodeid'] for x in collection}
    xml_path = record_path.with_suffix('.xml')
    result = {}
    for case in ET.parse(xml_path).getroot().iter('testcase'):
        properties = case.find('properties')
        hashes = [p.get('value') for p in properties or () if p.get('name') == 'fpr4_nodeid_sha256']
        assert len(hashes) == 1 and hashes[0] in by_hash
        node = by_hash[hashes[0]]
        assert node not in result
        result[node] = 'passed' if not any(case.find(t) is not None for t in ('failure', 'error', 'skipped')) else 'nonpassing'
    assert set(result) == set(x['nodeid'] for x in collection)
    return result

def main():
    assert not REPORT_PATH.exists(), 'preserve previous targeted records'
    serial_bytes = (OUT / 'python311-serial.json').read_bytes()
    serial = json.loads(serial_bytes)
    assert 'exact_complete_partition' in serial, 'serial runner still active'
    assert serial['exact_complete_partition'], 'original collection incomplete'
    REPORT['original_serial_sha256'] = sha(serial_bytes)
    REPORT['original_serial_ok'] = serial['ok']
    REPORT['original_collection_count'] = serial['collected_total']
    assert serial['collected_total'] == 1196
    EVIDENCE.mkdir(exist_ok=False)
    os.chdir(INSTALL)
    manifest_bytes = (INSTALL / 'SOURCE-MANIFEST.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    names = sorted(manifest['files'])
    assert len(names) == 1483
    assert v1.runtime()['sha256'] == RUNTIME
    before = source_snapshot(names)
    write_new(EVIDENCE / 'fixture-init-before.json', before)
    for name, item in manifest['files'].items():
        observed = before['source_members'][name]
        assert observed['sha256'] == item['sha256']
        assert observed['size'] == item['size']
        assert observed['mode'] == int(item['mode'], 8)
    args = [INSTALL / 'cli/ok', '-C', INSTALL, 'init', '--vcs', 'git',
            '--repo-name', 'fpr5-python311-acceptance', '--lane', 'product',
            '--model', 'GPT-6 Astra', '--non-interactive', '--json']
    preview = command([*args, '--dry-run'], tag='fixture-init-dry-run')
    assert not (INSTALL / '.overseer').exists()
    assert inventory(names) == before['source_members']
    allowed = ('.overseer/', '.cursor/rules/', '.cursor/skills/', '.claude/skills/')
    assert all(p.startswith(allowed) for p in preview['changed']), preview['changed']
    initialized = command(args, tag='fixture-init-apply')
    REPORT['fixture_initialization'] = {'preview': preview, 'applied': initialized,
                                      'hooks_requested': False}
    bound = INSTALL / '.overseer/bin/ok'
    command([bound, '-C', INSTALL, 'status', '--json'], tag='bound-status')
    command([bound, '-C', INSTALL, 'next', '--json'], tag='bound-next')
    again = command([bound, '-C', INSTALL, 'init', '--vcs', 'git', '--json'], tag='bound-init-idempotent')
    assert not again['changed'], again
    after = source_snapshot(names)
    write_new(EVIDENCE / 'fixture-init-after.json', after)
    for field in ('source_members', 'source_manifest_sha256', 'venv_members', 'boundary'):
        assert before[field] == after[field], field
    assert v1.runtime()['sha256'] == RUNTIME
    assert not (INSTALL / '.cursor/hooks.json').exists()
    assert not (INSTALL / '.cursor/hooks').exists()
    REPORT['fixture_source_test_runtime_dependencies_head_refs_identical'] = True
    REPORT['fixture_source_member_count'] = len(names)
    REPORT['fixture_added_members'] = inventory(
        p.relative_to(INSTALL).as_posix()
        for folder in ('.overseer', '.cursor', '.claude')
        for p in (INSTALL / folder).rglob('*'))
    REPORT['fixture_added_members'].update(inventory(['docs/NEXT.md']))
    save()
    twin = run_case('py311-twin-prerequisite-corrected', TWIN)
    assert twin.get('ok'), 'twin prerequisite rerun failed'

    before_candidate = source_snapshot(names)
    write_new(EVIDENCE / 'final-candidate-before.json', before_candidate)
    assert before_candidate['source_members'] == before['source_members']
    replacement = (ROOT / CONFIG).read_bytes()
    old_config = json.loads((INSTALL / CONFIG).read_bytes())
    new_config = json.loads(replacement)
    expected_config = json.loads(json.dumps(old_config))
    expected_config['app']['windows'][0]['create'] = False
    assert new_config == expected_config, 'unauthorized Tauri difference'
    assert len(new_config['app']['windows']) == 1
    (EVIDENCE / 'SOURCE-MANIFEST.original.json').write_bytes(manifest_bytes)
    (EVIDENCE / 'tauri.conf.original.json').write_bytes((INSTALL / CONFIG).read_bytes())
    (INSTALL / CONFIG).write_bytes(replacement)
    changed_manifest = json.loads(manifest_bytes)
    changed_manifest['files'][CONFIG]['sha256'] = sha(replacement)
    changed_manifest['files'][CONFIG]['size'] = len(replacement)
    (INSTALL / 'SOURCE-MANIFEST.json').write_text(json.dumps(changed_manifest, indent=2, sort_keys=True) + '\n')
    after_candidate = source_snapshot(names)
    write_new(EVIDENCE / 'final-candidate-after.json', after_candidate)
    changed = [name for name in names
               if before_candidate['source_members'][name] != after_candidate['source_members'][name]]
    assert changed == [CONFIG], changed
    for field in ('runtime', 'runtime_files', 'test_sources', 'python', 'executable', 'prefix',
                  'platform', 'machine', 'git', 'dependencies', 'requirements', 'refs',
                  'validation_scripts', 'packaging_sources', 'muse_runtime', 'head', 'parents', 'branch'):
        assert before_candidate['boundary'][field] == after_candidate['boundary'][field], field
    assert before_candidate['venv_members'] == after_candidate['venv_members']
    assert v1.runtime()['sha256'] == RUNTIME
    REPORT['final_candidate_delta'] = {
        'source_member_count': len(names), 'only_changed_source_member': CONFIG,
        'before': before_candidate['source_members'][CONFIG],
        'after': after_candidate['source_members'][CONFIG],
        'matches_authorized_root_config_sha256': sha((ROOT / CONFIG).read_bytes()) == sha(replacement),
        'manifest_before_sha256': sha(manifest_bytes),
        'manifest_after_sha256': sha((INSTALL / 'SOURCE-MANIFEST.json').read_bytes()),
        'runtime_tests_dependencies_head_refs_unchanged': True,
    }
    save()
    for i, node in enumerate(PACKAGES, 1):
        run_case('py311-finalcandidate-package-' + str(i), node)
    final = source_snapshot(names)
    write_new(EVIDENCE / 'final-candidate-after-reruns.json', final)
    for field in ('source_members', 'source_manifest_sha256', 'venv_members', 'boundary'):
        assert final[field] == after_candidate[field], field

    expected = {r['nodeid'] for r in json.loads((OUT / 'python311-expected-collection.json').read_text())['cases']}
    original = {}
    for group in serial['groups']:
        record_path = OUT / 'matrix' / ('py311-' + group + '.json')
        record = json.loads(record_path.read_text())
        assert record['boundary_unchanged'] and record['exact_collection_executed_once']
        row = outcomes(record_path)
        assert not original.keys() & row.keys()
        original.update(row)
    assert set(original) == expected
    reconciled = dict(original)
    for rerun in REPORT['reruns']:
        record = json.loads(Path(rerun['record']).read_text())
        assert record['boundary_unchanged'] and record['exact_collection_executed_once']
        reconciled.update(outcomes(Path(rerun['record'])))
    REPORT['coverage'] = {
        'expected_distinct_cases': len(expected),
        'original_outcomes': dict(Counter(original.values())),
        'original_nonpassing_nodeids': [n for n, outcome in original.items() if outcome != 'passed'],
        'distinct_reconciled_outcomes': dict(Counter(reconciled.values())),
        'unresolved_nodeids': [n for n, outcome in reconciled.items() if outcome != 'passed'],
        'complete_distinct_passing_coverage': set(reconciled) == expected and set(reconciled.values()) == {'passed'},
        'basis': 'Original immutable repaired-source partitions plus prerequisite-corrected twin case and two affected final-candidate package cases; original failures retained.',
    }
    assert (OUT / 'python311-serial.json').read_bytes() == serial_bytes
    REPORT['ok'] = REPORT['coverage']['complete_distinct_passing_coverage']
    save()
    print(json.dumps({'ok': REPORT['ok'], 'coverage': REPORT['coverage'], 'report': str(REPORT_PATH)}, indent=2), flush=True)

try:
    main()
except Exception as exc:
    REPORT['ok'] = False
    REPORT['error'] = repr(exc)
    if EVIDENCE.exists():
        save()
    raise
