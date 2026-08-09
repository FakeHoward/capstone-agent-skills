---
name: capstone-arch-tricore
description: >-
  Guides Capstone TriCore (CS_ARCH_TRICORE) disassembly: exact version modes
  1.1–1.8.0, little-endian only, runtime MODE/SYNTAX, detail operands with
  access and update_flags, and regs_access. Use when working with TriCore,
  TC1.6.2, Infineon AURIX, tricore.h, or CS_ARCH_TRICORE.
---

# Capstone arch: TriCore

Source of truth: sibling Capstone tree — `include/capstone/tricore.h`,
`arch/TriCore/TriCoreModule.c`, `TriCoreDisassembler.c` feature bits,
`cs.c` (`CS_ARCH_CONFIG_TRICORE`), `tests/details/tricore.yaml`.

## Hard rules

- Supported versions (exactly one): `CS_MODE_TRICORE_110`, `_120`, `_130`,
  `_131`, `_160`, `_161`, `_162`, `_180`.
- Endian: little-endian only (`CS_MODE_LITTLE_ENDIAN` / `0`). Big-endian is
  rejected by the mode mask.
- Runtime `CS_OPT_MODE` / `CS_OPT_SYNTAX` **replace** (`handle->mode` /
  `handle->syntax = value` in `TRICORE_option`). Pass the full mode each time.
- Detail: `insn->detail->tricore` — REG/IMM/MEM, per-operand `access`,
  `update_flags`.
- `cs_regs_access` supported via `TriCore_reg_access`.
- No real Capstone aliases (`alias_insn_names` empty; `is_alias` unused).

## Quick open

```c
csh handle;
cs_open(CS_ARCH_TRICORE, CS_MODE_TRICORE_162, &handle);
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## More

- Versions, options, operands, pitfalls: [reference.md](reference.md)
- API / cstool snippets: [examples.md](examples.md)
