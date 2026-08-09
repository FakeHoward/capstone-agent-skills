# Capstone WASM examples

## Minimal disasm with detail

```c
#include <capstone/capstone.h>

csh h;
cs_insn *insn;
size_t n;
uint8_t code[] = { 0x20, 0x00, 0x41, 0x20, 0x0b }; /* get_local 0; i32.const 0x20; end */

if (cs_open(CS_ARCH_WASM, 0, &h) != CS_ERR_OK)
    return;
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(h, code, sizeof(code), 0, 0, &insn);
for (size_t i = 0; i < n; i++) {
    cs_wasm *w = &insn[i].detail->wasm;
    printf("%s %s (ops=%u)\n", insn[i].mnemonic, insn[i].op_str, w->op_count);
    for (uint8_t o = 0; o < w->op_count; o++) {
        if (w->operands[o].type == WASM_OP_VARUINT32)
            printf("  varuint32=0x%x size=%u\n",
                   w->operands[o].varuint32, w->operands[o].size);
    }
}
cs_free(insn, n);
cs_close(&h);
```

## Mode / option failures

```c
csh h;
/* fails: CS_ERR_MODE */
cs_open(CS_ARCH_WASM, CS_MODE_BIG_ENDIAN, &h);

cs_open(CS_ARCH_WASM, 0, &h);
/* fails: CS_ERR_OPTION (arch hook) */
cs_option(h, CS_OPT_MODE, 0);
cs_option(h, CS_OPT_SYNTAX, CS_OPT_SYNTAX_DEFAULT);
cs_close(&h);
```

## cstool

```bash
cstool -d wasm "20 00 41 20 10 c9 01 45 0b"
```

Expected shape (from `tests/details/wasm.yaml`): `get_local`, `i32.const`,
`call`, `i32.eqz`, `end` with `WASM_OP_VARUINT32` where immediates exist.

## br_table operand

When detail shows `WASM_OP_BRTABLE`, read:

```c
cs_wasm_brtable *t = &op->brtable;
/* t->length, t->address, t->default_target */
```
