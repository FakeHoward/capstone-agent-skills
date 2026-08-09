# Capstone AArch64 — examples

## Default LE open

```c
csh handle;
if (cs_open(CS_ARCH_AARCH64, 0, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## Apple proprietary encodings

```c
cs_open(CS_ARCH_AARCH64, CS_MODE_APPLE_PROPRIETARY, &handle);
/* or later: */
cs_option(handle, CS_OPT_MODE, CS_MODE_APPLE_PROPRIETARY);
```

## Explicit wide immediates

```c
cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_AARCH64_EXPLICIT_WIDE_IMM);
```

## Reading sysreg / vector detail

```c
cs_aarch64 *a64 = &insn->detail->aarch64;
for (int i = 0; i < a64->op_count; i++) {
	cs_aarch64_op *op = &a64->operands[i];
	if (op->type == AARCH64_OP_SYSREG)
		; /* op->sysop */
	if (op->is_vreg)
		; /* interpret reg as V; check op->vas */
}
```

## Compat include (legacy ARM64 names)

```c
#define CAPSTONE_AARCH64_COMPAT_HEADER
#include <capstone/capstone.h>
/* cs_arm64 / ARM64_* available via arm64.h path */
```

## cstool

```text
cstool arm64 0x...
cstool aarch64+apple 0x...
cstool aarch64+regalias 0x...
```
