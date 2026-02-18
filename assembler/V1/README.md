# toolchain-v1 (Assembler & Toolchain v1)

Implements Section 4 (v1) minimal end-to-end loop:

`.asm → assembler → flat .bin → loader`

## Requirements

- Python 3.11+

## Setup

```bash
python -m venv .venv
# Windows PowerShell:
#.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Commands (v1)

Assemble:

```bash
python -m src.asm.cli examples/v1/demo.asm -o demo.bin
```

Load binary (prints a short report; can also emit a memory image):

```bash
python -m src.loadbin.cli demo.bin --base 0x0000
```

**OR**

Go to ~/.bashrc and add the following line :

export PATH="PATH_TO_TOOLCHAIN_V1/.local/bin:$PATH"
!!! REPLACE "PATH_TO_TOOLCHAIN_V1" WITH THE ACTUAL PATH
use anywhere :

Assemble and load :

```bash
ass_cli PATH_TO_.ASM PATH_TO_.BIN
```

Assemble, load and run on cpu :

```bash
ass_run_cli PATH_TO_.ASM PATH_TO_.BIN
```

!!! REQUIRES : pip install -e PATH_TO_CPU-EMULATOR

## Tests

```bash
pytest -q
```

## Notes

- Fixed 8-byte instruction encoding:
  `opcode(8) | rd(8) | ra(8) | rb(8) | imm32(LE)`
- Two-pass assembler for labels.
- v1 mnemonics only (no directives, no linker, no macros).

If your emulator already uses specific opcode values, update `src/toolchain/asm/isa.py`
to match your emulator’s opcode table.
