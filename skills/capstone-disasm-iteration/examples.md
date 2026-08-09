# Disasm examples

## Batch

```c
cs_insn *insns;
size_t n = cs_disasm(handle, code, size, 0x1000, 0, &insns);
if (n == 0) {
    fprintf(stderr, "%s\n", cs_strerror(cs_errno(handle)));
    return;
}
for (size_t i = 0; i < n; i++) {
    printf("0x%" PRIx64 ": %s %s\n",
           insns[i].address, insns[i].mnemonic, insns[i].op_str);
}
cs_free(insns, n);
```

## Iter with detail (correct order)

```c
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
cs_insn *insn = cs_malloc(handle);
const uint8_t *cur = code;
size_t left = size;
uint64_t addr = 0x1000;

while (cs_disasm_iter(handle, &cur, &left, &addr, insn)) {
    printf("%s\t%s\n", insn->mnemonic, insn->op_str);
    if (insn->detail) {
        /* implicit regs / groups */
    }
}
cs_free(insn, 1);
```

## Wrong order (broken detail pointer)

```c
cs_insn *insn = cs_malloc(handle);                 /* detail == NULL */
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);       /* too late for this insn */
/* iter may fill fields, but insn->detail remains NULL */
```
