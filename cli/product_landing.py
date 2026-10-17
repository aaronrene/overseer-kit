"""Landing checks use selected authority and canonical NEXT, never HANDOVER fences."""
from argparse import Namespace
import json
import os
from pathlib import Path
import subprocess
import sys
from cli import v1
from cli.v1_io import Refusal, read


def native_query(b, paths=()):
    from cli.v1_revision import bounded_run, unique_json
    c = b.context.config
    python = c['vcs']['muse']['binding']['runtime']['python']
    env = {k: v for k,v in os.environ.items() if not k.startswith(('GIT_', 'MUSE_', 'PYTHON')) and k != 'VIRTUAL_ENV'}
    env.update(PATH='/usr/bin:/bin', PYTHONDONTWRITEBYTECODE='1')
    result = bounded_run([python,'-I','-B',str(v1.KIT/'cli/product_native_read.py'),str(b.context.root),
                          c['vcs']['muse']['main_branch'],json.dumps(list(paths))], cwd=b.context.root,env=env)
    if result.returncode:
        raise Refusal('native_main_read_failed')
    value = json.loads(result.stdout, object_pairs_hook=unique_json)
    binding = c['vcs']['muse']['binding']
    if (value['state']['repo_id'] != binding['repo_id'] or value['state']['store'] != binding['store']
            or value['state']['runtime'] != binding['runtime']):
        raise Refusal('native_query_binding_mismatch')
    b.recheck()
    return value


def run(b):
    from cli.product_next import display
    args, c, root = b.args, b.model.adapter, b.context.root
    ritual = c.close_ritual
    mode = getattr(args, 'mode', None) or ritual.mode
    result = {'ok': True, 'exit_code': 0, 'mode': mode, 'auto_merge': False,
              'remote': 'not_checked_offline', 'landed': False, 'paths': []}
    try:
        fields, _ = display(root,b.context.config,read(root,v1.NEXT),Namespace(lane=getattr(args,'lane',None)),b.context.observed)
        result['next'] = fields
    except Refusal as exc:
        result.update(ok=False,exit_code=2,next_error=str(exc))
    if args.command == 'land-closeout':
        result['state'] = 'current_handoff' if result['ok'] else 'handoff_requires_explicit_refresh'
        from cli.product_governance import observation
        result['local_governance'] = observation(b)
        result['merge_completion'] = 'not_inferred_from_documents'
        if args.probe_merged_pr:
            from cli.product_service import gh_run
            response=gh_run(b,['gh','pr','list','--state','merged','--limit','5','--json','number,mergeCommit,mergedAt'])
            if response.returncode:
                raise Refusal('merged_pr_probe_failed')
            result.update(remote='observed',merged_prs=json.loads(response.stdout))
        return result
    if not ritual.enabled:
        result.update(state='disabled',landed=False)
        return result
    if ritual.consumer_verify_script:
        path=b.watch(ritual.consumer_verify_script)
        b.recheck()
        response=subprocess.run([sys.executable,str(path)],cwd=root,capture_output=True,text=True,timeout=300)
        b.recheck()
        result.update(consumer_exit=response.returncode,landed=response.returncode==0 and result['ok'])
        if response.returncode:
            result.update(ok=False,exit_code=response.returncode)
        return result
    if not ritual.require_paths:
        raise Refusal('land_check_requires_paths_or_consumer_script')
    for relative in ritual.require_paths:
        b.watch(relative)
    if b.context.observed['vcs']=='muse':
        value=native_query(b,ritual.require_paths)
        ref=value['revision'];rows=value['paths']
        dirty=v1.revision(root,b.context.config,dirty=True).dirty
    else:
        # Retain the original path-comparison engine with an explicit Git root.
        from tools.close_ritual.land_check import compare_paths_to_main
        ref,rows,dirty=compare_paths_to_main(root,ritual.require_paths,remote=c.vcs.git.remote,main_branch=c.vcs.git.main_branch)
    passed=not dirty and (mode=='prepare_pr' or all(row['match'] for row in rows))
    result.update(ref=ref,paths=rows,dirty_paths=dirty,landed=passed and result['ok'] and mode=='verify_landed')
    if not passed:
        result.update(ok=False,exit_code=1)
    return result
