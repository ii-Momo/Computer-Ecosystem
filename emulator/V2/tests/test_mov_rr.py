
import pytest

from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.executor_v2 import step


def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem

def test_mov_rr_ok():
    # MOV_RI R1, 5  : 01 01 00 00 05 00 00 00
    # MOV_RR R2 ,R1 : 02 02 01 00 00 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 02 02 01 00 00 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)

    assert st.halted is False
    assert st.regs[1] == 5
    assert st.regs[2] == 5
    assert st.pc == 0x0010  # PC update: none