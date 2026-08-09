# Capstone ARM — examples

## A32 LE with detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_ARM, CS_MODE_ARM, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_arm *arm = &insn[i].detail->arm;
	/* arm->cc, arm->operands[0..arm->op_count) */
}
cs_free(insn, n);
cs_close(&handle);
```

## Thumb + Cortex-M

```c
cs_open(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS, &handle);
```

## Thumb interworking (mode OR)

```c
cs_open(CS_ARCH_ARM, CS_MODE_ARM, &handle);
/* ... disassemble until state switch ... */
cs_option(handle, CS_OPT_MODE, CS_MODE_THUMB); /* bits OR'd in */
```

To return to A32-only decoding, reopen the handle; OR cannot clear `CS_MODE_THUMB`.

## Alias real operands

```c
cs_option(handle, CS_OPT_DETAIL, CS_OPT_DETAIL_REAL | CS_OPT_ON);
```

## regs_access

```c
cs_regs regs_read, regs_write;
uint8_t read_count, write_count;
if (cs_regs_access(handle, &insn[i],
		regs_read, &read_count,
		regs_write, &write_count) == CS_ERR_OK) {
	/* use counts */
}
```

## cstool

```text
cstool arm 0x...
cstool thumb 0x...
cstool arm+regalias 0x...
```
