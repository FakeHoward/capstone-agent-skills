# v6 migration examples

## Native v6 AArch64 open

```c
#include <capstone/capstone.h>

csh h;
cs_open(CS_ARCH_AARCH64, CS_MODE_LITTLE_ENDIAN, &h);
```

## Dual-tree compat open

```c
#define CAPSTONE_AARCH64_COMPAT_HEADER
#define CAPSTONE_SYSTEMZ_COMPAT_HEADER
#include <capstone/capstone.h>

csh h;
cs_open(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, &h);
cs_open(CS_ARCH_SYSZ, CS_MODE_BIG_ENDIAN, &h2);
```

## Update alias checks

```c
/* pre-v6: often compared insn->id to alias enum values as "real" ids */
/* v6: */
if (insn->is_alias) {
    use_alias_id(insn->alias_id);
    use_real_id(insn->id);
}
```
