---
name: capstone-cmake-build
description: >-
  Builds Capstone with CMake, covering configure/build/install, library type
  defaults, presets, and common cache options. Use when compiling Capstone,
  choosing static vs shared libraries, reading BUILDING.md or CMakeLists.txt,
  using CMakePresets.json, or when Makefile/make.sh comes up (deprecated).
---

# Capstone CMake build

## Source of truth

Prefer `BUILDING.md` and root `CMakeLists.txt`. There is no Meson build.
`COMPILE_MAKE.TXT` and `./make.sh` are deprecated legacy paths only.

## Default workflow

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
cmake --install build --prefix "<install-prefix>"
```

Windows:

```bash
cmake.exe -B build
cmake.exe --build build --config Release
cmake.exe --install build
```

Optional presets live in `CMakePresets.json` (`linux-x64`, `macos-x64`,
`windows-x64`, diet variants, matching build/install presets).

## Library defaults (CMake)

| Option | Default | Notes |
|--------|---------|--------|
| `CAPSTONE_BUILD_STATIC_LIBS` | `ON` | Static library |
| `CAPSTONE_BUILD_SHARED_LIBS` | `OFF` | Shared/DLL |
| `CAPSTONE_BUILD_CSTOOL` | `ON` if top-level | CLI tool |
| `CAPSTONE_BUILD_CSTEST` | `OFF` | `cstest` + **unit/integration** tests (needs libyaml) |
| `CAPSTONE_BUILD_LEGACY_TESTS` | `ON` if top-level | Legacy stdout tests only |
| `CAPSTONE_USE_DEFAULT_ALLOC` | `ON` | See below |

`CAPSTONE_BUILD_CSTEST=ON` is the gate for modern `tests/unit` and
`tests/integration` targets (for example `riscv_reg_access`, `test_skipdata`).
`CAPSTONE_BUILD_LEGACY_TESTS` does **not** build those directories.

At least one of static/shared must stay enabled or configure fails.

## Correct alloc flag

CMake option is **`CAPSTONE_USE_DEFAULT_ALLOC`**. When `ON`, the compile
definition `CAPSTONE_USE_SYS_DYN_MEM` is set. Older docs that say
`-DCAPSTONE_USE_SYS_DYN_MEM=0` mean turn default alloc off via:

```bash
-DCAPSTONE_USE_DEFAULT_ALLOC=OFF
```

## Agent rules

1. Recommend CMake first; mention Make only for legacy scripts that still use it.
2. Do not invent Meson, CI jobs, or packaging steps beyond `cpack` examples in `BUILDING.md`.
3. Quote real option names from `CMakeLists.txt` when advising flags.

## More detail

- Options, packaging, ASAN/coverage: [reference.md](reference.md)
- Concrete configure lines: [examples.md](examples.md)
