"""Restored product commands on the pinned native authority, without Git."""
import json
from tests.muse.test_handoffs import init,commit,publish
from tests.v1.conftest import command


def test_native_product_status_review_hygiene_and_local_commit(muse_root,muse_python,muse):
    root=muse_root
    state=init(root,muse_python)
    assert state['governance']['authority']=='muse'
    commit(root,muse)
    muse(root,'branch','feat/surfaces')
    muse(root,'checkout','feat/surfaces')
    assert publish(root).returncode==0
    p=command('-C',root,'status','--check-footprint','--json');assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['governance']['local_main']
    next_bytes=(root/'docs/NEXT.md').read_bytes()
    p=command('-C',root,'governance-sync','--write','--json');assert p.returncode==0,p.stderr+p.stdout
    assert json.loads(p.stdout)['committed']
    assert (root/'docs/NEXT.md').read_bytes()==next_bytes
    assert command('-C',root,'next').returncode==2
    assert publish(root).returncode==0
    p=command('-C',root,'land-closeout','--json');assert p.returncode==0,p.stderr
    p=command('-C',root,'check-ok','--path','docs/check.md','--scaffold-only');assert p.returncode==0,p.stderr
    p=command('-C',root,'review','--freeze','docs/check.md','--dry-run');assert p.returncode==0,p.stderr
    assert not (root/'.git').exists()
