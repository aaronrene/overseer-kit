"""Relocate preserved FPR-5 probes into a new nonrepository fixture directory."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ORIGINAL_ROOT = '/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014'
ORIGINAL_OUTPUT = '/private/tmp/overseer-fpr5-review.jTlE9P'
REVIEWED_HEAD = '4c62c17cff6c606a5e1ddf565e12353973b3bcad'
REVIEWED_RUNTIME = 'bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec'
SCRIPTS = {
    'foundation': ['repro_foundation.py'],
    'redirect': ['surfaces/repro_redirect.py'],
    'commands': ['surfaces/repro_cli.py'],
    'resources': ['authority/probe_resource_membership.py'],
    'http': ['surfaces/http_functional_supplement-r4.py'],
    'accounting': ['evidence/audit_disposition.py'],
    'semantics': ['evidence/audit_disposition.py', 'evidence/audit_semantics.py'],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=[*SCRIPTS, 'foundation-tests', 'authority-tests'])
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--output', type=Path,
                        help='A nonexistent directory below /private/tmp; default creates one.')
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    evidence = Path(__file__).resolve().parent
    python = repo / '.venv/bin/python3'
    if not python.is_file():
        parser.error('The selected repository needs its conventional .venv/bin/python3.')
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    if head != REVIEWED_HEAD:
        parser.error('This wrapper reproduces the fixed reviewed commit only. Adapt the raw probes and record a new boundary for repaired-source validation.')
    tracked = subprocess.run(['git', '-C', str(repo), 'diff', '--quiet', 'HEAD', '--'])
    if tracked.returncode:
        parser.error('Tracked source differs from the reviewed commit.')
    runtime = json.loads(subprocess.check_output([
        str(python), '-I', '-B', '-c',
        'import sys,json; sys.path.insert(0,sys.argv[1]); from cli.v1 import runtime; print(json.dumps(runtime()))',
        str(repo)], text=True))
    if runtime['sha256'] != REVIEWED_RUNTIME:
        parser.error('Runtime differs from the reviewed runtime.')
    # Do not overwrite a previous reproduction, including its pytest basetemp.
    if args.output is None:
        output = Path(tempfile.mkdtemp(prefix='overseer-fpr5-reproduce-', dir='/private/tmp'))
    else:
        output = args.output.resolve()
        if not output.is_relative_to(Path('/private/tmp')) or output == Path('/private/tmp'):
            parser.error('--output must be a new child of /private/tmp.')
        output.mkdir(parents=False, exist_ok=False)
    for name in ('foundation', 'authority', 'surfaces', 'evidence', 'scripts'):
        (output / name).mkdir()

    def relocate(value):
        return value.replace(ORIGINAL_ROOT, str(repo)).replace(ORIGINAL_OUTPUT, str(output))

    status = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain=v1'], text=True)
    record = {'case': args.case, 'head': head, 'runtime': runtime, 'repo': str(repo), 'output': str(output),
              'worktree_status': status, 'commands': [],
              'note': 'New reproduction, separate from the preserved original review evidence.'}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    commands = []
    if args.case.endswith('-tests'):
        group = args.case.removesuffix('-tests')
        original = json.loads((evidence / group / 'focused-command.json').read_text())
        argv = [relocate(value) for value in original['argv']]
        argv[0] = str(python)
        env.update(original['environment']['explicit_overrides'])
        commands.append((argv, output / group / 'focused.log'))
    else:
        for name in SCRIPTS[args.case]:
            source = evidence / name
            relocated = output / 'scripts' / source.name
            relocated.write_text(relocate(source.read_text()))
            argv = [str(python), '-I', '-B', '-c',
                    'import runpy,sys; sys.path.insert(0,sys.argv[1]); '
                    'p=sys.argv[2]; sys.argv=[p]+sys.argv[3:]; '
                    'runpy.run_path(p,run_name="__main__")', str(repo), str(relocated)]
            if args.case == 'foundation':
                argv.extend([str(repo), str(output / 'foundation')])
            commands.append((argv, output / (source.stem + '.log')))
    code = 0
    for argv, logfile in commands:
        row = {'argv': argv, 'log': str(logfile)}
        record['commands'].append(row)
        with logfile.open('w') as stream:
            proc = subprocess.run(argv, cwd=repo, env=env, stdout=stream, stderr=subprocess.STDOUT)
        row['exit_code'] = proc.returncode
        code = proc.returncode
        if code:
            break
    record['exit_code'] = code
    (output / 'reproduction.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
