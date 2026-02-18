import pytest

from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.executor_v1 import step


def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem

def test_demo_1():
    program_hex = (
        "01 01 00 00 05 00 00 00"
        "01 02 00 00 0a 00 00 00"
        "10 03 01 02 00 00 00 00"
        "00 00 00 00 00 00 00 00"
    )

    mem = make_mem(bytes.fromhex(program_hex))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    step(st, mem)
    step(st, mem)
    step(st, mem)

    assert st.halted is True
    assert st.regs[1] == 5
    assert st.regs[3] == 15
    assert st.regs[2] == 10
    assert st.halt_reason == HaltReason.NORMAL