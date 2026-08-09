# Capstone M680X — reference

## Source map

| Item | Location |
|------|----------|
| Header | `include/capstone/m680x.h` |
| Module validation | `arch/M680X/M680XModule.c` |
| Chip select | `arch/M680X/M680XDisassembler.c` (~2207–2241) |
| Config mask | `cs.c` `CS_ARCH_CONFIG_M680X` |
| Tests | `tests/details/m680x.yaml` |

## Init rules (not “exactly one”)

1. Reject unknown mode bits outside the chip set → `CS_ERR_MODE`
2. Require `(mode & chip_bits) != 0` — comment: *“At least the cpu type has to be selected. No default.”*
3. Multiple chip bits: accepted; decode uses first `else if` hit

## Priority when several chip modes are set

| Order | Mode bit | CPU type |
|------:|----------|----------|
| 1 | `CS_MODE_M680X_6800` | 6800 |
| 2 | `CS_MODE_M680X_6801` | 6801 |
| 3 | `CS_MODE_M680X_6805` | 6805 |
| 4 | `CS_MODE_M680X_6808` | 6808 |
| 5 | `CS_MODE_M680X_HCS08` | HCS08 |
| 6 | `CS_MODE_M680X_6809` | 6809 |
| 7 | `CS_MODE_M680X_6301` | 6301 |
| 8 | `CS_MODE_M680X_6309` | 6309 |
| 9 | `CS_MODE_M680X_6811` | 6811 |
| 10 | `CS_MODE_M680X_CPU12` | CPU12 |
| 11 | `CS_MODE_M680X_RS08` | RS08 |
| 12 | `CS_MODE_M680X_HCS12X` | HCS12X |

## Option handler

```c
cs_err M680X_option(cs_struct *handle, cs_opt_type type, size_t value)
{
	/* TODO */
	return CS_ERR_OK;
}
```

## Operand types

| Type | Detail |
|------|--------|
| `M680X_OP_REGISTER` | `reg` |
| `M680X_OP_IMMEDIATE` | `imm` |
| `M680X_OP_INDEXED` | `idx` (`base_reg`, `offset_reg`, `offset`, `offset_bits`, `inc_dec`, `flags`) |
| `M680X_OP_EXTENDED` | `ext.address`, `ext.indirect` |
| `M680X_OP_DIRECT` | `direct_addr` |
| `M680X_OP_RELATIVE` | `rel.address`, `rel.offset` |
| `M680X_OP_CONSTANT` | `const_val` (bit index, page, …) |

Indexed flags: `M680X_IDX_INDIRECT`, `NO_COMMA`, `POST_INC_DEC`.

## regs_access / groups

`M680X_reg_access` registered in module (non-DIET). Groups include JUMP, CALL,
RET, INT, IRET, BRAREL.

## Skipdata

**1** byte (`ud->skipdata_size = 1`).

## cstool

`m6800`, `m6801`, `m6805`, `m6808`, `m6809`, `m6811`, `cpu12`, `hd6301`,
`hd6309`, `hcs08`, `rs08`, `hcs12x`.
