"""Small confined-file primitives for the trusted-host v1 utility."""
from __future__ import annotations

import errno
import os
from pathlib import Path
import stat
import tempfile

from cli.digest import sha256_hex_raw as digest

LIMIT = 128 * 1024


class Refusal(Exception):
    pass


def confined(root: Path, relative: str, *, parents: bool = False,
             missing_parents: bool = False) -> Path:
    """Reject symlink components and traversal; create only requested directories."""
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(p in (".", "..") for p in rel.parts):
        raise Refusal("path_invalid")
    current = root
    for part in rel.parts[:-1]:
        current /= part
        if parents and not current.exists() and not current.is_symlink():
            current.mkdir()
        if missing_parents and not current.exists() and not current.is_symlink():
            continue
        if current.is_symlink() or not current.is_dir():
            raise Refusal("path_parent_invalid")
    target = current / rel.name
    if target.is_symlink():
        raise Refusal("path_symlink")
    if target.exists():
        st = target.stat()
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise Refusal("path_not_regular")
    return target


def read(root: Path, relative: str, *, missing: bool = False) -> bytes | None:
    path = confined(root, relative, missing_parents=missing)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        if missing:
            return None
        raise Refusal("file_missing: " + relative) from None
    with os.fdopen(fd, "rb") as stream:
        st = os.fstat(stream.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > LIMIT:
            raise Refusal("file_invalid: " + relative)
        data = stream.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise Refusal("file_too_large")
        return data


def atomic(root: Path, relative: str, data: bytes, *, expected: str,
           mode: int = 0o644) -> None:
    """Compare prior bytes; fsync a unique sibling; replace and fsync its directory.

    Caller serialization is deliberately not a security subsystem. The second
    comparison catches ordinary stale writers; malicious same-UID races are out
    of scope. NEXT callers also take a brief advisory directory lock.
    """
    if len(data) > LIMIT:
        raise Refusal("file_too_large")
    path = confined(root, relative, parents=True)

    def compare() -> None:
        old = read(root, relative, missing=True)
        actual = "absent" if old is None else digest(old)
        if expected != actual:
            raise Refusal("stale_write: " + relative)

    compare()
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            os.fchmod(stream.fileno(), mode)
            stream.flush()
            os.fsync(stream.fileno())
        compare()
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            try:
                os.fsync(directory)
            except OSError as exc:
                if exc.errno not in (errno.EINVAL, errno.ENOTSUP):
                    raise
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)
