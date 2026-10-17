import hashlib, json, shutil
from pathlib import Path
from tools.ci import source_package as package

base=Path('/private/tmp/overseer-fpr5-review.jTlE9P/authority')
root=base/'resource-fixture'
root.mkdir()
manifest=package.manifest(package.ROOT)
for name, path in package.source_files(package.ROOT).items():
    target=root/name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path,target)
    target.chmod(int(manifest['files'][name]['mode'],8))
(root/package.MANIFEST).write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
assert package.verify_tree(root)==manifest
extra={'.overseer/config.yaml':b'repo: {root: /fake/private/repository}\n',
       'docs/NEXT.md':b'Owner-specific pending task fixture\n',
       'tools/.env':b'FAKE_TOKEN=fake_fixture_value\n'}
rows=[]
for name,body in extra.items():
    path=root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(body)
    try:
        package.verify_tree(root)
    except Exception as exc:
        outcome={'rejected':True,'reason':str(exc)}
    else:
        outcome={'rejected':False}
    rows.append({'extra':name,'archive_eligible':package.eligible(name),'manifested':name in manifest['files'],**outcome})
result={'baseline_manifested_files':len(manifest['files']),'fixture':str(root),'extra_file_results':rows,
        'source_manifest_sha256':hashlib.sha256((root/package.MANIFEST).read_bytes()).hexdigest()}
(base/'resource-membership.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
