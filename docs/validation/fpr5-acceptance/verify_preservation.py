"""Read-only acceptance preservation check; no independent certification."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
OPENING = '2e8ec694def9be4a0faa4a994bf2fff3f212ab23'
NATIVE = 'desktop/src-tauri/tauri.conf.json'
NATIVE_SHA = 'd65242ef9ca4be228e791d7596bd2a60ff90ba200445c0d5dbf58229c5eecab6'
sys.path.insert(0, str(ROOT))
from cli import v1

def git(*args):
    return subprocess.check_output(['/usr/bin/git', '-C', str(ROOT), *args], text=True).strip()

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify_row(p, row):
    assert p.is_file() and not p.is_symlink(), str(p)
    assert digest(p) == row['sha256'], str(p)
    if 'bytes' in row:
        assert p.stat().st_size == row['bytes'], str(p)
    if 'mode' in row:
        assert p.stat().st_mode & 0o777 == row['mode'], str(p)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--closing-commit', action='store_true')
    args = parser.parse_args()
    base = ROOT / 'docs/validation/fpr5-repairs'
    original = json.loads((base / 'opening.json').read_text())
    prior = json.loads((base / 'integrated/repaired-packages-package.json').read_text())['after']
    assert str(ROOT.resolve()) == git('rev-parse', '--show-toplevel') == original['physical_root']
    assert git('branch', '--show-current') == original['branch']
    head = git('rev-parse', 'HEAD')
    if args.closing_commit:
        assert git('show', '-s', '--format=%P', head) == OPENING
    else:
        assert head == OPENING
    refs = git('for-each-ref', '--format=%(refname) %(objectname)').splitlines()
    expected = [f"refs/heads/{original['branch']} {head}" if line.startswith('refs/heads/' + original['branch'] + ' ')
                else line for line in original['initial_refs']]
    assert refs == expected
    for name, row in original['original_review'].items():
        verify_row(ROOT / name, row)
    actual_review = {'docs/reviews/FPR-5-REVIEW.md'} | {
        str(p.relative_to(ROOT)) for p in (ROOT / 'docs/reviews/fpr5').rglob('*') if p.is_file()}
    assert actual_review == set(original['original_review'])
    historical = json.loads((ROOT / 'tests/historical/baseline-test-inventory.json').read_text())
    for row in historical:
        assert digest(ROOT / row['path']) == row['sha256']
    names = git('ls-tree', '-r', '--name-only', OPENING, '--',
                'docs/validation', 'docs/reviews', 'tests/historical').splitlines()
    assert not git('diff', '--name-only', OPENING, '--', *names)
    artifacts = json.loads((base / 'ARTIFACTS.json').read_text())
    assert digest(base / 'ARTIFACTS.json') == '72a48127b26bd1860e7ab4006c46a083e09a08d0bce2aa6d83be98e298ccadc5'
    for name, row in artifacts['files'].items():
        verify_row(base / name, row)
    governed = {'docs/NEXT.md', 'docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md', '.overseer/version.lock'}
    for name, row in artifacts['companion_files'].items():
        if name not in governed:
            verify_row(ROOT / name, row)
    for key in ('runtime_files', 'test_sources', 'validation_scripts', 'native_sources', 'packaging_sources', 'requirements'):
        for name, sha in prior[key].items():
            assert digest(ROOT / name) == (NATIVE_SHA if name == NATIVE else sha), (key, name)
    runtime = v1.runtime()
    assert runtime['sha256'] == 'cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774'
    current_runtime = {name: digest(ROOT / name) for name in v1.runtime_files()}
    assert current_runtime == prior['runtime_files']
    allowed = governed | {NATIVE}
    tracked_changes = git('diff', '--name-only', OPENING).splitlines()
    assert all(name in allowed or name == 'docs/validation/FPR-5-ACCEPTANCE.md'
               or name.startswith('docs/validation/fpr5-acceptance/') for name in tracked_changes), tracked_changes
    print(json.dumps({'ok': True, 'kind': 'Author preservation check; not adjudication',
        'head': head, 'closing_commit': args.closing_commit, 'refs': len(refs),
        'original_review_files': len(actual_review), 'original_historical_tests': len(historical),
        'unchanged_prior_evidence': len(names), 'repair_evidence_files': len(artifacts['files']),
        'runtime': runtime, 'runtime_files': len(current_runtime), 'test_files': len(prior['test_sources']),
        'native_change': {'path': NATIVE, 'before': prior['native_sources'][NATIVE], 'after': NATIVE_SHA},
        'other_native_files_unchanged': len(prior['native_sources']) - 1,
        'tracked_changes_since_opening': tracked_changes}, indent=2))

if __name__ == '__main__':
    main()
