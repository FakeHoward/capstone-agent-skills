# Capstone ARM — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_ARM` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_ARM | CS_MODE_V8 |
  CS_MODE_MCLASS | CS_MODE_THUMB | CS_MODE_BIG_ENDIAN)
```

Any other mode bit → `CS_ERR_MODE` / `CS_ERR_OPTION`.

`CS_MODE_LITTLE_ENDIAN` and `CS_MODE_ARM` are both `0`.

## Runtime option behavior (`ARM_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | bitwise OR into `handle->mode` |
| `CS_OPT_SYNTAX` | bitwise OR into `handle->syntax` |
| Other | ignored (returns OK) |

## `cs_arm` summary

Header: `include/capstone/arm.h`.

| Field | Role |
|-------|------|
| `usermode` | LDM/STM user-mode regs |
| `vector_size` / `vector_data` | NEON/vector element info |
| `cps_mode` / `cps_flag` | CPS |
| `cc` | `ARMCC_CondCodes` (`ARMCC_EQ == 0`; invalid is non-zero) |
| `vcc` | VPT condition |
| `update_flags` | flag-writing insn |
| `post_index` | meaningful when `detail->writeback`; false → pre-index |
| `mem_barrier` | barrier option |
| `pred_mask` | IT/VPT block mask (`ARM_PredBlockMask`) |
| `op_count` / `operands[36]` | operand list |

### Operand types (`arm_op_type`)

`REG`, `IMM`, `FP`, `PRED`, `MEM`, plus specials: `CIMM`, `PIMM`, `SETEND`, `SYSREG`, `BANKEDREG`, `SPSR`, `CPSR`, `SYSM`, `VPRED_R`, `VPRED_N`.

`cs_arm_op`: `shift`, `subtracted`, `access`, `neon_lane`, `vector_index`, `sysop` for system operands.

## Alias support

ARM is Auto-Sync. Instruction aliases use:

- `cs_insn.is_alias`
- `cs_insn.alias_id`
- `cs_insn.usesAliasDetails`

Default detail operands follow the alias when applicable. Force real operands:

```c
cs_option(handle, CS_OPT_DETAIL, CS_OPT_DETAIL_REAL | CS_OPT_ON);
```

## Register access

- `ARM_global_init` sets `ud->reg_access = ARM_reg_access` unless `CAPSTONE_DIET`.
- `cs_regs_access` works with detail enabled and non-diet builds.
- Implicit regs also appear in `detail->regs_read` / `regs_write` when detail is on.

## Skipdata

`skipdata_size()`: Thumb → 2; otherwise → 4.

## Evidence pointers

- Details regression: `tests/details/arm.yaml`
- MC: `tests/MC/ARM/`
- Printer/disasm: `arch/ARM/ARMInstPrinter.c` / `.h`, `ARMDisassembler.c`,
  mapping under `arch/ARM/`
- v6 notes: `docs/cs_v6_release_guide.md` (ARM / Auto-Sync sections)
