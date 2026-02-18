from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourcePos:
    file: str
    line: int
    col: int


class AsmError(Exception):
    def __init__(self, pos: SourcePos, code: str, message: str, hint: Optional[str] = None):
        self.pos = pos
        self.code = code
        self.message = message
        self.hint = hint
        super().__init__(self.__str__())

    def __str__(self) -> str:
        base = f"{self.pos.file}:{self.pos.line}:{self.pos.col}: {self.code}: {self.message}"
        if self.hint:
            return f"{base}\n  hint: {self.hint}"
        return base
