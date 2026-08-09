# Capstone Xtensa — examples

## ESP32 with detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_XTENSA, CS_MODE_XTENSA_ESP32, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_xtensa *x = &insn[i].detail->xtensa;
	/* x->format, XTENSA_OP_L32R / MEM / REG */
}
cs_free(insn, n);
cs_close(&handle);
```

## ESP32-S3 (ee.* / HiFi3)

```c
cs_open(CS_ARCH_XTENSA, CS_MODE_XTENSA_ESP32S3, &handle);
```

## LITBASE (Extended L32R)

```c
cs_open(CS_ARCH_XTENSA, CS_MODE_XTENSA_ESP32, &handle);
/* LSB=1 enables; high bits supply base */
cs_option(handle, CS_OPT_LITBASE, 0xfffff001);
```

Default `LITBASE=0` uses PC-relative resolution
`((addr + 3) & ~3) + offset`.

## Mode OR — cannot clear chip bits

```c
cs_open(CS_ARCH_XTENSA, CS_MODE_XTENSA_ESP32, &handle);
cs_option(handle, CS_OPT_MODE, CS_MODE_XTENSA_ESP32S3);
/* both bits set; reopen to switch cleanly */
```

## regs_access

```c
cs_regs regs_read, regs_write;
uint8_t read_count, write_count;
cs_regs_access(handle, &insn[i],
	regs_read, &read_count, regs_write, &write_count);
```

## Skipdata warning (current tree)

```c
cs_option(handle, CS_OPT_SKIPDATA, CS_OPT_ON);
/* WARNING: default skip size is currently 255 for Xtensa.
   Prefer CS_OPT_SKIPDATA_SETUP with an explicit callback/size. */
```

## Big-endian rejected

```c
/* CS_ERR_MODE */
cs_open(CS_ARCH_XTENSA, CS_MODE_BIG_ENDIAN | CS_MODE_XTENSA_ESP32, &handle);
```

## cstool

```text
cstool esp32 0x...
cstool esp32s2 0x...
cstool esp32s3 0x...
cstool esp8266 0x...
```
