import hashlib
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from cli.v1 import parse_next
from tests.v1.conftest import KIT, command, seed, status, write_action


def fingerprint(root):
    return {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mode)
            for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}


def test_status_init_sync_and_persistent_identity(repo):
    original = status(repo)
    before = fingerprint(repo)
    for cmd in ('status', 'next', 'status', 'next'):
        r = command('-C', repo, cmd)
        assert r.returncode == 0, r.stderr
    assert fingerprint(repo) == before
    assert command('-C', repo, 'init', '--hooks').returncode == 0
    assert command('-C', repo, 'sync', '--hooks').returncode == 0
    assert fingerprint(repo) == before
    assert status(repo)['repository'] == original['repository']


def test_init_preserves_living_docs(tmp_path):
    root = seed(tmp_path / 'preexisting')
    (root / 'docs').mkdir()
    for name in ('ROADMAP.md', 'OVERSEER-HANDOVER.md'):
        (root / 'docs' / name).write_text('Owner document\n')
    assert command('-C', root, 'init').returncode == 0
    for name in ('ROADMAP.md', 'OVERSEER-HANDOVER.md'):
        assert (root / 'docs' / name).read_text() == 'Owner document\n'


def test_canonical_next_ignores_old_handover_and_roadmap(repo):
    for name in ('ROADMAP.md', 'OVERSEER-HANDOVER.md'):
        (repo / 'docs' / name).write_text('NEXT: OBSOLETE-SECURITY-TASK\n')
    result = command('-C', repo, 'next')
    assert result.returncode == 0
    assert 'OBSOLETE' not in result.stdout
    assert 'Action ID: SETUP' in result.stdout
    assert str(repo) in result.stdout


def test_sync_preserves_next_and_living_docs(repo):
    write_action(repo, 'Retained action\n')
    before = {p: (repo / p).read_bytes() for p in ('docs/NEXT.md', 'docs/ROADMAP.md', 'docs/OVERSEER-HANDOVER.md')}
    assert command('-C', repo, 'sync', '--hooks').returncode == 0
    assert all((repo / p).read_bytes() == data for p, data in before.items())


def test_writer_cas_rejects_stale_and_wrong_context(repo):
    state = status(repo)
    write_action(repo, 'First action\n')
    before = (repo / 'docs/NEXT.md').read_bytes()
    r = write_action(repo, 'Overwritten action\n', expect_next=state['next_sha256'])
    assert r.returncode != 0
    assert 'stale_write' in r.stderr
    assert (repo / 'docs/NEXT.md').read_bytes() == before


@pytest.mark.parametrize('field,value', [('repo_id','00000000-0000-0000-0000-000000000000'),
    ('branch','other'), ('lane','other'), ('model','Other Model'), ('action_id','bad/action'),
    ('action_kind','deploy')])
def test_writer_binding_checks(repo, field, value):
    before = (repo / 'docs/NEXT.md').read_bytes()
    r = write_action(repo, 'Safe prompt\n', **{field:value})
    assert r.returncode != 0 and not r.stdout
    assert (repo / 'docs/NEXT.md').read_bytes() == before


@pytest.mark.parametrize('field,value', [('repo-id','00000000-0000-0000-0000-000000000000'),
    ('branch','other'), ('lane','other'), ('model','Other Model'), ('action-id','OTHER'),
    ('action-kind','review'), ('expect-next','0'*64)])
def test_reader_expectations_fail_without_prompt(repo, field, value):
    r = command('-C', repo, 'next', '--'+field, value)
    assert r.returncode != 0 and not r.stdout


def test_missing_next_is_not_regenerated(repo):
    (repo / 'docs/NEXT.md').unlink()
    r = command('-C', repo, 'next')
    assert r.returncode != 0 and not r.stdout
    state = command('-C', repo, 'status', '--json')
    assert state.returncode == 1
    assert 'file_missing' in json.loads(state.stdout)['next_error']
    assert command('-C', repo, 'sync').returncode == 0
    assert not (repo / 'docs/NEXT.md').exists()


