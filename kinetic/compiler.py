"""Public orchestration API for the Kinetic compilation pipeline."""

from llvmlite import binding

from kinetic.analyzer import TypeAnalyzer
from kinetic.backend import LLVMBackend
from kinetic.lexer import Lexer
from kinetic.parser import Parser


def compile_source(source: str) -> str:
    """Compile Kinetic source text into verified textual LLVM IR."""
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    function_types = TypeAnalyzer(program).analyze()
    llvm_ir = LLVMBackend(program, function_types).generate()

    module = binding.parse_assembly(llvm_ir)
    module.verify()
    return llvm_ir
