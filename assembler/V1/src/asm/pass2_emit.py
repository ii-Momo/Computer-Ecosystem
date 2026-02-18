from __future__ import annotations

from typing import Dict, List

from .ast import Instruction, LabelRef, Line, Number, Operand, Register
from .diagnostics import AsmError
from .encoding import encode_instr
from .isa import INSTRUCTIONS
from .pass1_symbols import INSTR_SIZE


def assemble_to_bytes(lines: List[Line], symtab: Dict[str, int], *, base: int = 0) -> bytes:
    out = bytearray()
    pc = base

    for ln in lines:
        if ln.instr is None:
            continue

        spec = INSTRUCTIONS[ln.instr.mnemonic]
        rd = ra = rb = 0
        imm = 0

        operands = ln.instr.operands
        expected = spec.schema
        if len(operands) != len(expected):
            raise AsmError(
                ln.instr.pos,
                "E_ARITY",
                f"{ln.instr.mnemonic} expects {len(expected)} operand(s), got {len(operands)}",
            )

        for kind, op in zip(expected, operands):
            if kind == "rd":
                rd = _expect_reg(op, ln.instr)
            elif kind == "ra":
                ra = _expect_reg(op, ln.instr)
            elif kind == "rb":
                rb = _expect_reg(op, ln.instr)
            elif kind in ("imm32", "addr_abs"):
                imm = _resolve_imm32(op, symtab, ln.instr)
            elif kind == "addr_rel":
                imm = _resolve_imm32(op, symtab, ln.instr) #addr_abs and addr_rel are the same when it comes to assembling
            else:
                raise AsmError(ln.instr.pos, "E_INTERNAL", f"Unknown schema kind: {kind}")

        if spec.rd_must_be_zero and rd != 0:
            raise AsmError(ln.instr.pos, "E_FIELD_NONZERO", "rd must be zero for this instruction")
        if spec.ra_must_be_zero and ra != 0:
            raise AsmError(ln.instr.pos, "E_FIELD_NONZERO", "ra must be zero for this instruction")
        if spec.rb_must_be_zero and rb != 0:
            raise AsmError(ln.instr.pos, "E_FIELD_NONZERO", "rb must be zero for this instruction")
        if spec.imm_must_be_zero and imm != 0:
            raise AsmError(ln.instr.pos, "E_FIELD_NONZERO", "imm32 must be zero for this instruction")

        try:
            out += encode_instr(spec.opcode, rd, ra, rb, imm)
        except ValueError as e:
            raise AsmError(ln.instr.pos, "E_RANGE", str(e))

        pc += INSTR_SIZE

    return bytes(out)


def _expect_reg(op: Operand, instr: Instruction) -> int:
    if isinstance(op, Register):
        if not (0 <= op.index <= 15):
            raise AsmError(op.pos, "E_BAD_REG", f"Register out of range: R{op.index}")
        return op.index
    raise AsmError(getattr(op, "pos", instr.pos), "E_BAD_OPERAND", "Expected register operand")


def _resolve_imm32(op: Operand, symtab: Dict[str, int], instr: Instruction) -> int:
    if isinstance(op, Number):
        return op.value
    if isinstance(op, LabelRef):
        if op.name not in symtab:
            raise AsmError(op.pos, "E_UNDEF_LABEL", f"Undefined label: {op.name}")
        return symtab[op.name]
    raise AsmError(getattr(op, "pos", instr.pos), "E_BAD_OPERAND", "Expected number or label operand")
