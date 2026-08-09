# Performance / concurrency examples

## Per-thread handles

```c
/* each thread: */
csh h;
cs_open(CS_ARCH_X86, CS_MODE_64, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);
cs_insn *insn = cs_malloc(h);
/* decode loop */
cs_free(insn, 1);
cs_close(&h);
```

## Global allocator install (single-threaded init)

```c
static cs_opt_mem mem = {
    .malloc = my_malloc,
    .calloc = my_calloc,
    .realloc = my_realloc,
    .free = my_free,
    .vsnprintf = vsnprintf,
};

void capstone_init(void) {
    cs_option(0, CS_OPT_MEM, (uintptr_t)&mem);
}
```

## Hot loop without detail

```c
csh h;
cs_open(CS_ARCH_X86, CS_MODE_64, &h); /* detail stays off */
cs_insn *insn = cs_malloc(h);
while (cs_disasm_iter(h, &p, &n, &addr, insn)) {
    sink(insn->mnemonic, insn->op_str, insn->size);
}
cs_free(insn, 1);
cs_close(&h);
```
