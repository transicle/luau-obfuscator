#!/bin/bash
set -e

cd "$(dirname "$0")/.."

python main.py >/dev/null

# chud autofill
python3 - <<'PYEOF'
import sys
sys.path.insert(0, ".")

from lexer import tokenize
from parser import parse, pretty_parse
from scope import analyse, format_symbol_table

with open("@template/input.lua", "r") as f:
    source = f.read()

tokens = tokenize(source)
tokens_text = "\n".join(str(t) for t in tokens)
ast = parse(tokens)
scope_text = format_symbol_table(analyse(ast))
pretty_ast = pretty_parse(ast)

readme = """\
# luau-obfuscator
A Luau obfuscator and learning project covering lexical analysis, AST construction, scope analysis, and a full suite of code-transformation passes including string encryption, variable renaming, control-flow flattening, opaque predicates, dead-code injection, numeric literal encoding, and bytecode wrapping.

## Visual Obfuscation Process

1. Source

```lua
{source}
```

2. Lexical Analysis for Tokenization

Reads source code, identifies keywords, symbols, etc., to produce a stream of tokens.

```
{tokens}
```

3. Symbol Table Managing (Scopes)

We use symbol tables to efficiently track variables, their data, and their scope assigned to them. With a time complexity of O(n), we can safely handle variable data without loss.

Visual representation on scope tracking:

```
{scope}
```

4. Parsing (Rescursive Descent, Pratt)

Takes that stream of tokens generated from the source code and constructs an AST (**A**bstract **S**yntax **T**ree) based off Luau's grammar rules to allow for deep analysis without guessing how the output should be designed.

```
{ast}
```

5. Code Generation

Taking the result of the AST, we're able to generate Luau output code that is obfuscated and still functional. This is done by traversing the AST and applying transformations to variable names, function names, etc., while ensuring the logic remains intact.

```lua
{output}
```

---

## Pipeline

`main.py` runs the full obfuscation pipeline in order:

```
Source Lua
    │
    ▼
[lexer]       tokenize()               — produces a flat Token list
    │
    ▼
[parser]      parse()                  — builds the AST
    │
    ▼
[encrypt]     encrypt_strings()        — XOR-encrypts string literals
    │
    ▼
[substitute]  encode_numeric_literals() — hides integer constants
    │
    ▼
[expand_expr] expand_expressions()     — rewrites numbers into complex algebra
    │
    ▼
[opaque]      inject_opaque_predicates() — adds unprovable boolean guards
    │
    ▼
[control_flow] flatten_control_flow()  — state-machine loop flattening
    │
    ▼
[rename]      rename_vars()            — renames all locals to lookalike names
    │
    ▼
[builtin_table] obfuscate_builtins()   — hoists builtins into hidden table
    │
    ▼
[dead_code]   inject_dead_code()       — injects unreachable entropy-guarded blocks
    │
    ▼
[constructor] Constructor(minify=True).generate() — serializes AST → Luau text
    │
    ▼
[bytecode]    wrap_bytecode()          — compiles to bytecode, XOR-encrypts, wraps in loader
    │
    ▼
Obfuscated Output
```

---

## Usage

Place your Luau source in `@template/input.lua`, then run:

```bash
python main.py
```

The obfuscated output is written to `@template/output.lua`. Requires `luau-compile` to be on your `PATH` for the bytecode-wrapping step.

---

## Module Reference

### `tokens.py`
Defines the vocabulary of the Luau language as static lists: symbols, keywords, type names, builtins, attributes, and variable declaration keywords. Also defines the `Token` dataclass and a `make_token` factory function used throughout the pipeline.

### `lexer.py`
Hand-written tokenizer (`tokenize`) that scans Luau source text character-by-character and produces a flat list of `Token` objects. Handles all Luau string forms (single/double-quoted, backtick interpolated, long-bracket `[[ ]]`), numeric literals (decimal, hex, binary, floats), comments, and all symbol sequences.

### `luau_ast.py`
Declares the full AST node class hierarchy for Luau as plain Python dataclasses. Covers every statement (`LocalDecl`, `Assign`, `IfStmt`, `WhileLoop`, `NumericFor`, `FuncDecl`, `ReturnStmt`, etc.) and every expression type (`BinOp`, `UnOp`, `CallExpr`, `MethodCallExpr`, `FieldExpr`, `IndexExpr`, `TableConstructor`, `StringLit`, `NumberLit`, `Name`, etc.).

### `parser.py`
Recursive-descent `Parser` class that consumes a `Token` list and builds the `luau_ast` node tree. Implements operator-precedence climbing for binary expressions using a `PRECEDENCE` table and handles all Luau statement and expression forms including type annotations, generics, and compound assignments.

### `scope.py`
Performs a scope-analysis pass over the AST via an `analyse` function, building a `SymbolTable` that maps every node and identifier to its lexical `Scope`. Tracks whether each `Symbol` is local, a parameter, or an upvalue, and records all reference sites for downstream renaming.

### `visitor.py`
Generic `Visitor` base class that traverses the AST in either pre-order or post-order. Dispatches to `visit_<NodeType>` methods (falling back to `generic_visit`) with explicit child-traversal logic for every node type, making it easy to implement analysis passes by subclassing.

### `util.py`
Single utility function `random_name` that generates visually confusing obfuscated identifiers of length 13–21 using only visually similar characters (`I`, `l`, `J`, `j`, `f`, `F`, `t`, `T`, `1`, `7`). Used by nearly every obfuscation pass.

### `rename.py`
Implements `rename_vars`, which uses `scope.analyse` to identify every locally declared symbol and replaces its name everywhere it appears in the AST with a fresh `random_name` lookalike. Correctly handles parameters, `for` loop variables, method declarations, and avoids renaming globals, builtins, or keywords.

### `encrypt.py`
Implements `encrypt_strings`, which XOR-encrypts every `StringLit` node using a per-file random key combined with a position-dependent byte mask (`key[i % n] ^ (i & 0xFF) ^ ((i >> 8) & 0xFF)`). Injects a Lua-side decoder function at the top of the AST and replaces each string literal with a call to that decoder.

### `builtin_table.py`
Implements `obfuscate_builtins`, which hoists all Luau built-in globals (`print`, `math`, `table`, `string`, `os`, etc.) into a single randomly named local table at script top, then rewrites every unresolved reference to a builtin into a field access on that table (e.g. `print(x)` → `_obf.field(x)`). Uses `scope.analyse` to avoid rewriting legitimately shadowed locals.

### `dead_code.py`
Implements `inject_dead_code`, which inserts syntactically valid but unreachable Lua blocks guarded by opaque-false predicates. The dead blocks use runtime entropy (`os.time`, `os.clock`, `DateTime.now`) combined with LCG-scrambled nonces and HMAC-like signature checks to make static analysis of their unreachability extremely difficult.

### `control_flow.py`
Implements `flatten_control_flow`, a control-flow-flattening pass that transforms sequential statement blocks into a `while true` dispatcher loop driven by a state integer variable. Each original statement becomes an `if state == N then ... state = N+1 end` branch, hiding the program's original linear control flow.

### `opaque.py`
Implements `inject_opaque_predicates`, which injects mathematically provable but statically opaque boolean expressions into `if`, `while`, and `repeat` condition expressions. Also randomly prepends dead `if`-clauses guarded by always-false predicates (e.g. `x - x == 1`) containing junk assignments.

### `substitute.py`
Implements `encode_numeric_literals`, which replaces integer literals in the AST with indirect calls to an injected decoder function: `n` becomes `decode(n + key, key)` where `key` is a random per-literal offset. This hides numeric constants from straightforward static analysis.

### `expand_expr.py`
Implements `expand_expressions`, which rewrites `NumberLit` nodes into algebraically equivalent but more complex expressions (e.g. `n` → `((n + delta) + delta) - (delta * 2)`) and probabilistically appends `+ (z - z)` zero-terms to binary arithmetic expressions to further obscure numeric intent.

### `bytecode.py`
Compiles obfuscated Luau source to raw bytecode via an external `luau-compile` binary (invoked via `subprocess`), then XOR-encrypts the bytecode with a random key and emits a self-contained Lua wrapper that decrypts and `loadstring`-executes it at runtime. The result is a script whose logic is entirely opaque without the key.

### `tamper.py`
Implements `wrap_with_tamper_guard`. Compiles the payload to a custom VM bytecode format with randomized opcodes, state-machine checksums, and a 4-byte cookie header, then XOR-encrypts the VM blob and emits a Lua wrapper that verifies FNV-1a and DJB2 integrity hashes of both the key and ciphertext before executing.

### `obfuscate.py`
Thin re-export module that exposes all obfuscation pass functions (`rename_vars`, `encrypt_strings`, `obfuscate_builtins`, `inject_dead_code`, `flatten_control_flow`, `inject_opaque_predicates`, `encode_numeric_literals`, `expand_expressions`, `wrap_with_tamper_guard`) from a single namespace.

### `constructor.py`
The code-generation back-end. The `Constructor` class walks the AST and serializes it back to Luau source text. Supports both pretty-printed (indented) and minified output modes, and handles operator-precedence-aware parenthesization for all binary and unary expressions.

---

## Project Structure

```
luau-obfuscator/
├── main.py            # Entry point — runs the full pipeline
├── tokens.py          # Token types, keyword/symbol/builtin lists
├── lexer.py           # Tokenizer (source → Token list)
├── luau_ast.py        # AST node dataclasses
├── parser.py          # Parser (Token list → AST)
├── scope.py           # Scope/symbol-table analysis
├── visitor.py         # Generic AST visitor base class
├── util.py            # random_name() identifier generator
├── constructor.py     # Code generator (AST → Luau source)
├── rename.py          # Pass: variable renaming
├── encrypt.py         # Pass: string encryption
├── builtin_table.py   # Pass: builtin hoisting
├── dead_code.py       # Pass: dead-code injection
├── control_flow.py    # Pass: control-flow flattening
├── opaque.py          # Pass: opaque predicates
├── substitute.py      # Pass: numeric literal encoding
├── expand_expr.py     # Pass: expression expansion
├── bytecode.py        # Pass: bytecode compilation + XOR wrapping
├── tamper.py          # Pass: tamper-guard VM wrapping
├── obfuscate.py       # Re-exports all pass functions
└── @template/
    ├── input.lua      # Place your source here
    └── output.lua     # Obfuscated output written here
```
""".format(
    source=source.rstrip(),
    tokens=tokens_text,
    scope=scope_text.rstrip(),
    ast=pretty_ast.rstrip(),
    output=open("@template/output.lua", "r").read().rstrip()
)

with open("README.md", "w") as f:
    f.write(readme)

print("README.md updated.")
PYEOF

