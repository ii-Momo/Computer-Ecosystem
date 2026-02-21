"""EMU package (CPU v1 starter)."""

from .test_conftest import run_steps, get_fault_code, get_pc, get_sp, get_fp, set_sp, set_fp, set_pc, reg, set_reg
from .test_helpers import instr, make_mem

__all__ = [
    "run_steps", "get_fault_code", "get_pc", "get_sp", "get_fp", "set_sp", "set_fp", "set_pc", "reg", "set_reg","instr", "make_mem",
]
