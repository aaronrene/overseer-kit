"""Maintained command options; registered only by the unified dispatcher."""
from __future__ import annotations

COMMANDS = frozenset({'review', 'check-ok', 'check-if-ok', 'governance-sync',
    'workspace', 'verify-step', 'honesty-status', 'ledger', 'route', 'app',
    'hosted-dashboard', 'land-check', 'land-closeout', 'pr-land', 'handover-compact'})


def configure(p, name, globals_to):
    def flag(*names, **kw):
        p.add_argument(*names, **kw)
    if name in {'review', 'check-ok', 'check-if-ok'}:
        if name == 'review':
            flag('--freeze', dest='freeze_path', required=True)
        else:
            for key in ('path', 'topic', 'scope'):
                flag('--' + key)
            flag('--scaffold-only', action='store_true')
            flag('--force-scaffold', action='store_true')
        flag('--dry-run', action='store_true')
        flag('--mode', choices=('agent', 'human'))
        flag('--provider', choices=('local', 'api'))
        flag('--model', help='Reviewer policy label; does not change the NEXT model')
        flag('--no-stamp', action='store_true')
        flag('--checklist')
        flag('--override-non-pass-stamp', action='store_true')
        flag('--allow-network', action='store_true', help='Explicit provider request permission')
    if name in {'governance-sync', 'handover-compact'}:
        flag('--write', action='store_true', help='Apply local changes; governance also commits locally')
        flag('--dry-run', action='store_true', help='Read-only plan (default)')
        flag('--lane')
    if name == 'governance-sync':
        flag('--all-lanes', action='store_true')
        flag('--print-next', action='store_true', help='Read canonical docs/NEXT.md')
        flag('--push', action='store_true', help='Separately request feature-branch transport after local write')
        flag('--allow-network', action='store_true')
        flag('--gh', help='Explicit gh executable for requested remote enrichment')
    if name == 'handover-compact':
        flag('--keep', type=int, default=15)
    if name == 'workspace':
        sub = p.add_subparsers(dest='workspace_action', required=True)
        for action in ('status', 'check-next', 'doctor'):
            s = sub.add_parser(action, allow_abbrev=False)
            globals_to(s)
            s.add_argument('--lane')
            if action == 'status':
                s.add_argument('--strict-all', action='store_true')
    if name == 'verify-step':
        for key in ('manifest', 'step', 'policy'):
            flag('--' + key)
        flag('--through', choices=('current',))
        flag('--all', action='store_true')
        flag('--dry-run', action='store_true')
    if name == 'honesty-status':
        for key in ('hook', 'artifact', 'producer-session', 'verification-evidence',
                    'frozen-spec', 'deploy-health', 'independent-second-review',
                    'adversarial-freeze', 'artifact-digest'):
            flag('--' + key)
    if name == 'ledger':
        sub = p.add_subparsers(dest='ledger_action', required=True)
        for action in ('append', 'verify', 'show'):
            s = sub.add_parser(action, allow_abbrev=False)
            globals_to(s)
            if action == 'append':
                s.add_argument('--kind', required=True)
                group = s.add_mutually_exclusive_group(required=True)
                group.add_argument('--file')
                group.add_argument('--stdin', action='store_true')
            if action == 'show':
                s.add_argument('--last', type=int)
    if name == 'route':
        for key in ('position', 'phase-tier', 'gate'):
            flag('--' + key)
        flag('--validate', action='store_true')
    if name in {'app', 'hosted-dashboard'}:
        flag('--port', type=int, default=8765 if name == 'app' else 8766)
        flag('--bind', default='127.0.0.1')
        flag('--open', action='store_true')
        flag('--lane')
        if name == 'hosted-dashboard':
            flag('--allow-network', action='store_true', help='Allow configured read-only upstream sources')
    if name == 'land-check':
        flag('--mode', choices=('verify_landed', 'prepare_pr'))
    if name == 'land-closeout':
        flag('--probe-merged-pr', action='store_true', default=False)
        flag('--no-probe-merged-pr', action='store_false', dest='probe_merged_pr')
        flag('--allow-network', action='store_true')
        flag('--gh')
    if name == 'pr-land':
        flag('--pr', required=True)
        flag('--authorized', default='', help='Required explicit owner merge authorization')
        flag('--allow-network', action='store_true')
        flag('--gh', help='Explicit physical gh executable')
        flag('--method', choices=('squash', 'merge', 'rebase'), default='squash')
        flag('--poll-seconds', type=float, default=20)
        flag('--timeout-seconds', type=float, default=1800)
        flag('--allow-empty-checks', action='store_true')
        flag('--dry-run', action='store_true', help='Remote read only; still requires network authorization')
        flag('--post-land-sync', action='store_true', help='Also authorize configured clean local main checkout and ff-only remote sync')


def validate(args):
    from cli.v1_io import Refusal
    if getattr(args, 'write', False) and getattr(args, 'dry_run', False):
        raise Refusal('write_and_dry_run_conflict')
    if getattr(args, 'lane', None) and getattr(args, 'all_lanes', False):
        raise Refusal('lane_and_all_lanes_conflict')
    if args.command == 'governance-sync':
        if args.gh and not args.allow_network:
            raise Refusal('remote_enrichment_requires_allow_network')
        if args.print_next and (args.write or args.push or args.all_lanes):
            raise Refusal('print_next_incompatible_with_write_push_all_lanes')
        if args.push and not (args.write and args.allow_network):
            raise Refusal('push_requires_write_and_allow_network')
    if args.command == 'pr-land' and not (args.authorized.strip() and args.allow_network and args.gh):
        raise Refusal('pr_land_requires_authorized_allow_network_and_gh')
    if args.command == 'pr-land' and (args.poll_seconds < 0 or args.timeout_seconds <= 0):
        raise Refusal('invalid_poll_or_timeout')
    if args.command == 'land-closeout' and args.probe_merged_pr and not (args.allow_network and args.gh):
        raise Refusal('remote_probe_requires_allow_network_and_gh')
    if args.command == 'hosted-dashboard' and not args.allow_network:
        raise Refusal('hosted_sources_require_explicit_allow_network')