@pytest.mark.parametrize('text', ['not frontmatter', '---\nrepo_id: [broken\n---\nbody',
    '---\nschema: 1\nschema: 1\n---\nprompt', '---\n{}\n---\nprompt', ''])
def test_malformed_next_fails_closed(repo, text):
    (repo / 'docs/NEXT.md').write_text(text)
    r = command('-C', repo, 'next')
    assert r.returncode != 0 and not r.stdout


def test_hand_edit_of_prompt_detected(repo):
    p = repo / 'docs/NEXT.md'
    p.write_text(p.read_text() + 'Stale accidental edit\n')
    r = command('-C', repo, 'next')
    assert r.returncode != 0 and 'prompt_digest_mismatch' in r.stderr


def test_branch_and_head_freshness(repo):
    subprocess.run(['/usr/bin/git','-C',str(repo),'switch','-c','changed'], check=True, capture_output=True)
    r = command('-C', repo, 'next')
    assert r.returncode != 0 and 'branch_mismatch' in r.stderr
    subprocess.run(['/usr/bin/git','-C',str(repo),'switch','main'], check=True, capture_output=True)
    subprocess.run(['/usr/bin/git','-C',str(repo),'add','.'], check=True)
    # Preserve the legacy tracked-NEXT closing-commit exception explicitly.
    # New init now excludes checkout-local NEXT from ordinary git add.
    subprocess.run(['/usr/bin/git','-C',str(repo),'add','-f','docs/NEXT.md'], check=True)
    subprocess.run(['/usr/bin/git','-C',str(repo),'-c','core.hooksPath=/dev/null','commit','-m','publish NEXT'], check=True, capture_output=True)
    assert command('-C', repo, 'next').returncode == 0
    subprocess.run(['/usr/bin/git','-C',str(repo),'-c','core.hooksPath=/dev/null','commit','--allow-empty','-m','later work'], check=True, capture_output=True)
    r = command('-C', repo, 'next')
    assert r.returncode != 0 and 'next_stale_head' in r.stderr


def test_detached_head_refused(repo):
    subprocess.run(['/usr/bin/git','-C',str(repo),'checkout','--detach'], check=True, capture_output=True)
    r = command('-C', repo, 'next')
    assert r.returncode != 0 and not r.stdout and 'detached_head' in r.stderr


def test_prompt_fences_are_contained(repo):
    write_action(repo, 'Example:\n```text\ncontent\n```\n')
    r = command('-C', repo, 'next')
    assert r.returncode == 0
    assert '\n````text\n' in r.stdout and r.stdout.endswith('````\n')


def test_prompt_cannot_introduce_contradictory_binding(repo):
    state = status(repo)
    r = write_action(repo, 'Model: a different model\n', action_id='OTHER')
    assert r.returncode != 0
    assert status(repo)['next_sha256'] == state['next_sha256']


def test_required_writer_arguments(repo):
    r = command('-C', repo, 'next-write')
    assert r.returncode != 0 and not r.stdout


def test_runtime_hash_change_requires_explicit_sync(repo):
    config_path = repo / '.overseer/config.yaml'
    config = yaml.safe_load(config_path.read_text())
    identity = config['repo']['id']
    config['runtime']['sha256'] = '0'*64
    config_path.write_text(yaml.safe_dump(config))
    assert command('-C',repo,'next').returncode != 0
    before = fingerprint(repo)
    dry = command('-C',repo,'sync','--dry-run','--json')
    assert dry.returncode == 0 and '.overseer/config.yaml' in json.loads(dry.stdout)['changed']
    assert fingerprint(repo) == before
    assert command('-C',repo,'sync').returncode == 0
    assert status(repo)['repository']['id'] == identity


def test_source_and_compat_launcher(repo):
    for launcher in (KIT/'cli/ok', KIT/'cli/overseer'):
        assert command('-C',repo,'status',executable=launcher).returncode == 0
    assert (KIT/'.venv/bin/python3').is_symlink()


