"""Shared bound command execution for CLI and local app requests."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import shlex
import subprocess
import os
import re

from cli import v1
from cli.product_boundary import engine_boundary
from cli.v1_io import Refusal

HANDLERS = {
    'review': ('review', 'run_review'),
    'check-ok': ('check_ok', 'run_check_ok'),
    'check-if-ok': ('check_ok', 'run_check_ok'),
    'verify-step': ('verify_step', 'run_verify_step_command'),
    'honesty-status': ('honesty_status', 'run_honesty_status_command'),
    'ledger': ('ledger', 'run_ledger_command'),
    'route': ('route', 'run_route_command'),
    'handover-compact': ('handover_compact', 'run_handover_compact_command'),
    'app': ('app', 'run_app'),
    'hosted-dashboard': ('hosted_dashboard', 'run_hosted_dashboard'),
    'land-check': ('land_check', 'run_land_check_command'),
    'land-closeout': ('land_closeout', 'run_land_closeout_command'),
    'pr-land': ('pr_land', 'run_pr_land_command'),
}


class CapturedOutput:
    json_mode = True
    quiet = False
    verbose = False
    no_color = True

    def __init__(self):
        self.payload = None
        self.messages = []

    def emit_json(self, value):
        self.payload = value

    def emit(self, value):
        self.messages.append(str(value))

    error = warn = debug = emit


class BoundRunner:
    """Argv-only transport, fixed repository, no ambient shell or Muse binary."""
    def __init__(self, boundary):
        self.boundary = boundary

    def run(self, command, *, cwd=None):
        from adapters.runner import CommandResult
        b = self.boundary
        if cwd is not None and Path(cwd).resolve() != b.context.root:
            raise Refusal('engine_runner_repository_mismatch')
        argv = shlex.split(command)
        if not argv:
            raise Refusal('empty_command')
        b.recheck()
        if argv[0] == 'git':
            allowed = {'rev-parse', 'status', 'log', 'show', 'diff', 'merge-base',
                       'symbolic-ref', 'ls-files', 'for-each-ref', 'remote'}
            if len(argv) < 2 or argv[1] not in allowed:
                raise Refusal('engine_git_mutation_requires_explicit_service')
            if argv[1] == 'remote' and argv[2:3] != ['get-url']:
                raise Refusal('engine_remote_read_only')
            value = v1.git(b.context.root, *argv[1:], optional=True)
            return CommandResult(value, '', 0 if value else 1)
        if argv[0] == 'gh' and getattr(b.args, 'allow_network', False):
            result = gh_run(b, argv)
            return CommandResult(result.stdout.strip(), result.stderr.strip(), result.returncode)
        raise Refusal('engine_transport_not_authorized')


def _github_repository(boundary):
    """Capture the configured remote once, then refuse target changes mid-call."""
    remote = boundary.context.config['vcs']['git']['remote']
    url = v1.git(boundary.context.root, 'remote', 'get-url', remote, optional=True)
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?', url)
    if not match:
        raise Refusal('gh_requires_bound_github_remote')
    target = (remote, url, 'github.com/' + match[1])
    prior = getattr(boundary, '_github_target', target)
    if prior != target:
        raise Refusal('gh_bound_remote_changed')
    boundary._github_target = target
    return target[2]


def _pr_url_number(value, repository):
    if not isinstance(value, str):
        raise Refusal('gh_pr_identity_invalid')
    match = re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)', value, re.IGNORECASE)
    if not match or ('github.com/' + match[1]).lower() != repository.lower():
        raise Refusal('gh_pr_repository_mismatch')
    return match[2]


def _pr_selector(value, repository, root):
    """Keep number, matching URL and Git branch selectors; reject argv options."""
    if not isinstance(value, str) or not value or value.startswith('-'):
        raise Refusal('gh_pr_selector_invalid')
    if '://' in value:
        return _pr_url_number(value, repository)
    if re.fullmatch(r'[0-9]+', value):
        if not re.fullmatch(r'[1-9][0-9]*', value):
            raise Refusal('gh_pr_selector_invalid')
        return value
    # Use the bound local Git validator rather than narrowing its branch grammar.
    # Reject expressions before Git can expand them against checkout history.
    if ('\0' in value or '@{' in value or
            not v1.git(root, 'check-ref-format', '--branch', value, optional=True, raw=True)):
        raise Refusal('gh_pr_selector_invalid')
    return value


def _github_arguments(boundary, argv, repository):
    """Constrain retained PR operations before any transport sees caller argv."""
    if len(argv) < 3 or argv[:2] != ['gh', 'pr']:
        raise Refusal('gh_command_not_supported')
    operation = argv[2]
    args = list(argv)
    if operation == 'list':
        # The maintained callers request recent merged PR enrichment only.
        pairs = args[3:]
        if len(pairs) != 6 or pairs[::2] != ['--state', '--limit', '--json'] or pairs[1] != 'merged' or not re.fullmatch(r'[1-9][0-9]*', pairs[3]):
            raise Refusal('gh_pr_arguments_invalid')
    else:
        valid = (operation == 'view' and len(args) == 6 and args[4] == '--json' or
                 operation == 'checks' and len(args) == 4 or
                 operation == 'merge' and len(args) == 5 and args[4] in {'--squash', '--merge', '--rebase'})
        if not valid:
            raise Refusal('gh_pr_arguments_invalid')
        selector = _pr_selector(args[3], repository, boundary.context.root)
        if operation == 'view':
            args[3] = selector
        else:
            resolved = getattr(boundary, '_github_pr_resolutions', {}).get(selector)
            if resolved is None:
                raise Refusal('gh_pr_identity_not_resolved')
            args[3] = resolved
    if operation in {'view', 'list'}:
        fields = args[-1].split(',')
        if not fields or any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', field) for field in fields):
            raise Refusal('gh_pr_arguments_invalid')
        if operation == 'view':
            args[-1] = ','.join(dict.fromkeys([*fields, 'number', 'url']))
    if operation == 'merge' and (not getattr(boundary.args, 'authorized', '').strip() or getattr(boundary.args, 'dry_run', False)):
        raise Refusal('gh_pr_merge_not_authorized')
    return args + ['--repo', repository]


def _remember_pr_identity(boundary, selector, response, repository):
    from cli.v1_revision import unique_json
    try:
        value = json.loads(response.stdout, object_pairs_hook=unique_json)
    except (ValueError, TypeError):
        raise Refusal('gh_pr_identity_invalid') from None
    if not isinstance(value, dict) or type(value.get('number')) is not int or value['number'] <= 0:
        raise Refusal('gh_pr_identity_invalid')
    number = _pr_url_number(value.get('url'), repository)
    if number != str(value['number']) or (re.fullmatch(r'[1-9][0-9]*', selector) and selector != number):
        raise Refusal('gh_pr_identity_mismatch')
    identities = getattr(boundary, '_github_pr_resolutions', {})
    if selector in identities and identities[selector] != number:
        raise Refusal('gh_pr_identity_changed')
    identities[selector] = number
    boundary._github_pr_resolutions = identities


def gh_run(boundary, argv):
    executable = getattr(boundary.args, 'gh', None)
    if not getattr(boundary.args, 'allow_network', False) or not executable:
        raise Refusal('remote_requires_allow_network_and_explicit_gh')
    path = Path(executable)
    if not path.is_absolute() or path.resolve() != path or not path.is_file():
        raise Refusal('gh_executable_must_be_physical')
    boundary.recheck()
    repository = _github_repository(boundary)
    argv = _github_arguments(boundary, argv, repository)
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_') and k not in ('GH_REPO', 'GH_HOST')}
    env.update(GH_REPO=repository, GH_HOST='github.com', GH_PROMPT_DISABLED='1')
    result = subprocess.run([str(path), *argv[1:]], cwd=boundary.context.root,
                            env=env, capture_output=True, text=True, timeout=60)
    boundary.recheck()
    _github_repository(boundary)
    if argv[2] == 'view' and result.returncode == 0:
        _remember_pr_identity(boundary, argv[3], result, repository)
    return result


def mutates(args):
    if args.command in {'review', 'check-ok', 'check-if-ok'}:
        return not args.dry_run and (args.command != 'review' or not args.no_stamp)
    return (getattr(args, 'write', False) or getattr(args, 'post_land_sync', False) or args.command == 'land-check' or
            (args.command == 'verify-step' and not args.dry_run) or
            (args.command == 'ledger' and args.ledger_action == 'append'))


def invoke(context, args, *, provider_factory=None, script_executor=None):
    from cli.context import CliContext
    output = CapturedOutput()
    args.repo = str(context.root)
    # Reviewer --model is a policy label, not a context identity selector.
    with engine_boundary(context, args, writable=mutates(args)) as boundary:
        lane = getattr(args, 'lane', None)
        if lane is not None and lane not in context.config['docs']['lanes']:
            raise Refusal('unknown_lane')
        from cli.product_migration import inventory
        for row in inventory(context.root, context.config):
            boundary.watch(row['path'])
        if args.command in {'review', 'check-ok', 'check-if-ok'}:
            provider = args.provider or boundary.model.adapter.freeze_contract.reviewer.provider
            if provider == 'api' and not args.dry_run and not getattr(args, 'allow_network', False) and provider_factory is None:
                raise Refusal('api_review_requires_explicit_allow_network')
        ctx = CliContext(kit=v1.KIT, cwd=context.root, runner=BoundRunner(boundary), output=output,
                         review_provider_factory=provider_factory, script_executor=script_executor)
        ctx.bound_context = context
        ctx.bound_args = args
        if args.command == 'governance-sync':
            from cli.product_governance import run
            payload = run(boundary)
            code = payload.get('exit_code', 0 if payload['ok'] else 2)
        elif args.command in {'land-check', 'land-closeout'}:
            from cli.product_landing import run
            payload = run(boundary)
            code = payload['exit_code']
        elif args.command == 'workspace':
            from cli.product_workspace import report
            payload = report(context, args)
            code = payload['exit_code']
        else:
            module, name = HANDLERS[args.command]
            code = getattr(importlib.import_module('cli.commands.' + module), name)(args, ctx)
            payload = output.payload
        boundary.recheck()
    if payload is None:
        payload = {'ok': code == 0, 'exit_code': code, 'messages': output.messages}
    else:
        payload = dict(payload, ok=code == 0, exit_code=code)
        if output.messages:
            payload['messages'] = output.messages
    return code, payload


def execute(context, args):
    code, payload = invoke(context, args)
    if args.json or not args.quiet:
        print(json.dumps(payload, indent=None if args.json else 2))
    return code
