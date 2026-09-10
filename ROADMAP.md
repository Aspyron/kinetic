# Kinetic roadmap

## Goal

Kinetic's next major destination is **self-hosting**: a compiler written in
Kinetic that can compile its own source and build a working successor compiler.

The current compiler is a Python 1.1.1 prototype. It is not self-hosting, and no
compiler stage has been ported to Kinetic yet. The language and runtime need
additional capabilities before that port is practical.

This roadmap is ordered by dependencies, not release dates. An implemented
prototype feature is not a promise of production readiness or memory safety.

## Done — implemented foundations

- [x] Lexer with keywords, literals, comments, and source locations.
- [x] Recursive-descent parser and an abstract syntax tree.
- [x] Function calls, type inference, and implicit function returns.
- [x] Immutable bindings, opt-in mutation, conditional branches, and loops.
- [x] Integer arithmetic, equality and ordered comparisons, string literals,
  and integer-array literals with indexed reads.
- [x] Printing builtin accepting one integer or string.
- [x] LLVM IR generation and verification through llvmlite.
- [x] Command-line build and run workflows using Clang for native executables.
- [x] A flat compiler package, example programs, user documentation, and agent guidance.
- [x] Static checks for repository layout, Python syntax, imports, and documentation.
- [x] Structured compile-time diagnostics: located `error: line:column` output,
  migration hints for removed syntax, unused-variable and shadowing warnings,
  constant array-bounds errors, and pluralized warning summaries.

See the [syntax guide](docs/syntax_guide.md) for the current language and the
[architecture guide](docs/architecture.md) for the implementation. Frontend
behavioral tests run without any external dependency; backend tests require
llvmlite and native tests require Clang (both are opt-in and skip cleanly).

## In progress

### Declaration syntax and CI rollout

The compiler sources, examples, and guides now use
[`func`](compiler/lexer.py:33), [`let`](compiler/lexer.py:34), and standalone
[`mut`](compiler/lexer.py:35). The [Hello World example](examples/01_hello.kn)
shows the function declaration in a complete program.

The [GitHub workflow](.github/workflows/ci.yml) is configured to run the shared
static checker on Windows and Linux. Local static verification has passed;
native behavior checks for the syntax change and the first hosted CI run are
still pending. Do not mark those verification steps complete based on static
source inspection alone.

### Self-hosting preparation

The current focus is identifying the smallest coherent language and runtime
needed to implement a compiler. This is planning work, not an active compiler
port or an implemented runtime expansion.

- Define the bootstrap subset and the order in which its missing capabilities
  should be added.
- Identify representations for tokens, syntax trees, types, symbol tables, and
  generated output.
- Decide the allocation, lifetime, and host-runtime boundaries those structures need.
- Define the behavioral tests and bootstrap checks required to demonstrate success.

**Planning is complete when:** the subset, runtime interfaces, and acceptance
tests have concrete specifications. The milestones below are the proposed
sequence; their implementations remain future work.

## Milestones toward self-hosting

### 1. Establish a reliable bootstrap compiler

- [x] Add automated lexer, parser, analyzer, and code-generation regression tests
  ([frontend](tests/test_frontend.py), [backend](tests/test_backend.py)).
- [x] Add expected diagnostics for invalid programs (located errors, migration
  hints, warning emission, and summary pluralization).
- [x] Specify and test scoping, inference, immutability, array bounds, and error
  handling within the 1.0.0 language surface.
- [x] Define the supported toolchain versions (llvmlite pinned in
  [requirements.txt](requirements.txt), Python 3.10+, Clang for native builds)
  and a repeatable verification workflow ([static + behavioral CI](.github/workflows/ci.yml)).
- [ ] Run the native example suite on a machine with Clang
  (`KINETIC_NATIVE_TESTS=1 python -B tools/check.py`) and record expected outputs.

**Status:** substantially complete. The remaining item is the first hosted CI
run plus a native-build pass on a Clang-equipped machine; neither changes the
1.0.0 language, they only confirm the toolchain end to end.

### 2. Add the language and runtime building blocks

- [ ] Source-text operations: lengths, byte or character access, comparison,
  slicing, and construction of output strings.
- [ ] Data structures suitable for compiler records and variants, growable
  buffers, and symbol lookup; choose the minimum useful design before adding features.
- [ ] Mutable indexed storage and explicit collection-size handling.
- [ ] Defined allocation and lifetime rules for compiler-owned data, with checks
  appropriate to the chosen design.
- [ ] File input/output, command-line arguments, diagnostics, and error/status reporting.
- [ ] Multi-file organization and a way to resolve compiler modules.
- [ ] A documented interface to native services and the LLVM/Clang toolchain
  that does not require Python-specific llvmlite APIs inside Kinetic code.

**Complete when:** Kinetic programs can read source files, build and traverse
compiler data structures, report errors, and write generated output with tested
resource-management behavior. This does not by itself establish production memory safety.

### 3. Implement the compiler in Kinetic incrementally

- [ ] Write a lexer in Kinetic and compare its results with the Python implementation.
- [ ] Port parsing and syntax-tree construction.
- [ ] Port semantic analysis and type checking.
- [ ] Implement code generation and a build driver using the agreed toolchain interface.
- [ ] Run the same language and diagnostic regression suites against both implementations.

The Python compiler remains the bootstrap implementation during this work.
Port one stage at a time, and establish parity before replacing a working stage.
Textual LLVM IR remains a possible output; the backend interface must be decided
and tested before the port depends on it.

**Complete when:** the Python compiler can build a Kinetic-written compiler that
compiles the agreed language subset and passes its regression suite.

### 4. Demonstrate a repeatable self-hosting cycle

- [ ] Use the Python bootstrap compiler to build the Kinetic compiler: stage 1.
- [ ] Use stage 1 to compile the same compiler sources: stage 2.
- [ ] Use stage 2 to rebuild the compiler and run the regression suite without
  using the Python compiler for those compilations.
- [ ] Compare deterministic generated output across rebuilds, accounting explicitly
  for any non-semantic build metadata.
- [ ] Document the bootstrap procedure, retained bootstrap version, and recovery path.

**Self-hosting is achieved when:** the Kinetic-written compiler rebuilds itself
and the resulting compiler passes the required behavior tests. LLVM, Clang,
and native runtime dependencies may remain; self-hosting does not mean rewriting
the entire native toolchain in Kinetic.

## After self-hosting

- [ ] Improve diagnostics, tooling, performance, and platform coverage.
- [ ] Evolve runtime and library facilities based on real compiler and user workloads.
- [ ] Maintain a reproducible bootstrap path as the language evolves.

Update this document when implementation and verification change a milestone's
status. Do not treat a planned capability as part of the current language.
