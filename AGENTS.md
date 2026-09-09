# Agent guidance

Kinetic is a 1.1.0 prototype language compiler written in Python. It emits textual
LLVM IR through llvmlite and invokes Clang for native binaries. Keep changes small
and do not imply that the prototype provides a production memory-safety model.

## Layout

- [Compiler sources](compiler/README.md) form one flat Python package, with stage files directly in the compiler directory.
- [Root launcher](kinetic.py) delegates to the compiler CLI.
- [Package configuration](pyproject.toml) installs the compiler package directly.
- [Tools](tools/README.md), [tests](tests/README.md), [docs](docs/README.md), and
  [examples](examples/README.md) have separate responsibilities.

Use package-relative imports within the compiler. Keep the launcher thin and
avoid additional package layers or duplicate implementations. Sample programs
belong in the examples directory.

## Setup and commands

Install the sole runtime dependency from [requirements.txt](requirements.txt):

```shell
python -m pip install -r requirements.txt
```

An editable installation is optional:

```shell
python -m pip install -e .
```

Clang must be on the executable search path for native builds:

```shell
python kinetic.py build examples/01_hello.kn
python kinetic.py run examples/01_hello.kn
```

## Verification

For structural changes, run the static-only checker:

```shell
python -B tools/check.py
```

It needs only Python and does not import Kinetic, generate IR, invoke Clang, or
run Kinetic programs. See [tests](tests/README.md) for its coverage.

The [GitHub Actions workflow](.github/workflows/ci.yml) runs the same static
checker on pushes, pull requests, and manual dispatches, with Python 3.10 and
3.14 on Windows and Linux. Keep local checks and CI aligned; a green static job
does not demonstrate compiler behavior.

There is no automated compiler-behavior suite or linter.
When compiler behavior changes and native builds are permitted, manually verify:

```shell
python kinetic.py run examples/01_hello.kn
python kinetic.py run examples/02_logic.kn
python kinetic.py run examples/03_arrays.kn
```

**If the user asks not to compile or run programs, do not invoke these commands,
the compilation API, or native tools. Limit verification to static checks and
report that behavioral verification was skipped.**

Native build and run operations write IR and binaries next to the source.
[.gitignore](.gitignore) covers common outputs and Python/package caches, but
remove artifacts after manual verification. A Clang warning about overriding the
module target triple is benign on its own.

## Architecture

The root launcher delegates to the [CLI](compiler/cli.py), which calls
[`compile_source()`](compiler/compiler.py:11), the single pipeline
orchestration point.

The stage order is [lexer](compiler/lexer.py),
[parser](compiler/parser.py), [analyzer](compiler/analyzer.py), and
[LLVM backend](compiler/backend.py). The orchestration API verifies the
IR with llvmlite before returning it.

Printing is a compiler builtin, not a user-level or library function. It is
special-cased in both the analyzer and backend, lowers to C's formatted-output
function, and accepts exactly one integer or string. New builtins need matching
handling in both stages.

The [syntax guide](docs/syntax_guide.md) documents the 1.1.0 language. The three
numbered [examples](examples/README.md) cover inference, control flow, mutation,
and arrays. Comparisons remain limited to equality, less-than, and greater-than.

Declarations use [`func`](compiler/lexer.py:33) for functions,
[`let`](compiler/lexer.py:34) for immutable bindings, and standalone
[`mut`](compiler/lexer.py:35) for mutable bindings. Keep lexer tokens, parser
handling, examples, and documentation synchronized when syntax changes.

See [architecture](docs/architecture.md) and [contributing](CONTRIBUTING.md) before
changing compiler boundaries or verification workflows.

## Direction and status

The [roadmap](ROADMAP.md) tracks completed work, current planning, and future
milestones toward self-hosting. Kinetic is not self-hosting yet; the compiler is
implemented in Python. Do not describe planned language or runtime features as
available, and update milestone status only when the work and its verification
are actually complete.

[Claude Code guidance](CLAUDE.md) imports these shared instructions.
