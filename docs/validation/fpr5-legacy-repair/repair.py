"""Confined offline dependency addition and guarded rollback for FPR-OPS-2.

No package manager, network, wrapper change, source change or bytecode writes.
Preparation is mandatory; apply refuses changed inputs or an unverified rehearsal.
"""
import argparse
import base64
import csv
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
LEGACY = ROOT.parent / 'overseer-kit-main-stable'
TARGET = LEGACY / '.venv'
SITE = Path('lib/python3.14/site-packages')
PROVENANCE = ROOT / 'docs/validation/fpr4/distribution-repaired-results.json'
PROVENANCE_SHA = 'ca4351d12e79fb47e0c2d0ab0e88a83513d475978e2f4d7cf8542d77df3490c3'
OLD_LINKS = {
    str(SITE/'PyYAML-6.0.1.dist-info'): '/opt/homebrew/lib/python3.10/site-packages/PyYAML-6.0.1.dist-info',
    str(SITE/'yaml'): '/opt/homebrew/lib/python3.10/site-packages/yaml',
}


def xattrs(path):
    # This macOS Python lacks os.listxattr; read the native no-follow API.
    libc = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    libc.listxattr.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
    libc.listxattr.restype = ctypes.c_ssize_t
    libc.getxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p,
                              ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]
    libc.getxattr.restype = ctypes.c_ssize_t
    raw = os.fsencode(path)
    size = libc.listxattr(raw, None, 0, 1)
    assert size >= 0, ('listxattr', path, ctypes.get_errno())
    names = ctypes.create_string_buffer(size)
    assert libc.listxattr(raw, names, size, 1) == size
    result = {}
    for name in sorted(names.raw.rstrip(b'\0').split(b'\0')) if size else []:
        length = libc.getxattr(raw, name, None, 0, 0, 1)
        assert length >= 0, ('getxattr', path, name, ctypes.get_errno())
        value = ctypes.create_string_buffer(length)
        assert libc.getxattr(raw, name, value, length, 0, 1) == length
        result[os.fsdecode(name)] = base64.b64encode(value.raw).decode()
    return result


