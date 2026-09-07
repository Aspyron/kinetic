# Compiler sources

This directory is Kinetic's Python package. All compiler stages and the CLI live
directly here, with one source file per concern.

| Stage or concern | Source |
| --- | --- |
| Public package API | [Package initializer](__init__.py) |
| Pipeline orchestration and IR verification | [Compiler](compiler.py) |
| Lexing and token definitions | [Lexer](lexer.py), [tokens](tokens.py) |
| Parsing and syntax tree | [Parser](parser.py), [AST](ast.py) |
| Type checking and inference | [Analyzer](analyzer.py), [types](types.py) |
| LLVM code generation | [Backend](backend.py) |
| Diagnostics | [Errors](errors.py) |
| Native build and run driver | [CLI](cli.py) |
| Module entry point | [Module launcher](__main__.py) |

Stage modules use package-relative imports. The public orchestration function is
[`compile_source()`](compiler.py:11), also exported by the package initializer.

The root [launcher](../kinetic.py), the module entry point, and the installed
command all use the same CLI. [pyproject.toml](../pyproject.toml) packages this
directory directly.

See the [architecture guide](../docs/architecture.md) for dependencies between stages.
