# Capstone EVM — reference

## Source map

| Item | Location |
|------|----------|
| Header | `include/capstone/evm.h` |
| Module | `arch/EVM/EVMModule.c` |
| Config | `cs.c` `CS_ARCH_CONFIG_EVM` → `arch_disallowed_mode_mask = 0` |
| Op helpers | `cs.c` `CS_ARCH_EVM` cases: empty / `#if 0` |
| Tests | `tests/details/evm.yaml` |

## Mode reject

```c
cs_err EVM_global_init(cs_struct *ud)
{
	if (ud->mode)
		return CS_ERR_MODE;
	/* … */
}
```

Mask `0` means `mode & mask` never fails in `cs_open`; the module enforces
mode == 0.

## Detail struct

```c
typedef struct cs_evm {
	unsigned char pop;
	unsigned char push;
	unsigned int fee;
} cs_evm;
```

## Groups

| Group | Role |
|-------|------|
| `EVM_GRP_JUMP` | jumps |
| `EVM_GRP_MATH` | arithmetic |
| `EVM_GRP_STACK_WRITE` / `STACK_READ` | stack effects |
| `EVM_GRP_MEM_WRITE` / `MEM_READ` | memory |
| `EVM_GRP_STORE_WRITE` / `STORE_READ` | storage |
| `EVM_GRP_HALT` | halt |

## No registers / operands

- No `evm_reg` enum
- No operand array on `cs_evm`
- `cs_regs_access` unsupported
- PUSH immediates appear in disassembly text/bytes, not as `CS_OP_IMM` detail ops

## Option handler

```c
cs_err EVM_option(cs_struct *handle, cs_opt_type type, size_t value)
{
	return CS_ERR_OK;
}
```

## Skipdata

**1** byte.
