"""Recursive-descent parser for Kinetic V1."""

from kinetic.ast import (
    ArrayExpr,
    AssignStatement,
    BinaryExpr,
    CallExpr,
    Expr,
    ExpressionStatement,
    Function,
    IfStatement,
    IndexExpr,
    LetStatement,
    NameExpr,
    NumberExpr,
    Program,
    Statement,
    StringExpr,
    WhileStatement,
)
from kinetic.errors import ParseError
from kinetic.tokens import Token, TokenKind


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def parse(self) -> Program:
        functions: list[Function] = []
        while self.current.kind is not TokenKind.EOF:
            functions.append(self._parse_function())
        return Program(functions)

    def _advance(self) -> Token:
        token = self.current
        self.index += 1
        return token

    def _expect(self, kind: TokenKind, message: str) -> Token:
        if self.current.kind is not kind:
            token = self.current
            raise ParseError(f"{message} at {token.line}:{token.column}")
        return self._advance()

    def _match(self, kind: TokenKind) -> bool:
        if self.current.kind is kind:
            self._advance()
            return True
        return False

    def _parse_function(self) -> Function:
        self._expect(TokenKind.FN, "Expected 'fn'")
        name = self._expect(TokenKind.IDENT, "Expected function name").value
        self._expect(TokenKind.LPAREN, "Expected '('")
        parameters = self._parse_parameters()
        self._expect(TokenKind.RPAREN, "Expected ')'")
        self._expect(TokenKind.LBRACE, "Expected '{'")
        body = self._parse_block()
        return Function(name, parameters, body)

    def _parse_parameters(self) -> list[str]:
        parameters: list[str] = []
        if self.current.kind is TokenKind.RPAREN:
            return parameters
        while True:
            parameters.append(
                self._expect(TokenKind.IDENT, "Expected parameter name").value
            )
            if not self._match(TokenKind.COMMA):
                return parameters

    def _parse_block(self) -> list[Statement]:
        body: list[Statement] = []
        while self.current.kind is not TokenKind.RBRACE:
            if self.current.kind is TokenKind.EOF:
                raise ParseError("Unclosed block")
            body.append(self._parse_statement())
        self._advance()
        return body

    def _parse_statement(self) -> Statement:
        if self._match(TokenKind.LET):
            is_mut = self._match(TokenKind.MUT)
            name = self._expect(TokenKind.IDENT, "Expected variable name").value
            self._expect(TokenKind.EQUAL, "Expected '='")
            return LetStatement(name, self._parse_expression(), is_mut)
            
        if self._match(TokenKind.WHILE):
            condition = self._parse_expression()
            self._expect(TokenKind.LBRACE, "Expected '{'")
            body = self._parse_block()
            return WhileStatement(condition, body)
            
        if self._match(TokenKind.IF):
            condition = self._parse_expression()
            self._expect(TokenKind.LBRACE, "Expected '{'")
            then_branch = self._parse_block()
            else_branch = None
            if self._match(TokenKind.ELSE):
                self._expect(TokenKind.LBRACE, "Expected '{'")
                else_branch = self._parse_block()
            return IfStatement(condition, then_branch, else_branch)
            
        if self.current.kind is TokenKind.IDENT:
            if self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].kind is TokenKind.EQUAL:
                name = self._advance().value
                self._expect(TokenKind.EQUAL, "Expected '='")
                return AssignStatement(name, self._parse_expression())
                
        return ExpressionStatement(self._parse_expression())

    def _parse_expression(self) -> Expr:
        return self._parse_equality()

    def _parse_equality(self) -> Expr:
        expression = self._parse_relational()
        while self.current.kind is TokenKind.EQEQ:
            operator = self._advance().value
            expression = BinaryExpr(operator, expression, self._parse_relational())
        return expression

    def _parse_relational(self) -> Expr:
        expression = self._parse_additive()
        while self.current.kind in (TokenKind.LT, TokenKind.GT):
            operator = self._advance().value
            expression = BinaryExpr(operator, expression, self._parse_additive())
        return expression

    def _parse_additive(self) -> Expr:
        expression = self._parse_multiplicative()
        while self.current.kind in (TokenKind.PLUS, TokenKind.MINUS):
            operator = self._advance().value
            expression = BinaryExpr(
                operator, expression, self._parse_multiplicative()
            )
        return expression

    def _parse_multiplicative(self) -> Expr:
        expression = self._parse_postfix()
        while self.current.kind in (TokenKind.STAR, TokenKind.SLASH):
            operator = self._advance().value
            expression = BinaryExpr(operator, expression, self._parse_postfix())
        return expression

    def _parse_postfix(self) -> Expr:
        expression = self._parse_primary()
        while True:
            if self._match(TokenKind.LPAREN):
                if not isinstance(expression, NameExpr):
                    raise ParseError("Only names can be called")
                expression = CallExpr(expression.name, self._parse_arguments())
            elif self._match(TokenKind.LBRACKET):
                index = self._parse_expression()
                self._expect(TokenKind.RBRACKET, "Expected ']'")
                expression = IndexExpr(expression, index)
            else:
                break
        return expression

    def _parse_primary(self) -> Expr:
        token = self.current
        if self._match(TokenKind.NUMBER):
            return NumberExpr(int(token.value))
        if self._match(TokenKind.STRING):
            return StringExpr(token.value)
        if self._match(TokenKind.IDENT):
            return NameExpr(token.value)
        if self._match(TokenKind.LBRACKET):
            elements = []
            if self.current.kind is not TokenKind.RBRACKET:
                while True:
                    elements.append(self._parse_expression())
                    if not self._match(TokenKind.COMMA):
                        break
            self._expect(TokenKind.RBRACKET, "Expected ']'")
            return ArrayExpr(elements)
        if self._match(TokenKind.LPAREN):
            expression = self._parse_expression()
            self._expect(TokenKind.RPAREN, "Expected ')'")
            return expression
        raise ParseError(
            f"Expected expression at {token.line}:{token.column}, got {token.value!r}"
        )

    def _parse_arguments(self) -> list[Expr]:
        arguments: list[Expr] = []
        if self.current.kind is not TokenKind.RPAREN:
            while True:
                arguments.append(self._parse_expression())
                if not self._match(TokenKind.COMMA):
                    break
        self._expect(TokenKind.RPAREN, "Expected ')' after arguments")
        return arguments
