# Capstone RISC-V — examples

## RV64 + compressed

```c
csh handle;
cs_mode mode = CS_MODE_RISCV64 | CS_MODE_RISCV_C;
if (cs_open(CS_ARCH_RISCV, mode, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## RV32 with atomics and float/double

```c
cs_mode mode = CS_MODE_RISCV32 | CS_MODE_RISCV_A | CS_MODE_RISCV_FD;
cs_open(CS_ARCH_RISCV, mode, &handle);
```

## Bit-manip via Z* flags (correct)

```c
cs_mode mode = CS_MODE_RISCV64 | CS_MODE_RISCV_ZBA | CS_MODE_RISCV_ZBB |
	CS_MODE_RISCV_ZBS;
cs_open(CS_ARCH_RISCV, mode, &handle);
```

## Dead flag — do not use

```c
/* Rejected by arch_disallowed_mode_mask */
cs_open(CS_ARCH_RISCV, CS_MODE_RISCV64 | CS_MODE_RISCV_BITMANIP, &handle);
```

## Suppress alias text

```c
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NO_ALIAS_TEXT);
/* or compressed-only: */
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_NO_ALIAS_TEXT_COMPRESSED);
```

## CSR operand

```c
cs_riscv_op *op = &insn->detail->riscv.operands[i];
if (op->type == RISCV_OP_CSR)
	use(op->csr);
```

## Replace mode with full mask

```c
cs_option(handle, CS_OPT_MODE,
	CS_MODE_RISCV64 | CS_MODE_RISCV_C | CS_MODE_RISCV_V);
```

## cstool

```text
cstool riscv32 0x...
cstool riscv64 0x...
cstool riscv64+c+zbb 0x...
```

Avoid `+bitmanip` (maps to the dead `CS_MODE_RISCV_BITMANIP` flag). Prefer `+zba`, `+zbb`, `+zbc`, `+zbs`, ….
