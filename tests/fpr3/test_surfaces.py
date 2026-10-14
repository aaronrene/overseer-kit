import json
import socket
from pathlib import Path
import urllib.request
import urllib.error
import pytest
from cli import v1
from cli.context import CliContext
from cli.main import ValidatedContext, _arguments
from tests.v1.conftest import command, seed, KIT
from tests.fpr3.test_commands import settings, git


def bound_ctx(root):
    args=_arguments(['-C',str(root),'app'])
    c=ValidatedContext.capture(root,args)
    ctx=CliContext.create(cwd=root,kit=KIT)
    ctx.bound_context=c;ctx.bound_args=args
    return ctx


def request(url, *, method='GET', body=None, token='session-fixture', csrf='csrf-fixture', origin=None):
    headers={}
    if token is not None:headers['Authorization']='Bearer '+token
    if csrf is not None:headers['X-Overseer-CSRF']=csrf
    if origin is not None:headers['Origin']=origin
    raw=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(url,data=raw,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=10) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as exc:
        try:payload=json.load(exc)
        except (ValueError,UnicodeError):payload={}
        return exc.code,payload


def test_loopback_real_service_auth_csrf_origin_next_and_paths(repo):
    from tools.app.server import build_server_config,start_app_server
    server=start_app_server(build_server_config(repo_root=repo,bind='127.0.0.1',port=0,ctx=bound_ctx(repo),
        session_credential='session-fixture',csrf_token='csrf-fixture'))
    try:
        base=server.base_url
        assert request(base+'/api/health',token=None)[0]==401
        assert request(base+'/api/health',token='wrong')[0]==401
        assert request(base+'/api/health',origin='https://evil.invalid')[0]==403
        code,body=request(base+'/api/health');assert code==200 and body['ok']
        assert body['result']['repo_root']==str(repo)
        code,body=request(base+'/api/next');assert body['ok'],body
        assert body['result']['rendered']==command('-C',repo,'next').stdout
        assert request(base+'/api/next?lane=product&lane=other')[0]==400
        assert request(base+'/api/status?repo=/foreign')[0]==400
        assert request(base+'/api/ledger/show?last=invalid')[0]==400
        assert request(base+'/api/governance-sync',method='POST',body={},csrf=None)[0]==403
        code,body=request(base+'/api/governance-sync',method='POST',body={'write':False})
        assert body['ok'] and body['result']['dry_run'],body
        code,body=request(base+'/api/review/freeze',method='POST',body={'path':'../outside.md'})
        assert not body['ok']
        assert request(base+'/api/governance-sync',method='POST',body={'push':True})[0]==400
        assert request(base+'/assets/../../static-secret.txt')[0] in (403,404)
        config=(repo/'.overseer/config.yaml').read_text()
        (repo/'.overseer/config.yaml').write_text(config+'\n# changed binding\n')
        code,body=request(base+'/api/health');assert not body['ok'] and 'binding_changed' in body['error']
    finally:server.shutdown()


def test_app_copied_context_and_symlink_docs_refuse(repo,tmp_path):
    from tools.app.engine import handle_status,handle_docs_handover
    ctx=bound_ctx(repo)
    other=seed(tmp_path/'other');assert command('-C',other,'init').returncode==0
    assert not handle_status(ctx,repo_arg=str(other)).ok
    (repo/'docs/OVERSEER-HANDOVER.md').unlink()
    (repo/'docs/OVERSEER-HANDOVER.md').symlink_to(other/'docs/OVERSEER-HANDOVER.md')
    assert not handle_docs_handover(ctx).ok


