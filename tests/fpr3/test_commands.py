import ast
import hashlib
import json
from pathlib import Path
import subprocess
import pytest
import yaml
from tests.v1.conftest import command, KIT
from cli.main import COMMANDS, _arguments, ValidatedContext
from cli.v1_io import Refusal


def git(root, *args):
    p = subprocess.run(['/usr/bin/git','-c','core.hooksPath=/dev/null','-C',str(root),*args], capture_output=True,text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


def settings(root, **values):
    path=root/'.overseer/config.yaml'
    c=yaml.safe_load(path.read_text());c.update(values);path.write_text(yaml.safe_dump(c,sort_keys=False))
    return c


@pytest.mark.parametrize('name', sorted(COMMANDS))
def test_actual_command_help(name):
    p=command(name,'--help')
    assert p.returncode == 0, p.stderr
    assert 'usage:' in p.stdout


def test_registry_covers_all_historical_commands_and_subcommands():
    tree=ast.parse((KIT/'cli/legacy_main.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id','')=='COMMANDS' for t in n.targets))
    assert ast.literal_eval(node.value.args[0]) <= COMMANDS
    for cmd, sub in [('workspace','status'),('workspace','check-next'),('workspace','doctor'),('ledger','append'),('ledger','verify'),('ledger','show')]:
        assert command(cmd,sub,'--help').returncode == 0


def test_status_route_full_assets_read_only(repo):
    before={p.relative_to(repo):p.read_bytes() for p in repo.rglob('*') if p.is_file() and '.git' not in p.parts}
    p=command('-C',repo,'status','--workspace','--check-footprint','--json')
    assert p.returncode==0,p.stderr
    state=json.loads(p.stdout)
    assert {'governance','governance_gates','model_routing','cost_awareness','optional_feature_tips','footprint_integrity','workspace','readiness'}<=state.keys()
    assert state['footprint_integrity']['ok']
    assert command('-C',repo,'route','--validate').returncode == 0
    assert command('-C',repo,'route','--position','thinking','--phase-tier','tier3','--gate','freeze_review').returncode == 0
    assert before=={p.relative_to(repo):p.read_bytes() for p in repo.rglob('*') if p.is_file() and '.git' not in p.parts}


@pytest.mark.parametrize('argv',[
    ['governance-sync','--write','--dry-run'],['governance-sync','--print-next','--write'],
    ['governance-sync','--push','--write'],['pr-land','--pr','1','--authorized','fixture'],
    ['hosted-dashboard'],['land-closeout','--probe-merged-pr'],
    ['handover-compact','--write','--dry-run'],['workspace','status','-C','/tmp','-C','/'],
])
def test_contradictions_refuse_before_execution(repo,argv):
    p=command('-C',repo,*argv)
    assert p.returncode==2,p.stdout+p.stderr


def test_check_ok_review_dry_run_stamp_and_confinement(repo):
    args=['-C',repo,'check-ok','--path','docs/reviews/check.md','--topic','fixture','--scope','bounded fixture']
    p=command(*args,'--dry-run','--json');assert p.returncode==0,p.stderr
    assert not (repo/'docs/reviews/check.md').exists()
    p=command(*args,'--scaffold-only');assert p.returncode==0,p.stderr
    p=command('-C',repo,'review','--freeze','docs/reviews/check.md','--json');assert p.returncode==0,p.stderr+p.stdout
    report=json.loads(p.stdout);assert report['gate']=='mechanical'
    assert 'mechanical_verdict' in (repo/'docs/reviews/check.md').read_text()
    assert command('-C',repo,'check-if-ok','--path','docs/reviews/check.md','--dry-run').returncode==0
    for path in ('../escape.md','.overseer/config.yaml','docs/NEXT.md'):
        p=command('-C',repo,'check-ok','--path',path,'--force-scaffold','--scaffold-only')
        assert p.returncode!=0,p.stdout
    (repo/'docs/reviews/link.md').symlink_to(repo/'docs/reviews/check.md')
    assert command('-C',repo,'review','--freeze','docs/reviews/link.md').returncode!=0