def clone_tree(source, dest):
    assert not dest.exists()
    subprocess.run(['/usr/bin/ditto', '--rsrc', '--extattr', '--acl', str(source), str(dest)], check=True)
    # ditto preserves xattrs/ACLs but refreshes symlink and empty-directory mtimes.
    for path in sorted(source.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        shutil.copystat(path, dest/path.relative_to(source), follow_symlinks=False)
    shutil.copystat(source, dest, follow_symlinks=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def snapshot(root):
    result = {}
    def visit(path):
        info = path.lstat()
        row = {'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
               'gid': info.st_gid, 'mtime_ns': info.st_mtime_ns,
               'flags': info.st_flags,
               'xattrs': xattrs(path)}
        if path.is_symlink():
            row.update(kind='symlink', target=os.readlink(path))
        elif path.is_dir():
            row['kind'] = 'directory'
        elif path.is_file():
            row.update(kind='file', bytes=info.st_size, sha256=sha(path))
        else:
            raise RuntimeError(f'unsupported filesystem object: {path}')
        result[str(path.relative_to(root))] = row
        if row['kind'] == 'directory':
            for child in sorted(path.iterdir()):
                visit(child)
    visit(root)
    return result


def assert_originals_preserved(before, after):
    for name, row in before.items():
        if name in OLD_LINKS:
            continue
        actual = dict(after[name])
        expected = dict(row)
        if row['kind'] == 'directory':
            actual.pop('mtime_ns'); expected.pop('mtime_ns')
        assert actual == expected, ('original entry changed', name)


def add_payload(venv, bundle, files):
    site = venv / SITE
    assert site.resolve() == site and not site.is_symlink()
    for name, expected in OLD_LINKS.items():
        link = venv / name
        assert link.is_symlink() and os.readlink(link) == expected
        link.unlink()  # Unlink only the venv alias; never follow or change its target.
    for name, expected in files.items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        source, dest = bundle / relative, site / relative
        assert source.is_file() and not source.is_symlink() and sha(source) == expected
        assert not dest.exists() and not dest.is_symlink(), ('refusing overwrite', dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        assert dest.parent.resolve().is_relative_to(site)
        with dest.open('xb') as stream:
            stream.write(source.read_bytes())
            stream.flush(); os.fsync(stream.fileno())
        shutil.copystat(source, dest)
        assert sha(dest) == expected


def restore_added(venv, backup, before, expected_after):
    assert snapshot(venv) == expected_after, 'environment changed; rollback refused'
    assert snapshot(backup) == before, 'backup changed; rollback refused'
    added = set(expected_after) - set(before)
    for name in sorted(added, key=lambda value: (len(Path(value).parts), value), reverse=True):
        path = venv / name
        if expected_after[name]['kind'] == 'directory':
            path.rmdir()
        else:
            path.unlink()
    # Native clone preserves the original links' macOS xattrs; move just those
    # links into place without changing either external Python 3.10 directory.
    temporary = Path(tempfile.mkdtemp(prefix='rollback-links-', dir=backup.parent))
    try:
        clone = temporary/'venv'
        clone_tree(backup, clone)
        assert snapshot(clone) == before
        for name in OLD_LINKS:
            dest = venv/name
            if dest.is_symlink():
                dest.unlink()
            elif dest.exists():
                dest.rmdir()
            os.replace(clone/name,dest)
    finally:
        shutil.rmtree(temporary)
    for name in sorted(before, key=lambda value: len(Path(value).parts), reverse=True):
        if before[name]['kind'] == 'directory':
            shutil.copystat(backup / name, venv / name, follow_symlinks=False)
    assert snapshot(venv) == before, 'rollback metadata/content mismatch'


def command(argv, cwd, env, records):
    p = subprocess.run([str(a) for a in argv], cwd=cwd, env=env,
                       text=True, capture_output=True)
    records.append({'argv': [str(a) for a in argv], 'cwd': str(cwd),
                    'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    return p


def validate(venv, use_shim=False):
    # Explicit environment: no inherited PYTHONPATH, user-site, provider config,
    # package caches or credentials. HOME is neither changed nor supplied.
    env = {'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1',
           'PYTHONNOUSERSITE': '1', 'PYTHONPATH': str(LEGACY),
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}
    records = []
    probe = '''import sys, json, platform, importlib.metadata as md
from pathlib import Path
import yaml, yaml._yaml, cryptography, cffi, _cffi_backend, pycparser
from cryptography.hazmat.primitives import hashes
expected = {"PyYAML":"6.0.3", "cryptography":"49.0.0", "cffi":"2.1.0", "pycparser":"3.0"}
assert {name:md.version(name) for name in expected} == expected
assert sys.version_info[:3] == (3,14,4) and platform.machine() == "arm64"
assert yaml.safe_load("repair: true") == {"repair":True}
assert cffi.FFI().sizeof("int") > 0
assert pycparser.CParser().parse("int fixture;") is not None
h=hashes.Hash(hashes.SHA256()); h.update(b"offline dependency compatibility")
assert len(h.finalize()) == 32
paths={m.__name__:m.__file__ for m in [yaml,cryptography,cffi,_cffi_backend,pycparser]}
assert all(Path(p).is_relative_to(Path(sys.prefix)) for p in paths.values())
print(json.dumps({"version":sys.version,"prefix":sys.prefix,"executable":sys.executable,
 "resolved_interpreter":str(Path(sys.executable).resolve()),"machine":platform.machine(),
 "packages":expected,"module_paths":paths,"native_dependency_operations":"passed"},indent=2))
'''
    with tempfile.TemporaryDirectory(prefix='fpr5-ops2-check-') as temp:
        fixture = Path(temp).resolve()
        p = command([venv/'bin/python3', '-I', '-B', '-c', probe], fixture, env, records)
        assert p.returncode == 0, records[-1]
        executable = [LEGACY/'cli/ok'] if use_shim else [venv/'bin/python3', '-B', '-s', '-m', 'cli.main']
        p = command([*executable, '--help'], fixture, env, records)
        assert p.returncode == 0 and 'Overseer Kit vendoring CLI' in p.stdout, records[-1]
        # Generate only fixture documents; no init/sync or consumer access.
        import yaml
        configuration = yaml.safe_load((LEGACY/'tests/fixtures/config-git-only.yaml').read_text())
        for marker in ['a', 'b']:
            repo = fixture/marker
            (repo/'.overseer').mkdir(parents=True)
            (repo/'docs').mkdir(); (repo/'nested').mkdir()
            config = json.loads(json.dumps(configuration))
            config['repo']['name'] = 'ops2-fixture-'+marker
            (repo/'.overseer/config.yaml').write_text(yaml.safe_dump(config))
            (repo/'docs/OVERSEER-HANDOVER.md').write_text(
                '# Disposable handover\n\n### Paste-ready prompt\n\n```text\n'
                'Model: GPT-6 Astra\nFixture: '+marker+'\n```\n')
        for selected, cwd_marker in [('a','b'),('b','a')]:
            p = command([*executable, '-C', fixture/selected, '--json', 'next'],
                        fixture/cwd_marker/'nested', env, records)
            assert p.returncode == 0, records[-1]
            data = json.loads(p.stdout)
            assert data['repo_root'] == str(fixture/selected) and data['repo_name'] == 'ops2-fixture-'+selected, data
            assert 'Fixture: '+selected in p.stdout and 'Fixture: '+cwd_marker not in p.stdout, data
        p = command([*executable, '-C', fixture/'a', '--config', fixture/'b/.overseer/config.yaml', '--json', 'next'],
                    fixture/'a', env, records)
        assert p.returncode == 4 and p.stdout == '' and 'refused: config path outside repo root' in p.stderr, records[-1]
    return records


def prepare():
    assert not (EVIDENCE/'preparation.json').exists(), 'preparation already recorded'
    assert sha(PROVENANCE) == PROVENANCE_SHA
    before = snapshot(TARGET)
    run = Path(tempfile.mkdtemp(prefix='20261015-fpr-ops2-', dir=ROOT.parent/'RECOVERY-RUNS')).resolve()
    backup = run/'venv-before'
    clone_tree(TARGET, backup)
    assert snapshot(backup) == before, 'backup is not exact'
    shutil.copy2('/Users/aaronrenecarvajal/.local/bin/ok', run/'global-wrapper-before')
    dependencies = json.loads(PROVENANCE.read_text())['dependencies']['3.14']
    files = {}
    for name in ['PyYAML','cryptography','cffi','pycparser']:
        for relative, expected in dependencies[name]['files'].items():
            assert relative not in files
            files[relative] = expected
    bundle = run/'selected-artifacts'; bundle.mkdir()
    for relative, expected in files.items():
        source = ROOT/'.venv'/SITE/relative
        assert source.is_file() and not source.is_symlink() and sha(source) == expected
        dest = bundle/relative; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source,dest)
        assert sha(dest) == expected
    record_counts = {}
    omitted_entrypoints = []
    for record in bundle.glob('*.dist-info/RECORD'):
        count=0
        for relative, digest, size in csv.reader(record.read_text().splitlines()):
            if '__pycache__' in Path(relative).parts or relative.endswith('.pyc'):
                continue
            if relative == '../../../bin/cffi-gen-src' and record.parent.name == 'cffi-2.1.0.dist-info':
                # Match the prior runtime-library artifact scope. Do not copy a
                # console script whose installed shebang points at recovery.
                algorithm,encoded=digest.split('=',1)
                assert algorithm=='sha256' and int(size)==218
                omitted_entrypoints.append({'record_path':relative,'record_digest':digest,
                    'record_bytes':int(size),'source_script_available':False,
                    'reason':'optional CFFI generator absent from recorded runtime-library artifact set and source venv; unused by legacy CLI; no script invented; original RECORD reference preserved'})
                continue
            assert relative in files
            if digest:
                algorithm,encoded=digest.split('=',1);assert algorithm=='sha256'
                p=bundle/relative
                assert base64.urlsafe_b64encode(bytes.fromhex(sha(p))).rstrip(b'=').decode()==encoded
                assert p.stat().st_size==int(size);count+=1
        record_counts[record.parent.name]=count
    save(EVIDENCE/'venv-before.json', before)
    save(run/'venv-before.json', before)
    selection={'provenance':str(PROVENANCE),'provenance_sha256':PROVENANCE_SHA,
               'source':'previously approved exact installed-file artifacts; not newly downloaded wheels',
               'dependencies':dependencies,'selected_file_count':len(files),'record_hashes_checked':record_counts,
               'omitted_optional_entrypoints':omitted_entrypoints,'bundle':str(bundle),'files':files}
    save(EVIDENCE/'dependency-selection.json',selection)
    # Rehearse exact addition and removal using the same symlinked interpreter.
    trial=run/'disposable-venv'
    clone_tree(backup,trial)
    assert snapshot(trial)==before
    add_payload(trial,bundle,files)
    trial_after=snapshot(trial);assert_originals_preserved(before,trial_after)
    try:
        results=validate(trial)
    except Exception as error:
        save(EVIDENCE/'preparation-failure.json',{'error':str(error),'run':str(run),'target_changed':snapshot(TARGET)!=before})
        raise
    assert snapshot(trial)==trial_after, 'validation wrote into trial environment'
    restore_added(trial,backup,before,trial_after)
    assert snapshot(TARGET)==before, 'target changed during preparation'
    shutil.rmtree(trial)
    save(EVIDENCE/'disposable-validation.json',{'commands':results,'rollback_rehearsal':'exact restorable inventory match','target_unchanged':True})
    save(EVIDENCE/'preparation.json',{'run':str(run),'backup':str(backup),'bundle':str(bundle),
         'verified_rollback':True,'target':str(TARGET),'added_file_count':len(files),
         'before_inventory_sha256':sha(EVIDENCE/'venv-before.json'),'selection_sha256':sha(EVIDENCE/'dependency-selection.json'),
         'target_mutated':False,'metadata_scope':'bytes, paths, symlinks, modes, uid/gid, mtime_ns, flags, xattrs; inode/ctime are not restorable'})


def apply():
    assert not (EVIDENCE/'application.json').exists(), 'application already recorded'
    preparation=json.loads((EVIDENCE/'preparation.json').read_text())
    assert preparation['verified_rollback'] and preparation['target']==str(TARGET)
    assert sha(EVIDENCE/'venv-before.json')==preparation['before_inventory_sha256']
    assert sha(EVIDENCE/'dependency-selection.json')==preparation['selection_sha256']
    before=json.loads((EVIDENCE/'venv-before.json').read_text())
    backup=Path(preparation['backup']);assert snapshot(backup)==before and snapshot(TARGET)==before
    opening=json.loads((EVIDENCE/'opening-verification.json').read_text())
    assert sha(Path(opening['interpreter']['resolved']))==opening['interpreter']['sha256']
    for relative,row in opening['legacy_source_files'].items():
        assert sha(LEGACY/relative)==row['sha256']
    assert sha(Path(opening['global_wrapper']['path']))==opening['global_wrapper']['sha256']
    selection=json.loads((EVIDENCE/'dependency-selection.json').read_text())
    assert sha(PROVENANCE)==selection['provenance_sha256']
    try:
        add_payload(TARGET,Path(preparation['bundle']),selection['files'])
        after=snapshot(TARGET);assert_originals_preserved(before,after)
        save(EVIDENCE/'venv-after.json',after)
        results=validate(TARGET,use_shim=True)
        assert snapshot(TARGET)==after, 'validation wrote into target environment'
    except Exception as error:
        failed=snapshot(TARGET)
        assert_originals_preserved(before,failed)
        restore_added(TARGET,backup,before,failed)
        save(EVIDENCE/'application-failure.json',{'error':str(error),'rolled_back':True})
        raise
    save(EVIDENCE/'target-validation.json',{'commands':results,'bytecode_writes':False,
         'scope':'dependency compatibility, real legacy shim startup, two-root selection and cross-root config refusal',
         'not_supported_by_legacy_source':['UUID binding','branch binding','expected digest validation','canonical next-write']})
    save(EVIDENCE/'application.json',{'target':str(TARGET),'backup':str(backup),'added_files':len(selection['files']),
         'added_paths':sorted(set(after)-set(before)),
         'replaced_external_yaml_links':OLD_LINKS,
         'other_existing_entries_preserved':True,
         'after_inventory_sha256':sha(EVIDENCE/'venv-after.json'),'source_interpreter_pair_preserved':True,
         'global_wrapper_changed':False,'network_used':False,'method':'exclusive addition of 190 manifested distribution files'})


def rollback():
    preparation=json.loads((EVIDENCE/'preparation.json').read_text())
    application=json.loads((EVIDENCE/'application.json').read_text())
    assert sha(EVIDENCE/'venv-after.json')==application['after_inventory_sha256']
    before=json.loads((EVIDENCE/'venv-before.json').read_text())
    after=json.loads((EVIDENCE/'venv-after.json').read_text())
    restore_added(TARGET,Path(preparation['backup']),before,after)
    print('Original venv content and restorable metadata restored; missing-dependency failure returns.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['prepare','apply','rollback'])
    action=parser.parse_args().action
    assert TARGET.resolve()==TARGET and TARGET.is_dir()
    {'prepare':prepare,'apply':apply,'rollback':rollback}[action]()
    print(json.dumps({'action':action,'ok':True}))
