"""Unit tests for footprint_digest algorithm (§K4.7)."""

from __future__ import annotations

from cli.digest import (
    FootprintRecord,
    canonical_bytes,
    compute_footprint_digest,
    sha256_hex,
)


def test_deterministic_digest() -> None:
    records = [
        FootprintRecord("docs/A.md", sha256_hex(b"alpha\n")),
        FootprintRecord("docs/B.md", sha256_hex(b"beta\n")),
    ]
    d1 = compute_footprint_digest(records)
    d2 = compute_footprint_digest(list(reversed(records)))
    assert d1 == d2
    assert d1.startswith("sha256:")


def test_sort_order_independence() -> None:
    a = FootprintRecord("a.txt", sha256_hex(b"x"))
    b = FootprintRecord("b.txt", sha256_hex(b"y"))
    assert compute_footprint_digest([a, b]) == compute_footprint_digest([b, a])


def test_crlf_normalization_equality() -> None:
    assert sha256_hex(b"a\r\nb\n") == sha256_hex(b"a\nb\n")


def test_empty_footprint_digest() -> None:
    digest = compute_footprint_digest([])
    assert digest == "sha256:" + __import__("hashlib").sha256(b"").hexdigest()


def test_single_byte_change_flips_digest() -> None:
    r1 = [FootprintRecord("f.txt", sha256_hex(b"same"))]
    r2 = [FootprintRecord("f.txt", sha256_hex(b"same!"))]
    assert compute_footprint_digest(r1) != compute_footprint_digest(r2)


def test_trailing_newlines_preserved() -> None:
    assert sha256_hex(b"line\n") != sha256_hex(b"line\n\n")
    assert canonical_bytes(b"x\r\n") == b"x\n"