def test_governance_print_next_and_local_commit(repo):
    manual=command('-C',repo,'next').stdout
    p=command('-C',repo,'governance-sync','--print-next','--json');assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['rendered']==manual
    git(repo,'add','.');git(repo,'commit','-m','fixture');git(repo,'checkout','-b','feat/hygiene')
    next_bytes=(repo/'docs/NEXT.md').read_bytes()
    old=git(repo,'rev-parse','HEAD')
    p=command('-C',repo,'governance-sync','--dry-run');assert p.returncode==0,p.stderr
    assert git(repo,'status','--porcelain')==''
    p=command('-C',repo,'governance-sync','--write','--json');assert p.returncode==0,p.stderr+p.stdout
    assert json.loads(p.stdout)['committed']
    assert git(repo,'rev-parse','HEAD^')==old
    assert (repo/'docs/NEXT.md').read_bytes()==next_bytes
    assert set(git(repo,'diff-tree','--no-commit-id','--name-only','-r','HEAD').splitlines())=={'docs/OVERSEER-HANDOVER.md','docs/ROADMAP.md'}
    p=command('-C',repo,'governance-sync','--write','--json');assert p.returncode==0,p.stderr
    assert not json.loads(p.stdout)['committed']


def test_compaction_uses_bound_atomic_writer(repo):
    from tools.handover_compact.compact import CHANGE_LOG_START,CHANGE_LOG_END
    path=repo/'docs/OVERSEER-HANDOVER.md'
    path.write_text('# Handover\n'+CHANGE_LOG_START+'\n'+''.join(f'- **2026-10-{i:02d}** — entry {i}\n' for i in range(20,0,-1))+CHANGE_LOG_END+'\n')
    before=path.read_bytes(); nxt=(repo/'docs/NEXT.md').read_bytes()
    assert command('-C',repo,'handover-compact','--keep','5','--dry-run').returncode==0
    assert path.read_bytes()==before
    p=command('-C',repo,'handover-compact','--keep','5','--write');assert p.returncode==0,p.stderr+p.stdout
    assert (repo/'docs/archive/handover/CHANGE-LOG.md').exists()
    assert (repo/'docs/NEXT.md').read_bytes()==nxt


def test_ledger_append_verify_show_and_honesty(repo):
    original=yaml.safe_load((KIT/'tests/fixtures/honesty/config-honesty-enabled.yaml').read_text())
    settings(repo,honesty=original['honesty'])
    (repo/'entry.json').write_text('{}')
    p=command('-C',repo,'ledger','append','--kind','genesis','--file','entry.json','--json')
    assert p.returncode==0,p.stderr+p.stdout
    assert command('-C',repo,'ledger','verify').returncode==0
    p=command('-C',repo,'ledger','show','--last','1','--json');assert p.returncode==0,p.stderr
    assert len(json.loads(p.stdout)['entries'])==1
    p=command('-C',repo,'honesty-status','--hook','handoff','--artifact','entry.json','--json');assert p.returncode in (0,20),p.stdout+p.stderr


def test_engine_write_rechecks_context_and_file_cas(repo):
    from cli.product_boundary import engine_boundary
    args=_arguments(['-C',str(repo),'check-ok','--scaffold-only'])
    c=ValidatedContext.capture(repo,args)
    path=repo/'target.txt';path.write_text('before')
    with pytest.raises(Refusal,match='stale_write'):
        with engine_boundary(c,args,writable=True) as b:
            b.watch(path);path.write_text('owner edit');b.write(path,b'bad')
    assert path.read_text()=='owner edit'
    with pytest.raises(Refusal,match='context_changed'):
        with engine_boundary(c,args,writable=True) as b:
            b.watch(path);git(repo,'checkout','-b','changed');b.write(path,b'bad')
    assert path.read_text()=='owner edit'
