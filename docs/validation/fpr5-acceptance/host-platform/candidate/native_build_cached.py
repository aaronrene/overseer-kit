from pathlib import Path
import subprocess,os,json,time,shutil,signal,hashlib
root=Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22/candidate');old=Path('/private/tmp/overseer-fpr4-distribution-20261014-2/native-target');target=root/'cargo-target-cloned'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def inventory(base):
 return {p.relative_to(base).as_posix():{'sha256':digest(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o777} for p in sorted(base.rglob('*')) if p.is_file() and not p.is_symlink()}
before=inventory(old);assert before['debug/overseer-kit-desktop']['sha256']=='0eca7f90280274afa114ee4563db1dcf6d722c3f82f0a6d8f01b64847fb6a6c7'
(root/'old-cache-before.json').write_text(json.dumps(before,indent=2)+'\n')
r=subprocess.run(['/bin/cp','-cR',str(old),str(target)],capture_output=True,text=True);assert r.returncode==0,r.stderr
# Force every candidate application crate/build-script and copied resource to be new.
removed=[]
for p in list((target/'debug').iterdir()):
 if p.name.startswith('overseer-kit-desktop') or p.name.startswith('liboverseer_kit_desktop') or p.name=='kit':
  removed.append(str(p.relative_to(target)));shutil.rmtree(p) if p.is_dir() else p.unlink()
for sub in ['deps','build','.fingerprint','incremental']:
 for p in list((target/'debug'/sub).glob('*')):
  if 'overseer_kit_desktop' in p.name or 'overseer-kit-desktop' in p.name:
   removed.append(str(p.relative_to(target)));shutil.rmtree(p) if p.is_dir() else p.unlink()
toolchain=Path('/Users/aaronrenecarvajal/.rustup/toolchains/1.88.0-aarch64-apple-darwin/bin');cmd=[str(toolchain/'cargo'),'build','--offline','--locked','--manifest-path',str(root/'source/desktop/src-tauri/Cargo.toml'),'--target-dir',str(target)]
env=dict(os.environ);flags={'RUSTC':str(toolchain/'rustc'),'RUSTDOC':str(toolchain/'rustdoc'),'CARGO_NET_OFFLINE':'true'};env.update(flags)
for key in ['CARGO_PROFILE_DEV_DEBUG','CARGO_INCREMENTAL','CARGO_TARGET_DIR','RUSTFLAGS']:env.pop(key,None)
free_before=shutil.disk_usage(root).free;start=time.time();minimum=free_before;reason='completed'
(root/'native-build-cached-command.json').write_text(json.dumps({'argv':cmd,'environment':flags,'profile':'matching prior default dev unoptimized+debuginfo for verified dependency cache reuse','old_target':str(old),'new_cloned_target':str(target),'old_cache_entries':len(before),'clone_argv':['/bin/cp','-cR',str(old),str(target)],'removed_cloned_application_outputs':removed,'free_before_bytes':free_before,'floor_bytes':650*1024*1024},indent=2)+'\n')
with (root/'native-build-cached.log').open('w') as log:
 p=subprocess.Popen(cmd,cwd=root/'source/desktop/src-tauri',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll() is None:
  free=shutil.disk_usage(root).free;minimum=min(minimum,free)
  if free<650*1024*1024:
   reason='free_space_floor';os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   break
  time.sleep(1)
after=inventory(old);(root/'old-cache-after.json').write_text(json.dumps(after,indent=2)+'\n');assert before==after,'PROTECTED OLD CACHE CHANGED'
result={'exit':p.returncode,'reason':reason,'elapsed_seconds':time.time()-start,'minimum_free_bytes':minimum,'free_after_bytes':shutil.disk_usage(root).free,'old_cache_byte_mode_membership_unchanged':before==after}
if p.returncode==0:
 binary=target/'debug/overseer-kit-desktop';h=digest(binary);artifact=root/'overseer-kit-desktop-candidate';size=binary.stat().st_size;os.replace(binary,artifact);assert digest(artifact)==h
 result.update({'candidate_binary':str(artifact),'candidate_binary_sha256':h,'binary_size':size})
(root/'native-build-cached-result.json').write_text(json.dumps(result,indent=2)+'\n')
# The only retained executable is the rebuilt candidate artifact; reclaim our own cloned cache.
shutil.rmtree(target)
(root/'native-build-cached-cleanup.json').write_text(json.dumps({'removed_only_new_cloned_target':str(target),'free_after_bytes':shutil.disk_usage(root).free},indent=2)+'\n')
print(json.dumps(result),flush=True);print((root/'native-build-cached.log').read_text()[-4000:],flush=True)
