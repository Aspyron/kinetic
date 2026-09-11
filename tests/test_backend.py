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
        self.assertEqual(len(examples), 6)
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

    def test_extended_operators_lower_to_expected_opcodes(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func main() {\n"
            "  let a = 7 % 3\n"
            "  let b = 5 & 6\n"
            "  let c = 5 | 6\n"
            "  let d = 5 ^ 6\n"
            "  let e = 1 << 4\n"
            "  let f = 32 >> 2\n"
            "  if a != b {\n"
            "    print(a)\n"
            "  }\n"
            "  if a <= b {\n"
            "    print(b)\n"
            "  }\n"
            "  if a >= b {\n"
            "    print(c)\n"
            "  }\n"
            "  print(d + e + f)\n"
            "}"
        )
        for opcode in (
            "srem i64",
            "and i64",
            "or i64",
            "xor i64",
            "shl i64",
            "ashr i64",
            "icmp ne i64",
            "icmp sle i64",
            "icmp sge i64",
        ):
            with self.subTest(opcode=opcode):
                self.assertIn(opcode, llvm_ir)

    def test_index_assignment_emits_element_store(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func main() {\n"
            "  mut xs = [1, 2]\n"
            "  xs[1] = 9\n"
            "  print(xs[1])\n"
            "}"
        )
        self.assertIn("store i64 9, ", llvm_ir)


if __name__ == "__main__":
    unittest.main()
