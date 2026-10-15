import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
import yaml
r=Recorder('02-workflow')
r.note('native_host_limit',result='Actual isolated Cursor3.24.18 launch failed under its enforcing outer sandbox before native events; separate host agent retains evidence. Synthetic checks below are adapter-only evidence, not native lifecycle acceptance.')
before=r.snapshot(['docs/NEXT.md','.overseer/config.yaml','.cursor/rules/build-verification-required.mdc','.overseer/policy/pilot-owner.yaml'])
manual=r.ok('next','--lane','product').stdout
event=json.dumps({'workspace_roots':[str(ROOT)],'lane':'product','repo_id':r.state()['repository']['id'],'hook_event_name':'sessionStart'})
start=json.loads(r.run([ROOT/'.cursor/hooks/session-start-next.sh'],input=event).stdout)
assert start['additional_context']==manual and start['followup_message']==manual
assert r.snapshot(before)==before
r.note('synthetic_start',canonical_equal=True,read_only=True,native_delivery=False)
r.ok('status','--check-footprint','--json')
r.ok('sync','--dry-run','--json')
r.ok('governance-sync','--all-lanes','--dry-run','--json')
oldnext=(ROOT/'docs/NEXT.md').read_bytes()
governance=json.loads(r.ok('governance-sync','--all-lanes','--write','--json').stdout)
assert governance['committed'] and not governance['pushed'] and (ROOT/'docs/NEXT.md').read_bytes()==oldnext
assert set(governance['changed'])=={'docs/HANDOVER.md','docs/ROADMAP.md','docs/validation/HANDOVER.md','docs/validation/ROADMAP.md'}
r.note('paired_local_governance',result=governance,next_preserved=True)
r.publish('PILOT-WORK','Complete the authorized local checks, application readback and rollback. Preserve author evidence; native lifecycle and final independent adjudication remain separate.')
r.ok('check-ok','--path','docs/reviews/pilot-local.md','--topic','integrated-pilot','--scope','Disposable local author workflow only; no certification or external effects.','--provider','local','--json')
review=json.loads(r.ok('review','--freeze','docs/reviews/pilot-local.md','--provider','local','--no-stamp','--json').stdout)
assert review['gate']=='mechanical'
r.note('review_interpretation',gate=review['gate'],independent=False,scope='Local mechanical engine behavior only')
r.ok('review','--freeze','docs/reviews/pilot-local.md','--mode','human','--no-stamp','--json',expected=(0,1,2))
assignment={'actor_role':'overseer','actor_session_id':'fpr5-disposable-pilot-author-20261015','assignment':{'scope':'Owner-approved local integrated pilot','verification':'Check preserved owner policy/rule and bound NEXT with confined script','independent_adjudication':False}}
r.write('pilot-assignment.json',json.dumps(assignment,indent=2)+'\n')
r.ok('ledger','append','--kind','task_assigned','--file','pilot-assignment.json','--json')
policy={'version':1,'placeholder_tokens':['UNRESOLVED_PILOT_TOKEN'],'steps':{'owner-preservation':{'verify_script':'scripts/verify-pilot.sh','description':'Verify actual preserved policy/rule and canonical NEXT files'}},'templates':{'pilot':{'steps':['owner-preservation']}},'overrides':{'default':{'domain':'disposable-local-pilot'}}}
manifest={'schema_version':1,'template_id':'pilot','slug':'integrated-pilot','current_step':'owner-preservation','meta':{'branch':'pilot/fpr5-integrated-20261015'},'steps':{'owner-preservation':{'verified':False,'verified_at':None,'artifact_sha256':None}}}
r.write('policy/pilot-checkpoints.yaml',yaml.safe_dump(policy,sort_keys=False))
r.write('manifests/pilot.yaml',yaml.safe_dump(manifest,sort_keys=False))
r.write('scripts/verify-pilot.sh','#!/bin/sh\nset -eu\ntest "$(cat .overseer/policy/pilot-owner.yaml)" = "pilot_owner: preserve-byte-exact"\n/usr/bin/grep -q "Pilot owner requires offline local verification" .cursor/rules/build-verification-required.mdc\ntest -s docs/NEXT.md\ntest -s .overseer/config.yaml\nprintf "%s\\n" "Pilot owner bytes and canonical bound files verified"\n',0o755)
preview_before=r.snapshot(['manifests/pilot.yaml'])
r.ok('verify-step','--step','owner-preservation','--dry-run','--json')
assert r.snapshot(preview_before)==preview_before
verified=json.loads(r.ok('verify-step','--step','owner-preservation','--json').stdout)
assert verified['ok'] and yaml.safe_load((ROOT/'manifests/pilot.yaml').read_text())['steps']['owner-preservation']['verified']
r.write('docs/validation/pilot-verification.json',json.dumps(verified,indent=2)+'\n')
ruling={'actor_role':'overseer','actor_session_id':'fpr5-disposable-pilot-author-20261015','ruling':'The confined local owner-preservation checkpoint executed successfully. This author observation is not an independent verdict.','evidence_path':'docs/validation/pilot-verification.json','evidence_sha256':digest((ROOT/'docs/validation/pilot-verification.json').read_bytes())}
r.write('pilot-ruling.json',json.dumps(ruling,indent=2)+'\n')
r.ok('ledger','append','--kind','overseer_ruling','--file','pilot-ruling.json','--json')
r.ok('ledger','verify','--json');ledger=json.loads(r.ok('ledger','show','--last','3','--json').stdout)
assert len(ledger['entries'])==3
r.ok('honesty-status','--hook','handoff','--artifact','docs/reviews/pilot-local.md','--json',expected=(0,20))
r.ok('route','--validate','--json')
r.ok('land-closeout','--json')
r.note('workflow_complete',verification=verified,ledger_entries=3,local_mechanical_review_only=True,native_lifecycle='blocked')
print(json.dumps({'ok':True,'stage':r.stage,'ledger_entries':3,'native_lifecycle':'blocked'}))
