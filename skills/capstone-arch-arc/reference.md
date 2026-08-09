# Capstone ARC — reference

## Allowed mode mask

From `CS_ARCH_CONFIG_ARC` in `cs.c`:

```
~(CS_MODE_LITTLE_ENDIAN)
```

Only LE (`0`) is valid. Big-endian and all other mode bits fail.

Skipdata default stride: **2** bytes (insn lengths 2/4/6/8).

## Runtime options (`ARC_option`)

| Option | Behavior |
|--------|----------|
| `CS_OPT_MODE` | `handle->mode = value` |
| `CS_OPT_SYNTAX` | `handle->syntax \|= value` |
| Other | ignored (returns OK) |

No ARC-specific options or syntax flags. SoftFail supported in disassembler.

## `cs_arc` summary

Header: `include/capstone/arc.h`.

| Field | Role |
|-------|------|
| `op_count` | operand count |
| `operands[8]` | `cs_arc_op` (`type`, `reg`/`imm`, `access`) |

### Operand types

`ARC_OP_INVALID`, `ARC_OP_REG`, `ARC_OP_IMM` only.

### Memory and CC (flattened)

Internal op groups (`ARCGenCSOpGroup.inc`): `Operand`, `PredicateOperand`,
`MemOperandRI`, `BRCCPredicateOperand`, `CCOperand`, `U6`.

- **MemOperandRI**: base → REG, offset → IMM (not a MEM type).
- **Predicate / CC**: numeric IMM from private `ARCCC_*` / BRCC codes in
  `arch/ARC/ARCInfo.h` — not exposed in public header.

Example from `tests/details/arc.yaml` (`mov.eq`): IMM `1` (CC), REG write,
REG read; `regs_read` includes `status32`.

### Groups

`ARC_GRP_JUMP`, `CALL`, `RET`, `BRANCH_RELATIVE`.

Writeback is not a `cs_arc` field; addressing mode is in the mnemonic
(`.aw` / `.ab`). `detail->writeback` may still be set for cstool.

## Alias support

Effectively none:

- `printAliasInstr` stub always returns false.
- No `ARC_INS_ALIAS_*` enums.
- No `is_alias` / `alias_id` population under `arch/ARC/`.
- Conditional suffixes are real encodings / printer text.

## Register access

- `ud->reg_access = ARC_reg_access` (non-DIET).
- Merges implicits (`detail->regs_read`/`regs_write`) with explicit `ARC_OP_REG`
  by `access`.
- IMM/CC operands do not contribute to explicit access lists.
- Requires detail ON.

## Registers

Public enum includes `BLINK`, `FP`, `GP`, `ILINK`, `SP`, `R0`–`R25`, `R30`,
`R32`–`R63`, `STATUS32`. Gaps: no `R26`–`R29`, `R31` (use special names).

## Evidence pointers

- Details: `tests/details/arc.yaml`
- MC: `tests/MC/ARC/` (`alu_arc`, `compact_arc`, `ldst_arc`, `br_arc`, …)
- Module/mapping: `arch/ARC/ARCModule.c`, `ARCMapping.c`, `ARCDisassembler.c`
- Private CC: `arch/ARC/ARCInfo.h`
