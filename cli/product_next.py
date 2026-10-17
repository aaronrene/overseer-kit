"""Schema-3 lane collection in the sole canonical NEXT file and CAS writer."""
from __future__ import annotations

import argparse
import re
from cli.v1_io import Refusal, digest, read

COMMON = ('schema', 'repo_id', 'repo_root', 'vcs', 'source_id', 'entries')
ENTRY = ('branch', 'base_head', 'model', 'action_id', 'action_kind', 'prompt_sha256')
DELIMITER = re.compile(r'(?m)^<!-- overseer-next:([A-Za-z0-9][A-Za-z0-9_.-]{0,127}) -->\n')


def parse_collection(data):
    from cli import v1
    try:
        text = data.decode('utf-8')
    except UnicodeError:
        raise Refusal('next_encoding_invalid') from None
    if not text.startswith('---\n') or '\r' in text:
        return None
    parts = text[4:].split('\n---\n', 1)
    if len(parts) != 2:
        return None
    meta = v1.decode(parts[0].encode())
    if not isinstance(meta, dict) or meta.get('schema') != 3:
        return None
    v1.keys(meta, COMMON)
    if type(meta['schema']) is not int or meta['vcs'] not in ('git', 'muse'):
        raise Refusal('next_version_invalid')
    if meta['vcs'] == 'git' and meta['source_id'] is not None:
        raise Refusal('next_revision_kind_invalid')
    if meta['vcs'] == 'muse':
        from cli.v1_revision import OID
        if not isinstance(meta['source_id'], str) or not OID.fullmatch(meta['source_id']):
            raise Refusal('next_source_id_invalid')
    v1.label(meta['repo_id']); v1.label(meta['repo_root'])
    entries = meta['entries']
    if not isinstance(entries, dict) or not entries or len(entries) > 64:
        raise Refusal('next_entries_invalid')
    bodies = {}
    matches = list(DELIMITER.finditer(parts[1]))
    if not matches or matches[0].start() != 0:
        raise Refusal('next_lane_bodies_invalid')
    for i, match in enumerate(matches):
        lane = match[1]
        if lane in bodies:
            raise Refusal('next_duplicate_lane_body')
        bodies[lane] = parts[1][match.end():matches[i+1].start() if i+1 < len(matches) else None]
    if set(bodies) != set(entries):
        raise Refusal('next_lane_map_body_mismatch')
    for lane, entry in entries.items():
        v1.token(lane); v1.keys(entry, ENTRY)
        single = {k: meta[k] for k in ('repo_id', 'repo_root', 'vcs', 'source_id')}
        single.update(entry, schema=2, lane=lane)
        # One strict validator for single-entry metadata and prompt text.
        v1.parse_next(b'---\n' + v1.encode(single) + b'---\n' + bodies[lane].encode())
    return meta, bodies


def selected_lane(config, args):
    lane = getattr(args, 'lane', None)
    lanes = config['docs']['lanes']
    if lane is None:
        if len(lanes) != 1:
            raise Refusal('next_lane_selection_required')
        lane = config['context']['lane']
    if lane not in lanes:
        raise Refusal('next_lane_mismatch')
    if lanes[lane]['repo_id'] != config['repo']['id']:
        raise Refusal('next_lane_owner_mismatch')
    return lane


def selected_entry(meta, prompt, config, args):
    lane = selected_lane(config, args)
    if meta['schema'] != 3:
        return meta, prompt
    if set(meta['entries']) - set(config['docs']['lanes']):
        raise Refusal('next_undeclared_lane')
    if lane not in meta['entries']:
        raise Refusal('next_lane_missing: ' + lane)
    entry = {k: meta[k] for k in ('repo_id', 'repo_root', 'vcs', 'source_id')}
    entry.update(meta['entries'][lane], schema=3, lane=lane)
    return entry, prompt[lane]


def publication(root, config, meta, prompt, expected, *, reset=False, previous_data=None):
    from cli import v1
    v1.validate_prompt(prompt)
    if DELIMITER.search(prompt):
        raise Refusal('prompt_contains_lane_delimiter')
    old = previous_data if previous_data is not None else read(root, v1.NEXT, missing=True)
    if ('absent' if old is None else digest(old)) != expected:
        raise Refusal('stale_write: ' + v1.NEXT)
    prior = v1.parse_next(old) if old is not None else None
    multi = len(config['docs']['lanes']) > 1 or (prior and prior[0]['schema'] == 3)
    if not multi:
        return b'---\n' + v1.encode(meta) + b'---\n' + prompt.encode()
    common = {'schema': 3, 'repo_id': meta['repo_id'], 'repo_root': meta['repo_root'],
              'vcs': meta.get('vcs', 'git'), 'source_id': meta.get('source_id'), 'entries': {}}
    bodies = {}
    if prior:
        previous, body = prior
        if any(previous[k] != common[k] for k in ('repo_id', 'repo_root')):
            raise Refusal('next_collection_repository_mismatch')
        changed_authority = any(previous.get(k, 'git' if k == 'vcs' else None) != common[k]
                                for k in ('vcs', 'source_id'))
        if changed_authority:
            if not reset:
                raise Refusal('next_collection_binding_change_requires_explicit_reset')
            previous = dict(common)
            body = {}
        elif reset:
            raise Refusal('next_reset_requires_authority_change')
        if previous['schema'] == 3:
            common['entries'].update(previous['entries']); bodies.update(body)
        else:
            common['entries'][previous['lane']] = {k: previous[k] for k in ENTRY}
            bodies[previous['lane']] = body
    common['entries'][meta['lane']] = {k: meta[k] for k in ENTRY}
    bodies[meta['lane']] = prompt
    return b'---\n' + v1.encode(common) + b'---\n' + ''.join(
        '<!-- overseer-next:' + lane + ' -->\n' + bodies[lane]
        for lane in sorted(bodies)).encode()


