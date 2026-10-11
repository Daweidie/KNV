#!/usr/bin/env python3
"""Structural parser regression tests for the seed-built Kix front end."""

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests" / "kix" / "parser"


def run(compiler: Path, source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(compiler), "--lang=kix", "--ast-json", str(source)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def require_kinds(ast, expected):
    kinds = {node.get("kind") for node in walk(ast)}
    missing = sorted(set(expected) - kinds)
    if missing:
        raise AssertionError(f"missing AST kinds: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", type=Path, default=ROOT / "build" / "kixc-stage0")
    args = parser.parse_args()
    compiler = args.compiler.resolve()

    core = run(compiler, CASES / "syntax_core.kix")
    if core.returncode != 0:
        raise AssertionError(core.stderr or core.stdout)
    ast = json.loads(core.stdout)
    require_kinds(
        ast,
        {
            "Attribute", "ModuleDoc", "TypeDecl", "Variant", "TraitDecl",
            "ImplDecl", "ModDecl", "UseDecl", "Function", "GenericApply", "Call", "Closure",
            "Let", "For", "While", "Match", "MatchArm", "OrPattern",
            "VariantPattern", "TuplePattern", "RecordPattern", "SlicePattern",
            "RangePattern", "WildcardPattern", "FieldPattern", "Slice", "Pipe",
            "Propagate", "Coalesce",
        },
    )
    print("ok   syntax_core.kix")

    docs = run(compiler, CASES / "docs_complete.kix")
    if docs.returncode != 0:
        raise AssertionError(docs.stderr or docs.stdout)
    docs_ast = json.loads(docs.stdout)
    require_kinds(docs_ast, {"TypeDecl", "TraitDecl", "ImplDecl", "If", "RecordLiteral", "GenericApply"})
    print("ok   docs_complete.kix")

    borrow = run(compiler, CASES / "borrow_places.kix")
    if borrow.returncode != 0:
        raise AssertionError(borrow.stderr or borrow.stdout)
    borrow_ast = json.loads(borrow.stdout)
    borrows = [node for node in walk(borrow_ast) if node.get("kind") == "Borrow"]
    operands = [node["children"][0]["kind"] for node in borrows]
    if operands != ["Field", "Index", "Unary"]:
        raise AssertionError(f"borrow operands lost their place expressions: {operands}")
    if [node.get("text") for node in borrows] != ["&", "&mut", "&"]:
        raise AssertionError("borrow mutability was not retained")
    print("ok   borrow_places.kix")

    text_ast = subprocess.run(
        [str(compiler), "--lang=kix", "--ast", str(CASES / "borrow_places.kix")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if text_ast.returncode != 0 or not text_ast.stdout.startswith("Program\n") or "Borrow &mut" not in text_ast.stdout:
        raise AssertionError("text AST mode did not emit the expected tree")
    print("ok   text AST mode")

    bad = run(compiler, CASES / "error_missing_arm.kix")
    diagnostic = bad.stderr + bad.stdout
    if bad.returncode == 0 or "E1100 Kix parse error" not in diagnostic or ":" not in diagnostic:
        raise AssertionError(f"missing structured parse failure: {diagnostic}")
    print("ok   error_missing_arm.kix")
    print("all Kix parser tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