def test_hosted_allowlists_canonical_display_and_write_refusal():
    from tests.fixtures.hosted_dashboard import FixtureUpstream
    from tools.hosted_dashboard.config import parse_hosted_dashboard_config
    from tools.hosted_dashboard.adapters.github import GitHubAdapters
    from tools.hosted_dashboard.handlers import DashboardService
    from tools.hosted_dashboard.http_client import UpstreamClient
    from tools.hosted_dashboard.server import HostedServerConfig,start_hosted_server
    fixture=FixtureUpstream();fixture.seed_kit_repo();fixture.put_file('acme','kit-demo','docs/NEXT.md','historical remote bytes')
    config=parse_hosted_dashboard_config({'enabled':True,'org_allowlist':['acme/kit-demo']})
    service=DashboardService(GitHubAdapters(UpstreamClient(token=None,transport=fixture.transport)),config)
    before=len(fixture.calls)
    refused=service.next('foreign','kit-demo',{})
    assert refused.http_status==403 and len(fixture.calls)==before
    result=service.next('acme','kit-demo',{})
    assert result.ok and result.result['actionable'] is False
    assert result.result['path']=='docs/NEXT.md'
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    server=start_hosted_server(HostedServerConfig(bind='127.0.0.1',port=port,viewer_token='session-fixture',upstream_token=None,dashboard=config,service=service))
    try:
        for path in ('/api/governance-sync','/api/review/freeze','/api/ledger/append','/api/next-write'):
            assert request(server.base_url+path,method='POST',body={})[0]==405
        assert request(server.base_url+'/api/repos/acme/kit-demo/next')[1]['result']['actionable'] is False
    finally:server.shutdown()


def test_desktop_real_launcher_identity_and_ambient_refusal(repo,monkeypatch,tmp_path):
    from tools.desktop.launcher import DesktopLauncher,resolve_kit_root,resolve_repo_root,build_launch_argv
    monkeypatch.setenv('OVERSEER_KIT_ROOT',str(tmp_path/'foreign'))
    assert resolve_kit_root()==KIT
    with pytest.raises(ValueError):resolve_repo_root(kit=KIT)
    with pytest.raises(ValueError):build_launch_argv(kit_root_path=tmp_path,repo_root=repo)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    launcher=DesktopLauncher(KIT,repo,port=port)
    try:
        banner=launcher.start()
        code,payload=request(banner.url.rstrip('/')+'/api/next',token=banner.session_credential,csrf=banner.csrf_token)
        assert code==200 and payload['ok'],payload
    finally:launcher.stop()


def test_workspace_canonical_members_stale_pin_and_no_ambient_scan(repo,tmp_path,monkeypatch):
    other=seed(tmp_path/'member');assert command('-C',other,'init').returncode==0
    manifest={'overseer_workspace_version':1,'id':'fixture','product_order_member':'primary',
      'members':[{'id':'primary','role':'product_order','root':str(repo),'required':True,'relay':False,'regime':'git-only'},
                 {'id':'peer','role':'other','root':str(other),'required':True,'relay':True,'regime':'git-only'}],
      'lanes':[{'id':'product','primary':True,'owner_member':'primary'}]}
    import yaml
    (repo/'.overseer/workspace.yaml').write_text(yaml.safe_dump(manifest))
    settings(repo,workspace={'constellation_id':'fixture','manifest':'.overseer/workspace.yaml'})
    monkeypatch.setenv('OVERSEER_WORKSPACE_MANIFEST','/foreign/nope.yaml')
    p=command('-C',repo,'workspace','check-next','--json');assert p.returncode==0,p.stdout+p.stderr
    assert len(json.loads(p.stdout)['members'])==2
    manifest['canonical_next_pins']={'peer':'0'*64}
    (repo/'.overseer/workspace.yaml').write_text(yaml.safe_dump(manifest))
    assert command('-C',repo,'workspace','check-next').returncode==35


def test_hosted_rechecks_binding_before_returning_projection():
    from tools.hosted_dashboard.handlers import DashboardService
    from tools.hosted_dashboard.config import parse_hosted_dashboard_config
    from tools.hosted_dashboard.adapters.github import GitHubAdapters
    from tools.hosted_dashboard.http_client import UpstreamClient
    from tests.fixtures.hosted_dashboard import FixtureUpstream
    from cli.v1_io import Refusal
    state={'changed':False}
    def validate():
        if state['changed']:raise Refusal('changed')
    fixture=FixtureUpstream();fixture.seed_kit_repo()
    service=DashboardService(GitHubAdapters(UpstreamClient(token=None,transport=fixture.transport)),
        parse_hosted_dashboard_config({'enabled':True,'org_allowlist':['acme/kit-demo']}),validate_context=validate)
    state['changed']=True
    assert service.handover('acme','kit-demo',{}).http_status==409
    assert not fixture.calls
