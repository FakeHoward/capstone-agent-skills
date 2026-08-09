# cstest / YAML examples

## Enable and run on Linux

```bash
# sudo apt install libyaml-dev   # or dnf install libyaml-devel
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DCAPSTONE_BUILD_CSTEST=ON
cmake --build build
./build/cstest tests/details/arm.yaml
# paths may be build/Debug/cstest etc. depending on generator
```

## cstest_py on any host

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
cd bindings/python
pip install -e .
pip install -e cstest_py
cd ../..
cstest_py tests/
```

## Minimal YAML shape

```yaml
test_cases:
 -
  input:
    bytes: [ 0x05, 0xb0, 0xa0, 0xe1 ]
    arch: "arm"
    options: ["arm"]
  expected:
    insns:
      -
        asm_text: "mov r11, r5"
```

## Boolean fields

```yaml
is_alias: 1    # true
is_alias: 0    # unset
is_alias: -1   # false
```

## Skip a mismatched MC case

```yaml
skip: 1
skip_reason: "MC variant differs; Capstone keeps last llvm-mc feature set"
```
