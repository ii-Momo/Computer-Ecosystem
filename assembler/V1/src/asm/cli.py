from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .assembler import assemble_text
from .diagnostics import AsmError


def _parse_base(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s, 10)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="asm", description="v1 two-pass assembler (.asm -> flat .bin)")
    p.add_argument("input", help="Input .asm file")
    p.add_argument("-o", "--output", required=True, help="Output .bin file")
    p.add_argument("--base", default="0x0000", help="Base load address (default 0x0000)")
    args = p.parse_args(argv)

    in_path = Path(args.input)
    out_path = Path(args.output)
    base = _parse_base(args.base)

    try:
        text = in_path.read_text(encoding="utf-8")
        res = assemble_text(text, file=str(in_path), base=base)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(res.binary)
    except AsmError as e:
        print(str(e), file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"{in_path}: E_NOFILE: input file not found", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
