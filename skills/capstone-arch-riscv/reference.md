# Capstone RISC-V — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_RISCV` in `cs.c`:

```
~(CS_MODE_RISCV32 | CS_MODE_RISCV64 | CS_MODE_RISCV_C |
  CS_MODE_RISCV_FD | CS_MODE_RISCV_V | CS_MODE_RISCV_ZFINX |
  CS_MODE_RISCV_ZCMP_ZCMT_ZCE | CS_MODE_RISCV_ZICFISS |
  CS_MODE_RISCV_E | CS_MODE_RISCV_A | CS_MODE_RISCV_COREV |
  CS_MODE_RISCV_SIFIVE | CS_MODE_RISCV_THEAD |
  CS_MODE_RISCV_VENTANA | CS_MODE_RISCV_ZBA |
  CS_MODE_RISCV_ZBB | CS_MODE_RISCV_ZBC | CS_MODE_RISCV_ZBKB |
  CS_MODE_RISCV_ZBKC | CS_MODE_RISCV_ZBKX | CS_MODE_RISCV_ZBS)
```

## Defect: `CS_MODE_RISCV_BITMANIP`

| Item | Fact |
|------|------|
| Enum | `CS_MODE_RISCV_BITMANIP = 1 << 13` in `capstone.h` |
| cstool | `+bitmanip` maps to that flag (`cstool/cstool.c`) |
| Allowed mask | **not listed** in `CS_ARCH_CONFIG_RISCV` |
| Result | `cs_open` / `CS_OPT_MODE` rejects with `CS_ERR_MODE` / `CS_ERR_OPTION` |

Working replacements for bit-manipulation coverage:

- Standard: `CS_MODE_RISCV_ZBA`, `ZBB`, `ZBC`, `ZBKB`, `ZBKC`, `ZBKX`, `ZBS`
- CORE-V XCVbitmanip tests: use `CS_MODE_RISCV_COREV` (YAML name `CS_MODE_RISCV_XCVBITMANIP` maps to `COREV` in `suite/cstest`)

Do not recommend `CS_MODE_RISCV_BITMANIP` or `+bitmanip` as a functional enable path.

## Runtime option behavior (`RISCV_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode = (cs_mode)value` (replace) |
| `CS_OPT_SYNTAX` | bitwise OR into `handle->syntax` |

## `cs_riscv` summary

`#define NUM_RISCV_OPS 8`.

| Field | Role |
|-------|------|
| `need_effective_addr` | EA required |
| `op_count` / `operands[8]` | operand list |
| `rounding_mode` | `riscv_rounding_mode` (`RNE`…`DYN`, or `INVALID`) |

Operand types: `REG`, `IMM`, `MEM`, `FP`, `CSR` (`CS_OP_SPECIAL`).

`cs_riscv_op` union: `reg`, `imm`, `dimm`, `mem` (`base`/`disp`), `csr` (`uint16_t`), plus `access`.

## Alias support

Auto-Sync. Asm-text controls (from `docs/cs_v6_release_guide.md`):

| Options | Behavior |
|---------|----------|
| neither | print aliases (default) |
| `NO_ALIAS_TEXT` only | no aliases |
| `NO_ALIAS_TEXT_COMPRESSED` only | aliases for non-compressed; exact text for compressed |
| both | same as `NO_ALIAS_TEXT` only (`NO_ALIAS_TEXT` wins) |

Detail operand alias vs real: `CS_OPT_DETAIL_REAL | CS_OPT_ON`.

## Register access

`RISCV_global_init` always sets `ud->reg_access = RISCV_reg_access` in the current module (not wrapped in `#ifndef CAPSTONE_DIET`). Unit coverage: `tests/unit/riscv_reg_access.c`. Diet builds may still restrict related detail surfaces via core diet checks.

## Skipdata

- With `CS_MODE_RISCV_C`: 2
- Else: 4

## Evidence pointers

- `tests/details/riscv.yaml` — alias text, RV32/64, extensions
- `tests/MC/RISCV/` — including XCVbitmanip with `COREV`
- `tests/unit/riscv_sysreg.c`, `riscv_op_count_iter.c`, `riscv_insn_name_segv.c`
- `arch/RISCV/RISCVDisassemblerExtension.c` — `CS_MODE_RISCV_FD` gating
- `docs/cs_v6_release_guide.md` — RISC-V mode/alias sections
