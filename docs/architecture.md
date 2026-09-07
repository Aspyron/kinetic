# Compiler architecture

Kinetic's 1.0.0 implementation lives in the [compiler source directory](../compiler/README.md).
It is a flat Python package with separate modules for each compilation stage.

## Entry points

The root [launcher](../kinetic.py) delegates to the
[CLI](../compiler/cli.py). The CLI reads a source file, calls the
[compilation API](../compiler/compiler.py), writes the resulting IR,
and invokes Clang to link a native executable. Run mode then starts it.

The [module launcher](../compiler/__main__.py) and the installed command
declared in [pyproject.toml](../pyproject.toml) delegate to the same CLI; there are
no separate implementations for these entry points.

## Pipeline

| Step | Input → output | Implementation |
| --- | --- | --- |
| Lexing | Source text → tokens with locations | [Lexer](../compiler/lexer.py) and [tokens](../compiler/tokens.py) |
| Parsing | Tokens → abstract syntax tree | [Parser](../compiler/parser.py) and [AST](../compiler/ast.py) |
| Semantic analysis | Syntax tree → inferred and checked types | [Analyzer](../compiler/analyzer.py) and [types](../compiler/types.py) |
| Code generation | Checked program → textual LLVM IR | [LLVM backend](../compiler/backend.py) |
| IR verification | Textual IR → verified textual IR | [Pipeline coordinator](../compiler/compiler.py) using llvmlite's LLVM bindings |
| Native build | Verified IR → native executable | [CLI](../compiler/cli.py) invoking Clang |

The public orchestration function is
[`compile_source()`](../compiler/compiler.py:11). It is re-exported by
the package and is the single pipeline coordination point. It generates
and verifies IR in memory; file output and native processes belong to the CLI.

## Shared representations and diagnostics

The lexer and parser share token definitions; the parser, analyzer, and backend
share the syntax tree. The analyzer and backend share type definitions. User-facing
errors derive from the base exception in [errors](../compiler/errors.py).

The printing builtin is special-cased by both the analyzer and the backend and
lowers to C's formatted-output function. It accepts exactly one integer or string.
It is not evidence of a separate runtime or standard library.

## Package organization

The [package initializer](../compiler/__init__.py) exposes the compilation API.
Stage modules use package-relative imports, and the root launcher imports the
CLI from this package. An editable installation is optional when working from
the repository root; the installed command uses the same code.

## Boundaries

- Compiler implementation and the user-facing CLI belong in the compiler package.
- Repository maintenance belongs in [tools](../tools/README.md).
- Static regression checks belong in [tests](../tests/README.md).
- Tutorials and complete sample programs belong in [examples](../examples/README.md).
- User and contributor explanations belong in [documentation](README.md).

The [roadmap](../ROADMAP.md) tracks the language, runtime, and validation work
needed before Kinetic can host its own compiler. Those planned components are
not part of the 1.0.0 implementation described here.
