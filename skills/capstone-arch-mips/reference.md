# Capstone MIPS — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_MIPS` in `cs.c` (allowed = complement of this mask):

```
CS_MODE_LITTLE_ENDIAN | CS_MODE_BIG_ENDIAN |
CS_MODE_MIPS16 | CS_MODE_MIPS32 | CS_MODE_MIPS64 |
CS_MODE_MICRO | CS_MODE_MIPS1 | CS_MODE_MIPS2 |
CS_MODE_MIPS32R2 | CS_MODE_MIPS32R3 | CS_MODE_MIPS32R5 |
CS_MODE_MIPS32R6 | CS_MODE_MIPS3 | CS_MODE_MIPS4 |
CS_MODE_MIPS5 | CS_MODE_MIPS64R2 | CS_MODE_MIPS64R3 |
CS_MODE_MIPS64R5 | CS_MODE_MIPS64R6 | CS_MODE_OCTEON |
CS_MODE_OCTEONP | CS_MODE_NANOMIPS | CS_MODE_NMS1 |
CS_MODE_I7200 | CS_MODE_MIPS_NOFLOAT | CS_MODE_MIPS_PTR64
```

Note `CS_MODE_NMS1` / `CS_MODE_I7200` already include `CS_MODE_NANOMIPS`.
`CS_MODE_MICRO32R3` = `MICRO | MIPS32R3`; `MICRO32R6` = `MICRO | MIPS32R6`.

## Runtime option behavior (`Mips_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode = (cs_mode)value` (replace) |
| `CS_OPT_SYNTAX` | bitwise OR into `handle->syntax` |

## `cs_mips` summary

`#define NUM_MIPS_OPS 16`.

```c
typedef struct cs_mips {
	uint8_t op_count;
	cs_mips_op operands[NUM_MIPS_OPS];
} cs_mips;
```

`cs_mips_op`:

| Field | Role |
|-------|------|
| `type` | `MIPS_OP_REG` / `IMM` / `MEM` |
| `reg` / `imm` / `uimm` / `mem` | payload |
| `is_reglist` | register list membership |
| `is_unsigned` | choose `uimm` vs signed `imm` |
| `access` | `cs_ac_type` (diet: irrelevant) |

`mips_op_mem`: `base`, `disp`.

## Alias support

MIPS is Auto-Sync. Prefer `CS_OPT_DETAIL_REAL` when alias operands must not be used.

## Register access

`Mips_global_init` sets `Mips_reg_access` unless `CAPSTONE_DIET`.

## Skipdata

4 bytes.

## Evidence pointers

- `tests/details/mips.yaml` — MIPS32R5 BE, MIPS64 LE, etc.
- `tests/MC/Mips/`
- `docs/cs_v6_release_guide.md` — Mips syntax/`uimm` notes
- `arch/Mips/` — Auto-Sync mapping/printer
