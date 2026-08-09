# Custom memory and embedding reference

## How defaults are selected (`cs.c`)

When `CAPSTONE_USE_SYS_DYN_MEM` is defined (CMake: `CAPSTONE_USE_DEFAULT_ALLOC=ON`):

- Normal user mode: libc `malloc` / `calloc` / `realloc` / `free` / `vsnprintf`.
- `_KERNEL_MODE`: `cs_winkernel_*` from `windows/winkernel_mm.*`.
- `CAPSTONE_HAS_OSXKERNEL`: `kern_os_malloc` / `kern_os_realloc` / `kern_os_free`
  with a local calloc wrapper.

When the define is absent, all five function pointers start NULL until
`CS_OPT_MEM` fills them.

## `cs_opt_mem`

Fields: `malloc`, `calloc`, `realloc`, `free`, `vsnprintf` (see
`include/capstone/capstone.h`). `CS_OPT_MEM` is the only option allowed with a
dummy handle so setup can precede `cs_open`.

## Windows driver sample constraints (`contrib/cs_driver`)

Comments in `cs_driver.c` state:

- Capstone APIs must not run above `DISPATCH_LEVEL` with the provided pool-based
  malloc.
- 32-bit drivers should wrap Capstone use with `KeSaveFloatingPointState` /
  `KeRestoreFloatingPointState`.
- Link notes mention `ntstrsafe.lib` and include paths into `include/`.

This is a Visual Studio sample tree, not a CMake target in the root build.

## Size pairing

Embedding builds often also enable `CAPSTONE_BUILD_DIET` and
`CAPSTONE_X86_REDUCE`. Those are independent of the allocator switch but commonly
combined for firmware/kernel footprints.

## Out-of-tree examples

`docs/README.md` links external KernelProject / CapstoneTest samples. Treat them
as optional external references; do not assume they ship inside this repo.
