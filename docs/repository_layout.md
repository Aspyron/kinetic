# Repository layout

Kinetic keeps its implementation flat and separates it from documentation,
examples, and repository maintenance.

## Directories

| Directory | Responsibility |
| --- | --- |
| [Compiler](../compiler/README.md) | The Python package, with the lexer, parser, analyzer, backend, and CLI directly inside it. |
| [Documentation](README.md) | Language syntax, compiler architecture, and repository guides. |
| [Examples](../examples/README.md) | Complete Kinetic programs used in tutorials and manual verification. |
| [Tools](../tools/README.md) | Development and repository maintenance utilities. |
| [Tests](../tests/README.md) | Static repository checks and a home for future compiler regression tests. |
| [GitHub workflows](../.github/workflows/ci.yml) | Runs the shared static checker for pushes, pull requests, and manual CI runs. |

## Root files

| File | Responsibility |
| --- | --- |
| [Launcher](../kinetic.py) | The build and run command-line entry point. |
| [Package configuration](../pyproject.toml) | Packages the compiler directory directly and defines the installed command. |
| [Requirements](../requirements.txt) | The runtime Python dependency list. |
| [Overview](../README.md) | Introduction and quick start. |
| [Installation](../INSTALL.md) | Toolchain setup and command usage. |
| [Contributing](../CONTRIBUTING.md) | Development practices and verification workflows. |
| [Agent guidance](../AGENTS.md) | Shared instructions for coding agents. |
| [Claude Code guidance](../CLAUDE.md) | Claude Code's repository instructions. |
| [Roadmap](../ROADMAP.md) | Completed work, current priorities, and future milestones. |
| [License](../LICENSE) | Project licensing. |

## Working rules

- Keep compiler modules directly in the compiler package, with package-relative imports.
- Keep command-line launchers thin; pipeline logic belongs in the compilation API.
- Put runnable sample programs in the examples directory.
- Put maintenance commands in tools, not in the compiler pipeline.
- Add directories only when there is a real implementation to put in them.

The [architecture guide](architecture.md) explains how the compiler modules
interact. The roadmap describes future work without presenting it as existing
compiler functionality.
