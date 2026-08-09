# Capstone SH examples

## SH4A + FPU (little endian)

```c
#include <capstone/capstone.h>

csh h;
cs_insn *insn;
size_t n;
/* sample from tests/details/sh.yaml (starts with add r0,r1) */
uint8_t code[] = { 0x0c, 0x31, 0x10, 0x20 };

cs_open(CS_ARCH_SH, CS_MODE_SH4A | CS_MODE_SHFPU, &h);
cs_option(h, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(h, code, sizeof(code), 0x80000000, 0, &insn);
for (size_t i = 0; i < n; i++) {
    cs_regs r_read, r_write;
    uint8_t nr, nw;
    printf("%s %s\n", insn[i].mnemonic, insn[i].op_str);
    if (cs_regs_access(h, &insn[i], r_read, &nr, r_write, &nw) == CS_ERR_OK) {
        for (uint8_t k = 0; k < nr; k++)
            printf("  read %s\n", cs_reg_name(h, r_read[k]));
        for (uint8_t k = 0; k < nw; k++)
            printf("  write %s\n", cs_reg_name(h, r_write[k]));
    }
}
cs_free(insn, n);
cs_close(&h);
```

## MODE no-op — reopen to switch

```c
csh h;
cs_open(CS_ARCH_SH, CS_MODE_SH2 | CS_MODE_BIG_ENDIAN, &h);
/* returns OK, mode stays SH2|BE */
cs_option(h, CS_OPT_MODE, CS_MODE_SH4A | CS_MODE_SHFPU);
cs_close(&h);

cs_open(CS_ARCH_SH, CS_MODE_SH4A | CS_MODE_SHFPU, &h); /* actual switch */
cs_close(&h);
```

## SH2A big-endian + FPU

```c
cs_open(CS_ARCH_SH,
        CS_MODE_SH2A | CS_MODE_SHFPU | CS_MODE_BIG_ENDIAN,
        &h);
```

## Memory operand walk

```c
cs_sh *sh = &insn->detail->sh;
for (uint8_t i = 0; i < sh->op_count; i++) {
    cs_sh_op *op = &sh->operands[i];
    if (op->type == SH_OP_MEM) {
        printf("mem kind=%u reg=%s disp=%u\n",
               op->mem.address,
               cs_reg_name(h, op->mem.reg),
               op->mem.disp);
    }
}
```

## cstool

```bash
cstool -d sh4a "0c 31 10 20"
cstool -d sh2a-fpu "32 11 92 00"
```
