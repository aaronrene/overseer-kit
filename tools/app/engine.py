"""HTTP requests share the CLI's captured context, canonical NEXT and engines."""
from pathlib import Path
from cli import v1
from cli.v1_io import Refusal, digest
from cli.product_boundary import read
from tools.app.envelope import ApiEnvelope, bad_request, engine_failure, engine_success


def _capture(ctx, repo_arg=None, lane=None):
    from cli.main import ValidatedContext, _arguments
    if lane is not None and (not isinstance(lane, str) or not lane):
        raise Refusal('invalid_lane')
    root = Path(repo_arg or ctx.cwd).resolve(strict=True)
    if root != Path(ctx.cwd).resolve() or ctx.kit.resolve() != v1.KIT:
        raise Refusal('app_repository_or_runtime_mismatch')
    args = _arguments(['-C', str(root), 'status', '--json'])
    args.lane = lane or getattr(getattr(ctx, 'bound_args', None), 'lane', None)
    c = ValidatedContext.capture(root, args)
    pinned = getattr(ctx, 'bound_context', None)
    if pinned is not None and (pinned.original != c.original or pinned.root != root):
        raise Refusal('app_binding_changed_restart_required')
    return c, args


def _failure(exc):
    return engine_failure(exit_code=2, error=str(exc)[:200], result=None)


def _invoke(ctx, argv, repo_arg=None, *, body=None, lane=None):
    from cli.main import _arguments
    from cli.product_service import invoke
    try:
        c, a = _capture(ctx, repo_arg, lane)
        args = _arguments(['-C', str(c.root), '--json', *argv])
        if hasattr(args, 'lane'):
            args.lane = a.lane
        if body is not None:
            args.append_body = body
        code, result = invoke(c, args, provider_factory=ctx.review_provider_factory,
                              script_executor=ctx.script_executor)
        return ApiEnvelope(ok=code == 0, exit_code=code, error=None if code == 0 else 'engine_refusal',
                           result=result, http_status=200)
    except SystemExit:
        return bad_request('invalid_command_arguments')
    except (Refusal, OSError, ValueError) as exc:
        return _failure(exc)


def handle_health(*, port, bind, repo_root, ctx=None):
    if ctx is None:
        from cli.context import CliContext
        ctx = CliContext.create(cwd=Path(repo_root), kit=v1.KIT)
    try:
        c, a = _capture(ctx, str(repo_root))
        c.recheck(a)
        return engine_success({'status': 'ok', 'port': port, 'bind': bind,
            'repo_root': str(c.root), 'repo_id': c.config['repo']['id'],
            'runtime': c.config['runtime'], 'lane': a.lane or c.config['context']['lane']})
    except (Refusal, OSError, ValueError) as exc:
        return _failure(exc)


def handle_status(ctx, *, repo_arg=None):
    from cli.main import _read
    try:
        c, a = _capture(ctx, repo_arg)
        result = _read(c, a)
        return ApiEnvelope(ok=result['ok'], exit_code=0 if result['ok'] else 1,
                           error=None if result['ok'] else result.get('next_error', 'status'),
                           result=result, http_status=200)
    except (Refusal, OSError, ValueError) as exc:
        return _failure(exc)


def handle_next(ctx, *, repo_arg=None, lane=None):
    from cli.product_next import display
    try:
        c, a = _capture(ctx, repo_arg, lane)
        data = read(c.root, v1.NEXT)
        fields, rendered = display(c.root, c.config, data, a, c.observed)
        c.recheck(a)
        return engine_success(dict(fields, rendered=rendered, next_sha256=digest(data)))
    except (Refusal, OSError, ValueError) as exc:
        return _failure(exc)


def handle_gates(ctx, *, repo_arg=None):
    result = handle_status(ctx, repo_arg=repo_arg)
    if result.result is not None:
        return engine_success(result.result.get('governance_gates'))
    return result


def _document(ctx, field, repo_arg):
    try:
        c, a = _capture(ctx, repo_arg)
        lane = a.lane or c.config['context']['lane']
        if lane not in c.config['docs']['lanes']:
            raise Refusal('unknown_lane')
        relative = str(Path(c.config['repo']['root_relative_docs']) / c.config['docs']['lanes'][lane][field])
        data = read(c.root, relative)
        c.recheck(a)
        return engine_success({'path': relative, 'content': data.decode(), 'text': data.decode(),
                               'lane': lane, 'canonical_next': v1.NEXT})
    except (Refusal, OSError, ValueError) as exc:
        return _failure(exc)


def handle_docs_roadmap(ctx, *, repo_arg=None):
    return _document(ctx, 'roadmap', repo_arg)


def handle_docs_handover(ctx, *, repo_arg=None):
    return _document(ctx, 'handover', repo_arg)


def handle_review_freeze(ctx, body, *, repo_arg=None):
    if set(body) - {'path', 'dry_run', 'no_stamp', 'lane', 'allow_network'}:
        return bad_request('unknown_fields')
    if not isinstance(body.get('path'), str) or not body['path'].strip():
        return bad_request('path_required')
    if any(type(body.get(key, default)) is not bool for key, default in [('dry_run', True), ('no_stamp', False), ('allow_network', False)]):
        return bad_request('invalid_boolean')
    argv = ['review', '--freeze', body['path']]
    for key, default in [('dry_run', True), ('no_stamp', False), ('allow_network', False)]:
        if body.get(key, default):
            argv.append('--' + key.replace('_', '-'))
    return _invoke(ctx, argv, repo_arg, lane=body.get('lane'))


def handle_governance_sync(ctx, body, *, repo_arg=None):
    if set(body) - {'write', 'lane'}:
        return bad_request('unknown_fields')
    if type(body.get('write', False)) is not bool:
        return bad_request('invalid_boolean')
    return _invoke(ctx, ['governance-sync', '--write' if body.get('write') else '--dry-run'],
                   repo_arg, lane=body.get('lane'))


def handle_ledger_show(ctx, *, last=None, repo_arg=None):
    return _invoke(ctx, ['ledger', 'show', '--last', str(20 if last is None else last)], repo_arg)


def handle_ledger_verify(ctx, body, *, repo_arg=None):
    if body:
        return bad_request('unknown_fields')
    return _invoke(ctx, ['ledger', 'verify'], repo_arg)


def handle_ledger_append(ctx, body, *, repo_arg=None):
    from tools.honesty.types import ENTRY_KINDS
    if set(body) - {'kind', 'entry'}:
        return bad_request('unknown_fields')
    if body.get('kind') not in ENTRY_KINDS or not isinstance(body.get('entry'), dict):
        return bad_request('invalid_entry')
    return _invoke(ctx, ['ledger', 'append', '--kind', body['kind'], '--stdin'], repo_arg, body=body['entry'])


def handle_honesty_status(ctx, body, *, repo_arg=None):
    allowed = {'hook', 'artifact', 'producer_session', 'verification_evidence', 'frozen_spec',
               'deploy_health', 'independent_second_review', 'adversarial_freeze', 'artifact_digest'}
    if set(body) - allowed or any(not isinstance(v, str) for v in body.values()):
        return bad_request('unknown_or_invalid_fields')
    argv = ['honesty-status']
    for key, value in body.items():
        argv.extend(['--' + key.replace('_', '-'), value])
    return _invoke(ctx, argv, repo_arg)
