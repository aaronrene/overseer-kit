"""Create a NEW, bounded owner-observation session; never reuse raw evidence paths."""
from pathlib import Path
import argparse,ctypes,hashlib,json,os,signal,subprocess,tempfile,time
BASE=Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22')
PILOT=Path('/private/tmp/overseer-fpr5-integrated-pilot-20261015/project')
KIT=PILOT.parent/'installation'
BINARY=BASE/'candidate/overseer-kit-desktop-candidate'
BINARY_SHA='a515148a94ffebb88e7520fb194bc0287967484896c44900e6d7ab4e7b364551'
NEXT_SHA='489ded7be7f530ea242e1ed5dbdce96037ec752cc63c9359eaa778aa483ba055'
RUNTIME_SHA='cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774'
PROFILE_SHA='ba54a8e1217b4d9d5db7c11115bcc4515f501a10d83c945d474680147dc34eff'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normal_quit(pid):
 ctypes.CDLL('/System/Library/Frameworks/AppKit.framework/AppKit');objc=ctypes.CDLL('/usr/lib/libobjc.A.dylib');objc.objc_getClass.argtypes=[ctypes.c_char_p];objc.objc_getClass.restype=ctypes.c_void_p;objc.sel_registerName.argtypes=[ctypes.c_char_p];objc.sel_registerName.restype=ctypes.c_void_p
 get=ctypes.CFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int32)(('objc_msgSend',objc));term=ctypes.CFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)(('objc_msgSend',objc));app=get(objc.objc_getClass(b'NSRunningApplication'),objc.sel_registerName(b'runningApplicationWithProcessIdentifier:'),pid);return bool(app and term(app,objc.sel_registerName(b'terminate')))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--surface',choices=['desktop','cursor'],required=True);args=ap.parse_args()
 assert sha(PILOT/'docs/NEXT.md')==NEXT_SHA,'Pilot NEXT changed; stop for context revalidation'
 status=subprocess.run([str(PILOT/'.overseer/bin/ok'),'-C',str(PILOT),'status','--json'],capture_output=True,text=True);binding=json.loads(status.stdout)
 assert binding['runtime']['sha256']==RUNTIME_SHA and binding['runtime']['root']==str(KIT)
 assert binding['repository']['id']=='20dd0872-c7a4-5fdf-81a5-27eefa0acc2e'
 run=Path(tempfile.mkdtemp(prefix='c-' if args.surface=='cursor' else 'd-',dir=BASE));(run/'temp').mkdir();(run/'cache-home').mkdir()
 profile=BASE/'isolated-cursor.sb';assert sha(profile)==PROFILE_SHA,'Isolation profile changed; refuse';text=profile.read_text();assert '(deny network*)' in text and '(deny file-read* (subpath "/Users/aaronrenecarvajal"))' in text
 env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin','TMPDIR':str(run/'temp')+'/', 'LANG':'en_US.UTF-8'}
 if args.surface=='desktop':
  assert sha(BINARY)==BINARY_SHA,'Candidate binary changed; stop for revalidation'
  env['CFFIXED_USER_HOME']=str(run/'cache-home');command=[str(BINARY),'--kit-root',str(KIT),'--repo',str(PILOT)]
 else:
  user=run/'profile';(user/'User').mkdir(parents=True);extensions=run/'extensions';extensions.mkdir()
  (user/'User/settings.json').write_text(json.dumps({'telemetry.telemetryLevel':'off','update.mode':'none','extensions.autoCheckUpdates':False,'extensions.autoUpdate':False,'security.workspace.trust.enabled':True,'workbench.startupEditor':'none','window.restoreWindows':'none','git.enabled':False,'git.autofetch':False})+'\n')
  command=['/Applications/Cursor.app/Contents/MacOS/Cursor','--user-data-dir',str(user),'--extensions-dir',str(extensions),'--new-window','--no-sandbox','--disable-gpu','--disable-extensions','--disable-updates','--disable-telemetry','--disable-crash-reporter','--skip-welcome','--skip-release-notes','--password-store=basic','--log','trace',str(PILOT)]
 command=['/usr/bin/sandbox-exec','-f',str(profile)]+command
 with (run/'host.log').open('w') as log:
  p=subprocess.Popen(command,cwd=PILOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  (run/'launch.json').write_text(json.dumps({'surface':args.surface,'argv':command,'env':env,'pid':p.pid,'limit_seconds':600,'next_sha256':NEXT_SHA,'runtime_sha256':RUNTIME_SHA},indent=2)+'\n');print('NEW evidence directory:',run,flush=True);print('Only inspect this disposable window. Do not sign in, submit a model prompt or enable network. Close it normally when done; maximum600 seconds.',flush=True)
  normal=False;fallback=False
  try:
   for _ in range(600):
    if p.poll() is not None:break
    time.sleep(1)
  except KeyboardInterrupt:pass
  finally:
   if p.poll() is None:
    normal=normal_quit(p.pid)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:
     fallback=True;os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=5)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   # Remove no files and act only on this new process group if helpers survived.
   group=subprocess.run(['/bin/ps','-g',str(p.pid),'-o','pid=,pgid=,comm='],capture_output=True,text=True)
   if group.stdout:
    fallback=True
    try:os.killpg(p.pid,signal.SIGTERM)
    except ProcessLookupError:pass
   (run/'result.json').write_text(json.dumps({'exit':p.returncode,'normal_quit_requested':normal,'fallback_signal':fallback,'remaining_group_before_fallback':group.stdout,'next_unchanged':sha(PILOT/'docs/NEXT.md')==NEXT_SHA,'acceptance_verdict':'not_automatically_adjudicated'},indent=2)+'\n')
  print('Observation ended; evidence:',run,flush=True)
if __name__=='__main__':main()
