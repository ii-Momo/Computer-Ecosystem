from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .faults import FaultInfo


class HaltReason(str, Enum):
    NONE = "NONE"
    NORMAL = "NORMAL"
    FAULT = "FAULT"


@dataclass(slots=True)
class CPUState:
    # v1: 16 x 64-bit GPRs, PC, Z flag, halted state, fault info.
    regs: List[int] = field(default_factory=lambda: [0] * 16)
    pc: int = 0x0000
    z: bool = False

    halted: bool = False
    halt_reason: HaltReason = HaltReason.NONE
    fault_info: Optional[FaultInfo] = None


def reset_state() -> CPUState:
    """Reset convention for v1 (PC=0, Z=0, regs cleared, not halted)."""
    return CPUState()
