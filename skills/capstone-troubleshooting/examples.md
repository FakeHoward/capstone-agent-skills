# Troubleshooting examples

## Xtensa skipdata workaround callback

```c
static size_t CAPSTONE_API xtensa_skip(const uint8_t *code, size_t code_size,
                                       size_t offset, void *user)
{
    (void)code; (void)offset; (void)user;
    if (code_size == 0)
        return 0;
    return 1; /* explicit; do not rely on default 255 */
}

cs_opt_skipdata s = { .mnemonic = ".byte", .callback = xtensa_skip };
cs_option(h, CS_OPT_SKIPDATA, CS_OPT_ON);
cs_option(h, CS_OPT_SKIPDATA_SETUP, (uintptr_t)&s);
```

## Detect latched detail

```c
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);
cs_option(h, CS_OPT_DETAIL, CS_OPT_OFF); /* still on */
/* reopen if non-detail decode is required */
cs_close(&h);
cs_open(arch, mode, &h);
```

## Distinguish regs_access failures

```c
cs_err e = cs_regs_access(h, insn, r, &nr, w, &nw);
if (e == CS_ERR_ARCH) {
    /* unsupported arch — not a transient failure */
} else if (e == CS_ERR_DETAIL) {
    /* forgot CS_OPT_DETAIL or malloc order */
} else if (e == CS_ERR_SKIPDATA) {
    /* insn->id == 0 */
}
```
