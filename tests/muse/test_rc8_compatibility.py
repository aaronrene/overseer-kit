"""Exact rc8 reader qualification in disposable native stores (no services).

This tests tip reading, including native N-parent integrity. It does not claim
that the tip projection is a full-history export or preserves historical modes.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest
from cli.v1_io import Refusal
from cli.v1_revision import muse_read, revision
from tests.muse.test_handoffs import inventory

KIT = Path(__file__).resolve().parents[2]


def child(python, code, *args):
    result = subprocess.run([str(python), '-I', '-B', '-c', code, str(KIT), *map(str, args)],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


@pytest.fixture
def native_rc8(muse_runtime, muse_root, muse):
    if muse_runtime.version != '0.2.3rc8':
        pytest.skip('rc8 checkout-local state/exclusion contract; legacy coverage remains separate')
    root = muse_root
    (root / 'app.py').write_text('value = 1\n')
    muse(root, 'code', 'add', '.')
    muse(root, 'commit', '-m', 'rc8 native seed', '--json')
    return root


def test_rc8_revision_dirty_and_recovery_bytes_are_readonly(native_rc8, muse_python, muse):
    root = native_rc8
    (root / '.muse/.muse-tmp-preserve').write_bytes(b'recovery bytes')
    before = inventory(root)
    clean = muse_read(root, str(muse_python), dirty=True)
    assert clean['dirty'] is False and clean['branch'] == 'main'
    assert inventory(root) == before
    (root / 'app.py').write_text('value = 2\n')
    muse(root, 'code', 'add', 'app.py')
    before = inventory(root)
    assert muse_read(root, str(muse_python), dirty=True)['dirty'] is True
    assert inventory(root) == before


def test_rc8_linked_checkout_owns_head_stage_and_interruption_state(native_rc8, muse_python, muse, tmp_path):
    root = native_rc8
    linked = (tmp_path / 'linked').resolve()
    muse(root, 'worktree', 'add', 'linked', 'main', '-b', 'feature', '--path', str(linked), '--json')
    (root / 'app.py').write_text('primary staged change\n')
    muse(root, 'code', 'add', 'app.py')
    before = inventory(root), inventory(linked)
    assert muse_read(root, str(muse_python), dirty=True)['dirty'] is True
    state = muse_read(linked, str(muse_python), dirty=True)
    assert state['branch'] == 'feature' and state['dirty'] is False
    assert (inventory(root), inventory(linked)) == before
    (linked / 'app.py').write_text('linked staged change\n')
    muse(linked, 'code', 'add', 'app.py')
    assert muse_read(linked, str(muse_python), dirty=True)['dirty'] is True
    sentinel = root / '.muse/worktrees/linked/CHECKOUT_HEAD'
    sentinel.write_text('interrupted checkout\n')
    before = inventory(root), inventory(linked)
    with pytest.raises(Refusal, match='muse_read_failed'):
        muse_read(linked, str(muse_python))
    # Primary is unaffected by a linked checkout's interruption.
    assert muse_read(root, str(muse_python))['branch'] == 'main'
    assert (inventory(root), inventory(linked)) == before


def test_rc8_legacy_linked_head_requires_native_repair_without_fallback(native_rc8, muse_python, muse, tmp_path):
    root = native_rc8
    linked = (tmp_path / 'linked').resolve()
    muse(root, 'worktree', 'add', 'linked', 'main', '-b', 'feature', '--path', str(linked), '--json')
    head = root / '.muse/worktrees/linked/HEAD'
    head.unlink()
    (root / '.muse/worktrees/linked.HEAD').write_text('refs/heads/feature\n')
    before = inventory(root), inventory(linked)
    result = subprocess.run([str(muse_python), '-I', '-B', str(KIT / 'cli/v1_muse_reader.py'),
                             str(linked), 'revision'], capture_output=True, text=True)
    assert result.returncode == 2 and 'muse_worktree_repair_required' in result.stderr
    assert (inventory(root), inventory(linked)) == before


def test_rc8_exclusion_negation_cannot_expose_secrets(native_rc8, muse_python, muse):
    root = native_rc8
    # Synthetic inert values, never credentials. Native rc8 tracks .env.example.
    (root / '.museignore').write_text('[global]\npatterns=["!*.key", "ignored/**"]\n')
    (root / '.env.example').write_text('EXAMPLE=\n')
    muse(root, 'code', 'add', '.museignore', '.env.example')
    muse(root, 'commit', '-m', 'safe template', '--json')
    (root / 'fixture.key').write_text('inert test text\n')
    (root / 'UPPER.KEY').write_text('inert test text\n')
    (root / 'ignored').mkdir()
    (root / 'ignored/file.txt').write_text('ignored\n')
    before = inventory(root)
    assert muse_read(root, str(muse_python), dirty=True)['dirty'] is False
    assert inventory(root) == before
    (root / '.env.example').write_text('EXAMPLE=changed\n')
    assert muse_read(root, str(muse_python), dirty=True)['dirty'] is True


@pytest.mark.parametrize('field', ['repo_id', 'store', 'runtime'])
def test_rc8_wrong_bound_identity_or_runtime_refuses(native_rc8, muse_python, field):
    state = muse_read(native_rc8, str(muse_python))
    binding = {k: state[k] for k in ('repo_id', 'store', 'runtime')}
    if field == 'runtime':
        binding[field] = dict(binding[field], sha256='0' * 64)
    else:
        binding[field] = 'sha256:' + '0' * 64 if field == 'repo_id' else str(native_rc8 / 'wrong')
    before = inventory(native_rc8)
    with pytest.raises(Refusal, match='muse_(repository_mismatch|runtime_changed)'):
        revision(native_rc8, {'vcs': 'muse', 'muse': binding})
    assert inventory(native_rc8) == before


@pytest.mark.parametrize('path', ['.muse/repo.json', '.muse/code/stage.json', '.museignore'])
def test_rc8_concurrent_metadata_change_refuses(native_rc8, muse_python, path):
    # Inject a second-observation race without writing from the reader process.
    result = child(muse_python, r'''
import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from cli import v1_muse_reader as reader
real=reader.read; count=0
path=sys.argv[3]
def changing(root, relative, **kwargs):
    global count
    value=real(root,relative,**kwargs)
    if relative==path:
        count+=1
        if count>1:return (value or b'')+b' '
    return value
reader.read=changing
try: reader.run(Path(sys.argv[2]),True)
except reader.Refusal as exc: print(json.dumps({'refusal':str(exc)}))
else: raise AssertionError('race accepted')
''', native_rc8, path)
    assert result['refusal'] == 'muse_revision_changed_during_read'


def test_rc8_complete_native_parent_list_and_tip_read(native_rc8, muse_python):
    result = child(muse_python, r'''
import sys,json,datetime
from pathlib import Path
from muse.core.commits import read_commit,write_commit,CommitRecord,commit_parent_ids
from muse.core.snapshot import compute_commit_id
root=Path(sys.argv[2]);initial=(root/'.muse/refs/heads/main').read_text().strip()
seed=read_commit(root,initial);created=[];when=datetime.datetime(2026,1,1,tzinfo=datetime.timezone.utc)
def make(message,parents):
    oid=compute_commit_id(parent_ids=parents,snapshot_id=seed.snapshot_id,message=message,committed_at_iso=when.isoformat(),author='Fixture')
    commit=CommitRecord(commit_id=oid,branch='main',snapshot_id=seed.snapshot_id,message=message,committed_at=when,author='Fixture',parent_commit_id=parents[0] if parents else None,parent2_commit_id=parents[1] if len(parents)>1 else None,parent_commit_ids=parents if len(parents)>2 else [])
    write_commit(root,commit);return oid
for i in range(3):created.append(make('parent '+str(i),[initial]))
merge=make('three-parent merge',created)
(root/'.muse/refs/heads/main').write_text(merge+'\n')
assert commit_parent_ids(read_commit(root,merge))==created
sys.path.insert(0,sys.argv[1]);from cli.v1_muse_reader import run
state=run(root,False)
assert state['head']==merge
print(json.dumps({'parents':created,'head':merge,'snapshot':seed.snapshot_id}))
''', native_rc8)
    assert len(set(result['parents'])) == 3
    before = inventory(native_rc8)
    assert muse_read(native_rc8, str(muse_python))['head'] == result['head']
    assert inventory(native_rc8) == before


def test_rc8_wrong_package_origin_refuses_before_object_read(native_rc8, muse_python, tmp_path):
    shadow = tmp_path / 'shadow'
    (shadow / 'muse').mkdir(parents=True)
    (shadow / 'muse/__init__.py').write_text('# inert shadow package for origin refusal\n')
    before = inventory(native_rc8)
    result = child(muse_python, r'''
import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from cli.v1_muse_reader import run,Refusal
sys.path.insert(0,sys.argv[3])
try:run(Path(sys.argv[2]),False)
except Refusal as exc:print(json.dumps({'refusal':str(exc)}))
else:raise AssertionError('shadow package accepted')
''', native_rc8, shadow)
    assert result['refusal'] == 'muse_import_origin_mismatch'
    assert inventory(native_rc8) == before
