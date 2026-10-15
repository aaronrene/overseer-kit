import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
import yaml
r=Recorder('02b-workflow')
r.note('human_fallback',observed_exit=8,verdict='blocked',reason='mode_human',interpretation='Expected explicit human escalation, not a product failure or independent pass. Initial driver assumed a generic nonpass code; exact result is retained in02-workflow.json. Continue remaining steps without relabelling.')
source=(BASE/'02-workflow.py').read_text().split('\nassignment=',1)[1]
exec(compile('assignment='+source,str(BASE/'02-workflow.py')+'[continuation]','exec'))
