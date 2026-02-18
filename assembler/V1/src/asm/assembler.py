from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .lexer import lex
from .parser import parse
from .pass1_symbols import build_symbol_table
from .pass2_emit import assemble_to_bytes


@dataclass(frozen=True)
class AssembleResult:
    binary: bytes
    symtab: Dict[str, int]


def assemble_text(text: str, *, file: str, base: int = 0) -> AssembleResult:
    tokens = lex(text, file=file)
    lines = parse(tokens)
    symtab = build_symbol_table(lines, file=file, base=base)
    binary = assemble_to_bytes(lines, symtab, base=base)
    return AssembleResult(binary=binary, symtab=symtab)
