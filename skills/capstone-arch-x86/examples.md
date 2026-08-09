# Capstone x86 — examples

## x86-64 Intel detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_X86, CS_MODE_64, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, len, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_x86 *x = &insn[i].detail->x86;
	/* x->prefix, x->modrm, x->encoding, x->operands */
}
cs_free(insn, n);
cs_close(&handle);
```

## ATT syntax (when built)

```c
cs_err e = cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_ATT);
if (e == CS_ERR_X86_ATT || e == CS_ERR_DIET) {
	/* fall back to Intel */
	cs_option(handle, CS_OPT_SYNTAX, CS_OPT_SYNTAX_INTEL);
}
```

## Switch 32 → 64 at runtime

```c
cs_option(handle, CS_OPT_MODE, CS_MODE_64); /* replaces mode */
```

## Relative address helper

```c
uint64_t target = X86_REL_ADDR(insn[i]);
```

## cstool

```text
cstool x16 0x...
cstool x32 0x...
cstool x64 0x...
cstool x64att 0x...
```
