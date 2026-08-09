# Capstone TriCore reference

## Modes

Disallowed mask:

```
~(CS_MODE_TRICORE_110 | CS_MODE_TRICORE_120 | CS_MODE_TRICORE_130 |
  CS_MODE_TRICORE_131 | CS_MODE_TRICORE_160 | CS_MODE_TRICORE_161 |
  CS_MODE_TRICORE_162 | CS_MODE_TRICORE_180 | CS_MODE_LITTLE_ENDIAN)
```

| Mode | ISA |
| --- | --- |
| `CS_MODE_TRICORE_110` | TriCore 1.1 |
| `CS_MODE_TRICORE_120` | TriCore 1.2 |
| `CS_MODE_TRICORE_130` | TriCore 1.3 |
| `CS_MODE_TRICORE_131` | TriCore 1.3.1 |
| `CS_MODE_TRICORE_160` | TriCore 1.6 |
| `CS_MODE_TRICORE_161` | TriCore 1.6.1 |
| `CS_MODE_TRICORE_162` | TriCore 1.6.2 |
| `CS_MODE_TRICORE_180` | TriCore 1.8.0 |

`TriCore_getFeatureBits()` switches on the **entire** `mode` value against one
of those constants. Pass exactly one version flag (optionally OR `0` for LE).
`CS_MODE_BIG_ENDIAN` is not allowed.

Mode `0` opens (mask allows it) but enables no version features — decode fails
for normal opcodes. Always set a version.

Instruction length is 2 or 4 bytes; default skipdata size is **2**.

## Runtime options

`TRICORE_option` (**replace**, not OR):

- `CS_OPT_SYNTAX` → `handle->syntax = value`
- `CS_OPT_MODE` → `handle->mode = value` (after core mask check)

Other arch-routed types return OK without side effects. Core options
(`CS_OPT_DETAIL`, skipdata, …) work as usual.

## Detail / operands

`cs_tricore`:

- `op_count`, `operands[NUM_TRICORE_OPS]` (`8`)
- `update_flags` — true when the insn updates the flags register

`cs_tricore_op`:

| Field | Notes |
| --- | --- |
| `type` | `TRICORE_OP_REG`, `IMM`, `MEM` |
| `reg` / `imm` / `mem` | `mem.base` (uint8_t), `mem.disp` (int64_t) |
| `access` | `cs_ac_type` (irrelevant in DIET builds) |

Registers: address `A0–A15`, data `D0–D15`, extended `E*`, pair `P*`, plus
`FCX`, `PC`, `PCXI`, `PSW`.

## Alias and regs_access

| Feature | Support |
| --- | --- |
| Alias name map | Empty stub only |
| `is_alias` / `alias_id` | Not used |
| Operand `access` | Yes |
| `TriCore_reg_access` | Yes — implicit detail lists + explicit REG/MEM base |

Some access annotations in fixtures are marked `# fixme`; treat access as
best-effort when debugging mismatches.

## Workflows

1. Open with the target TriCore generation (`_162` is common in tests/AURIX).
2. Enable detail; walk REG/MEM operands and optional `update_flags`.
3. Switch versions at runtime with `cs_option(CS_OPT_MODE, CS_MODE_TRICORE_xxx)`
   if the mask accepts the value.
4. Use `cs_regs_access` for combined read/write sets.

## Pitfalls

- Big-endian open fails (`CS_ERR_MODE`).
- Wrong version → many instructions decode as invalid even if bytes are fine.
- Combining multiple version bits yields a mode that matches none of the
  `case CS_MODE_TRICORE_*` arms in `TriCore_getFeatureBits`.
- `mem.base` is a register id; compare against TriCore register enums, not ARM.

## Source map

- Mask / skip size: `cs.c`
- Init/options: `arch/TriCore/TriCoreModule.c`
- Features: `TriCore_getFeatureBits` in `TriCoreDisassembler.c`
- Mapping / regs_access: `TriCoreMapping.c`
- Public types: `include/capstone/tricore.h`
- Fixtures: `tests/details/tricore.yaml`
- cstool: `tc110` … `tc180`
