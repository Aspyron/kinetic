# Warning examples

These programs **compile successfully**, but the compiler emits warnings to
stderr to point out code that is probably not what you intended.

Build any of them with:

```shell
python kinetic.py build examples/warnings/<file>.kn
```

You will see output shaped like:

```text
kinetic: warn: <line>:<column>: <message>
kinetic: N warning(s) emitted
Building ...
Build successful!
```

| Program | Warning it demonstrates |
| --- | --- |
| [unused_variable.kn](unused_variable.kn) | A binding that is declared but never read. |
| [shadowing.kn](shadowing.kn) | An inner declaration that reuses (shadows) an outer name. |

Warnings never stop the build — they are the compiler telling you it handled
the code, but you may want to clean it up. See [errors](../errors/README.md)
for diagnostics that do stop compilation.
