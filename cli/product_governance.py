"""Bound hygiene: retained drift/queue algorithms, canonical NEXT untouched.

The former orchestration coupled prompt generation, branch switching and push.
This service records local observations, applies paired summaries, and commits
only their exact paths. Remote enrichment and transport are separate requests.
"""
from argparse import Namespace
from dataclasses import asdict
import os
from pathlib import Path
import re
import subprocess

from cli import v1
from cli.v1_io import digest, Refusal
from cli.product_boundary import read


def observation(b, *, lane=None, merged=None):
    from tools.governance_hygiene.parse import parse_handover_github_main_sha
    root, config, observed = b.context.root, b.context.config, b.context.observed
    lane = lane or config['context']['lane']
    if lane not in config['docs']['lanes']:
        raise Refusal('unknown_lane')
    docs = config['docs']['lanes'][lane]
    relative = str(Path(config['repo']['root_relative_docs']) / docs['handover'])
    data = read(root, relative, missing=True)
    main = None
    if observed['vcs'] == 'git':
        main = v1.git(root, 'rev-parse', '--verify', config['vcs']['git']['main_branch'] + '^{commit}', optional=True) or None
    else:
        from cli.product_landing import native_query
        main = native_query(b)['revision']
    claim = parse_handover_github_main_sha(data.decode()) if data else None
    cached = None
    if observed['vcs'] == 'git':
        ref = 'refs/remotes/' + config['vcs']['git']['remote'] + '/' + config['vcs']['git']['main_branch']
        cached = v1.git(root, 'rev-parse', '--verify', ref + '^{commit}', optional=True) or None
    from tools.governance_hygiene.types import VerifiedReads
    from tools.governance_hygiene.drift import detect_drift
    roadmap = read(root, str(Path(config['repo']['root_relative_docs']) / docs['roadmap']), missing=True)
    drift = asdict(detect_drift(VerifiedReads(config['vcs']['regime'], cached, 'cached local ref only',
        main or '', 'selected authority main', main, 'local main read', merged or (),
        observed['branch'], False, config['vcs']['regime']),
        data.decode() if data else '', roadmap.decode() if roadmap else ''))
    if merged is None:
        drift['d3_queue_vs_merged'] = 'unknown_offline'
    if observed['vcs'] == 'muse':
        # Cross-authority correspondence is verified by controlled mirror history,
        # never by comparing unrelated Git and Muse commit identifiers.
        drift['d1_handover_vs_git'] = 'requires_controlled_mirror_verify'
        drift['d2_anchor_vs_canonical'] = 'native_main_observed'
    return {'lane': lane, 'authority': observed['vcs'], 'branch': observed['branch'],
            'revision': observed['head'], 'local_main': main,
            'remote': 'not_checked_offline', 'claimed_github_main': claim,
            'remote_drift': 'unknown_offline', 'cached_remote_main': cached, 'drift': drift,
            'realignment': 'controlled_mirror_reconcile' if observed['vcs'] == 'muse' else 'not_applicable',
            'canonical_next': v1.NEXT}


def _refresh_after_commit(b, prior):
    from cli.main import ValidatedContext
    new = ValidatedContext.capture(b.context.root, b.args)
    if new.original != b.context.original or new.observed['branch'] != prior['branch']:
        raise Refusal('governance_commit_context_changed')
    if prior['vcs'] == 'git':
        parents = v1.git(new.root, 'rev-list', '--parents', '-n', '1', new.observed['head']).split()
        if parents[1:] != [prior['head']]:
            raise Refusal('governance_commit_parent_changed')
    b.context = new


