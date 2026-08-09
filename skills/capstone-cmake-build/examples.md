# CMake build examples

## Release static library (default shape)

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

Produces static `capstone` when `CAPSTONE_BUILD_STATIC_LIBS` stays ON
and shared stays OFF.

## Shared library + cstool

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_BUILD_SHARED_LIBS=ON \
  -DCAPSTONE_BUILD_STATIC_LIBS=ON
cmake --build build
```

## Debug with compile commands and ASAN

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DENABLE_ASAN=ON
cmake --build build
```

## Preset (Linux host)

```bash
cmake --preset linux-x64
cmake --build --preset build-linux-release
```

## Custom alloc + diet (embedding-oriented)

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCAPSTONE_USE_DEFAULT_ALLOC=OFF \
  -DCAPSTONE_BUILD_DIET=ON \
  -DCAPSTONE_X86_REDUCE=ON
cmake --build build
```

(Runtime must call `cs_option(..., CS_OPT_MEM, ...)` before other APIs.)

## cstest + unit/integration (CSTEST gate)

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DCAPSTONE_BUILD_CSTEST=ON
cmake --build build --config Debug
ctest --test-dir build -R 'unit_riscv_reg_access|test_skipdata' --output-on-failure
```

`-DCAPSTONE_BUILD_CSTEST=ON` is required for `tests/unit` and
`tests/integration` (including `riscv_reg_access` and `test_skipdata`).
Legacy tests alone (`CAPSTONE_BUILD_LEGACY_TESTS`) are not enough.

Prefer system `libyaml` (`libyaml-dev` / `libyaml-devel`); CMake can fetch
and build libyaml if missing.

## Runtime smoke (skills package)

From `capstone-agent-skills`, against a Capstone checkout:

```bash
python scripts/runtime_smoke.py --capstone /path/to/capstone
```

Uses build dir `build-skill-smoke` by default. If cmake/compiler is missing,
scenarios **SKIP** (exit 0) instead of failing. See package README.
