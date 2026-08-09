# Capstone MOS65XX — reference

## Source map

| Item | Location |
|------|----------|
| Header | `include/capstone/mos65xx.h` |
| Module | `arch/MOS65XX/MOS65XXModule.c` |
| Config mask | `cs.c` `CS_ARCH_CONFIG_MOS65XX` |
| Tests | `tests/details/mos65xx.yaml` |
| cstool | `6502`, `65c02`, `w65c02`, `65816` → `LONG_MX` |

## Allowed mask

```c
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_MOS65XX_6502 |
  CS_MODE_MOS65XX_65C02 | CS_MODE_MOS65XX_W65C02 |
  CS_MODE_MOS65XX_65816_LONG_MX)
```

`LONG_MX` = `LONG_M | LONG_X` (bits 5 and 6). Bit 4
(`CS_MODE_MOS65XX_65816`) is **not** in the allowed set.

## Mode option logic

```c
if (value & CS_MODE_MOS65XX_6502)   cpu = 6502;
if (value & CS_MODE_MOS65XX_65C02)  cpu = 65C02;
if (value & CS_MODE_MOS65XX_W65C02) cpu = W65C02;
if (value & (CS_MODE_MOS65XX_65816 | LONG_M | LONG_X))
	cpu = 65816;
long_m = !!(value & LONG_M);
long_x = !!(value & LONG_X);
handle->mode = (cs_mode)value;  /* replace */
```

Open with `mode == 0` skips `MOS65XX_option` and keeps default CPU **6502**.

## Troubleshooting: dead `CS_MODE_MOS65XX_65816`

`CS_MODE_MOS65XX_65816` (1<<4, “8-bit m/x”) appears in `capstone.h` and is
recognized inside `MOS65XX_option`, but the `cs.c` mask rejects that bit on
`cs_open` / `CS_OPT_MODE` (`CS_ERR_MODE` / `CS_ERR_OPTION`).

**User rule:** open 65816 with `LONG_M`, `LONG_X`, or `LONG_MX` only.
Treat bare `CS_MODE_MOS65XX_65816` as a dead public flag when diagnosing
unexpected `CS_ERR_MODE`.

Working 65816 paths used in-tree:

- cstool `"65816"` → `CS_MODE_MOS65XX_65816_LONG_MX`
- `tests/details/mos65xx.yaml` → `CS_MODE_MOS65XX_65816_LONG_MX`

## Detail

```c
typedef struct cs_mos65xx {
	mos65xx_address_mode am;
	bool modifies_flags;
	uint8_t op_count;
	cs_mos65xx_op operands[3];
} cs_mos65xx;
```

Address modes cover implied/acc/imm/relative/interrupt/block, zeropage and
absolute forms (including long and stack-relative for 65816).

## Syntax

| Value | Effect |
|-------|--------|
| `CS_OPT_SYNTAX_DEFAULT` | `hex_prefix = NULL` |
| `CS_OPT_SYNTAX_MOTOROLA` | `hex_prefix = "$"` |

## regs_access

Not registered → `CS_ERR_ARCH`.

## Skipdata

**1** byte.
