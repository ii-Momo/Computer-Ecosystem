import pytest

from .test_helpers import instr, make_mem
from .test_conftest import get_fault_code, get_pc, get_sp, get_fp, set_sp, set_fp, set_pc, reg, set_reg
from emu.memory import Memory
from emu.executor_v2 import step
from emu.cpu_state import reset_state,HaltReason


HALT      = 0x00
MOV_RI    = 0x01
MOV_RR    = 0x02
ADD       = 0x10
SUB       = 0x11
CMP       = 0x12
LOAD8_ABS = 0x20
STORE8_ABS= 0x21
JMP_ABS   = 0x30
JMP_REL   = 0x31
JZ_ABS    = 0x32
JZ_REL    = 0x33
PUSH8     = 0x40
POP8      = 0x41
CALL_ABS  = 0x42
RET       = 0x43

SEL_SP = 0x10
SEL_FP = 0x11


def load_program(mem: Memory, start: int, program: bytes) -> None:
    mem.load(start, program)




def test_v2_two_calls_nested_stack_alignment_and_fp_prologue():
    """
    Program layout:
      main @ 0x0100
      f1   @ 0x0200
      f2   @ 0x0300

    main:
      R1 = 7
      R2 = 3
      CALL f1
      STORE8_ABS [0x0400], R0      ; store low byte of result
      HALT

    f1:
      ; exercise PUSH8/POP8 (byte stack traffic)
      PUSH8 R1
      POP8  R3                     ; R3 gets low byte of R1 (7)
      ; compute partial: R0 = R1 + R2
      ADD R0, R1, R2               ; 7 + 3 = 10
      ; nested call
      CALL f2

      RET

    f2:
      ; add 2: R0 = R0 + 2
      MOV_RI R4, 2
      ADD R0, R0, R4               ; 10 + 2 = 12
      RET

    Expectations:
      - program halts normally
      - MEM[0x0400] == 12
      - SP restored to reset value (0xFDFF) after nested calls
      - FP restored to reset value (0xFDFF)
      - R3 == 7 (PUSH8/POP8 correctness)
    """
    mem = Memory.blank()

    MAIN = 0x0100
    F1   = 0x0200
    F2   = 0x0300
    OUT  = 0x0400

    # --- main ---
    main_prog = b"".join([
        instr(MOV_RI, rd=0x01, imm32=7),                 # R1 = 7
        instr(MOV_RI, rd=0x02, imm32=3),                 # R2 = 3
        instr(CALL_ABS, rd=0, ra=0, rb=0, imm32=F1),     # CALL f1 (imm16 in imm32&0xFFFF)
        instr(STORE8_ABS, rd=0, ra=0x00, rb=0, imm32=OUT),  # STORE8_ABS [OUT], R0 (ra=R0)
        instr(HALT, 0, 0, 0, 0),
    ])
    load_program(mem, MAIN, main_prog)

    # --- f1 ---
    f1_prog = b"".join([
        instr(PUSH8,  rd=0,     ra=0x01,   rb=0, imm32=0),    # PUSH8 R1
        instr(POP8,   rd=0x03,  ra=0,      rb=0, imm32=0),    # POP8 R3
        instr(ADD,    rd=0x00,  ra=0x01,   rb=0x02, imm32=0), # R0 = R1 + R2
        instr(CALL_ABS, rd=0, ra=0, rb=0, imm32=F2),          # CALL f2 (nested)
        instr(RET,    0, 0, 0, 0),
    ])
    load_program(mem, F1, f1_prog)

    # --- f2 ---
    f2_prog = b"".join([
        instr(MOV_RI, rd=0x04, imm32=2),                      # R4 = 2
        instr(ADD,    rd=0x00, ra=0x00, rb=0x04, imm32=0),     # R0 = R0 + R4
        instr(RET,    0, 0, 0, 0),
    ])
    load_program(mem, F2, f2_prog)

    # Run from MAIN
    st = reset_state()
    st.pc = MAIN  # if your reset_state already sets PC=0, this forces entry to main

    # Some projects' step() uses global state; some use passed-in state.
    # So we load MAIN into the reset state's PC by temporarily patching reset_state.
    # Simplest: just run with our own loop that starts from a patched state:
    cur = st

    for _ in range(10_000):
        step(cur, mem)  # type: ignore[misc]
        if st.halted:
            break

    # Assert HALT (normal end, not a fault)
    # Many implementations distinguish NORMAL vs FAULT; if yours stores fault_code, you can assert it is None.
    if st.halt_reason is not None:
        print(cur)
        assert st.halt_reason == HaltReason.NORMAL, f"Expected NORMAL halt, got {st.halt_reason}"

    # Check stored output byte
    out_b = mem.read_u8(OUT)
    assert out_b == 12, f"Expected RAM[{hex(OUT)}]=12, got {out_b}"

    # Check PUSH8/POP8 result
    r = cur.regs
    assert r is not None, "Could not find registers array on state (expected st.r / st.R / st.regs)"
    assert int(r[3]) == 7, f"Expected R3=7 after PUSH8/POP8, got {int(r[3])}"

    # Check SP/FP restored (default reset is SP=FP=0xFDFF in v2)
    sp = cur.sp
    fp = cur.fp
    assert sp == 0xFDFF, f"Expected SP restored to 0xFDFF, got {hex(sp)}"
    assert fp == 0xFDFF, f"Expected FP restored to 0xFDFF, got {hex(fp)}"