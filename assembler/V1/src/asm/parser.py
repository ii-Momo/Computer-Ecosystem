from __future__ import annotations

from typing import List, Optional

from .ast import Instruction, LabelRef, Line, Number, Operand, Register
from .diagnostics import AsmError
from .isa import INSTRUCTIONS
from .lexer import Token
from ..common.utils import parse_int


class _TokStream:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i]

    def pop(self) -> Token:
        t = self.tokens[self.i]
        self.i += 1
        return t

    def match(self, kind: str) -> Optional[Token]:
        if self.peek().kind == kind:
            return self.pop()
        return None


def parse(tokens: List[Token]) -> List[Line]:
    ts = _TokStream(tokens)
    lines: List[Line] = []

    while True:
        if ts.peek().kind == "EOF":
            break

        if ts.match("EOL"):
            lines.append(Line(label=None, label_pos=None, instr=None))
            continue

        label = None
        label_pos = None

        # label?
        if ts.peek().kind == "IDENT":
            t_ident = ts.pop()
            if ts.match("COLON"):
                label = t_ident.text
                label_pos = t_ident.pos
            else:
                ts.i -= 1  # rewind

        instr = None
        if ts.peek().kind == "IDENT":
            m = ts.pop()
            mnemonic = m.text
            if mnemonic not in INSTRUCTIONS:
                raise AsmError(m.pos, "E_UNKNOWN_MNEMONIC", f"Unknown mnemonic: {mnemonic}")
            operands: List[Operand] = []
            if ts.peek().kind not in ("EOL", "EOF"):
                operands.append(_parse_operand(ts))
                while ts.match("COMMA"):
                    operands.append(_parse_operand(ts))
            instr = Instruction(mnemonic=mnemonic, operands=operands, pos=m.pos)

        # end of line
        if ts.peek().kind == "EOL":
            ts.pop()
        elif ts.peek().kind == "EOF":
            pass
        else:
            bad = ts.peek()
            raise AsmError(bad.pos, "E_TRAILING_TOKENS", f"Unexpected token: {bad.kind} ({bad.text})")

        lines.append(Line(label=label, label_pos=label_pos, instr=instr))
    #debug print : print(lines)
    return lines


def _parse_operand(ts: _TokStream) -> Operand:
    t = ts.peek()
    if t.kind == "REG":
        tok = ts.pop()
        return Register(index=int(tok.text[1:]), pos=tok.pos)
    if t.kind == "NUMBER":
        tok = ts.pop()
        try:
            val = parse_int(tok.text)
        except Exception:
            raise AsmError(tok.pos, "E_BAD_NUMBER", f"Invalid number: {tok.text}")
        return Number(value=val, pos=tok.pos)
    if t.kind == "IDENT":
        tok = ts.pop()
        return LabelRef(name=tok.text, pos=tok.pos)
    raise AsmError(t.pos, "E_BAD_OPERAND", f"Expected register/number/label, got {t.kind}")
