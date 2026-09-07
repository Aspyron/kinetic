# Kinetic examples

These are complete programs for learning and experimenting with the 1.0.0 language.

| Program | Focus |
| --- | --- |
| [Hello World](01_hello.kn) | A minimal function that prints a greeting. |
| [Logic](02_logic.kn) | Immutable and mutable bindings, conditional branches, and loops. |
| [Arrays](03_arrays.kn) | Array indexing, arithmetic, and a conditional check. |

Read the [syntax guide](../docs/syntax_guide.md) for the language rules.

Declarations use [`func`](../compiler/lexer.py:33) for functions,
[`let`](../compiler/lexer.py:34) for immutable bindings, and standalone
[`mut`](../compiler/lexer.py:35) for mutable bindings.

When native builds are appropriate and the toolchain is installed, run an example
from the repository root:

```shell
python kinetic.py run examples/01_hello.kn
```

This command compiles and executes the program and writes artifacts alongside
the source. It is not part of the [static repository checks](../tests/README.md).
