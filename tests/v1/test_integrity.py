import hashlib
import os
from pathlib import Path
import subprocess
import time
from unittest.mock import patch

import pytest

from cli.v1_io import Refusal, atomic, digest, read
from tests.v1.conftest import command, status, write_action


@pytest.mark.parametrize('component',['.overseer/config.yaml','docs/NEXT.md','docs','.overseer'])
def test_symlinks_cannot_cross_repository(pair,tmp_path,component):
    a,b=pair
    target=b/component
    saved=target.with_name(target.name+'.saved')
    target.rename(saved)
    target.symlink_to(a/component,target_is_directory=saved.is_dir())
    for cmd in ('next','status','sync'):
        r=command('-C',b,cmd)
        assert r.returncode != 0 and 'Unique content for '+a.name not in r.stdout


def test_hardlinked_next_refused(pair):
    a,b=pair
    (b/'docs/NEXT.md').unlink();os.link(a/'docs/NEXT.md',b/'docs/NEXT.md')
    r=command('-C',b,'next')
    assert r.returncode != 0 and not r.stdout


@pytest.mark.parametrize('failure',['replace','fsync'])
def test_atomic_failure_preserves_old_bytes_and_removes_temp(tmp_path,failure):
    (tmp_path/'docs').mkdir();path=tmp_path/'docs/NEXT.md';path.write_bytes(b'old\n')
    with patch('cli.v1_io.os.'+failure,side_effect=OSError('injected before publication')):
        with pytest.raises(OSError):
            atomic(tmp_path,'docs/NEXT.md',b'new\n',expected=digest(b'old\n'))
    assert path.read_bytes()==b'old\n'
    assert list(path.parent.iterdir())==[path]


def test_atomic_unique_temp_and_permissions(tmp_path):
    atomic(tmp_path,'docs/NEXT.md',b'first\n',expected='absent')
    with pytest.raises(Refusal,match='stale_write'):
        atomic(tmp_path,'docs/NEXT.md',b'second\n',expected='absent')
    assert (tmp_path/'docs/NEXT.md').stat().st_mode & 0o777 == 0o644


def test_writer_rejects_external_or_symlink_prompt(repo,tmp_path):
    outside=tmp_path/'outside';outside.write_text('external')
    for candidate in ('../outside',str(outside),'prompt-link'):
        if candidate=='prompt-link': (repo/candidate).symlink_to(outside)
        state=status(repo)
        result=write_action(repo,'valid',prompt_file=candidate)
        assert result.returncode != 0
        assert status(repo)['next_sha256']==state['next_sha256']


def test_oversized_next_refused(repo):
    (repo/'docs/NEXT.md').write_bytes(b'x'*140000)
    assert command('-C',repo,'next').returncode != 0


def test_concurrent_readers_and_cas_writers(repo):
    state=status(repo)
    (repo/'prompt-a').write_text('Concurrent A\n');(repo/'prompt-b').write_text('Concurrent B\n')
    from tests.v1.conftest import KIT
    args=[str(KIT/'cli/ok'),'-C',str(repo),'next-write','--repo-id',state['repository']['id'],
          '--branch','main','--lane','product','--model','GPT-6 Astra','--action-id','CONCURRENT',
          '--action-kind','implement','--expect-next',state['next_sha256']]
    workers=[subprocess.Popen(args+['--prompt-file',p],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
             for p in ('prompt-a','prompt-b')]
    for _ in range(5):
        r=command('-C',repo,'next');assert r.returncode==0,r.stderr
    outcomes=[(p.communicate(timeout=10),p.returncode) for p in workers]
    assert sorted(code for _,code in outcomes)==[0,2]
    assert not list((repo/'docs').glob('.NEXT.md.*'))


def test_next_read_bounded(repo):
    start=time.monotonic()
    for _ in range(10):assert command('-C',repo,'next').returncode==0
    assert time.monotonic()-start < 10


def test_post_replace_directory_fsync_failure_reports_failure_with_whole_file(tmp_path):
    atomic(tmp_path,'docs/NEXT.md',b'old',expected='absent')
    original=os.fsync;calls=0
    def fail_directory(fd):
        nonlocal calls
        calls+=1
        if calls==2:raise OSError('directory persistence failed after publication')
        return original(fd)
    with patch('cli.v1_io.os.fsync',side_effect=fail_directory):
        with pytest.raises(OSError):atomic(tmp_path,'docs/NEXT.md',b'new',expected=digest(b'old'))
    assert (tmp_path/'docs/NEXT.md').read_bytes()==b'new'
    assert not list((tmp_path/'docs').glob('.NEXT.md.*'))


def test_raw_digest_preserves_exact_next_bytes():
    assert digest(b'a\r\n') != digest(b'a\n')


def test_old_test_sources_preserved():
    import json
    from tests.v1.conftest import KIT
    entries=json.loads((KIT/'tests/historical/baseline-test-inventory.json').read_text())
    assert entries
    for item in entries:
        assert digest((KIT/item['path']).read_bytes())==item['sha256'],item['path']
