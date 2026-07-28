#!/usr/bin/env python3
"""Fixture verify script — always fails."""

import sys


def main() -> int:
    print("intentional failure", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
