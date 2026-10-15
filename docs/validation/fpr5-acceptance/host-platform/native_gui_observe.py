from pathlib import Path
import subprocess,os,json,time,socket,signal,hashlib
root=Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22');pilot=Path('/private/tmp/overseer-fpr5-integrated-pilot-20261015/project');kit=pilot.parent/'installation'
(root/'native-temp').mkdir(exist_ok=True)
s=socket.socket();s.bind(('127.0.0.1',8765));s.close()
args=['/usr/bin/sandbox-exec','-f',str(root/'isolated-cursor.sb'),str(root/'overseer-kit-desktop-fresh'),'--kit-root',str(kit),'--repo',str(pilot)]
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin','TMPDIR':str(root/'native-temp')+'/', 'LANG':'en_US.UTF-8','RUST_BACKTRACE':'1'}
nextpath=pilot/'docs/NEXT.md';before=hashlib.sha256(nextpath.read_bytes()).hexdigest();head=subprocess.run(['/usr/bin/git','-C',str(pilot),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
start=time.time()
with (root/'native-gui.log').open('w') as log:
 p=subprocess.Popen(args,cwd=pilot,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (root/'native-gui-command.json').write_text(json.dumps({'argv':args,'env':env,'pid':p.pid,'pilot_head':head,'pilot_next_sha256':before,'timeout_seconds':40,'port8765_available_before_launch':True,'binary_sha256':hashlib.sha256((root/'overseer-kit-desktop-fresh').read_bytes()).hexdigest()},indent=2)+'\n')
 print('native pid '+str(p.pid),flush=True)
 try:p.wait(timeout=40);reason='process_exited'
 except subprocess.TimeoutExpired:
  reason='bounded_timeout';os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
 # Clean up only any surviving child in this exact newly-created process group.
 try:os.killpg(p.pid,signal.SIGTERM)
 except ProcessLookupError:pass
result={'exit':p.returncode,'reason':reason,'elapsed_seconds':time.time()-start,'pilot_next_sha256_after':hashlib.sha256(nextpath.read_bytes()).hexdigest(),'pilot_next_unchanged':before==hashlib.sha256(nextpath.read_bytes()).hexdigest(),'native_gui_acceptance_pass':False}
(root/'native-gui-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);print((root/'native-gui.log').read_text()[-12000:],flush=True)
