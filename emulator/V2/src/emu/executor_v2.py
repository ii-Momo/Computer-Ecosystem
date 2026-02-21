from __future__ import annotations

from .cpu_state import CPUState, HaltReason
from .decoder import decode_instruction
from .faults import FaultCode, FaultInfo
from .memory import Memory, MEM_SIZE 


# v2 opcode map (subset for starter)
OPC_HALT = 0x00
OPC_MOV_RI = 0x01
OPC_MOV_RR = 0x02
OPC_ADD = 0x10
OPC_SUB = 0x11
OPC_CMP = 0x12
OPC_LOAD8_ABS = 0x20 
OPC_STORE8_ABS = 0x21
OPC_JMP_ABS = 0x30
OPC_JMP_REL = 0x31
OPC_JZ_ABS = 0x32
OPC_JZ_REL = 0x33
OPC_PUSH8 = 0x40
OPC_POP8 = 0x41
OPC_CALL_ABS = 0x42
OPC_RET = 0x43



def _fault(state: CPUState, info: FaultInfo) -> None:
    state.halted = True
    state.halt_reason = HaltReason.FAULT
    state.fault_info = info


def _pc_oob_or_misaligned(state: CPUState, opcode: int = 0, rd: int = 0, ra: int = 0, rb: int = 0, imm32: int = 0) -> None:
    # Fetch rules:
    # - PC+7 must be <= 0xFFFF
    # - PC must be 8-byte aligned
    if state.pc < 0 or state.pc + 7 >= MEM_SIZE:
        _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, opcode, rd, ra, rb, imm32, "PC fetch out of range"))
        return
    if state.pc % 8 != 0:
        _fault(state, FaultInfo(FaultCode.MISALIGNED, state.pc, opcode, rd, ra, rb, imm32, "PC not 8-byte aligned"))
        return


def _default_pc_increment(state: CPUState, opcode: int, rd: int, ra: int, rb: int, imm32: int) -> None:
    next_pc = state.pc + 8
    if next_pc < 0 or next_pc + 7 >= MEM_SIZE:
        _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, opcode, rd, ra, rb, imm32, "next PC out of range"))
        return
    state.pc = next_pc