def test_unsupported_commands_cannot_run(repo):
    for cmd in ('pr-land','governance-sync','upgrade-regime','app'):
        r = command('-C',repo,cmd)
        assert r.returncode != 0 and not r.stdout


def test_unborn_repository_first_commit_is_supported(tmp_path):
    root=tmp_path/'unborn';root.mkdir()
    subprocess.run(['/usr/bin/git','-C',str(root),'init','-b','main'],check=True,capture_output=True)
    assert command('-C',root,'init').returncode==0
    assert status(root)['head']=='unborn'
    subprocess.run(['/usr/bin/git','-C',str(root),'add','.'],check=True)
    subprocess.run(['/usr/bin/git','-C',str(root),'-c','user.name=Fixture','-c',
        'user.email=fixture@example.invalid','-c','core.hooksPath=/dev/null','commit','-m','first'],check=True,capture_output=True)
    r = command('-C',root,'next')
    assert r.returncode == 2 and 'next_stale_head' in r.stderr
    # The ignored local handoff is deliberately published after the first commit.
    import yaml
    cfg = yaml.safe_load((root/'.overseer/config.yaml').read_bytes())
    from cli.v1_io import digest
    (root/'prompt.txt').write_text('First post-commit task.\n')
    r = command('-C',root,'next-write','--repo-id',cfg['repo']['id'], '--branch','main',
                '--lane','product','--model','GPT-6 Astra','--action-id','FIRST',
                '--action-kind','implement','--expect-next',digest((root/'docs/NEXT.md').read_bytes()),
                '--prompt-file','prompt.txt')
    assert r.returncode == 0, r.stderr
    assert command('-C',root,'next').returncode == 0


def test_git_worktree_supported(repo,tmp_path):
    # A separate linked worktree has its own checkout identity, never inherits
    # the main checkout's bound config even though Git history is shared.
    other=tmp_path/'linked'
    subprocess.run(['/usr/bin/git','-C',str(repo),'worktree','add','-b','linked',str(other)],check=True,capture_output=True)
    assert command('-C',other,'init').returncode==0
    assert status(other)['branch']=='linked'
    assert status(other)['repository']['id'] != status(repo)['repository']['id']


@pytest.mark.parametrize('section,field,value', [('repo','id','bad'),('context','lane','bad/lane'),
    ('context','model',''),('runtime','version','wrong')])
def test_malformed_config_refused(repo,section,field,value):
    path=repo/'.overseer/config.yaml';config=yaml.safe_load(path.read_text())
    config[section][field]=value;path.write_text(yaml.safe_dump(config))
    r=command('-C',repo,'next')
    assert r.returncode!=0 and not r.stdout


def test_duplicate_config_key_refused(repo):
    p=repo/'.overseer/config.yaml';p.write_text(p.read_text()+'schema: 1\n')
    r=command('-C',repo,'next')
    assert r.returncode!=0 and 'duplicate_or_invalid_key' in r.stderr


def test_bad_hook_event_refuses_cleanly(repo):
    hook=repo/'.cursor/hooks/session-start-next.sh'
    for event in ('[]','{broken','{"workspace_roots":[17]}','{"workspace_roots":"wrong"}'):
        r=command(cwd=repo,executable=hook,input=event)
        assert r.returncode!=0 and not r.stdout and 'Traceback' not in r.stderr


def test_sync_dry_run_plans_missing_launcher_without_writes(repo):
    from tests.v1.test_commands import fingerprint
    path=repo/'.overseer/bin/ok';path.unlink();path.parent.rmdir()
    before=fingerprint(repo)
    r=command('-C',repo,'sync','--dry-run','--json')
    assert r.returncode==0,r.stderr
    assert '.overseer/bin/ok' in json.loads(r.stdout)['changed']
    assert fingerprint(repo)==before and not path.parent.exists()
    assert command('-C',repo,'sync').returncode==0
    assert command('next',cwd=repo,executable=path).returncode==0
