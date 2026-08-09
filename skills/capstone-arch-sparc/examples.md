# Capstone SPARC — examples

## Big-endian V8-ish with detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_SPARC, CS_MODE_BIG_ENDIAN, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_sparc *s = &insn[i].detail->sparc;
	/* s->cc, s->hint, s->operands[0..s->op_count) */
}
cs_free(insn, n);
cs_close(&handle);
```

## V9 (forces 64-bit via option path)

```c
cs_open(CS_ARCH_SPARC, CS_MODE_BIG_ENDIAN | CS_MODE_V9, &handle);
```

## Little-endian (sparcle)

```c
cs_open(CS_ARCH_SPARC, CS_MODE_LITTLE_ENDIAN, &handle);
/* or CS_MODE_LITTLE_ENDIAN | CS_MODE_V9 */
```

## Real operands for aliases

```c
cs_option(handle, CS_OPT_DETAIL, CS_OPT_DETAIL_REAL | CS_OPT_ON);
```

## regs_access — unsupported

```c
/* Expect CS_ERR_ARCH: SPARC has no reg_access hook */
cs_regs_access(handle, &insn[i], regs_read, &rc, regs_write, &wc);
```

Use per-operand `op->access` instead when detail is on.

## cstool

```text
cstool sparc 0x...
cstool sparcle 0x...
cstool sparc+v9 0x...
```