def step(state: CPUState, mem: Memory) -> None:
    """Execute exactly one v2 instruction (HALT + MOV_RI implemented)."""
    if state.halted:
        return

    _pc_oob_or_misaligned(state)
    if state.halted:
        return

    try:
        instr_bytes = mem.read_slice(state.pc, 8)
    except IndexError:
        _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, 0, 0, 0, 0, 0, "fetch failed"))
        return

    ins = decode_instruction(instr_bytes)

    # Dispatch
    if ins.opcode == OPC_HALT:
        # Must satisfy rd=ra=rb=0 and imm32=0 else ILLEGAL_ENCODING
        if ins.rd != 0 or ins.ra != 0 or ins.rb != 0 or ins.imm32 != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "HALT encoding requires all fields zero"))
            return
        state.halted = True
        state.halt_reason = HaltReason.NORMAL
        # PC update: none
        return

    if ins.opcode == OPC_MOV_RI:
        # Must satisfy ra=0, rb=0 else ILLEGAL_ENCODING
        if ins.ra != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "MOV_RI requires ra=0, rb=0"))
            return
        # Sign-extend imm32 to 64-bit (Python int already signed; mask to 64-bit on write)
        val = ins.imm32 & 0xFFFFFFFFFFFFFFFF
        if ins.rd ==16 :
            if not (0<=state.sp<=0xFFFF):
                _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP out of memory range"))
                return
            state.sp = val
        elif ins.rd ==17 :
            if not (0<=state.fp<=0xFFFF):
                _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "FP out of memory range"))
                return
            state.fp = val
        # v2 register indices are 0..15
        elif not (0 <= ins.rd <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        else:
            state.regs[ins.rd] = val
        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    
    if ins.opcode == OPC_MOV_RR:
        # Must satisfy rb=0, imm32=0 or fault ILLEGAL_ENCODING.
        if ins.rb != 0 or ins.imm32 != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "MOV_RR requires rb=0, imm32=0"))
            return
        # v2 register indices are 0..15
        if ins.rd ==16 :
            if not (0<=state.sp<=0xFFFF):
                _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP out of memory range"))
                return
        elif ins.rd ==17 :
            if not (0<=state.fp<=0xFFFF):
                _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "FP out of memory range"))
                return
        elif not (0 <= ins.rd <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        if ins.ra ==16 :
            if not (0<=state.sp<=0xFFFF):
                _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP out of memory range"))
                return
        elif ins.ra ==17 :
            if not (0<=state.fp<=0xFFFF):
                _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "FP out of memory range"))
                return
        elif not (0 <= ins.ra <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ra out of range for v2"))
            return
        
        if ins.rd == 17:
            if ins.ra == 17:
                state.fp = state.fp
            elif ins.ra == 16:
                state.fp = state.sp
            else :
                state.fp = state.regs[ins.ra]
        elif ins.rd == 16 :
            if ins.ra == 17:
                state.sp = state.fp
            elif ins.ra == 16:
                state.sp = state.sp
            else :
                state.sp = state.regs[ins.ra]
        else:
            if ins.ra == 17:
                state.regs[ins.rd] = state.fp
            elif ins.ra == 16:
                state.regs[ins.rd] = state.sp
            else :
                state.regs[ins.rd] = state.regs[ins.ra]

        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_ADD:
        # Must satisfy imm32=0 or fault ILLEGAL_ENCODING.
        if ins.imm32 != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ADD requires imm32=0"))
            return
        # v2 register indices are 0..15
        if not (0 <= ins.rd <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        if not (0 <= ins.ra <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ra out of range for v2"))
            return
        if not (0 <= ins.rb <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        temp = (state.regs[ins.ra] + state.regs[ins.rb])%(2**64)
        state.regs[ins.rd] = temp
        state.z = temp == 0
        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_SUB:
        # Must satisfy imm32=0 or fault ILLEGAL_ENCODING.
        if ins.imm32 != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SUB requires imm32=0"))
            return
        # v2 register indices are 0..15
        if not (0 <= ins.rd <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        if not (0 <= ins.ra <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ra out of range for v2"))
            return
        if not (0 <= ins.rb <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        temp = (state.regs[ins.ra] - state.regs[ins.rb])%(2**64)
        state.regs[ins.rd] = temp
        state.z = temp == 0
        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_CMP:
        # Must satisfy rd=0, imm32=0 or ILLEGAL_ENCODING.
        if ins.imm32 != 0 or ins.rd !=0 :
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "CMP requires rd=0, imm32=0"))
            return
        # v2 register indices are 0..15
        if not (0 <= ins.ra <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ra out of range for v2"))
            return
        if not (0 <= ins.rb <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        temp = (state.regs[ins.ra] - state.regs[ins.rb])%(2**64)
        state.z = temp == 0
        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
        
    if ins.opcode == OPC_LOAD8_ABS:
        # Must satisfy ra=0, rb=0 or fault ILLEGAL_ENCODING.
        if ins.ra != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "LOAD8_ABS requires ra=0, rb=0"))
            return
        # v2 register indices are 0..15
        if not (0 <= ins.rd <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        if not (0<= ins.imm32 < MEM_SIZE) :
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Address is out of memory range"))
            return
        
        addr = ins.imm32 

        b = mem.read_u8(addr)

        #sign extention !!
        state.regs[ins.rd] = b & 0xFFFFFFFFFFFFFFFF

        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_STORE8_ABS:
        # Must satisfy ra=0, rb=0 or fault ILLEGAL_ENCODING.
        if ins.rd != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "STORE8_ABS requires rd=0, rb=0"))
            return
        # v2 register indices are 0..15
        if not (0 <= ins.ra <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ra out of range for v2"))
            return
        if not (0<= ins.imm32 < MEM_SIZE) :
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Address is out of memory range"))
            return
        addr = ins.imm32 

        mem.write_u8(addr , state.regs[ins.ra] & 0xFF)
        
        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_JMP_ABS:
        # Must satisfy rd=0, ra=0, rb=0 or fault ILLEGAL_ENCODING.
        if ins.rd != 0 or ins.ra != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "JMP_ABS requires rd=0, ra=0, rb=0"))
            return
        #Faults PC_OOB
        if not (0<= ins.imm32 < 0xFFFF) :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Out of PC range"))
            return
        
        target = ins.imm32 

        if target%8 !=0:
            _fault(state,FaultInfo(FaultCode.MISALIGNED, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target is misaligned"))
            return
        if target+7 > 0xFFFF :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target out of range"))
            return
        state.pc = target
        return
    
    if ins.opcode == OPC_JMP_REL:
        # Must satisfy rd=0, ra=0, rb=0 or fault ILLEGAL_ENCODING.
        if ins.rd != 0 or ins.ra != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "JMP_REL requires rd=0, ra=0, rb=0"))
            return
        
        target = state.pc + ins.imm32
        
        if target+7 > 0xFFFF :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target out of range"))
            return
        if not (0 <= target <= 0xFFFF) :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target out of range"))
            return
        if target%8 !=0:
            _fault(state,FaultInfo(FaultCode.MISALIGNED, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target is misaligned"))
            return
        state.pc = target
        return
    if ins.opcode == OPC_JZ_ABS:
        # Must satisfy rd=0, ra=0, rb=0 or fault ILLEGAL_ENCODING.
        if ins.rd != 0 or ins.ra != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "JZ_ABS requires rd=0, ra=0, rb=0"))
            return
        if not (0<= ins.imm32 < 0xFFFF) :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Out of PC range"))
            return
        
        target = ins.imm32 

        if target+7 > 0xFFFF :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target out of range"))
            return
        if state.z :
            state.pc = target
        else:
            _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_JZ_REL:
        # Must satisfy rd=0, ra=0, rb=0 or fault ILLEGAL_ENCODING.
        if ins.rd != 0 or ins.ra != 0 or ins.rb != 0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "JZ_REL requires rd=0, ra=0, rb=0"))
            return
        
        target = state.pc + ins.imm32
        if target+7 > 0xFFFF :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target out of range"))
            return
        if not (0 <= target <= 0xFFFF) :
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "Target out of range"))
            return
        if state.z :
            state.pc = target
        else:
            _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_PUSH8:
        #Must satisfy rd=0, rb=0, imm32=0 or ILLEGAL_ENCODING.
        if ins.rd != 0 or ins.rb != 0 or ins.imm32 !=0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "PUSH8 requires rd=0, rb=0, imm32=0"))
            return
        
        if not (0 <= ins.ra <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "ra out of range for v2"))
            return
        
        if not (0 <= state.sp <= 0xFFFF):
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP out of memory range"))
            return
        if state.sp == 0:
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP underflow"))
            return
        mem.write_u8(state.sp,state.regs[ins.ra] & 0xFF)
        state.sp -=1


        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_POP8:
        #Must satisfy ra=0, rb=0, imm32=0 or ILLEGAL_ENCODING.
        if ins.ra != 0 or ins.rb != 0 or ins.imm32 !=0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "POP8 requires ra=0, rb=0, imm32=0"))
            return
        
        if not (0 <= ins.rd <= 15):
            _fault(state, FaultInfo(FaultCode.REG_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "rd out of range for v2"))
            return
        
        if state.sp == 0xFFFF:
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP overflow"))
            return
        state.sp +=1
        b = mem.read_u8(state.sp)

        #sign extention !!
        state.regs[ins.rd] = b & 0xFFFFFFFFFFFFFFFF


        _default_pc_increment(state, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32)
        return
    if ins.opcode == OPC_CALL_ABS:
        #Must satisfy rd=ra=rb=0 or ILLEGAL_ENCODING.
        if ins.ra != 0 or ins.rb != 0 or ins.rd !=0:
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "CALL_ABS requires rd=0, ra=0, rb=0"))
            return
        if state.pc + 15 > 0xFFFF:
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "PC is our of pc range"))
            return
        base = state.sp -7
        if (base) %8 !=0:
            _fault(state, FaultInfo(FaultCode.MISALIGNED, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP is not aligned"))
            return
        if base <0 or base+7 >0xFFFF:
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP is not in range"))
            return
        return_pc = state.pc+8
        rpc = '0'*(18-len(hex(return_pc))) + hex(return_pc)[2:]
        rpc = rpc[::-1]
        for i in range(8):
            mem.write_u8(state.sp, int(rpc[2*i:2*i+2][::-1],16))
            state.sp -=1

        state.pc = ins.imm32 & 0xFFFF
        return
    if ins.opcode == OPC_RET:
        #Must satisfy rd=ra=rb=0, imm32=0 or ILLEGAL_ENCODING.
        if ins.ra != 0 or ins.rb != 0 or ins.rd !=0 or ins.imm32 !=0 :
            _fault(state, FaultInfo(FaultCode.ILLEGAL_ENCODING, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "RET requires rd=0, ra=0, rb=0, imm32=0"))
            return
        if state.pc + 15 > 0xFFFF:
            _fault(state, FaultInfo(FaultCode.PC_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "PC is our of pc range"))
            return
        base = state.sp +1
        if (base) %8 !=0:
            _fault(state, FaultInfo(FaultCode.MISALIGNED, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP is not aligned"))
            return
        if base <0 or base+7 >0xFFFF:
            _fault(state, FaultInfo(FaultCode.MEM_OOB, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "SP is not in range"))
            return
        new_pc =0
        pc_bytes = mem.read_slice(state.sp+1,8)
        for i in range(len(pc_bytes)):
            new_pc += (256**(7-i))*pc_bytes[i]
        state.sp +=8

        state.pc = new_pc
        return
        
    # Any other opcode is reserved in v2
    _fault(state, FaultInfo(FaultCode.ILLEGAL_OPCODE, state.pc, ins.opcode, ins.rd, ins.ra, ins.rb, ins.imm32, "opcode not defined in v2"))
