"""The product dispatcher; all handlers cross the same repository boundary.

Foundation, authority/lane and maintained product services are registered. Engine tests may inject their own dependencies
below this boundary; there is no production validation-bypass switch.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys

from cli import v1
from cli.v1_io import LIMIT, Refusal, digest, read

from cli.product_commands import COMMANDS as PRODUCT_COMMANDS

COMMANDS = PRODUCT_COMMANDS | frozenset({'status', 'init', 'sync', 'next', 'next-write', 'hook', 'adopt', 'mirror', 'upgrade-regime'})


@dataclass(frozen=True)
class ValidatedContext:
    root: Path
    config: dict
    original: bytes
    observed: dict

    @classmethod
    def capture(cls, root, args, *, syncing=False):
        config, original = v1.config_for(root, args, syncing=syncing)
        return cls(root, config, original, v1.capture_context(root, original))

    def recheck(self, args):
        v1.check_context(self.root, self.config, args, self.observed)


def parser():
    p = argparse.ArgumentParser(prog='ok', description='Repository-bound Overseer product; local changes, remote transport and release are separate',
                                allow_abbrev=False)

    def globals_to(target):
        for names, opts in [
            (('-C', '--repo'), {}), (('--config',), {}),
            (('--json',), {'action': 'store_true'}),
            (('-q', '--quiet'), {'action': 'store_true'}),
            (('-v', '--verbose'), {'action': 'store_true'}),
            (('--no-color',), {'action': 'store_true'}),
            (('--bound-root',), {'help': argparse.SUPPRESS}),
            (('--bound-id',), {'help': argparse.SUPPRESS}),
            (('--binding-path',), {'help': argparse.SUPPRESS}),
        ]:
            target.add_argument(*names, default=argparse.SUPPRESS, **opts)

    globals_to(p)
    p.set_defaults(repo=None, config=None, json=False, quiet=False, verbose=False,
                   no_color=False, bound_root=None, bound_id=None, binding_path=None)
    p.add_argument('--version', action='version', version=v1.VERSION)
    sub = p.add_subparsers(dest='command', required=True)
    for name in sorted(COMMANDS):
        cmd = sub.add_parser(name, allow_abbrev=False)
        globals_to(cmd)
        if name in PRODUCT_COMMANDS:
            from cli.product_commands import configure
            configure(cmd, name, globals_to)
        if name in ('init', 'adopt'):
            cmd.add_argument('--vcs', choices=('git', 'muse'))
            cmd.add_argument('--muse-python')
            cmd.add_argument('--tracked-bindings', choices=('preserve',))
        if name == 'adopt':
            cmd.add_argument('--restore-config')
            cmd.add_argument('--expect-config', required=True)
            cmd.add_argument('--base-head', required=True)
            cmd.add_argument('--dry-run', action='store_true')
        if name == 'mirror':
            cmd.add_argument('operation', choices=('prepare', 'reconcile', 'verify', 'deliver'))
            cmd.add_argument('--plan-file', required=True)
            cmd.add_argument('--expect-plan', required=True)
            cmd.add_argument('--gh')
            cmd.add_argument('--allow-network', action='store_true')
        if name == 'upgrade-regime':
            cmd.add_argument('--plan-file')
            cmd.add_argument('--expect-plan')
            cmd.add_argument('--expect-config')
            cmd.add_argument('--apply', action='store_true')
            cmd.add_argument('--dry-run', action='store_true')
            cmd.add_argument('--yes', action='store_true')
            cmd.add_argument('--live-bridge', action='store_true')
        if name == 'init':
            cmd.add_argument('--muse-staging-remote')
            cmd.add_argument('--mirror-branch')
            cmd.add_argument('--regime', default=None)
            cmd.add_argument('--repo-name')
            cmd.add_argument('--lane')
            cmd.add_argument('--model')
            cmd.add_argument('--non-interactive', action='store_true')
            cmd.add_argument('--migrate', action='store_true')
            cmd.add_argument('--apply-plan', help='Confined JSON plan from migration dry-run')
            cmd.add_argument('--expect-plan')
            cmd.add_argument('--expect-config')
            cmd.add_argument('--resume', action='store_true')
            cmd.add_argument('--refresh-runtime', action='store_true')
        if name in ('init', 'sync'):
            cmd.add_argument('--hooks', action='store_true', help='Install bound Cursor bookends in the explicitly selected repository')
            cmd.add_argument('--dry-run', action='store_true')
        if name == 'sync':
            cmd.add_argument('--only', action='append', metavar='GLOB',
                             help='Select available foundation asset paths (or launcher/hooks)')
            cmd.add_argument('--diff', action='store_true')
            cmd.add_argument('--preserve-modified', action='store_true')
        if name in ('next', 'next-write', 'status', 'adopt'):
            for field in ('repo-id', 'branch', 'lane', 'model', 'action-id', 'action-kind'):
                cmd.add_argument('--' + field, required=(name == 'next-write' and field in ('repo-id', 'branch')) or (name == 'adopt' and field not in ('action-id', 'action-kind')),
                                 choices=v1.KINDS if field == 'action-kind' else None)
            if name != 'adopt':
                cmd.add_argument('--expect-next', required=name == 'next-write')
        if name == 'status':
            cmd.add_argument('--exit-code', action='store_true')
            cmd.add_argument('--check-footprint', action='store_true')
            cmd.add_argument('--workspace', action='store_true')
        if name in ('next', 'status'):
            cmd.add_argument('--all-lanes', action='store_true')
        if name == 'next-write':
            cmd.add_argument('--vcs', choices=('git', 'muse'))
            cmd.add_argument('--base-head')
            cmd.add_argument('--prompt-file', help='Confined repository-relative UTF-8 file')
            cmd.add_argument('--batch-file', help='Confined JSON map of explicitly selected lane updates')
            cmd.add_argument('--reset-authority', action='store_true', help='Explicitly replace old-authority lane collection after adoption')
        if name == 'hook':
            cmd.add_argument('--lane')
            cmd.add_argument('--hook-path', required=True)
            cmd.add_argument('--event', choices=('sessionStart', 'stop'))
    return p


def build_parser():
    """Preserve the public parser factory on the unified command registry."""
    return parser()


def _arguments(argv):
    # Argparse permits duplicate and abbreviated selectors. Neither may change
    # the binding established by a generated launcher or a caller's earlier flag.
    for aliases in (('-C', '--repo'), ('--config',), ('--bound-root',), ('--bound-id',),
                    ('--binding-path',), ('--lane',), ('--model',), ('--repo-id',),
                    ('--branch',), ('--vcs',), ('--base-head',), ('--action-id',), ('--action-kind',),
                    ('--prompt-file',), ('--batch-file',), ('--expect-next',), ('--expect-plan',), ('--expect-config',)):
        if sum(a.split('=', 1)[0] in aliases or
               (a.startswith('-C') and a != '-C' and '-C' in aliases) for a in argv) > 1:
            raise Refusal('duplicate_binding_option')
    args = parser().parse_args(argv)
    if args.command == 'next-write':
        if bool(args.prompt_file) == bool(args.batch_file):
            raise Refusal('next_write_requires_prompt_or_batch_file')
        fields = ('lane', 'model', 'action_id', 'action_kind')
        if args.batch_file and any(getattr(args, k, None) for k in fields):
            raise Refusal('batch_entries_supply_lane_model_action')
        if not args.batch_file and not all(getattr(args, k, None) for k in fields):
            raise Refusal('next_write_requires_explicit_lane_model_action')
    if args.command == 'init':
        migrate_flags = args.apply_plan or args.expect_plan or args.expect_config or args.resume or args.refresh_runtime
        if migrate_flags and not args.migrate:
            raise Refusal('migration_options_require_migrate')
        if args.migrate:
            if args.dry_run == bool(args.apply_plan):
                raise Refusal('migration_requires_dry_run_or_apply_plan')
            if args.apply_plan and not (args.expect_plan and args.expect_config):
                raise Refusal('migration_expected_digests_required')
            if args.dry_run and (args.expect_plan or args.expect_config or args.resume):
                raise Refusal('migration_apply_options_in_dry_run')
    if args.command == 'sync' and args.only and 'hooks' in args.only and not args.hooks:
        raise Refusal('sync_hooks_require_explicit_hooks')
    from cli.product_commands import validate
    validate(args)
    return args


def _inspect(root, args):
    """Read-only legacy/Muse inspection has no authoritative revision or NEXT."""
    from cli.product_config import normalize
    original = read(root, v1.CONFIG)
    model = normalize(original, root=root)
    config = model.data
    if model.bound and (config['vcs']['canonical'] == 'git' or config['vcs']['muse'].get('binding')):
        return None
    if args.bound_id and config.get('repo', {}).get('id') != args.bound_id:
        raise Refusal('launcher_identity_mismatch')
    if config.get('runtime') and config['runtime'].get('root') != str(v1.KIT):
        raise Refusal('runtime_installation_mismatch')
    if config.get('runtime') and config['runtime'] != v1.runtime():
        raise Refusal("runtime_changed: run this installation's explicit sync")
    for field, actual in (('repo_id', config['repo'].get('id')),
                          ('lane', config['context']['lane']), ('model', config['context']['model'])):
        if getattr(args, field, None) is not None and getattr(args, field) != actual:
            raise Refusal('expected_' + field + '_mismatch')
    if any(getattr(args, field, None) is not None
           for field in ('branch', 'action_id', 'action_kind', 'expect_next')):
        raise Refusal('authority_unavailable_for_expectation')
    # No Git calls or foreign authority fallback even in mixed checkouts.
    if read(root, v1.CONFIG) != original:
        raise Refusal('config_context_changed')
    return {'ok': False, 'repository': config['repo'], 'configuration': config,
            'source_schema': model.source_schema, 'migration_required': model.source_schema != 'schema-3',
            'authority': config['vcs']['canonical'], 'diagnostics': list(model.diagnostics),
            'next_error': 'authority_unavailable' if model.bound else 'configuration_unbound'}


def _read(context, args):
    root, config, observed = context.root, context.config, context.observed
    event = None
    if args.command == 'hook':
        from cli.product_bookends import read_event, validate_event
        raw = b'' if sys.stdin.isatty() else read_event(sys.stdin)
        event = validate_event(root, config, args, raw)
    result = {'ok': True, 'repository': config['repo'], 'branch': observed['branch'],
              'head': observed['head'], 'runtime': config['runtime'],
              'vcs': observed['vcs'], 'source_id': observed['source_id'],
              'publication': 'not_checked_offline'}
    try:
        data = read(root, v1.NEXT)
        from cli.product_next import display
        fields, output = display(root, config, data, args, observed)
        result.update(fields, next_sha256=digest(data))
    except Refusal as exc:
        if args.command != 'status':
            raise
        result.update(ok=False, next_error=str(exc))
    if args.command in ('next', 'hook'):
        context.recheck(args)
        if args.command == 'hook':
            from cli.product_bookends import hook_response
            print(json.dumps(hook_response(output, event)))
        elif args.json:
            print(json.dumps(dict(result, rendered=output)))
        elif not args.quiet:
            print(output, end='')
        return None
    from cli.product_config import normalize
    from cli.product_migration import classify_assets, inventory
    model = normalize(context.original, root=root)
    result.update(configuration=config, source_schema=model.source_schema,
                  migration_required=model.source_schema != 'schema-3',
                  diagnostics=list(model.diagnostics), authority=config['vcs']['canonical'],
                  assets=classify_assets(root, v1.assets(root, config), config),
                  preserved_inventory=inventory(root, config))
    state = v1.revision(root, config, dirty=True)
    result.update(dirty=state.dirty, tracked_local=list(state.tracked_local))
    if state.kind == 'muse':
        from cli.v1_mirror import RECORD
        record = read(root, RECORD, missing=True)
        result['mirror'] = {'record_present': record is not None, 'verification': 'not_checked_offline',
                            'authority': False}
    from cli.product_status import sections
    result.update(sections(context, args))
    if getattr(args, 'check_footprint', False) or getattr(args, 'exit_code', False):
        result['ok'] = result['ok'] and result['footprint_integrity']['ok'] and result['footprint_coverage']['ok']
    if getattr(args, 'exit_code', False):
        result['ok'] = result['ok'] and result['drift']['status'] == 'current'
    if 'workspace' in result:
        result['ok'] = result['ok'] and result['workspace']['ok']
    context.recheck(args)
    return result


def main(argv=None):
    try:
        args = _arguments(list(sys.argv[1:] if argv is None else argv))
        root = v1.root_for(args)
        if args.command == 'init':
            if args.migrate:
                from cli.product_migration import migrate
                result = migrate(root, args)
            else:
                result = v1.initialize(root, args)
        elif args.command == 'adopt':
            from cli.product_authority import adopt
            config, original = v1.config_for(root, args, authority=False)
            result = adopt(root, config, original, args)
        elif args.command == 'status' and (inspection := _inspect(root, args)) is not None:
            result = inspection
        else:
            context = ValidatedContext.capture(root, args, syncing=args.command == 'sync')
            if args.command == 'sync':
                from cli.product_migration import sync
                result = sync(root, context.config, context.original, args)
            elif args.command == 'mirror':
                if args.operation == 'deliver' and not (args.allow_network and args.gh):
                    raise Refusal('mirror_deliver_requires_allow_network_and_explicit_gh')
                from cli.v1_mirror import command
                context.recheck(args)
                result = command(root, context.config, context.original, args)
                context.recheck(args)
            elif args.command == 'upgrade-regime':
                from cli.product_upgrade import upgrade
                result = upgrade(context, args)
            elif args.command == 'next-write':
                prompt = '' if args.batch_file else read(root, args.prompt_file).decode('utf-8')
                if not prompt.endswith('\n'):
                    prompt += '\n'
                expected = args.expect_next
                args.expect_next = None
                result = {'ok': True, 'next_sha256': digest(v1.write_next(
                    root, context.config, args, prompt, expected=expected, context=context.observed))}
            elif args.command in PRODUCT_COMMANDS:
                from cli.product_service import execute
                return execute(context, args)
            else:
                result = _read(context, args)
                if result is None:
                    return 0
        if args.json or not args.quiet:
            print(json.dumps(result, indent=None if args.json else 2))
        return 0 if result['ok'] else 1
    except (Refusal, OSError, ValueError, UnicodeError, subprocess.SubprocessError) as exc:
        message = str(exc) if isinstance(exc, Refusal) else type(exc).__name__
        print('refused: ' + message[:300], file=sys.stderr)
        return 2


if __name__ == '__main__':
    print('refused: launch with cli/ok', file=sys.stderr)
    raise SystemExit(2)
