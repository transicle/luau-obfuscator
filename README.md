# luau-obfuscator
Basic Luau obfuscator and learning project for beginners exploring code obfuscation and script rewriting.

## Visual Obfuscation Process

1. Source

```lua
local name = "transicle"
local age = 17

if age == 17 and name == "transicle" then
    print("Hello, transicle! You are 17 years old.")
else
    print("Hello, stranger!")
end
```

2. Lexical Analysis for Tokenization

Reads source code, identifies keywords, symbols, etc., to produce a stream of tokens.

```
Token(KEYWORD, local)
Token(IDENTIFIER, name)
Token(SYMBOL, =)
Token(STRING, "transicle")
Token(KEYWORD, local)
Token(IDENTIFIER, age)
Token(SYMBOL, =)
Token(NUMBER, 17)
Token(KEYWORD, if)
Token(IDENTIFIER, age)
Token(SYMBOL, ==)
Token(NUMBER, 17)
Token(KEYWORD, and)
Token(IDENTIFIER, name)
Token(SYMBOL, ==)
Token(STRING, "transicle")
Token(KEYWORD, then)
Token(BUILTIN, print)
Token(SYMBOL, ()
Token(STRING, "Hello, transicle! You are 17 years old.")
Token(SYMBOL, ))
Token(KEYWORD, else)
Token(BUILTIN, print)
Token(SYMBOL, ()
Token(STRING, "Hello, stranger!")
Token(SYMBOL, ))
Token(KEYWORD, end)
```

3. Symbol Table Managing (Scopes)

We use symbol tables to efficiently track variables, their data, and their scope assigned to them. With a time complexity of O(n), we can safely handle variable data without loss.

Visual representation on scope tracking:

```
SymbolTable(scopes=3, unique_names=2)

Scope 1 (root)
  - age [local] refs=1
  - name [local] refs=1
  Scope 2 (depth=1)
    - <no local declarations>
  Scope 3 (depth=1)
    - <no local declarations>
```

4. Parsing (Rescursive Descent, Pratt)

Takes that stream of tokens generated from the source code and constructs an AST (**A**bstract **S**yntax **T**ree) based off Luau's grammar rules to allow for deep analysis without guessing how the output should be designed.

```
{'type': 'Block',
 'stmts': [{'type': 'LocalDecl',
            'names': ['name'],
            'exprs': [{'type': 'StringLit', 'value': '"transicle"'}]},
           {'type': 'LocalDecl', 'names': ['age'], 'exprs': [{'type': 'NumberLit', 'value': '17'}]},
           {'type': 'IfStmt',
            'clauses': [({'type': 'BinOp',
                          'op': 'and',
                          'left': {'type': 'BinOp',
                                   'op': '==',
                                   'left': {'type': 'Name', 'name': 'age'},
                                   'right': {'type': 'NumberLit', 'value': '17'}},
                          'right': {'type': 'BinOp',
                                    'op': '==',
                                    'left': {'type': 'Name', 'name': 'name'},
                                    'right': {'type': 'StringLit', 'value': '"transicle"'}}},
                         {'type': 'Block',
                          'stmts': [{'type': 'CallStmt',
                                     'call_expr': {'type': 'CallExpr',
                                                   'func': {'type': 'Name', 'name': 'print'},
                                                   'args': [{'type': 'StringLit',
                                                             'value': '"Hello, transicle! You are '
                                                                      '17 years old."'}]}}]})],
            'else_body': {'type': 'Block',
                          'stmts': [{'type': 'CallStmt',
                                     'call_expr': {'type': 'CallExpr',
                                                   'func': {'type': 'Name', 'name': 'print'},
                                                   'args': [{'type': 'StringLit',
                                                             'value': '"Hello, stranger!"'}]}}]}}]}
```

5. Code Generation

Taking the result of the AST, we're able to generate Luau output code that is obfuscated and still functional. This is done by traversing the AST and applying transformations to variable names, function names, etc., while ensuring the logic remains intact.

```lua
local function Ftl77Ft1JTjIfJf1FTl(tFFf1fFFfj117FT) local f1lIljIFFljIfII1IT1JlI={129,50,254,55,11,136,12} local tjFlFfIlj717J7={} for FFFltTT1Tf17tF1=1,#tFFf1fFFfj117FT do tjFlFfIlj717J7[FFFltTT1Tf17tF1]=string.char(string.byte(tFFf1fFFfj117FT,FFFltTT1Tf17tF1)~f1lIljIFFljIfII1IT1JlI[(FFFltTT1Tf17tF1-1)%#f1lIljIFFljIfII1IT1JlI+1]~((FFFltTT1Tf17tF1-1)%256)~((math.floor((FFFltTT1Tf17tF1-1)/256))%256)) end return table.concat(tjFlFfIlj717J7) end;local I777Tl7fFTl7tlIlFT=Ftl77Ft1JTjIfJf1FTl("\245\65\157\90\124\228\105\234\95");local FfTI1IjJlIIfTtTfFIITf=17;if FfTI1IjJlIIfTtTfFIITf==17 and I777Tl7fFTl7tlIlFT==Ftl77Ft1JTjIfJf1FTl("\245\65\157\90\124\228\105\234\95") then print(Ftl77Ft1JTjIfJf1FTl("\201\86\144\88\96\161\42\242\72\150\83\115\237\98\227\88\207\6\64\244\109\180\69\155\74\50\163\32\189\86\133\73\89\218\14\205\122\191\63")) else print(Ftl77Ft1JTjIfJf1FTl("\201\86\144\88\96\161\42\245\78\133\92\110\227\100\253\28")) end
```

