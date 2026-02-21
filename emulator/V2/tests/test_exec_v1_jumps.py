import pytest

from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.executor_v2 import step

def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem

def test_jmp_abs_ok():
    # 0x0000 MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # 0x0008 JMP_ABS 0x0020        : 30 00 00 00 20 00 00 00
    # 0x0010                       : 00 00 00 00 00 00 00 00
    # 0x0018                       : 00 00 00 00 00 00 00 00
    # 0x0020 MOV_RI R2 , 6         : 01 02 00 00 06 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 30 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 02 00 00 06 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)
    step(st, mem)
    assert st.halted == False
    assert st.regs[2] == 6
    assert st.pc == 0x0028
def test_jmp_rel_ok():
    # 0x0000 MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # 0x0008 JMP_REL 0x0018        : 31 00 00 00 18 00 00 00
    # 0x0010                       : 00 00 00 00 00 00 00 00
    # 0x0018                       : 00 00 00 00 00 00 00 00
    # 0x0020 MOV_RI R2 , 6         : 01 02 00 00 06 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 31 00 00 00 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 02 00 00 06 00 00 00"))
    st = reset_state()
    st.pc = 0x0000

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)
    step(st, mem)
    assert st.halted == False
    assert st.regs[2] == 6
    assert st.pc == 0x0028
def test_jz_abs_ok():
    # 0x0000 MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # 0x0008 JZ_ABS 0x0020         : 32 00 00 00 20 00 00 00
    # 0x0010                       : 00 00 00 00 00 00 00 00
    # 0x0018                       : 00 00 00 00 00 00 00 00
    # 0x0020 MOV_RI R2 , 6         : 01 02 00 00 06 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 32 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 02 00 00 06 00 00 00"))
    st = reset_state()
    st.pc = 0x0000
    st.z = True

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)
    step(st, mem)
    assert st.halted == False
    assert st.regs[2] == 6
    assert st.pc == 0x0028
def test_jz_rel_ok():
    # 0x0000 MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # 0x0008 JZ_REL 0x0018         : 33 00 00 00 18 00 00 00
    # 0x0010                       : 00 00 00 00 00 00 00 00
    # 0x0018                       : 00 00 00 00 00 00 00 00
    # 0x0020 MOV_RI R2 , 6         : 01 02 00 00 06 00 00 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 33 00 00 00 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 02 00 00 06 00 00 00"))
    st = reset_state()
    st.pc = 0x0000
    st.z = True

    step(st, mem)
    assert st.regs[1] == 5
    step(st, mem)
    step(st, mem)
    assert st.halted == False
    assert st.regs[2] == 6
    assert st.pc == 0x0028