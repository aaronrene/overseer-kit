from pathlib import Path
import subprocess,os,json,time,shutil,signal
root=Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22')
toolchain=Path('/Users/aaronrenecarvajal/.rustup/toolchains/1.88.0-aarch64-apple-darwin/bin')
cmd=[str(toolchain/'cargo'),'build','--offline','--locked','--manifest-path',str(root/'source/desktop/src-tauri/Cargo.toml'),'--target-dir',str(root/'cargo-target-reduced')]
env=dict(os.environ);flags={'RUSTC':str(toolchain/'rustc'),'RUSTDOC':str(toolchain/'rustdoc'),'CARGO_NET_OFFLINE':'true','CARGO_PROFILE_DEV_DEBUG':'0','CARGO_INCREMENTAL':'0'};env.update(flags)
start=time.time();free_before=shutil.disk_usage(root).free
(root/'native-build-reduced-command.json').write_text(json.dumps({'argv':cmd,'environment':flags,'cwd':str(root/'source/desktop/src-tauri'),'start':start,'minimum_free_bytes':650*1024*1024,'free_before_bytes':free_before},indent=2)+'\n')
minimum=free_before;reason='completed'
with (root/'native-build-reduced.log').open('w') as log:
 p=subprocess.Popen(cmd,cwd=root/'source/desktop/src-tauri',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll() is None:
  free=shutil.disk_usage(root).free;minimum=min(minimum,free)
  if free<650*1024*1024:
   reason='free_space_floor';os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   break
  time.sleep(1)
result={'exit':p.returncode,'reason':reason,'elapsed_seconds':time.time()-start,'minimum_free_bytes':minimum,'free_after_bytes':shutil.disk_usage(root).free}
(root/'native-build-reduced-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True);print((root/'native-build-reduced.log').read_text()[-3000:],flush=True)
