# Capstone WASM reference

## Modes

| Mode | Result |
| --- | --- |
| `0` / `CS_MODE_LITTLE_ENDIAN` | Valid (only supported open mode) |
| Any non-zero bit | `cs_open` → `CS_ERR_MODE` |

`CS_ARCH_CONFIG_WASM` sets `arch_disallowed_mode_mask = 0`, so every mode bit is
disallowed at the `cs_open` mask check. `WASM_global_init` also rejects
`ud->mode != 0` with `CS_ERR_MODE`.

Endian is not a WASM concept here; `CS_MODE_LITTLE_ENDIAN` works only because it
is `0`.

## Runtime options

`WASM_option()` unconditionally returns `CS_ERR_OPTION`.

Implications:

- `CS_OPT_MODE` / `CS_OPT_SYNTAX` → `CS_ERR_OPTION` (reach arch hook).
- `CS_OPT_DETAIL`, `CS_OPT_SKIPDATA`, `CS_OPT_SKIPDATA_SETUP`, `CS_OPT_UNSIGNED`,
  `CS_OPT_MNEMONIC`, `CS_OPT_ONLY_OFFSET_BRANCH` are handled in core `cs_option`
  before the arch hook and succeed.

Default skipdata size for WASM is **1** byte.

## Detail / operands

`cs_wasm`:

- `op_count`
- `operands[2]` of `cs_wasm_op`

`wasm_op_type`:

| Type | Payload |
| --- | --- |
| `WASM_OP_IMM` | `immediate[2]` |
| `WASM_OP_NONE` | none |
| `WASM_OP_INT7` | `int7` |
| `WASM_OP_VARUINT32` | `varuint32` |
| `WASM_OP_VARUINT64` | `varuint64` |
| `WASM_OP_UINT32` | `uint32` |
| `WASM_OP_UINT64` | `uint64` |
| `WASM_OP_BRTABLE` | `brtable` (`length`, `address`, `default_target`) |

Each operand also has `size` (encoded immediate width in bytes).

Groups (from `wasm.h`): `WASM_GRP_NUMBERIC`, `WASM_GRP_PARAMETRIC`,
`WASM_GRP_VARIABLE`, `WASM_GRP_MEMORY`, `WASM_GRP_CONTROL`.

There are no register operands. Instruction IDs match primary opcode values
(e.g. `WASM_INS_GET_LOCAL = 0x20`). Header typos (`WASN_INS_I64_GT_S`,
`WASP_INS_I32_TRUNC_S_F32`, `WASM_INS_I32_WARP_I64`) exist in the public enum;
use the defined names as-is.

## Alias and regs_access

| Feature | Support |
| --- | --- |
| `is_alias` / `alias_id` | No |
| Operand `access` | No |
| `detail->regs_read` / `regs_write` | Not populated for WASM |
| `ud->reg_access` | Not set in `WASM_global_init` |
| `cs_regs_access` | Returns `CS_ERR_ARCH` (no `reg_access` callback) |

## Workflows

1. Disassemble function bodies / opcode streams with mode `0` + detail ON.
2. Switch on `detail->wasm.operands[i].type` for immediates and `br_table`.
3. Use groups to classify control vs variable vs numeric ops.
4. For invalid bytes, enable skipdata (1-byte default) rather than inventing modes.

## Pitfalls

- Passing `CS_MODE_32`, Thumb-style flags, or any non-zero mode fails open.
- Do not call `cs_option(..., CS_OPT_MODE, ...)` expecting success.
- Do not use `cs_regs_access` or assume register read/write lists.
- Detail tests omit operands for zero-operand ops (`i32.eqz`, `end`); check
  `op_count` before indexing.
- Alignment / skip size is 1 (`cs.c` `skipdata_size`).

## Source map

- Mask / registration: `cs.c` (`CS_ARCH_CONFIG_WASM`, `cs_arch_register_wasm`)
- Init / options: `arch/WASM/WASMModule.c`
- Public types: `include/capstone/wasm.h`
- Fixtures: `tests/details/wasm.yaml`, `tests/unit/wasm_brtable_size.c`
