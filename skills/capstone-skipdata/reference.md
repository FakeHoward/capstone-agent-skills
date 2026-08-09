# Skipdata reference

## Setup fields (`cs_opt_skipdata`)

- `mnemonic` — display name for data records
- `callback` — optional `cs_skipdata_cb_t`
- `user_data` — passed to callback

Copy is stored on the handle (`skipdata_setup`). If `mnemonic == NULL` after
setup, engine restores `".byte"`.

## Engine fields (`cs_priv.h`)

- `bool skipdata`
- `uint8_t skipdata_size` — filled on first SKIPDATA ON when zero
- `cs_opt_skipdata skipdata_setup`

## Failure / stop conditions

Skip path abandoned when:

- SKIPDATA off, or
- `skipdata_size > remaining`, or
- callback returns `0`, or
- callback returns size `> remaining`

Batch returns the count decoded so far; iter returns `false`.

## Header comment caveat

`capstone.h` documents callback `@code` as the buffer passed to `cs_disasm()`.
That matches **batch** only. Iter passes the current remaining pointer — follow
`cs.c`, not the comment, when using `cs_disasm_iter`.
