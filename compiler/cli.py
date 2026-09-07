import argparse
import subprocess
import sys
from pathlib import Path

from .compiler import compile_source
from .errors import KineticError


def build_command(source_path: Path) -> Path:
    source_text = source_path.read_text(encoding="utf-8")

    llvm_ir = compile_source(source_text)

    ll_file = source_path.with_suffix(".ll")
    ll_file.write_text(llvm_ir, encoding="utf-8")

    app_name = source_path.with_suffix(".exe" if sys.platform == "win32" else "")

    print(f"Building {app_name}...")

    try:
        subprocess.run(["clang", str(ll_file), "-o", str(app_name)], check=True)
    except FileNotFoundError:
        print("Whoops! We couldn't find 'clang'. Make sure it's installed and in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Clang hit an error while building the binary.")
        sys.exit(1)

    print("Build successful!")
    return app_name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kinetic Compiler CLI - A systems-level programming language designed for humans."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Compile a .kn file to a binary executable")
    build_parser.add_argument("source", type=Path, help="The Kinetic source file to build")

    run_parser = subparsers.add_parser("run", help="Compile and immediately run a .kn file")
    run_parser.add_argument("source", type=Path, help="The Kinetic source file to run")

    args = parser.parse_args()

    try:
        app_name = build_command(args.source)

        if args.command == "run":
            print(f"Running {app_name.name}...\n{'-'*30}")
            subprocess.run([str(app_name.resolve())])

    except (OSError, KineticError, RuntimeError) as error:
        print(f"kinetic: error: {error}", file=sys.stderr)
        return 1

    return 0