def _local_command(b, *argv):
    b.recheck()
    if b.context.observed['vcs'] == 'git':
        return v1.git(b.context.root, *argv)
    python = Path(b.context.config['vcs']['muse']['binding']['runtime']['python'])
    env = {k: v for k, v in os.environ.items() if not k.startswith(('MUSE_', 'GIT_', 'PYTHON'))}
    result = subprocess.run([str(python), '-I', '-B', '-c',
                            'from muse.cli.app import main; raise SystemExit(main())',
                            '-C', str(b.context.root), *(['code', *argv] if argv[0] == 'add' else [argv[0], '--no-verify', *argv[1:]])],
                            env=env, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise Refusal('native_local_mutation_failed: ' + argv[0])
    return result.stdout


def run(b):
    args, root, config = b.args, b.context.root, b.context.config
    if args.push and config['vcs']['canonical'] != 'git':
        raise Refusal('muse_transport_requires_explicit_mirror_deliver')
    if args.print_next:
        from cli.product_next import display
        fields, rendered = display(root, config, read(root, v1.NEXT), args, b.context.observed)
        return dict(fields, ok=True, rendered=rendered)
    lanes = list(config['docs']['lanes']) if args.all_lanes else [args.lane or config['context']['lane']]
    observations, changes = [], {}
    merged = None
    if args.gh:
        from cli.product_service import BoundRunner
        from tools.governance_hygiene.reads import fetch_merged_prs, ReadFailure
        merged = fetch_merged_prs(BoundRunner(b))
        if isinstance(merged, ReadFailure):
            raise Refusal('governance_remote_read_failed')
    from tools.governance_hygiene.anchors import replace_anchor_block
    from tools.governance_hygiene.patch import _patch_queue_rows, _render_done_recently
    from tools.governance_hygiene.drift import merged_prs_missing_from_done
    for lane in lanes:
        observed = observation(b, lane=lane, merged=merged)
        observations.append(observed)
        docs = config['docs']['lanes'][lane]
        # Revision is deliberately omitted from the authored block: committing
        # a self-referential HEAD makes every subsequent hygiene run dirty.
        body = ('## Repository governance\n\n'
                f"Repository: {config['repo']['name']}; lane: {lane}; authority: {observed['authority']}.\n\n"
                'Read the current revision and drift with `ok status`. '
                'Remote freshness requires an explicit remote read.\n\n'
                'Current action: `ok next` validates canonical `docs/NEXT.md`.\n')
        for field in ('handover', 'roadmap'):
            relative = str(Path(config['repo']['root_relative_docs']) / docs[field])
            b.watch(relative)
            prior = read(root, relative).decode()
            after = replace_anchor_block(prior, 'product-governance', body)
            if merged is not None:
                if field == 'roadmap':
                    after = _patch_queue_rows(after, merged)
                else:
                    missing = merged_prs_missing_from_done(after, merged)
                    if missing:
                        after = replace_anchor_block(after, 'done-recently', _render_done_recently(after, missing))
            if after != prior:
                changes[relative] = after.encode()
    result = {'ok': True, 'dry_run': not args.write, 'observations': observations,
              'changed': list(changes), 'committed': False, 'pushed': False,
              'next': 'preserved; republish explicitly after a work commit',
              'remote': 'enriched' if merged is not None else 'not_checked_offline'}
    if not args.write:
        return result
    branch = b.context.observed['branch']
    if branch in {config['vcs']['git']['main_branch'], config['vcs']['muse']['main_branch']}:
        raise Refusal('governance_write_requires_selected_feature_branch')
    if v1.revision(root, config, dirty=True).dirty:
        raise Refusal('governance_write_requires_clean_worktree')
    original_next = read(root, v1.NEXT, missing=True)
    if changes:
        for path, data in changes.items():
            b.write(path, data)
        prior = b.context.observed
        _local_command(b, 'add', '--', *changes)
        _local_command(b, 'commit', '-m', 'docs: synchronize repository governance')
        _refresh_after_commit(b, prior)
        result.update(committed=True, commit_sha=b.context.observed['head'])
    if read(root, v1.NEXT, missing=True) != original_next:
        raise Refusal('governance_next_changed')
    if args.push:
        if config['vcs']['canonical'] != 'git':
            raise Refusal('muse_transport_requires_explicit_mirror_deliver')
        remote = config['vcs']['git']['remote']
        if any(not x or x.startswith('-') or any(c.isspace() for c in x) for x in (remote, branch)):
            raise Refusal('unsafe_transport_ref')
        b.recheck()
        v1.git(root, 'push', remote, f'HEAD:refs/heads/{branch}')
        result['pushed'] = True
    return result
