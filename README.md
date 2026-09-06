# Welcome to Kinetic 👋

> A systems-level programming language designed for humans. Achieve zero-cost performance and strict safety, completely free from the mental gymnastics of complex memory ownership models.

Hey there! If you're reading this, you're looking at the very first prototype of the Kinetic compiler (V1). 

We built this because we wanted the blazing-fast execution speeds of C/C++ without having to constantly fight with the compiler over borrow checking or manually tracking `malloc` and `free`. 

This repository contains everything you need to take `.kn` source files, parse them, run type-checking, and spit out LLVM Intermediate Representation (IR). From there, we hand it off to `clang` to give you a native, runnable binary!

## What's in the box? 📦

V1 is intentionally small and focused so we can get the core architecture right before we pile on features. Right now we support:
- Implicit returns
- Super smart type inference (you don't write `: i32`, we figure it out)
- `if` / `else` control flow
- `while` loops
- Mutable and immutable variables
- Arrays and array indexing!

## Project Structure

```text
Kinetic/
|-- kinetic.py             # Our friendly CLI tool!
|-- main.kn                # Your playground file
|-- requirements.txt       # Python dependencies (just llvmlite)
|-- README.md              # You are here!
|-- docs/
|   `-- syntax_guide.md    # Quick tutorial on how to write Kinetic
|-- examples/              # Cool snippets showing what Kinetic can do
`-- kinetic/               # The actual compiler brains
    |-- __init__.py
    |-- errors.py          # Custom error handling
    |-- tokens.py          # The building blocks (Tokens)
    |-- lexer.py           # Breaks your code down into Tokens
    |-- ast.py             # The Tree structure of your code
    |-- parser.py          # Turns Tokens into the AST
    |-- types.py           # Type Definitions (Int, String, Array)
    |-- analyzer.py        # Validates types and logic (The semantic pass)
    |-- backend.py         # Converts the AST into LLVM machine instructions
    |-- compiler.py        # Glues all the phases together
    `-- cli.py             # Handles the 'build' and 'run' terminal commands
```

## Getting Started 🚀

**Requirements:**
- Python 3.10 or newer
- `clang` installed and in your system PATH (so we can build the final binary).

**Installation:**
```shell
# Grab the LLVM Python bindings
python -m pip install -r requirements.txt
```

**Running Code:**
We built a super handy CLI wrapper around the compiler.

If you just want to compile your code to a binary:
```shell
python kinetic.py build main.kn
```

If you want to compile AND run it immediately:
```shell
python kinetic.py run main.kn
```

## How the magic happens

When you run `kinetic.py`, your code goes on a little journey:

1. **Lexical Analysis (`lexer.py`)**: First, we chew through your source code using Regex and chop it up into `Tokens` (like `NUMBER`, `IDENTIFIER`, `WHITESPACE`). We attach line numbers to everything so if you make a typo, we can tell you exactly where it is!
2. **Parsing (`parser.py`)**: We take that flat list of tokens and build a 3D tree out of it (the Abstract Syntax Tree). This is where we figure out the order of operations (like doing `*` before `+`).
3. **Semantic Analysis (`analyzer.py`)**: The AST doesn't know what types are. The analyzer walks the tree and acts like a detective. Oh, `x = 5`? `x` must be an Integer! Trying to do `x + "hello"`? The analyzer throws a compilation error.
4. **LLVM Generation (`backend.py`)**: Finally, we translate your validated AST into LLVM IR. For example, a `+` symbol becomes an `add` instruction, and arrays get their own memory space allocated via `alloca`. We then pass that IR to `clang` to give you a real binary!

## Next Steps

Want to see what Kinetic code looks like? Go check out the `examples/` folder, or read the full breakdown in `docs/syntax_guide.md`. Happy coding!
