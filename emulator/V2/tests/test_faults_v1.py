import pytest

from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.faults import FaultCode
from emu.executor_v2 import step

def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem

def test_illeagle_incoding():
    # HALT          : 00 00 00 00 00 00 00 01
    mem = make_mem(bytes.fromhex("00 00 00 00 00 00 00 01"))
    st = reset_state()
    st.pc = 0x0000
    
    step(st, mem)
    assert st.halted == True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info.code == FaultCode.ILLEGAL_ENCODING
def test_reg_oob():
    # MOV_RI R18 , 5          : 01 12 00 00 05 00 00 00, 
    mem = make_mem(bytes.fromhex("01 12 00 00 05 00 00 00"))
    st = reset_state()
    st.pc = 0x0000
    
    step(st, mem)
    assert st.halted == True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info.code == FaultCode.REG_OOB
def test_mem_oob():
    # MOV_RI R1, 5          : 01 01 00 00 05 00 00 00
    # STORE8_ABS [0x10000],R1: 21 00 01 00 00 00 01 00
    mem = make_mem(bytes.fromhex("01 01 00 00 05 00 00 00 21 00 01 00 00 00 01 00"))
    st = reset_state()
    st.pc = 0x0000
    
    step(st, mem)
    step(st, mem)
    assert st.halted == True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info.code == FaultCode.MEM_OOB

def test_pc_oob():
    # JMP_ABS 0x10000        : 30 00 00 00 00 00 01 00
    mem = make_mem(bytes.fromhex("30 00 00 00 00 00 01 00"))
    st = reset_state()
    st.pc = 0x0000
    
    step(st, mem)
    assert st.halted == True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info.code == FaultCode.PC_OOB

def test_misaligned1():
    # JMP_ABS 0x0203        : 30 00 00 00 03 20 00 00
    mem = make_mem(bytes.fromhex("30 00 00 00 03 20 00 00"))
    st = reset_state()
    st.pc = 0x0000
    
    step(st, mem)
    assert st.halted == True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info.code == FaultCode.MISALIGNED
def test_misaligned2():
    # JZ_ABS 0x0001       :32 00 00 00 01 00 00 00
    mem = make_mem(bytes.fromhex("32 00 00 00 01 00 00 00"))
    st = reset_state()
    st.pc = 0x0000
    st.z = True
    
    step(st, mem)
    assert st.halted == False
    assert st.pc == 0x0001
    step(st , mem)
    assert st.halted == True
    assert st.halt_reason == HaltReason.FAULT
    assert st.fault_info.code == FaultCode.MISALIGNED