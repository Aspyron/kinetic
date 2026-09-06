"""Command-line interface for the Kinetic compiler.

We use this wrapper to take our generated LLVM IR, pass it off to Clang,
and compile it down to a real executable. It saves developers from having 
to memorize Clang compiler flags.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from kinetic.compiler import compile_source
from kinetic.errors import KineticError


def build_command(source_path: Path) -> Path:
    """Compiles the .kn file down to a native executable using LLVM and Clang."""
    # 1. Read our source code
    source_text = source_path.read_text(encoding="utf-8")
    
    # 2. Compile to textual LLVM IR
    llvm_ir = compile_source(source_text)
    
    # 3. Save the IR temporarily so Clang can read it.
    # We just swap out the .kn extension for .ll.
    ll_file = source_path.with_suffix(".ll")
    ll_file.write_text(llvm_ir, encoding="utf-8")
    
    # 4. Figure out the final binary name (Windows needs that sweet .exe extension).
    app_name = source_path.with_suffix(".exe" if sys.platform == "win32" else "")
    
    print(f"Building {app_name}...")
    
    # 5. Hand it off to Clang to do the heavy lifting of machine code generation.
    try:
        # Check=True will raise an exception if Clang fails.
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
    
    # Set up our subcommands (build and run)
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    build_parser = subparsers.add_parser("build", help="Compile a .kn file to a binary executable")
    build_parser.add_argument("source", type=Path, help="The Kinetic source file to build")
    
    run_parser = subparsers.add_parser("run", help="Compile and immediately run a .kn file")
    run_parser.add_argument("source", type=Path, help="The Kinetic source file to run")
    
    args = parser.parse_args()
    
    try:
        # We always have to build the executable first, even if they just want to run it.
        app_name = build_command(args.source)
        
        if args.command == "run":
            print(f"Running {app_name.name}...\n{'-'*30}")
            subprocess.run([str(app_name.resolve())])
            
    except (OSError, KineticError, RuntimeError) as error:
        print(f"kinetic: error: {error}", file=sys.stderr)
        return 1
        
    return 0
