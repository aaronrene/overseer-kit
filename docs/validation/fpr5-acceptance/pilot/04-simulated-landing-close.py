import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
r=Recorder('04-simulated-landing-close')
fake=BASE/'fake-gh.sh';log=EVIDENCE/'fake-gh-argv.txt'
fake.write_text('#!/bin/sh\nset -eu\nprintf "%s\\n" "$*" >> '+str(log)+'\ncase "$2" in\n view) printf "%s\\n" \'{"number":17,"url":"https://github.com/pilot-fixture/overseer-integrated/pull/17","state":"OPEN","mergeable":"MERGEABLE","mergeStateStatus":"CLEAN"}\';;\n checks) printf "pilot-local\\tpass\\t1s\\thttps://example.invalid/fake-check\\n";;\n *) exit 97;;\nesac\n');fake.chmod(0o755)
r.note('fake_transport',path=str(fake),sha256=digest(fake.read_bytes()),external_requests=0,allowed_responses=['view','checks'],merge_refused=True)
assert r.git('remote').stdout.strip()==''
r.git('remote','add','origin','https://github.com/pilot-fixture/overseer-integrated')
try:
 result=json.loads(r.ok('pr-land','--pr','17','--authorized','Owner-approved fake-transport local pilot; no real merge','--allow-network','--gh',fake,'--dry-run','--json').stdout)
 assert result['ok'] and not result['merged'] and not result['already_merged']
 calls=log.read_text().splitlines();assert len(calls)==2 and all('--repo github.com/pilot-fixture/overseer-integrated' in row for row in calls)
 assert not any('merge' in row.split() for row in calls)
 r.note('simulated_landing',result=result,calls=calls,network_permission_flag_only_for_fake_executable=True,real_transfers=0)
finally:r.git('remote','remove','origin')
assert r.git('remote').stdout.strip()==''
r.note('mirror_delivery',pilot_authority='git-only',preparation='not selected for this pilot authority',native_muse_and_mirror_matrix='required separately; not waived',live_delivery=False)
for lane,paths in {'product':['docs/HANDOVER.md','docs/ROADMAP.md'],'validation':['docs/validation/HANDOVER.md','docs/validation/ROADMAP.md']}.items():
 for path in paths:
  text=(ROOT/path).read_text()
  text+='\n## Integrated local pilot progress\n\nLegacy migration preserved owner content, settings and two lanes. Local governance, mechanical Check OK/review, real confined verification and accurate author ledger passed. App and desktop-child readbacks used localhost; hosted reads and landing used fake transports. Explicit human review correctly remains blocked for human adjudication. Native Cursor lifecycle and native GUI acceptance are separate unresolved requirements. No release or independent certification is claimed.\n'
  r.write(path,text)
r.publish('PILOT-LOCAL-CLOSE','Local disposable author workflow completed. Preserve this project and its evidence. Required native host lifecycle, native GUI/platform acceptance, remaining matrix evidence, independent final adjudication and owner release decision remain unresolved. No external operations are authorized.',kind='stop')
r.git('add','.')
r.git('commit','-m','Record bounded integrated pilot workflow and pending acceptance')
state=r.state()
assert r.git('status','--porcelain=v1').stdout==''
manual=r.ok('next','--lane','product').stdout
event=json.dumps({'workspace_roots':[str(ROOT)],'lane':'product','repo_id':state['repository']['id'],'hook_event_name':'stop'})
before=r.snapshot(['docs/NEXT.md','.overseer/config.yaml','docs/HANDOVER.md','docs/ROADMAP.md'])
stop=json.loads(r.run([ROOT/'.cursor/hooks/session-end-closeout.sh'],input=event).stdout)
assert stop['additional_context']==manual and stop['followup_message']==manual and r.snapshot(before)==before
for lane in ('product','validation'):r.ok('next','--lane',lane,'--json')
r.ok('land-closeout','--json')
r.note('local_close',head=state['head'],next_sha256=digest((ROOT/'docs/NEXT.md').read_bytes()),clean=True,synthetic_end_canonical_equal=True,native_end_delivery=False)
print(json.dumps({'ok':True,'head':state['head'],'next_sha256':digest((ROOT/'docs/NEXT.md').read_bytes()),'clean':True}))
