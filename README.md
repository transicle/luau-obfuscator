# luau-obfuscator
Basic Luau obfuscator and learning project for beginners exploring code obfuscation and script rewriting.

## Visual Obfuscation Process

1. Source

```lua
local Players = game:GetService("Players")

local localPlayer = Players.LocalPlayer
local character = localPlayer.Character or localPlayer.CharacterAdded:Wait()
local humanoid = character:FindFirstChild("Humanoid")

desiredSpeed = 64
local function applyWalkspeed(newCharacter)
    local humanoid = newCharacter:FindFirstChild("Humanoid")

    humanoid.WalkSpeed = desiredSpeed
end

humanoid.WalkSpeed = desiredSpeed

localPlayer.CharacterAdded:Connect(applyWalkspeed)
```

2. Lexical Analysis for Tokenization

Reads source code, identifies keywords, symbols, etc., to produce a stream of tokens.

```
Token(KEYWORD, local)
Token(IDENTIFIER, Players)
Token(SYMBOL, =)
Token(BUILTIN, game)
Token(SYMBOL, :)
Token(IDENTIFIER, GetService)
Token(SYMBOL, ()
Token(STRING, "Players")
Token(SYMBOL, ))
Token(KEYWORD, local)
Token(IDENTIFIER, localPlayer)
Token(SYMBOL, =)
Token(IDENTIFIER, Players)
Token(SYMBOL, .)
Token(IDENTIFIER, LocalPlayer)
Token(KEYWORD, local)
Token(IDENTIFIER, character)
Token(SYMBOL, =)
Token(IDENTIFIER, localPlayer)
Token(SYMBOL, .)
Token(IDENTIFIER, Character)
Token(KEYWORD, or)
Token(IDENTIFIER, localPlayer)
Token(SYMBOL, .)
Token(IDENTIFIER, CharacterAdded)
Token(SYMBOL, :)
Token(IDENTIFIER, Wait)
Token(SYMBOL, ()
Token(SYMBOL, ))
Token(KEYWORD, local)
Token(IDENTIFIER, humanoid)
Token(SYMBOL, =)
Token(IDENTIFIER, character)
Token(SYMBOL, :)
Token(IDENTIFIER, FindFirstChild)
Token(SYMBOL, ()
Token(STRING, "Humanoid")
Token(SYMBOL, ))
Token(IDENTIFIER, desiredSpeed)
Token(SYMBOL, =)
Token(NUMBER, 64)
Token(KEYWORD, local)
Token(KEYWORD, function)
Token(IDENTIFIER, applyWalkspeed)
Token(SYMBOL, ()
Token(IDENTIFIER, newCharacter)
Token(SYMBOL, ))
Token(KEYWORD, local)
Token(IDENTIFIER, humanoid)
Token(SYMBOL, =)
Token(IDENTIFIER, newCharacter)
Token(SYMBOL, :)
Token(IDENTIFIER, FindFirstChild)
Token(SYMBOL, ()
Token(STRING, "Humanoid")
Token(SYMBOL, ))
Token(IDENTIFIER, humanoid)
Token(SYMBOL, .)
Token(IDENTIFIER, WalkSpeed)
Token(SYMBOL, =)
Token(IDENTIFIER, desiredSpeed)
Token(KEYWORD, end)
Token(IDENTIFIER, humanoid)
Token(SYMBOL, .)
Token(IDENTIFIER, WalkSpeed)
Token(SYMBOL, =)
Token(IDENTIFIER, desiredSpeed)
Token(IDENTIFIER, localPlayer)
Token(SYMBOL, .)
Token(IDENTIFIER, CharacterAdded)
Token(SYMBOL, :)
Token(IDENTIFIER, Connect)
Token(SYMBOL, ()
Token(IDENTIFIER, applyWalkspeed)
Token(SYMBOL, ))
```

3. Symbol Table Managing (Scopes)

We use symbol tables to efficiently track variables, their data, and their scope assigned to them. With a time complexity of O(n), we can safely handle variable data without loss.

Visual representation on scope tracking:

```
SymbolTable(scopes=2, unique_names=7)

Scope 1 (root)
  - Players [local] refs=1
  - applyWalkspeed [local] refs=1
  - character [local] refs=1
  - desiredSpeed [global | upval] refs=2
  - humanoid [local] refs=1
  - localPlayer [local] refs=3
  Scope 2 (depth=1)
    - humanoid [local] refs=1
    - newCharacter [local | param] refs=1
```

4. Parsing (Rescursive Descent, Pratt)

Takes that stream of tokens generated from the source code and constructs an AST (**A**bstract **S**yntax **T**ree) based off Luau's grammar rules to allow for deep analysis without guessing how the output should be designed.

