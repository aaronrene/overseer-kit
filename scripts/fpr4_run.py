"""Record an offline FPR-4 fixture run and its exact source/environment boundary.

The optional pytest plugin hook emits lossless collection JSON. Node identifiers
are never reconstructed by splitting parameter text or scraping terminal output.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cli import v1

COLLECTION_ENV = 'OVERSEER_FPR4_COLLECTION'
BOUNDARY_KEYS = ('physical_cwd', 'git_root', 'branch', 'head', 'parents', 'runtime',
                 'runtime_files', 'test_sources', 'python', 'executable', 'prefix',
                 'platform', 'machine', 'git', 'dependencies', 'requirements',
                 'refs', 'validation_scripts', 'native_sources', 'packaging_sources', 'muse_runtime')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['/usr/bin/git', '-C', str(ROOT), *args], text=True).strip()


def snapshot(muse_python=None):
    files = {name: sha(ROOT / name) for name in v1.runtime_files()}
    source_names = subprocess.check_output(['/usr/bin/git', '-C', str(ROOT), 'ls-files', '-z',
                                            '--cached', '--others', '--exclude-standard']).decode().split('\0')
    native = {name: sha(ROOT / name) for name in sorted(set(source_names))
              if name.startswith('desktop/') and (ROOT / name).is_file()
              and not {'target', 'resources', 'node_modules', '__pycache__'}.intersection(Path(name).parts)}
    muse_python = muse_python or os.environ.get('FPR2_MUSE_PYTHON')
    muse_runtime = None
    if muse_python:
        probe = subprocess.run([muse_python, '-I', '-B', '-c',
            "import hashlib,importlib.metadata,json,pathlib,sys,muse; "
            "root=pathlib.Path(muse.__file__).resolve().parent; "
            "print(json.dumps({'python':sys.version,'executable':sys.executable,'prefix':sys.prefix,"
            "'module_root':str(root),'version':importlib.metadata.version('muse'),"
            "'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},"
            "'source_files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() "
            "for p in sorted(root.rglob('*.py'))}}))"],
            capture_output=True, text=True, timeout=30, check=True)
        muse_runtime = json.loads(probe.stdout)
    return {
        'physical_cwd': str(Path.cwd().resolve()), 'git_root': git('rev-parse', '--show-toplevel'),
        'branch': git('branch', '--show-current'), 'head': git('rev-parse', 'HEAD'),
        'parents': git('show', '-s', '--format=%P', 'HEAD').split(),
        'runtime': v1.runtime(), 'runtime_files': files,
        'test_sources': {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'tests').rglob('*'))
                         if p.is_file() and '__pycache__' not in p.parts},
        'validation_scripts': {str(p.relative_to(ROOT)): sha(p)
                               for p in sorted((ROOT / 'scripts').glob('fpr4_*.py'))},
        'native_sources': native,
        'packaging_sources': {name: sha(ROOT / name) for name in sorted(set(source_names))
                              if name == 'pyproject.toml' or name.startswith(('.github/workflows/', 'scripts/'))
                              if (ROOT / name).is_file()},
        'muse_runtime': muse_runtime,
        'python': sys.version, 'executable': sys.executable, 'prefix': sys.prefix,
        'platform': platform.platform(), 'machine': platform.machine(),
        'git': subprocess.check_output(['/usr/bin/git', '--version'], text=True).strip(),
        'dependencies': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
        'requirements': {p: sha(ROOT / p) for p in ('requirements-v1.txt', 'requirements-v1-dev.txt')},
        'refs': git('for-each-ref', '--format=%(refname) %(objectname)').splitlines(),
    }


def runner_environment(muse_python=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_GLOBAL='/dev/null',
               GIT_CONFIG_NOSYSTEM='1', GIT_OPTIONAL_LOCKS='0', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    for key in ('PYTEST_ADDOPTS', 'PYTEST_PLUGINS', COLLECTION_ENV):
        env.pop(key, None)
    if muse_python:
        env['FPR2_MUSE_PYTHON'] = muse_python
    return env


def junit_key(nodeid, prefix=None):
    # Match the installed, recorded pytest version, including parameter text
    # containing ::, brackets, newlines or characters XML cannot represent.
    from _pytest.junitxml import bin_xml_escape, mangle_test_address
    names = mangle_test_address(nodeid)
    classes = names[:-1]
    if prefix:
        classes.insert(0, prefix)
    return '.'.join(classes), bin_xml_escape(names[-1])


def pytest_collection_finish(session):
    destination = os.environ.get(COLLECTION_ENV)
    if not destination:
        return
    prefix = getattr(session.config.option, 'junitprefix', None)
    rows = []
    for item in session.items:
        identity = hashlib.sha256(item.nodeid.encode('utf-8', 'surrogatepass')).hexdigest()
        item.user_properties.append(('fpr4_nodeid_sha256', identity))
        rows.append({'nodeid': item.nodeid, 'node_sha256': identity,
                     'junit': list(junit_key(item.nodeid, prefix))})
    with Path(destination).open('x') as stream:
        json.dump({'schema': 1, 'pytest': importlib.metadata.version('pytest'),
                   'cases': rows}, stream, indent=2)
        stream.write('\n')


def collection_counts(path):
    cases = json.loads(path.read_text())['cases']
    return cases, Counter(row['nodeid'] for row in cases), Counter(tuple(row['junit']) for row in cases)


def junit_results(path):
    cases = list(ET.parse(path).iter('testcase'))
    results = {'tests': len(cases), 'failed': sum(c.find('failure') is not None for c in cases),
               'errors': sum(c.find('error') is not None for c in cases),
               'skipped': sum(c.find('skipped') is not None for c in cases)}
    results['passed'] = sum(not any(c.find(tag) is not None for tag in ('failure', 'error', 'skipped'))
                            for c in cases)
    return cases, results


def junit_identities(cases):
    identities = Counter()
    for case in cases:
        values = [p.get('value') for p in case.findall('properties/property')
                  if p.get('name') == 'fpr4_nodeid_sha256']
        if len(values) != 1:
            raise ValueError('JUnit case missing its unique collected-node identity')
        identities[values[0]] += 1
    return identities


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--name', required=True)
    p.add_argument('--selection', type=Path, required=True)
    p.add_argument('--muse-python')
    p.add_argument('--evidence-dir', type=Path, default=ROOT / 'docs/validation/fpr4',
                   help='New evidence destination; existing runs are never overwritten.')
    args = p.parse_args()
    if Path(sys.prefix).resolve() != ROOT / '.venv':
        p.error("use this installation's conventional .venv")
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}', args.name):
        p.error('name must be a simple evidence basename')
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    paths = {kind: evidence / (args.name + suffix) for kind, suffix in
             [('record', '.json'), ('log', '.log'), ('xml', '.xml'), ('collection', '-collection.json')]}
    if any(path.exists() for path in paths.values()):
        p.error('evidence name already exists; preserve prior runs')
    selection_bytes = args.selection.read_bytes()
    selection = json.loads(selection_bytes)
    selected, deselected = (selection['selected'], selection.get('deselected', [])) if isinstance(selection, dict) else (selection, [])
    if not selected or not all(isinstance(s, str) and s for s in selected + deselected):
        p.error('selection must contain explicit nonempty pytest selectors')
    fixture = tempfile.mkdtemp(prefix='overseer-fpr4-' + args.name + '-', dir='/private/tmp')
    command = [sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
               '-p', 'scripts.fpr4_run', '--rootdir=' + str(ROOT), '-c', str(ROOT / 'pyproject.toml'),
               *selected, *['--deselect=' + item for item in deselected],
               '--basetemp=' + fixture, '--junitxml=' + str(paths['xml'])]
    if args.muse_python:
        command += ['--muse-python', args.muse_python]
    env = runner_environment(args.muse_python)
    env[COLLECTION_ENV] = str(paths['collection'])
    record = {'command': command, 'cwd': str(ROOT), 'fixture_parent': fixture,
              'selection_file': str(args.selection), 'selection_sha256': hashlib.sha256(selection_bytes).hexdigest(),
              'before': snapshot(args.muse_python), 'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'collection_file': str(paths['collection']),
              'runner_environment': {'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'PYTEST_ADDOPTS': 'removed', 'PYTEST_PLUGINS': 'removed'}}
    with paths['record'].open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    start = time.monotonic()
    with paths['log'].open('xb') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    record.update(exit_code=result.returncode, seconds=time.monotonic() - start, after=snapshot(args.muse_python))
    record['runtime_unchanged'] = all(record['before'][key] == record['after'][key] for key in ('runtime', 'runtime_files'))
    record['test_sources_unchanged'] = record['before']['test_sources'] == record['after']['test_sources']
    record['boundary_unchanged'] = all(record['before'][key] == record['after'][key] for key in BOUNDARY_KEYS)
    record['selection_unchanged'] = args.selection.read_bytes() == selection_bytes
    try:
        cases, record['results'] = junit_results(paths['xml'])
        collected, node_counts, expected = collection_counts(paths['collection'])
        actual = Counter((c.get('classname'), c.get('name')) for c in cases)
        record['unique_collected_nodes'] = bool(node_counts) and all(count == 1 for count in node_counts.values())
        record['exact_collection_executed_once'] = (record['unique_collected_nodes'] and actual == expected and
            junit_identities(cases) == Counter(row['node_sha256'] for row in collected))
        record['nonpassing'] = [{'case': (c.get('classname') or '') + '::' + (c.get('name') or ''),
                                'outcome': e.tag, 'message': e.get('message')}
                               for c in cases for e in c if e.tag in ('failure', 'error', 'skipped')]
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        record['evidence_error'] = str(exc)
        record['exact_collection_executed_once'] = False
    record['ok'] = (result.returncode == 0 and record['boundary_unchanged'] and record['selection_unchanged']
                    and record['exact_collection_executed_once'] and not record.get('results', {}).get('skipped'))
    paths['record'].write_text(json.dumps(record, indent=2) + '\n')
    # Full identifiers stay in JSON/XML; terminal summaries cannot be flooded by
    # deliberately huge parameter IDs from hostile-input tests.
    print(json.dumps({k: record.get(k) for k in ('ok', 'exit_code', 'seconds', 'boundary_unchanged',
                                                'exact_collection_executed_once', 'results', 'evidence_error')}, indent=2))
    return 0 if record['ok'] else (result.returncode or 1)


if __name__ == '__main__':
    raise SystemExit(main())
