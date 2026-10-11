# Kix compiler tests

This directory is the home for Kix-only lexer, parser, semantic, CLI, and
end-to-end tests. Lexer token-stream goldens live in `lexer/`; parser fixtures
and structural AST assertions live in `parser/` and `run_parser.py`.

Run the implemented suite with:

```sh
sh scripts/build-kixc-stage0.sh
python3 tests/kix/run_lexer.py --compiler build/kixc-stage0
python3 tests/kix/run_parser.py --compiler build/kixc-stage0
```

Future semantic, CLI, and executable tests should follow the same convention:
fixtures under `tests/kix/<phase>/` and a small runner with structural
assertions rather than output-only smoke tests.
