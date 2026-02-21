import pytest

from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.executor_v2 import step

def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem

def test_sotre8_ok():
    # MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # STORE8_ABS [0x0200],R1: 21 00 01 00 00 02 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 21 00 01 00 00 02 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)

    assert st.halted is False
    assert st.regs[1] == 5
    assert mem.read_u8(0x0200) == 5
    assert st.pc == 0x0010  # PC update: none

def test_load8_ok():
    # MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # STORE8_ABS [0x0200],R1: 21 00 01 00 00 02 00 00
    # LOAD8_ABS R1,[0x0200] : 20 01 00 00 00 02 00 00 
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 21 00 01 00 00 02 00 00 20 01 00 00 00 02 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)
    step(st, mem)

    assert st.halted is False
    assert st.regs[1] == 5
    assert mem.read_u8(0x0200) == 5
    assert st.pc == 0x0018  # PC update: none
