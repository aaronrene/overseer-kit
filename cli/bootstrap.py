"""Isolated source bootstrap; never discover another checkout or a PATH Python."""
from pathlib import Path
import sys


def run() -> int:
    if not sys.flags.isolated:
        print("refused: launch with cli/ok (isolated Python required)", file=sys.stderr)
        return 2
    root = Path(__file__).resolve().parent.parent
    # A normal venv executable may be a symlink. Its prefix, not its inode, binds it.
    if Path(sys.prefix).resolve() != root / ".venv":
        print("refused: runtime_environment_mismatch", file=sys.stderr)
        return 2
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    import cli
    if Path(cli.__file__).resolve() != root / "cli/__init__.py":
        print("refused: import_origin_mismatch", file=sys.stderr)
        return 2
    try:
        from cli.v1 import main
    except ModuleNotFoundError:
        print("refused: install requirements-v1.txt into this installation's .venv", file=sys.stderr)
        return 2
    if Path(sys.modules["cli.v1"].__file__).resolve() != root / "cli/v1.py":
        print("refused: import_origin_mismatch", file=sys.stderr)
        return 2
    return main()


if __name__ == "__main__":
    raise SystemExit(run())
