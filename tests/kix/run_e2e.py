#!/usr/bin/env python3
"""Compile and execute the Kix backend's supported end-to-end slice."""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests" / "kix" / "e2e"


def invoke(compiler: Path, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(compiler), *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        raise AssertionError(f"{label} failed:\n{result.stderr}{result.stdout}")


def check_program(compiler: Path, temp: Path, name: str, expected: str) -> None:
    source = CASES / f"{name}.kix"
    executable = temp / name
    built = invoke(compiler, source, "-o", executable)
    require_success(built, f"compile {name}")
    ran = invoke(executable)
    require_success(ran, f"run {name}")
    if ran.stdout != expected:
        raise AssertionError(f"{name}: expected stdout {expected!r}, got {ran.stdout!r}")
    print(f"ok   {name}.kix -> executable -> expected stdout")


def check_emit_modes(compiler: Path, temp: Path) -> None:
    source = CASES / "hello.kix"
    for option, suffix, marker in (
        ("-ll", ".ll", "define i32 @main"),
        ("-S", ".s", "main:"),
        ("-obj", ".o", None),
    ):
        output = temp / f"hello{suffix}"
        result = invoke(compiler, source, option, "-o", output)
        require_success(result, f"emit {option}")
        if not output.is_file() or output.stat().st_size == 0:
            raise AssertionError(f"{option} did not create a non-empty {output}")
        if marker is not None and marker not in output.read_text(errors="replace"):
            raise AssertionError(f"{option} output is missing {marker!r}")
        print(f"ok   hello.kix {option}")


def check_default_output_preserves_source(compiler: Path, temp: Path) -> None:
    source = temp / "hello.kix"
    original = (CASES / "hello.kix").read_bytes()
    source.write_bytes(original)
    result = invoke(compiler, source)
    require_success(result, "default executable output")
    executable = source.with_suffix("")
    if source.read_bytes() != original:
        raise AssertionError("default output overwrote hello.kix")
    if not executable.is_file():
        raise AssertionError(f"default output did not create {executable}")
    ran = invoke(executable)
    require_success(ran, "run default output")
    if ran.stdout != "Hello, Kix!\n":
        raise AssertionError(f"default output produced unexpected stdout {ran.stdout!r}")
    print("ok   hello.kix default output is hello and preserves its source")


def check_lowering_rejection(compiler: Path) -> None:
    source = CASES / "unsupported_tuple.kix"
    result = invoke(compiler, source, "-ll", "-o", "/tmp/knv-should-not-exist.ll")
    diagnostic = result.stderr + result.stdout
    located = re.search(r"unsupported_tuple\.kix:\d+:\d+", diagnostic)
    spanned = re.search(r"\[bytes \d+\.\.\d+\]", diagnostic)
    if result.returncode == 0 or "E7001" not in diagnostic or not located or not spanned:
        raise AssertionError(f"invalid lowering rejection:\n{diagnostic}")
    print("ok   unsupported lowering -> E7001 with location and byte span")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", type=Path, default=ROOT / "build" / "kixc-stage0")
    args = parser.parse_args()
    compiler = args.compiler.resolve()
    try:
        with tempfile.TemporaryDirectory(prefix="kix-e2e-") as directory:
            temp = Path(directory)
            check_emit_modes(compiler, temp)
            check_default_output_preserves_source(compiler, temp)
            check_program(compiler, temp, "hello", "Hello, Kix!\n")
            check_program(compiler, temp, "fib", "102334155\n")
            check_program(compiler, temp, "control_data", "1\n5\n3\nok\n0\n1\n2\n")
            check_program(compiler, temp, "record", "3\n9\n")
        check_lowering_rejection(compiler)
    except AssertionError as error:
        print(f"FAIL {error}")
        return 1
    print("all Kix end-to-end tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
