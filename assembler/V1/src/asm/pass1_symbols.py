from __future__ import annotations

from typing import Dict, List

from .ast import Line
from .diagnostics import AsmError, SourcePos

INSTR_SIZE = 8


def build_symbol_table(lines: List[Line], *, file: str, base: int = 0) -> Dict[str, int]:
    pc = base
    sym: Dict[str, int] = {}

    for ln in lines:
        if ln.label is not None:
            if ln.label in sym:
                pos = ln.label_pos or SourcePos(file=file, line=1, col=1)
                raise AsmError(pos, "E_DUP_LABEL", f"Duplicate label: {ln.label}")
            sym[ln.label] = pc
        if ln.instr is not None:
            pc += INSTR_SIZE

    return sym
