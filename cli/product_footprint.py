"""Full owned footprint records; existing preserved entries remain authoritative.

Living documents and assets use migration's asset bound; config and NEXT keep
the smaller bound through the same bounded reader.
"""
from cli import v1
from cli.v1_io import digest


def with_lock(root, mapping, config, *, preserved=()):
    from cli.product_migration import LOCK, _lock_entries, _document_paths, read
    from cli.version_lock import FootprintEntry, compute_lock_digest
    entries = _lock_entries(root)
    raw = read(root, LOCK, missing=True)
    old = v1.decode(raw) if raw else {}
    living = _document_paths(config)
    for path, data in mapping.items():
        if path in (LOCK, v1.CONFIG, v1.NEXT):
            continue
        origin = 'preserved' if path in living else 'kit'
        entries[path] = dict(path=path, source='bound-product-assets',
                             sha256='sha256:' + digest(data), origin=origin)
    for path in set(preserved) | living:
        if path == v1.NEXT:
            continue
        data = read(root, path, missing=True)
        if data is not None:
            entries[path] = dict(path=path, source=entries.get(path, {}).get('source', 'consumer'),
                                sha256='sha256:' + digest(data), origin='preserved')
    rows = [entries[path] for path in sorted(entries)]
    lock = dict(lock_version=1, kit_version=v1.runtime()['version'], config_version=3,
                installed_at=old.get('installed_at', 'unrecorded'),
                synced_at=old.get('synced_at', 'unrecorded'),
                footprint_digest=compute_lock_digest([FootprintEntry(**row) for row in rows]),
                footprint=rows)
    # No fabricated installation timestamp; existing timestamps are retained.
    return {**mapping, LOCK: v1.encode(lock)}
