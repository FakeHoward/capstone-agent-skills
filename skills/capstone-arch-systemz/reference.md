# Capstone SystemZ — reference

## Arch IDs

| Build | Symbol |
|-------|--------|
| Default | `CS_ARCH_SYSTEMZ` (= 2) |
| `#define CAPSTONE_SYSTEMZ_COMPAT_HEADER` | `CS_ARCH_SYSZ` (= 2) |

Detail union field: `detail->systemz` vs `detail->sysz`.

## Allowed mode mask

From `CS_ARCH_CONFIG_SYSTEMZ` in `cs.c`:

```
~(CS_MODE_BIG_ENDIAN |
  CS_MODE_SYSTEMZ_ARCH8..ARCH14 |
  CS_MODE_SYSTEMZ_Z10 | Z196 | ZEC12 | Z13 | Z14 | Z15 | Z16 |
  CS_MODE_SYSTEMZ_GENERIC)
```

`CS_MODE_LITTLE_ENDIAN` is `0` and is not rejected by the mask.

## Feature gating

`SystemZ_getFeatureBits(mode, feature)` clears `CS_MODE_BIG_ENDIAN`, then
matches exact Arch/Z pairs (higher levels include lower features).

- `ARCH8` / `Z10` / `GENERIC`: no gated features → false for those features.
- **No CPU bit set**: `return true` (allow all; legacy Capstone, issue #1992).

Paired levels: ARCH14/Z16 → … → ARCH8/Z10/GENERIC.

## Runtime options (`SystemZ_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode \|= value` |
| `CS_OPT_SYNTAX` | `handle->syntax = value` |

No SystemZ-specific syntax flags.

Skipdata default stride: **2** bytes.

## `cs_systemz` summary

Header: `include/capstone/systemz.h`.

| Field | Role |
|-------|------|
| `cc` | `SYSTEMZ_CC_*` |
| `format` | `SYSTEMZ_INSN_FORM_*` |
| `op_count` / `operands[6]` | operand list |

### Operand types

`SYSTEMZ_OP_REG`, `IMM`, `MEM`.

`systemz_op_mem`: `am`, `base`, `index`, `length`, `disp`.

Addressing modes: `SYSTEMZ_AM_BD`, `BDX`, `BDL`, `BDR`, `BDV`.

Per-op: `access`, `imm_width` (1–48 bits when known).

## Alias support

- Generated `SYSTEMZ_INS_ALIAS_BEGIN` … `END` (vector-style aliases).
- Printer sets `alias_id` via `map_set_alias_id`.
- Register aliases in header: none.

## Register access

- `SystemZ_global_init` does **not** set `ud->reg_access`.
- No `reg_access` under `arch/SystemZ/`.
- `cs_regs_access` → `CS_ERR_ARCH`.
- Per-operand `access` and implicit R/W mapping still exist.

## Compat header

`systemz_compatibility.h` mirrors `SYSZ_*`, `cs_sysz`, `NUM_SYSZ_OPS`.
Activated only when `CAPSTONE_SYSTEMZ_COMPAT_HEADER` is defined before
including Capstone. Integration test:
`tests/integration/compat_header/src/test_sysz_compatibility_header.c`.

## Evidence pointers

- Details: `tests/details/systemz.yaml` (often `CS_MODE_SYSTEMZ_ARCH14`)
- MC (literal files): `tests/MC/SystemZ/insns-z13.txt.yaml`,
  `insns-z14.txt.yaml`, `insns-z15.txt.yaml`, `insns-z16.txt.yaml`
  (plus `insns.txt.yaml`; real `CS_MODE_SYSTEMZ_Z*`)
- Feature bits: `arch/SystemZ/SystemZDisassemblerExtension.c`
- Mapping: `arch/SystemZ/SystemZMapping.c`
