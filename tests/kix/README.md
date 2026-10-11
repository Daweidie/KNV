# Kix compiler tests

This directory is the home for Kix-only lexer, parser, semantic, CLI, and
end-to-end tests. Lexer token-stream goldens live in `lexer/`; parser fixtures
and structural AST assertions live in `parser/` and `run_parser.py`; semantic
accept/reject fixtures and stable diagnostic assertions live in `semantic/`
and `run_semantic.py`.

Run the implemented suite with:

```sh
sh scripts/build-kixc-stage0.sh
python3 tests/kix/run_lexer.py --compiler build/kixc-stage0
python3 tests/kix/run_parser.py --compiler build/kixc-stage0
python3 tests/kix/run_semantic.py --compiler build/kixc-stage0
python3 tests/kix/run_e2e.py --compiler build/kixc-stage0
```

Semantic `accept/*.kix` cases must pass `--check` with exit code 0. Each
`reject/<name>.kix` case must fail with a non-zero exit code and report the
stable `E6xxx` code stored in the sibling `reject/<name>.code` file together
with a `file:line:column` location.

End-to-end fixtures live under `e2e/`. The runner checks LLVM IR, assembly and
object emission, executes hello and fib binaries with exact stdout assertions,
and verifies unsupported lowering fails with a located `E7xxx` diagnostic.
