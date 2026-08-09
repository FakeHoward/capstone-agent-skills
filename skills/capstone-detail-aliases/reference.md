# Detail / alias reference

## Bit values (`cs_opt_value`)

| Symbol | Value |
| --- | --- |
| `CS_OPT_OFF` | `0` |
| `CS_OPT_ON` | `1 << 0` |
| `CS_OPT_DETAIL_REAL` | `1 << 1` (same numeric bit as `CS_OPT_SYNTAX_DEFAULT`) |

`DETAIL_REAL` is only meaningful as a `CS_OPT_DETAIL` value (combined with
`CS_OPT_ON`), not as a syntax flag.

## Truth table for `usesAliasDetails`

| `CS_OPT_ON` | `CS_OPT_DETAIL_REAL` | Alias insn detail |
| --- | --- | --- |
| 0 | * | No detail allocation / unused |
| 1 | 0 | Alias details (`usesAliasDetails == true` when alias) |
| 1 | 1 | Real details (`usesAliasDetails == false`) |

Because options OR together, enabling REAL later on an already-ON handle
latches REAL permanently on that handle.

## Interaction with diet builds

Diet engines omit many name/detail paths; detail-dependent helpers return
`CS_ERR_DIET`. Check `cs_support(CS_SUPPORT_DIET)`.

## cstool

- `-d` detail
- `-r` → `CS_OPT_DETAIL_REAL | CS_OPT_ON`

## Tests to read

- `tests/unit/riscv_reg_access.c` — `DETAIL_REAL | ON`
- `tests/unit/riscv_op_count_iter.c` — detail before `cs_malloc`
- `tests/integration/test_iter.c` — detail + iter pattern
