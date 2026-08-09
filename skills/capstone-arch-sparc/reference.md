# Capstone SPARC — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_SPARC` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_BIG_ENDIAN | CS_MODE_V9 |
  CS_MODE_64 | CS_MODE_32)
```

Any other mode bit → `CS_ERR_MODE` / `CS_ERR_OPTION`.

## V9 and endian (explicit)

### Endian

- Instruction words use `readBytes32` / `MODE_IS_BIG_ENDIAN`.
- Capstone default mode is **little-endian (`0`)**.
- Production SPARC binaries are almost always **big-endian**; prefer
  `CS_MODE_BIG_ENDIAN` unless targeting sparcle-style LE streams.
- LE is real and lightly tested (`sparcle`, MC LE fixtures).

### V9

- `CS_MODE_V9` selects `DecoderTableSparcV932`; else V8 table, then fallback
  `DecoderTableSparc32`.
- `Sparc_getFeatureBits`: only `Sparc_FeatureV9` is mode-gated; other features
  return true.
- `Sparc_option`: if `CS_MODE_V9` or `CS_MODE_64` is set, force
  `CS_MODE_64 | CS_MODE_V9`.

## Runtime options (`Sparc_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode \|= value` (+ V9/64 mutual force) |
| `CS_OPT_SYNTAX` | `handle->syntax = value` |
| Other | ignored (returns OK) |

No SPARC-specific syntax flags. No `CS_OPT_ALIAS`.

Skipdata default stride: **4** bytes.

## `cs_sparc` summary

Header: `include/capstone/sparc.h`.

| Field | Role |
|-------|------|
| `cc` | Condition code (`SPARC_CC_ICC_*`, FCC, CPCC, REG, …) |
| `cc_field` | `FCC0..3`, `ICC`, `XCC`, `NONE` |
| `hint` | `SPARC_HINT_A`, `PT`, `PN`, combinations |
| `format` | `SPARC_INSN_FORM_*` |
| `op_count` / `operands[6]` | operand list |

### Operand types

`SPARC_OP_REG`, `IMM`, `MEM` (`base`/`index`/`disp`), `MEMBAR_TAG`, `ASI`.

Each `cs_sparc_op` has `cs_ac_type access`.

### Groups / features

Generic `SPARC_GRP_*` plus `SPARC_FEATURE_IS64BIT`, `HASV9`, `HASVIS*`,
`HASCASA`, `HASPWRPSR`, `USESOFTMULDIV`.

## Alias support

- Large `SPARC_INS_ALIAS_*` range (`cmp`, `mov`, `ba`, `ret`, `cas`, …).
- Driven by Auto-Sync: `is_alias`, `alias_id`, `usesAliasDetails`.
- Alias detail vs real: `map_use_alias_details` — detail ON and not
  `CS_OPT_DETAIL_REAL`.

## Register access

- `Sparc_global_init` does **not** set `ud->reg_access`.
- `cs_regs_access` → `CS_ERR_ARCH`.
- Operand-level `access` and implicit `detail->regs_read` / `regs_write` may
  still be populated; the aggregate API is unsupported.
- Detail YAML has no `regs_read` / `regs_write` expectations for SPARC.

## Evidence pointers

- Details: `tests/details/sparc.yaml`
- MC: `tests/MC/Sparc/` (`*_big_endian*`, `*_v9_big_endian*`, LE sparcle file)
- Issues: `tests/issues/issues.yaml` (e.g. #2419 `cc` on conditional branches)
- Module / disasm: `arch/Sparc/SparcModule.c`, `SparcDisassembler.c`,
  `SparcDisassemblerExtension.c`
