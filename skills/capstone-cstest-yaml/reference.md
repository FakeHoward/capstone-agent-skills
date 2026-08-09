# cstest / YAML reference

## Test layout (`tests/`)

- `details/` — `cs_detail` focused cases
- `MC/<Arch>/` — LLVM MC-derived regression YAML
- `issues/`, `features/`, `negative/` — targeted suites
- Unit/integration **C** tests: `tests/unit`, `tests/integration` (CMake)

Legacy stdout tests exist separately; `CAPSTONE_BUILD_LEGACY_TESTS` controls
older integration-style binaries. YAML is the supported detailed path.

## Running

```bash
cstest -h
cstest tests/
# or
cstest_py tests/
```

Self-tests for the runners:

```bash
./suite/cstest/test/integration_tests.py cstest
./suite/cstest/test/integration_tests.py cstest_py
```

CMake test manager (after CSTEST build):

```bash
ctest --test-dir build -N
ctest --test-dir build -R "<name>"
```

## Optional case fields

Useful fields called out in `tests/README.md`: `name`, `skip`, `skip_reason`.

## MCUpdater caveat

`suite/auto-sync` `MCUpdater.py` can regenerate MC YAML from llvm-mc/FileCheck
output. Capstone modules enable all CPU features, while LLVM files often run
multiple feature variants; Capstone keeps the **last** variant written. Expect
occasional valid-but-mismatching disassembly — mark `skip` with a reason until
upstream issue tracking multi-variant MC is resolved.

## Dependencies pulled by suite/cstest CMake

When system libyaml is missing, ExternalProject may fetch libyaml, libcyaml
(patched), and cmocka for unit tests. That needs network at configure/build
time; prefer distro packages when available.
