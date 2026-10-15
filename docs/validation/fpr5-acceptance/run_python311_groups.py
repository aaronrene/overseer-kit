"""Serial complete cell, immutable inputs, external evidence and bounded disk use."""
from collections import Counter
import hashlib, json, os
from pathlib import Path
import shutil, signal, subprocess, sys, time

OUT=Path(__file__).resolve().parent
INSTALL=OUT/'python3.11-installation'
EVIDENCE=OUT/'matrix'
BASE=json.loads((OUT/'python311-selection.json').read_text())
EXPECTED=json.loads((OUT/'python311-expected-collection.json').read_text())['cases']
PACKAGES=['tests/fpr3/test_package.py::test_actual_package_deterministic_manifest_modes_and_resource_bundle',
          'tests/fpr5/test_resource_repairs.py::test_provisioned_runtime_and_actual_packaged_entrypoints']
ORDER=['retained','v1','fpr1','fpr2','fpr3','fpr4','fpr5','performance','packages']
REPORT={'kind':'Complete Python3.11 Git cell executed in serial disjoint groups on immutable repaired source',
        'expected_cases':1196,'groups':{},'runtime_sha256':'cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774',
        'prior_collection_failure':'python311-complete.json: ENOSPC before test execution; preserved unchanged',
        'no_new_requirement_waivers':True,'disk_floor_bytes':250*1024*1024,'cleanup_policy':'Only newly generated fully passing fixture trees; raw logs/XML/records preserved outside them'}
def save(): (OUT/'python311-serial.json').write_text(json.dumps(REPORT,indent=2)+'\n')
def category(n):
    if n in PACKAGES:return 'packages'
    if n.startswith('tests/performance/'):return 'performance'
    parts=n.split('/')
    if len(parts)>1 and parts[1] in ORDER:return parts[1]
    return 'retained'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PIP_NO_INDEX='1',UV_OFFLINE='1')
env.pop('FPR2_MUSE_PYTHON',None)
all_actual=[]; save()
for group in ORDER:
    expected=[r for r in EXPECTED if category(r['nodeid'])==group]
    selected=PACKAGES if group=='packages' else [s for s in BASE['selected'] if category(s)==group]
    selection={'selected':selected,'deselected':BASE['deselected']+([] if group=='packages' else PACKAGES),
               'expected_count':len(expected),'cell':'Python3.11 Git; native Muse remains assigned to Python3.14'}
    p=OUT/('selection-'+group+'.json');p.write_text(json.dumps(selection,indent=2)+'\n')
    name='py311-'+group
    cmd=[str(INSTALL/'.venv/bin/python'),'-I','-B',str(INSTALL/'scripts/fpr4_run.py'),
         '--name',name,'--selection',str(p),'--evidence-dir',str(EVIDENCE)]
    free=shutil.disk_usage(OUT).free
    if free<REPORT['disk_floor_bytes']*2:
        REPORT['stopped_before_group']={'group':group,'reason':'insufficient disk reserve','free':free};save();break
    row={'expected_cases':len(expected),'command':cmd,'free_before':free};REPORT['groups'][group]=row;save()
    with (EVIDENCE/(name+'-driver.log')).open('xb') as log:
        proc=subprocess.Popen(cmd,cwd=INSTALL,env=env,stdout=log,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            time.sleep(2)
            if shutil.disk_usage(OUT).free<REPORT['disk_floor_bytes']:
                row['disk_stop']=True;proc.send_signal(signal.SIGINT)
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=15)
                break
    row['exit_code']=proc.returncode
    record_path=EVIDENCE/(name+'.json')
    if record_path.exists():
        rec=json.loads(record_path.read_text());row['result']={k:rec.get(k) for k in ('ok','results','boundary_unchanged','exact_collection_executed_once','seconds','nonpassing')}
        col=EVIDENCE/(name+'-collection.json')
        if col.exists():
            try:
                actual=json.loads(col.read_text())['cases'];all_actual.extend(actual)
                row['matches_expected_partition']=Counter(x['nodeid'] for x in actual)==Counter(x['nodeid'] for x in expected)
            except (ValueError,KeyError) as exc:row['collection_error']=str(exc)
        if rec.get('ok') and row.get('matches_expected_partition'):
            fixture=Path(rec['fixture_parent'])
            assert fixture.parent==Path('/private/tmp') and fixture.name.startswith('overseer-fpr4-'+name+'-')
            assert fixture.is_dir() and not fixture.is_symlink()
            shutil.rmtree(fixture)
            row['passing_fixture_reclaimed']=str(fixture)
    row['free_after']=shutil.disk_usage(OUT).free;save()
    print(json.dumps({'group':group,'result':row.get('result'),'partition_matches':row.get('matches_expected_partition'),'free':row['free_after']}),flush=True)
    if row.get('disk_stop'):break
REPORT['exact_complete_partition']=Counter(x['nodeid'] for x in all_actual)==Counter(x['nodeid'] for x in EXPECTED)
REPORT['collected_total']=len(all_actual)
REPORT['ok']=(REPORT['exact_complete_partition'] and len(REPORT['groups'])==len(ORDER)
              and all(r.get('result',{}).get('ok') and r.get('matches_expected_partition') for r in REPORT['groups'].values()))
save();print(json.dumps({'complete_cell_ok':REPORT['ok'],'collected_total':len(all_actual),'report':str(OUT/'python311-serial.json')}),flush=True)
sys.exit(0 if REPORT['ok'] else 1)
