
from __future__ import annotations
from dataclasses import dataclass

def enc_u32_le(x:int) -> bytes:
    x &= 0xFFFFFFFF
    return bytes([x & 0xFF, (x>>8)&0xFF, (x>>16)&0xFF, (x>>24)&0xFF])

def instr(op:int, rd:int=0, ra:int=0, rb:int=0, imm32:int=0) -> bytes:
    return bytes([op & 0xFF, rd & 0xFF, ra & 0xFF, rb & 0xFF]) + enc_u32_le(imm32)

def make_mem(program: bytes, start: int = 0x0000):
    from emu.memory import Memory
    mem = Memory.blank()
    mem.load(start, program)
    return mem
