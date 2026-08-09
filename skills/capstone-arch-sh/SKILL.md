---
name: capstone-arch-sh
description: >-
  Guides Capstone SuperH (CS_ARCH_SH) disassembly: ISA modes SH2–SH4A with
  optional FPU/DSP/endian, CS_OPT_MODE no-op requiring reopen, detail memory
  operands, and regs_access via detail lists. Use when working with SuperH,
  SH2A, SH4A, SHFPU, SHDSP, sh.h, or CS_ARCH_SH.
---

# Capstone arch: SH

Source of truth: sibling Capstone tree — `include/capstone/sh.h`,
`arch/SH/SHModule.c`, `arch/SH/SHDisassembler.c`, `cs.c` (`CS_ARCH_CONFIG_SH`),
`tests/details/sh.yaml`, `cstool/cstool.c` SH entries.

## Hard rules

- Allowed mode bits: `CS_MODE_SH2`, `SH2A`, `SH3`, `SH4`, `SH4A`, `SHFPU`,
  `SHDSP`, `CS_MODE_BIG_ENDIAN` (plus LE as `0`).
- Pick ISA level at `cs_open`. Combine one ISA bit with optional `SHFPU` /
  `SHDSP` and endian.
- `CS_OPT_MODE` validates then returns OK but **does not update** `handle->mode`
  (`SH_option` is a no-op). Reopen to change mode.
- Detail: `insn->detail->sh` (`cs_sh`). `cs_sh_op` has no `access` field.
- `cs_regs_access` copies `detail->regs_read` / `regs_write` filled at decode.
- No Capstone alias fields.

## Quick open

```c
csh handle;
cs_open(CS_ARCH_SH, CS_MODE_SH4A | CS_MODE_SHFPU, &handle); /* LE default */
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## More

- Modes, options, operands, pitfalls: [reference.md](reference.md)
- API / cstool snippets: [examples.md](examples.md)
