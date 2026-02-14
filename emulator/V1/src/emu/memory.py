from __future__ import annotations

from dataclasses import dataclass

MEM_SIZE = 65536  # 0x0000..0xFFFF


@dataclass(slots=True)
class Memory:
    data: bytearray

    @classmethod
    def blank(cls) -> "Memory":
        return cls(bytearray(MEM_SIZE))

    def load(self, addr: int, blob: bytes) -> None:
        if addr < 0 or addr >= MEM_SIZE:
            raise ValueError("address out of range")
        end = addr + len(blob)
        if end > MEM_SIZE:
            raise ValueError("blob does not fit in memory")
        self.data[addr:end] = blob

    def read_u8(self, addr: int) -> int:
        if addr < 0 or addr >= MEM_SIZE:
            raise IndexError("MEM_OOB")
        return self.data[addr]

    def write_u8(self, addr: int, val: int) -> None:
        if addr < 0 or addr >= MEM_SIZE:
            raise IndexError("MEM_OOB")
        self.data[addr] = val & 0xFF

    def read_slice(self, addr: int, size: int) -> bytes:
        if size < 0:
            raise ValueError("size must be >= 0")
        if addr < 0 or addr + size - 1 >= MEM_SIZE:
            raise IndexError("MEM_OOB")
        return bytes(self.data[addr:addr + size])
