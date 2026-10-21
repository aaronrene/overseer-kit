"""Explicit authority changes; preserve complete settings, history and NEXT."""
from __future__ import annotations

import os
from copy import deepcopy
from cli.v1_io import Refusal, read, digest, confined
from cli.v1_revision import muse_read, revision
from cli.v1_policy import ignore_assets, local_path

REBIND_RECOVERY = ("restore .overseer/bin/ok, .overseer/version.lock, then "
                   ".overseer/config.yaml from each copy present in {backup}/, "
                   "then preview again")


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


def rebind_muse_runtime(root, args):
    """Rebind reviewed runtimes without invoking the obsolete bound runtime.

    This explicit path can relocate the Kit binding as well as refresh Muse.
    Only the exact generated launcher is eligible. Settings, source identity,
    NEXT, policies, ledgers and living documents are protected plan inputs.
    """
    from cli import v1
    from cli.product_config import normalize
    from cli.product_migration import (
        CONFIG, LOCK, LAUNCHER, _json, _snapshot, _same, _updates, inventory,
        read as asset_read, apply_mapping)
    from cli.version_lock import FootprintEntry, compute_lock_digest

    if args.restore_config or args.vcs not in (None, 'muse') or not args.muse_python:
        raise Refusal('rebind_requires_explicit_muse_python_and_existing_authority')
    original = asset_read(root, CONFIG)
    model = normalize(original, root=root)
    config = model.data
    if not model.bound or model.source_schema != 'schema-3' or config['vcs']['canonical'] != 'muse':
        raise Refusal('rebind_requires_bound_schema3_muse')
    if config['repo']['root'] != str(root):
        raise Refusal('config_repository_mismatch')
    if getattr(args, 'bound_id', None) not in (None, config['repo']['id']):
        raise Refusal('launcher_identity_mismatch')
    if digest(original) != args.expect_config:
        raise Refusal('stale_write: ' + CONFIG)
    for field, actual in {'repo_id': config['repo']['id'], **config['context']}.items():
        if getattr(args, field) != actual:
            raise Refusal('expected_' + field + '_mismatch')
    before = config['vcs']['muse'].get('binding')
    if not before:
        raise Refusal('rebind_requires_existing_muse_binding')
    state = muse_read(root, str(args.muse_python))
    if any(before[k] != state[k] for k in ('repo_id', 'store')):
        raise Refusal('adoption_source_identity_change_refused')
    if (state['branch'], state['head']) != (args.branch, args.base_head):
        raise Refusal('adoption_target_revision_mismatch')
    updated = deepcopy(config)
    updated['vcs']['muse']['binding']['runtime'] = state['runtime']
    updated['runtime'] = v1.runtime()
    payload = v1.encode(updated)
    if normalize(payload, root=root).data != updated:
        raise Refusal('rebind_config_invalid')
    old_launcher = asset_read(root, LAUNCHER)
    if old_launcher != v1.launcher(root, config['repo']['id'], runtime_root=config['runtime']['root']):
        raise Refusal('rebind_custom_launcher_requires_resolution')
    launcher = v1.launcher(root, config['repo']['id'])
    original_lock = asset_read(root, LOCK)
    # Change only the launcher's existing lock row; never refresh unrelated
    # footprint claims or reinterpret owner edits as a new accepted baseline.
    lock = v1.decode(original_lock)
    from cli.product_migration import _lock_entries
    entries = _lock_entries(root, raw=original_lock)
    entry = entries.get(LAUNCHER, {})
    if entry.get('origin', 'kit') != 'kit' or entry.get('sha256') != 'sha256:' + digest(old_launcher):
        raise Refusal('rebind_launcher_footprint_mismatch')
    new_lock = deepcopy(lock)
    for row in new_lock['footprint']:
        if row['path'] == LAUNCHER:
            row['sha256'] = 'sha256:' + digest(launcher)
    new_lock['footprint_digest'] = compute_lock_digest(
        [FootprintEntry(**row) for row in new_lock['footprint']])
    backup = '.overseer/local/rebind-' + digest(original)
    mapping = {backup + '/' + CONFIG: original,
               backup + '/' + LAUNCHER: old_launcher,
               backup + '/' + LOCK: original_lock,
               LAUNCHER: launcher, LOCK: v1.encode(new_lock), CONFIG: payload}
    for path, data in list(mapping.items())[:3]:
        saved = asset_read(root, path, missing=True)
        if saved is not None and saved != data:
            raise Refusal('rebind_backup_mismatch')
    tracked = tracked_bindings(root, updated)
    preservation = args.tracked_bindings == 'preserve'
    allowed = not any(tracked.values()) or preservation
    protected = {row['path']: row for row in inventory(root, config)}
    for path in ('.gitignore', '.museignore', v1.NEXT):
        protected[path] = _snapshot(root, path)
    protected = [row for path, row in sorted(protected.items()) if path not in mapping]
    changes = _updates(root, mapping)
    target = revision(root, updated)
    plan = {'operation': 'same-source-runtime-rebind', 'repository': config['repo'],
            'source_config_sha256': digest(original), 'context': config['context'],
            'branch': target.branch, 'head': target.head,
            'before_binding': before, 'after_binding': updated['vcs']['muse']['binding'],
            'before_runtime': config['runtime'], 'after_runtime': updated['runtime'],
            'normalized_config': updated, 'assets': changes, 'protected': protected,
            'tracked_local': tracked, 'tracked_binding_choice': 'preserve' if preservation else None,
            'next': 'preserved byte-for-byte; operator acceptance and next-write are separate',
            'backup': backup}
    plan_digest = digest(_json(plan))
    expected = {path: _snapshot(root, path) for path in mapping}

    def recheck():
        if (asset_read(root, CONFIG) != original or v1.runtime() != updated['runtime']
                or revision(root, updated) != target or tracked_bindings(root, updated) != tracked):
            raise Refusal('context_changed_before_rebind')
        for row in protected:
            if not _same(root, row):
                raise Refusal('rebind_protected_changed: ' + row['path'])
        for path, row in expected.items():
            # Permit only this plan's partial additive writes on a retry.
            if not _same(root, row) and asset_read(root, path, missing=True) != mapping[path]:
                raise Refusal('stale_write: ' + path)

    recheck()
    if not args.dry_run:
        if not allowed:
            raise Refusal('tracked_local_bindings: choose --tracked-bindings preserve or untrack separately')
        if args.expect_rebind != plan_digest:
            raise Refusal('rebind_plan_digest_mismatch: review --dry-run and supply --expect-rebind')
    changed = apply_mapping(root, mapping, check_context=recheck, dry_run=args.dry_run,
                            recovery=REBIND_RECOVERY.format(backup=backup))
    return {'ok': allowed, 'dry_run': args.dry_run, 'rebind_sha256': plan_digest,
            'plan': plan, 'changed': changed, 'config_sha256': digest(payload)}


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
