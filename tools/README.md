# Development tools

Repository maintenance utilities live here, separate from the
[compiler CLI](../compiler/cli.py).

## Static repository check

The [checker](check.py) discovers the static [layout tests](../tests/test_layout.py)
and returns a nonzero status if a check fails:

```shell
python -B tools/check.py
```

It resolves the repository location from its own location, so it does not depend
on the terminal's current directory. It needs only the Python standard library.
The bytecode-suppression option keeps this check from leaving Python caches.

The checker does not import the compiler, generate LLVM IR, run Clang, install
dependencies, or execute Kinetic programs. See [test documentation](../tests/README.md)
for the exact coverage and limitations.

Future repository maintenance tools should live here; user-facing language
commands should continue to live in the compiler package.

## GitHub Actions

The [workflow](../.github/workflows/ci.yml) invokes the same command on Windows
and Linux using Python 3.10 and 3.14. No separate CI-only checker is maintained.
Both local and hosted runs are static-only and require no runtime dependencies.
