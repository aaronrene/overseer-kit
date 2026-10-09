"""Ephemeral Git credential helper: one approved GitHub HTTPS repository only.

Invoked by isolated Git, never as a user-facing token command. Store/erase are
deliberate no-ops. gh output is held in memory and returned only on Git's pipe.
"""
from pathlib import Path
import os
import re
import subprocess
import sys


def main():
    if len(sys.argv) != 4:
        return 1
    gh, repository, operation = sys.argv[1:]
    if operation in ('store', 'erase'):
        return 0
    path = Path(gh)
    if (operation != 'get' or not path.is_absolute() or path.resolve() != path
            or any(p.is_symlink() for p in (path, *path.parents))
            or not path.is_file() or not os.access(path, os.X_OK)
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', repository)):
        return 1
    raw = sys.stdin.buffer.read(16385)
    if len(raw) > 16384:
        return 1
    fields = {}
    for row in raw.decode('utf-8', errors='strict').splitlines():
        if not row:
            continue
        key, sep, value = row.partition('=')
        if not sep or key in fields or key not in ('protocol', 'host', 'path', 'username'):
            return 1
        fields[key] = value
    if any(fields.get(k) != v for k, v in
           {'protocol': 'https', 'host': 'github.com', 'path': repository + '.git'}.items()):
        return 1
    environment = {k: v for k, v in os.environ.items() if k not in ('GH_DEBUG', 'GH_HOST')}
    environment.update(GH_HOST='github.com', GH_PROMPT_DISABLED='1')
    proc = subprocess.run([gh, 'auth', 'token', '--hostname', 'github.com'],
                          env=environment, capture_output=True, timeout=15)
    token = proc.stdout.strip()
    if proc.returncode or not token or len(token) > 4096 or any(c < 33 or c > 126 for c in token):
        return 1
    sys.stdout.buffer.write(b'username=x-access-token\npassword=' + token + b'\n\n')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError):
        # Never echo credential subprocess output or input fields on failure.
        raise SystemExit(1) from None
