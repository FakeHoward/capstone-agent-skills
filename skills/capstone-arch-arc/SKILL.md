---
name: capstone-arch-arc
description: >-
  Guides Capstone ARC disassembly: little-endian only, cs_arc REG/IMM detail,
  flattened memory/CC operands, empty aliases, and cs_regs_access. Use when
  working with CS_ARCH_ARC, arc.h, ARCModule, or ARC Capstone decode.
---

# Capstone ARC

Load only this skill for ARC work. Do not pull other architecture skills.

## Source of truth

Sibling Capstone tree (`capstone/`):

- `include/capstone/arc.h` — `cs_arc` (REG/IMM only)
- `arch/ARC/ARCModule.c` — init, mode assign, `reg_access`
- `cs.c` — `CS_ARCH_CONFIG_ARC`, skipdata 2
- `tests/details/arc.yaml`, `tests/MC/ARC/`

## Valid modes

Allowed: **`CS_MODE_LITTLE_ENDIAN` only** (value `0`). Any other mode bit
(including big-endian) → `CS_ERR_MODE` / `CS_ERR_OPTION`.

No `CS_MODE_ARC_*`. Compact and normal forms coexist without a mode flag.

`ARC_option`: `CS_OPT_MODE` **assigns**; `CS_OPT_SYNTAX` **ORs**. No ARC-specific
options.

## Options and detail

- Detail → `insn->detail->arc` (up to 8 ops)
- Ops: `ARC_OP_REG`, `ARC_OP_IMM` only — **no `ARC_OP_MEM`**
- Memory printed as `[base, offset]` but detail is flat REG + IMM
- Predicates / CC stored as IMM (private `ARCCC_*`; no public CC enum)
- Aliases: **none** (`printAliasInstr` stub returns false; no `ARC_INS_ALIAS_*`)
- `cs_regs_access`: **supported** (non-DIET)
- Groups: `JUMP`, `CALL`, `RET`, `BRANCH_RELATIVE`

## Workflow

1. Open `CS_ARCH_ARC` + `CS_MODE_LITTLE_ENDIAN`.
2. Enable detail for operands / access / groups.
3. Reconstruct memory from adjacent REG+IMM; treat CC as IMM.
4. Use `cs_regs_access` for aggregate regs (implicits include `status32`).

## Traps

- BE open fails.
- Suffixes (`.eq`, `.f`, `.aw`, `.ab`) are encodings/mnemonics, not Capstone aliases.
- Variable length 2/4/6/8; skipdata stride **2**.
- Register enum gaps: no `R26`–`R29`/`R31`; use `FP`/`SP`/`BLINK`/etc.

## More

- Modes, structs, traps: [reference.md](reference.md)
- Open/disasm snippets: [examples.md](examples.md)