```
{'type': 'Block',
 'stmts': [{'type': 'LocalDecl',
            'names': ['Players'],
            'exprs': [{'type': 'MethodCallExpr',
                       'obj': {'type': 'Name', 'name': 'game'},
                       'method': 'GetService',
                       'args': [{'type': 'StringLit', 'value': '"Players"'}]}]},
           {'type': 'LocalDecl',
            'names': ['localPlayer'],
            'exprs': [{'type': 'FieldExpr',
                       'obj': {'type': 'Name', 'name': 'Players'},
                       'field': 'LocalPlayer'}]},
           {'type': 'LocalDecl',
            'names': ['character'],
            'exprs': [{'type': 'BinOp',
                       'op': 'or',
                       'left': {'type': 'FieldExpr',
                                'obj': {'type': 'Name', 'name': 'localPlayer'},
                                'field': 'Character'},
                       'right': {'type': 'MethodCallExpr',
                                 'obj': {'type': 'FieldExpr',
                                         'obj': {'type': 'Name', 'name': 'localPlayer'},
                                         'field': 'CharacterAdded'},
                                 'method': 'Wait',
                                 'args': []}}]},
           {'type': 'LocalDecl',
            'names': ['humanoid'],
            'exprs': [{'type': 'MethodCallExpr',
                       'obj': {'type': 'Name', 'name': 'character'},
                       'method': 'FindFirstChild',
                       'args': [{'type': 'StringLit', 'value': '"Humanoid"'}]}]},
           {'type': 'Assign',
            'targets': [{'type': 'Name', 'name': 'desiredSpeed'}],
            'exprs': [{'type': 'NumberLit', 'value': '64'}]},
           {'type': 'FuncDecl',
            'name': 'applyWalkspeed',
            'params': ['newCharacter'],
            'body': {'type': 'Block',
                     'stmts': [{'type': 'LocalDecl',
                                'names': ['humanoid'],
                                'exprs': [{'type': 'MethodCallExpr',
                                           'obj': {'type': 'Name', 'name': 'newCharacter'},
                                           'method': 'FindFirstChild',
                                           'args': [{'type': 'StringLit',
                                                     'value': '"Humanoid"'}]}]},
                               {'type': 'Assign',
                                'targets': [{'type': 'FieldExpr',
                                             'obj': {'type': 'Name', 'name': 'humanoid'},
                                             'field': 'WalkSpeed'}],
                                'exprs': [{'type': 'Name', 'name': 'desiredSpeed'}]}]},
            'is_local': True,
            'is_method': False},
           {'type': 'Assign',
            'targets': [{'type': 'FieldExpr',
                         'obj': {'type': 'Name', 'name': 'humanoid'},
                         'field': 'WalkSpeed'}],
            'exprs': [{'type': 'Name', 'name': 'desiredSpeed'}]},
           {'type': 'CallStmt',
            'call_expr': {'type': 'MethodCallExpr',
                          'obj': {'type': 'FieldExpr',
                                  'obj': {'type': 'Name', 'name': 'localPlayer'},
                                  'field': 'CharacterAdded'},
                          'method': 'Connect',
                          'args': [{'type': 'Name', 'name': 'applyWalkspeed'}]}}]}
```

5. Code Generation

Taking the result of the AST, we're able to generate Luau output code that is obfuscated and still functional. This is done by traversing the AST and applying transformations to variable names, function names, etc., while ensuring the logic remains intact.

```
local F1JIlIfFITtltfjIt1FT = game:GetService("Players")
local jj7IfFTltlTJj1 = F1JIlIfFITtltfjIt1FT.LocalPlayer
local TJITFTtlJj1If7FIjFIlfF = jj7IfFTltlTJj1.Character or jj7IfFTltlTJj1.CharacterAdded:Wait()
local Tljtl17jTtFf1tt = TJITFTtlJj1If7FIjFIlfF:FindFirstChild("Humanoid")
lTTjlj17FIfjlT771J1F7F = 64
local function IIjTffl7l77IJ7lj1Ttt1f(lFjJjFjJlTFl1I7f1TJ)
    local j17FjlltTI1FlJl1FfF = lFjJjFjJlTFl1I7f1TJ:FindFirstChild("Humanoid")
    j17FjlltTI1FlJl1FfF.WalkSpeed = lTTjlj17FIfjlT771J1F7F
end
Tljtl17jTtFf1tt.WalkSpeed = lTTjlj17FIfjlT771J1F7F
jj7IfFTltlTJj1.CharacterAdded:Connect(IIjTffl7l77IJ7lj1Ttt1f)
```

