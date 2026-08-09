# Capstone LoongArch — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_LOONGARCH` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_LOONGARCH32 | CS_MODE_LOONGARCH64)
```

`LoongArch_getFeatureBits`: only `LoongArch_Feature64Bit` is mode-gated;
other features always true.

Skipdata / alignment: **4** bytes.

## Runtime options (`LoongArch_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode = value` |
| `CS_OPT_SYNTAX` | `handle->syntax \|= value` |
| Other | ignored (returns OK) |

Useful syntax: `CS_OPT_SYNTAX_NOREGNAME`, `CS_OPT_SYNTAX_NO_DOLLAR`.

## `cs_loongarch` summary

Header: `include/capstone/loongarch.h`.

| Field | Role |
|-------|------|
| `format` | `LOONGARCH_INSN_FORM_*` |
| `op_count` / `operands[8]` | operand list |

### Operand types

`LOONGARCH_OP_REG`, `IMM`, `MEM`.

`loongarch_op_mem`: `base`, `index`, `disp`. Per-op `access`.

### Post-decode rewrites

1. **Memory** — REG+IMM or REG+REG collapsed to one `MEM` for loads/stores/AMO/…
2. **Address** — direct branches: IMM rewritten to absolute (`imm += address`)
3. **Groups** — `JUMP`/`CALL`/`RET`/`INT`/`IRET`/`PRIVILEGE` + feature groups
   (`LOONGARCH_FEATURE_ISLA64`, …)

## Partial alias support

Public IDs between `LOONGARCH_INS_ALIAS_BEGIN` … `END`:

| Alias | Real insn | Notes |
|-------|-----------|-------|
| `NOP` | `ANDI` | text + MC |
| `MOVE` | `OR` | text + MC |
| `RET` | `JIRL` | default alias detail often empty ops |
| `JR` | `JIRL` | one-reg form |
| `LA` / `LA_GLOBAL` / `LA_LOCAL` | PseudoLA_* | assembler pseudos; rare from raw decode |

What works: asm text, `is_alias` / `alias_id`, MC `pseudos.s.yaml`, issues tests
for `ret` ± `CS_OPT_DETAIL_REAL`.

What is partial:

- Default alias details for `ret` can be `operands: []`.
- `LA*` targets assembler pseudos, not normal 4-byte binary decode.
- Group logic for `JIRL` depends on alias operand count (0 → RET, 1 → JUMP).
- Release guide still marks LoongArch aliases incomplete — treat as beta/partial.

ABI register name aliases (`ZERO`/`RA`/`SP`/`A0`… → `R*`) are separate and full.

## Register access

- `ud->reg_access = LoongArch_reg_access` (non-DIET).
- Merges implicits + explicit `REG` + `MEM.base` (and writeback base).
- **Gap:** `mem.index` is not added to the read set.

## Evidence pointers

- Details: `tests/details/loongarch.yaml`
- Issues: `tests/issues/issues.yaml` (#2349 MEM rewrites; alias `ret`)
- MC: `tests/MC/LoongArch/` (mostly LA64)
- Mapping: `arch/LoongArch/LoongArchMapping.c`
- Docs: `docs/cs_v6_release_guide.md`
