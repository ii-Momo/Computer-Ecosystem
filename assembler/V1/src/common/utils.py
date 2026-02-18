from __future__ import annotations

import re

_HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")


def parse_int(text: str) -> int:
    """
    Parse an integer literal.
    Supports:
      - decimal: 123, -5
      - hex: 0x10, -0x20
    """
    s = text.strip()
    if s.startswith("-"):
        return -parse_int(s[1:])
    if _HEX_RE.match(s):
        return int(s, 16)
    return int(s, 10)


def is_identifier(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text))
