# Capstone Alpha reference

## Modes

Disallowed mask:

```
~(CS_MODE_LITTLE_ENDIAN | CS_MODE_BIG_ENDIAN)
```

| Mode | Meaning |
| --- | --- |
| `CS_MODE_LITTLE_ENDIAN` (`0`) | Default LE (MC tests: `insn-alpha.s.yaml`) |
| `CS_MODE_BIG_ENDIAN` | Byte-swapped 32-bit words (`insn-alpha-be.s.yaml`) |

No EV4/EV5/EV6 mode bits exist in Capstone. Alignment / default skip size is
**4** bytes.

## Runtime options

`ALPHA_option` (**replace**, not OR):

- `CS_OPT_SYNTAX` → `handle->syntax = value`
- `CS_OPT_MODE` → `handle->mode = value` (mask-checked in core first)

Use runtime MODE to flip endian without recreating other options, or reopen —
both work for Alpha.

## Detail / operands

`cs_alpha`:

- `op_count`
- `operands[NUM_ALPHA_OPS]` (`3`)

`cs_alpha_op`:

| Field | Notes |
| --- | --- |
| `type` | `ALPHA_OP_REG` or `ALPHA_OP_IMM` only (no MEM type) |
| `reg` / `imm` | Register id or immediate |
| `access` | `cs_ac_type` |

Memory-form asm (`ldah $29,2($27)`) is modeled as REG + IMM + REG, not
`OP_MEM`.

Registers: integer `R0–R31` (printed as `$0`… / ABI names) and FP `F0–F31`.

Groups mapped: call, jump, branch_relative.

## Alias and regs_access

| Feature | Support |
| --- | --- |
| `printAliasInstr` | Stub always `false` |
| Special alias name map | Commented out / unused |
| `is_alias` / `alias_id` | Not populated |
| Operand `access` | Yes |
| Implicit `regs_read` / `regs_write` | Yes (mapping tables) |
| `Alpha_reg_access` | Merges implicit + explicit REG ops |

Detail tests show implicit writes (e.g. `$28`) alongside operand registers.

## Workflows

1. Open LE or BE to match the image; enable detail.
2. Walk `detail->alpha.operands`; treat base+disp loads as REG/IMM/REG triples.
3. Call `cs_regs_access` when you need the full read/write set including
   implicits.
4. Flip endian with `CS_OPT_MODE` if streaming mixed corpora.

## Pitfalls

- There is no `ALPHA_OP_MEM` — do not search for a mem union field.
- Wrong endian yields different mnemonics/operands for the same byte string;
  compare LE/BE fixtures in `tests/details/alpha.yaml`.
- Do not expect Capstone alias metadata even if LLVM-style alias printing exists
  in the tree; the generated alias printer is a no-op.

## Source map

- Mask: `cs.c` `CS_ARCH_CONFIG_ALPHA`
- Init/options: `arch/Alpha/AlphaModule.c`
- Mapping / regs_access: `arch/Alpha/AlphaMapping.c`
- Public types: `include/capstone/alpha.h`
- Fixtures: `tests/details/alpha.yaml`, `tests/MC/Alpha/`
- cstool: `alpha`, `alphabe`
