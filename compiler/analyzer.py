from .ast import (
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
from .diagnostics import Diagnostics
from .errors import CompileError
from .types import FunctionType, KType


class TypeAnalyzer:
    def __init__(self, program: Program, diagnostics: Diagnostics | None = None):
        self.program = program
        self.diagnostics = (
            diagnostics if diagnostics is not None else Diagnostics()
        )
        function_names = {function.name for function in program.functions}
        if len(function_names) != len(program.functions):
            raise CompileError("duplicate function definition")
        if program.functions and "main" not in function_names:
            location = program.functions[0].location
            raise CompileError(
                "program has no 'main' entry point",
                location.line if location else None,
                location.column if location else None,
            )
        self.types = {
            function.name: FunctionType(
                [KType.UNKNOWN] * len(function.parameters), KType.UNKNOWN
            )
            for function in program.functions
        }
        self._array_lengths: dict[str, int] = {}

    def analyze(self) -> dict[str, FunctionType]:
        for _ in range(max(2, len(self.program.functions) + 1)):
            changed = False
            for function in self.program.functions:
                changed |= self._analyze_function(function)
            if not changed:
                break

        for name, signature in self.types.items():
            if any(kind is KType.UNKNOWN for kind in signature.parameters):
                function = next(
                    item for item in self.program.functions if item.name == name
                )
                location = function.location
                raise CompileError(
                    f"could not infer all parameter types for {name!r}",
                    location.line if location else None,
                    location.column if location else None,
                )
            if signature.result is KType.UNKNOWN:
                signature.result = KType.VOID
        return self.types

    @staticmethod
    def _location_of(expression: Expr | Statement) -> tuple[int | None, int | None]:
        location = expression.location
        if location is None:
            return None, None
        return location.line, location.column

    @staticmethod
    def _unify(old: KType, new: KType, context: str) -> KType:
        if new is KType.UNKNOWN:
            return old
        if old is KType.UNKNOWN:
            return new
        if old is not new:
            raise CompileError(f"type mismatch in {context}: {old.name} vs {new.name}")
        return old

    def _analyze_function(self, function: Function) -> bool:
        signature = self.types[function.name]

        environment = dict(zip(function.parameters, signature.parameters))

        mutables: set[str] = set()
        used: set[str] = set()

        last_type = self._analyze_block(
            function.body, environment, mutables, used
        )

        for name, statement_location in self._declared_bindings(function.body):
            if name not in used and name not in function.parameters:
                self.diagnostics.warn(
                    f"variable {name!r} is never used",
                    statement_location,
                )

        changed = False

        for index, parameter in enumerate(function.parameters):
            inferred = environment[parameter]
            unified = self._unify(
                signature.parameters[index], inferred, f"parameter {parameter!r}"
            )
            if unified is not signature.parameters[index]:
                signature.parameters[index] = unified
                changed = True

        expected_result = KType.INT if function.name == "main" else last_type

        unified_result = self._unify(
            signature.result, expected_result, f"return value of {function.name!r}"
        )
        if unified_result is not signature.result:
            signature.result = unified_result
            changed = True

        return changed

    def _declared_bindings(self, block: list[Statement]):
        for statement in block:
            if isinstance(statement, LetStatement):
                yield statement.name, statement.location
            if isinstance(statement, IfStatement):
                yield from self._declared_bindings(statement.then_branch)
                if statement.else_branch is not None:
                    yield from self._declared_bindings(statement.else_branch)
            if isinstance(statement, WhileStatement):
                yield from self._declared_bindings(statement.body)

    def _analyze_block(
        self,
        block: list[Statement],
        environment: dict[str, KType],
        mutables: set[str],
        used: set[str],
    ) -> KType:
        last_type = KType.VOID
        original_keys = set(environment.keys())
        original_mutables = set(mutables)
        original_lengths = set(self._array_lengths.keys())

        for statement in block:
            if isinstance(statement, LetStatement):
                if statement.name in environment:
                    self.diagnostics.warn(
                        f"declaration of {statement.name!r} shadows an "
                        "existing binding",
                        statement.location,
                    )
                value_type = self._expr_type(statement.value, environment, used)
                if value_type is KType.VOID:
                    line, column = self._location_of(statement)
                    raise CompileError(
                        "cannot bind a void expression", line, column
                    )
                environment[statement.name] = value_type
                if statement.is_mut:
                    mutables.add(statement.name)
                if isinstance(statement.value, ArrayExpr):
                    self._array_lengths[statement.name] = len(
                        statement.value.elements
                    )
                last_type = KType.VOID

            elif isinstance(statement, AssignStatement):
                line, column = self._location_of(statement)
                if statement.name not in environment:
                    raise CompileError(
                        f"undefined variable {statement.name!r}", line, column
                    )
                if statement.name not in mutables:
                    raise CompileError(
                        f"cannot reassign immutable variable {statement.name!r}",
                        line,
                        column,
                    )
                used.add(statement.name)
                value_type = self._expr_type(statement.value, environment, used)
                self._unify(
                    environment[statement.name],
                    value_type,
                    f"assignment to {statement.name!r}",
                )
                last_type = KType.VOID

            elif isinstance(statement, WhileStatement):
                cond_type = self._expr_type(statement.condition, environment, used)
                self._constrain_name(statement.condition, KType.BOOL, environment)
                if cond_type not in (KType.BOOL, KType.UNKNOWN):
                    line, column = self._location_of(statement.condition)
                    raise CompileError(
                        "while condition must be a boolean", line, column
                    )
                self._analyze_block(statement.body, environment, mutables, used)
                last_type = KType.VOID

            elif isinstance(statement, IfStatement):
                cond_type = self._expr_type(statement.condition, environment, used)
                self._constrain_name(statement.condition, KType.BOOL, environment)
                if cond_type not in (KType.BOOL, KType.UNKNOWN):
                    line, column = self._location_of(statement.condition)
                    raise CompileError(
                        "if condition must be a boolean", line, column
                    )

                then_type = self._analyze_block(
                    statement.then_branch, environment, mutables, used
                )
                if statement.else_branch is not None:
                    else_type = self._analyze_block(
                        statement.else_branch, environment, mutables, used
                    )
                    last_type = self._unify(then_type, else_type, "if/else branches")
                else:
                    last_type = KType.VOID

            elif isinstance(statement, ExpressionStatement):
                last_type = self._expr_type(statement.expression, environment, used)

        for key in list(environment.keys()):
            if key not in original_keys:
                del environment[key]
        for key in list(mutables):
            if key not in original_mutables:
                mutables.remove(key)
        for key in list(self._array_lengths.keys()):
            if key not in original_lengths:
                del self._array_lengths[key]

        return last_type

    def _expr_type(
        self, expression: Expr, environment: dict[str, KType], used: set[str]
    ) -> KType:
        if isinstance(expression, NumberExpr):
            return KType.INT
        if isinstance(expression, StringExpr):
            return KType.STRING
        if isinstance(expression, NameExpr):
            if expression.name not in environment:
                line, column = self._location_of(expression)
                raise CompileError(
                    f"undefined variable {expression.name!r}", line, column
                )
            used.add(expression.name)
            return environment[expression.name]
        if isinstance(expression, ArrayExpr):
            for element in expression.elements:
                elem_type = self._expr_type(element, environment, used)
                self._unify(elem_type, KType.INT, "array element")
            return KType.INT_ARRAY
        if isinstance(expression, IndexExpr):
            collection_type = self._expr_type(
                expression.collection, environment, used
            )
            self._unify(collection_type, KType.INT_ARRAY, "array indexing collection")
            index_type = self._expr_type(expression.index, environment, used)
            self._unify(index_type, KType.INT, "array index")
            if (
                isinstance(expression.collection, NameExpr)
                and isinstance(expression.index, NumberExpr)
            ):
                self._check_constant_bounds(expression, environment)
            return KType.INT
        if isinstance(expression, BinaryExpr):
            return self._binary_type(expression, environment, used)
        if isinstance(expression, CallExpr):
            return self._call_type(expression, environment, used)
        raise AssertionError(f"Unhandled expression: {expression!r}")

    def _check_constant_bounds(
        self, expression: IndexExpr, environment: dict[str, KType]
    ) -> None:
        index = expression.index
        if not isinstance(index, NumberExpr) or index.value < 0:
            return
        lengths = self._array_lengths.get(expression.collection.name, None)
        if lengths is not None and index.value >= lengths:
            line, column = self._location_of(expression)
            raise CompileError(
                f"index {index.value} is out of bounds for array "
                f"{expression.collection.name!r} of length {lengths}",
                line,
                column,
            )

    def _binary_type(
        self, expression: BinaryExpr, environment: dict[str, KType], used: set[str]
    ) -> KType:
        left = self._expr_type(expression.left, environment, used)
        right = self._expr_type(expression.right, environment, used)
        if left not in (KType.INT, KType.UNKNOWN) or right not in (
            KType.INT,
            KType.UNKNOWN,
        ):
            line, column = self._location_of(expression)
            raise CompileError(
                f"operator {expression.operator!r} requires integers",
                line,
                column,
            )
        self._constrain_name(expression.left, KType.INT, environment)
        self._constrain_name(expression.right, KType.INT, environment)
        if expression.operator in ("==", "<", ">"):
            return KType.BOOL
        return KType.INT

    def _call_type(
        self, expression: CallExpr, environment: dict[str, KType], used: set[str]
    ) -> KType:
        argument_types = [
            self._expr_type(argument, environment, used)
            for argument in expression.arguments
        ]
        if expression.callee == "print":
            if len(argument_types) != 1 or argument_types[0] not in (
                KType.INT,
                KType.STRING,
            ):
                line, column = self._location_of(expression)
                raise CompileError(
                    "print expects one integer or string argument", line, column
                )
            return KType.VOID
        if expression.callee not in self.types:
            line, column = self._location_of(expression)
            raise CompileError(
                f"undefined function {expression.callee!r}", line, column
            )

        signature = self.types[expression.callee]
        if len(argument_types) != len(signature.parameters):
            line, column = self._location_of(expression)
            raise CompileError(
                f"function {expression.callee!r} expects "
                f"{len(signature.parameters)} arguments",
                line,
                column,
            )
        for index, argument_type in enumerate(argument_types):
            signature.parameters[index] = self._unify(
                signature.parameters[index],
                argument_type,
                f"call to {expression.callee!r}",
            )
        return signature.result

    def _constrain_name(
        self, expression: Expr, required: KType, environment: dict[str, KType]
    ) -> None:
        if isinstance(expression, NameExpr):
            environment[expression.name] = self._unify(
                environment[expression.name], required, expression.name
            )
