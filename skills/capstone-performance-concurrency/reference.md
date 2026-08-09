# Performance / concurrency reference

## Global memory function pointers (`cs.c`)

Depending on build:

- Default userspace: libc `malloc`/`calloc`/`realloc`/`free`/`vsnprintf`
- Kernel / winkernel builds: alternate defaults
- `CAPSTONE_USE_SYS_DYN_MEM` off: start NULL → need `CS_OPT_MEM` or
  `CS_ERR_MEMSETUP`

`cs_option(CS_OPT_MEM)` assigns all five pointers unconditionally from
`cs_opt_mem`.

## Why handle-per-thread

`cs_struct` holds mutable decode state (mode, detail_opt, skipdata, mnemonic
list, arch printer state such as ARM IT blocks, caches). Concurrent decode on
one handle races those fields.

## Benchmark claim source

`capstone.h` documents that some benchmarks show `cs_disasm_iter` about 30%
faster than `cs_disasm(count=1)` on random input. Re-measure for your workload.

## Detail allocation cost

Batch path `calloc`s a `cs_detail` per insn when `detail_opt` non-zero. Iter
allocates one detail with `cs_malloc` and reuses it — lower allocator pressure.
