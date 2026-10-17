from pathlib import Path
import subprocess,os,json,time,socket,signal,hashlib,ctypes
root=Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22/candidate');run=root/'gui-clean-exit-r2';run.mkdir();(run/'temp').mkdir();(run/'cache-home').mkdir();pilot=Path('/private/tmp/overseer-fpr5-integrated-pilot-20261015/project');kit=pilot.parent/'installation'
s=socket.socket();s.bind(('127.0.0.1',8765));s.close();args=['/usr/bin/sandbox-exec','-f',str(root.parent/'isolated-cursor.sb'),str(root/'overseer-kit-desktop-candidate'),'--kit-root',str(kit),'--repo',str(pilot)];env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin','TMPDIR':str(run/'temp')+'/', 'LANG':'en_US.UTF-8','RUST_BACKTRACE':'1','CFFIXED_USER_HOME':str(run/'cache-home')}
start=time.time()
with (run/'native-gui.log').open('w') as log:
 p=subprocess.Popen(args,cwd=pilot,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (run/'command.json').write_text(json.dumps({'argv':args,'env':env,'pid':p.pid,'candidate_binary_sha256':hashlib.sha256((root/'overseer-kit-desktop-candidate').read_bytes()).hexdigest()},indent=2)+'\n')
 time.sleep(5)
 before=subprocess.run(['/bin/ps','-g',str(p.pid),'-o','pid=,ppid=,pgid=,comm='],capture_output=True,text=True)
 ctypes.CDLL('/System/Library/Frameworks/AppKit.framework/AppKit');objc=ctypes.CDLL('/usr/lib/libobjc.A.dylib');objc.objc_getClass.argtypes=[ctypes.c_char_p];objc.objc_getClass.restype=ctypes.c_void_p;objc.sel_registerName.argtypes=[ctypes.c_char_p];objc.sel_registerName.restype=ctypes.c_void_p
 get=ctypes.CFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int32)(('objc_msgSend',objc));term=ctypes.CFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)(('objc_msgSend',objc));app=get(objc.objc_getClass(b'NSRunningApplication'),objc.sel_registerName(b'runningApplicationWithProcessIdentifier:'),p.pid);accepted=bool(app and term(app,objc.sel_registerName(b'terminate')))
 timedout=False
 try:p.wait(timeout=15)
 except subprocess.TimeoutExpired:timedout=True
 after=subprocess.run(['/bin/ps','-g',str(p.pid),'-o','pid=,ppid=,pgid=,comm='],capture_output=True,text=True)
 s=socket.socket()
 try:s.bind(('127.0.0.1',8765));port_free=True
 except OSError:port_free=False
 finally:s.close()
 result={'pid':p.pid,'normal_quit_accepted':accepted,'exit_before_fallback':p.poll(),'timed_out':timedout,'process_group_before_normal_quit':before.stdout,'process_group_after_before_fallback':after.stdout,'group_probe_exit':after.returncode,'port8765_free_before_fallback':port_free,'own_child_shutdown_proven':accepted and p.poll()==0 and after.stdout=='' and port_free,'elapsed_seconds':time.time()-start,'fallback_signals_sent':False}
 if timedout or after.stdout:
  result['fallback_signals_sent']=True
  try:os.killpg(p.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
 (run/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
