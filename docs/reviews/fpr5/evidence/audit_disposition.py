"""Independent read-only reconciliation of fixed FPR-4 records; no test execution."""
import collections
import hashlib
import json
import pathlib
import subprocess
import xml.etree.ElementTree as ET

ROOT = pathlib.Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
OUT = pathlib.Path('/private/tmp/overseer-fpr5-review.jTlE9P/evidence')
BASE = ROOT / 'docs/validation/fpr4'

def read(name):
    return json.loads((BASE / name).read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(revision, path):
    return subprocess.check_output(['git', 'show', revision + ':' + path], cwd=ROOT)

def matches(selector, node):
    return selector == node or node.startswith(selector + '[') or node.startswith(selector + '::')

errors = []
raw = read('combined-final.json')
recorded_outcomes = read('disposition-final-outcomes.json')
audit = read('disposition-audit.json')
closing = read('closing-source.json')
baseline = json.loads((ROOT / 'docs/validation/baseline-failures.json').read_text())
baseline_by_node = {row['node']: row for row in baseline['failures']}
cases = {}
runs = []
boundary_keys = ('runtime', 'runtime_files', 'validation_scripts', 'native_sources',
                 'packaging_sources', 'muse_runtime', 'python', 'dependencies', 'requirements')
for name in [row['name'] for row in raw['groups']] + ['import-boundary-final-rerun']:
    run = read(name + '.json')
    collection = read(name + '-collection.json')['cases']
    by_sha = {row['node_sha256']: row for row in collection}
    if len(by_sha) != len(collection):
        errors.append([name, 'duplicate collection digest'])
    for row in collection:
        if sha(row['nodeid'].encode()) != row['node_sha256']:
            errors.append([name, 'node digest mismatch', row])
    xml_cases = list(ET.parse(BASE / (name + '.xml')).iter('testcase'))
    outcomes = collections.Counter()
    seen = set()
    for case in xml_cases:
        props = {p.attrib['name']: p.attrib['value'] for p in case.findall('./properties/property')}
        digest = props.get('fpr4_nodeid_sha256')
        entry = by_sha.get(digest)
        if entry is None:
            errors.append([name, 'JUnit missing collection entry', case.attrib]); continue
        if [case.attrib['classname'], case.attrib['name']] != entry['junit']:
            errors.append([name, 'JUnit textual identity mismatch', entry])
        if digest in seen:
            errors.append([name, 'duplicate JUnit case', entry])
        seen.add(digest)
        outcome = next((kind for tag, kind in [('failure', 'failed'), ('error', 'error'), ('skipped', 'skipped')]
                        if case.find(tag) is not None), 'passed')
        outcomes[outcome] += 1
        identifier = name + ':' + digest
        cases[identifier] = {'nodeid': entry['nodeid'], 'outcome': outcome, 'xml': str((BASE / (name + '.xml')).relative_to(ROOT))}
        existing = recorded_outcomes['cases'].get(identifier)
        if existing is None or any(existing[k] != cases[identifier][k] for k in ('nodeid', 'outcome', 'xml')):
            errors.append([name, 'outcome-map mismatch', identifier])
    if seen != set(by_sha):
        errors.append([name, 'missing JUnit case', sorted(set(by_sha) - seen)])
    if run['before'] != run['after']:
        errors.append([name, 'before/after boundary mismatch'])
    for key in boundary_keys:
        if run['before'][key] != raw['opening_boundary'][key]:
            errors.append([name, 'combined production/dependency boundary mismatch', key])
    runs.append({'name': name, 'cases': len(collection), 'outcomes': dict(outcomes), 'exit_code': run['exit_code']})

if set(cases) != set(recorded_outcomes['cases']):
    errors.append(['all cases', 'outcome-map key mismatch'])
passing = {row['nodeid'] for row in cases.values() if row['outcome'] == 'passed'}
closeout = read('disposition-closeout-collection.json')['cases']
if len(passing) != 1209 or len(closeout) != len({r['nodeid'] for r in closeout}) or passing != {r['nodeid'] for r in closeout}:
    errors.append(['closeout', 'passing union mismatch'])
historical = []
for row in audit['historical_failures']:
    source = baseline_by_node.get(row['historical_node'])
    if source is None or source['category'] != row['historical_category'] or source['message'] != row['historical_message']:
        errors.append(['historical source mismatch', row['historical_node']])
    selected = [c for c in cases.values() if matches(row['original_pytest_node'], c['nodeid'])]
    if bool(selected) != row['original_selected_now']:
        errors.append(['original selection mismatch', row['historical_node']])
    verified = []
    for entry in row['final_original_evidence'] + row['final_successor_evidence']:
        ids = entry['case_ids']
        expected = {k for k, c in cases.items() if matches(entry['selector'], c['nodeid'])}
        if set(ids) != expected or any(k not in cases for k in ids):
            errors.append(['historical outcome mapping mismatch', row['historical_node'], entry['selector']])
        if any(cases[k]['outcome'] != 'passed' for k in ids):
            errors.append(['historical nonpassing successor', row['historical_node'], entry['selector']])
        verified.extend(ids)
    if not verified:
        errors.append(['historical no passing coverage', row['historical_node']])
    historical.append({'historical_node': row['historical_node'], 'category': row['historical_category'],
                       'original_selected': row['original_selected_now'], 'verified_case_ids': sorted(set(verified)),
                       'successor_nodes': row['successor_nodes'], 'contract_reason': row['contract_reason']})
if len(historical) != 104 or {r['historical_node'] for r in historical} != set(baseline_by_node):
    errors.append(['historical list mismatch'])

originals = []
for row in audit['files']:
    path = row['path']
    disk = (ROOT / path).read_bytes()
    original = blob('d47291d5d9030de5ebef713da95efa978c4d8c6e', path)
    committed = blob('HEAD', path)
    if sha(disk) != row['sha256'] or disk != original or disk != committed:
        errors.append(['original file preservation mismatch', path])
    originals.append(path)

manifests = {}
for key in ('runtime_files', 'test_sources', 'validation_scripts', 'native_sources', 'packaging_sources', 'requirements'):
    mapping = closing['snapshot'][key]
    for path, digest in mapping.items():
        if sha((ROOT / path).read_bytes()) != digest or sha(blob('HEAD', path)) != digest:
            errors.append(['closing manifest mismatch', key, path])
    manifests[key] = len(mapping)

source_map = json.loads((ROOT / 'docs/validation/fpr3/source-disposition.json').read_text())
source_map_changes = []
for row in source_map['files']:
    path = row['path']
    if sha(blob('6289d2823184a63e2968d2c5f6a76abab5818368', path)) != row['sha256']:
        errors.append(['FPR3 source map opening hash mismatch', path])
    if sha((ROOT / path).read_bytes()) != row['sha256']:
        source_map_changes.append(path)
    for source in row['exact_sources']:
        if sha(blob(source_map['pins'][source], path)) != row['sha256']:
            errors.append(['source map exact-source mismatch', path, source])

expected_refs = dict(line.split(' ', 1) for line in closing['snapshot']['refs'])
actual_refs = dict(line.split(' ', 1) for line in subprocess.check_output(
    ['git', 'for-each-ref', '--format=%(refname) %(objectname)'], cwd=ROOT, text=True).splitlines())
ref_delta = {name: {'before': expected_refs.get(name), 'after': actual_refs.get(name)}
             for name in expected_refs.keys() | actual_refs.keys() if expected_refs.get(name) != actual_refs.get(name)}
expected_ref_delta = {'refs/heads/feat/overseer-v1-recovery-20261014': {
    'before': '6289d2823184a63e2968d2c5f6a76abab5818368', 'after': '4c62c17cff6c606a5e1ddf565e12353973b3bcad'}}
if ref_delta != expected_ref_delta:
    errors.append(['unexpected ref changes', ref_delta])
preserved = read('opening.json')['preserved']
for path, digest in preserved.items():
    if sha((ROOT / path).read_bytes()) != digest or sha(blob('HEAD', path)) != digest:
        errors.append(['preserved evidence mismatch', path])
index_modes = {line.split('\t', 1)[1]: line.split(' ', 1)[0] for line in
               subprocess.check_output(['git', 'ls-files', '-s'], cwd=ROOT, text=True).splitlines()}
mode_count = 0
for key in ('runtime_files', 'test_sources', 'validation_scripts', 'native_sources', 'packaging_sources', 'requirements'):
    for path in closing['snapshot'][key]:
        executable = bool((ROOT / path).stat().st_mode & 0o111)
        if executable != (index_modes[path] == '100755'):
            errors.append(['manifest executable-mode mismatch', path])
        mode_count += 1

result = {'scope': 'Independent read-only evidence reconciliation; no product tests executed and no separate verdict.',
          'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'runtime': raw['opening_boundary']['runtime'], 'raw_and_supplemental_runs': runs,
          'passing_current_contract_union': len(passing), 'historical_rows': len(historical),
          'historical_categories': dict(collections.Counter(r['category'] for r in historical)),
          'historical_originals_selected': sum(r['original_selected'] for r in historical),
          'original_files_verified_against_D_HEAD_disk': len(originals), 'closing_manifests': manifests,
          'source_map_entries': len(source_map['files']), 'source_map_fpr4_changes': source_map_changes,
          'refs_verified': len(actual_refs), 'permitted_ref_delta': ref_delta,
          'preserved_evidence_hashes': preserved, 'manifest_executable_modes_checked': mode_count,
          'errors': errors}
(OUT / 'independent-evidence-accounting.json').write_text(json.dumps(result, indent=2) + '\n')
(OUT / 'independent-historical-rows.json').write_text(json.dumps(historical, indent=2) + '\n')
print(json.dumps(result, indent=2))
