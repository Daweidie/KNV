# Kix backend lowering map

Kix keeps its own parser and semantic pass, then lowers the checked
`KixProgram` into the established `AstProgram`.  The lowered program must still
pass `semantic_check_program_with_warnings` and its `type_result`: the Vix
semantic/type inference result is an input to desugaring, typed ownership
analysis, MIR lowering, and both existing backends.  This second check is also
the boundary that detects mistakes in the adapter; it does not replace Kix
semantic checking.

## Node map

| Kix node | Existing AST representation |
| --- | --- |
| `Function` | `AstFunction`; `text` is the name, `aux` is the return type, `names`/`types` are parameters, and the child is its body |
| `Block` | `AstStmt(block)` for statements; when used as a value, `AstExpr(block_expr)` carries the optional tail expression |
| `Let` | `AstStmt(let)`; only a `PathPattern` is representable in the first slice |
| `Return` | `AstStmt(return_expr)` |
| `ExprStmt` | `AstStmt(expr)`, except a call to the builtin `print`, which maps to `AstStmt(print)` |
| `IntLiteral`, `FloatLiteral`, `StringLiteral`, `RawStringLiteral`, `BoolLiteral` | `AstExpr(int/float/string/bool)` |
| `Path` | `AstExpr(ident)` |
| `Binary` | `AstExpr(binop)` |
| `Unary` | `AstExpr(unaryop)` (`*` later maps to `deref`) |
| `Call` | `AstExpr(call)` when the callee is a path, otherwise expression-call; statement-position `print` uses the print statement |
| `If` | `AstExpr(if_expr)` in value position or `AstStmt(if)` in statement position |
| `While` | `AstStmt(while)` |
| `For` + `Range` | `AstStmt(for_range)` |
| `Assign` | name, field, index, and dereference assignment statement variants |
| `Index`, `Slice`, `Field` | `AstExpr(index/slice/field)`; a field followed by a call becomes `method_call` |
| `ArrayLiteral` | `AstExpr(array_literal)` |
| `TupleLiteral` | no direct legacy node; lower only after choosing the backend tuple representation |
| `RecordLiteral`, record `TypeDecl` | `AstExpr(struct_literal)`, `AstStructDecl` |
| sum `TypeDecl`, `Variant*`, `Match*` | `AstAdtDecl`, constructor calls, and match expression/statement patterns |
| `Closure` | `AstExpr(lambda)` |
| `Borrow` | `AstExpr(borrow)` for a path; nested place operands need an AST extension before lowering |
| `GenericApply` | generic call type arguments; function declarations use `AstFunction.type_params` |
| `Propagate`, `Coalesce` | desugared Option/Result control flow |

Any checked node without a valid mapping is a lowering error in the new
`E7xxx` range, with filename and the Kix node's source location/span.  It must
never be silently discarded.

## Delivery plan

1. Add an arena-to-arena adapter for functions, parameters, block statements,
   returns, simple lets, scalar literals, operators, calls, and `print`.
2. Route Kix codegen modes through Kix parse/semantic, the adapter, then the
   unchanged Vix semantic/typeck/desugar/analysis/MIR/LLVM pipeline.
3. Establish executable hello and recursive fib tests, plus a stable unsupported
   lowering diagnostic.
4. Expand control flow and place/data lowering, then records/ADTs/match,
   generics/closures/borrows, and finally Option/Result desugaring.  Rebuild and
   run both Kix and Vix regressions after each slice.
