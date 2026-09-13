import unittest

try:
    import llvmlite.binding

    HAS_LLVMLITE = True
except ImportError:
    HAS_LLVMLITE = False


@unittest.skipUnless(HAS_LLVMLITE, "llvmlite is not installed")
class BackendTests(unittest.TestCase):
    def test_examples_generate_verified_ir(self):
        from compiler.compiler import compile_source
        from pathlib import Path

        examples = sorted(Path("examples").glob("*.kn"))
        self.assertTrue(examples, "No valid examples were found")
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

    def test_length_reads_array_metadata(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func count(values) { len(values) }\n"
            "func main() { let empty = [] print(len(empty)) print(count([1, 2])) }"
        )
        self.assertIn("insertvalue", llvm_ir)
        self.assertIn("extractvalue", llvm_ir)
        self.assertIn('call i64 @"count"', llvm_ir)
        self.assertNotIn('@"len"', llvm_ir)

    def test_array_metadata_survives_forwarding_and_reassignment(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func main() {\n"
            "  mut values = [1]\n"
            "  let replacement = [2, 3, 4]\n"
            "  values = identity(replacement)\n"
            "  print(len(values))\n"
            "  let index = 2\n"
            "  print(values[index])\n"
            "}\n"
            "func identity(values) { values }"
        )
        self.assertIn('call {i64*, i64} @"identity"', llvm_ir)
        self.assertIn("store {i64*, i64}", llvm_ir)
        self.assertIn("load {i64*, i64}", llvm_ir)
        self.assertIn("extractvalue", llvm_ir)

    def test_length_evaluates_function_argument_once(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func observe(values) { print(99) values }\n"
            "func main() { let values = [1, 2] print(len(observe(values))) }"
        )
        self.assertEqual(llvm_ir.count('call {i64*, i64} @"observe"'), 1)

    def test_runtime_bounds_guard_precedes_element_address_and_load(self):
        from compiler.compiler import compile_source
        from llvmlite import binding

        llvm_ir = compile_source(
            "func read_at(values, index) { values[index] }\n"
            "func main() { print(read_at([10, 20], 1)) }"
        )
        self.assertIn("icmp sge i64", llvm_ir)
        self.assertIn("icmp slt i64", llvm_ir)
        self.assertIn("and i1", llvm_ir)
        with binding.parse_assembly(llvm_ir) as module:
            function = module.get_function("read_at")
            blocks = {block.name: list(block.instructions) for block in function.blocks}
            self.assertEqual(blocks["entry"][-1].opcode, "br")
            self.assertEqual(blocks["bounds.fail"][-1].opcode, "unreachable")
            self.assertTrue(any("llvm.trap" in str(inst) for inst in blocks["bounds.fail"]))
            self.assertFalse(any(inst.opcode in ("load", "getelementptr") for inst in blocks["entry"]))
            self.assertFalse(any(inst.opcode in ("load", "getelementptr") for inst in blocks["bounds.fail"]))
            self.assertEqual(blocks["bounds.ok"][0].opcode, "getelementptr")
            self.assertEqual(blocks["bounds.ok"][1].opcode, "load")

    def test_empty_negative_and_upper_bound_accesses_generate_guards(self):
        from compiler.compiler import compile_source

        for values, index in (("[]", "0"), ("[1]", "0 - 1"), ("[1]", "len(values)")):
            with self.subTest(values=values, index=index):
                llvm_ir = compile_source(
                    "func main() { let values = " + values + " let index = " + index + " print(values[index]) }"
                )
                self.assertIn("bounds.fail", llvm_ir)
                self.assertIn('call void @"llvm.trap"()', llvm_ir)
                self.assertIn("unreachable", llvm_ir)

    def test_bounds_blocks_work_inside_loops_and_value_branches(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func pick(values, index) { if index > 0 { values[index] } else { values[0] } }\n"
            "func main() { let values = [10, 20] mut index = 0\n"
            "  while index < len(values) { print(pick(values, index)) index = index + 1 }\n"
            "}"
        )
        self.assertIn("phi", llvm_ir)
        self.assertIn("bounds.ok", llvm_ir)
        self.assertIn("while.cond", llvm_ir)

    def test_array_literals_allocate_element_storage_on_the_heap(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func main() { let values = [1, 2, 3] print(values[0]) }"
        )
        self.assertIn('declare i64* @"malloc"(i64', llvm_ir)
        self.assertNotIn("alloca i64", llvm_ir)

    def test_returned_local_array_keeps_heap_storage(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func make() { [7, 8] }\n"
            "func main() { let values = make() print(values[0]) }"
        )
        self.assertEqual(llvm_ir.count('call i64* @"malloc"'), 1)
        self.assertIn('call {i64*, i64} @"make"', llvm_ir)

    def test_immutable_array_shadow_does_not_load_as_mutable_storage(self):
        from compiler.compiler import compile_source

        llvm_ir = compile_source(
            "func main() { mut values = [1, 2]\n"
            "  if 1 < 2 { let values = [3] print(len(values)) print(values[0]) }\n"
            "  print(len(values))\n"
            "}"
        )
        self.assertIn("extractvalue", llvm_ir)


if __name__ == "__main__":
    unittest.main()
