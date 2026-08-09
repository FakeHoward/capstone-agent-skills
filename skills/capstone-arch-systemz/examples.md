# Capstone SystemZ — examples

## Modern API with Z14 feature level

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_SYSTEMZ,
	CS_MODE_BIG_ENDIAN | CS_MODE_SYSTEMZ_Z14, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_systemz *z = &insn[i].detail->systemz;
	/* z->cc, z->format, z->operands[].mem.am */
}
cs_free(insn, n);
cs_close(&handle);
```

## Allow-all features (legacy open)

```c
/* No CPU mode bit → feature gate allows all */
cs_open(CS_ARCH_SYSTEMZ, CS_MODE_BIG_ENDIAN, &handle);
```

## Compatibility header

```c
#define CAPSTONE_SYSTEMZ_COMPAT_HEADER
#include <capstone/capstone.h>

csh handle;
cs_open(CS_ARCH_SYSZ, CS_MODE_BIG_ENDIAN, &handle);
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
/* use insn->detail->sysz, SYSZ_OP_*, SYSZ_AM_BDX */
```

## regs_access — unsupported

```c
/* Expect CS_ERR_ARCH */
cs_regs_access(handle, &insn[i], regs_read, &rc, regs_write, &wc);
```

## Mode OR pitfall

```c
cs_open(CS_ARCH_SYSTEMZ, CS_MODE_BIG_ENDIAN | CS_MODE_SYSTEMZ_Z13, &handle);
cs_option(handle, CS_OPT_MODE, CS_MODE_SYSTEMZ_Z14);
/* bits accumulate; may match no exact feature-gate case → allow all */
```

Reopen to switch CPU level cleanly.

## cstool

Prefer Capstone mode constants in tests (`CS_MODE_SYSTEMZ_Z15`, …). Decorative
MC strings like `"zEC12"` are not mode enums.
