<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/README/1807057DDfsRhTXUKh7Gk5.png">
    <source media="(prefers-color-scheme: light)" srcset="images/README/1807057DDfsRhTXUKh7Gk5.png">
    <img
      alt="Kix Programming Language"
      src="images/README/1807057DDfsRhTXUKh7Gk5.png"
      width="50%">
  </picture>

[当前状态](#当前状态) | [语法速览](#语法速览) | [构建](#构建) | [使用](#使用) | [测试](#测试) | [示例](#示例) | [路线](#路线)
</div>

本仓库是 **Kix** 语言（仓库代号 **KNV**，即 **Kix Not Vix**）的主源码仓库，包含编译器、运行时相关组件、示例和语言文档。

Kix 的目标是用少量、统一、可判定的规则，构建一门适合人类阅读、工具分析和长期演进的原生语言。它借鉴 Vix 编译器的工程经验和 LLVM 后端，但拥有独立的词法、语法和 AST，不继承 Vix 的语言兼容限制。

> 🚧 当前处于 **Stage 0 启动阶段**。编译器主体仍使用 Vix 编写，并由上一级目录的只读 `../Vix-lang` 作为启动编译器构建。Kix 的 lexer、parser 与语义分析已经实现，代码生成尚未接通。

## 为什么是 Kix？

- **静态类型：** 名字解析与类型检查在编译期完成，尽早暴露错误。
- **少而统一的规则：** `type` 统一记录、别名与求和类型；`if`、`match` 和块都是表达式，块尾表达式即块的值。
- **对人类和工具友好：** 确定性的换行终止规则、结构化模式，以及稳定且带位置的错误码。
- **复用成熟后端：** 沿用既有 Vix lowering、MIR、LLVM 与 runtime，而不重写后端。

## Hello world

```kix
fn main(): Int
{
    print("Hello, Kix!")
    0
}
```

## 当前状态

已经实现：

- 独立 Kix lexer，并保留 Vix 兼容模式；
- 嵌套块注释、文档注释、进制数字、指数浮点数、raw/byte string；
- 确定性的换行终止规则；
- Kix parser 和独立 arena AST；
- 函数、统一 `type` 声明、trait、impl、mod、use 和属性；
- 表达式块、无括号 `if`、`match`、循环、闭包和 `let-else`；
- 泛型调用、记录构造、索引、切片、范围、管道、`?` 和 `??`；
- 结构化模式以及文本、JSON AST 输出；
- 字段、索引和解引用 place 的 `&` / `&mut` 借用 AST；
- Kix 名字解析、作用域和符号表，覆盖函数、类型、参数、局部绑定和构造子；
- Kix 类型规范化与基础类型检查，包括字面量、调用、字段、索引、块、`if`、`match`、赋值、`return`、`break` 和闭包；
- 拒绝隐式数值转换，并验证合法的显式 `as`；
- 结构化模式绑定、重复绑定检查、or-pattern 一致性、match 分支类型统一与穷尽性诊断；
- `&`/`&mut` place 分类和最小可变性检查，拒绝右值借用；
- 首版 `Option`/`Result` 的 `?` 与 `??` 类型规则；
- 基础 trait/impl 方法查找。

仍在实现：

- 完整借用检查、生命周期和所有权分析；
- 泛型约束和 trait 约束的完整求解；
- Kix AST 到现有 Vix/LLVM 后端的 lowering；
- `kixc build|run|check|ast` 的最终命令界面；
- 使用 Kix 源码完成固定点自举。

## 语法速览

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

`--check` 会执行 Kix 名字解析和类型检查，并使用独立的 `E6xxx` 诊断码；词法/语法错误仍是 `E1100`。Kix 代码生成尚未接通，因此目前不能把 `.kix` 编译为可执行文件；Vix 模式仍可使用既有后端。

## 测试

```sh
python3 tests/kix/run_lexer.py --compiler build/kixc-stage0
python3 tests/kix/run_parser.py --compiler build/kixc-stage0
python3 tests/kix/run_semantic.py --compiler build/kixc-stage0

# Vix 兼容回归
python3 tests/syntax_tests.py build/kixc-stage0
```

语义测试位于 `tests/kix/semantic/`：`accept/` 用例必须以 0 退出；`reject/` 用例必须非零退出，并返回同名 `.code` 文件中记录的稳定 `E6xxx` 错误码和 `文件:行:列` 位置。

Kix 语义诊断使用独立的错误码范围：名字解析 `E61xx`、类型检查 `E62xx`、模式 `E63xx`、借用 place `E64xx`、`Option`/`Result` 传播 `E65xx`、赋值可变性 `E66xx`。

解析器回归还确认以下复合 place 借用不会退化为单一变量名：

```kix
let field = &point.x
let item = &mut items[0]
let target = &*pointer
```

## 示例

`examples/` 中的示例全部使用 Kix 编写：

| 示例 | 说明 |
| --- | --- |
| `examples/hello.kix`、`examples/fib.kix` | 入门与递归 |
| `examples/adt_pattern.kix`、`examples/match_3.kix` | 求和类型与模式匹配 |
| `examples/generics.kix`、`examples/result.kix`、`examples/option.kix` | 泛型与错误传播 |
| `examples/owner.kix`、`examples/pointer.kix`、`examples/swap.kix` | 引用、可变借用与所有权 |
| `examples/modules/` | 多文件模块系统 |
| `examples/ed/ed.kix`、`examples/coreutils/grep.kix`、`examples/brainfuck.kix` | 更大规模的程序 |

每个 `.kix` 示例都通过 Kix parser；可用 `./build/kixc-stage0 --lang=kix --ast-json <文件>` 查看其 AST。

## 目录

```text
src/                  Stage 0 编译器源码
src/kix_ast.vix       Kix AST
src/kix_parser.vix    Kix parser
src/kix_semantic.vix  Kix 名字解析与类型检查
tests/kix/            Kix lexer/parser/semantic 回归测试
examples/             Kix 示例程序
scripts/              LLVM 23 host 与 kixc-stage0 构建脚本
seed/                 KNV 内保留的只读 Vix seed
```

所有 Kix 实现改动和构建产物都留在 KNV。`../Vix-lang` 只承担只读启动编译器职责。

## 路线

1. 完成名字解析、类型系统、模式绑定和诊断。（已完成首版）
2. 完成 `Option`/`Result`、`?`、`??`、trait/impl 和 match 穷尽性。（已完成首版）
3. 将 Kix AST lowering 到现有中间表示，复用 LLVM 后端。
4. 打通 hello、fib、ADT/match、泛型、循环和错误传播程序。
5. 用 Kix 重写编译器并完成固定点自举。

功能只有在对应测试通过后才视为已经实现。

## 文档

- `examples/modules/README.md`：Kix 模块系统示例。
- 语言规范以本 README 与测试为准；规范缺失处采用最小且向后兼容的行为，不恢复整个 docs 目录。

## 参与贡献

欢迎围绕语言设计、bug 报告、测试、标准库和文档提出贡献。请先在本仓库的 issue 中讨论：

- GitHub Issues: <https://github.com/Daweidie/KNV/issues>

## 许可

本仓库是 Vix-lang 的衍生实验分支，许可沿用上游 Vix 的 Apache License 2.0。本启动分支当前尚未附 `LICENSE` 文件。

## 生态

| 项目 | 说明 | 状态 |
| --- | --- | --- |
| **Kix 编译器（KNV）** | Kix 前端与后端实现 | Stage 0 启动中 |
| **Vix（上游）** | 启动编译器与 LLVM 后端来源 | 只读依赖 |
| **Kix 示例** | `examples/` 中的 Kix 程序 | 持续补充 |
