import sys,json,socket,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pilotlib import *
sys.path.insert(0,str(KIT))
from tools.desktop.launcher import DesktopLauncher
from tests.fixtures.hosted_dashboard import FixtureUpstream
from tools.hosted_dashboard.config import parse_hosted_dashboard_config
from tools.hosted_dashboard.adapters.github import GitHubAdapters
from tools.hosted_dashboard.handlers import DashboardService
from tools.hosted_dashboard.http_client import UpstreamClient
from tools.hosted_dashboard.server import HostedServerConfig,start_hosted_server
stage=sys.argv[1] if len(sys.argv)>1 else '03-surfaces'
r=Recorder(stage)
paths=['docs/NEXT.md','.overseer/config.yaml','docs/HANDOVER.md','docs/ROADMAP.md','.overseer/honesty/VERDICT-LEDGER.jsonl','manifests/pilot.yaml','.cursor/rules/build-verification-required.mdc']
before=r.snapshot(paths)
def request(base,path,token,method='GET',body=None,csrf=None):
    assert base.startswith('http://127.0.0.1:')
    headers={} if token is None else {'Authorization':'Bearer '+token}
    if csrf is not None:headers['X-Overseer-CSRF']=csrf
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(base+path,data=data,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=10) as response:code=response.status; payload=json.load(response)
    except urllib.error.HTTPError as exc:
        code=exc.code
        try:payload=json.load(exc)
        except ValueError:payload={}
    r.note('loopback_http',path=path,method=method,authentication='absent' if token is None else 'present-redacted',status=code,result=payload)
    return code,payload
try:
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    launcher=DesktopLauncher(KIT,ROOT,port=port)
    r.note('desktop_child_start',argv=launcher.argv,cwd=str(KIT),native_gui=False)
    try:
        banner=launcher.start();base=banner.url.rstrip('/')
        assert request(base,'/api/health',None)[0]==401
        health=request(base,'/api/health',banner.session_credential)[1]
        assert health['ok'] and health['result']['repo_root']==str(ROOT)
        for lane in ('product','validation'):
            code,payload=request(base,'/api/next?lane='+lane,banner.session_credential)
            assert code==200 and payload['ok']
            assert payload['result']['rendered']==r.ok('next','--lane',lane).stdout
        for path in ('/api/status','/api/ledger/show?last=3','/api/docs/handover','/api/docs/roadmap'):
            code,payload=request(base,path,banner.session_credential)
            assert code==200 and payload['ok'],(path,code,payload)
        code,payload=request(base,'/api/ledger/verify',banner.session_credential,'POST',{},banner.csrf_token)
        assert code==200 and payload['ok']
    finally:
        launcher.stop();r.note('desktop_child_stopped',exited=launcher._process is None or launcher._process.poll() is not None)
    fixture=FixtureUpstream();fixture.seed_kit_repo()
    fixture.put_file('acme','kit-demo','docs/NEXT.md',(ROOT/'docs/NEXT.md').read_text())
    config=parse_hosted_dashboard_config({'enabled':True,'org_allowlist':['acme/kit-demo']})
    service=DashboardService(GitHubAdapters(UpstreamClient(token=None,transport=fixture.transport)),config)
    calls_before=len(fixture.calls)
    assert service.next('foreign','kit-demo',{}).http_status==403 and len(fixture.calls)==calls_before
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    server=start_hosted_server(HostedServerConfig(bind='127.0.0.1',port=port,viewer_token='disposable-fake-viewer',upstream_token=None,dashboard=config,service=service))
    try:
        code,payload=request(server.base_url,'/api/repos/acme/kit-demo/next','disposable-fake-viewer')
        assert code==200 and payload['ok'] and payload['result']['actionable'] is False
        for path in ('/api/governance-sync','/api/ledger/append','/api/next-write'):
            assert request(server.base_url,path,'disposable-fake-viewer','POST',{})[0]==405
    finally:server.shutdown()
    r.note('hosted_transport',fake_only=True,external_requests=0,projection_actionable=False,calls=[str(x) for x in fixture.calls])
    assert r.snapshot(paths)==before
    r.note('surface_readonly_snapshot',unchanged=True,files=before)
except BaseException as exc:
    r.note('surface_attempt_failure',exception=repr(exc));raise
print(json.dumps({'ok':True,'stage':stage,'native_gui':False,'native_lifecycle':'separate unresolved requirement','external_requests':0}))
