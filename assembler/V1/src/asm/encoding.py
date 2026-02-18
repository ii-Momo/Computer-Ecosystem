from __future__ import annotations

import struct


def pack_u8(x: int) -> int:
    if not (0 <= x <= 0xFF):
        raise ValueError(f"u8 out of range: {x}")
    return x


def pack_i32_le(x: int) -> bytes:
    if not (-2**31 <= x <= 2**31 - 1):
        raise ValueError(f"imm32 out of range: {x}")
    return struct.pack("<i", x)


def encode_instr(opcode: int, rd: int, ra: int, rb: int, imm32: int) -> bytes:
    return bytes([pack_u8(opcode), pack_u8(rd), pack_u8(ra), pack_u8(rb)]) + pack_i32_le(imm32)
