"""Abstract syntax tree nodes for Kinetic V1."""

from dataclasses import dataclass


class Expr:
    """Base class for expressions."""


@dataclass
class NumberExpr(Expr):
    value: int


@dataclass
class StringExpr(Expr):
    value: str


@dataclass
class NameExpr(Expr):
    name: str


@dataclass
class BinaryExpr(Expr):
    operator: str
    left: Expr
    right: Expr


@dataclass
class CallExpr(Expr):
    callee: str
    arguments: list[Expr]


@dataclass
class ArrayExpr(Expr):
    elements: list[Expr]


@dataclass
class IndexExpr(Expr):
    collection: Expr
    index: Expr


class Statement:
    """Base class for statements."""


@dataclass
class LetStatement(Statement):
    name: str
    value: Expr
    is_mut: bool = False


@dataclass
class AssignStatement(Statement):
    name: str
    value: Expr


@dataclass
class ExpressionStatement(Statement):
    expression: Expr


@dataclass
class IfStatement(Statement):
    condition: Expr
    then_branch: list[Statement]
    else_branch: list[Statement] | None


@dataclass
class WhileStatement(Statement):
    condition: Expr
    body: list[Statement]


@dataclass
class Function:
    name: str
    parameters: list[str]
    body: list[Statement]


@dataclass
class Program:
    functions: list[Function]
