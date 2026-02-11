# Computer Ecosystem (Emulator → Toolchain → OS)

A from-scratch computing stack built step-by-step: **CPU emulator → assembler → compiler → minimalist OS/kernel**.  
The goal is to grow a coherent “mini computer” where every layer fits together through explicit contracts (ISA/ABI/memory map) and stays runnable as the project scales.

---

## Tools

![Python](https://img.shields.io/badge/Python-3.x-blue)
![GitHub](https://img.shields.io/badge/GitHub-repo-black)
![Linux](https://img.shields.io/badge/Linux-Dev%20Environment-yellow)
![Markdown](https://img.shields.io/badge/Markdown-Docs-lightgrey)

---

## IMPORTANT

**Educational Purpose Disclaimer:** This repository is provided solely for educational and research purposes. It is not a production-grade system and should not be used in safety-critical or commercial environments.

---

## AI Usage Policy

This project was developed with the assistance of AI-based tools for brainstorming, documentation refinement, and selective code optimization. All architectural decisions, integration, testing, and final validation were performed manually.
AI tools were used as development assistants. All outputs were reviewed, tested, and validated before integration.

---

## What’s inside

This repository is organized as a small but complete computing ecosystem:

- **Emulator** — a reference CPU + memory model with a clear fetch–decode–execute loop
- **Assembler** — converts project assembly into raw binaries (`.asm → .bin`)
- **Compiler** — compiles a small high-level language into project assembly (then assembled into binaries)
- **OS/Kernel** — a minimal boot flow and kernel foundation to run user code on the emulator

---

## Project goals

- Build a system that is **understandable by construction**
- Keep interfaces explicit and versioned:
  - **ISA** (instruction set and encoding)
  - **ABI** (calling conventions and stack/register rules)
  - **SYS** (syscall interface)
- Maintain at least one **working end-to-end pipeline** at all times:
  **source → compiler → asm → assembler → bin → run (OS + emulator)**

### Non-goals (early phases)

This project is clarity-first, so early phases intentionally avoid:

- advanced optimization and performance tuning
- full POSIX compliance
- complex linking/relocation systems
- large driver/device stacks

---

## Repository layout

docs/
global/ # overview, roadmap, architecture, decisions, glossary, references (+ PDFs)
sections/ # per-component docs (emulator/assembler/compiler/os) (+ PDFs)
assets/ # images & diagrams

emulator/ # emulator code + quick README
assembler/ # assembler code + quick README
compiler/ # compiler code + quick README
os/ # boot + kernel code + quick README

tools/ # helper scripts (debugging, utilities, etc.)

---

## Documentation

### Start here (high-level)

- `docs/global/overview.md`
- `docs/global/roadmap.md`
- `docs/global/architecture.md`
- `docs/global/decisions.md`

### Deep dives (per section)

- `docs/sections/emulator/`
- `docs/sections/assembler/`
- `docs/sections/compiler/`
- `docs/sections/os/`

### PDFs (committed, read-only artifacts)

PDFs are included for easy reading and sharing:

- Global PDF: `docs/global/global.pdf`
- Section PDFs: `docs/sections/<section>/<section>.pdf`

> Note: the docs started as early-project baselines and are updated progressively as stages advance.  
> The decisions log and the current tests/demos are the most reliable source of “current truth”.

---

## Current status

This project progresses in stages (see `docs/global/roadmap.md`).  
Each stage ends with a runnable demo and tests to prevent regressions.

**Next milestone target:** a complete end-to-end run:
**high-level program → compiler → binary → OS runs it on the emulator**

---

## How to contribute (short version)

- Keep `main` runnable.
- Use feature branches: `feat/<area>-<change>`
- Update docs/tests when changing core contracts (ISA/ABI/memory map).
- If you modify `docs/**/*.pdf`, expect maintainer review (PDFs are treated as artifacts).

See `CONTRIBUTING.md` for details.

---

## License

See `LICENSE`.
