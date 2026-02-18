from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_bin


def _parse_base(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s, 10)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="loadbin", description="Load a flat .bin into memory at base address")
    p.add_argument("binary", help="Input .bin file")
    p.add_argument("--base", default="0x0000", help="Base address to load at (default 0x0000)")
    p.add_argument("--emit-mem", default=None, help="Optional: write a memory image file (zeros up to end)")
    args = p.parse_args(argv)

    base = _parse_base(args.base)
    data, rep = load_bin(args.binary, base=base)

    print(f"Loaded: {rep.path}")
    print(f"Base:   0x{rep.base:04X}")
    print(f"Size:   {rep.size} bytes")
    print(f"End:    0x{rep.end:04X}")

    if args.emit_mem:
        out = bytearray(b"\x00" * rep.base) + data
        Path(args.emit_mem).write_bytes(bytes(out))
        print(f"Wrote memory image: {args.emit_mem} ({len(out)} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
