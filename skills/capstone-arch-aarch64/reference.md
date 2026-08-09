# Capstone AArch64 — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_AARCH64` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_ARM | CS_MODE_BIG_ENDIAN |
  CS_MODE_APPLE_PROPRIETARY)
```

`CS_MODE_APPLE_PROPRIETARY` = `1 << CS_MODE_VENDOR_AARCH64_BIT0` (bit 30).
`CS_MODE_BIG_ENDIAN` = `1U << 31`.

## Runtime option behavior (`AArch64_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | bitwise OR into `handle->mode` |
| `CS_OPT_SYNTAX` | bitwise OR into `handle->syntax` |

## `cs_aarch64` summary

Header: `include/capstone/aarch64.h`. `#define NUM_AARCH64_OPS 16`.

| Field | Role |
|-------|------|
| `cc` | `AArch64CC_CondCode` (`EQ == 0`; `Invalid` non-zero) |
| `update_flags` | flag update |
| `post_index` | with `detail->writeback` |
| `is_doing_sme` | SME/SVE edit marker |
| `op_count` / `operands[]` | operand list |

### Operand highlights (`aarch64_op_type`)

Common: `REG`, `IMM`, `MEM`, `MEM_REG`, `MEM_IMM`, `FP`, `PRED`.

System / special: `CIMM`, `REG_MRS`/`REG_MSR`, `SVCR`, `AT`, `DB`, `DC`, `ISB`, `TSB`, `PRFM` / SVE PRFM / `RPRFM`, PSTATE immediates, `PSB`, `BTI`, `SME`, `IMM_RANGE`, `TLBI`, `IC`, `DBNXS`, `EXACTFPIMM`, `SYSREG`, `SYSIMM`, `SYSALIAS`.

`cs_aarch64_op` also carries `shift`, `ext`, `vas` (`AArch64Layout_VectorLayout`), `is_vreg`, `sme`, `pred`, `sysop`, `access`, `is_list_member`.

## Compatibility

- `CS_ARCH_ARM64` is an alias of `CS_ARCH_AARCH64`.
- `include/capstone/arm64.h` provides legacy names when `CAPSTONE_AARCH64_COMPAT_HEADER` is defined before include.

## Alias support

Auto-Sync architecture. Use `is_alias` / `alias_id` / `usesAliasDetails`. Prefer `CS_OPT_DETAIL_REAL | CS_OPT_ON` for real operand sets.

Asm-text alias control for wide immediates: `CS_OPT_SYNTAX_AARCH64_EXPLICIT_WIDE_IMM`.

## Register access

`AArch64_global_init` installs `AArch64_reg_access` unless `CAPSTONE_DIET`. `cs_regs_access` → `CS_ERR_ARCH` if callback missing; diet → `CS_ERR_DIET`.

## Skipdata

Always 4 bytes for AArch64.

## Evidence pointers

- `tests/details/aarch64.yaml` — MRS/MSR/sysalias, vector lists, writeback
- `tests/MC/AArch64/`
- `docs/cs_v6_release_guide.md` — AArch64 (formerly ARM64) section
- `arch/AArch64/` — disassembler, printer, mapping
