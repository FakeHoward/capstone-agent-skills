# Language bindings reference

## Python (`bindings/python/`)

- User install: `bindings/python/README.md`, `bindings/python/BUILDING.md`.
- Tests demos under `bindings/python` (e.g. `test_lite.py` for `disasm_lite`).
- `cstest_py`: `bindings/python/cstest_py/` — consumes YAML under repo `tests/`.

Windows tip from README: prebuilt wheels via PyPI avoid a local C toolchain;
source builds need Visual Studio / Developer Command Prompt.

## Java (`bindings/java/`)

Needs OpenJDK and JNA (`libjna-java` on Debian/Ubuntu examples). Build/run via
`make` and `./run.sh`. Samples: `TestBasic.java`, `Test<arch>.java`.

## OCaml (`bindings/ocaml/`)

Needs OCaml toolchain; `make` builds the binding. Samples: `test_basic.ml`,
`test_detail.ml`, `test_<arch>.ml`.

## PowerShell (`bindings/powershell/`)

Place `capstone.dll` under `./Capstone/Lib/Capstone/`, add the Capstone folder
to a PSModulePath entry, then `Import-Module Capstone`. Help:
`Get-Help Get-CapstoneDisassembly -Full`.

## VB6 (`bindings/vb6/`)

FireEye FLARE sample with `vbCapstone.dll` shim; README notes it was built
against Capstone 3.0 rc4 — verify struct compatibility before relying on it
with a modern core.

## Community list

See `bindings/README.md` for external projects (gapstone, capstone-rs,
Capstone.NET, and others). Links may age; verify upstream before recommending.
