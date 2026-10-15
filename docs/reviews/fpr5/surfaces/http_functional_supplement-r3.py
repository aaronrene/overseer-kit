"""Independent reviewer supplement; all identities/evidence below are synthetic fixtures."""
import hashlib,json,pathlib,socket,stat,traceback,yaml
from tests.v1.conftest import KIT,command,seed
from tests.fpr3.test_commands import settings
from tests.fpr3.test_surfaces import bound_ctx,request
from tools.app.server import build_server_config,start_app_server
base=pathlib.Path('/private/tmp/overseer-fpr5-review.jTlE9P/surfaces')
report={'source':'4c62c17cff6c606a5e1ddf565e12353973b3bcad','kind':'FPR-5 reviewer supplement; not FPR-4 rerun','setup':[],'requests':[],'checks':[],'external_network_used':False}
server=None

def check(name,condition):
    report['checks'].append({'name':name,'passed':bool(condition)})
    assert condition,name

def cli(root,*args):
    p=command('-C',root,*args)
    report['setup'].append({'argv':[str(x) for x in args],'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    check('CLI '+str(args[0])+' succeeds',p.returncode==0)
    return json.loads(p.stdout) if p.stdout.strip() else None

def snap(root):
    return {p.relative_to(root).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode),'mtime_ns':p.stat().st_mtime_ns} for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}

def http(path,**kw):
    code,body=request(server.base_url+path,**kw)
    report['requests'].append({'path':path,'method':kw.get('method','GET'),'request_body':kw.get('body'),'http_status':code,'response':body})
    check(path+' returns HTTP 200 and successful engine envelope',code==200 and body.get('ok') is True and body.get('exit_code')==0)
    return body['result']

try:
    root=seed(base/'http-fixture-r3')
    report['fixture']=str(root)
    cli(root,'init','--json')
    original=yaml.safe_load((KIT/'tests/fixtures/honesty/config-honesty-enabled.yaml').read_text())
    c=settings(root,honesty=original['honesty'])
    from cli.product_config import normalize
    model=normalize((root/'.overseer/config.yaml').read_bytes(),root=root)
    check('configured review provider is local',model.adapter.freeze_contract.reviewer.provider=='local')
    artifact=root/'fixture-artifact.txt'
    artifact.write_bytes(b'Synthetic FPR-5 HTTP evidence fixture.\n')
    actual_digest=hashlib.sha256(artifact.read_bytes()).hexdigest()
    check('synthetic artifact bytes verified',artifact.read_bytes()==b'Synthetic FPR-5 HTTP evidence fixture.\n')
    verdict={'actor_role':'verifier','actor_session_id':'fixture-verifier','artifact_sha256':actual_digest,'passed':True,'evidence':{'reexecuted':['fixture artifact exact bytes and SHA-256 verified by this supplement']}}
    (root/'fixture-verdict.json').write_text(json.dumps(verdict))
    cli(root,'ledger','append','--kind','verdict','--file','fixture-verdict.json','--json')
    cli(root,'check-ok','--path','docs/reviews/http-check.md','--topic','Synthetic HTTP fixture','--scope','Local no-execution review preview','--scaffold-only','--json')
    cli_ledger=cli(root,'ledger','show','--last','20','--json')
    cli_honesty=cli(root,'honesty-status','--hook','handoff','--artifact','fixture-artifact.txt','--producer-session','fixture-producer','--json')
    cli_status=cli(root,'status','--json')
    before=snap(root)
    # Explicitly prohibit non-loopback sockets in this reviewer process.
    connect=socket.create_connection
    def loopback_only(address,*args,**kw):
        if address[0] not in {'127.0.0.1','localhost','::1'}:
            raise AssertionError('external socket forbidden: '+str(address))
        return connect(address,*args,**kw)
    socket.create_connection=loopback_only
    server=start_app_server(build_server_config(repo_root=root,bind='127.0.0.1',port=0,ctx=bound_ctx(root),session_credential='session-fixture',csrf_token='csrf-fixture'))
    status=http('/api/status')
    check('HTTP status exactly equals actual CLI status',status==cli_status)
    check('HTTP status is current with bound identity runtime and lanes',status['ok'] is True and status['repository']['root']==str(root) and status['runtime']['root']==str(KIT))
    gates=http('/api/gates')
    check('HTTP gates equal status governance_gates',gates==status['governance_gates'])
    review=http('/api/review/freeze',method='POST',body={'path':'docs/reviews/http-check.md','dry_run':True,'allow_network':False})
    check('review dry-run result marks dry_run',review.get('dry_run') is True)
    ledger=http('/api/ledger/show?last=20')
    check('HTTP ledger equals real CLI ledger entries',ledger['entries']==cli_ledger['entries'])
    check('ledger contains genesis and fixture verdict',len(ledger['entries'])==2 and ledger['entries'][0]['kind']=='genesis' and ledger['entries'][1]['kind']=='verdict')
    verified=http('/api/ledger/verify',method='POST',body={})
    check('HTTP ledger verification engine exits zero',verified['exit_code']==0)
    honesty=http('/api/honesty-status',method='POST',body={'hook':'handoff','artifact':'fixture-artifact.txt','producer_session':'fixture-producer'})
    check('HTTP honesty equals CLI matched evidence',honesty==cli_honesty)
    check('HTTP honesty matched exact synthetic verdict',honesty['matched_verdict_hash']==ledger['entries'][1]['entry_hash'] and honesty['artifact_sha256']==actual_digest)
    check('all HTTP functional operations preserve fixture bytes modes mtimes',snap(root)==before)
    report['result']='PASS'
except Exception as exc:
    report['result']='BLOCKED' if isinstance(exc,OSError) and getattr(exc,'errno',None) in (1,13) else 'FAIL'
    report['error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
    raise
finally:
    if server is not None:
        server.shutdown()
    (base/'http_functional_supplement-r3.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'result':report.get('result'),'checks':report['checks'],'request_count':len(report['requests']),'error':report.get('error')},indent=2))
