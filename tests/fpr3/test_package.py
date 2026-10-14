"""Actual deterministic source/resource archive and validation boundaries."""
import hashlib
import io
import json
from pathlib import Path
import tarfile
import pytest
from tools.ci.source_package import build,verify,unpack,eligible,MANIFEST
from tests.v1.conftest import KIT


def test_actual_package_deterministic_manifest_modes_and_resource_bundle(tmp_path):
    a,b=tmp_path/'a.tar.gz',tmp_path/'b.tar.gz'
    first=build(KIT,a);second=build(KIT,b)
    assert first['sha256']==second['sha256']
    m=verify(a); names=set(m['files'])
    assert {'cli/ok','cli/product_service.py','tools/app/engine.py','desktop/src-tauri/src/launcher.rs',
            'tools/ci/muse-rc5-artifact.json','policy/model-routing.yaml','cursor/skills/print-next/SKILL.md'}<=names
    assert m['files']['cli/ok']['mode']=='0755' and m['release_ready'] is False
    assert not any(n.startswith(('.overseer/','.cursor/','.claude/','.git/','.muse/','.venv/')) or n=='docs/NEXT.md' for n in names)
    destination=tmp_path/'resources/kit';unpack(a,destination)
    assert (destination/'cli/ok').stat().st_mode&0o111
    assert not (destination/'.venv').exists()
    third=build(destination,tmp_path/'repacked.tar.gz');assert first['sha256']==third['sha256']
    with pytest.raises(ValueError):unpack(a,destination)
    with pytest.raises(ValueError):build(KIT,a)


def test_package_traversal_and_tamper_refused(tmp_path):
    for path in ('../escape','/etc/passwd','docs/NEXT.md','.muse/key','cli/__pycache__/x.pyc','desktop/resources/kit/cli/ok','tools/private.key',''):
        assert not eligible(path)
    a=tmp_path/'malicious.tar.gz'
    with tarfile.open(a,'w:gz') as tar:
        for path,body in [(MANIFEST,b'{"schema":1,"files":{}}'),('../escape',b'bad')]:
            info=tarfile.TarInfo(path);info.size=len(body);info.mode=0o644;tar.addfile(info,io.BytesIO(body))
    with pytest.raises(ValueError):verify(a)


def test_landing_and_active_handoff_copy():
    from tools.landing.validate import validate_landing
    result=validate_landing(KIT);assert result.ok,result.errors
    for relative in ('templates/OVERSEER-HANDOVER.template.md','templates/ROADMAP.template.md','cursor/skills/governance-sync/SKILL.md'):
        text=(KIT/relative).read_text();assert 'docs/NEXT.md' in text or 'canonical' in text
        assert 'NEXT SESSION' not in text and 'git-export --git-dir .' not in text
