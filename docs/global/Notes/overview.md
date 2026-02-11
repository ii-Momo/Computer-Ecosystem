# Overview

This project builds a complete “mini computer ecosystem” from first principles—starting from a tiny CPU model and growing upward into a full, runnable stack:

**CPU (emulated) → assembler → compiler → minimal OS/kernel → user programs**

The key idea is that these layers are **not separate projects**. They are designed to **co-evolve** with clear contracts (ISA/ABI/memory map), so the whole system remains consistent and runnable as it grows.

---

## What we are building

### The machine (conceptual)

A small CPU with:

- a minimal register set
- a program counter (PC) and stack pointer (SP)
- status flags (FLAGS)
- byte-addressed memory
- a small instruction set sufficient to run real programs

This machine is implemented first as a **software emulator**, which acts as the reference platform.

### The toolchain

A minimal toolchain that targets the machine:

- **Assembler**: `.asm` → `.bin` (raw machine code bytes)
- **Compiler**: small high-level language → `.asm` (then assembled into `.bin`)

### The OS layer

A minimal OS/kernel that can:

- boot into a kernel entrypoint
- establish a basic memory layout
- provide minimal runtime services (starting small and growing later)

### The end-to-end goal

A complete pipeline that works end-to-end:

**source code → compiler → assembly → assembler → binary → run under OS on emulator**

---

## Why this project exists

### 1) Understanding by construction

Instead of treating computers as a black box, the project reconstructs the stack step-by-step so each piece is fully understood:

- what an instruction really is
- how bytes become behavior
- how a toolchain transforms source into machine code
- how an OS “boots” and provides services

### 2) Engineering discipline, not just hacking

The project is designed to develop real engineering habits:

- explicit interfaces (ISA, ABI, syscalls)
- decision logging (why choices were made)
- regression tests and runnable demos
- incremental milestones

### 3) A scalable sandbox

Because everything is small and inspectable, the system becomes a perfect sandbox for experiments:

- add an instruction and see effects across the stack
- change calling conventions and observe behavior
- prototype OS services without real hardware risk

---

## Project philosophy

### Keep it runnable

At any time, there must be at least one working end-to-end demo program.

If improvements break the pipeline, they must be fixed (or reverted) before merging.

### Clarity first

This is not a performance competition. Early designs prefer:

- simpler encodings
- fewer moving parts
- explicit behavior over “cleverness”

### Version key contracts

The system’s stability depends on contracts:

- **ISA** (instruction meanings and encoding)
- **ABI** (calling convention and stack/register rules)
- **SYS** (syscall interface)

These should be versioned and “frozen” at milestones (ISA v1, ABI v1, SYS v1) to prevent endless rewrites.

---

## What “done” looks like (MVP)

The MVP milestone is reached when:

- a small high-level program compiles successfully
- the assembler produces a runnable binary
- the OS boots and runs the program (as “user code”)
- the emulator executes everything deterministically with tests verifying correctness

---

## Documentation map

- **Global docs (the big picture):** `docs/global/`
  - overview, roadmap, architecture, decisions, glossary, references
- **Section docs (deep dives):** `docs/sections/`
  - emulator, assembler, compiler, OS internals and specifications
- **Committed PDFs:** global + per-section PDFs are stored alongside the Markdown for easy reading and sharing.

---

## How to use this repository

A suggested reading order:

1. `docs/global/roadmap.md` — the staged plan and milestones
2. `docs/global/architecture.md` — how the layers connect
3. `docs/sections/emulator/isa.md` — the ISA contract
4. `docs/sections/assembler/encoding.md` — bytes and instruction encoding
5. `docs/sections/compiler/codegen.md` — how high-level code becomes assembly
6. `docs/sections/os/memory-map.md` — memory layout once OS exists

---

## Scope and non-goals (early phases)

The early phases explicitly avoid:

- complex linking/relocation systems
- advanced compiler optimizations
- full POSIX-style OS features
- drivers and hardware support beyond what the emulator models

These can be added later, but only after the minimal system is stable and runnable.
