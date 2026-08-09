# Capstone SH reference

## Modes

Disallowed mask (`cs.c`):

```
~(CS_MODE_SH2 | CS_MODE_SH2A | CS_MODE_SH3 | CS_MODE_SH4 |
  CS_MODE_SH4A | CS_MODE_SHFPU | CS_MODE_SHDSP | CS_MODE_BIG_ENDIAN)
```

| Flag | Role |
| --- | --- |
| `CS_MODE_SH2` … `CS_MODE_SH4A` | ISA level (bit scan in `isalevel()`) |
| `CS_MODE_SHFPU` | Enable FPU opcodes |
| `CS_MODE_SHDSP` | Enable DSP opcodes |
| `CS_MODE_BIG_ENDIAN` | Big-endian fetch |
| `CS_MODE_LITTLE_ENDIAN` (`0`) | Little-endian (default) |

`isalevel()` skips the endian bit, then returns the lowest set ISA bit among
SH2→SH4A. Mode `0` / bare BE yields `ISA_ALL` (SH1-class base).

Typical combinations (also in `cstool`):

- SH2A+FPU BE: `CS_MODE_SH2A | CS_MODE_SHFPU | CS_MODE_BIG_ENDIAN`
- SH4A+FPU LE: `CS_MODE_SH4A | CS_MODE_SHFPU`
- SH4A+DSP+FPU: add `CS_MODE_SHDSP`

Do not set multiple ISA level bits; behavior follows the lowest set bit.

## Runtime options

`SH_option()` always returns `CS_ERR_OK` and never mutates the handle.

| Option | Behavior |
| --- | --- |
| `CS_OPT_MODE` | Mask-checked in core; then no-op. Mode stays at `cs_open` value |
| `CS_OPT_SYNTAX` | Accepted, ignored |
| `CS_OPT_DETAIL` etc. | Core handling (works) |

**To change ISA/endian/FPU/DSP: `cs_close` + `cs_open` with the new mode.**

## Detail / operands

`cs_sh`:

- `insn` (`sh_insn`), `size`, `op_count`, `operands[3]`

`sh_op_type`: `SH_OP_REG`, `SH_OP_IMM`, `SH_OP_MEM`.

`sh_op_mem`:

- `address` (`sh_op_mem_type`: reg-ind, post/pre, disp, R0-indexed, GBR,
  PC-relative, TBR, …)
- `reg`, `disp`

DSP ops use `SH_INS_DSP` with `sh_op_dsp` in the operand union (`insn`,
operands, registers, `cc`, `imm`, `size`).

Groups include jump/call/ret plus ISA groups (`SH_GRP_SH2A`, `SH_GRP_SH4A`, …).

## Alias and regs_access

| Feature | Support |
| --- | --- |
| Capstone `is_alias` | No |
| Operand `access` | No on `cs_sh_op` |
| `detail->regs_read` / `regs_write` | Yes, filled during decode |
| `SH_reg_access` / `cs_regs_access` | Yes (copies detail lists) |

## Workflows

1. Choose ISA + optional FPU/DSP + endian at open (match firmware).
2. Enable detail; inspect `detail->sh.operands` and `regs_read`/`regs_write`.
3. For FPU/DSP instructions, ensure `CS_MODE_SHFPU` / `CS_MODE_SHDSP` or decode
   will reject those encodings.
4. Switch profiles by reopening — do not rely on `CS_OPT_MODE`.

## Pitfalls

- Silent MODE no-op: `cs_option(CS_OPT_MODE, …)` can return OK while leaving the
  old ISA active.
- Missing `SHFPU`/`SHDSP` looks like “bad bytes”, not an option error.
- Endian mismatches garbled 16-bit opcode pairs; SH2A detail tests use BE.
- Instruction size is normally 2; SH2A can decode 32-bit encodings when mode
  includes `CS_MODE_SH2A`.

## Source map

- Mask: `cs.c` `CS_ARCH_CONFIG_SH`
- Init/options: `arch/SH/SHModule.c`
- Decode / regs: `arch/SH/SHDisassembler.c` (`isalevel`, `SH_reg_access`)
- Public types: `include/capstone/sh.h`
- Fixtures: `tests/details/sh.yaml`
