"""Real dispatcher and shared service checks for the restored retained engines."""
import json
import shutil
from pathlib import Path
import pytest
import yaml
from tests.v1.conftest import KIT, command
from tests.fpr3.test_commands import settings


def test_checkpoint_real_script_dry_run_failure_and_confinement(repo):
    source=KIT/'tests/fixtures/checkpoints'
    for directory in ('policy','manifests','scripts'):
        shutil.copytree(source/directory,repo/directory,dirs_exist_ok=True)
    for p in (repo/'scripts/verify').glob('*.py'):p.chmod(0o755)
    c=yaml.safe_load((source/'config-checkpoints-enabled.yaml').read_text())
    settings(repo,checkpoints=c['checkpoints'],modules=c['modules'])
    path=repo/'manifests/work-unit.yaml'; before=path.read_bytes()
    p=command('-C',repo,'verify-step','--step','alpha','--dry-run','--json')
    assert p.returncode==0,p.stderr+p.stdout
    assert path.read_bytes()==before
    p=command('-C',repo,'verify-step','--step','alpha','--json')
    assert p.returncode==0,p.stderr+p.stdout
    assert yaml.safe_load(path.read_text())['steps']['alpha']['verified'] is True
    policy=repo/'policy/checkpoints.yaml'; text=policy.read_text()
    policy.write_text(text.replace('scripts/verify/verify_alpha.py','scripts/verify/verify_gamma_fail.py'))
    p=command('-C',repo,'verify-step','--step','alpha','--json')
    assert p.returncode!=0,p.stdout
    policy.write_text(text.replace('scripts/verify/verify_alpha.py','../outside.py'))
    assert command('-C',repo,'verify-step','--step','alpha').returncode!=0


def test_review_fake_provider_human_fallback_never_passes(repo):
    from cli.main import ValidatedContext,_arguments
    from cli.product_service import invoke
    from tests.support import unreachable_provider_factory
    assert command('-C',repo,'check-ok','--path','docs/reviews/check.md','--scaffold-only').returncode==0
    args=_arguments(['-C',str(repo),'review','--freeze','docs/reviews/check.md','--provider','api','--json'])
    code,result=invoke(ValidatedContext.capture(repo,args),args,provider_factory=unreachable_provider_factory('offline fixture'))
    assert code==8,result
    assert not result['ok']
    assert command('-C',repo,'review','--freeze','docs/reviews/check.md','--provider','api').returncode==2


def test_fake_pr_transport_requires_explicit_authorization_and_preserves_context(repo):
    from tests.fpr3.test_commands import git
    git(repo, 'remote', 'add', 'origin', 'https://github.com/fixture/bound.git')
    before=(repo/'docs/NEXT.md').read_bytes()
    gh=repo/'fake-gh'
    gh.write_text('#!/bin/sh\ncase "$2" in\nview) echo \'{"state":"OPEN"}\';;\nchecks) printf "ci\\tpass\\t0s\\tfixture\\n";;\nmerge) exit 77;;\nesac\n')
    gh.chmod(0o755)
    p=command('-C',repo,'pr-land','--pr','1','--authorized','disposable fixture','--allow-network','--gh',gh,'--dry-run','--json')
    assert p.returncode==0,p.stderr+p.stdout
    assert not json.loads(p.stdout)['merged']
    assert (repo/'docs/NEXT.md').read_bytes()==before


def test_full_footprint_preserves_settings_origins_and_next(repo):
    cfg=repo/'.overseer/config.yaml'; original=cfg.read_bytes(); nxt=(repo/'docs/NEXT.md').read_bytes()
    path=repo/'.cursor/rules/orchestrator.mdc'; path.write_text('Owner-specific instructions\n')
    p=command('-C',repo,'sync','--preserve-modified','--json'); assert p.returncode==0,p.stderr
    assert cfg.read_bytes()==original and (repo/'docs/NEXT.md').read_bytes()==nxt
    lock=yaml.safe_load((repo/'.overseer/version.lock').read_text())
    assert next(row for row in lock['footprint'] if row['path']=='.cursor/rules/orchestrator.mdc')['origin']=='preserved'
    assert path.read_text()=='Owner-specific instructions\n'
    assert any(row['path'].startswith('.claude/skills/') for row in lock['footprint'])
    assert command('-C',repo,'status','--check-footprint').returncode==0
    (repo/'.claude/skills/check-ok/SKILL.md').unlink()
    assert command('-C',repo,'status','--check-footprint').returncode==1


def test_atomic_reader_reopens_replaced_inode_without_accepting_hardlinks(repo,monkeypatch):
    import os
    from cli import v1_io
    path=repo/'atomic-input';path.write_bytes(b'old')
    replacement=repo/'replacement';replacement.write_bytes(b'new')
    original=os.open
    fired=False
    def opening(name,*a,**kw):
        nonlocal fired
        fd=original(name,*a,**kw)
        if Path(name)==path and not fired:
            fired=True;os.replace(replacement,path)
        return fd
    monkeypatch.setattr(os,'open',opening)
    assert v1_io.read(repo,'atomic-input')==b'new'
    os.link(path,repo/'other-link')
    with pytest.raises(v1_io.Refusal):v1_io.read(repo,'atomic-input')


def test_landing_compares_pinned_binary_bytes_and_requires_current_next(repo):
    from tests.fpr3.test_commands import git
    from tests.muse.test_handoffs import publish
    (repo/'binary.bin').write_bytes(b'\x00\xff\r\n')
    settings(repo,close_ritual={'enabled':True,'require_paths':['binary.bin']})
    git(repo,'add','.');git(repo,'commit','-m','binary fixture')
    assert publish(repo).returncode==0
    p=command('-C',repo,'land-check','--json');assert p.returncode==0,p.stderr+p.stdout
    assert json.loads(p.stdout)['landed'] is True
    (repo/'binary.bin').write_bytes(b'changed')
    assert command('-C',repo,'land-check').returncode!=0
