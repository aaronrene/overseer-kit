import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
r=Recorder('01d-publish-start')
r.note('prior_attempt',explanation='Original 01c evidence remains truncated after ENOSPC. Capacity was reclaimed only from a separately owned new rebuildable native target. Resume small local pilot; stop below250MiB free. Reserved binding prose removed; product unchanged.')
r.publish('PILOT-START','Perform only the owner-authorized disposable local integrated pilot. No external providers, transfers, signing or release.')
r.git('add','.')
r.git('commit','-m','Initialize migrated Git-only pilot with two bound lanes')
state=r.state();assert state['runtime']['sha256']==RUNTIME
for lane in ('product','validation'):r.ok('next','--lane',lane,'--json')
r.note('ready_for_host_agent',project=str(ROOT),installation=str(KIT),repository=state['repository'],runtime=state['runtime'],head=state['head'],hooks='Installed only in disposable project; native delivery unverified')
print(json.dumps({'ok':True,'project':str(ROOT),'installation':str(KIT),'uuid':state['repository']['id'],'runtime':state['runtime'],'head':state['head']}))
