import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
import yaml
r=Recorder('01-migration')
r.git('init','--template=','-b','main')
r.git('config','core.hooksPath','/dev/null')
r.git('config','user.name','Overseer Disposable Pilot')
r.git('config','user.email','pilot@example.invalid')
r.git('commit','--allow-empty','-m','Seed new noncritical integrated pilot')
r.git('checkout','-b','pilot/fpr5-integrated-20261015')
c=yaml.safe_load((KIT/'tests/fixtures/config-two-lane.yaml').read_text())
c['repo']={'name':'overseer-fpr5-integrated-pilot-20261015','root_relative_docs':'docs'}
c['vcs']['git']['feature_branch_pattern']='pilot/{slug}'
c['docs']={'handover':'HANDOVER.md','roadmap':'ROADMAP.md','handover_title':'Pilot Handover','roadmap_title':'Pilot Roadmap','coordination':None,'standing_decisions':'ROADMAP.md','default_lane':'product','lanes':{'product':{'handover':'HANDOVER.md','roadmap':'ROADMAP.md','handover_title':'Pilot Handover','roadmap_title':'Pilot Roadmap'},'validation':{'handover':'validation/HANDOVER.md','roadmap':'validation/ROADMAP.md','handover_title':'Validation Handover','roadmap_title':'Validation Roadmap'}}}
c['honesty']=yaml.safe_load((KIT/'tests/fixtures/honesty/config-honesty-enabled.yaml').read_text())['honesty']
c['modules']={'governance':{'enabled':True},'honesty':{'enabled':True},'checkpoints':{'enabled':True}}
c['checkpoints']={'enabled':True,'policy':'policy/pilot-checkpoints.yaml','active_manifest':'manifests/pilot.yaml','progress':'PROGRESS.md','orchestrator':None,'allow_hand_verified':False}
r.write('.overseer/config.yaml','# Deliberately authored legacy pilot configuration.\n'+yaml.safe_dump(c,sort_keys=False),0o600)
owned={'.cursor/rules/build-verification-required.mdc':b'---\nalwaysApply: true\n---\nPilot owner requires offline local verification.\n','.overseer/policy/pilot-owner.yaml':b'pilot_owner: preserve-byte-exact\n','docs/HANDOVER.md':b'# Pilot Handover\n\nOwner content: preserve through migration.\n','docs/ROADMAP.md':b'# Pilot Roadmap\n\nOwner content: preserve through migration.\n','docs/validation/HANDOVER.md':b'# Validation Handover\n\nOwner validation notes.\n','docs/validation/ROADMAP.md':b'# Validation Roadmap\n\nOwner validation work.\n'}
for path,body in owned.items():r.write(path,body,0o750 if path.endswith('.mdc') else 0o644)
before=r.snapshot(owned)
plan=json.loads(r.run([KIT/'cli/ok','-C',ROOT,'init','--migrate','--lane','product','--model','GPT-6 Astra','--dry-run','--json']).stdout)
assert r.snapshot(owned)==before
r.write('migration-plan.json',json.dumps(plan,indent=2)+'\n')
applied=json.loads(r.run([KIT/'cli/ok','-C',ROOT,'init','--migrate','--apply-plan','migration-plan.json','--expect-plan',plan['plan_sha256'],'--expect-config',plan['plan']['source_config_sha256'],'--json']).stdout)
assert r.snapshot(owned)==before
normalized=yaml.safe_load((ROOT/'.overseer/config.yaml').read_text())
assert normalized['runtime']['sha256']==RUNTIME
assert set(normalized['docs']['lanes'])=={'product','validation'}
assert normalized['honesty']==c['honesty'] and normalized['checkpoints']==c['checkpoints']
assert normalized['freeze_contract']==c['freeze_contract']
r.note('migration_preservation',owner_files=before,backup=applied['backup'],repository=normalized['repo'],runtime=normalized['runtime'],full_settings_preserved=True)
resumed=r.run([KIT/'cli/ok','-C',ROOT,'init','--migrate','--apply-plan','migration-plan.json','--expect-plan',plan['plan_sha256'],'--expect-config',plan['plan']['source_config_sha256'],'--resume','--json'])
assert json.loads(resumed.stdout)['changed']==[]
r.run([KIT/'cli/ok','-C',ROOT,'init','--hooks','--lane','product','--model','GPT-6 Astra','--json'])
assert r.snapshot(owned)==before
r.publish('PILOT-START','Perform only the owner-authorized disposable local integrated pilot. No external providers, transfers, signing or release.')
r.git('add','.')
r.git('commit','-m','Initialize migrated Git-only pilot with two bound lanes')
state=r.state();assert state['runtime']['sha256']==RUNTIME
for lane in ('product','validation'):
 r.ok('next','--lane',lane,'--json')
r.note('ready_for_host_agent',project=str(ROOT),installation=str(KIT),repository=state['repository'],runtime=state['runtime'],head=state['head'],hooks='Installed only in disposable project; native delivery unverified')
print(json.dumps({'ok':True,'project':str(ROOT),'installation':str(KIT),'uuid':state['repository']['id'],'runtime':state['runtime'],'head':state['head']}))
