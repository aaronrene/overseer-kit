"""Explicit authority changes; preserve complete settings, history and NEXT."""
from __future__ import annotations

import os
from copy import deepcopy
from cli.v1_io import Refusal, read, digest, confined
from cli.v1_revision import muse_read, revision
from cli.v1_policy import ignore_assets, local_path


def select(root, args, existing=None):
    selected = getattr(args, 'vcs', None)
    regime = getattr(args, 'regime', None)
    if regime:
        if regime not in ('git-only', 'muse-only', 'muse+git-mirror'):
            raise Refusal('regime_invalid')
        mapped = 'git' if regime == 'git-only' else 'muse'
        if selected and selected != mapped:
            raise Refusal('conflicting_vcs_selection')
        selected = mapped
    if selected is None:
        if existing:
            return existing['vcs']['canonical']
        if os.path.lexists(root / '.muse'):
            raise Refusal('explicit_vcs_selection_required')
        selected = 'git'
    return selected


def bind_muse(root, config, python):
    if not python:
        raise Refusal('muse_python_required')
    state = muse_read(root, str(python))
    result = deepcopy(config)
    result['vcs']['canonical'] = 'muse'
    if result['vcs']['regime'] == 'git-only':
        result['vcs']['regime'] = 'muse-only'
    section = result['vcs']['muse']
    section['main_branch'] = section.get('main_branch') or 'main'
    section['binding'] = {k: state[k] for k in ('repo_id', 'store', 'runtime')}
    return result


def tracked_bindings(root, config):
    from cli import v1
    result = {}
    if (root / '.git').exists():
        result['git'] = sorted(p for p in v1.git(root, 'ls-files', '-z').split('\0') if local_path(p))
    if config['vcs']['canonical'] == 'muse':
        result['muse'] = list(revision(root, config).tracked_local)
    return result


def adopt(root, config, original, args):
    from cli import v1
    from cli.product_config import normalize
    from cli.product_migration import apply_mapping
    if digest(original) != args.expect_config:
        raise Refusal('stale_write: ' + v1.CONFIG)
    for field, actual in {'repo_id': config['repo']['id'], **config['context']}.items():
        if getattr(args, field) != actual:
            raise Refusal('expected_' + field + '_mismatch')
    mapping = {}
    ignore_expected = {}
    captured_source = None
    if args.restore_config:
        if args.muse_python or args.vcs:
            raise Refusal('rollback_uses_preserved_binding')
        if not args.restore_config.startswith('.overseer/local/'):
            raise Refusal('rollback_requires_local_config_backup')
        payload = read(root, args.restore_config)
        updated = normalize(payload, root=root).data
        if updated['repo'] != config['repo'] or updated['context'] != config['context']:
            raise Refusal('rollback_identity_or_context_mismatch')
        if updated['runtime'] != v1.runtime():
            raise Refusal('rollback_runtime_mismatch')
    else:
        updated = deepcopy(config)
        authority = select(root, args, config)
        if authority == 'muse':
            updated = bind_muse(root, updated, args.muse_python or
                config['vcs']['muse'].get('binding', {}).get('runtime', {}).get('python'))
            mapping.update(ignore_assets(root, expected=ignore_expected))
        else:
            if args.muse_python:
                raise Refusal('git_does_not_use_muse_python')
            updated['vcs']['canonical'] = 'git'
            updated['vcs']['regime'] = 'git-only'
            updated['vcs']['muse'].pop('binding', None)
        updated['runtime'] = v1.runtime()
        payload = v1.encode(updated)
        updated = normalize(payload, root=root).data
    target = revision(root, updated)
    if not args.restore_config:
        if config['vcs']['canonical'] == updated['vcs']['canonical'] == 'muse':
            before_binding = config['vcs']['muse']['binding']
            after_binding = updated['vcs']['muse']['binding']
            if any(before_binding[k] != after_binding[k] for k in ('repo_id', 'store')):
                raise Refusal('adoption_source_identity_change_refused')
        else:
            captured_source = v1.capture_context(root, original, config)
    if (target.branch, target.head) != (args.branch, args.base_head):
        raise Refusal('adoption_target_revision_mismatch')
    tracked = tracked_bindings(root, updated)
    preservation = getattr(args, 'tracked_bindings', None) == 'preserve'
    allowed = updated['vcs']['canonical'] == 'git' or not any(tracked.values()) or preservation
    backup = '.overseer/local/config-before-' + digest(original) + '.yaml'
    previous = read(root, backup, missing=True)
    if previous is not None and previous != original:
        raise Refusal('adoption_backup_mismatch')
    mapping[backup] = original
    mapping[v1.CONFIG] = payload
    # Snapshot all planned inputs before any replacement. apply_mapping supplies
    # the shared lock, CAS, after-lock and before-replace checks; config is last.
    expected = {p: read(root, p, missing=True) for p in mapping}
    protected = {p: read(root, p, missing=True) for p in (v1.NEXT, '.overseer/bin/ok')}
    runtime = v1.runtime()
    def recheck():
        if captured_source is not None:
            v1.check_context(root, config, args, captured_source)
        for p, prior_digest in ignore_expected.items():
            body = read(root, p, missing=True)
            if ('absent' if body is None else digest(body)) not in (prior_digest, digest(mapping[p])):
                raise Refusal('stale_write: ' + p)
        if read(root, v1.CONFIG) != original or v1.runtime() != runtime or revision(root, updated) != target:
            raise Refusal('context_changed_before_adoption')
        for p, body in protected.items():
            if read(root, p, missing=True) != body:
                raise Refusal('adoption_protected_changed')
        for p, body in expected.items():
            # Partial additive backup/ignore writes are repeatable; owner edits refuse.
            if read(root, p, missing=True) not in (body, mapping[p]):
                raise Refusal('stale_write: ' + p)
    if not args.dry_run and not allowed:
        raise Refusal('tracked_local_bindings: choose --tracked-bindings preserve or untrack separately')
    for p in mapping:
        confined(root, p, missing_parents=True)
    changed = apply_mapping(root, mapping, check_context=recheck, dry_run=args.dry_run)
    return {'ok': allowed, 'repository': config['repo'], 'vcs': updated['vcs']['canonical'],
            'branch': target.branch, 'head': target.head, 'changed': changed, 'backup': backup,
            'tracked_local': tracked, 'tracked_binding_choice': 'preserve' if preservation else None,
            'config_sha256': digest(payload), 'dry_run': args.dry_run,
            'next': 'preserved; explicitly publish after the authority change',
            'rollback': 'adopt --restore-config ' + backup + '; additive ignores retained'}
