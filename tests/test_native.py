import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLANG = shutil.which("clang")
RUN_NATIVE = os.environ.get("KINETIC_NATIVE_TESTS") == "1"

EXPECTED = {
    "01_hello.kn": "Hello World!",
    "02_logic.kn": "We hit the lucky number 3!",
    "03_arrays.kn": "Math and arrays work perfectly!",
}


@unittest.skipUnless(CLANG, "clang is not installed")
@unittest.skipUnless(RUN_NATIVE, "set KINETIC_NATIVE_TESTS=1 to run native builds")
class NativeExampleTests(unittest.TestCase):
    def test_examples_build_and_run(self):
        from compiler.compiler import compile_source

        for name, expected_output in EXPECTED.items():
            with self.subTest(example=name):
                source = Path("examples") / name
                with tempfile.TemporaryDirectory() as directory:
                    work = Path(directory) / name
                    work.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
                    llvm_ir = compile_source(work.read_text(encoding="utf-8"))
                    ll_file = work.with_suffix(".ll")
                    ll_file.write_text(llvm_ir, encoding="utf-8")
                    binary = work.with_suffix(
                        ".exe" if sys.platform == "win32" else ""
                    )
                    subprocess.run(
                        ["clang", str(ll_file), "-o", str(binary)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    result = subprocess.run(
                        [str(binary)], capture_output=True, text=True, check=True
                    )
                    self.assertIn(expected_output, result.stdout)


if __name__ == "__main__":
    unittest.main()
