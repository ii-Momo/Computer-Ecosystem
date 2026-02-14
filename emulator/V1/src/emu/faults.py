from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FaultCode(str, Enum):
    ILLEGAL_OPCODE = "ILLEGAL_OPCODE"
    ILLEGAL_ENCODING = "ILLEGAL_ENCODING"
    REG_OOB = "REG_OOB"
    MEM_OOB = "MEM_OOB"
    PC_OOB = "PC_OOB"
    MISALIGNED = "MISALIGNED"


@dataclass(slots=True)
class FaultInfo:
    code: FaultCode
    pc: int
    opcode: int
    rd: int
    ra: int
    rb: int
    imm32: int
    message: str = ""
