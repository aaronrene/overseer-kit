import sys,json,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
import yaml
r=Recorder('05-rollback')
SOURCE=Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
PARENT='4c62c17cff6c606a5e1ddf565e12353973b3bcad'
OLD='bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec'
source_map=json.loads((KIT/'docs/validation/fpr5-repairs/source-map.json').read_text())
opening=json.loads((KIT/'docs/validation/fpr5-repairs/opening.json').read_text())
backup=BASE/'backups/current-compatible';backup.mkdir(exist_ok=False)
config_paths=['.overseer/config.yaml','.overseer/version.lock']
preserved=['docs/NEXT.md','docs/HANDOVER.md','docs/ROADMAP.md','docs/validation/HANDOVER.md','docs/validation/ROADMAP.md','.cursor/rules/build-verification-required.mdc','.overseer/policy/pilot-owner.yaml','.overseer/honesty/VERDICT-LEDGER.jsonl','manifests/pilot.yaml']
before=r.snapshot(preserved); identity=r.state()['repository'];head=r.git('rev-parse','HEAD').stdout.strip()
for name in config_paths:
 dest=backup/'project'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
rows=[]
for row in source_map['production_changes']:
 path=KIT/row['path'];assert digest(path.read_bytes())==row['after_sha256']
 dest=backup/'source'/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
 old=r.run(['/usr/bin/git','-C',SOURCE,'show',PARENT+':'+row['path']],cwd=BASE).stdout.encode()
 assert digest(old)==row['before_sha256']
 prior=BASE/'backups/previous-compatible'/row['path'];prior.parent.mkdir(parents=True,exist_ok=True);prior.write_bytes(old);prior.chmod(int(row['mode'],8))
 rows.append(row)
r.note('rollback_plan',source_parent=PARENT,previous_runtime=OLD,current_runtime=RUNTIME,source_files=rows,root_unchanged=True,previous_build_known_defects=True)
try:
 for row in rows:
  shutil.copy2(BASE/'backups/previous-compatible'/row['path'],KIT/row['path'])
 assert all(digest((KIT/name).read_bytes())==sha for name,sha in opening['initial']['runtime_files'].items())
 refused=r.ok('next','--lane','product','--json',expected=2)
 assert 'runtime' in refused.stderr or 'runtime' in refused.stdout
 r.ok('sync','--only','launcher','--dry-run','--json')
 r.ok('sync','--only','launcher','--json')
 previous=r.state();assert previous['runtime']['sha256']==OLD and previous['repository']==identity
 for lane in ('product','validation'):r.ok('next','--lane',lane,'--json')
 assert r.snapshot(preserved)==before and r.git('rev-parse','HEAD').stdout.strip()==head
 prior_config=BASE/'backups/previous-compatible/project';prior_config.mkdir(parents=True,exist_ok=False)
 for name in config_paths:
  dest=prior_config/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
 r.note('previous_compatible_readback',runtime=previous['runtime'],all295_runtime_file_hashes_match=True,identity_docs_lanes_next_owner_ledger_preserved=True,known_defects_not_cleared=True)
 for row in rows:shutil.copy2(backup/'source'/row['path'],KIT/row['path'])
 refused=r.ok('next','--lane','product','--json',expected=2)
 assert 'runtime' in refused.stderr or 'runtime' in refused.stdout
finally:
 # This quiescent operator rollback restores only exact files backed up above.
 for row in rows:shutil.copy2(backup/'source'/row['path'],KIT/row['path'])
 for name in config_paths:shutil.copy2(backup/'project'/name,ROOT/name)
restored=r.state();assert restored['runtime']['sha256']==RUNTIME and restored['repository']==identity
assert r.snapshot(preserved)==before and r.git('rev-parse','HEAD').stdout.strip()==head
assert r.git('status','--porcelain=v1').stdout==''
for name in config_paths:assert (ROOT/name).read_bytes()==(backup/'project'/name).read_bytes()
for row in rows:assert digest((KIT/row['path']).read_bytes())==row['after_sha256']
for lane in ('product','validation'):r.ok('next','--lane',lane,'--json')
r.run([KIT/'.venv/bin/python3','-B',KIT/'tools/ci/source_package.py','verify-tree','--directory',KIT],cwd=BASE)
r.note('rollback_return_current',runtime=restored['runtime'],identity=identity,head=head,clean=True,config_and_lock_exactly_restored=True,preserved_files=before,previous_known_defects_not_relabelled_safe=True)
print(json.dumps({'ok':True,'runtime':restored['runtime'],'head':head,'clean':True,'preserved_files':len(before)}))
