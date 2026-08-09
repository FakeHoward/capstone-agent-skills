# Capstone M68K — reference

## Source map

| Item | Location |
|------|----------|
| Header | `include/capstone/m68k.h` |
| Module | `arch/M68K/M68KModule.c` |
| Feature gating | `arch/M68K/M68KDisassembler.h` (`m68k_has_feature`) |
| Mode apply | `M68KDisassembler.c` (~5422): `handle->mode & CS_MODE_M68K_FEATURE_MASK` |
| Config | `cs.c` `CS_ARCH_CONFIG_M68K` |
| Tests | `tests/details/m68k.yaml` |

## Allowed mode mask

```c
~(CS_MODE_BIG_ENDIAN | CS_MODE_M68K_FEATURE_MASK)
```

`CS_MODE_M68K_FEATURE_MASK` = 000|010|020|030|040|060|CPU32|COLDFIRE
(ColdFire expands to ISA_A/A+/B/C, USP, DIV, MAC, EMAC, EMAC_B, FPU).

## Runtime MODE no-op

```c
cs_err M68K_option(cs_struct *handle, cs_opt_type type, size_t value)
{
	return CS_ERR_OK;
}
```

Core does not assign `handle->mode` for `CS_OPT_MODE`; only arch_option can.
M68K never updates it → reopen required.

## Default CPU

```c
features = handle->mode & CS_MODE_M68K_FEATURE_MASK;
if (!features)
	features = CS_MODE_M68K_000;
```

## Operand highlights

- `M68K_OP_MEM` + `m68k_op_mem` (base/index/disp/scale/bitfield/…)
- `M68K_OP_BR_DISP` + `m68k_op_br_disp`
- `M68K_OP_REG_PAIR`, `M68K_OP_REG_BITS` (`register_bits` for movem)
- `M68K_BF_*` helpers for bitfield offset/width encoding
- `op_size.type`: `M68K_SIZE_TYPE_CPU` / `FPU`

## regs_access

Set in `M68K_global_init` unless `CAPSTONE_DIET`. Tests under
`tests/details/m68k.yaml` include `regs_read` / `regs_impl_read` expectations.

## Skipdata

Alignment skip size **2** (`cs.c` / `ud->skipdata_size = 2` in module).

## cstool names

`m68k`, `m68k10`…`m68k60`, `m68kcpu32`, `m68kcf`, `m68kcfv1`…`m68kcfv5`.
