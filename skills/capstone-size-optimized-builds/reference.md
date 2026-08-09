# Size optimization reference

## Architecture list

`SUPPORTED_ARCHITECTURES` in root `CMakeLists.txt`:

ARM, AARCH64, M68K, MIPS, PPC, SPARC, SYSTEMZ, XCORE, X86, TMS320C64X, M680X,
EVM, MOS65XX, WASM, BPF, RISCV, SH, TRICORE, ALPHA, HPPA, LOONGARCH, XTENSA, ARC.

Each maps to `CAPSTONE_<NAME>_SUPPORT`. With
`CAPSTONE_USE_ARCH_REGISTRATION=ON`, per-arch compile defs are not propagated
the same way; registration APIs select modules at runtime.

**Registration gap (current tree):** `capstone.h` / `cs.c` export
`cs_arch_register_*` for every arch **except** HPPA and Xtensa (no
`cs_arch_register_hppa`, no `cs_arch_register_xtensa`). Selective-registration
builds cannot enable those two via the public API; use non-selective
`CAPSTONE_HPPA_SUPPORT` / `CAPSTONE_XTENSA_SUPPORT` (or patch in
`CS_ARCH_REGISTER` helpers).

## Diet mode effects

`CAPSTONE_BUILD_DIET` defines `CAPSTONE_DIET`. Public headers document that many
name/detail helpers are irrelevant in diet mode and can yield `CS_ERR_DIET`.
`cstool -v` can report `diet=1` when the linked core was built that way.

## X86 reduce

`CAPSTONE_X86_REDUCE` defines `CAPSTONE_X86_REDUCE`. Meant for size-sensitive
X86 embeddings; combine with diet when targeting firmware/kernel footprints.
Docs site links in `docs/README.md` describe diet / x86reduce / embed themes;
trust in-tree CMake options over external pages if they disagree.

## Preset

`CMakePresets.json` includes `windows-x64-diet` / `build-windows-diet*` which
set `CAPSTONE_BUILD_DIET=ON`. Other hosts can pass the same cache variable
manually.

## What does not shrink the core by itself

- Turning off `CAPSTONE_BUILD_CSTEST` (already OFF by default).
- Packaging with cpack.
- Language bindings (built separately under `bindings/`).
