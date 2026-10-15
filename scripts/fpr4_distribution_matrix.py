#!/usr/bin/env python3
"""Offline FPR-4 source-install checks; all fixture mutations use a new /private/tmp root.

Run from the integration installation's conventional venv. This is author
validation, with explicit missing prerequisites, not a release or pilot driver.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

KIT = Path(__file__).resolve().parents[1]
PINNED = {'PyYAML':'6.0.3','cryptography':'49.0.0','cffi':'2.1.0','pycparser':'3.0',
          'pytest':'9.1.1','iniconfig':'2.3.0','packaging':'26.2','Pygments':'2.20.0','pluggy':'1.6.0'}
YAML311 = Path('/Users/aaronrenecarvajal/Library/Caches/pip/http-v2/d/f/8/1/8/df81886714b54404e117f63ef5cc13e3f49981e19471f28dabd1ec77.body')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--phase',choices=['prepare','exercise','core','native','template'],default='prepare')
    parser.add_argument('--python-version',choices=['3.11','3.14'],default='3.14')
    parser.add_argument('--evidence-tag',default='',help='Separate final evidence from preserved initial runs')
    parser.add_argument('--expected-runtime',help='Required SHA256 of the immutable product runtime')
    parser.add_argument('--native-target',type=Path,help='Reuse only an explicitly selected task-local Cargo target')
    args=parser.parse_args()
    if args.evidence_tag and not args.evidence_tag.replace('-','').replace('_','').isalnum():
        parser.error('--evidence-tag must contain only letters, digits, hyphens or underscores')
    if args.expected_runtime and (len(args.expected_runtime)!=64 or any(c not in '0123456789abcdef' for c in args.expected_runtime)):
        parser.error('--expected-runtime must be a lowercase SHA256')
    if args.native_target and not args.native_target.absolute().is_relative_to(Path('/private/tmp')):
        parser.error('--native-target must be under /private/tmp')
    if Path(sys.prefix).resolve()!=KIT/'.venv':
        parser.error('run with this integration source installation\'s conventional .venv')
    output=args.output.absolute()
    if not output.is_relative_to(Path('/private/tmp')):
        parser.error('--output must be a new absolute /private/tmp fixture parent')
    evidence=KIT/'docs/validation/fpr4'
    evidence.mkdir(exist_ok=True)
    if args.phase=='prepare':
        output.mkdir(parents=True,exist_ok=False)
    elif not (output/'distribution.json').is_file():
        parser.error('run prepare first')
    assert output.is_relative_to(Path('/private/tmp'))
    report=json.loads((output/'distribution.json').read_text()) if (output/'distribution.json').exists() else {
        'source':str(KIT),'fixture_parent':str(output),'author_validation':True,'release_ready':False,
        'commands':[],'checks':[],'unresolved':[],'dependencies':{},'environments':{}}
    report['driver_sha256']=sha(Path(__file__).read_bytes())
    report['evidence_tag']=args.evidence_tag
    if args.expected_runtime:
        report['expected_runtime']=args.expected_runtime
    def evidence_name(name):
        return name.replace('distribution', 'distribution-'+args.evidence_tag, 1) if args.evidence_tag else name
    env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','GIT_')) and k not in {'VIRTUAL_ENV'}}
    env.update(PATH='/usr/bin:/bin',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1',PYTHONDONTWRITEBYTECODE='1')
    def save():
        name='distribution' if args.phase=='prepare' else 'distribution-'+args.phase+'-'+args.python_version
        (output/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        (evidence/(evidence_name(name)+'-results.json')).write_text(json.dumps(report,indent=2)+'\n')
    def run(argv,cwd=KIT,expected=0,timeout=60,extra_env=None,label=None):
        argv=list(map(str,argv))
        p=subprocess.run(argv,cwd=cwd,env=dict(env,**(extra_env or {})),capture_output=True,text=True,timeout=timeout)
        row={'argv':argv,'cwd':str(cwd),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
        if extra_env:row['explicit_environment']=extra_env
        if label:row['label']=label
        report['commands'].append(row);save()
        if expected is not None:assert p.returncode==expected,row
        return p
    def check(label):
        report['checks'].append(label);save();print('PASS',label,flush=True)
    if args.phase=='prepare':
        report['opening_head']=run(['/usr/bin/git','rev-parse','HEAD']).stdout.strip()
        # Freeze the package first. Later logs never alter this archive; repacking
        # the manifest-bound unpacked source proves exact reproducibility.
        archive=output/'source.tar.gz'
        sys.path.insert(0,str(KIT))
        from tools.ci.source_package import source_files
        snapshot=output/'frozen-source';snapshot.mkdir()
        source_map={}
        for name,original in source_files(KIT).items():
            target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(original,target);target.chmod(0o755 if original.stat().st_mode&0o111 else 0o644)
            source_map[name]={'sha256':sha(target.read_bytes()),'size':target.stat().st_size,'mode':'0755' if target.stat().st_mode&0o111 else '0644'}
        (snapshot/'SOURCE-MANIFEST.json').write_text(json.dumps({'schema':1,'files':source_map}))
        report['frozen_source']=str(snapshot)
        report['frozen_source_files']=source_map
        build=run([sys.executable,snapshot/'tools/ci/source_package.py','build','--output',archive])
        report['artifact']=json.loads(build.stdout)
        run([sys.executable,KIT/'tools/ci/source_package.py','verify','--archive',archive])
        for version,python in [('3.11','/Users/aaronrenecarvajal/.local/bin/python3.11'),('3.14','/opt/homebrew/bin/python3.14')]:
            install=output/('python'+version)
            run([sys.executable,KIT/'tools/ci/source_package.py','unpack','--archive',archive,'--destination',install])
            missing=run([install/'cli/ok','--help'],cwd=output,expected=2)
            assert 'no runtime fallback' in missing.stderr
            run([python,'-m','venv','--without-pip',install/'.venv'])
            site=next((install/'.venv/lib').glob('python*/site-packages'))
            dependency_map={}
            for name,pinned in PINNED.items():
                d=importlib.metadata.distribution(name);assert d.version==pinned
                hashes={}
                for row in d.files or []:
                    relative=Path(str(row))
                    if relative.is_absolute() or '..' in relative.parts or '__pycache__' in relative.parts or relative.suffix in {'.pyc','.pth'}:continue
                    original=Path(d.locate_file(row)).resolve()
                    assert original.is_relative_to(KIT/'.venv')
                    if not original.is_file():continue
                    # CPython extensions are never silently transplanted to an
                    # incompatible interpreter. PyYAML has a pinned cp311 wheel.
                    if version=='3.11' and (name=='PyYAML' or (name=='cffi' and relative.name.startswith('_cffi_backend'))):continue
                    target=site/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target)
                    hashes[str(relative)]=sha(target.read_bytes())
                dependency_map[name]={'version':pinned,'source':'integration .venv exact installed files','files':hashes}
            if version=='3.11':
                assert YAML311.is_file()
                with zipfile.ZipFile(YAML311) as z:
                    assert 'Version: 6.0.3\n' in z.read('pyyaml-6.0.3.dist-info/METADATA').decode()
                    assert 'Tag: cp311-cp311-macosx_11_0_arm64' in z.read('pyyaml-6.0.3.dist-info/WHEEL').decode()
                    for n in z.namelist():
                        assert not Path(n).is_absolute() and '..' not in Path(n).parts
                    z.extractall(site)
                dependency_map['PyYAML']={'version':'6.0.3','source':str(YAML311),'archive_sha256':sha(YAML311.read_bytes()),'files':{n:sha((site/n).read_bytes()) for n in z.namelist() if (site/n).is_file()}}
                report['unresolved'].append('Python 3.11: pinned cffi 2.1.0 CPython 3.11 native backend unavailable in inspected local caches; no replacement version/download used. Core checks may run, but the full dependency cell remains unresolved.')
            report['dependencies'][version]=dependency_map
            probe=run([install/'.venv/bin/python','-I','-B','-c','import sys,json,importlib.metadata,yaml,cryptography; print(json.dumps({"python":sys.version,"prefix":sys.prefix,"base_prefix":sys.base_prefix,"yaml":yaml.__file__,"versions":{n:importlib.metadata.version(n) for n in '+repr(list(PINNED))+'}}))'])
            report['environments'][version]=json.loads(probe.stdout)
            runtime_probe=run([install/'.venv/bin/python','-I','-B','-c','import sys,json;sys.path.insert(0,sys.argv[1]);from cli.v1 import runtime;print(json.dumps(runtime()))',install])
            installed_runtime=json.loads(runtime_probe.stdout)
            report['environments'][version]['runtime']=installed_runtime
            if args.expected_runtime:
                assert installed_runtime['sha256']==args.expected_runtime,installed_runtime
            crypto=run([install/'.venv/bin/python','-I','-B','-c','from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; k=Ed25519PrivateKey.generate(); k.public_key().verify(k.sign(b"fpr4"),b"fpr4"); print("Ed25519 verified")'],expected=None)
            report['environments'][version]['cryptography_native_exit']=crypto.returncode
            run([install/'.venv/bin/python','-I','-B','-c','import _cffi_backend; print(_cffi_backend.__version__)'],expected=1 if version=='3.11' else 0)
            assert not run([install/'.venv/bin/python','-I','-B','-c','import importlib.util; assert importlib.util.find_spec("muse") is None']).returncode
            check('fresh conventional Python '+version+' source environment; no Muse installed')
        second=output/'repacked.tar.gz'
        again=json.loads(run([output/'python3.14/.venv/bin/python',output/'python3.14/tools/ci/source_package.py','build','--output',second]).stdout)
        assert again['sha256']==report['artifact']['sha256']
        check('immutable unpack/repack has identical archive SHA256 and manifest')
        manifest=json.loads((output/'python3.14/SOURCE-MANIFEST.json').read_text())
        assert {'cli/ok','cli/overseer','desktop/src-tauri/src/launcher.rs','.github/workflows/supported-v1.yml','cursor/skills/print-next/SKILL.md','templates/ROADMAP.template.md','tools/app/static/index.html'}<=set(manifest['files'])
        assert all(not n.startswith(('.overseer/','.venv/','.git/','.muse/')) and n!='docs/NEXT.md' for n in manifest['files'])
        assert all(manifest['files'][n]['mode']=='0755' for n in ['cli/ok','cli/overseer'])
        report['source_manifest_sha256']=sha((output/'python3.14/SOURCE-MANIFEST.json').read_bytes())
        check('required product assets, executable modes and CI dotfiles; runtime-local bindings excluded')
    elif args.phase=='exercise':
        version=args.python_version;install=output/('python'+version);repo=output/('consumer'+version);repo.mkdir(exist_ok=False)
        for argv in (['init','-b','main'],['config','user.name','FPR4 Fixture'],['config','user.email','fpr4@example.invalid'],['-c','core.hooksPath=/dev/null','commit','--allow-empty','-m','fixture seed']):
            run(['/usr/bin/git','-C',repo,*argv])
        run([install/'cli/ok','-C',repo,'init','--vcs','git','--repo-name','source-python'+version])
        state=json.loads(run([install/'cli/ok','-C',repo,'status','--json']).stdout)
        report['environments'][version]['runtime']=state['runtime']
        if args.expected_runtime:
            assert state['runtime']['sha256']==args.expected_runtime,state['runtime']
        report['environments'][version]['repository']=state['repository']
        for entry in [install/'cli/ok',install/'cli/overseer',repo/'.overseer/bin/ok']:
            run([entry,'--help'],cwd=output)
            result=json.loads(run([entry,'-C',repo,'next','--json'],cwd=output).stdout)
            assert result['runtime']==state['runtime'] and result['repository']==state['repository']
        footprint=json.loads(run([install/'cli/ok','-C',repo,'status','--check-footprint','--json']).stdout)
        assert footprint['ok'] is True,footprint
        assert all(row['classification']=='unchanged' for row in footprint['assets']),footprint['assets']
        run([install/'cli/ok','-C',repo,'governance-sync','--dry-run'])
        run([install/'cli/ok','-C',repo,'check-ok','--topic','source-fixture','--dry-run'])
        desktop_code='''import sys,json,socket,urllib.request
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from tools.desktop.launcher import DesktopLauncher
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
launcher=DesktopLauncher(Path(sys.argv[1]),Path(sys.argv[2]),port=port)
try:
 banner=launcher.start()
 request=urllib.request.Request(banner.url.rstrip('/')+'/api/health',headers={'Authorization':'Bearer '+banner.session_credential})
 with urllib.request.urlopen(request) as response:health=json.load(response)
 print(json.dumps({'health':health,'argv':launcher.argv}))
finally:launcher.stop()
'''
        launched=run([install/'.venv/bin/python','-I','-B','-c',desktop_code,install,repo],cwd=output,expected=None)
        if launched.returncode==0:
            report['environments'][version]['desktop_child']=json.loads(launched.stdout)
            check('Python '+version+' actual packaged app/desktop child authenticated health and shutdown')
        else:
            report['unresolved'].append('Python '+version+' app/desktop child failure: '+launched.stderr[-1000:])
        check('Python '+version+' actual CLI aliases/bound launcher, init/NEXT/status/full footprint/governance/Check OK')
    elif args.phase=='core':
        version=args.python_version;install=output/('python'+version)
        selection_path=KIT/'docs/validation/fpr4/disposition-selection.json'
        selection=json.loads(selection_path.read_text())
        selected=[x for x in selection['selected'] if x!='tests/muse']
        report['selection_sha256']=sha(selection_path.read_bytes())
        report['test_overlay']={}
        for original in (KIT/'tests/fpr4').rglob('*'):
            if not original.is_file() or '__pycache__' in original.parts:continue
            relative=original.relative_to(KIT);target=install/relative
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target)
            report['test_overlay'][str(relative)]=sha(target.read_bytes())
        selected.extend(['--deselect=tests/fpr4/test_composition.py::test_two_active_repositories_lanes_bookends_cas_and_revision[muse-only]',
                         '--deselect=tests/fpr4/test_composition.py::test_two_active_repositories_lanes_bookends_cas_and_revision[muse+git-mirror]'])
        report['selected']=selected
        p=run([install/'.venv/bin/python','-m','pytest','-q','--continue-on-collection-errors',*selected,'-p','no:cacheprovider','--basetemp',output/('pytest-'+version),'--junitxml',evidence/(evidence_name('distribution-python'+version)+'.xml')],cwd=install,expected=None,timeout=1800)
        (evidence/(evidence_name('distribution-python'+version)+'.log')).write_text(p.stdout+p.stderr)
        report['environments'][version]['pytest_exit']=p.returncode
        if p.returncode:report['unresolved'].append('Python '+version+' selected core suite failed; see exact retained log/XML')
        else:check('Python '+version+' combined fresh-source core selection passed')
    elif args.phase=='template':
        version=args.python_version;install=output/('python'+version)
        selected=['tests/unit/test_templating.py::test_render_handover_template']
        report['selected']=selected
        result_name=evidence_name('distribution-template-python'+version)
        p=run([install/'.venv/bin/python','-m','pytest','-q',*selected,'-p','no:cacheprovider',
               '--basetemp',output/('pytest-template-'+version),'--junitxml',evidence/(result_name+'.xml')],
              cwd=install,expected=None)
        (evidence/(result_name+'.log')).write_text(p.stdout+p.stderr)
        report['environments'][version]['template_pytest_exit']=p.returncode
        if p.returncode:
            report['unresolved'].append('Python '+version+' configured handover-path template check failed')
        else:
            check('Python '+version+' configured handover path preserved by the repaired template')
    elif args.phase=='native':
        install=output/'python3.14';toolchain=Path('/Users/aaronrenecarvajal/.rustup/toolchains/1.88.0-aarch64-apple-darwin/bin')
        run([toolchain/'rustc','--version']);run([toolchain/'cargo','--version'])
        resource=install/'desktop/src-tauri/resources/kit'
        if not resource.exists():
            run([install/'scripts/bundle-desktop-kit.sh',resource],cwd=install)
        run([install/'.venv/bin/python',install/'tools/ci/source_package.py','verify-tree','--directory',resource])
        resource_runtime=json.loads(run([install/'.venv/bin/python','-I','-B','-c','import sys,json;sys.path.insert(0,sys.argv[1]);from cli.v1 import runtime;print(json.dumps(runtime()))',resource]).stdout)
        if args.expected_runtime:
            assert resource_runtime['sha256']==args.expected_runtime,resource_runtime
        report['resource']={'root':str(resource),'runtime':resource_runtime,'manifest_sha256':sha((resource/'SOURCE-MANIFEST.json').read_bytes())}
        native_target=(args.native_target or output/'native-target').absolute()
        native_env={'RUSTC':str(toolchain/'rustc'),'RUSTDOC':str(toolchain/'rustdoc'),'CARGO_TARGET_DIR':str(native_target),'CARGO_NET_OFFLINE':'true'}
        report['native']={'platform':sys.platform,'target':str(native_target),'cargo_lock_sha256':sha((install/'desktop/src-tauri/Cargo.lock').read_bytes()),'gui_run':False,'signing':False,'installer':False}
        p=run([toolchain/'cargo','build','--locked','--offline'],cwd=install/'desktop/src-tauri',expected=None,timeout=1800,extra_env=native_env)
        (evidence/('environment-native-build'+('-'+args.evidence_tag if args.evidence_tag else '')+'.log')).write_text(p.stdout+p.stderr)
        report['native']['exit']=p.returncode
        binary=native_target/'debug/overseer-kit-desktop'
        if p.returncode==0:
            report['native']['binary_sha256']=sha(binary.read_bytes());check('local macOS arm64 native cargo build --locked --offline')
        else:report['unresolved'].append('Native build failed; see environment-native-build.log')
    save()
    if args.phase in {'core','native','template'}:
        return p.returncode
    return 0


if __name__=='__main__':
    raise SystemExit(main())
