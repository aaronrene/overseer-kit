"""Execute one FPR-4 selection in disjoint groups on one unchanged source set.

Collection is recorded losslessly by a pytest hook. The source-archive case runs
last, after group evidence stops changing. No test-runner dependency is added.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.fpr4_run import (BOUNDARY_KEYS, COLLECTION_ENV, collection_counts,
                             junit_identities, junit_results, runner_environment, snapshot)

EVIDENCE = ROOT / 'docs/validation/fpr4'
PACKAGES = (
    'tests/fpr3/test_package.py::test_actual_package_deterministic_manifest_modes_and_resource_bundle',
    'tests/fpr5/test_resource_repairs.py::test_provisioned_runtime_and_actual_packaged_entrypoints',
)
LATENCY_FILE = 'tests/fpr4/test_disposition_contracts.py'


def execution_groups(selected):
    """Keep partial node selections intact and split directories only by file.

    The complete selection is collected before these groups run, and collection
    counters prove that expansion neither loses nor duplicates a test case.
    """
    buckets = {name: [] for name in ('foundation-v1', 'foundation-fpr1', 'surfaces',
                                     'native-mirror', 'native-other', 'retained', 'latency')}
    expansion = {}
    for selector in selected:
        path = selector.partition('::')[0].rstrip('/')
        directory = ROOT / path
        if '::' not in selector and directory.is_dir():
            items = sorted({str(p.relative_to(ROOT)) for pattern in ('test_*.py', '*_test.py')
                            for p in directory.rglob(pattern)})
            if not items:
                raise ValueError('selected directory has no test files: ' + selector)
            expansion[selector] = items
        else:
            items = [selector]
        for item in items:
            path = item.partition('::')[0]
            if path.startswith('tests/performance/') or path == LATENCY_FILE:
                label = 'latency'
            elif path.startswith('tests/v1/'):
                label = 'foundation-v1'
            elif path.startswith('tests/fpr1/'):
                label = 'foundation-fpr1'
            elif path.startswith('tests/muse/'):
                label = 'native-mirror' if Path(path).name in ('test_mirror.py', 'test_reconciliation.py') else 'native-other'
            elif path.startswith(('tests/fpr2/', 'tests/fpr3/', 'tests/fpr4/')):
                label = 'surfaces'
            else:
                label = 'retained'
            buckets[label].append(item)
    return buckets, expansion


def simple_counter(counter):
    """Keep complete huge/hostile IDs in evidence, not in dictionary key encodings."""
    return [{'key': list(key) if isinstance(key, tuple) else key, 'count': count}
            for key, count in sorted(counter.items(), key=lambda item: json.dumps(item[0]))]


def main():
    global EVIDENCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--muse-python', required=True)
    parser.add_argument('--evidence-dir', type=Path, default=EVIDENCE,
                        help='New evidence destination; existing runs are never overwritten.')
    args = parser.parse_args()
    EVIDENCE = args.evidence_dir.resolve()
    if Path(sys.prefix).resolve() != ROOT / '.venv':
        parser.error("use this installation's conventional .venv")
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,80}', args.name):
        parser.error('name must be a simple evidence basename')
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    target = EVIDENCE / (args.name + '.json')
    if any(EVIDENCE.glob(args.name + '*')):
        parser.error('evidence prefix already exists; preserve earlier matrix evidence')
    selection_bytes = args.selection.read_bytes()
    selection = json.loads(selection_bytes)
    selected, deselected = selection['selected'], selection.get('deselected', [])
    if not selected or not all(isinstance(s, str) and s for s in selected + deselected):
        parser.error('selection must contain explicit nonempty pytest selectors')
    buckets, expansion = execution_groups(selected)
    record = {'scope': 'One combined selection; disjoint execution groups, same source/runtime/dependencies.',
              'selection': str(args.selection), 'selection_sha256': hashlib.sha256(selection_bytes).hexdigest(),
              'groups': [], 'directory_expansion': expansion, 'opening_boundary': snapshot(args.muse_python), 'ok': False,
              'scheduling': 'Disjoint file groups run concurrently; explicit latency tier then archive case run after they finish.'}
    with target.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    collection_path = EVIDENCE / (args.name + '-collection.json')
    collect = [sys.executable, '-B', '-m', 'pytest', '-q', '--collect-only', '-p', 'no:cacheprovider',
               '-p', 'scripts.fpr4_run', '--rootdir=' + str(ROOT), '-c', str(ROOT / 'pyproject.toml'),
               *selected, *['--deselect=' + s for s in deselected]]
    if any(s.partition('::')[0] == 'tests/muse' or s.startswith('tests/muse/') for s in selected):
        collect += ['--muse-python', args.muse_python]
    env = runner_environment(args.muse_python)
    env[COLLECTION_ENV] = str(collection_path)
    collected = subprocess.run(collect, cwd=ROOT, env=env, capture_output=True, text=True)
    (EVIDENCE / (args.name + '-collection.txt')).write_text(collected.stdout + collected.stderr)
    record.update(collection_command=collect, collection_exit_code=collected.returncode,
                  collection_file=str(collection_path))
    try:
        collected_rows, nodes, expected = collection_counts(collection_path)
        record['collected_cases'] = sum(nodes.values())
        record['duplicate_collected_nodes'] = simple_counter(Counter({n: c for n, c in nodes.items() if c != 1}))
        if collected.returncode or not nodes or record['duplicate_collected_nodes']:
            raise ValueError('collection failed, empty, or duplicated; inspect collection evidence')
    except (OSError, ValueError, KeyError) as exc:
        record['evidence_error'] = str(exc)
        target.write_text(json.dumps(record, indent=2) + '\n')
        print(record['evidence_error'], flush=True)
        return 1
    # These cases archive the live source, including evidence. They must wait
    # until every concurrent evidence writer has finished before capturing it.
    deferred_packages = [case for case in PACKAGES if case in nodes]
    record['deferred_package_cases'] = deferred_packages
    handles = []

    def launch(label, group_selected, *, deferred=False):
        if not group_selected:
            return
        name = args.name + '-' + label
        plan = EVIDENCE / (name + '-selection.json')
        group_deselected = [] if deferred else list(deselected)
        if not deferred:
            group_deselected.extend(deferred_packages)
        with plan.open('x') as stream:
            stream.write(json.dumps({'selected': group_selected, 'deselected': group_deselected}, indent=2) + '\n')
        command = [sys.executable, '-B', str(ROOT / 'scripts/fpr4_run.py'), '--name', name,
                   '--selection', str(plan), '--evidence-dir', str(EVIDENCE)]
        if any(s.partition('::')[0] == 'tests/muse' or s.startswith('tests/muse/') for s in group_selected):
            command += ['--muse-python', args.muse_python]
        log = (EVIDENCE / (name + '-driver.log')).open('xb')
        try:
            process = subprocess.Popen(command, cwd=ROOT, env=runner_environment(args.muse_python),
                                       stdout=log, stderr=subprocess.STDOUT)
        except BaseException:
            log.close()
            raise
        row = {'name': name, 'command': command, 'selected': group_selected, 'deselected': group_deselected}
        record['groups'].append(row)
        handles.append((process, log, row))

    try:
        for label, group_selected in buckets.items():
            if label == 'latency':
                continue
            # Avoid a zero-case run when all explicit items are deferred.
            if group_selected and all(case in deferred_packages for case in group_selected):
                continue
            launch(label, group_selected)
        for process, log, row in handles:
            row['exit_code'] = process.wait()
            log.close()
        if buckets['latency']:
            print('Concurrent groups finished; running the isolated latency tier.', flush=True)
            launch('latency', buckets['latency'])
            process, log, row = handles[-1]
            row['exit_code'] = process.wait()
            log.close()
        if deferred_packages:
            print('Disjoint groups finished; running the deferred archive cases.', flush=True)
            launch('package', deferred_packages, deferred=True)
            process, log, row = handles[-1]
            row['exit_code'] = process.wait()
            log.close()
    except BaseException as exc:
        record['driver_error'] = repr(exc)
        for process, log, row in handles:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            row['exit_code'] = process.returncode
            log.close()
        target.write_text(json.dumps(record, indent=2) + '\n')
        raise

    actual, actual_nodes, cases, boundaries = Counter(), Counter(), [], []
    for row in record['groups']:
        try:
            detail = json.loads((EVIDENCE / (row['name'] + '.json')).read_text())
            boundaries.append(detail)
            _, group_nodes, _ = collection_counts(EVIDENCE / (row['name'] + '-collection.json'))
            actual_nodes.update(group_nodes)
            group_cases, _ = junit_results(EVIDENCE / (row['name'] + '.xml'))
            actual.update((case.get('classname'), case.get('name')) for case in group_cases)
            cases.extend(group_cases)
            row['evidence_ok'] = detail.get('ok', False)
        except (OSError, ValueError, KeyError, ET.ParseError) as exc:
            row['evidence_error'] = str(exc)
            row['evidence_ok'] = False
    try:
        exact_identities = junit_identities(cases) == Counter(row['node_sha256'] for row in collected_rows)
    except ValueError as exc:
        exact_identities = False
        record['identity_error'] = str(exc)
    record['exact_collection_executed_once'] = (actual_nodes == nodes and actual == expected and
                                               exact_identities and all(c == 1 for c in actual_nodes.values()))
    record['missing_junit_cases'] = simple_counter(expected - actual)
    record['unexpected_junit_cases'] = simple_counter(actual - expected)
    record['missing_collected_nodes'] = simple_counter(nodes - actual_nodes)
    record['unexpected_collected_nodes'] = simple_counter(actual_nodes - nodes)
    record['closing_boundary'] = snapshot(args.muse_python)
    opening = record['opening_boundary']
    record['same_source_runtime_dependencies'] = (bool(boundaries) and
        all(opening[key] == record['closing_boundary'][key] for key in BOUNDARY_KEYS) and
        all(d.get('boundary_unchanged') and
            all(d[side][key] == opening[key] for side in ('before', 'after') for key in BOUNDARY_KEYS)
            for d in boundaries))
    record['selection_unchanged'] = args.selection.read_bytes() == selection_bytes
    record['runtime'] = opening['runtime']
    record['results'] = {'tests': len(cases), 'failed': sum(c.find('failure') is not None for c in cases),
                         'errors': sum(c.find('error') is not None for c in cases),
                         'skipped': sum(c.find('skipped') is not None for c in cases),
                         'passed': sum(not any(c.find(tag) is not None for tag in ('failure', 'error', 'skipped')) for c in cases)}
    record['ok'] = (all(row['exit_code'] == 0 and row['evidence_ok'] for row in record['groups']) and
                    record['exact_collection_executed_once'] and record['same_source_runtime_dependencies'] and
                    record['selection_unchanged'] and not record['results']['skipped'])
    target.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ('ok', 'results', 'runtime', 'exact_collection_executed_once', 'same_source_runtime_dependencies')}, indent=2))
    return 0 if record['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
