# Capstone XCore — reference

## Source map

| Item | Location |
|------|----------|
| Public header | `include/capstone/xcore.h` |
| Module | `arch/XCore/XCoreModule.c` |
| Config mask | `cs.c` `CS_ARCH_CONFIG_XCORE` → `~(CS_MODE_BIG_ENDIAN)` |
| Skipdata | `cs.c` `skipdata_size`: arch → **2** |
| Detail tests | `tests/details/xcore.yaml` |
| cstool | `"xcore"` → `CS_ARCH_XCORE`, `CS_MODE_BIG_ENDIAN` |

## Mode mask

```c
#define CS_ARCH_CONFIG_XCORE \
	{ XCore_global_init, XCore_option, ~(CS_MODE_BIG_ENDIAN), }
```

Any mode bit other than big-endian fails `cs_open` / `CS_OPT_MODE` with
`CS_ERR_MODE` / `CS_ERR_OPTION`.

## Option handler

```c
cs_err XCore_option(cs_struct *handle, cs_opt_type type, size_t value)
{
	/* Do not set mode because only CS_MODE_BIG_ENDIAN is valid */
	return CS_ERR_OK;
}
```

## Detail shape

```c
typedef struct cs_xcore {
	uint8_t op_count;
	cs_xcore_op operands[8];
} cs_xcore;
```

Operand types align with `CS_OP_REG` / `CS_OP_IMM` / `CS_OP_MEM`.

Groups: `XCORE_GRP_JUMP` (generic jump group).

## regs_access

No `ud->reg_access` assignment in `XCore_global_init`. Core path:

```c
if (handle->reg_access) { ... }
else { return CS_ERR_ARCH; }
```

## Opcode helpers

`cs_op_count` / `cs_op_index` iterate `detail->xcore.operands[]` by
`xcore_op_type`.
