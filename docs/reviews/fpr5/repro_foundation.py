"""Independent FPR-5 CLI probes. Only creates fixtures below the given output root."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import yaml

KIT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert OUT.is_relative_to(Path('/private/tmp'))
records = []

def cli(root, *args):
    argv = [str(KIT / 'cli/ok'), '-C', str(root), *args]
    proc = subprocess.run(argv, text=True, capture_output=True, timeout=40)
    records.append(dict(argv=argv, exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
    return proc

def seed(name):
    root = Path(tempfile.mkdtemp(prefix=name+'-', dir=OUT))
    for args in [('init','-b','main'), ('config','user.name','FPR5 fixture'),
                 ('config','user.email','fpr5@example.invalid'),
                 ('-c','core.hooksPath=/dev/null','commit','--allow-empty','-m','seed')]:
        subprocess.run(['/usr/bin/git','-C',str(root),*args],check=True,capture_output=True)
    return root

results = {}
root = seed('multilane-init')
assert cli(root, 'init').returncode == 0
assert cli(root, 'init', '--dry-run').returncode == 0
cfgpath = root / '.overseer/config.yaml'
cfg = yaml.safe_load(cfgpath.read_bytes())
cfg['docs']['lanes']['architecture'] = dict(repo_id=cfg['repo']['id'], roadmap='ARCH-ROADMAP.md', handover='ARCH-HANDOVER.md')
cfgpath.write_text(yaml.safe_dump(cfg))
assert cli(root,'next','--lane','product').returncode == 0
before = (root/'docs/NEXT.md').read_bytes()
for args in [('init','--dry-run'), ('init','--dry-run','--lane','product')]:
    p = cli(root,*args)
    results[' '.join(args)] = dict(exit_code=p.returncode,stderr=p.stderr,next_unchanged=before==(root/'docs/NEXT.md').read_bytes())

root = seed('migration-owner-asset')
(root/'.overseer').mkdir()
(root/'.overseer/config.yaml').write_bytes((KIT/'tests/fixtures/config-two-lane.yaml').read_bytes())
asset = root/'.cursor/rules/build-verification-required.mdc'
asset.parent.mkdir(parents=True)
owner_bytes=b'---\nalwaysApply: true\n---\nOwner requires the custom offline safety verification before any local commit.\n'
asset.write_bytes(owner_bytes)
p=cli(root,'init','--migrate','--dry-run','--json')
assert p.returncode==0, p.stderr
plan=json.loads(p.stdout)
(root/'plan.json').write_text(p.stdout)
relative=asset.relative_to(root).as_posix()
row=next(r for r in plan['plan']['classification'] if r['path']==relative)
p=cli(root,'init','--migrate','--apply-plan','plan.json','--expect-plan',plan['plan_sha256'],'--expect-config',plan['plan']['source_config_sha256'],'--json')
results['migration_owner_asset'] = dict(path=relative, classification=row, apply_exit=p.returncode,
    owner_content_preserved=asset.read_bytes()==owner_bytes,
    backup_contains_owner_bytes=(root/json.loads(p.stdout)['backup']/'files'/relative).read_bytes()==owner_bytes if p.returncode==0 else None,
    stderr=p.stderr)

(OUT/'foundation-transcript.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'foundation-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
