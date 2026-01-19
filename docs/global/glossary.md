# Glossary

This glossary defines the key terms used across the project.  
If a term has a specific meaning **in this project**, it is documented here to keep the language consistent across the emulator, assembler, compiler, and OS.

---

## A

**ABI (Application Binary Interface)**  
The rules that compiled programs follow so they can run correctly on the machine/OS: calling convention, register preservation, stack usage, syscall interface, and binary expectations.

**Address Space**  
The set of memory addresses a program can reference. In this project it is typically a single, flat, byte-addressed memory array inside the emulator.

**ALU (Arithmetic Logic Unit)**  
The conceptual part of the CPU that performs arithmetic and logical operations (ADD, SUB, AND, etc.). In the emulator this is implemented as code that updates registers/flags.

**Assembler**  
A tool that converts human-readable assembly (`.asm`) into machine code bytes (`.bin`) following the ISA encoding rules.

**Assembly (Assembly Language)**  
A human-readable representation of machine instructions and their operands. It is tightly coupled to the ISA.

---

## B

**Binary Image / Binary**  
A file containing machine code bytes meant to be loaded into memory and executed by the emulator (or by the OS under the emulator). Often `*.bin` in this project.

**Boot / Bootstrapping**  
The process of starting execution from an initial entrypoint and building up enough runtime to run more complex programs. Also refers to building the toolchain step-by-step to break circular dependencies.

**Boot Code / Bootloader**  
The earliest code that runs and prepares the system state (e.g., sets the stack pointer) before jumping into the kernel entrypoint.

**Byte-addressed**  
A memory model where each address points to one byte (8 bits). Multi-byte values occupy consecutive addresses.

---

## C

**Calling Convention**  
Part of the ABI. Defines how function calls work: where arguments go (registers/stack), where return values go, who saves which registers, and how the stack is managed.

**CPU State**  
All values that define the machine at a moment in time, typically including registers, PC, SP, FLAGS, memory, and whether the CPU is running or halted.

**Compiler**  
A tool that converts a high-level language into assembly (or directly into machine code). In this project, the compiler targets the project’s ISA and ABI.

**Control Flow**  
The order in which instructions execute. Jumps, conditional branches, calls, and returns modify control flow.

---

## D

**Decode**  
The step in execution where raw instruction bytes are interpreted as an opcode + operands.

**Directive**  
An assembler-only instruction (not a CPU instruction) that affects assembly output or layout, e.g., `.org`, `.byte`, `.word`. Directives do not execute on the CPU.

---

## E

**Emulator**  
A software implementation of the CPU + memory + execution rules. In this project it is the “reference machine” used for bootstrapping and debugging.

**Encoding**  
The mapping between an instruction’s meaning (opcode + operands) and its byte representation in machine code.

**Endianness**  
The byte order for multi-byte values in memory. Common choices are little-endian or big-endian. Must be defined if multi-byte immediates/loads exist.

**Entrypoint**  
The address where execution begins. For raw binaries, this is usually the load address; for structured images, it may be an address stored in a header.

---

## F

**Fetch–Decode–Execute**  
The core CPU cycle:

1. fetch instruction bytes from memory at PC
2. decode into opcode/operands
3. execute to update CPU state and memory

**FLAGS (Status Register)**  
A set of bits that record outcomes of operations (e.g., Zero flag). Used for conditional branching.

**Freeze Point**  
A moment where an interface contract (ISA/ABI/syscalls) is stabilized to prevent constant breaking changes.

---

## G

**Golden Program / Reference Program**  
A small set of programs used as regression tests. These must keep working to guarantee the ecosystem remains runnable.

---

## H

**HALT**  
An instruction that stops execution. Used for program termination or failure states in early stages.

**Host Environment**  
The real machine + OS (Linux) used to develop and bootstrap the project before the ecosystem is self-contained.

---

## I

**Immediate (Immediate Value)**  
A constant embedded directly inside an instruction encoding, e.g., `ADD R1, 5`.

**Instruction**  
A single CPU operation (like ADD, LOAD, JMP) represented in machine code by an opcode and operands.

**Instruction Format**  
The layout of bytes/bits in an instruction (opcode field, operand fields, immediate fields).

**ISA (Instruction Set Architecture)**  
The contract defining the CPU’s instructions, registers, memory model, and execution semantics. The ISA is the foundation that all other layers depend on.

**IR (Intermediate Representation)**  
A compiler-internal representation between source code and assembly, designed to make code generation and optimizations easier.

---

## J

**JMP (Jump)**  
An instruction that sets PC to a new address unconditionally, changing control flow.

**JZ (Jump if Zero)**  
A conditional jump that occurs when the Zero flag (or equivalent condition) is set.

---

## K

**Kernel**  
The core of the OS that runs with full control over the machine. Manages boot flow and provides system services.

---

## L

**Label**  
A named address in assembly. Labels are resolved by the assembler (usually in a first pass) into numeric addresses.

**Linker**  
A tool that combines multiple compiled/assembled files into one binary and resolves cross-file symbols. Typically out-of-scope early in this project.

**LOAD / STORE**  
Instructions that move data between memory and registers.

---

## M

**Machine Code**  
The raw bytes executed by the CPU. Produced by the assembler (and indirectly by the compiler).

**Memory Map**  
A documented layout of how memory addresses are used (boot, kernel, user program, stack, etc.). Becomes essential once the OS exists.

**Mnemonic**  
A human-friendly name for an instruction opcode, like `ADD` or `JMP`.

---

## O

**Opcode**  
The numeric code that identifies which instruction to execute.

**Operand**  
An input/output of an instruction. Could be a register, an immediate, or a memory address (depending on the ISA).

**OS (Operating System)**  
Software that provides runtime services and control over execution. In this project, it starts minimal (boot + kernel entry) and grows gradually.

---

## P

**PC (Program Counter)**  
Register holding the address of the next instruction to fetch.

**Pipeline (Toolchain Pipeline)**  
The full transformation chain:
high-level source → compiler → assembly → assembler → binary → run on emulator/OS

**Port / Portability**  
Ability to move components between environments. In this project, portability is improved by keeping contracts explicit and minimizing hidden assumptions.

---

## R

**Register**  
A small, fast storage location inside the CPU state used for computation and addressing.

**Relocation**  
A linker/loader concept: adjusting addresses in code/data when loading at a different address. Typically deferred early in this project.

**Runtime**  
Support code and conventions required for programs to run (stack setup, calling convention helpers, syscall wrappers, etc.).

---

## S

**SP (Stack Pointer)**  
Register pointing to the top of the stack.

**Stack**  
A region of memory used for function call frames, local variables, and saved registers. Often grows downward.

**Stage**  
A roadmap milestone grouping deliverables into incremental, testable steps (Stage 0, Stage 1, etc.).

**Syscall (System Call)**  
A controlled way for user programs to request services from the kernel (e.g., exit, write output). Requires a defined interface (SYS/ABI).

---

## T

**Toolchain**  
The set of tools that transform programs into runnable machine code (assembler, compiler, plus optional linker).

**Trap**  
A mechanism to transfer control from user code to kernel code (often used for syscalls or faults). Can be implemented via a special instruction or reserved opcode.

---

## V

**Versioned Contract**  
A rule that key interfaces are explicitly versioned (ISA v1, ABI v1, SYS v1). Breaking changes require updates across layers and docs/tests.

---

## Z

**Zero Flag (Z flag)**  
A FLAGS bit set when an operation result is zero. Commonly used for conditional branching (e.g., JZ).
