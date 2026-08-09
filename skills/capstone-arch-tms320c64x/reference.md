# Capstone TMS320C64x — reference

## Source map

| Item | Location |
|------|----------|
| Header | `include/capstone/tms320c64x.h` |
| Module | `arch/TMS320C64x/TMS320C64xModule.c` |
| Decode | `TMS320C64xDisassembler.c` (`readBytes32`, 4-byte) |
| Config | `cs.c` `CS_ARCH_CONFIG_TMS320C64X` → `~(LE\|BE)` |
| Tests | `tests/details/tms320c64x.yaml` |

## Option handler

```c
case CS_OPT_MODE:
	handle->mode |= (cs_mode)value;
	break;
case CS_OPT_SYNTAX:
	handle->syntax |= (int)value;
	break;
```

## Detail fields (YAML mapping)

Tests assert:

- `funit_unit` / `funit_side` / `parallel`
- `cond_reg` / `cond_zero`
- MEM: `mem_base`, `mem_disptype`, `mem_disp_const`, `mem_unit`,
  `mem_direction`, `mem_modify`, `mem_scaled`

## Operand types

```c
TMS320C64X_OP_INVALID
TMS320C64X_OP_REG
TMS320C64X_OP_IMM
TMS320C64X_OP_REGPAIR   /* CS_OP_SPECIAL + 0 */
TMS320C64X_OP_MEM
```

REGPAIR: `reg` holds the first register of the pair.

## Mem enums

- `tms320c64x_mem_disp`: CONSTANT / REGISTER
- `tms320c64x_mem_dir`: FW / BW
- `tms320c64x_mem_mod`: NO / PRE / POST

## regs_access

No callback registered → `CS_ERR_ARCH`.

## Skipdata

**4** bytes.

## cstool

- `tms320c64x` → big endian
- `tms320c64xle` → little endian
