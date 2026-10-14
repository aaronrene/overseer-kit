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


def gh_run(boundary, argv):
    executable = getattr(boundary.args, 'gh', None)
    if not getattr(boundary.args, 'allow_network', False) or not executable:
        raise Refusal('remote_requires_allow_network_and_explicit_gh')
    path = Path(executable)
    if not path.is_absolute() or path.resolve() != path or not path.is_file():
        raise Refusal('gh_executable_must_be_physical')
    boundary.recheck()
    remote = boundary.context.config['vcs']['git']['remote']
    url = v1.git(boundary.context.root, 'remote', 'get-url', remote, optional=True)
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?', url)
    if not match:
        raise Refusal('gh_requires_bound_github_remote')
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_') and k not in ('GH_REPO', 'GH_HOST')}
    env.update(GH_REPO='github.com/' + match[1], GH_HOST='github.com', GH_PROMPT_DISABLED='1')
    return subprocess.run([str(path), *argv[1:]], cwd=boundary.context.root,
                          env=env, capture_output=True, text=True, timeout=60)


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
