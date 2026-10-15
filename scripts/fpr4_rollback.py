"""Disposable integrated source/configuration upgrade and rollback evidence.

Reads pinned committed objects only. Does not reuse the completed bounded exercise.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cli import v1
EVIDENCE = ROOT / 'docs/validation/fpr4/rollback-results.json'
CURRENT = '6289d2823184a63e2968d2c5f6a76abab5818368'
PREVIOUS = '695444fb5f8261391f5c273807129c13dc8db1fd'
BOUNDED = '348e0f323a3b17cd5022a1bfd56fa09a6831c51f'
record = {'source_commits': {'current': CURRENT, 'compatible_previous': PREVIOUS, 'bounded': BOUNDED},
          'commands': [], 'checks': [], 'limits': 'Author fixture exercise; no pilot, certification, release, provider or consumer.'}


def save():
    EVIDENCE.write_text(json.dumps(record, indent=2) + '\n')


def run(argv, *, cwd=ROOT, expected=0):
    result = subprocess.run(list(map(str, argv)), cwd=cwd, text=True, capture_output=True,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                                     GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1'), timeout=90)
    record['commands'].append({'argv': list(map(str, argv)), 'cwd': str(cwd), 'exit_code': result.returncode,
                               'stdout': result.stdout, 'stderr': result.stderr})
    save()
    assert (result.returncode == expected if expected is not None else result.returncode != 0), result.stdout + result.stderr
    return result


def check(name, condition):
    record['checks'].append({'name': name, 'passed': bool(condition)})
    save()
    assert condition, name


def source(commit, destination):
    raw = subprocess.check_output(['/usr/bin/git', '-C', str(ROOT), 'archive', commit])
    if destination.exists():
        for child in destination.iterdir():
            if child.name == '.venv':
                continue
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        archive.extractall(destination, filter='data')
    if commit == CURRENT:
        # The final candidate may include bounded FPR-4 repairs above its base.
        # Overlay and hash every bound runtime file, never borrow a neighboring installation.
        for relative in v1.runtime_files():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        record['current_runtime'] = v1.runtime()
        record['current_runtime_files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                           for p in v1.runtime_files()}
    record.setdefault('source_archive_sha256', {})[commit] = hashlib.sha256(raw).hexdigest()
    save()


def provision(installation):
    venv.EnvBuilder(with_pip=False, symlinks=True).create(installation / '.venv')
    # Copy this same interpreter's installed pinned dependencies offline.
    import sysconfig
    site = Path(run([installation / '.venv/bin/python', '-I', '-c',
                    'import sysconfig; print(sysconfig.get_path("purelib"))']).stdout.strip())
    original = Path(sysconfig.get_path('purelib'))
    for path in original.iterdir():
        if path.name == '__pycache__':
            continue
        if path.is_dir():
            shutil.copytree(path, site / path.name, ignore=shutil.ignore_patterns('__pycache__'))
        elif path.is_file():
            shutil.copyfile(path, site / path.name)
    run([installation / '.venv/bin/python', '-I', '-c',
         'import importlib.metadata,json; print(json.dumps({d.metadata["Name"]:d.version for d in importlib.metadata.distributions()},sort_keys=True))'])


def seed(root, installation):
    root.mkdir()
    for args in (['init', '-b', 'main'], ['config', 'user.name', 'FPR4 fixture'],
                 ['config', 'user.email', 'fixture@example.invalid'],
                 ['-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-m', 'seed']):
        run(['/usr/bin/git', '-C', root, *args])
    run([installation / 'cli/ok', '-C', root, 'init'])


def observe(root, installation):
    return json.loads(run([installation / 'cli/ok', '-C', root, 'status', '--json']).stdout)


def protected(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (root / 'docs').rglob('*') if p.is_file()}


def normalized_settings(config):
    value = yaml.safe_load(config)
    value.pop('runtime')
    return value


def compatible(parent):
    installation, repo = parent / 'compatible-install', parent / 'compatible-repo'
    source(PREVIOUS, installation)
    provision(installation)
    seed(repo, installation)
    path = repo / '.overseer/config.yaml'
    cfg = yaml.safe_load(path.read_bytes())
    cfg['thresholds']['realign_max_commits'] = 37
    cfg['docs']['lanes']['operations'] = {'handover': 'OPS-HANDOVER.md', 'roadmap': 'OPS-ROADMAP.md',
                                           'handover_title': 'Operations', 'roadmap_title': 'Operations roadmap',
                                           'repo_id': cfg['repo']['id']}
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    for name in ('OPS-HANDOVER.md', 'OPS-ROADMAP.md'):
        (repo / 'docs' / name).write_text('# Owner content: ' + name + '\n')
    original, docs = path.read_bytes(), protected(repo)
    old = observe(repo, installation)
    source(CURRENT, installation)
    refusal = run([installation / 'cli/ok', '-C', repo, 'status'], expected=None)
    check('compatible upgrade refuses stale runtime', 'runtime' in refusal.stderr)
    for dry in (['--dry-run'], []):
        run([repo / '.overseer/bin/ok', '-C', repo, 'sync', '--only', '.overseer/bin/ok', *dry])
    upgraded = path.read_bytes()
    new = observe(repo, installation)
    check('upgrade preserves all non-runtime settings/UUID/two lanes', normalized_settings(original) == normalized_settings(upgraded))
    check('upgrade preserves every living document and exact NEXT', docs == protected(repo))
    source(PREVIOUS, installation)
    run([installation / 'cli/ok', '-C', repo, 'status'], expected=None)
    path.write_bytes(original)
    restored = observe(repo, installation)
    check('previous source with matching byte-exact config restores binding', restored['runtime'] == old['runtime'])
    check('compatible rollback preserves docs and NEXT', protected(repo) == docs)
    source(CURRENT, installation)
    run([installation / 'cli/ok', '-C', repo, 'status'], expected=None)
    path.write_bytes(upgraded)
    final = observe(repo, installation)
    check('return to current restores exact runtime and full configuration', final['runtime'] == new['runtime'] and path.read_bytes() == upgraded)
    check('return to current preserves all docs and NEXT', protected(repo) == docs)


def bounded(parent):
    installation, repo = parent / 'schema-install', parent / 'schema-repo'
    source(BOUNDED, installation)
    provision(installation)
    seed(repo, installation)
    path = repo / '.overseer/config.yaml'
    old_config, docs = path.read_bytes(), protected(repo)
    source(CURRENT, installation)
    raw = run([installation / 'cli/ok', '-C', repo, 'init', '--migrate', '--dry-run', '--refresh-runtime', '--json'])
    plan = json.loads(raw.stdout)
    (repo / 'plan.json').write_text(raw.stdout)
    run([installation / 'cli/ok', '-C', repo, 'init', '--migrate', '--apply-plan', 'plan.json',
         '--expect-plan', plan['plan_sha256'], '--expect-config', plan['plan']['source_config_sha256']])
    upgraded = path.read_bytes()
    new = observe(repo, installation)
    check('bounded tracked schema1 upgrades to schema3', yaml.safe_load(upgraded)['schema'] == 3)
    check('bounded upgrade preserves UUID/docs/NEXT', yaml.safe_load(old_config)['repo']['id'] == new['repository']['id'] and docs == protected(repo))
    source(BOUNDED, installation)
    refusal = run([installation / 'cli/ok', '-C', repo, 'status'], expected=None)
    check('old bounded runtime refuses unknown schema3', 'schema' in refusal.stderr or 'configuration' in refusal.stderr)
    path.write_bytes(old_config)
    old = observe(repo, installation)
    check('matching schema1 rollback restores identity', old['repository']['id'] == new['repository']['id'])
    check('schema rollback preserves exact docs/NEXT', protected(repo) == docs)
    source(CURRENT, installation)
    path.write_bytes(upgraded)
    final = observe(repo, installation)
    check('schema cycle returns to same current binding/config/docs', final['runtime'] == new['runtime'] and path.read_bytes() == upgraded and docs == protected(repo))


def main():
    global EVIDENCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='rollback-results')
    args = parser.parse_args()
    assert '/' not in args.name
    EVIDENCE = EVIDENCE.with_name(args.name + '.json')
    assert not EVIDENCE.exists(), 'preserve earlier evidence'
    parent = Path(tempfile.mkdtemp(prefix='overseer-fpr4-rollback-', dir='/private/tmp'))
    record['fixture_parent'] = str(parent)
    record['python'] = sys.version
    save()
    try:
        compatible(parent)
        bounded(parent)
    except Exception as exc:
        record['failure'] = repr(exc)
        save()
        raise
    record['ok'] = True
    save()
    print(json.dumps({'ok': True, 'checks': len(record['checks']), 'fixture_parent': str(parent)}))


if __name__ == '__main__':
    main()
