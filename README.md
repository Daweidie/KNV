# Kix Not Vix

Kix 是一门正在实现中的静态类型系统语言。项目目标是用少量、统一、可判定的规则，构建一门适合人类阅读、工具分析和长期演进的原生语言。

仓库代号 **KNV**，即 **Kix Not Vix**。Kix 借鉴 Vix 编译器的工程经验和 LLVM 后端，但拥有独立的词法、语法和 AST，不继承 Vix 的语言兼容限制。

## 当前状态

项目处于 Stage 0：编译器主体仍使用 Vix 编写，并由上一级目录的只读 `../Vix-lang` 作为启动编译器构建。

已经实现：

- Kix 独立 lexer，并保留 Vix 兼容模式；
- 嵌套块注释、文档注释、进制数字、指数浮点数、raw/byte string；
- 确定性的换行终止规则；
- Kix parser 和独立 arena AST；
- 函数、统一 `type` 声明、trait、impl、mod、use 和属性；
- 表达式块、无括号 `if`、`match`、循环、闭包和 `let-else`；
- 泛型调用、记录构造、索引、切片、范围、管道、`?` 和 `??`；
- 结构化模式以及文本、JSON AST 输出；
- 字段、索引和解引用 place 的 `&` / `&mut` 借用 AST。

仍在实现：

- Kix 名字解析、类型检查和 trait/impl 语义；
- match 穷尽性和借用检查；
- Kix AST 到现有 Vix/LLVM 后端的 lowering；
- `kixc build|run|check|ast` 的最终命令界面；
- 使用 Kix 源码完成固定点自举。

当前 `build/kixc-stage0 --check` 只做 Kix 词法和语法检查，尚不代表类型检查已经完成。

## 语法概览

```kix
type Shape =
    | Circle { radius: f64 }
    | Rect { width: f64, height: f64 }
    | Dot

trait Area {
    fn area(self): f64
}

impl Area for Shape {
    fn area(self): f64 = match self {
        Circle { radius } => 3.14159 * radius * radius
        Rect { width, height } => width * height
        Dot => 0.0
    }
}

fn id[T](value: T): T = value

fn fib(n: Int): Int {
    if n < 2 { return n }
    fib(n - 1) + fib(n - 2)
}

fn main(): Int {
    let shape = Circle { radius: 2.0 }
    let value = id[f64](shape.area())
    print(value)
    0
}
```

Kix 的主要规则：

- 返回类型使用 `:`，match 分支使用 `=>`，`->` 保留；
- `if`、`match` 和块都是表达式，块尾表达式就是块的值；
- 泛型写作 `id[T]` 和 `Box[T]`；
- 记录、别名和求和类型统一使用 `type`；
- 借用只使用 `&` 和 `&mut`；
- `print`、类型名以及 `and`/`or` 不是关键字；
- `Option`、`Result` 及其构造子是普通类型和普通构造子。

## 构建

系统需要 LLVM、Clang、LLD 和 Python 3。本机验证版本为 LLVM 23.1.1。

`../Vix-lang` 中的预编译程序依赖 LLVM 21/22。构建脚本只读取它的 seed IR 和支持源码，在 KNV 的 `build/` 内重新链接，不会修改 `Vix-lang`。

```sh
sh scripts/build-vixc-host.sh
./build/vixc-host --version

sh scripts/build-kixc-stage0.sh
./build/kixc-stage0 --version
```

默认位置可以通过环境变量覆盖：

```sh
VIX_HOME=/path/to/Vix-lang sh scripts/build-vixc-host.sh
```

## 使用

```sh
# 自动根据 .kix 扩展名选择 Kix
./build/kixc-stage0 --lex program.kix
./build/kixc-stage0 --check program.kix
./build/kixc-stage0 --ast program.kix
./build/kixc-stage0 --ast-json program.kix

# 也可以显式选择语言
./build/kixc-stage0 --lang=kix --check program.kix
./build/kixc-stage0 --lang=vix --check program.vix
```

Kix 语义分析和代码生成尚未接通，因此目前不能把 `.kix` 编译为可执行文件。Vix 模式仍可使用既有后端。

## 测试

```sh
python3 tests/kix/run_lexer.py --compiler build/kixc-stage0
python3 tests/kix/run_parser.py --compiler build/kixc-stage0

# Vix 兼容回归
python3 tests/syntax_tests.py build/kixc-stage0
```

解析器测试覆盖主要语法、结构化模式、错误诊断和复合 place 借用。借用用例确认以下结构不会退化为单一变量名：

```kix
let field = &point.x
let item = &mut items[0]
let target = &*pointer
```

## 目录

```text
src/                  Stage 0 编译器源码
src/kix_ast.vix       Kix AST
src/kix_parser.vix    Kix parser
tests/kix/            Kix lexer/parser 回归测试
scripts/              LLVM 23 host 与 kixc-stage0 构建脚本
seed/                 KNV 内保留的只读 Vix seed
```

所有 Kix 实现改动和构建产物都留在 KNV。`../Vix-lang` 只承担只读启动编译器职责。

## 路线

1. 完成名字解析、类型系统、模式绑定和诊断。
2. 完成 `Option`/`Result`、`?`、`??`、trait/impl 和 match 穷尽性。
3. 将 Kix AST lowering 到现有中间表示，复用 LLVM 后端。
4. 打通 hello、fib、ADT/match、泛型、循环和错误传播程序。
5. 用 Kix 重写编译器并完成固定点自举。

功能只有在对应测试通过后才视为已经实现。
