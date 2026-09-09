class KineticError(Exception):
    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


class LexerError(KineticError):
    pass


class ParseError(KineticError):
    pass


class CompileError(KineticError):
    pass
