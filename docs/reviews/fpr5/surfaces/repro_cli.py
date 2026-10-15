import json, pathlib, shutil, subprocess, sys, yaml
from tests.v1.conftest import command,seed,KIT
from tests.fpr3.test_commands import settings,git
base=pathlib.Path('/private/tmp/overseer-fpr5-review.jTlE9P/surfaces')
root=seed(base/'command-fixture')
rows=[]
def invoke(*args):
    p=command('-C',root,*args)
    rows.append({'argv':[str(x) for x in args],'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    return p
assert invoke('init').returncode==0
for d in ('policy','manifests','scripts'):
    shutil.copytree(KIT/'tests/fixtures/checkpoints'/d,root/d,dirs_exist_ok=True)
conf=yaml.safe_load((KIT/'tests/fixtures/checkpoints/config-checkpoints-enabled.yaml').read_text())
script=root/'scripts/override.py'
script.write_text('#!/usr/bin/env python3\nimport pathlib\npathlib.Path("override-executed").write_text("ran")\n')
script.chmod(0o755)
conf['checkpoints']['orchestrator']='scripts/override.py'
settings(root,checkpoints=conf['checkpoints'],modules=conf['modules'])
p=invoke('verify-step','--all','--dry-run','--json')
assert p.returncode==2 and 'script_execution_requires_explicit_bound_mutation' in p.stderr
assert not (root/'override-executed').exists()
# Fake gh logs exact caller argv; it never opens sockets or invokes real gh.
git(root,'remote','add','origin','https://github.com/fixture/bound.git')
fake=base/'fake-gh'
log=base/'fake-gh-calls.jsonl'
fake.write_text('#!'+sys.executable+'\nimport json,os,sys,pathlib\nwith pathlib.Path('+repr(str(log))+').open("a") as f: f.write(json.dumps({"argv":sys.argv[1:],"GH_REPO":os.environ.get("GH_REPO")})+"\\n")\nif sys.argv[2]=="view": print(json.dumps({"state":"OPEN", "url":"https://github.com/foreign/repo/pull/7", "headRefOid":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}))\nelif sys.argv[2]=="checks": print("ci\\tpass\\t0s\\tfixture")\n')
fake.chmod(0o755)
for pr in ('https://github.com/foreign/repo/pull/7','--repo=foreign/repo'):
    p=invoke('pr-land','--pr='+pr,'--authorized','fixture only','--allow-network','--gh',fake,'--json')
    assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['merged'] is True
(base/'repro_cli_result.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({'results':rows,'fake_gh_calls':[json.loads(s) for s in log.read_text().splitlines()],'network_used':False},indent=2))
