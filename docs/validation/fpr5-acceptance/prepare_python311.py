"""Prepare a disposable exact-source Python 3.11 acceptance installation offline."""
import base64, csv, hashlib, importlib.metadata, io, json, os
from pathlib import Path
import shutil, subprocess, sys, zipfile

ROOT = Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
OUT = Path(__file__).resolve().parent
INSTALL = OUT / 'python3.11-installation'
ARCHIVE = Path('/private/tmp/overseer-fpr5-acceptance-preparation-w580lsq4/source.tar.gz')
PINS = {'PyYAML':'6.0.3','cryptography':'49.0.0','cffi':'2.1.0','pycparser':'3.0',
        'pytest':'9.1.1','iniconfig':'2.3.0','packaging':'26.2','Pygments':'2.20.0','pluggy':'1.6.0'}
REPORT = {'kind':'Exact repaired-source Python3.11 acceptance setup; no release claim',
          'author_validation':True, 'source_head':'2e8ec694def9be4a0faa4a994bf2fff3f212ab23',
          'runtime_sha256':'cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774',
          'commands':[], 'dependencies':{}, 'installation':str(INSTALL)}
ENV = {k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','GIT_'))
       and k not in ('VIRTUAL_ENV','FPR2_MUSE_PYTHON')}
ENV.update(PATH='/usr/bin:/bin', PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_GLOBAL='/dev/null',
           GIT_CONFIG_NOSYSTEM='1', PIP_NO_INDEX='1', UV_OFFLINE='1')

def sha(data): return hashlib.sha256(data).hexdigest()
def save(): (OUT/'python311-preparation.json').write_text(json.dumps(REPORT,indent=2)+'\n')
def run(argv,cwd=INSTALL):
    p=subprocess.run(list(map(str,argv)),cwd=cwd,env=ENV,capture_output=True,text=True,timeout=60)
    REPORT['commands'].append({'argv':list(map(str,argv)),'cwd':str(cwd),'exit_code':p.returncode,
                              'stdout':p.stdout,'stderr':p.stderr});save()
    assert p.returncode==0,REPORT['commands'][-1]
    return p.stdout

def wheel(path,name,version,site):
    data=path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        entries=z.namelist()
        assert len(entries)==len(set(entries))
        metadata_name=next(n for n in entries if n.endswith('.dist-info/METADATA'))
        metadata=z.read(metadata_name).decode()
        assert ('Name: '+name+'\n').lower() in metadata.lower() and 'Version: '+version+'\n' in metadata
        record_name=next(n for n in entries if n.endswith('.dist-info/RECORD'))
        recorded={row[0]:row for row in csv.reader(io.StringIO(z.read(record_name).decode()))}
        hashes={}
        for n in entries:
            if n.endswith('/'):continue
            relative=Path(n)
            assert not relative.is_absolute() and '..' not in relative.parts
            blob=z.read(n);row=recorded[n]
            if row[1]:
                kind,value=row[1].split('=',1);assert kind=='sha256'
                assert base64.urlsafe_b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')==value
                assert len(blob)==int(row[2])
            target=site/relative;assert not target.exists()
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
            target.chmod(0o644);hashes[n]=sha(blob)
        REPORT['dependencies'][name]={'version':version,'source_wheel':str(path),'wheel_sha256':sha(data),'files':hashes}

