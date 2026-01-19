# Decisions Log

This file records _architectural and project-level decisions_ and (most importantly) **why** they were made.  
The goal is to prevent “design drift” and repeated debates, and to keep the whole ecosystem coherent as it evolves.

This project is **clarity-first**: correctness and clean interfaces matter more than performance or feature count.

---

## How to use this log

### When to add an entry

Add a decision whenever it affects compatibility between layers or changes assumptions, such as:

- ISA changes (new opcode, encoding change, register model changes)
- ABI / calling convention changes
- Memory map changes
- Program/binary format changes
- Boot flow / kernel entry changes
- Toolchain changes (assembler syntax rules, compiler targets)
- Scope changes (new major features, removed goals)

### Decision template

Copy/paste this block for new entries:

```text
## YYYY-MM-DD — <Decision title>
**Status:** Proposed | Accepted | Deprecated
**Scope:** ISA | Emulator | Assembler | Compiler | OS | Docs | Process

**Context**
- What problem are we solving?
- What constraints matter?

**Decision**
- What exactly are we doing?

**Rationale**
- Why this option?
- What trade-offs are we accepting?

**Consequences**
- What must change (docs/tests/code)?
- What becomes easier/harder?

**Follow-ups**
- Concrete tasks to implement or document this decision
```
