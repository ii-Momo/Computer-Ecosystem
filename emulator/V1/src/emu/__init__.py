"""EMU package (CPU v1 starter)."""

from .cpu_state import CPUState, FaultInfo, HaltReason, reset_state
from .memory import Memory
from .decoder import DecodedInstr, decode_instruction
from .executor_v1 import step

__all__ = [
    "CPUState",
    "FaultInfo",
    "HaltReason",
    "reset_state",
    "Memory",
    "DecodedInstr",
    "decode_instruction",
    "step",
]
