"""Argv preprocessing so global flags work before or after subcommands."""

from __future__ import annotations

GLOBAL_OPTIONS: dict[str, int] = {
    "-C": 1,
    "--repo": 1,
    "--config": 1,
    "--json": 0,
    "-q": 0,
    "--quiet": 0,
    "-v": 0,
    "--verbose": 0,
    "--no-color": 0,
}

STANDALONE_GLOBALS = frozenset({"-h", "--help", "--version"})


def extract_global_args(argv: list[str]) -> tuple[list[str], list[str]]:
    """Pull global flags out of ``argv`` regardless of position."""
    global_args: list[str] = []
    rest: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in STANDALONE_GLOBALS:
            global_args.append(token)
            index += 1
            continue
        if token in GLOBAL_OPTIONS:
            global_args.append(token)
            value_count = GLOBAL_OPTIONS[token]
            for _ in range(value_count):
                index += 1
                if index >= len(argv):
                    break
                global_args.append(argv[index])
            index += 1
            continue
        rest.append(token)
        index += 1
    return global_args, rest
