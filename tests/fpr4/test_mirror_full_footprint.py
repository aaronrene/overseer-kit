"""Explicit native staging for the full-footprint mirror delta contract."""
import json
from pathlib import Path
import subprocess

from cli import v1_mirror as mirror
from cli.v1_policy import local_path
from cli.v1_revision import muse_read
from tests.fpr4.test_composition import composition_muse_python, native
from tests.muse.test_handoffs import init
from tests.muse.test_mirror import test_add_change_delete_and_no_content_source_commit as _exercise_delta


def test_full_footprint_mirror_delta_and_identical_native_snapshot(tmp_path, composition_muse_python):
    python = composition_muse_python

    def muse(root, *args):
        return native(python, root, *args)

    root = (tmp_path/'native-full-footprint').resolve()
    root.mkdir()
    muse(root, 'init', '--domain', 'code', '--json')
    init(root, python)
    (root/'app.py').write_text('value = 1\n')
    (root/'data.bin').write_bytes(b'\0\xff\r\n\x01')
    muse(root, 'code', 'add', '.')
    # rc5 recursive staging omits dot-directories. Include every portable hidden
    # footprint file explicitly before approving the initial source revision.
    hidden = []
    for relative in ('.claude', '.overseer/policy', '.overseer/version.lock',
                     '.overseer/STANDING-DECISIONS.reference.md'):
        path = root/relative
        for item in sorted(path.rglob('*')) if path.is_dir() else [path]:
            if item.is_file():
                name = item.relative_to(root).as_posix()
                assert not local_path(name)
                hidden.append(name)
                muse(root, 'code', 'add', name)
    assert '.claude/skills/print-next/SKILL.md' in hidden
    assert '.overseer/version.lock' in hidden
    muse(root, 'commit', '-m', 'approved complete portable footprint', '--json')
    state = muse_read(root, str(python))
    plan = {'schema': 1, 'source': {'repo_id': state['repo_id'], 'branch': 'main',
        'revision': state['head'], 'hub_url': 'https://staging.musehub.ai/fixture/source'},
        'destination': {'url': 'https://github.com/fixture/mirror.git', 'repository': 'fixture/mirror',
            'branch': 'muse-mirror', 'base': 'main', 'expected_head': 'absent'},
        'target': str((tmp_path/'bare-mirror').resolve()), 'expected_target': 'absent', 'executables': []}
    # Retain the original add/change/delete, interrupted fake delivery retry and
    # mapped-no-content-change assertions unchanged, with a complete source fixture.
    _exercise_delta((root, plan), muse)
    target = Path(plan['target'])
    first_paths = mirror.git(target, 'ls-tree', '-r', '--name-only', 'HEAD~2').decode().splitlines()
    assert set(hidden) <= set(first_paths)
    assert not any(local_path(path) for path in first_paths)
    assert mirror.git(target, 'show', 'HEAD:app.py') == b'value = 2\n'
    assert mirror.git(target, 'show', 'HEAD:new.txt') == b'addition\n'
    assert mirror.git(target, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD^', 'HEAD') == b''
    current = muse_read(root, str(python))
    probe = subprocess.run([str(python), '-I', '-B', '-c',
        'import json,sys; from pathlib import Path; from muse.core.commits import read_commit; '
        'root=Path(sys.argv[1]); current=read_commit(root,sys.argv[2]); '
        'parent=read_commit(root,current.parent_commit_id); '
        'print(json.dumps({"current":current.snapshot_id,"parent":parent.snapshot_id}))',
        str(root), current['head']], capture_output=True, text=True, timeout=20)
    assert probe.returncode == 0, probe.stderr
    snapshots = json.loads(probe.stdout)
    assert snapshots['current'] == snapshots['parent']
