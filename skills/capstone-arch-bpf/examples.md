# Capstone BPF — examples

## Classic BPF LE with detail

```c
csh handle;
cs_insn *insn;
size_t n;

if (cs_open(CS_ARCH_BPF, CS_MODE_BPF_CLASSIC, &handle) != CS_ERR_OK)
	return -1;
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);

n = cs_disasm(handle, code, code_size, address, 0, &insn);
for (size_t i = 0; i < n; i++) {
	cs_bpf *b = &insn[i].detail->bpf;
	/* b->operands[0..b->op_count): REG/IMM/OFF/EXT/MMEM/... */
}
cs_free(insn, n);
cs_close(&handle);
```

## Extended BPF (eBPF)

```c
cs_open(CS_ARCH_BPF, CS_MODE_BPF_EXTENDED, &handle);
cs_option(handle, CS_OPT_DETAIL, CS_OPT_ON);
```

## Endian variants

```c
cs_open(CS_ARCH_BPF, CS_MODE_BIG_ENDIAN | CS_MODE_BPF_CLASSIC, &handle);
cs_open(CS_ARCH_BPF, CS_MODE_BIG_ENDIAN | CS_MODE_BPF_EXTENDED, &handle);
```

## regs_access

```c
cs_regs regs_read, regs_write;
uint8_t read_count, write_count;
if (cs_regs_access(handle, &insn[i],
		regs_read, &read_count,
		regs_write, &write_count) == CS_ERR_OK) {
	/* use counts */
}
```

## Mode switch replaces

```c
cs_open(CS_ARCH_BPF, CS_MODE_BPF_CLASSIC, &handle);
cs_option(handle, CS_OPT_MODE, CS_MODE_BPF_EXTENDED); /* replaces mode */
```

## cstool

```text
cstool bpf 0x...
cstool bpfbe 0x...
cstool ebpf 0x...
cstool ebpfbe 0x...
```
