# Architecture

This document explains how the system fits together as a **single computing ecosystem**: CPU design, tooling, language, and OS are not isolated projects—they are **co-designed layers** with explicit contracts between them. The goal is correctness and clarity over performance.

This architecture follows an **emulator-first bootstrapping strategy**, using a Linux host as temporary scaffolding until the ecosystem becomes self-consistent.

---

## 1) Architectural Principles

### 1.1 Co-evolving layers

Each layer is designed with awareness of the layers above and below it:

- The **ISA** constrains the assembler, compiler codegen, and OS entry/ABI.
- The **assembler** constrains what “machine code” means in practice.
- The **compiler** constrains the ABI and what the OS must provide (at minimum).
- The **OS** constrains runtime expectations (boot flow, memory map, syscalls).

This reduces integration surprises and supports incremental iteration.

### 1.2 Clarity over feature count

Success is measured by:

- clean boundaries
- explicit trade-offs
- predictable execution
- end-to-end demonstrations  
  not by matching real-world feature sets.

### 1.3 Keep it runnable

At all times, the repo should provide a working pipeline (at least one reference program):
**source → compiler → asm → assembler → binary → emulator/OS run**

If improvements break the pipeline, they must be fixed (or reverted) before merging.

---

## 2) Layered System Overview

### 2.1 The stack (conceptual)

[ High-level Language Programs ]
|
v
Compiler
|
v
Assembly (.asm)
|
v
Assembler
|
v
Binary Image (.bin)
|
v
Emulator (CPU + Memory)
|
v
OS/Kernel (boot + services)
|
v
User code under OS

### 2.2 What each layer is responsible for

#### CPU / ISA (the “contract core”)

Defines:

- machine state (registers, PC, SP, FLAGS)
- instruction meanings and encoding
- memory model (byte-addressed, fixed size)
- behavior for invalid opcodes / faults (halt + diagnostics early)

#### Emulator (the “reference machine”)

Implements:

- fetch–decode–execute loop
- deterministic state transitions
- program loading
- debugging/trace facilities (high leverage early)

#### Assembler (first toolchain anchor)

Transforms human-readable assembly into raw bytes matching the ISA encoding.

- Two-pass labels strongly recommended
- No linker/optimizer early (keeps scope realistic)

#### Compiler (language → assembly)

Transforms a small high-level language into correct assembly under the ABI rules.

- Can evolve from direct AST→asm to IR-based design as complexity grows

#### OS/Kernel (minimal but functional)

Provides:

- boot flow into kernel entry
- minimal memory assumptions + memory map
- minimal “services” (can start as just exit codes / console output)
- optional syscall/trap mechanism later

---

## 3) Core Contracts (the rules that keep layers compatible)

These contracts must be explicit and versioned (e.g., ISA v1, ABI v1).

### 3.1 ISA contract (Instruction Set Architecture)

**Minimum CPU state** (initial target):

- General-purpose registers (e.g., R0–R7)
- PC (Program Counter)
- SP (Stack Pointer)
- FLAGS / status register
- Running/halted state flag

**Memory model**:

- Byte-addressed contiguous array
- Fixed size (often 64KB early, but configurable)
- Reads/writes are explicit effects of instructions

**Instruction categories** (minimal complete set):

- Data movement: `MOV`, `LOAD`, `STORE`
- Arithmetic: `ADD`, `SUB` (optionally `MUL`)
- Control flow: `JMP`, `JZ`, `CALL`, `RET`
- Stack: `PUSH`, `POP`
- System: `HALT`

**Instruction encoding** (simple, clarity-first):
A fixed-width format is recommended early, e.g. 4 bytes:
[ opcode | operandA | operandB | imm8 ]
This trades density for simplicity and makes assembler/emulator easier.

> Exact opcode values, operand meaning rules, and sizes live in the ISA section docs:
> `docs/sections/emulator/isa.md`

### 3.2 Binary image contract (what the emulator loads)

**Initial approach (Stage 1–2): raw binary**

- `.bin` is a plain byte sequence
- Emulator loads it at a defined base address (e.g., 0x0000)
- PC is set to the base address (or an agreed entrypoint)

**Optional later: tiny header**
If needed, introduce a minimal header:

- magic bytes (format identifier)
- entrypoint address
- image size
  This helps OS boot images and user programs coexist, but is not required early.

### 3.3 ABI contract (compiler ↔ OS ↔ conventions)

The ABI is the “social contract” for generated code:

- how functions pass arguments and return values
- what registers must be preserved across calls
- how the stack is used and aligned
- how syscalls (if any) are invoked

**Minimal ABI v1 (recommended early)**

- Return value in a single register (e.g., R0)
- Arguments in registers first (e.g., R0–R3), spill to stack if needed
- `CALL` pushes return address; `RET` pops it
- Stack grows downward (common + simplifies reasoning)

> ABI details should be documented in:
>
> - global view here
> - plus section docs later (compiler codegen + OS syscall ABI)

