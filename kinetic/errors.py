"""Compiler-specific exception types."""


class KineticError(Exception):
    """Base class for errors that should be reported to Kinetic users."""


class LexerError(KineticError):
    """Raised when source text cannot be tokenized."""


class ParseError(KineticError):
    """Raised when a token sequence does not match Kinetic grammar."""


class CompileError(KineticError):
    """Raised during semantic analysis or LLVM IR generation."""
