"""Additive checkout-local exclusions; never untrack or rewrite user rules."""
from __future__ import annotations

import json
import re
import tomllib

from cli.v1_io import Refusal, digest, read

LOCAL_PATHS = (".overseer/config.yaml", ".overseer/bin/", ".overseer/local/",
               "docs/NEXT.md", ".cursor/")


def local_path(path):
    return any(path == p or (p.endswith("/") and path.startswith(p)) for p in LOCAL_PATHS)


def muse_ignore(raw):
    text = (raw or b"").decode("utf-8")
    try:
        parsed = tomllib.loads(text)
        forced = parsed.get("force_track", {}).get("paths", [])
        if not isinstance(forced, list) or any(not isinstance(p, str) for p in forced):
            raise ValueError()
        if any(local_path(p.lstrip("/")) for p in forced):
            raise Refusal("muse_force_tracks_local_binding")
        sections = [("global", parsed.get("global", {}))]
        domains = parsed.get("domain", {})
        if not isinstance(domains, dict):
            raise ValueError()
        sections.extend(("domain." + name, value) for name, value in domains.items())
        for name, value in sections:
            if not isinstance(value, dict) or not isinstance(value.get("patterns", []), list):
                raise ValueError()
            patterns = value.get("patterns", [])
            if any(not isinstance(p, str) for p in patterns):
                raise ValueError()
            additions = ["/" + p for p in LOCAL_PATHS] + ["/.git/"]
            # A final suffix makes last-rule-wins negations harmless. Preserve
            # all prior text, comments and rule order, even duplicate old rules.
            if patterns[-len(additions):] == additions:
                continue
            table = re.search(r"(?m)^\[" + re.escape(name) + r"\][ \t]*(?:#[^\n]*)?$", text)
            suffix = "\n# Overseer checkout-local bindings (never distribute).\npatterns = [\n" + "".join(
                "    " + json.dumps(p) + ",\n" for p in additions) + "]\n"
            if not table:
                if value:
                    raise Refusal("museignore_layout_unsupported")
                text += ("\n" if text and not text.endswith("\n") else "") + "\n[" + name + "]" + suffix
                continue
            end_table = re.search(r"(?m)^\[", text[table.end():])
            end = table.end() + end_table.start() if end_table else len(text)
            body = text[table.end():end]
            array = re.search(r"(?m)^patterns\s*=\s*\[", body)
            if not array:
                if "patterns" in value:
                    raise Refusal("museignore_layout_unsupported")
                text = text[:end] + suffix + text[end:]
                continue
            # Locate the TOML array end, ignoring comments and quoted strings.
            start = table.end() + array.end()
            quote = None
            comment = False
            escaped = False
            for pos in range(start, end):
                char = text[pos]
                if comment:
                    comment = char != "\n"
                elif quote:
                    if escaped:
                        escaped = False
                    elif char == "\\" and quote == '"':
                        escaped = True
                    elif char == quote:
                        quote = None
                elif char == "#":
                    comment = True
                elif char in "\"'":
                    quote = char
                elif char == "]":
                    # Newline puts any missing comma beyond a trailing comment.
                    insert = ("\n," if patterns else "") + "\n    # Overseer checkout-local bindings.\n"
                    # TOML permits a trailing comma, but not two commas.
                    cleaned = re.sub(r"#[^\n]*", "", text[start:pos]).rstrip()
                    if cleaned.endswith(","):
                        insert = insert.removeprefix("\n,")
                    insert += "".join("    " + json.dumps(p) + ",\n" for p in additions)
                    text = text[:pos] + insert + text[pos:]
                    break
            else:
                raise Refusal("museignore_layout_unsupported")
        updated = tomllib.loads(text)
        # The parser checks our insertion; no existing value may be discarded.
        for name, old in sections:
            new = updated["global"] if name == "global" else updated["domain"][name[7:]]
            if new["patterns"][:len(old.get("patterns", []))] != old.get("patterns", []):
                raise ValueError()
    except (tomllib.TOMLDecodeError, ValueError, TypeError, AttributeError):
        raise Refusal("museignore_invalid_or_unsupported") from None
    return text.encode()


def ignore_assets(root, *, expected=None):
    git_raw = read(root, ".gitignore", missing=True)
    muse_raw = read(root, ".museignore", missing=True)
    if expected is not None:
        expected.update({p: "absent" if data is None else digest(data)
                         for p, data in ((".gitignore", git_raw), (".museignore", muse_raw))})
    old = git_raw or b""
    suffix = b"\n# Overseer checkout-local bindings (never distribute).\n" + "".join(
        "/" + p + "\n" for p in (*LOCAL_PATHS, ".muse/")).encode()
    gitignore = old if old.endswith(suffix) else old + (b"\n" if old and not old.endswith(b"\n") else b"") + suffix
    return {".gitignore": gitignore, ".museignore": muse_ignore(muse_raw)}
