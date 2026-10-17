from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, time

BASE=Path(__file__).resolve().parent
KIT=BASE/'installation'
ROOT=BASE/'project'
EVIDENCE=BASE/'evidence'
RUNTIME='cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774'
ENV={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','GIT_','MUSE_','FPR2_MUSE')) and k!='VIRTUAL_ENV'}
ENV.update(PATH='/usr/bin:/bin',PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_NOSYSTEM='1',GIT_OPTIONAL_LOCKS='0')

def digest(data): return hashlib.sha256(data).hexdigest()

class Recorder:
    def __init__(self,stage):
        self.stage=stage;self.rows=[];self.path=EVIDENCE/(stage+'.json')
        assert not self.path.exists(), self.path
        driver=Path(sys.argv[0]).resolve()
        self.rows.append({'kind':'driver_invocation','argv':[sys.executable,*sys.argv],'cwd':str(Path.cwd()),'driver_sha256':digest(driver.read_bytes()),'helper_sha256':digest(Path(__file__).read_bytes())})
        self.save()
    def save(self):
        self.path.write_text(json.dumps({'stage':self.stage,'scope':'Author acceptance; not independent adjudication','commands_and_operations':self.rows},indent=2)+'\n')
    def note(self,kind,**fields):
        self.rows.append({'kind':kind,**fields});self.save()
    def run(self,argv,*,cwd=ROOT,input=None,expected=0,timeout=90):
        assert shutil.disk_usage(BASE).free>=250*1024*1024,'Stop: less than 250MiB free'
        argv=list(map(str,argv));start=time.time()
        p=subprocess.run(argv,cwd=cwd,env=ENV,input=input,capture_output=True,text=True,timeout=timeout)
        self.note('command',argv=argv,cwd=str(cwd),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,seconds=time.time()-start)
        if expected is not None: assert p.returncode in (expected if isinstance(expected,tuple) else (expected,)),p.stdout+p.stderr
        return p
    def git(self,*args,**kw): return self.run(['/usr/bin/git','-c','core.hooksPath=/dev/null','-C',ROOT,*args],**kw)
    def ok(self,*args,**kw): return self.run([ROOT/'.overseer/bin/ok','-C',ROOT,*args],**kw)
    def write(self,relative,body,mode=0o644):
        assert shutil.disk_usage(BASE).free>=250*1024*1024,'Stop: less than 250MiB free'
        path=ROOT/relative;path.parent.mkdir(parents=True,exist_ok=True)
        raw=body.encode() if isinstance(body,str) else body
        path.write_bytes(raw);path.chmod(mode)
        self.note('local_project_write',path=str(path),sha256=digest(raw),bytes=len(raw),mode=oct(mode))
    def state(self): return json.loads(self.ok('status','--json').stdout)
    def publish(self,action,prompt,kind='implement'):
        raw=self.ok('status','--json',expected=None)
        state=json.loads(raw.stdout)
        assert state['runtime']['sha256']==RUNTIME
        assert state['repository']['root']==str(ROOT)
        if raw.returncode:
            assert state.get('next_error') and 'error' not in state,state
        req={'lanes':{lane:{'model':'GPT-6 Astra','action_id':action+'-'+lane,'action_kind':kind,'prompt':prompt+'\nSelected work stream is '+lane+'.\n'} for lane in ('product','validation')}}
        relative='.overseer/local/'+action+'-batch.json';self.write(relative,json.dumps(req,indent=2)+'\n')
        next_path=ROOT/'docs/NEXT.md'; prior=digest(next_path.read_bytes()) if next_path.exists() else 'absent'
        result=self.ok('next-write','--repo-id',state['repository']['id'],'--branch',state['branch'],'--expect-next',prior,'--batch-file',relative,'--json')
        return json.loads(result.stdout)
    def snapshot(self,paths):
        out={}
        for relative in paths:
            p=ROOT/relative;out[relative]={'sha256':digest(p.read_bytes()),'mode':oct(p.stat().st_mode&0o777),'mtime_ns':p.stat().st_mtime_ns,'bytes':p.stat().st_size}
        return out
