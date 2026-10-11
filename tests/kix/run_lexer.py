#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Kix lexer golden tests")
    parser.add_argument("--compiler", type=Path, default=Path("build/kixc-stage0"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    compiler = args.compiler if args.compiler.is_absolute() else root / args.compiler
    lexer_dir = Path(__file__).resolve().parent / "lexer"
    failed = 0

    for source in sorted(lexer_dir.glob("*.kix")):
        expected_path = source.with_suffix(".tokens")
        result = subprocess.run(
            [str(compiler), "--lang=kix", "--lex", str(source)],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        expected_status = 1 if source.stem == "unterminated" else 0
        expected = expected_path.read_text()
        if result.returncode != expected_status or result.stdout != expected or result.stderr:
            failed += 1
            print(f"FAIL {source.name}")
            print(f"  exit: expected {expected_status}, got {result.returncode}")
            if result.stdout != expected:
                print("  token stream differs from golden")
            if result.stderr:
                print(f"  stderr: {result.stderr!r}")
        else:
            print(f"ok   {source.name}")

    auto = subprocess.run(
        [str(compiler), "--lex", str(lexer_dir / "keywords.kix")],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if auto.returncode != 0 or auto.stdout != (lexer_dir / "keywords.tokens").read_text():
        failed += 1
        print("FAIL automatic .kix language selection")
    else:
        print("ok   automatic .kix language selection")

    guarded = subprocess.run(
        [str(compiler), "--lang=kix", str(lexer_dir / "keywords.kix")],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if guarded.returncode == 0 or "Kix semantic analysis and code generation are not implemented" not in guarded.stderr:
        failed += 1
        print("FAIL unimplemented-parser guard")
    else:
        print("ok   unimplemented-parser guard")

    if failed:
        print(f"{failed} Kix lexer test(s) failed")
        return 1
    print("all Kix lexer tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
