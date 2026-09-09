from .diagnostics import CompilationResult, Diagnostic, Diagnostics, Severity, SourceLocation

__all__ = [
    "CompilationResult",
    "Diagnostic",
    "Diagnostics",
    "Severity",
    "SourceLocation",
    "compile_source",
]


def __getattr__(name):
    if name == "compile_source":
        from .compiler import compile_source

        return compile_source
    raise AttributeError(f"module 'compiler' has no attribute {name!r}")
