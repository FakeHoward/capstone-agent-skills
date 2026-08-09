# Operands / registers examples

## Full register access

```c
cs_regs regs_read, regs_write;
uint8_t nread = 0, nwrite = 0;
cs_err e = cs_regs_access(h, insn, regs_read, &nread, regs_write, &nwrite);
if (e == CS_ERR_ARCH) {
    /* arch has no reg_access implementation */
} else if (e != CS_ERR_OK) {
    fprintf(stderr, "%s\n", cs_strerror(e));
}
```

## Implicit-only check

```c
if (cs_reg_read(h, insn, X86_REG_RSP)) {
    /* RSP implicitly read */
}
```

## Safe guard before helpers

```c
if (!insn->id || !insn->detail) {
    /* skipdata or detail off / missing pointer */
    return;
}
```
