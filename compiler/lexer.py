import re

from .diagnostics import Diagnostics
from .errors import LexerError
from .tokens import Token, TokenKind


class Lexer:
    _token_re = re.compile(
        r"(?P<WHITESPACE>[ \t\r\n]+)"
        r"|(?P<COMMENT>//[^\n]*)"
        r'|(?P<STRING>"(?:\\.|[^"\\])*")'
        r"|(?P<NUMBER>\d+)"
        r"|(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)"
        r"|(?P<EQEQ>==)"
        r"|(?P<NEQ>!=)"
        r"|(?P<EQUAL>=)"
        r"|(?P<LSHIFT><<)"
        r"|(?P<LE><=)"
        r"|(?P<LT><)"
        r"|(?P<RSHIFT>>>)"
        r"|(?P<GE>>=)"
        r"|(?P<GT>>)"
        r"|(?P<PLUS>\+)"
        r"|(?P<MINUS>-)"
        r"|(?P<STAR>\*)"
        r"|(?P<SLASH>/)"
        r"|(?P<PERCENT>%)"
        r"|(?P<AMP>&)"
        r"|(?P<PIPE>\|)"
        r"|(?P<CARET>\^)"
        r"|(?P<LPAREN>\()"
        r"|(?P<RPAREN>\))"
        r"|(?P<LBRACE>\{)"
        r"|(?P<RBRACE>\})"
        r"|(?P<LBRACKET>\[)"
        r"|(?P<RBRACKET>\])"
        r"|(?P<COMMA>,)"
    )
    _keywords = {
        "func": TokenKind.FUNC,
        "let": TokenKind.LET,
        "mut": TokenKind.MUT,
        "while": TokenKind.WHILE,
        "if": TokenKind.IF,
        "else": TokenKind.ELSE,
    }
    _removed_keywords = {
        "fn": "the 'fn' keyword was removed in 1.0.0; declare functions with 'func'",
    }

    def __init__(self, source: str, diagnostics: Diagnostics | None = None):
        self.source = source
        self.diagnostics = diagnostics

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        position = 0
        line = 1
        column = 1

        while position < len(self.source):
            match = self._token_re.match(self.source, position)
            if match is None:
                raise LexerError(
                    f"unexpected character {self.source[position]!r}",
                    line,
                    column,
                )

            text = match.group(0)
            kind_name = match.lastgroup
            token_line, token_column = line, column
            line, column = self._advance_location(text, line, column)
            position = match.end()

            if kind_name in ("WHITESPACE", "COMMENT"):
                continue

            kind = self._token_kind(kind_name, text, token_line, token_column)
            value = self._token_value(kind, text, token_line, token_column)
            tokens.append(Token(kind, value, token_line, token_column))

        tokens.append(Token(TokenKind.EOF, "", line, column))
        return tokens

    @staticmethod
    def _advance_location(text: str, line: int, column: int) -> tuple[int, int]:
        newline_count = text.count("\n")
        if newline_count:
            return line + newline_count, len(text) - text.rfind("\n")
        return line, column + len(text)

    def _token_kind(
        self, kind_name: str | None, text: str, line: int, column: int
    ) -> TokenKind:
        if kind_name is None:
            raise AssertionError("Lexer regex produced an unnamed token")
        if kind_name == "IDENT":
            if text in self._removed_keywords:
                hint = self._removed_keywords[text]
                raise LexerError(f"{hint}", line, column)
            return self._keywords.get(text, TokenKind.IDENT)
        return TokenKind[kind_name]

    @staticmethod
    def _token_value(
        kind: TokenKind, text: str, line: int, column: int
    ) -> str:
        if kind is not TokenKind.STRING:
            return text
        try:
            return bytes(text[1:-1], "utf-8").decode("unicode_escape")
        except UnicodeDecodeError as error:
            raise LexerError("invalid string escape", line, column) from error
