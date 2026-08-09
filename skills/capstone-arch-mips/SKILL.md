---
name: capstone-arch-mips
description: >-
  Guides Capstone MIPS disassembly: ISA/micro/nano mode matrix, endianness,
  cs_mips operands, aliases, and regs_access. Use when the task involves
  CS_ARCH_MIPS, include/capstone/mips.h, MipsModule, CS_MODE_MIPS32/64/MICRO/
  NANOMIPS, or MIPS syntax options NO_DOLLAR/NOREGNAME.
---

# Capstone MIPS

Load only this skill for MIPS. Do not pull other architecture skills.

## Source of truth

Sibling Capstone tree (`capstone/`):

- `include/capstone/mips.h` — `cs_mips`
- `arch/Mips/MipsModule.c`
- `cs.c` — `CS_ARCH_CONFIG_MIPS`
- `tests/details/mips.yaml`, `tests/MC/Mips/`

## Valid modes

Allowed bits include endian plus width/ISA/ASE flags:

- Endian: `CS_MODE_LITTLE_ENDIAN` (0), `CS_MODE_BIG_ENDIAN`
- Width aliases: `CS_MODE_MIPS16` (=16), `CS_MODE_MIPS32` (=32), `CS_MODE_MIPS64` (=64)
- ASE: `CS_MODE_MICRO`, `CS_MODE_NANOMIPS`, `CS_MODE_NMS1`, `CS_MODE_I7200`
- ISA ladder: `MIPS1`…`MIPS5`, `MIPS32R2`…`R6`, `MIPS64R2`…`R6`
- Vendor/extra: `OCTEON`, `OCTEONP`, `MIPS_NOFLOAT`, `MIPS_PTR64`
- Combos: `CS_MODE_MICRO32R3`, `CS_MODE_MICRO32R6`

Runtime `CS_OPT_MODE` **replaces** the full mode word (`handle->mode = value`). Pass the complete combination each time.

## Options and syntax

- Detail / `CS_OPT_DETAIL_REAL` for alias vs real operands
- `CS_OPT_SYNTAX_NO_DOLLAR` — omit `$` on register names
- `CS_OPT_SYNTAX_NOREGNAME` — numeric GPR names where applicable
- Module ORs syntax flags (`syntax |=`)
- Skipdata stride: 4

## Detail, alias, regs_access

- Detail: `insn->detail->mips` — up to 16 ops: `REG`/`IMM`/`MEM`
- `cs_mips_op`: `imm` / `uimm`, `is_unsigned`, `is_reglist`, `access`
- Auto-Sync alias fields supported
- `cs_regs_access`: supported (`Mips_reg_access`, not in DIET)

## Workflow

1. Choose endian + ISA/ASE carefully (e.g. `CS_MODE_MIPS32R6 | CS_MODE_BIG_ENDIAN`).
2. `cs_open(CS_ARCH_MIPS, mode, &handle)`.
3. Enable detail; set `NO_DOLLAR` / `NOREGNAME` if consumers expect that text.
4. On mode change, pass the full new mask via `CS_OPT_MODE` (replace semantics).
5. For nano/micro firmware, include `NANOMIPS` / `MICRO` (and matching R3/R6 combo macros).

## Traps

- Replace semantics: `CS_OPT_MODE` with only `CS_MODE_MICRO` drops prior ISA/endian bits.
- Mode bit values collide with other arches in the shared `cs_mode` enum; never OR foreign arch flags.
- Wrong ISA revision changes which encodings decode.
- `#undef mips` in `mips.h` exists because GCC toolchains define a `mips` macro.

## More

- Full allowed mask and operand notes: [reference.md](reference.md)
- Snippets: [examples.md](examples.md)
