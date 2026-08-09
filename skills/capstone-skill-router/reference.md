# Router reference

## Selection heuristics

- "How do I open a handle / check version / handle errors?" → core-api
- "Batch disasm or iterator?" / "reuse one insn buffer?" → disasm-iteration
- "Why is detail still on?" / "alias vs real operands?" → detail-aliases
- "Which registers does this insn touch?" → operands-registers
- "Intel vs ATT / no alias text / CS_REG_ALIAS" → options-syntax
- "Skip invalid bytes / custom skip callback" → skipdata
- "Faster loop / multi-thread / custom malloc" → performance-concurrency
- "Porting from Capstone 4/5 / ARM64 rename" → v6-migration
- "Unexpected errno / wrong skip size / null detail" → troubleshooting
- Named ISA / `CS_ARCH_*` / arch header → `capstone-arch-<name>`
- CMake / diet / cross / embed → cmake-build, size-optimized, cross-platform,
  or custom-memory-embedding
- `cstool` / YAML tests / bindings / fuzz hex → cstool, cstest-yaml,
  language-bindings, or fuzzing-crash-repro

## Cross-links that commonly stack

- detail + iter: detail-aliases then disasm-iteration
- skipdata + iter callback offset: skipdata then troubleshooting
- regs_access + arch support: operands-registers then arch skill /
  troubleshooting
- AArch64 rename during port: v6-migration then options-syntax
- Selective registration + HPPA/Xtensa: size-optimized then arch-hppa /
  arch-xtensa (no public `cs_arch_register_*` for those)

## What not to invent

- No mutex around a shared `csh`.
- No `cs_option(CS_OPT_DETAIL, CS_OPT_OFF)` as a working disable path.
- No claim that skipdata callback signatures behave identically in
  `cs_disasm` and `cs_disasm_iter` regarding `code`/`offset`.
- No `cs_arch_register_hppa` / `cs_arch_register_xtensa` in current tree.
