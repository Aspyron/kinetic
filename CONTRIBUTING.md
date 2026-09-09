# Contributing to Kinetic

Kinetic is a small prototype. Prefer focused changes and explicit compiler
stages over adding infrastructure intended for a much larger language project.

## Start here

- [Installation](INSTALL.md) covers the source-checkout and editable-install workflows.
- [Architecture](docs/architecture.md) explains the compilation pipeline.
- [Repository layout](docs/repository_layout.md) explains where changes belong.
- [Language guide](docs/syntax_guide.md) documents the existing 1.1.0 surface.
- [Roadmap](ROADMAP.md) tracks implemented features and the path toward self-hosting.

## Where to make changes

| Change | Location |
| --- | --- |
| Tokenization and grammar | [Lexer](compiler/lexer.py), [tokens](compiler/tokens.py), and [parser](compiler/parser.py). |
| Syntax representation | [AST](compiler/ast.py). |
| Type rules and inference | [Analyzer](compiler/analyzer.py) and [types](compiler/types.py). |
| LLVM generation | [Backend](compiler/backend.py). |
| Pipeline orchestration | [Compiler API](compiler/compiler.py). |
| User-facing build and run commands | [CLI](compiler/cli.py). |
| Maintenance commands | [Tools](tools/README.md). |
| Validation | [Tests](tests/README.md) and [examples](examples/README.md). |

Keep compiler stages directly in the compiler package, using package-relative
imports. The root [launcher](kinetic.py) should delegate to the CLI rather than
contain another implementation of the build workflow.

Printing is currently a compiler builtin, not a library function. Changes to
builtins need matching analyzer and backend handling. Do not create a placeholder
standard-library tree before there is an actual library implementation.

## Static verification

Run the static checker before submitting a layout or documentation change:

```shell
python -B tools/check.py
```

The static portion uses only the Python standard library. It verifies Python
syntax, internal import targets, the single compiler source location, public API
exports, entry points, declaration-token references, the published Hello World
example, and local documentation links.

The same command also runs **frontend behavioral tests**, which exercise the
lexer, parser, and analyzer directly (located errors, migration hints, warnings,
constant bounds checks) without llvmlite or Clang. Backend and native suites
skip cleanly when llvmlite or Clang is unavailable; set
`KINETIC_NATIVE_TESTS=1` on a Clang-equipped machine to run native builds.

## GitHub CI

The [workflow](.github/workflows/ci.yml) runs the full local checker on pushes,
pull requests, and manual dispatches (Windows and Linux, Python 3.10 and 3.14).
A second `behavioral` job installs the pinned llvmlite from
[requirements.txt](requirements.txt) and runs the frontend and backend suites on
Ubuntu with Python 3.10.

CI uses read-only repository permissions and official actions pinned to commit
hashes. It does not install llvmlite or invoke Clang. Keep checks in the shared
checker rather than maintaining a separate implementation inside the workflow.

Run checks locally for fast feedback; CI makes them repeatable for every change.
A green static job does not replace compiler-behavior verification. When native
regression testing is added, give it a separate, clearly named job and keep the
static workflow usable without a compiler toolchain.

## Compiler verification, when builds are appropriate

Changes to compiler behavior should also be checked against all three examples
in an environment with llvmlite and Clang installed:

```shell
python kinetic.py run examples/01_hello.kn
python kinetic.py run examples/02_logic.kn
python kinetic.py run examples/03_arrays.kn
```

These commands **do compile and execute programs**. Do not use them when a task
requests static-only work. Remove generated artifacts afterward. There is not
yet an automated compiler-behavior suite.

## Before submitting

- Keep changes scoped to the task; do not mix a file move with language changes.
- Keep the launcher, package exports, and installed command aligned.
- Update documentation links and package configuration when moving files.
- Add examples or regression coverage for language changes.
- Update the roadmap when a milestone's actual status changes; planned work is not implemented work.
- Report which checks actually ran, and which were deliberately skipped.
