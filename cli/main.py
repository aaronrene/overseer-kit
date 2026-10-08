"""Bounded v1 entrypoint. The pre-recovery CLI is historical in legacy_main."""
from cli.v1 import main

if __name__ == "__main__":
    raise SystemExit(main())
