from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DecodedInstr:
    opcode: int
    rd: int
    ra: int
    rb: int
    imm32: int  # signed 32-bit sign-extended to Python int


def decode_instruction(instr8: bytes) -> DecodedInstr:
    """Decode 8-byte instruction: [opc, rd, ra, rb, imm32(le)]."""
    if len(instr8) != 8:
        raise ValueError("expected exactly 8 bytes")
    opcode = instr8[0]
    rd = instr8[1]
    ra = instr8[2]
    rb = instr8[3]
    imm32 = int.from_bytes(instr8[4:8], byteorder="little", signed=True)
    return DecodedInstr(opcode=opcode, rd=rd, ra=ra, rb=rb, imm32=imm32)
