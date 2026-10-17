"""Check the immutable FPR-5 inputs and historical records at repair closeout."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['/usr/bin/git', '-C', str(ROOT), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--closing-commit', action='store_true')
    args = parser.parse_args()
    opening = json.loads((ROOT / 'docs/validation/fpr5-repairs/opening.json').read_text())
    assert str(ROOT.resolve()) == opening['physical_root'] == git('rev-parse', '--show-toplevel')
    assert git('branch', '--show-current') == opening['branch']
    head = git('rev-parse', 'HEAD')
    initial = opening['initial']['head']
    if args.closing_commit:
        assert git('show', '-s', '--format=%P', head) == initial
    else:
        assert head == initial
    refs = git('for-each-ref', '--format=%(refname) %(objectname)').splitlines()
    expected_refs = opening['initial_refs']
    if args.closing_commit:
        expected_refs = [line.replace(initial, head) if line.startswith('refs/heads/' + opening['branch'] + ' ')
                         else line for line in expected_refs]
    assert refs == expected_refs
    for name, row in opening['original_review'].items():
        path = ROOT / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], name
        assert path.stat().st_size == row['bytes'], name
        assert path.stat().st_mode & 0o777 == row['mode'], name
    actual_review = {'docs/reviews/FPR-5-REVIEW.md'} | {
        str(path.relative_to(ROOT)) for path in (ROOT / 'docs/reviews/fpr5').rglob('*') if path.is_file()}
    assert actual_review == set(opening['original_review'])
    historical = json.loads((ROOT / 'tests/historical/baseline-test-inventory.json').read_text())
    for row in historical:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    # Compare every previously tracked validation/review artifact and original
    # test inventory to the initial commit, including the raw failed runs.
    names = git('ls-tree', '-r', '--name-only', initial, '--',
                'docs/validation', 'docs/reviews', 'tests/historical').splitlines()
    changed = git('diff', '--name-only', initial, '--', *names).splitlines()
    assert not changed, changed
    for name, sha in opening['preservation'].items():
        if name in {'.overseer/config.yaml', 'docs/NEXT.md', 'docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md'}:
            continue  # These four have explicit repair-closeout authorization.
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name
    print(json.dumps({'ok': True, 'head': head, 'refs': len(refs),
                      'original_review_files': len(actual_review),
                      'original_test_files': len(historical),
                      'prior_tracked_evidence_files': len(names),
                      'scope': 'Preservation check; not independent adjudication'}, indent=2))


if __name__ == '__main__':
    main()
