# Tests

This directory separates automated repository checks from teaching examples and
compiler implementation. The initial [suite](test_layout.py) is static-only and
uses Python's standard-library test framework.

## Run static checks

```shell
python -B tools/check.py
```

Or run discovery directly from the repository root:

```shell
python -B -m unittest discover -s tests -p test_layout.py -v
```

## Current coverage

### Static checks ([layout](test_layout.py))

- Expected repository sections exist.
- Compiler modules live directly in one flat package.
- Sample programs live in the examples directory, not at the repository root.
- Python sources parse successfully, without importing them.
- Token-kind references resolve to declared enum members, and declaration keywords
  match the current lexer mapping.
- The introductory Hello World program is published verbatim in the project overview.
- Examples and the syntax guide use the current function and mutable-binding declarations.
- The CI workflow invokes the shared static checker and pins official actions to commits.
- Relative and absolute internal imports point to existing compiler modules or packages.
- The package initializer exposes the public compilation API.
- The root and module launchers delegate to the same compiler CLI.
- Claude Code guidance imports the shared agent rules, and the roadmap exists.
- Local Markdown links resolve to existing repository paths.

### Frontend behavioral checks ([frontend](test_frontend.py))

Run everywhere with no external dependencies: lexer tokenization and locations,
removed-keyword migration hints, declaration parsing and precedence, old-syntax
rejection, analyzer errors (missing `main`, immutable reassignment, type
mismatches, constant out-of-bounds indexes), warnings (unused bindings,
shadowing), and warning-summary singular/plural rendering.

### Backend behavioral checks ([backend](test_backend.py))

Require llvmlite; skipped cleanly when it is not installed. Verify all three
examples compile to valid IR, the Hello World program emits a `printf` call,
and `compile_with_diagnostics()` returns warnings alongside IR.

### Native example checks ([native](test_native.py))

Require Clang **and** `KINETIC_NATIVE_TESTS=1`; skipped otherwise. Build each
example to a real binary and assert its expected output.

These checks do not require llvmlite or Clang. They do not execute compiler code,
check dynamic import behavior, generate or verify LLVM IR, build a distribution,
or compile and run Kinetic programs. Source-consistency checks do not prove that
the parser accepts or rejects programs correctly. The workflow check inspects
its command and action references; it is not a full YAML or GitHub Actions validator.
These are not compiler-behavior tests.

## CI and local verification

The [GitHub workflow](../.github/workflows/ci.yml) runs the same checker on pushes,
pull requests, and manual dispatches. Its matrix uses Python 3.10 and 3.14 on
Windows and Linux. Local runs provide fast feedback; CI provides consistent
checks for shared changes. Neither substitutes for behavioral regression tests.

## Future compiler regression tests

Language changes should gain focused regression coverage here when behavioral
testing is introduced. Keep test fixtures separate from the user-facing
[examples](../examples/README.md), and add specialized suites only when they
contain actual tests.

For the existing manual native-build workflow, see
[contributing](../CONTRIBUTING.md). That workflow must not be used for static-only tasks.
