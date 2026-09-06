"""Semantic analysis and type inference for Kinetic V1."""

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
from kinetic.errors import CompileError
from kinetic.types import FunctionType, KType


class TypeAnalyzer:
    """Infers function, parameter, variable, and expression types."""

    def __init__(self, program: Program):
        self.program = program
        function_names = {function.name for function in program.functions}
        if len(function_names) != len(program.functions):
            raise CompileError("Duplicate function definition")
        self.types = {
            function.name: FunctionType(
                [KType.UNKNOWN] * len(function.parameters), KType.UNKNOWN
            )
            for function in program.functions
        }

    def analyze(self) -> dict[str, FunctionType]:
        for _ in range(max(2, len(self.program.functions) + 1)):
            changed = False
            for function in self.program.functions:
                changed |= self._analyze_function(function)
            if not changed:
                break

        for name, signature in self.types.items():
            if any(kind is KType.UNKNOWN for kind in signature.parameters):
                raise CompileError(f"Could not infer all parameter types for {name!r}")
            if signature.result is KType.UNKNOWN:
                signature.result = KType.VOID
        return self.types

    @staticmethod
    def _unify(old: KType, new: KType, context: str) -> KType:
        if new is KType.UNKNOWN:
            return old
        if old is KType.UNKNOWN:
            return new
        if old is not new:
            raise CompileError(f"Type mismatch in {context}: {old.name} vs {new.name}")
        return old

    def _analyze_function(self, function: Function) -> bool:
        signature = self.types[function.name]
        
        # We zip the parameter names with their current inferred types to build the initial environment
        environment = dict(zip(function.parameters, signature.parameters))
        
        # Keep track of which variables are actually allowed to be modified
        mutables: set[str] = set()
        
        last_type = self._analyze_block(function.body, environment, mutables)

        changed = False
        
        # Now we feed the inferred types back into the function signature
        for index, parameter in enumerate(function.parameters):
            inferred = environment[parameter]
            unified = self._unify(
                signature.parameters[index], inferred, f"parameter {parameter!r}"
            )
            # If the type just became more specific (e.g. UNKNOWN -> INT), we mark it as changed
            if unified is not signature.parameters[index]:
                signature.parameters[index] = unified
                changed = True

        # C standard dictates the entry point main() must return an integer (usually 0 for success).
        expected_result = KType.INT if function.name == "main" else last_type
        
        unified_result = self._unify(
            signature.result, expected_result, f"return value of {function.name!r}"
        )
        if unified_result is not signature.result:
            signature.result = unified_result
            changed = True
            
        return changed

    def _analyze_block(self, block: list[Statement], environment: dict[str, KType], mutables: set[str]) -> KType:
        last_type = KType.VOID
        original_keys = set(environment.keys())
        original_mutables = set(mutables)
        
        for statement in block:
            if isinstance(statement, LetStatement):
                value_type = self._expr_type(statement.value, environment)
                if value_type is KType.VOID:
                    raise CompileError("Cannot assign a void expression")
                environment[statement.name] = value_type
                if statement.is_mut:
                    mutables.add(statement.name)
                last_type = KType.VOID
                
            elif isinstance(statement, AssignStatement):
                if statement.name not in environment:
                    raise CompileError(f"Undefined variable {statement.name!r}")
                if statement.name not in mutables:
                    raise CompileError(f"Cannot reassign immutable variable {statement.name!r}")
                value_type = self._expr_type(statement.value, environment)
                self._unify(environment[statement.name], value_type, f"assignment to {statement.name!r}")
                last_type = KType.VOID
                
            elif isinstance(statement, WhileStatement):
                cond_type = self._expr_type(statement.condition, environment)
                self._constrain_name(statement.condition, KType.BOOL, environment)
                if cond_type not in (KType.BOOL, KType.UNKNOWN):
                    raise CompileError("while condition must be boolean")
                self._analyze_block(statement.body, environment, mutables)
                last_type = KType.VOID
                
            elif isinstance(statement, IfStatement):
                cond_type = self._expr_type(statement.condition, environment)
                self._constrain_name(statement.condition, KType.BOOL, environment)
                if cond_type not in (KType.BOOL, KType.UNKNOWN):
                    raise CompileError("if condition must be boolean")
                
                then_type = self._analyze_block(statement.then_branch, environment, mutables)
                if statement.else_branch is not None:
                    else_type = self._analyze_block(statement.else_branch, environment, mutables)
                    last_type = self._unify(then_type, else_type, "if/else branches")
                else:
                    last_type = KType.VOID
                    
            elif isinstance(statement, ExpressionStatement):
                last_type = self._expr_type(statement.expression, environment)
                
        for key in list(environment.keys()):
            if key not in original_keys:
                del environment[key]
        for key in list(mutables):
            if key not in original_mutables:
                mutables.remove(key)
                
        return last_type

    def _expr_type(self, expression: Expr, environment: dict[str, KType]) -> KType:
        if isinstance(expression, NumberExpr):
            return KType.INT
        if isinstance(expression, StringExpr):
            return KType.STRING
        if isinstance(expression, NameExpr):
            if expression.name not in environment:
                raise CompileError(f"Undefined variable {expression.name!r}")
            return environment[expression.name]
        if isinstance(expression, ArrayExpr):
            for element in expression.elements:
                elem_type = self._expr_type(element, environment)
                self._unify(elem_type, KType.INT, "array element")
            return KType.INT_ARRAY
        if isinstance(expression, IndexExpr):
            collection_type = self._expr_type(expression.collection, environment)
            self._unify(collection_type, KType.INT_ARRAY, "array indexing collection")
            index_type = self._expr_type(expression.index, environment)
            self._unify(index_type, KType.INT, "array index")
            return KType.INT
        if isinstance(expression, BinaryExpr):
            return self._binary_type(expression, environment)
        if isinstance(expression, CallExpr):
            return self._call_type(expression, environment)
        raise AssertionError(f"Unhandled expression: {expression!r}")

    def _binary_type(
        self, expression: BinaryExpr, environment: dict[str, KType]
    ) -> KType:
        left = self._expr_type(expression.left, environment)
        right = self._expr_type(expression.right, environment)
        if left not in (KType.INT, KType.UNKNOWN) or right not in (
            KType.INT,
            KType.UNKNOWN,
        ):
            raise CompileError(f"Operator {expression.operator!r} requires integers")
        self._constrain_name(expression.left, KType.INT, environment)
        self._constrain_name(expression.right, KType.INT, environment)
        if expression.operator in ("==", "<", ">"):
            return KType.BOOL
        return KType.INT

    def _call_type(
        self, expression: CallExpr, environment: dict[str, KType]
    ) -> KType:
        argument_types = [
            self._expr_type(argument, environment)
            for argument in expression.arguments
        ]
        if expression.callee == "print":
            if len(argument_types) != 1 or argument_types[0] not in (
                KType.INT,
                KType.STRING,
            ):
                raise CompileError("print expects one integer or string argument")
            return KType.VOID
        if expression.callee not in self.types:
            raise CompileError(f"Undefined function {expression.callee!r}")

        signature = self.types[expression.callee]
        if len(argument_types) != len(signature.parameters):
            raise CompileError(
                f"Function {expression.callee!r} expects "
                f"{len(signature.parameters)} arguments"
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
