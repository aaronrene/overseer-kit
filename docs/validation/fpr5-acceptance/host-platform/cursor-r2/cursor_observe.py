from pathlib import Path
import os,subprocess,json,time,socket,shutil,signal
root=Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22/cursor-r2')
pilot=Path('/private/tmp/overseer-fpr5-integrated-pilot-20261015/project')
(root/'cursor-temp').mkdir(exist_ok=True)
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
args=['/usr/bin/sandbox-exec','-f',str(root.parent/'isolated-cursor.sb'),'/Applications/Cursor.app/Contents/MacOS/Cursor','--user-data-dir',str(root/'cursor-profile'),'--extensions-dir',str(root/'cursor-extensions'),'--new-window','--no-sandbox','--disable-gpu','--disable-extensions','--disable-updates','--disable-telemetry','--disable-crash-reporter','--skip-welcome','--skip-release-notes','--password-store=basic','--log','trace','--remote-debugging-address=127.0.0.1','--remote-debugging-port='+str(port),str(pilot)]
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin','TMPDIR':str(root/'cursor-temp')+'/', 'LANG':'en_US.UTF-8','ELECTRON_ENABLE_LOGGING':'1'}
start=time.time(); before=subprocess.run([str(pilot/'.overseer/bin/ok'),'-C',str(pilot),'next'],capture_output=True,text=True)
(root/'cursor-next-before.txt').write_text(before.stdout+before.stderr)
with (root/'cursor-host.log').open('w') as log:
 p=subprocess.Popen(args,cwd=pilot,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (root/'cursor-launch.json').write_text(json.dumps({'argv':args,'environment':env,'pid':p.pid,'port':port,'started_at':start,'next_before_exit':before.returncode},indent=2)+'\n')
 print(json.dumps({'pid':p.pid,'port':port,'evidence':str(root)}),flush=True)
 reason='time_budget'
 for i in range(180):
  if p.poll() is not None:reason='host_exited';break
  if (root/'stop-cursor').exists():reason='observation_complete';break
  if shutil.disk_usage(root).free<400000000:reason='disk_free_floor';break
  time.sleep(1)
 if p.poll() is None:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
 (root/'cursor-result.json').write_text(json.dumps({'exit':p.returncode,'stop_reason':reason,'elapsed_seconds':time.time()-start,'free_bytes':shutil.disk_usage(root).free,'native_lifecycle_pass':False},indent=2)+'\n')
 print('Cursor observation stopped: '+reason+' exit '+str(p.returncode),flush=True)
