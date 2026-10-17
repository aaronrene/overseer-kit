"""Native linked checkout identity with the restored tracked footprint contract."""
import stat

import yaml

from cli import v1
from cli.v1_policy import local_path
from tests.fpr4.test_composition import composition_muse_python, native
from tests.muse.test_handoffs import init, commit, publish, inventory
from tests.v1.conftest import command, status


def portable_inventory(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode))
        for p in root.rglob('*') if p.is_file() and not p.is_symlink()
        and '.muse' not in p.relative_to(root).parts and not local_path(p.relative_to(root).as_posix())}


def test_native_linked_checkout_reports_tracked_footprint_change_and_keeps_identity(tmp_path, composition_muse_python):
    python = composition_muse_python

    def muse(root, *args):
        return native(python, root, *args)

    root = (tmp_path/'native-primary').resolve()
    root.mkdir()
    muse(root, 'init', '--domain', 'code', '--json')
    init(root, python)
    commit(root, muse)
    assert publish(root).returncode == 0
    linked = (tmp_path/'native-linked').resolve()
    muse(root, 'worktree', 'add', 'native-linked', 'main', '-b', 'lane-two', '--path', str(linked), '--json')
    original = inventory(root)
    inherited = portable_inventory(linked)
    primary = status(root)
    other = init(linked, python, '--lane', 'architecture')
    assert other['branch'] == 'lane-two'
    assert other['source_id'] == primary['source_id']
    assert other['head'] == primary['head']
    assert other['repository']['id'] != primary['repository']['id']
    assert other['repository']['root'] == str(linked)

    after = portable_inventory(linked)
    changed = {path for path in inherited.keys() | after.keys() if inherited.get(path) != after.get(path)}
    assert changed == {'.overseer/version.lock'}
    before_lock = yaml.safe_load(inherited['.overseer/version.lock'][0])
    after_lock = yaml.safe_load(after['.overseer/version.lock'][0])
    before_rows = {entry['path']: entry for entry in before_lock['footprint']}
    after_rows = {entry['path']: entry for entry in after_lock['footprint']}
    assert before_rows.keys() == after_rows.keys()
    assert before_rows['.overseer/bin/ok']['sha256'] != after_rows['.overseer/bin/ok']['sha256']
    assert after_rows['.overseer/bin/ok']['origin'] == 'kit'
    for path, entry in after_rows.items():
        if path == '.overseer/bin/ok' or entry == before_rows[path]:
            continue
        assert entry['origin'] == 'preserved'
        assert entry['sha256'] == before_rows[path]['sha256']
    # The new root-bound launcher has a different footprint digest, and inherited
    # portable assets are explicitly preserved. The tracked lock change is real
    # local work; it must remain dirty until accepted and committed by the owner.
    assert other['dirty'] is True
    assert publish(linked).returncode == 0
    result = command('next', cwd=linked, executable=linked/'.overseer/bin/ok')
    assert result.returncode == 0, result.stderr
    assert inventory(root) == original
    commit(root, muse, 'primary advanced')
    assert command('-C', linked, 'next').returncode == 0
    assert command('-C', root, 'next').returncode == 2
    assert status(linked)['dirty'] is True
