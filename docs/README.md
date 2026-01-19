# Documentation

This folder contains the documentation for the entire project.

## Important note about freshness (read this first)

Most documents in this repository started as **starter baselines** written at the beginning of the project.  
That means:

- They could be **Placeholders** for future files.
- They are **meant to provide structure**, not final truth.
- Parts of them may become **outdated quickly** as the project evolves.
- The project is intentionally incremental, so docs are updated **stage by stage** as milestones are reached.

If you are reading these docs mid-project, treat them as a **living set of notes**: useful for understanding intent and direction, but not always perfectly synchronized with the latest implementation.

### How to know what’s currently accurate

- The **Roadmap** (`docs/global/roadmap.md`) indicates what stage the project is currently in and what should exist at that point.
- The **Decisions Log** (`docs/global/decisions.md`) records major choices and is usually the best place to understand “what the project currently believes”.
- The most reliable truth is always:
  1. the current code
  2. the tests / reference programs
  3. the most recently updated decision entries

---

## Documentation layout

### `docs/global/` — Whole-project documentation

Big-picture documents that explain the system as one coherent stack:

- Overview (what the project is and why it exists)
- Roadmap (stages and definitions of done)
- Architecture (how the layers connect)
- Decisions log (why key choices were made)
- Glossary and references

### `docs/sections/` — Per-component documentation

Deep dives for each component:

- Emulator (ISA, internals, testing)
- Assembler (syntax, encoding, testing)
- Compiler (language spec, IR, codegen, testing)
- OS (boot, kernel, syscalls, memory map, testing)

### `docs/assets/` — Images and diagrams

Reusable visuals used across documentation:

- `images/` for exported images
- `diagrams/` for diagram source files

---

## PDFs (committed artifacts)

PDFs are included in the repository as **pre-generated, read-only artifacts** for easy reading and sharing.

- Global PDF: `docs/global/global.pdf`
- Section PDFs: `docs/sections/<section>/<section>.pdf`

Contributors are not expected to regenerate PDFs. When the project reaches new milestones, the maintainer updates PDFs to match the latest stage and decisions.

---

## Suggested reading order

1. `docs/global/overview.md`
2. `docs/global/roadmap.md`
3. `docs/global/architecture.md`
4. `docs/global/decisions.md`
5. Section docs depending on what you’re working on:
   - Emulator: `docs/sections/emulator/`
   - Toolchain: `docs/sections/assembler/` and `docs/sections/compiler/`
   - OS: `docs/sections/os/`

## Latest updated doc :
