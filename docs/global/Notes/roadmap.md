# Roadmap

This roadmap describes the staged path from a normal Linux host environment to a complete end-to-end ecosystem:

**High-level program → compiler → assembly → assembler → binary → OS/kernel → CPU emulator**

The project is intentionally **clarity-first**:

- Keep interfaces between layers explicit.
- Prefer simple, testable milestones over feature count.
- Avoid premature optimization.

> Note on documentation artifacts: PDFs are committed “read-only” artifacts. Contributors are not expected to regenerate PDFs; the maintainer updates them when appropriate.

---

## Milestone Summary

| Stage | Name                      | Outcome (Definition of Done)                                           |
| ----: | ------------------------- | ---------------------------------------------------------------------- |
|     0 | Host Environment          | Repo, tooling, and project scaffolding ready on Linux                  |
|     1 | Emulator Execution        | Emulator runs binaries via fetch–decode–execute                        |
|     2 | Minimal Toolchain         | Assembler produces raw binaries that run on the emulator               |
|     3 | Early Kernel              | Boot code transfers control to a tiny kernel running on the emulator   |
|     4 | Language + Compiler (MVP) | A small language compiles to working binaries                          |
|     5 | End-to-End Loop           | Programs compiled from the language run _under the OS_ on the emulator |
|     6 | Refinement                | Tests, debugging tools, and docs harden the ecosystem                  |

---

## Stage 0 — Host Environment (External Anchor)

### Goal

Establish the development anchor (Linux + tools) and a repo structure that supports incremental growth.

### Deliverables

- Repository structure created (code + docs).
- Basic conventions:
  - `docs/global/*` for global system docs
  - `docs/sections/*` for component docs
- Baseline tooling:
  - Python runtime
  - Git + GitHub remote
  - Test runner plan (pytest recommended if using Python)

### Definition of Done

- Repo clones successfully.
- `README.md` explains:
  - What the project is
  - Where documentation lives
  - What the current working demo is (even if tiny)

### Acceptance Test

- A fresh machine can clone the repo and run a “hello world” script or minimal placeholder command.

---

## Stage 1 — Emulator Execution (CPU in Software)

### Goal

Implement a CPU emulator that can load and execute a binary program using a clear fetch–decode–execute loop.

### Core Concepts

- Machine state:
  - General-purpose registers (e.g., R0–R7)
  - PC (program counter), SP (stack pointer), FLAGS/status
  - Memory as a fixed-size byte array (e.g., 64KB)
- Instruction encoding:
  - Keep it simple (fixed-width is fine early)

### Deliverables

- Emulator executable/entrypoint:
  - Loads a binary file into memory
  - Sets PC to start address
  - Runs until HALT or error
- Minimal ISA implemented (starter set):
  - Data: MOV, LOAD, STORE
  - Arithmetic: ADD, SUB (MUL optional early)
  - Control flow: JMP, JZ (or equivalent)
  - System: HALT
- Tracing/debug mode:
  - Print PC, opcode, registers (at least optional)

### Definition of Done

- Emulator runs a binary and halts deterministically with correct final register/memory state.

### Acceptance Tests

- “Arithmetic program” produces expected register results.
- “Control flow program” demonstrates jumps/conditions.
- “Memory program” demonstrates LOAD/STORE correctness.

---

## Stage 2 — Minimal Toolchain (Assembler)

### Goal

Break the circular dependency by producing binaries for the emulator without relying on a full toolchain.

### Deliverables

- A hand-written assembler (Python):
  - Reads `.asm`
  - Outputs raw binary (`.bin`)
- Assembly syntax definition:
  - Labels
  - Immediate values
  - Comments and whitespace rules
- Two-pass label resolution (recommended):
  - Pass 1 collects label addresses
  - Pass 2 emits bytes

### Definition of Done

- Every Stage 1 test program can be written in assembly and assembled into a binary that runs on the emulator.

### Acceptance Tests

- `hello.asm` (or equivalent) assembles and runs.
- Labels work (forward/back jumps).
- Invalid syntax produces helpful errors.

### Non-Goals (Explicit)

- No linker.
- No optimizer.
- No relocations unless you truly need them.

---

## Stage 3 — Early Kernel (Boot + Minimal System)

### Goal

Introduce the first “OS-like” layer: boot sequence and kernel control flow.

### Scope Choice

This roadmap uses **Minimal OS scope (4A)**:

- Minimal memory setup
- Basic syscall/trap mechanism (optional early)
- No full process model, no scheduler required

### Deliverables

- Boot code in assembly:
  - Sets initial CPU state (stack pointer, memory assumptions)
  - Transfers control to kernel entrypoint
- Kernel skeleton:
  - Written in a higher-level subset (can still be assembly at first, then move up)
  - Provides a minimal “kernel loop” (or command dispatcher)
- Minimal memory map documented:
  - Boot region
  - Kernel region
  - User program region
  - Stack region

### Definition of Done

