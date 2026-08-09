# Core API examples

## Check support then open

```c
if (!cs_support(CS_ARCH_AARCH64)) {
    fputs("AArch64 not built into this Capstone\n", stderr);
    return 1;
}

csh h;
if (cs_open(CS_ARCH_AARCH64, CS_MODE_LITTLE_ENDIAN, &h) != CS_ERR_OK) {
    fprintf(stderr, "%s\n", cs_strerror(CS_ERR_ARCH));
    return 1;
}
cs_close(&h);
```

## Custom allocator before open

```c
cs_opt_mem mem = {
    .malloc = my_malloc,
    .calloc = my_calloc,
    .realloc = my_realloc,
    .free = my_free,
    .vsnprintf = vsnprintf,
};
cs_option(0, CS_OPT_MEM, (uintptr_t)&mem);

csh h;
cs_err e = cs_open(CS_ARCH_X86, CS_MODE_32, &h);
```

## Report last error after failed disasm

```c
size_t n = cs_disasm(h, code, size, addr, 0, &insn);
if (n == 0) {
    fprintf(stderr, "%s\n", cs_strerror(cs_errno(h)));
}
```
