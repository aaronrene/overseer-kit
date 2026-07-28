#!/usr/bin/env python3
"""Fixture verify script — passes with artifact hash line."""

import sys


def main() -> int:
    print("checks ok")
    print("ARTIFACT_SHA256=AbCdEf0123456789")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
