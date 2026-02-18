from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple

OpKind = Literal["rd", "ra", "rb", "imm32", "addr_abs", "addr_rel"]


@dataclass(frozen=True)
class InstrSpec:
    opcode: int
    schema: Tuple[OpKind, ...]
    rd_must_be_zero: bool = False
    ra_must_be_zero: bool = False
    rb_must_be_zero: bool = False
    imm_must_be_zero: bool = False


# IMPORTANT:
# If your emulator already defines opcodes, update these values to match your emulator.
INSTRUCTIONS: Dict[str, InstrSpec] = {
    "MOV_RI":     InstrSpec(0x01, ("rd", "imm32"), ra_must_be_zero=True, rb_must_be_zero=True),
    "MOV_RR":     InstrSpec(0x02, ("rd", "ra"), rb_must_be_zero=True, imm_must_be_zero=True),

    "ADD":        InstrSpec(0x10, ("rd", "ra", "rb"), imm_must_be_zero=True),
    "SUB":        InstrSpec(0x11, ("rd", "ra", "rb"), imm_must_be_zero=True),

    "LOAD8_ABS":  InstrSpec(0x20, ("rd", "addr_abs"), ra_must_be_zero=True, rb_must_be_zero=True),
    "STORE8_ABS": InstrSpec(0x21, ("addr_abs", "ra"), rd_must_be_zero=True, rb_must_be_zero=True),

    "JMP_ABS":    InstrSpec(0x30, ("addr_abs",), rd_must_be_zero=True, ra_must_be_zero=True, rb_must_be_zero=True),
    "JMP_REL":    InstrSpec(0x31, ("addr_rel",), rd_must_be_zero=True, ra_must_be_zero=True, rb_must_be_zero=True),
    "JZ_ABS":     InstrSpec(0x32, ("addr_abs",), rd_must_be_zero=True, ra_must_be_zero=True, rb_must_be_zero=True),
    "JZ_REL":     InstrSpec(0x33, ("addr_rel",), rd_must_be_zero=True, ra_must_be_zero=True, rb_must_be_zero=True),

    "HALT":       InstrSpec(0x00, tuple(), rd_must_be_zero=True, ra_must_be_zero=True, rb_must_be_zero=True, imm_must_be_zero=True),
}
