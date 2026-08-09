# Disasm / iteration reference

## Ownership

| Allocator | Object | Free |
| --- | --- | --- |
| `cs_disasm` | `cs_insn[]` (+ optional `detail` each) | `cs_free(ptr, n)` |
| `cs_malloc` | one `cs_insn` (+ optional `detail`) | `cs_free(ptr, 1)` |

`cs_free` walks `detail` pointers when present.

## `cs_disasm` internal behavior (summary)

- Grows an insn cache (~1.6x) when filling beyond initial cache size.
- On decode failure without skipdata (or remaining size &lt; skip size), breaks.
- Skipdata synthetic insns set `id = 0` and `detail = NULL`.

## `cs_disasm_iter` internal behavior (summary)

- Does not allocate; writes into caller-provided `insn`.
- Does not re-allocate `detail`; uses whatever `cs_malloc` set up.
- On X86 success path, applies `popcode_adjust` to `insn->id` (iter always;
  batch skips adjust for `X86_INS_VCMP`).

## Pointer update contract

After a successful iter decode of size `n`:

- `*code += n`
- `*size -= n`
- `*address += n`

Callers must not assume the original buffer base remains in `*code`.

## When batch is still better

- One-shot dump of a whole function with simple lifetime.
- Consumer wants random access into an insn array.
- Avoiding manual loop state.
