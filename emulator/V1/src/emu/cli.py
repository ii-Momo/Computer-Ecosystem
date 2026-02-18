# src/emu/cli.py
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Tuple

from .cpu_state import reset_state
from .decoder import decode_instruction
from .executor_v1 import step
from .memory import MEM_SIZE, Memory


def _parse_int(x: str) -> int:
    """
    Parse an int in decimal or hex.
    Examples: 123, 0x7B
    """
    x = x.strip().lower()
    return int(x, 0)


def _read_program_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) == 0:
        raise ValueError(f"Program file is empty: {path}")
    return data


def _read_program_hex(hex_str: str) -> bytes:
    """
    Read a program from a hex string. Spaces are allowed.
    Example: "01 01 00 00 05 00 00 00 00 00 00 00 00 00 00 00"
    """
    s = "".join(hex_str.split())
    if len(s) % 2 != 0:
        raise ValueError("Hex string has odd length (missing a nibble).")
    return bytes.fromhex(s)


def _hexdump(blob: bytes, start_addr: int = 0, width: int = 16) -> str:
    lines = []
    for i in range(0, len(blob), width):
        chunk = blob[i : i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"{start_addr + i:04X}  {hex_part:<{width*3}}  {ascii_part}")
    return "\n".join(lines)


def _dump_regs(regs: list[int]) -> str:
    # Display as 64-bit hex (masked)
    out = []
    for i in range(0, len(regs), 4):
        chunk = regs[i : i + 4]
        out.append(
            "  ".join(f"R{(i+j):02d}={chunk[j] & 0xFFFFFFFFFFFFFFFF:016X}" for j in range(len(chunk)))
        )
    return "\n".join(out)


def _decode_at(mem: Memory, pc: int) -> Tuple[bytes, str]:
    instr = mem.read_slice(pc, 8)
    ins = decode_instruction(instr)
    # A compact decode string; you can expand this as your ISA grows.
    s = f"opc=0x{ins.opcode:02X} rd={ins.rd} ra={ins.ra} rb={ins.rb} imm32={ins.imm32}"
    return instr, s


def run_program(
    program: bytes,
    start: int,
    max_steps: int,
    trace: bool,
    dump_regs_end: bool,
    dump_mem: Optional[Tuple[int, int]],
) -> int:
    """
    Returns exit code: 0 on normal halt, 1 on fault, 2 on max-steps exceeded.
    """
    if start < 0 or start >= MEM_SIZE:
        raise ValueError(f"--start out of range: {start:#x}")

    mem = Memory.blank()
    mem.load(start, program)

    st = reset_state()
    st.pc = start

    steps = 0
    while not st.halted and steps < max_steps:
        if trace:
            try:
                raw, decoded = _decode_at(mem, st.pc)
                raw_hex = " ".join(f"{b:02X}" for b in raw)
                print(f"{steps:06d} PC={st.pc:04X}  {raw_hex}   {decoded}  Z={int(st.z)}")
            except Exception as e:
                print(f"{steps:06d} PC={st.pc:04X}  <decode failed: {e}>")

        step(st, mem)
        steps += 1

    if not st.halted:
        print(f"[STOP] Max steps exceeded ({max_steps}).")
        if dump_regs_end:
            print("\n[REGS]\n" + _dump_regs(st.regs))
        return 2

    if st.fault_info is not None:
        print("[HALT] Fault.")
        fi = st.fault_info
        # Print fault fields in a readable way
        print(
            f"  code={fi.code} pc=0x{fi.pc:04X} opcode=0x{fi.opcode:02X} "
            f"rd={fi.rd} ra={fi.ra} rb={fi.rb} imm32={fi.imm32} msg={fi.message!r}"
        )
        if dump_regs_end:
            print("\n[REGS]\n" + _dump_regs(st.regs))
        if dump_mem is not None:
            addr, size = dump_mem
            blob = mem.read_slice(addr, size)
            print(f"\n[MEM 0x{addr:04X}..0x{addr+size-1:04X}]\n{_hexdump(blob, start_addr=addr)}")
        return 1

    print(f"[HALT] Normal. PC=0x{st.pc:04X} steps={steps} Z={int(st.z)}")
    if dump_regs_end:
        print("\n[REGS]\n" + _dump_regs(st.regs))
    if dump_mem is not None:
        addr, size = dump_mem
        blob = mem.read_slice(addr, size)
        print(f"\n[MEM 0x{addr:04X}..0x{addr+size-1:04X}]\n{_hexdump(blob, start_addr=addr)}")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="emu-cli",
        description="CPU v1 Emulator CLI (Section 03).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run a binary program in memory.")
    run_src = run.add_mutually_exclusive_group(required=True)
    run_src.add_argument("--bin", type=Path, help="Path to raw binary program.")
    run_src.add_argument("--hex", type=str, help="Program bytes as hex string (spaces allowed).")

    run.add_argument("--start", type=_parse_int, default=0x0000, help="Load/PC start address (default 0x0000).")
    run.add_argument("--max-steps", type=int, default=100000, help="Stop after N steps to avoid infinite loops.")
    run.add_argument("--trace", action="store_true", help="Print trace line for each executed instruction.")
    run.add_argument("--dump-regs", action="store_true", help="Print registers at the end.")
    run.add_argument(
        "--dump-mem",
        nargs=2,
        metavar=("ADDR", "SIZE"),
        help="Dump memory range at the end (ADDR and SIZE in dec or hex). Example: --dump-mem 0x0100 64",
    )

    hd = sub.add_parser("hexdump", help="Hexdump a binary file (useful for debugging).")
    hd.add_argument("--bin", type=Path, required=True, help="Path to raw binary program.")
    hd.add_argument("--start", type=_parse_int, default=0x0000, help="Address label for hexdump (default 0x0000).")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.cmd == "hexdump":
        blob = _read_program_bytes(args.bin)
        print(_hexdump(blob, start_addr=args.start))
        return 0

    if args.cmd == "run":
        if args.bin is not None:
            program = _read_program_bytes(args.bin)
        else:
            program = _read_program_hex(args.hex)

        dump_mem = None
        if args.dump_mem is not None:
            addr = _parse_int(args.dump_mem[0])
            size = _parse_int(args.dump_mem[1])
            if size <= 0:
                raise ValueError("SIZE must be > 0")
            if addr < 0 or addr + size - 1 >= MEM_SIZE:
                raise ValueError("dump range out of memory bounds")
            dump_mem = (addr, size)

        return run_program(
            program=program,
            start=args.start,
            max_steps=args.max_steps,
            trace=args.trace,
            dump_regs_end=args.dump_regs,
            dump_mem=dump_mem,
        )

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
