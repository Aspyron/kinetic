from llvmlite import binding

from .analyzer import TypeAnalyzer
from .backend import LLVMBackend
from .lexer import Lexer
from .parser import Parser


def compile_source(source: str) -> str:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    function_types = TypeAnalyzer(program).analyze()
    llvm_ir = LLVMBackend(program, function_types).generate()

    module = binding.parse_assembly(llvm_ir)
    module.verify()
    return llvm_ir
