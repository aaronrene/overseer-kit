"""RC13 reader API compatibility under the read-only audit hook.

Requires --muse-python. Does not open Knowtation, Muse 108, or Born Free.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import textwrap
from pathlib import Path

from cli.v1_revision import MUSE_RUNTIMES


def test_reader_imports_eight_apis_under_readonly_hook(tmp_path, muse_runtime):
    """Import the eight reader Muse names under readonly; hash_file matches blob."""
    assert muse_runtime.version == '0.2.1rc13'
    assert muse_runtime.sha256 == MUSE_RUNTIMES['0.2.1rc13']

    kit_root = Path(__file__).resolve().parents[2]
    sample = tmp_path / 'sample.txt'
    sample.write_bytes(b'hello\n')

    child = textwrap.dedent(r'''
        import hashlib
        import json
        import sys
        from pathlib import Path

        kit_root = Path(sys.argv[1])
        sample = Path(sys.argv[2])
        sys.path.insert(0, str(kit_root))
        from cli.v1_muse_reader import readonly
        sys.addaudithook(readonly)

        from muse.core.commits import read_commit
        from muse.core.snapshots import read_snapshot
        from muse.core.validation import validate_branch_name
        from muse.core.ignore import resolve_patterns, is_ignored
        from muse.core.snapshot import _BUILTIN_SECRET_PATTERNS
        from muse.core.types import hash_file
        from muse.plugins.code.plugin import _ALWAYS_IGNORE_DIRS

        assert callable(read_commit)
        assert callable(read_snapshot)
        assert callable(validate_branch_name)
        assert callable(resolve_patterns)
        assert callable(is_ignored)
        assert callable(hash_file)
        assert validate_branch_name('main') == 'main'
        raised = False
        try:
            validate_branch_name('bad name')
        except Exception:
            raised = True
        assert raised
        assert resolve_patterns({}, 'code') == []
        assert is_ignored('a.py', []) is False
        assert isinstance(_BUILTIN_SECRET_PATTERNS, list)
        assert '.env' in _BUILTIN_SECRET_PATTERNS
        assert isinstance(_ALWAYS_IGNORE_DIRS, frozenset)
        assert '.git' in _ALWAYS_IGNORE_DIRS and '.muse' in _ALWAYS_IGNORE_DIRS
        expected = 'sha256:' + hashlib.sha256(b'blob 6\0' + b'hello\n').hexdigest()
        assert hash_file(sample) == expected
        print(json.dumps({
            'ok': True,
            'hash_file': hash_file(sample),
            'expected': expected,
        }))
    ''')

    result = subprocess.run(
        [str(muse_runtime.python), '-I', '-B', '-c', child, str(kit_root), str(sample)],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload['ok'] is True
    expected = 'sha256:' + hashlib.sha256(b'blob 6\0' + b'hello\n').hexdigest()
    assert payload['hash_file'] == expected
    assert payload['expected'] == expected
    assert sample.read_bytes() == b'hello\n'
    sample.unlink()
