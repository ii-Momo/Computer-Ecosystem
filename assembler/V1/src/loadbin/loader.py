from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadReport:
    path: str
    base: int
    size: int
    end: int


def load_bin(path: str, *, base: int = 0) -> tuple[bytes, LoadReport]:
    p = Path(path)
    data = p.read_bytes()
    rep = LoadReport(path=str(p), base=base, size=len(data), end=base + len(data))
    return data, rep