def display(root, config, data, args, context):
    from cli import v1
    # Always validate the entire syntax/digest collection, including unselected lanes.
    v1.parse_next(data)
    if len(config['docs']['lanes']) == 1:
        meta, prompt = v1.validate_next(root, config, data, args, context=context)
        return {'next': meta, 'prompt': prompt}, v1.rendered(meta, prompt)
    lanes = {}
    for lane in config['docs']['lanes']:
        selection = argparse.Namespace(lane=lane)
        try:
            meta, prompt = v1.validate_next(root, config, data, selection, context=context)
            lanes[lane] = {'ok': True, 'next': meta, 'prompt': prompt}
        except Refusal as exc:
            lanes[lane] = {'ok': False, 'error': str(exc)}
    multiple = len(lanes) > 1
    selected = getattr(args, 'lane', None)
    all_lanes = getattr(args, 'all_lanes', False)
    if selected and all_lanes:
        raise Refusal('next_lane_and_all_lanes_conflict')
    if multiple and (selected is None or all_lanes):
        if any(getattr(args, k, None) is not None for k in
               ('branch', 'model', 'action_id', 'action_kind')):
            raise Refusal('next_lane_selection_required')
        if getattr(args, 'expect_next', None) not in (None, digest(data)):
            raise Refusal('next_digest_mismatch')
        if getattr(args, 'repo_id', None) not in (None, config['repo']['id']):
            raise Refusal('expected_repo_id_mismatch')
        lines = ['Repository lanes — select --lane L before action.\n']
        for lane, item in lanes.items():
            lines.append(lane + ': ' + ('valid' if item['ok'] else 'REFUSED ' + item['error']) + '\n')
            if item['ok']:
                lines.append(v1.rendered(item['next'], item['prompt']))
        return {'lanes': lanes, 'selection_required': True}, ''.join(lines)
    meta, prompt = v1.validate_next(root, config, data, args, context=context)
    output = v1.rendered(meta, prompt)
    if multiple:
        output += '\nOther repository lanes:\n' + ''.join(
            lane + ': ' + ('valid' if item['ok'] else 'REFUSED ' + item['error']) + '\n'
            for lane, item in lanes.items() if lane != selected)
    return {'next': meta, 'prompt': prompt, 'lanes': lanes}, output


def batch_publication(root, config, args, expected, context):
    """Build selected entries; publication still uses v1's one confined writer."""
    import json
    from cli import v1
    from cli.v1_revision import unique_json
    request = json.loads(read(root, args.batch_file), object_pairs_hook=unique_json)
    v1.keys(request, ('lanes',))
    entries = request['lanes']
    if not isinstance(entries, dict) or not entries or len(entries) > 64:
        raise Refusal('next_batch_entries_invalid')
    payload = read(root, v1.NEXT, missing=True)
    actual = 'absent' if payload is None else digest(payload)
    if actual != expected:
        raise Refusal('stale_write: ' + v1.NEXT)
    if context['vcs'] == 'muse' and (args.vcs != 'muse' or args.base_head != context['head']):
        raise Refusal('muse_writer_requires_explicit_vcs_and_base_head')
    if args.vcs not in (None, context['vcs']) or args.base_head not in (None, context['head']):
        raise Refusal('next_batch_revision_mismatch')
    for index, (lane, entry) in enumerate(entries.items()):
        v1.keys(entry, ('model', 'action_id', 'action_kind', 'prompt'))
        selection = argparse.Namespace(**vars(args))
        selection.lane = lane
        for key in ('model', 'action_id', 'action_kind'):
            setattr(selection, key, entry[key])
        selection.expect_next = None
        selected_lane(config, selection)
        prompt = entry['prompt']
        if not isinstance(prompt, str):
            raise Refusal('prompt_invalid')
        if not prompt.endswith('\n'):
            prompt += '\n'
        meta = {'schema': 2, 'repo_id': config['repo']['id'], 'repo_root': str(root),
                'branch': context['branch'], 'base_head': context['head'], 'lane': lane,
                'vcs': context['vcs'], 'source_id': context['source_id'],
                'model': entry['model'], 'action_id': entry['action_id'],
                'action_kind': entry['action_kind'], 'prompt_sha256': digest(prompt.encode())}
        v1.check_expectations(meta, selection)
        payload = publication(root, config, meta, prompt, actual,
                              reset=args.reset_authority and index == 0, previous_data=payload)
        v1.validate_next(root, config, payload, selection, context=context, freshness=False)
        actual = digest(payload)
    return payload
