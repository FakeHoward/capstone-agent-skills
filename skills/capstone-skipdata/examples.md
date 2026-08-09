# Skipdata examples

## Batch callback (absolute offset)

```c
static size_t CAPSTONE_API on_data(const uint8_t *code, size_t code_size,
                                   size_t offset, void *user)
{
    (void)user;
    if (offset >= code_size)
        return 0;
    return 1; /* skip one byte at absolute offset */
}

cs_opt_skipdata s = { .mnemonic = "db", .callback = on_data };
cs_option(h, CS_OPT_SKIPDATA, CS_OPT_ON);
cs_option(h, CS_OPT_SKIPDATA_SETUP, (uintptr_t)&s);
```

## Iter-safe callback

```c
static size_t CAPSTONE_API on_data_iter(const uint8_t *code, size_t code_size,
                                        size_t offset, void *user)
{
    (void)offset; /* engine passes 0 */
    (void)user;
    if (!code_size)
        return 0;
    return 1; /* code points at current remaining bytes */
}
```

## Consume data records safely

```c
if (insn->id == 0) {
    /* data: use insn->bytes[0 .. insn->size) only */
    continue;
}
```
