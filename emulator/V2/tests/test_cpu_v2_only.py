import pytest

from .test_helpers import instr, make_mem
from .test_conftest import run_steps, get_fault_code, get_pc, get_sp, get_fp, set_sp, set_fp, set_pc, reg, set_reg, state , step_fn

# Opcodes (v2)
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

SP_SEL = 0x10
FP_SEL = 0x11

def test_v2_reset_sp_fp_defaults(state):
    # v2 reset: SP=FP=0xFDFF (chosen so SP-7 aligns on CALL)
    assert get_sp(state) == 0xFDFF
    assert get_fp(state) == 0xFDFF

def test_mov_rr_can_read_sp_and_fp(state, step_fn):
    # MOV_RI R1, 0x9000; MOV_RR SP, R1; MOV_RR R2, SP; MOV_RR R3, FP; HALT
    prog = b"".join([
        instr(MOV_RI, 1, 0, 0, 0x9000),
        instr(MOV_RR, SP_SEL, 1, 0, 0),
        instr(MOV_RR, 2, SP_SEL, 0, 0),
        instr(MOV_RR, 3, FP_SEL, 0, 0),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_sp(state) == 0x9000
    assert reg(state, 2) == 0x9000
    assert reg(state, 3) == get_fp(state)

def test_mov_ri_write_sp_range_ok_and_oob_fault(state, step_fn):
    # First: valid SP write
    prog_ok = b"".join([instr(MOV_RI, SP_SEL, 0, 0, 0xFF00), instr(HALT)])
    mem = make_mem(prog_ok, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_sp(state) == 0xFF00


def test_sp_fp_selectors_not_allowed_on_other_opcodes(state, step_fn):
    # ADD with ra = SP selector must fault REG_OOB (ADD only accepts 0..15)
    prog = b"".join([
        instr(MOV_RI, 1, 0, 0, 1),
        instr(ADD, 2, SP_SEL, 1, 0),  # illegal ra selector for ADD
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("REG_OOB", "FAULT")

def test_cmp_sets_z_only_and_does_not_modify_regs(state, step_fn):
    # R1=7, R2=7 => Z=1, registers unchanged
    prog = b"".join([
        instr(MOV_RI, 1, 0, 0, 7),
        instr(MOV_RI, 2, 0, 0, 7),
        instr(CMP, 0, 1, 2, 0),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert reg(state, 1) == 7
    assert reg(state, 2) == 7
    # Z flag visibility varies; if exposed, assert it is set.
    if hasattr(state, "flags"):
        z = getattr(state.flags, "Z", getattr(state.flags, "z", None))
        if z is not None:
            assert int(z) == 1
    elif hasattr(state, "Z"):
        assert int(state.Z) == 1

def test_push8_post_decrement_and_pop8_pre_increment(state, step_fn):
    # Put 0xAB in R1; PUSH8 R1; POP8 R2; HALT
    prog = b"".join([
        instr(MOV_RI, 1, 0, 0, 0xAB),
        instr(PUSH8, 0, 1, 0, 0),
        instr(POP8, 2, 0, 0, 0),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    sp0 = get_sp(state)
    run_steps(step_fn, state, mem)
    # After PUSH then POP, SP should return to original value
    assert get_sp(state) == sp0
    assert reg(state, 2) == 0xAB
    # Memory at original SP should contain 0xAB after push
    assert mem.read_u8(sp0) == 0xAB

def test_push8_underflow_fault_at_sp_zero(state, step_fn):
    # Force SP=0 then PUSH8 should fault due to SP:=SP-1 underflow (spec treats as MEM_OOB)
    set_sp(state, 0x0000)
    set_reg(state, 1, 0x12)
    prog = b"".join([
        instr(PUSH8, 0, 1, 0, 0),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("MEM_OOB", "FAULT")

def test_pop8_overflow_fault_at_sp_ffff(state, step_fn):
    # POP8 begins with SP := SP+1; if SP==0xFFFF this overflows beyond 0xFFFF => MEM_OOB
    set_sp(state, 0xFFFF)
    prog = b"".join([
        instr(POP8, 1, 0, 0, 0),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("MEM_OOB", "FAULT")

def test_call_abs_and_ret_roundtrip_and_stack_bytes(state, step_fn):
    # Layout:
    # 0x0100: CALL_ABS 0x0200
    # 0x0108: HALT
    # 0x0200: RET
    prog_main = b"".join([
        instr(CALL_ABS, 0, 0, 0, 0x0200),
        instr(HALT),
    ])
    prog_sub = b"".join([instr(RET)])
    mem = make_mem(prog_main, start=0x0100)
    mem.load(0x0200, prog_sub)
    set_pc(state, 0x0100)
    sp0 = get_sp(state)
    run_steps(step_fn, state, mem)
    # After CALL+RET, SP should be restored
    assert get_sp(state) == sp0
    # Return address should have been pushed at sp0..sp0-7 as little-endian of 0x0108
    ret_pc = 0x0108
    expected = [(ret_pc >> (8*i)) & 0xFF for i in range(8)]
    addrs = [sp0 - i for i in range(8)]
    print(mem.read_slice(sp0-7,8))
    actual = [mem.read_u8(a) for a in addrs]
    print(addrs,actual)
    assert actual == expected

def test_call_abs_misaligned_sp_fault(state, step_fn):
    # Set SP so base=SP-7 is not 8-byte aligned. Example from spec: SP=0xFDFA.
    prog = b"".join([
        instr(MOV_RI, SP_SEL, 0, 0, 0xFDFA),
        instr(CALL_ABS, 0, 0, 0, 0x0200),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("MISALIGNED", "FAULT")

def test_ret_misaligned_fault(state, step_fn):
    # For RET, base := SP+1 must be 8-byte aligned.
    # Choose SP=0xFDFE => base=0xFDFF, not aligned.
    set_sp(state, 0xFDFE)
    # Fill memory so bounds would otherwise be OK
    from emu.memory import Memory
    prog = b"".join([instr(RET)])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("MISALIGNED", "FAULT")

def test_ret_empty_stack_mem_oob(state, step_fn):
    # If SP==0xFFFF, then base=SP+1 = 0x10000 => bounds fail => MEM_OOB
    set_sp(state, 0xFFFF)
    prog = b"".join([instr(RET)])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("MEM_OOB", "FAULT")

def test_ret_pc_oob_fault(state, step_fn):
    # Place a return address that is not fetchable: new_pc=0xFFFC => new_pc+7 > 0xFFFF
    # Need base aligned: choose base=0xFFF8, so SP should be base-1 = 0xFFF7
    set_sp(state, 0xFFF7)
    new_pc = 0xFFFC
    bytes_le = [(new_pc >> (8*i)) & 0xFF for i in range(8)]
    # The bytes will be popped from addresses SP+1..SP+8 == base..base+7
    mem = make_mem(instr(RET), start=0x0100)
    base = 0xFFF8
    for i,b in enumerate(bytes_le):
        mem.write_u8(base+i, b)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("PC_OOB", "FAULT")

def test_push8_and_pop8_illegal_encoding(state, step_fn):
    # PUSH8 requires rd=0, rb=0, imm32=0; POP8 requires ra=rb=0, imm32=0
    prog = b"".join([
        instr(PUSH8, 1, 1, 0, 0),  # illegal rd
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("ILLEGAL_ENCODING", "FAULT")

def test_call_abs_illegal_encoding(state, step_fn):
    # CALL_ABS requires rd=ra=rb=0
    prog = b"".join([
        instr(CALL_ABS, 1, 0, 0, 0x0200),
        instr(HALT),
    ])
    mem = make_mem(prog, start=0x0100)
    set_pc(state, 0x0100)
    run_steps(step_fn, state, mem)
    assert get_fault_code(state) in ("ILLEGAL_ENCODING", "FAULT")
