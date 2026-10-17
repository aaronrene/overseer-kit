"""Request-local guards for retained engines, never a second CLI entrypoint.

ContextVar keeps concurrent app requests separate. Production callers enter with
an already validated context; engine-only tests may still inject dependencies.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import fcntl
import os
from pathlib import Path

from cli.v1_io import Refusal, atomic, confined, digest, read as _read, LIMIT

ENGINE_LIMIT = 16 * 1024 * 1024


def read(root, relative, **kwargs):
    return _read(root, relative, limit=LIMIT if relative in ('docs/NEXT.md', '.overseer/config.yaml') else ENGINE_LIMIT, **kwargs)

ACTIVE = ContextVar('overseer_product_request', default=None)


@dataclass
class EngineBoundary:
    context: object
    args: object
    model: object
    writable: bool
    snapshots: dict = field(default_factory=dict)

    def recheck(self):
        self.context.recheck(self.args)

    def relative(self, path):
        path = Path(path)
        if not path.is_absolute():
            path = self.context.root / path
        try:
            relative = path.relative_to(self.context.root).as_posix()
        except ValueError:
            raise Refusal('engine_path_outside_repository') from None
        confined(self.context.root, relative, missing_parents=True)
        return relative

    def watch(self, path):
        relative = self.relative(path)
        if relative not in self.snapshots:
            data = read(self.context.root, relative, missing=True)
            self.snapshots[relative] = 'absent' if data is None else digest(data)
        return self.context.root / relative

    def write(self, path, data):
        from cli import v1
        if not self.writable:
            raise Refusal('read_only_engine_request')
        relative = self.relative(path)
        if relative in (v1.NEXT, v1.CONFIG) or relative.startswith(('.git/', '.muse/')):
            raise Refusal('engine_cannot_publish_binding_or_next')
        self.watch(path)
        self.recheck()
        target = self.context.root / relative
        mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
        atomic(self.context.root, relative, data, expected=self.snapshots[relative],
               mode=mode, before_replace=self.recheck, limit=ENGINE_LIMIT)
        self.snapshots[relative] = digest(data)


@contextmanager
def engine_boundary(context, args, *, writable=False):
    from cli.product_config import normalize
    boundary = EngineBoundary(context, args, normalize(context.original, root=context.root), writable)
    # Serialize engine read/modify/write operations, then capture their inputs.
    fd = None
    if writable:
        fd = os.open(context.root / '.overseer', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        fcntl.flock(fd, fcntl.LOCK_EX)
    token = ACTIVE.set(boundary)
    try:
        boundary.recheck()
        yield boundary
        boundary.recheck()
    finally:
        ACTIVE.reset(token)
        if fd is not None:
            os.close(fd)


def active():
    return ACTIVE.get()


def watch(path):
    boundary = active()
    return boundary.watch(path) if boundary else path
