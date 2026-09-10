# Claude Code guidance

@AGENTS.md

The shared [agent guidance](AGENTS.md) applies to Claude Code. It is the source of
truth for repository structure, compiler boundaries, and verification rules.

## Working context

- Kinetic is a 1.1.1 prototype compiler written in Python, using llvmlite and Clang.
- Compiler modules live directly in the [compiler package](compiler/README.md).
  Keep imports package-relative and avoid adding wrapper packages.
- The [root launcher](kinetic.py) delegates to the same CLI as the installed command.
- Use the [examples](examples/README.md) for documented build and run workflows.
- Consult [architecture](docs/architecture.md) and [contributing](CONTRIBUTING.md)
  before changing compiler stages or development tooling.

## Verification

For repository and documentation changes, use the static-only checker:

```shell
python -B tools/check.py
```

It needs only Python and does not import Kinetic, emit LLVM IR, invoke Clang, or
run Kinetic programs. When the user prohibits compilation or execution, do not
invoke the compilation API or native build commands, even as a smoke test.
Report skipped behavioral verification explicitly. Do not install dependencies
just to run these static checks.

The [GitHub workflow](.github/workflows/ci.yml) runs this same checker. Keep local
and hosted checks aligned, and do not interpret static CI results as evidence
that generated programs behave correctly.

## Roadmap discipline

Read [ROADMAP.md](ROADMAP.md) when planning language work. Self-hosting is a future
target, not an existing capability. Keep implemented functionality, planning,
and future work distinct; do not mark a milestone complete without evidence.
The 1.1.1 prototype does not provide a production memory-safety model.
