"""Verify this observation-only closeout without repeating acceptance tests."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
PARENT = '7ee9a372e478ad251c17d8e8fd1a4118811c01b2'
GOVERNED = {'docs/NEXT.md', 'docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md', '.overseer/version.lock'}
sys.path.insert(0, str(ROOT))
from cli import v1

def git(*args):
    return subprocess.check_output(['/usr/bin/git', '-C', str(ROOT), *args], text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(path, row):
    assert path.is_file() and not path.is_symlink(), str(path)
    assert sha(path) == row['sha256'], str(path)
    assert path.stat().st_size == row['bytes'], str(path)
    assert path.stat().st_mode & 0o777 == row['mode'], str(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--closing-commit', action='store_true')
    args = parser.parse_args()
    initial = json.loads((ROOT / 'docs/validation/fpr5-repairs/opening.json').read_text())
    head = git('rev-parse', 'HEAD')
    assert str(ROOT.resolve()) == git('rev-parse', '--show-toplevel') == initial['physical_root']
    assert git('branch', '--show-current') == initial['branch']
    assert git('show', '-s', '--format=%P', head) == PARENT if args.closing_commit else head == PARENT
    refs = git('for-each-ref', '--format=%(refname) %(objectname)').splitlines()
    expected = [f"refs/heads/{initial['branch']} {head}" if line.startswith('refs/heads/' + initial['branch'] + ' ')
                else line for line in initial['initial_refs']]
    assert refs == expected
    names = git('ls-tree', '-r', '--name-only', PARENT, '--', 'docs/validation', 'docs/reviews', 'tests/historical').splitlines()
    assert not git('diff', '--name-only', PARENT, '--', *names)
    artifact = ROOT / 'docs/validation/fpr5-acceptance/ARTIFACTS.json'
    assert sha(artifact) == '9e0c4b8fc17a14d3ca84b622357c7af60b821ef4f88f12b9475643ea29b4016f'
    records = json.loads(artifact.read_text())
    for name, row in records['files'].items():
        verify(artifact.parent / name, row)
    assert {str(p.relative_to(artifact.parent)) for p in artifact.parent.rglob('*') if p.is_file()} == set(records['files']) | {'ARTIFACTS.json'}
    for name, row in records['companion_files'].items():
        if name not in GOVERNED:
            verify(ROOT / name, row)
    changed = git('diff', '--name-only', PARENT).splitlines()
    extra = git('ls-files', '--others', '--exclude-standard').splitlines()
    assert all(name in GOVERNED or name == 'docs/validation/FPR-5-INTERACTIVE.md'
               or name.startswith('docs/validation/fpr5-interactive/') for name in changed + extra), changed + extra
    runtime = v1.runtime()
    assert runtime['sha256'] == 'cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774'
    for name, row in initial['original_review'].items():
        verify(ROOT / name, row)
    historical = json.loads((ROOT / 'tests/historical/baseline-test-inventory.json').read_text())
    for row in historical:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    print(json.dumps({'ok': True, 'scope': 'Observation/evidence preservation; not independent adjudication',
        'head': head, 'parent_commit': PARENT, 'closing_commit': args.closing_commit,
        'refs': len(refs), 'original_review_files': len(initial['original_review']),
        'historical_test_files': len(historical), 'prior_evidence_paths_unchanged': len(names),
        'prior_acceptance_artifacts_verified': len(records['files']), 'runtime': runtime,
        'production_native_tests_dependencies_unchanged': True,
        'tracked_changes': changed, 'new_untracked_evidence': extra}, indent=2))

if __name__ == '__main__':
    main()
