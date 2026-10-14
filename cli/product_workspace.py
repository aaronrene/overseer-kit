"""Explicit constellation members, each validated against its own canonical NEXT."""
from argparse import Namespace
from dataclasses import asdict
from pathlib import Path

from cli import v1
from cli.v1_io import read, digest, Refusal


def report(context, args):
    from cli.main import ValidatedContext
    from cli.product_next import display
    from tools.workspace.manifest import validate_manifest_dict
    from tools.workspace.board_names import board_name_violation
    setting = context.config.get('workspace')
    if not setting:
        return {'ok': True, 'configured': False, 'state': 'not_configured', 'exit_code': 0, 'members': []}
    # A declared relative manifest is the only discovery path. No env/home scan.
    relative = setting.get('manifest') or '.overseer/workspace.yaml'
    raw = v1.decode(read(context.root, relative))
    pins = raw.pop('canonical_next_pins', {})
    if not isinstance(pins, dict):
        raise Refusal('workspace_pins_invalid')
    manifest = validate_manifest_dict(raw, source_path=context.root / relative,
        manifest_source='config_manifest', expected_constellation_id=setting['constellation_id'])
    lane = getattr(args, 'lane', None) or manifest.primary_lane().id
    if lane not in {row.id for row in manifest.lanes}:
        raise Refusal('workspace_lane_unknown')
    members, captured, identities = [], [], set()
    for member in manifest.members:
        row = {'id': member.id, 'role': member.role, 'required': member.required, 'ok': False}
        root_path = Path(member.root_raw)
        if not root_path.is_absolute() or '$' in member.root_raw or '~' in member.root_raw:
            row['error'] = 'explicit_absolute_member_root_required'
        else:
            try:
                root = root_path.resolve(strict=True)
                a = Namespace(repo=str(root), config=None, bound_root=None, bound_id=None,
                              binding_path=None, lane=lane, all_lanes=False)
                member_context = ValidatedContext.capture(root, a)
                config = member_context.config
                identity = config['repo']['id']
                if identity in identities:
                    raise Refusal('workspace_duplicate_identity')
                identities.add(identity)
                if member.regime and member.regime != config['vcs']['regime']:
                    raise Refusal('workspace_member_regime_mismatch')
                data = read(root, v1.NEXT)
                fields, rendered = display(root, config, data, a, member_context.observed)
                if member.id in pins and pins[member.id] != digest(data):
                    raise Refusal('stale_relay_pin')
                row.update(ok=fields.get('ok', True), repository=config['repo'],
                           next_sha256=digest(data), next=fields, rendered=rendered,
                           relay='verified_pin' if member.id in pins else 'live_canonical_read')
                lane_docs = config['docs']['lanes'][lane]
                if board_name_violation(repo_name=config['repo']['name'],
                        handover_basename=Path(lane_docs['handover']).name,
                        roadmap_basename=Path(lane_docs['roadmap']).name,
                        strict=manifest.strict_board_names):
                    row['diagnostics'] = ['board_name_violation']
                    if getattr(args, 'workspace_action', None) == 'doctor':
                        row.update(ok=False, error='board_name_violation')
                member_context.recheck(a)
                captured.append((member_context, a))
            except (Refusal, OSError, ValueError) as exc:
                row['error'] = str(exc)
        members.append(row)
    for c, a in captured:
        c.recheck(a)
    context.recheck(args)
    ok = all(row['ok'] or (not row['required'] and not getattr(args, 'strict_all', False)) for row in members)
    return {'ok': ok, 'configured': True, 'state': 'ok' if ok else 'member_refusal',
            'constellation_id': manifest.id, 'lane': lane, 'members': members,
            'exit_code': 0 if ok else 35, 'discovery': 'explicit_manifest_only'}
