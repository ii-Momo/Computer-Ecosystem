from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .diagnostics import AsmError, SourcePos
from ..common.utils import is_identifier


@dataclass(frozen=True)
class Token:
    kind: str   # IDENT, REG, NUMBER, COLON, COMMA, EOL, EOF
    text: str
    pos: SourcePos


def _is_reg(s: str) -> bool:
    if len(s) < 2:
        return False
    if s[0] not in ("R", "r"):
        return False
    tail = s[1:]
    return tail.isdigit() and 0 <= int(tail) <= 15


def lex(source: str, *, file: str) -> List[Token]:
    tokens: List[Token] = []
    line_no = 1
    col = 1
    i = 0
    n = len(source)

    def emit(kind: str, text: str, line: int, column: int) -> None:
        tokens.append(Token(kind=kind, text=text, pos=SourcePos(file=file, line=line, col=column)))

    while i < n:
        ch = source[i]

        if ch == "\n":
            emit("EOL", "\n", line_no, col)
            i += 1
            line_no += 1
            col = 1
            continue

        if ch == ";":
            while i < n and source[i] != "\n":
                i += 1
            continue

        if ch in (" ", "\t", "\r"):
            i += 1
            col += 1
            continue

        if ch == ":":
            emit("COLON", ":", line_no, col)
            i += 1
            col += 1
            continue

        if ch == ",":
            emit("COMMA", ",", line_no, col)
            i += 1
            col += 1
            continue

        if ch.isdigit() or (ch == "-" and i + 1 < n and (source[i + 1].isdigit())):
            start_i = i
            start_col = col
            i += 1
            col += 1
            while i < n and (source[i].isalnum() or source[i] in ("x", "X")):
                i += 1
                col += 1
            emit("NUMBER", source[start_i:i], line_no, start_col)
            continue

        if ch.isalpha() or ch == "_":
            start_i = i
            start_col = col
            i += 1
            col += 1
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
                col += 1
            text = source[start_i:i]
            if _is_reg(text):
                emit("REG", text.upper(), line_no, start_col)
            else:
                if not is_identifier(text):
                    raise AsmError(SourcePos(file, line_no, start_col), "E_BAD_IDENT", f"Invalid identifier: {text}")
                emit("IDENT", text.upper(), line_no, start_col)
            continue

        raise AsmError(SourcePos(file=file, line=line_no, col=col), "E_BAD_CHAR", f"Unexpected character: {ch!r}")

    emit("EOF", "", line_no, col)
    return tokens