- The emulator can load a “boot image” that enters the kernel and performs at least one meaningful service (even if it’s just printing via emulator debug output or a simple “exit” code).

### Acceptance Tests

- Boot → kernel entry is reliable.
- Kernel can run a tiny “user program” or at least return control cleanly.
- Memory layout matches documentation.

---

## Stage 4 — Language + Compiler (MVP)

### Goal

Create a tiny high-level language and compile it into assembly that the assembler can turn into binaries.

### Deliverables

- Language MVP (keep it intentionally small):
  - Variables
  - Integer arithmetic
  - Conditionals (if/else) OR loops (choose one first)
  - Function calls optional early
- Compiler (Python):
  - Parser → AST
  - Optional IR (recommended if you plan to grow the language)
  - Codegen → target assembly

### Definition of Done

- A simple program written in the new language compiles to assembly, assembles to a binary, and runs correctly on the emulator.

### Acceptance Tests

- `examples/` contains:
  - A high-level source file
  - The generated `.asm`
  - The final `.bin`
- Tests cover:
  - arithmetic correctness
  - control flow correctness
  - error messages for syntax/semantic failures

---

## Stage 5 — End-to-End Loop Under the OS

### Goal

Complete the intended loop: programs compiled from the language run **as user code under the OS** on the emulator.

### Deliverables

- A basic ABI contract documented (even if very simple):
  - Calling convention (how arguments/returns work)
  - Stack usage rules
- Minimal syscall interface (optional but powerful):
  - e.g., exit(code), write_char, write_int
  - Implemented via a trap instruction or reserved opcode

### Definition of Done

- A language program runs under the kernel/OS environment (not just “bare emulator”), using the agreed ABI.

### Acceptance Tests

- `lang → compiler → asm → assembler → bin → boot → kernel → user program` works in one scripted run.
- At least one syscall works end-to-end (even if trivial).

---

## Stage 6 — Refinement and Hardening

### Goal

Make the ecosystem robust, debuggable, and maintainable.

### Deliverables

- Strong test suite:
  - Unit tests per component
  - Integration tests for the full pipeline
- Debugging tools:
  - Disassembler (optional)
  - Trace logs with step limits
  - Better error handling in assembler/compiler
- Documentation completeness:
  - ISA frozen v1 (or versioned)
  - Memory map updated
  - ABI documented

### Definition of Done

- You can change one layer (e.g., add an opcode) and confidently update tests + docs without breaking the ecosystem silently.

---

## Stretch Goals (Optional)

- Self-hosting (very long-term):
  - Compiler written in the language it compiles
- Hardware translation:
  - Port ISA/emulator model to an HDL (FPGA later)
- More OS features:
  - Processes + simple scheduler
  - Filesystem mock
  - Device abstractions (still minimal)

---

## Working Agreement: “Freeze Points”

To prevent constant rewrites, introduce freeze points:

- **ISA v1 Freeze**: opcode meanings and encoding stabilized
- **ABI v1 Freeze**: calling convention and stack rules stabilized
- **Syscall v1 Freeze**: stable set of minimal syscalls

After a freeze point, changes require updating:

- docs
- tests
- at least one end-to-end demo program

---

## Scalability and Continuous Upgrades

This project is designed to be **scalable by layers**: you can upgrade any section (emulator, assembler, compiler, OS) as much as you want **as long as the whole system stays runnable**.

### The golden rule

Every upgrade must keep at least one complete pipeline working:

**high-level source → compiler → assembly → assembler → binary → emulator/OS run**

If an improvement breaks the end-to-end run, it must be fixed (or reverted) before merging.

### How to scale safely

- **Version contracts instead of rewriting them**
  - Use version tags like `ISA v1`, `ABI v1`, `SYS v1`.
  - If you introduce breaking changes, create `v2` while keeping a compatibility path or updating the full pipeline immediately.
- **Maintain a “reference program set”**
  - Keep a small set of programs that must always run (e.g., `hello`, arithmetic, branching, memory, syscall demo).
  - These are your non-negotiable regression tests.
- **Prefer incremental upgrades**
  - Add instructions one group at a time.
  - Expand the assembler syntax gradually (directives, macros) without breaking basic syntax.
  - Grow the language feature-by-feature (types, functions, structs, etc.).
  - Extend OS services carefully (syscalls, memory model) with tests and documentation.

### Examples of scalable upgrades (non-exhaustive)

- Emulator: better tracing, breakpoints, faster execution, more devices (timer/console), more memory
- Assembler: macros, includes, improved diagnostics, debug symbols
- Compiler: richer language features, optimizations, better IR, improved register allocation
- OS: cleaner boot, syscall library, memory protection model, multitasking (later)

### Definition of “runnable”

At any moment, the repo should provide:

- A documented command/script to run the reference demo(s)
- Expected output (or expected final CPU state)
- Tests that confirm correctness

This rule ensures the project can scale indefinitely without becoming untestable or “half-finished”.
