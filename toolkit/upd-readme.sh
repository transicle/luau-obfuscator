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

with open("@template/output.lua", "r") as f:
    pretty_ast = f.read()

readme = """\
# luau-obfuscator
Basic Luau obfuscator and learning project for beginners exploring code obfuscation and script rewriting.

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
""".format(
    source=source.rstrip(),
    tokens=tokens_text,
    scope=scope_text.rstrip(),
    ast=pretty_ast.rstrip(),
)

with open("README.md", "w") as f:
    f.write(readme)

print("README.md updated.")
PYEOF

