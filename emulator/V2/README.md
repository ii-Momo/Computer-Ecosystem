# CPU Emulator — Section 03 (v1)

This repository contains the Python implementation for **Section 03: v1 CPU & Emulator**.  
The goal is a **deterministic**, **test-driven**, and **spec-faithful** emulator that will serve as the foundation for later sections.

---

## Prerequisites (WSL / Ubuntu)

Install Python and virtual environment support:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

(Optional) Make `python` point to `python3`:

```bash
sudo apt install -y python-is-python3
```

---

## Virtual Environment Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Commands (V1):

Run :

```bash
python -m emu.cli -h
```

**OR**

Go to ~/.bashrc and add the following line :

export PATH="PATH_TO_CPU-EMULATOR_V1/.local/bin:$PATH"
!!! REPLACE "PATH_TO_CPU-EMULATOR_V1" WITH THE ACTUAL PATH

use anywhere :

```bash
emu_cli -h
```

## Tests

```bash
pytest -q
```

## Development Notes (v1)

- Keep **CPU state**, **decoder**, and **executor** separated for clarity.
- Implement one opcode at a time with matching tests.
- Treat faults as **terminal** (halt + record diagnostic state).

---
