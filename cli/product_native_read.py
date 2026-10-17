"""Pinned, read-only native reference/path query used by product observations."""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cli.v1_muse_reader import run
from cli.v1_io import read, Refusal, confined


def query(root, ref, paths):
    state = run(root, False)
    from muse.core.validation import validate_branch_name
    from muse.core.commits import read_commit
    from muse.core.snapshots import read_snapshot
    from muse.core.object_store import read_object
    validate_branch_name(ref)
    store = Path(state['store'])
    ref_path = '.muse/refs/heads/' + ref
    raw = read(store, ref_path, missing=True)
    revision = raw.decode().strip() if raw else None
    snapshot = None
    if revision:
        commit = read_commit(store, revision)
        snapshot = read_snapshot(store, commit.snapshot_id) if commit else None
        if snapshot is None:
            raise Refusal('native_reference_objects_missing')
    rows = []
    for path in paths:
        confined(root, path, missing_parents=True)
        oid = snapshot.manifest.get(path) if snapshot else None
        data = read_object(store, oid) if oid else None
        local = read(root, path, missing=True)
        sha = hashlib.sha256(data).hexdigest() if data is not None else None
        current = hashlib.sha256(local).hexdigest() if local is not None else None
        rows.append({'path': path, 'mainSha256': sha, 'workingSha256': current,
                     'match': sha is not None and sha == current})
    if read(store, ref_path, missing=True) != raw or run(root, False) != state:
        raise Refusal('native_reference_changed')
    return {'state': state, 'revision': revision, 'paths': rows}


if __name__ == '__main__':
    try:
        print(json.dumps(query(Path(sys.argv[1]), sys.argv[2], json.loads(sys.argv[3]))))
    except Exception as exc:
        print(json.dumps({'error': str(exc) if isinstance(exc, Refusal) else type(exc).__name__}))
        raise SystemExit(2)
