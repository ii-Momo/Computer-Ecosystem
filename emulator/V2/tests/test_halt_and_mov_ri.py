import pytest

from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.executor_v2 import step


def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem


def test_halt_ok():
    # HALT bytes: 00 00 00 00 00 00 00 00
    mem = make_mem(bytes.fromhex("00 00 00 00 00 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)

    assert st.halted is True
    assert st.halt_reason == HaltReason.NORMAL
    assert st.pc == 0x0000  # PC update: none


def test_mov_ri_r1_5():
    # MOV_RI R1, 5: 01 01 00 00 05 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)

    assert st.halted is False
    assert st.regs[1] == 5
    assert st.pc == 0x0008


def test_halt_illegal_encoding_faults():
    # HALT with rd != 0 => ILLEGAL_ENCODING fault
    mem = make_mem(bytes.fromhex("00 01 00 00 00 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)

    assert st.halted is True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info is not None
    assert st.fault_info.code.value == "ILLEGAL_ENCODING"

def test_mov_ri_multiple():
    # MOV_RI R1, 5: 01 01 00 00 05 00 00 00
    # MOV_RI R2, 5: 01 02 00 00 05 00 00 00
    # MOV_RI R3, 5: 01 03 00 00 05 00 00 00
    # MOV_RI R4, 5: 01 04 00 00 05 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 01 02 00 00 05 00 00 00 01 03 00 00 05 00 00 00 01 04 00 00 05 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    step(st, mem)
    step(st, mem)
    step(st, mem)

    assert st.halted is False
    assert st.regs[1] == 5
    assert st.regs[2] == 5
    assert st.regs[3] == 5
    assert st.regs[4] == 5
    assert st.pc == 0x0020