### 3.4 OS interface contract (kernel entry + services)

**Kernel entry**

- Boot code sets initial machine state (at minimum: stack pointer)
- Boot transfers control to a fixed kernel entry address or symbol

**Services**
Early services can be minimal:

- exit / halt with status code
- optional console output
  Later services may include:
- memory allocation primitives
- process abstractions (not required in minimal scope)

---

## 4) Bootstrapping Model (how we break circular dependency)

Bootstrapping is about escaping the loop:
`Compiler → Executable → CPU → OS → Compiler`

This project uses external anchors:

- existing hardware + Linux host
- mature dev tools temporarily (Python/C compilers, debuggers)

**Staged strategy**:

- Stage 0: Host environment scaffolding
- Stage 1: Emulator runs binaries
- Stage 2: Minimal assembler emits binaries
- Stage 3: Boot + early kernel
- Stage 4+: Language + compiler
- Stage 5: Full loop under OS

---

## 5) Execution Model (what “running a program” means)

The emulator implements the canonical loop:

while running:
instr = memory[PC : PC+n]
PC += n
decode(instr)
execute(decoded)

### 5.1 Fetch

Read instruction bytes at PC.

### 5.2 Decode

Interpret opcode and operands, parse immediate values.

### 5.3 Execute

Apply state changes:

- registers updated
- memory read/write
- PC modified for jumps/calls/returns

### 5.4 Errors and traps (early behavior)

For invalid behavior:

- invalid opcode
- out-of-bounds memory access
- divide-by-zero (if division exists)

**Early strategy**: print diagnostic + halt  
**Later strategy**: trap instruction / structured exceptions

---

## 6) Memory Map (global conceptual layout)

Early on, memory can be “flat”. As the OS arrives, the map becomes important.

A reasonable conceptual map (addresses are illustrative; finalize later in OS docs):
0x0000 ─────────────────────────────
Boot / Entry region
(or user program region in Stage 1–2)
Kernel code/data (Stage 3+)

User program region (Stage 5+)

Heap / dynamic memory (optional)
Stack (grows downward)

0xFFFF ─────────────────────────────

The exact map must be documented and kept consistent across:

- emulator load behavior
- assembler output assumptions
- compiler codegen assumptions
- OS boot + kernel layout

> Memory map details belong in `docs/sections/os/memory-map.md`.

---

## 7) Repository Mapping (where architecture lives in the repo)

- **Global architecture + decisions**: `docs/global/`
- **ISA spec and emulator internals**: `docs/sections/emulator/`
- **Assembly syntax + encoding rules**: `docs/sections/assembler/`
- **Language spec + IR + codegen**: `docs/sections/compiler/`
- **Boot/kernel/syscalls/memory map**: `docs/sections/os/`

Rule of thumb:

- Global docs define _how pieces connect_
- Section docs define _how a piece works internally_

---

## 8) Observability and Testing Strategy (architecture-level)

This project benefits massively from observability because the emulator is fully inspectable.

### 8.1 Emulator observability (high leverage early)

- Instruction trace mode (PC/opcode/register dump)
- Step limit / run limit (prevents infinite loops)
- Deterministic execution (same program → same outcome)

### 8.2 Test layers

- Unit tests per component (assembler parsing, instruction semantics)
- Integration tests (assemble+run known programs)
- End-to-end tests (language → compiler → asm → assembler → bin → run)

Keep a small set of “golden programs” that must always work:

- arithmetic demo
- branching demo
- memory demo
- call/return demo
- syscall demo (once OS has it)

---

## 9) Versioning and Freeze Points (how we evolve safely)

To scale the system without constant rewrites:

### 9.1 Version contracts

- **ISA v1**, **ABI v1**, **SYS v1** (syscalls)
  Breaking changes require:
- updating docs
- updating tests
- updating at least one end-to-end demo

### 9.2 Freeze points

- ISA v1 freeze: opcode meanings + encoding stable
- ABI v1 freeze: calling convention stable
- Syscall v1 freeze: minimal syscall set stable

After a freeze point, changes must be deliberate and clearly documented.

---

## 10) Scalability (designed for indefinite growth)

You can upgrade each section as much as you want **as long as the system stays runnable**.

Safe upgrades include:

- Emulator: better tracing, breakpoints, faster dispatch, more memory/devices
- Assembler: macros, includes, richer diagnostics, debug symbols
- Compiler: more language features, IR improvements, optimizations
- OS: more syscalls, better memory model, later optional processes

The “runnable pipeline” rule ensures the ecosystem can grow without becoming half-finished or untestable.

---

## 11) Open Items (to be finalized in section docs)

These are intentionally deferred until the system needs them:

- Exact register count and widths (start small, version later)
- Final instruction encoding details (fixed-width vs mixed-width)
- Binary image header (only if required)
- Syscall/trap mechanism and numbering
- Final memory map addresses and reserved regions
- Standard library/runtime expectations for the language
