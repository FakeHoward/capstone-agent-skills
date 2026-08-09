# Capstone Xtensa — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_XTENSA` in `cs.c`:

```
~(CS_MODE_XTENSA_ESP32 | CS_MODE_XTENSA_ESP32S2 |
  CS_MODE_XTENSA_ESP8266 | CS_MODE_XTENSA_ESP32S3)
```

`CS_MODE_BIG_ENDIAN` (bit 31) is disallowed. LE (`0`) is fine.

Chip modes are not mutually exclusive at the API level; `CS_OPT_MODE` ORs them.

## Feature / chip gating

`Xtensa_getFeatureBits`:

- `FeatureESP32S3Ops` / `FeatureHIFI3` → only with `CS_MODE_XTENSA_ESP32S3`
- `FeatureDensity` → always true
- default → true (allow most features)

SR/UR validity in `CheckRegister` depends on chip mode. Decode sizes: density
16-bit → core 24-bit → S3 24/32 → HiFi3 24/48 (S3-gated).

## Runtime options (`Xtensa_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode \|= value` (**OR**, not replace) |
| `CS_OPT_SYNTAX` | `handle->syntax \|= value` |
| `CS_OPT_LITBASE` | `handle->LITBASE = (uint32_t)value` |

### LITBASE

`cs_priv.h`: LSB indicates “set”. Resolution in `Xtensa_L32R_Value`:

- If `LITBASE & 1`: `(LITBASE & 0xfffff000) + InstrOff`
- Else: `(((addr + 3) & ~3) + InstrOff)` (PC-relative default; LITBASE = 0)

Detail type for L32R targets: `XTENSA_OP_L32R` with absolute in `.imm`.

Integration: `tests/integration/test_litbase.c`.

## Skipdata — current-tree warning only

`skipdata_size()` has no Xtensa case → default `(uint8_t)-1` = **255**.

This is a **gap/bug in the current tree**, not correct architecture behavior.
Do not treat 255 as intended Xtensa skip alignment. Prefer
`CS_OPT_SKIPDATA_SETUP` with an explicit size/callback.

## `cs_xtensa` summary

Header: `include/capstone/xtensa.h`.

| Field | Role |
|-------|------|
| `format` | `XTENSA_INSN_FORM_*` (`RRR`, `RRI8`, `CALL`, …) |
| `op_count` / `operands[8]` | operand list |

### Operand types

`XTENSA_OP_REG`, `IMM`, `MEM` (`base`/`disp`), `L32R`.

Per-op `access`. Groups: `CALL`/`JUMP`/`RET` + `XTENSA_FEATURE_HAS*`.

Notable regs: `XTENSA_REG_LITBASE`, `XTENSA_REG_SP` (printed as `a1`).

## Alias support

Generated `PRINT_ALIAS_INSTR` table exists in `XtensaGenAsmWriter.inc`, but
`XtensaInstPrinter.c` does not define `PRINT_ALIAS_INSTR` — aliases inactive.
Hand case: `WSR` to `INTERRUPT` → `wsr <reg>, intset`.

## Register access

- `ud->reg_access = Xtensa_reg_access` (non-DIET).
- Merges implicits + `REG` + `MEM.base` (writeback writes base).
- Used by cstool / cstest.

## Missing public arch registration (HPPA and Xtensa)

`CAPSTONE_USE_ARCH_REGISTRATION` builds export `cs_arch_register_*` for other
arches but **not** `cs_arch_register_xtensa` (and not `cs_arch_register_hppa`).
Selective registration cannot enable Xtensa; keep `CAPSTONE_XTENSA_SUPPORT` on
the default (non-selective) arch table, or add a `CS_ARCH_REGISTER(XTENSA)`
helper. Empty arch slot → `CS_ERR_ARCH` from `cs_open`.

## Evidence pointers

- Details: `tests/details/xtensa.yaml`
- MC: `tests/MC/Xtensa/` (`l32r.yaml`, `esp32s3.s.yaml`, …)
- LITBASE: `tests/integration/test_litbase.c`
- Module/mapping: `arch/Xtensa/XtensaModule.c`, `XtensaMapping.c`
