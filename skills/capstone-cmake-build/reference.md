# CMake build reference

## Options commonly set at configure time

Architecture toggles (default: all on via `CAPSTONE_ARCHITECTURE_DEFAULT`):

- `CAPSTONE_<ARCH>_SUPPORT` for each arch in `SUPPORTED_ARCHITECTURES`
  (ARM, AARCH64, M68K, MIPS, PPC, SPARC, SYSTEMZ, XCORE, X86, TMS320C64X,
  M680X, EVM, MOS65XX, WASM, BPF, RISCV, SH, TRICORE, ALPHA, HPPA,
  LOONGARCH, XTENSA, ARC).

Other options from `CMakeLists.txt` / `BUILDING.md`:

| Option | Role |
|--------|------|
| `CAPSTONE_USE_ARCH_REGISTRATION` | Explicit `cs_arch_register_*()` instead of compile-time arch defs (no public helpers for HPPA/Xtensa — see size-optimized / arch skills) |
| `CAPSTONE_BUILD_DIET` | Compact “diet” engine (`CAPSTONE_DIET`) |
| `CAPSTONE_X86_REDUCE` | Smaller X86 table set |
| `CAPSTONE_X86_ATT_DISABLE` | Drop AT&T syntax |
| `CAPSTONE_BUILD_STATIC_MSVC_RUNTIME` | Windows; defaults to follow shared-lib ON |
| `CAPSTONE_BUILD_MACOS_THIN` | Skip universal `x86_64;arm64` |
| `CAPSTONE_OSXKERNEL_SUPPORT` | OS X kext embedding hooks |
| `CAPSTONE_DEBUG` | Extra asserts; also on with `Debug` build type |
| `CAPSTONE_BUILD_LEGACY_TESTS` | Legacy stdout tests; default ON if top-level |
| `CAPSTONE_BUILD_CSTEST` | OFF by default. When ON: builds `cstest` **and** adds `tests/unit` + `tests/integration` (CTest). Needs libyaml (system or fetched). |
| `CAPSTONE_INSTALL` | Install rules; default ON if top-level |
| `ENABLE_ASAN` | Address (+undefined) sanitizer flags |
| `ENABLE_COVERAGE` | Coverage compile/link flags |
| `CMAKE_EXPORT_COMPILE_COMMANDS` | `compile_commands.json` for clangd |

## Packaging (from BUILDING.md)

Shared build + install prefix under `/usr`, then from the build dir:

```bash
cpack -G DEB
cpack -G RPM
cpack -G DragNDrop
```

Only claim these when the user asks for packages; they need a configured shared build.

## Presets (`CMakePresets.json`)

- Generator: Ninja Multi-Config for host presets.
- Binary dir pattern: `build/<presetName>`.
- Install dir pattern: `out/install/<presetName>`.
- Host-gated: `linux-x64`, `macos-x64`, `windows-x64`, `windows-x64-diet`.
- Build presets include Release and install variants.

## Make / make.sh (deprecated)

`COMPILE_MAKE.TXT` states Makefile build is deprecated; use CMake.
Legacy env vars (`CAPSTONE_ARCHS`, `CAPSTONE_DIET`, `CAPSTONE_USE_SYS_DYN_MEM`,
etc.) apply only to `./make.sh` / `config.mk`, not as CMake `-D` names.

## Fuzzer target note

Root `CMakeLists.txt` always adds executable `fuzz_disasm` (onefile +
`suite/fuzz` sources). That is not a full libFuzzer CI setup; see the
fuzzing skill for reproduction workflow.
