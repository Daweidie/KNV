<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/README/1807057DDfsRhTXUKh7Gk5.png">
    <source media="(prefers-color-scheme: light)" srcset="images/README/1807057DDfsRhTXUKh7Gk5.png">
    <img
      alt="Kix Programming Language"
      src="images/README/1807057DDfsRhTXUKh7Gk5.png"
      width="50%">
  </picture>

[示例](examples/) | [构建](#构建) | [使用](#使用) | [测试](#测试) | [路线](#路线)
</div>

本仓库是 **Kix**（仓库代号 **KNV**，即 **Kix Not Vix**）的主源码仓库，包含编译器、运行时相关组件、示例和文档。Kix 借鉴 Vix 的经验与 LLVM 后端，但拥有独立的词法、语法和 AST。

> 🚧 **Stage 0**：编译器主体仍使用 Vix 编写，由上一级目录的只读 `../Vix-lang` 启动构建。Kix 前端（lexer、parser、语义）已实现，代码生成尚未接通。

## 为什么是 Kix？

- **静态类型：** 名字解析与类型检查在编译期完成，尽早暴露错误。
- **规则统一：** `type` 统一记录、别名与求和类型；`if`、`match` 和块都是表达式。
- **工具友好：** 确定性的换行规则、结构化模式和稳定且带位置的错误码。
- **复用后端：** 沿用既有 Vix lowering、MIR、LLVM 与 runtime，不重写后端。

## Hello world

```kix
fn main(): Int
{
    print("Hello, Kix!")
    0
}
```

## 构建

系统需要 LLVM、Clang、LLD 和 Python 3（本机验证 LLVM 23.1.1）。构建脚本只读取 `../Vix-lang` 的 seed IR，在 KNV 的 `build/` 内重新链接，不会修改 `Vix-lang`。

```sh
sh scripts/build-vixc-host.sh
./build/vixc-host --version

sh scripts/build-kixc-stage0.sh
./build/kixc-stage0 --version
```

## 使用

```sh
./build/kixc-stage0 --check program.kix      # 名字解析 + 类型检查
./build/kixc-stage0 --ast program.kix
./build/kixc-stage0 --ast-json program.kix
```

Kix 语义错误使用独立的 `E6xxx` 码，词法/语法错误仍是 `E1100`。Kix 代码生成尚未接通，暂不能编译为可执行文件；Vix 模式仍可使用既有后端。

## 测试

```sh
python3 tests/kix/run_lexer.py --compiler build/kixc-stage0
python3 tests/kix/run_parser.py --compiler build/kixc-stage0
python3 tests/kix/run_semantic.py --compiler build/kixc-stage0
python3 tests/syntax_tests.py build/kixc-stage0   # Vix 兼容回归
```

`examples/` 中的示例全部使用 Kix 编写，并以 `--ast-json` 解析通过。

## 路线

1. 名字解析、类型系统、模式绑定和诊断。（已完成首版）
2. `Option`/`Result`、`?`、`??`、trait/impl 与 match 穷尽性。（已完成首版）
3. 将 Kix AST lowering 到现有中间表示，复用 LLVM 后端。
4. 打通 hello、fib、ADT/match、泛型、循环和错误传播程序。
5. 用 Kix 重写编译器并完成固定点自举。

功能只有在对应测试通过后才视为已经实现。

## 许可

本仓库是 Vix-lang 的衍生实验分支，许可沿用上游 Vix 的 Apache License 2.0（本分支暂无 `LICENSE` 文件）。
