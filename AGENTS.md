# AGENTS.md

Kinetic is a prototype compiler (V1) for a small language (`.kn` files), written in pure Python. It emits textual LLVM IR and shells out to `clang` for the final binary.

## Commands

- Setup: `python -m pip install -r requirements.txt` (only dep is `llvmlite`); `clang` must be on PATH.
- Compile + run: `python kinetic.py run main.kn` (or any `.kn` file).
- Compile only: `python kinetic.py build <file.kn>`.

## Verification

There is **no test suite, linter, or CI**. To verify a compiler change, run it against the examples and check the program output:

```shell
python kinetic.py run examples/01_hello.kn
python kinetic.py run examples/02_logic.kn
python kinetic.py run examples/03_arrays.kn
```

Gotchas:
- `build`/`run` write a `.ll` file and a native binary **next to the source file**. There is no `.gitignore` — delete these artifacts after verifying.
- `clang` prints a benign `warning: overriding the module target triple` on every build; this is not a failure.

## Architecture

- Entry: `kinetic.py` → `kinetic/cli.py` (argparse, invokes clang) → `kinetic/compiler.py::compile_source()` — the single pipeline orchestration point.
- Pipeline stages, one module each, in `kinetic/`: `lexer.py` → `parser.py` → `analyzer.py` (types) → `backend.py` (LLVM IR via llvmlite). `compile_source()` verifies the IR with `llvmlite.binding` before returning it, so IR bugs surface as Python exceptions, not clang errors.
- `print` is **not** a user-level function — it is a compiler builtin special-cased in both `analyzer.py` and `backend.py` (lowers to C `printf`, accepts exactly one int or string argument). New builtins need handling in both places.

## Language reference

The `.kn` language surface is documented in `docs/syntax_guide.md`; `examples/` holds three numbered programs covering the full V1 feature set (inference, `if`/`else`, `while`, `mut`, arrays). V1 supports only `==`, `<`, `>` comparisons.
