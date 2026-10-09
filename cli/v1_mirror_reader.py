"""Pinned native object reads for offline mirror projection; no native exporter.

The Muse snapshot lacks POSIX metadata. The caller approves executable paths;
this helper refuses symlinks and verifies working bytes/modes against that policy.
All blobs, including excluded ones, must exist and pass native hash validation.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import stat
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cli.v1_io import Refusal, confined, read
from cli.v1_muse_reader import run
from cli.v1_policy import local_path

MAX_BYTES = 32 * 1024 * 1024


def excluded(path):
    parts = path.split('/')
    return (local_path(path) or any(p.lower() in {'.git', '.muse'} for p in parts)
            or any(p == '.env' or p.startswith('.env.') for p in parts)
            or path == '.overseer/.muse-bridge-sentinel')


def projection(root, executables):
    state = run(root, False)  # Installs the R1 side-effect assertion and pins APIs.
    from muse.core.commits import read_commit
    from muse.core.snapshots import read_snapshot
    from muse.core.object_store import read_object
    store = Path(state['store'])
    for path in ('.muse/bridge-hooks.toml', '.muse/hooks'):
        if (store / path).exists() or (store / path).is_symlink():
            raise Refusal('inherited_muse_hooks: ' + path)
    if state['head'] == 'unborn':
        raise Refusal('mirror_source_unborn')
    stage = read(store, '.muse/code/stage.json', missing=True)
    if stage and json.loads(stage).get('entries'):
        raise Refusal('mirror_source_staged')
    commit = read_commit(store, state['head'])
    snapshot = read_snapshot(store, commit.snapshot_id)
    result, omitted, total = {}, [], 0
    for path, oid in sorted(snapshot.manifest.items()):
        if (not path or path != Path(path).as_posix() or Path(path).is_absolute()
                or any(p in {'', '.', '..'} for p in path.split('/'))
                or any(ord(c) < 32 for c in path) or '\\' in path):
            raise Refusal('mirror_snapshot_path_invalid')
        data = read_object(store, oid)
        if data is None:
            raise Refusal('mirror_blob_missing: ' + path)
        total += len(data)
        if total > MAX_BYTES:
            raise Refusal('mirror_projection_too_large')
        if excluded(path):
            omitted.append(path)
            continue
        file = confined(root, path)
        mode = 0o755 if path in executables else 0o644
        actual = stat.S_IMODE(file.stat().st_mode)
        if actual & 0o7000 or bool(actual & 0o111) != (path in executables):
            raise Refusal('mirror_mode_mismatch: ' + path)
        if file.read_bytes() != data:
            raise Refusal('mirror_source_working_drift: ' + path)
        result[path] = {'data': base64.b64encode(data).decode(), 'mode': format(mode | stat.S_IFREG, 'o')}
    if set(executables) - result.keys():
        raise Refusal('mirror_executable_not_projected')
    if run(root, False) != state:
        raise Refusal('mirror_source_changed')
    return {'state': state, 'files': result, 'excluded': omitted,
            'directories_omitted': snapshot.directories}


if __name__ == '__main__':
    try:
        print(json.dumps(projection(Path(sys.argv[1]), json.loads(sys.argv[2]))))
    except Exception as exc:
        # R1's bounded process reader intentionally discards stderr. Return only
        # a bounded diagnostic (never object bytes) through its structured channel.
        print(json.dumps({'error': (str(exc) if isinstance(exc, Refusal) else type(exc).__name__)[:300]}))
        raise SystemExit(2)
