import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
r=Recorder('01b-publish-start')
r.note('prior_attempt',explanation='Migration and idempotent initialization correctly preserved missing NEXT. The first pilot driver assumed status succeeded before explicit initial publication; preserved 01-migration.json records the refusal. Publish now uses the absent CAS value; no product changes.')
r.publish('PILOT-START','Perform only the owner-authorized disposable local integrated pilot. No external providers, transfers, signing or release.')
r.git('add','.')
r.git('commit','-m','Initialize migrated Git-only pilot with two bound lanes')
state=r.state();assert state['runtime']['sha256']==RUNTIME
for lane in ('product','validation'):r.ok('next','--lane',lane,'--json')
r.note('ready_for_host_agent',project=str(ROOT),installation=str(KIT),repository=state['repository'],runtime=state['runtime'],head=state['head'],hooks='Installed only in disposable project; native delivery unverified')
print(json.dumps({'ok':True,'project':str(ROOT),'installation':str(KIT),'uuid':state['repository']['id'],'runtime':state['runtime'],'head':state['head']}))
