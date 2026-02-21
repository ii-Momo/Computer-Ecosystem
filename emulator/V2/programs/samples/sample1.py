#import pytest

#path_to_be_configured
from emu.cpu_state import reset_state, HaltReason
from emu.memory import Memory
from emu.executor_v1 import step


def make_mem(program: bytes, start: int = 0x0000) -> Memory:
    mem = Memory.blank()
    mem.load(start, program)
    return mem


def test_full_program_all_opcodes():
    # Program uses ALL opcodes and follows a meaningful flow:
    # 0x0000: MOV_RI R1, 10                 : 01 01 00 00 0A 00 00 00
    # 0x0008: MOV_RI R2, 3                  : 01 02 00 00 03 00 00 00
    # 0x0010: ADD   R3, R1, R2              : 10 03 01 02 00 00 00 00
    # 0x0018: STORE8_ABS [0x0100], R3       : 21 00 03 00 00 01 00 00
    # 0x0020: LOAD8_ABS  R4, [0x0100]       : 20 04 00 00 00 01 00 00
    # 0x0028: SUB   R5, R4, R3              : 11 05 04 03 00 00 00 00
    # 0x0030: JZ_ABS 0x0040                 : 32 00 00 00 40 00 00 00
    # 0x0038: MOV_RI R0, 123  (skipped)     : 01 00 00 00 7B 00 00 00
    # 0x0040: MOV_RR R6, R5                 : 02 06 05 00 00 00 00 00
    # 0x0048: JZ_REL +16  (to 0x0058)       : 33 00 00 00 10 00 00 00
    # 0x0050: MOV_RI R0, 77   (skipped)     : 01 00 00 00 4D 00 00 00
    # 0x0058: JMP_REL +16 (to 0x0068)       : 31 00 00 00 10 00 00 00
    # 0x0060: MOV_RI R0, 88   (skipped)     : 01 00 00 00 58 00 00 00
    # 0x0068: JMP_ABS 0x0078                : 30 00 00 00 78 00 00 00
    # 0x0070: MOV_RI R0, 99   (skipped)     : 01 00 00 00 63 00 00 00
    # 0x0078: HALT                          : 00 00 00 00 00 00 00 00

    program_hex = (
        "01 01 00 00 0A 00 00 00 "
        "01 02 00 00 03 00 00 00 "
        "10 03 01 02 00 00 00 00 "
        "21 00 03 00 00 01 00 00 "
        "20 04 00 00 00 01 00 00 "
        "11 05 04 03 00 00 00 00 "
        "32 00 00 00 40 00 00 00 "
        "01 00 00 00 7B 00 00 00 "
        "02 06 05 00 00 00 00 00 "
        "33 00 00 00 10 00 00 00 "
        "01 00 00 00 4D 00 00 00 "
        "31 00 00 00 10 00 00 00 "
        "01 00 00 00 58 00 00 00 "
        "30 00 00 00 78 00 00 00 "
        "01 00 00 00 63 00 00 00 "
        "00 00 00 00 00 00 00 00"
    )

    mem = make_mem(bytes.fromhex(program_hex))
    st = reset_state()
    st.pc = 0x0000

    # Step through until HALT (max bound to avoid infinite loops if buggy)
    for _ in range(32):
        step(st, mem)

    assert st.halted is True
    assert st.halt_reason == HaltReason.NORMAL
    assert st.pc == 0x0078  # HALT does not advance PC

    # Core expected results:
    assert st.regs[1] == 10
    assert st.regs[2] == 3
    assert st.regs[3] == 13
    assert mem.read_u8(0x0100) == 13
    assert st.regs[4] == 13  # loaded byte
    assert st.regs[5] == 0   # 13-13 -> 0 (Z should be 1 after SUB in typical v1)
    assert st.regs[6] == 0   # MOV_RR copied R5
    # All skipped MOV_RI to R0 should not have executed:
    assert st.regs[0] == 0
