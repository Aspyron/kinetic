import unittest

try:
    import llvmlite.binding  # noqa: F401

    HAS_LLVMLITE = True
except ImportError:
    HAS_LLVMLITE = False


@unittest.skipUnless(HAS_LLVMLITE, "llvmlite is not installed")
class BackendTests(unittest.TestCase):
    def test_examples_generate_verified_ir(self):
        from compiler.compiler import compile_source
        from pathlib import Path

        examples = sorted(Path("examples").glob("*.kn"))
        self.assertEqual(len(examples), 5)
        for example in examples:
            with self.subTest(example=example.name):
                llvm_ir = compile_source(example.read_text(encoding="utf-8"))
                self.assertIn("define", llvm_ir)
                self.assertIn('@"main"', llvm_ir)

    def test_hello_world_ir_contains_printf(self):
        from compiler.compiler import compile_source
        from pathlib import Path

        llvm_ir = compile_source(
            Path("examples/01_hello.kn").read_text(encoding="utf-8")
        )
        self.assertIn("printf", llvm_ir)
        self.assertIn("Hello World!", llvm_ir)

    def test_inferred_forward_result_reaches_codegen(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func identity(value) {\n"
            "  value\n"
            "}\n"
            "func main() {\n"
            "  print(identity(1))\n"
            "}"
        )
        self.assertIn('define i64 @"identity"', llvm_ir)
        self.assertIn('call i64 @"identity"', llvm_ir)

    def test_compile_with_diagnostics_collects_warnings(self):
        from compiler.compiler import compile_with_diagnostics

        result = compile_with_diagnostics("func main() {\n  let x = 1\n}")
        self.assertEqual(len(result.diagnostics.warnings), 1)
        self.assertIn("define", result.llvm_ir)


if __name__ == "__main__":
    unittest.main()