try:
    assert sha(ARCHIVE.read_bytes())=='de8cd9222df8cf6c5fe3f4d858e561018baa0dc6d61df1f0ac423928adaed47f'
    sys.path.insert(0,str(ROOT))
    from tools.ci.source_package import unpack
    unpack(ARCHIVE,INSTALL)
    run(['/usr/bin/git','init','-b','acceptance/fpr5-python311'])
    for key,value in [('core.hooksPath','/dev/null'),('user.name','Overseer Acceptance Fixture'),
                      ('user.email','acceptance@invalid'),('commit.gpgsign','false')]:
        run(['/usr/bin/git','config',key,value])
    run(['/usr/bin/git','add','--all'])
    run(['/usr/bin/git','commit','-m','fixture: pinned repaired source for Python3.11 acceptance'])
    run(['/Users/aaronrenecarvajal/.local/bin/python3.11','-m','venv','--without-pip',INSTALL/'.venv'])
    site=INSTALL/'.venv/lib/python3.11/site-packages'
    for name,version in PINS.items():
        if name in ('PyYAML','cffi'):continue
        d=importlib.metadata.distribution(name);assert d.version==version
        files={}
        for relative in d.files:
            if not relative.parts or relative.parts[0]=='..' or '__pycache__' in relative.parts:continue
            original=Path(d.locate_file(relative)).resolve()
            assert original.is_relative_to((ROOT/'.venv').resolve())
            if not original.is_file():continue
            blob=original.read_bytes()
            if relative.hash:
                assert relative.hash.mode=='sha256'
                assert base64.urlsafe_b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')==relative.hash.value
            target=site/relative;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(blob);target.chmod(original.stat().st_mode&0o777)
            files[str(relative)]=sha(blob)
        REPORT['dependencies'][name]={'version':version,'source':'exact existing local installation RECORD-checked files','files':files}
    wheel(Path('/Users/aaronrenecarvajal/Library/Caches/pip/http-v2/d/f/8/1/8/df81886714b54404e117f63ef5cc13e3f49981e19471f28dabd1ec77.body'),'PyYAML','6.0.3',site)
    wheel(OUT/'cffi-2.1.0-cp311-cp311-macosx_11_0_arm64.whl','cffi','2.1.0',site)
    py=INSTALL/'.venv/bin/python'
    probe='import sys,json,importlib.metadata,importlib.util,_cffi_backend,yaml; from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; k=Ed25519PrivateKey.generate(); k.public_key().verify(k.sign(b"acceptance"),b"acceptance"); assert importlib.util.find_spec("muse") is None; print(json.dumps({"python":sys.version,"cffi":_cffi_backend.__version__,"backend":_cffi_backend.__file__,"ed25519_verified":True,"muse_absent":True,"dependencies":{d.metadata["Name"]:d.version for d in importlib.metadata.distributions()}}))'
    REPORT['probe']=json.loads(run([py,'-I','-B','-c',probe]))
    s=json.loads((ROOT/'docs/validation/fpr5-repairs/integrated-selection.json').read_text())
    all_cases=json.loads((ROOT/'docs/validation/fpr5-repairs/integrated/repaired-integrated-collection.json').read_text())['cases']
    native_four=[r['nodeid'] for r in all_cases if r['nodeid'].startswith('tests/fpr4/') and
                 ('[muse-' in r['nodeid'] or '[muse+' in r['nodeid'] or
                  'test_mirror_full_footprint.py::' in r['nodeid'] or 'test_native_linked_footprint.py::' in r['nodeid'])]
    assert len(native_four)==4
    expected=[r for r in all_cases if not r['nodeid'].startswith('tests/muse/') and r['nodeid'] not in native_four]
    assert len(expected)==1196 and sum(r['nodeid'].startswith('tests/fpr5/') for r in expected)==152
    selection={'kind':'Complete repaired Python3.11 Git cell; native Muse remains separately assigned to Python3.14',
               'selected':[x for x in s['selected'] if x!='tests/muse'],
               'deselected':s['deselected']+native_four,'expected_cases':1196,
               'native_assignment':{'python':'3.14','tests_muse':161,'fpr4_cases':native_four},
               'prior_changed_contract_deselections':s['deselected'],'no_new_requirement_waivers':True}
    (OUT/'python311-selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    (OUT/'python311-expected-collection.json').write_text(json.dumps({'cases':expected},indent=2)+'\n')
    REPORT['selection']=selection
    REPORT['ok']=True
except Exception as exc:
    REPORT.update(ok=False,error=repr(exc));raise
finally:save()
print(json.dumps({'ok':REPORT['ok'],'installation':str(INSTALL),'probe':REPORT.get('probe'),'expected_cases':1196},indent=2))
