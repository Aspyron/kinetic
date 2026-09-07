class KineticError(Exception):
    pass


class LexerError(KineticError):
    pass


class ParseError(KineticError):
    pass


class CompileError(KineticError):
    pass
