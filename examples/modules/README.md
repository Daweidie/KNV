# Kix Module System Examples

This directory demonstrates the multi-file module system in Kix.

## Overview

The Kix module system allows you to organize code across multiple files:
- **Module declaration**: `mod module_name` or `pub mod module_name`
- **Use statement**: `use module::function` (Kix `use` takes a path; there is no `as` alias)
- **Qualified calls**: `module::function()` for functions from modules

## File Resolution

When you declare `mod math`, the compiler looks for:
1. `math.kix` in the same directory
2. `math/mod.kix` as a subdirectory module

## Examples

### 1. Basic Module (`basic_example.kix`)
Simple two-file program with a math module (`math.kix`).

```bash
# Parse the Kix source
./build/kixc-stage0 --lang=kix --ast-json examples/modules/basic_example.kix
```

### 2. Multiple Modules (`multi_module.kix`)
Demonstrates using several modules at once, including a module that defines a record type (`counter.kix`).

### 3. Module with Records (`counter.kix`)
Shows how to define and use record types across modules.

### 4. Nested Modules (`nested_module.kix` + `utils/mod.kix`)
Shows a directory module entry (`utils/mod.kix`) exposing a child module (`utils/string_helpers.kix`).

## Compilation

Kix code generation is not wired up yet, so use the front end:

```bash
# Parse a program
./build/kixc-stage0 --lang=kix --ast-json your_file.kix

# Semantic check (optional)
./build/kixc-stage0 --lang=kix --check your_file.kix
```

## Known Limitations

- Kix code generation is not connected yet, so `.kix` files cannot be built into executables.
- `use` accepts a path only; `import ... as` aliases are not part of Kix.

## Syntax Reference

### Module Declaration
```kix
// In main.kix
mod math              // Private module (not re-exported)
pub mod utilities     // Public module (can be re-exported)

fn main(): Int {
    return 0
}
```

### Module File (math.kix)
```kix
// All top-level functions are public by default
pub fn add(a: Int, b: Int): Int {
    return a + b
}

pub fn multiply(x: Int, y: Int): Int {
    return x * y
}
```

### Use and Usage
```kix
mod math

use math::add
use math::multiply

fn main(): Int {
    let sum = math::add(3, 4)       // Qualified call
    let product = math::multiply(2, 5)
    return sum + product            // Returns 17
}
```

### Nested Modules (utils/mod.kix)
```kix
mod utils

use utils::string_helpers

fn main(): Int {
    return utils::string_helpers::length("hello")
}
```
