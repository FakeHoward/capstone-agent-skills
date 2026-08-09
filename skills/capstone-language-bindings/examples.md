# Language binding examples

## Python from source (repo checkout)

```bash
# build/install C core first if you want a specific libcapstone
cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build

cd bindings/python
pip install -e .
# optional YAML runner:
pip install -e cstest_py
```

Skip compiling a private core during pip install:

```bash
# Unix example: point at directory containing libcapstone
export LIBCAPSTONE_PATH=/usr/lib
pip install bindings/python/
```

## Run Python YAML tests

```bash
cstest_py tests/
```

## Java smoke

```bash
cd bindings/java
make
./run.sh
```

## OCaml smoke

```bash
cd bindings/ocaml
make
```
