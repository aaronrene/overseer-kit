"""Offline full-product observations from retained policy/gate engines."""
from dataclasses import asdict

from cli import v1
from cli.product_boundary import engine_boundary
from cli.v1_io import digest, Refusal
from cli.product_boundary import read


def sections(context, args):
    from cli.commands.route import routing_policy_status
    from cli.product_migration import classify_assets
    from tools.optional_feature_tips import build_optional_feature_tips, optional_feature_tips_payload
    from tools.cost_awareness.surface import build_cost_awareness_report, cost_awareness_payload
    from tools.governance_gates import scan_governance_gates
    from tools.verification_evidence_gate import build_verification_evidence_gate, verification_evidence_gate_payload
    from tools.independent_second_reviewer import build_independent_second_reviewer_gate, independent_second_reviewer_gate_payload
    from tools.adversarial_freeze import build_adversarial_freeze_gate, adversarial_freeze_gate_payload
    from cli.product_governance import observation
    with engine_boundary(context, args) as b:
        c, root = b.model.adapter, context.root
        assets = classify_assets(root, v1.assets(root, context.config), context.config)
        damaged = [row['path'] for row in assets if row['classification'] in
                   ('missing', 'consumer-modified', 'both-changed', 'kit-updated')]
        lane = getattr(args, 'lane', None) or context.config['context']['lane']
        if lane not in context.config['docs']['lanes']:
            raise Refusal('unknown_lane')
        docs = context.config['docs']['lanes'][lane]
        base = context.config['repo']['root_relative_docs']
        texts = {}
        for field in ('handover', 'roadmap'):
            data = read(root, base + '/' + docs[field], missing=True)
            texts[field + '_text'] = data.decode() if data is not None else None
        gates = asdict(scan_governance_gates(c, root, **texts))
        gates['pending'] = [row for row in gates['pending'] if row['gate_id'] != 'handover_paste']
        from cli.product_migration import _lock_entries, LOCK
        declared = _lock_entries(root)
        missing_records = [row['path'] for row in assets if row['path'] not in declared]
        integrity = []
        for path, entry in declared.items():
            data = read(root, path, missing=True)
            if entry.get('origin', 'kit') != 'preserved' and (data is None or digest(data) != entry['sha256'].removeprefix('sha256:')):
                integrity.append(path)
        result = {
            'substrate': {'ok': True, 'state': 'bound_' + context.observed['vcs'],
                          'source_id': context.observed['source_id']},
            'muse_sync': {'state': 'not_applicable' if context.observed['vcs'] == 'git' else 'native_revision_observed',
                          'mirror_correspondence': 'use_explicit_mirror_verify'},
            'footprint_integrity': {'ok': not integrity, 'paths_requiring_attention': integrity},
            'footprint_coverage': {'ok': not missing_records, 'missing_records': missing_records},
            'drift': {'status': 'current' if not damaged else 'changed', 'changed_files': damaged},
            'lock': v1.decode(read(root, LOCK)) if declared else None,
            'governance': observation(b, lane=lane),
            'governance_gates': gates,
            'model_routing': routing_policy_status(c, root, kit_root=v1.KIT),
            'cost_awareness': cost_awareness_payload(build_cost_awareness_report(c, root, kit_root=v1.KIT)),
            'optional_feature_tips': optional_feature_tips_payload(build_optional_feature_tips(c)),
            'verification_evidence_gate': verification_evidence_gate_payload(build_verification_evidence_gate(c, root, **texts)),
            'independent_second_reviewer_gate': independent_second_reviewer_gate_payload(build_independent_second_reviewer_gate(c, root, **texts)),
            'adversarial_freeze_gate': adversarial_freeze_gate_payload(build_adversarial_freeze_gate(c, root, **texts)),
            'readiness': {'authority': 'bound', 'remote': 'not_checked_offline', 'release': 'not_certified'},
        }
        if getattr(args, 'workspace', False):
            from cli.product_workspace import report
            result['workspace'] = report(context, args)
        return result
