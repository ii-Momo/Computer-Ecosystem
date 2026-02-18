from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from .diagnostics import SourcePos


@dataclass(frozen=True)
class Register:
    index: int  # 0..15
    pos: SourcePos


@dataclass(frozen=True)
class Number:
    value: int
    pos: SourcePos


@dataclass(frozen=True)
class LabelRef:
    name: str
    pos: SourcePos


Operand = Union[Register, Number, LabelRef]


@dataclass(frozen=True)
class Instruction:
    mnemonic: str
    operands: List[Operand]
    pos: SourcePos


@dataclass(frozen=True)
class Line:
    label: Optional[str]
    label_pos: Optional[SourcePos]
    instr: Optional[Instruction]
