"""Bounded offline import of reviewed legacy history into a new owned mirror.

Only complete SHA-1 v2 bundles with exactly the two destination refs are accepted.
No Git config, hooks, remote, worktree or refs are imported from another directory.
"""
import base64
import os
from pathlib import Path
import re
import stat

from cli.v1_io import Refusal, digest

BUNDLE_LIMIT = 128 * 1024 * 1024
SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def validate(plan):
    from cli.v1 import keys
    from cli.v1_mirror import HEX, physical
    r = plan['reconciliation']
    keys(r, ('bundle', 'bundle_sha256', 'mirror_head', 'base_head', 'delta'))
    physical(r['bundle'])
    if (not SHA256.fullmatch(r['bundle_sha256']) or not HEX.fullmatch(r['mirror_head'])
            or not HEX.fullmatch(r['base_head']) or r['mirror_head'] == r['base_head']):
        raise Refusal('mirror_reconciliation_identity_invalid')
    if plan['expected_target'] == 'absent' and (
            plan['destination']['expected_head'] != r['mirror_head']
            or plan['destination'].get('expected_base', r['base_head']) != r['base_head']):
        raise Refusal('mirror_reconciliation_head_mismatch')
    if not isinstance(r['delta'], dict):
        raise Refusal('mirror_reconciliation_delta_invalid')
    for path, entry in r['delta'].items():
        if (not isinstance(path, str) or not path or path.startswith('/')
                or any(p in ('', '.', '..') for p in path.split('/')) or '\0' in path):
            raise Refusal('mirror_reconciliation_path_invalid')
        keys(entry, ('before', 'after', 'mode_before', 'mode_after'))
        for side in ('before', 'after'):
            value, mode = entry[side], entry['mode_' + side]
            if (value is None and mode is not None) or (value is not None and
                    (not isinstance(value, str) or not SHA256.fullmatch(value)
                     or mode not in ('100644', '100755'))):
                raise Refusal('mirror_reconciliation_delta_invalid')
        if entry['before'] is None and entry['after'] is None:
            raise Refusal('mirror_reconciliation_delta_invalid')


def bundle_bytes(plan):
    from cli.v1_mirror import physical
    r = plan['reconciliation']
    path = physical(r['bundle'])
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                or info.st_mode & 0o7111 or info.st_size > BUNDLE_LIMIT):
            raise Refusal('mirror_history_bundle_not_regular')
        raw = stream.read(BUNDLE_LIMIT + 1)
    if len(raw) > BUNDLE_LIMIT or digest(raw) != r['bundle_sha256']:
        raise Refusal('mirror_history_bundle_digest_mismatch')
    header, separator, pack = raw.partition(b'\n\n')
    dest = plan['destination']
    expected = {f'{r["mirror_head"]} refs/heads/{dest["branch"]}'.encode(),
                f'{r["base_head"]} refs/heads/{dest["base"]}'.encode()}
    lines = header.split(b'\n')
    if (not separator or lines[0] != b'# v2 git bundle' or len(lines) != 3
            or set(lines[1:]) != expected or not pack.startswith(b'PACK')):
        raise Refusal('mirror_history_bundle_refs_or_prerequisites')
    return pack


def import_history(target, plan, files):
    from cli.v1_mirror import git
    # Unpack directly into loose objects: no imported config, refs, packs or
    # alternates. Git checks the pack and object structure before installation.
    git(target, 'unpack-objects', '-r', '--strict', data=bundle_bytes(plan))
    verify_history(target, plan, files)
    r = plan['reconciliation']
    reachable = {row.split(b' ', 1)[0] for row in git(
        target, 'rev-list', '--objects', r['mirror_head'], r['base_head']).splitlines()}
    actual = set(git(target, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname)').splitlines())
    if reachable != actual:
        raise Refusal('mirror_history_unrelated_objects')


def manifest(target, commit):
    from cli.v1_mirror import git
    result = {}
    for row in git(target, 'ls-tree', '-r', '-z', commit).split(b'\0'):
        if not row:
            continue
        meta, path = row.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise Refusal('mirror_history_tree_unsupported')
        result[path.decode()] = {'sha256': digest(git(target, 'cat-file', 'blob', oid)), 'mode': mode}
    return result


def delta(before, after):
    return {p: {'before': before[p]['sha256'] if p in before else None,
                'after': after[p]['sha256'] if p in after else None,
                'mode_before': before[p]['mode'] if p in before else None,
                'mode_after': after[p]['mode'] if p in after else None}
            for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)}


def verify_history(target, plan, files):
    from cli.v1_mirror import git, HEX
    r = plan['reconciliation']
    parents = [r['mirror_head'], r['base_head']]
    for parent in parents:
        if git(target, 'cat-file', '-t', parent) != b'commit\n':
            raise Refusal('mirror_history_head_not_commit')
    git(target, 'fsck', '--strict', '--no-reflogs', '--no-dangling', *parents)
    common = git(target, 'merge-base', *parents, optional=True).decode().strip()
    if not HEX.fullmatch(common):
        raise Refusal('mirror_history_unrelated_heads')
    trees = [git(target, 'rev-parse', p + '^{tree}') for p in parents]
    if trees[0] != trees[1]:
        raise Refusal('mirror_history_base_tree_differs')
    after = {p: {'sha256': digest(base64.b64decode(item['data'], validate=True)), 'mode': item['mode']}
             for p, item in files.items()}
    if delta(manifest(target, parents[0]), after) != r['delta']:
        raise Refusal('mirror_reconciliation_delta_mismatch')
