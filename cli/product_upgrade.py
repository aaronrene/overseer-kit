"""Add controlled distribution while retaining Muse authority and all settings."""
import json
from copy import deepcopy
from cli.v1_io import Refusal, read, digest
from cli.v1_revision import unique_json


def upgrade(context, args):
    from cli import v1
    from cli.v1_mirror import validate_plan
    from cli.product_migration import apply_mapping
    root, config = context.root, context.config
    if args.live_bridge:
        raise Refusal('unsafe_legacy_live_export_refused: use mirror prepare/reconcile/verify; explicit mirror deliver for transport')
    if config['vcs']['canonical'] != 'muse':
        raise Refusal('upgrade_regime_requires_muse_authority')
    if args.apply and args.dry_run:
        raise Refusal('upgrade_apply_dry_run_conflict')
    if not args.plan_file or not args.expect_plan:
        raise Refusal('upgrade_requires_controlled_plan_and_expected_digest')
    raw = read(root, args.plan_file)
    if digest(raw) != args.expect_plan:
        raise Refusal('mirror_plan_digest_mismatch')
    plan = json.loads(raw, object_pairs_hook=unique_json)
    try:
        validate_plan(plan, root, config)
    except (TypeError, KeyError, AttributeError):
        raise Refusal('mirror_plan_invalid') from None
    if (plan['source']['branch'], plan['source']['revision']) != (context.observed['branch'], context.observed['head']):
        raise Refusal('mirror_source_drift')
    updated = deepcopy(config)
    updated['vcs']['regime'] = 'muse+git-mirror'
    if not updated['vcs']['muse']['staging_remote']:
        updated['vcs']['muse']['staging_remote'] = plan['source']['hub_url']
    if not updated['vcs']['git']['mirror_branch']:
        updated['vcs']['git']['mirror_branch'] = plan['destination']['branch']
    from cli.product_config import normalize
    updated = normalize(v1.encode(updated), root=root).data
    # Existing remote/branch settings remain owner data. The approved mirror
    # plan supplies isolated distribution choices, not a native export route.
    mapping = {v1.CONFIG: v1.encode(updated)}
    if args.apply and args.expect_config != digest(context.original):
        raise Refusal('upgrade_expected_config_required_or_stale')
    changed = apply_mapping(root, mapping, check_context=lambda: context.recheck(args), dry_run=not args.apply)
    return {'ok': True, 'changed': changed, 'dry_run': not args.apply,
            'authority': 'muse', 'regime': updated['vcs']['regime'],
            'plan_sha256': digest(raw), 'next_operation': 'mirror ' + ('reconcile' if 'reconciliation' in plan else 'prepare'),
            'delivery': 'not_attempted', 'next': 'preserved'}
