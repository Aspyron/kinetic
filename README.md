# Kinetic

A small language compiler, written in Python and targeting LLVM.

[Language guide](docs/syntax_guide.md) · [Architecture](docs/architecture.md) · [Installation](INSTALL.md) · [Contributing](CONTRIBUTING.md) · [Roadmap](ROADMAP.md)

Kinetic is an early compiler prototype (1.1.0). It reads Kinetic source, performs
lexical, syntactic, and type analysis, emits verified textual LLVM IR through
llvmlite, and uses Clang to produce a native executable.

The long-term goal is a readable systems language. The current prototype is
deliberately small; it does not yet provide a standard library or a production
memory-safety model.

## Language features

- Type inference and implicit function returns.
- Immutable bindings with opt-in mutation.
- Conditional branches and loops.
- Integer and string values, integer arrays, and array indexing.
- A built-in printing operation for one integer or string at a time.

Start with the [language guide](docs/syntax_guide.md) and the programs in
[examples](examples/README.md).

## Hello World

The [introductory example](examples/01_hello.kn) is a complete Kinetic program:

```text
func main() {
    print("Hello World!")
}
```

Functions use [`func`](compiler/lexer.py:33), immutable bindings use
[`let`](compiler/lexer.py:34), and mutable bindings use
[`mut`](compiler/lexer.py:35). See the [syntax guide](docs/syntax_guide.md) for
declarations, reassignment, and function calls.

## Quick start

You need Python 3.10 or newer, a compatible llvmlite release, and Clang on your
executable search path. See [installation](INSTALL.md) for details.

Install the Python dependency:

```shell
python -m pip install -r requirements.txt
```

Compile and run the introductory example:

```shell
python kinetic.py run examples/01_hello.kn
```

Compile without running the result:

```shell
python kinetic.py build examples/01_hello.kn
```

The root [launcher](kinetic.py) provides the build and run commands. Generated IR
and native binaries are written next to the input source.

## Repository layout

Compiler sources, documentation, examples, and development utilities each have
one clear location.

| Area | Responsibility |
| --- | --- |
| [Compiler](compiler/README.md) | A flat Python package containing all compiler stages and the CLI. |
| [Documentation](docs/README.md) | Language reference, architecture, and repository design. |
| [Examples](examples/README.md) | Small programs demonstrating the 1.1.0 language. |
| [Tools](tools/README.md) | Repository maintenance utilities, separate from the compiler CLI. |
| [Tests](tests/README.md) | Static repository checks; no native builds are required. |
| [Package configuration](pyproject.toml) | Python packaging and the optional installed command. |

See the [layout guide](docs/repository_layout.md) for the directory responsibilities.

## Development

Run the dependency-free, static-only repository checks:

```shell
python -B tools/check.py
```

The same command runs static checks (syntax, layout, links, keyword mapping)
plus **frontend behavioral tests** against the lexer, parser, and analyzer —
including the new compile-time diagnostics. Backend and native suites skip
cleanly without llvmlite or Clang.

The [GitHub Actions workflow](.github/workflows/ci.yml) runs the same checker on
pushes and pull requests, using Python 3.10 and 3.14 on Windows and Linux. It can
also be started manually from GitHub's Actions tab. A passing static check is not
a compiler-behavior result; targeted manual checks remain useful when native
builds are appropriate. See [contributing](CONTRIBUTING.md).

## Direction

The current goal is to build the foundations needed for a compiler written in
Kinetic that can compile itself. Version 1.1.0 is not self-hosting yet. The
[roadmap](ROADMAP.md) separates completed work, current planning, and future milestones.

## License

See [LICENSE](LICENSE).
