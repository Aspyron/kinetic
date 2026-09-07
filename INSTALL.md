# Installing and running Kinetic

## Requirements

- Python 3.10 or newer, with a version supported by the llvmlite release you install.
  A stable Python release is recommended; prerelease interpreters may not have
  compatible llvmlite wheels.
- llvmlite, the only runtime Python dependency.
- Clang on your executable search path for native builds and execution.

Clang is a separate toolchain dependency; installing the Python requirements
does not install it. Static repository checks need only Python.

## Work directly from a checkout

From the repository root, install the dependency listed in
[requirements.txt](requirements.txt):

```shell
python -m pip install -r requirements.txt
```

The root [launcher](kinetic.py) works without installing Kinetic itself:

```shell
python kinetic.py build examples/01_hello.kn
python kinetic.py run examples/01_hello.kn
```

The module entry point is also available:

```shell
python -m compiler run examples/01_hello.kn
```

## Optional editable installation

The [package configuration](pyproject.toml) installs the single
[compiler package](compiler/README.md):

```shell
python -m pip install -e .
```

This also installs the command-line entry point:

```shell
kinetic run examples/01_hello.kn
```

The editable installation reads its runtime dependency from the same
[requirements.txt](requirements.txt), so the two installation paths share one
dependency list. Paths to input programs are relative to your current working
directory.

## Build output

Both build and run write textual LLVM IR and a native executable next to the
input source. Windows executables have the usual executable extension;
Unix-like executables have no extension. The run command builds first and then
starts the resulting executable.

Clang may print a warning about overriding the module target triple. On its own,
that warning is not a build failure.

Common generated outputs are covered by [.gitignore](.gitignore). Remove artifacts
after manual verification, especially binaries from newly added examples.

## Static checks without a compiler toolchain

```shell
python -B tools/check.py
```

This does not require llvmlite or Clang and does not compile or run Kinetic code.
See [tests](tests/README.md) for the scope of these checks.
