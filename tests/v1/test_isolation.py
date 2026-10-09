import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml

from tests.v1.conftest import KIT, command, status


def assert_selected(result, wanted, other):
    assert result.returncode == 0, result.stderr
    assert 'Unique content for ' + wanted.name + '\n' in result.stdout
    assert 'Unique content for ' + other.name + '\n' not in result.stdout
    assert str(wanted) in result.stdout
    assert status(wanted)['repository']['id'] in result.stdout


def test_cwd_and_explicit_C_select_only_intended_repository(pair, tmp_path):
    a,b=pair
    assert status(a)['repository']['id'] != status(b)['repository']['id']
    assert status(a)['next']['action_id'] == status(b)['next']['action_id'] == 'SAME-ACTION'
    for wanted,other in ((a,b),(b,a)):
        (wanted/'nested').mkdir()
        for cwd in (wanted,wanted/'nested'):
            assert_selected(command('next',cwd=cwd),wanted,other)
        for cwd in (other,tmp_path,wanted/'nested'):
            assert_selected(command('-C',wanted,'next',cwd=cwd),wanted,other)
            assert_selected(command('next','-C',wanted,cwd=cwd),wanted,other)
        assert command('-C',wanted/'nested','next').returncode != 0
    assert command('next',cwd=tmp_path).returncode != 0


@pytest.mark.parametrize('file', ['.overseer/config.yaml','docs/NEXT.md'])
def test_copied_config_or_next_fails_without_foreign_prompt(pair, file):
    a,b=pair
    shutil.copyfile(a/file,b/file)
    for cmd in ('next','status'):
        r=command('-C',b,cmd)
        assert r.returncode != 0
        assert 'Unique content for '+a.name not in r.stdout
    if file.endswith('config.yaml'):
        assert command('-C',b,'sync').returncode != 0
        assert command('-C',b,'init').returncode != 0


def test_copied_config_and_next_still_fail(pair):
    a,b=pair
    for file in ('.overseer/config.yaml','docs/NEXT.md'):
        shutil.copyfile(a/file,b/file)
    assert command('-C',b,'next').returncode != 0


def test_foreign_explicit_config_refused(pair):
    a,b=pair
    r=command('-C',b,'--config',a/'.overseer/config.yaml','next')
    assert r.returncode != 0 and not r.stdout


def test_bound_launchers_respect_cwd_explicit_path_and_copy_location(pair,tmp_path):
    a,b=pair
    for root,other in ((a,b),(b,a)):
        launcher=root/'.overseer/bin/ok'
        assert_selected(command('next',cwd=root,executable=launcher),root,other)
        assert command('next',cwd=other,executable=launcher).returncode != 0
        assert_selected(command('-C',root,'next',cwd=other,executable=launcher),root,other)
        assert command('-C',other,'next',cwd=root,executable=launcher).returncode != 0
    shutil.copyfile(a/'.overseer/bin/ok',b/'.overseer/bin/ok')
    for cwd,args in ((b,()),(a,()),(b,('-C',a))):
        r=command(*args,'next',cwd=cwd,executable=b/'.overseer/bin/ok')
        assert r.returncode != 0 and not r.stdout


@pytest.mark.parametrize('name',['session-start-next.sh','session-end-closeout.sh'])
def test_hook_context_and_copied_hook_fail_closed(pair,name):
    a,b=pair
    hook=a/'.cursor/hooks'/name
    event=json.dumps({'workspace_roots':[str(a)]})
    r=command(cwd=a,executable=hook,input=event)
    assert r.returncode == 0
    payload=json.loads(r.stdout)
    assert 'Unique content for '+a.name in payload['additional_context']
    for cwd,roots in ((b,[str(a)]),(a,[str(b)]),(a,[str(a),str(b)])):
        r=command(cwd=cwd,executable=hook,input=json.dumps({'workspace_roots':roots}))
        assert r.returncode != 0 and not r.stdout
    shutil.copyfile(hook,b/'.cursor/hooks'/name)
    for cwd in (a,b):
        r=command(cwd=cwd,executable=b/'.cursor/hooks'/name,input='{}')
        assert r.returncode != 0 and not r.stdout


def test_environment_poisoning_cannot_select_neighbor(pair,tmp_path):
    a,b=pair
    poison=tmp_path/'poison';poison.mkdir()
    marker=tmp_path/'executed'
    for name in ('python3','git','ok'):
        p=poison/name;p.write_text('#!/bin/sh\ntouch '+str(marker)+'\nexit 99\n');p.chmod(0o755)
    (poison/'sitecustomize.py').write_text('raise RuntimeError("poison")\n')
    (poison/'cli').mkdir();(poison/'cli/__init__.py').write_text('raise RuntimeError("poison")\n')
    env={'PATH':str(poison),'PYTHONPATH':str(poison),'PYTHONHOME':str(poison),
         'VIRTUAL_ENV':str(b), 'GIT_DIR':str(b/'.git'),'GIT_WORK_TREE':str(b),
         'OVERSEER_OK':str(b/'.overseer/bin/ok'),'GIT_CONFIG_COUNT':'1',
         'GIT_CONFIG_KEY_0':'core.worktree','GIT_CONFIG_VALUE_0':str(b)}
    assert_selected(command('-C',a,'next',cwd=b,env=env),a,b)
    r=command(cwd=a,executable=a/'.cursor/hooks/session-start-next.sh',env=env,input='{}')
    assert r.returncode == 0, r.stderr
    assert not marker.exists()


def test_runtime_from_neighbor_refused(pair):
    a,b=pair
    path=b/'.overseer/config.yaml'
    config=yaml.safe_load(path.read_text());config['runtime']['root']=str(a)
    path.write_text(yaml.safe_dump(config))
    for cmd in ('next','sync','status'):
        r=command('-C',b,cmd)
        assert r.returncode != 0 and not r.stdout


def test_duplicate_C_or_bound_override_refused(pair):
    a,b=pair
    for args in [('-C',a,'next','-C',b),('-C',a,'next','--repo='+str(b)),
                 ('--bound-root',str(b),'next')]:
        r=command(*args,cwd=a,executable=a/'.overseer/bin/ok')
        assert r.returncode != 0 and not r.stdout


def test_symlink_repository_alias_resolves_same_physical_root(pair,tmp_path):
    a,b=pair
    alias=tmp_path/'alias';alias.symlink_to(a,target_is_directory=True)
    assert_selected(command('-C',alias,'next'),a,b)


def test_source_shim_copied_without_runtime_does_not_fall_back(pair):
    a,b=pair
    (b/'cli').mkdir();shutil.copy2(KIT/'cli/ok',b/'cli/ok')
    r=command('-C',b,'next',cwd=a,executable=b/'cli/ok')
    assert r.returncode != 0 and not r.stdout and 'no runtime fallback' in r.stderr


def test_relative_bound_launcher_from_child_directory(pair):
    a,b=pair
    (a/'child').mkdir()
    assert_selected(command('next',cwd=a/'child',executable='../.overseer/bin/ok'),a,b)
