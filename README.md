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

3. Parsing (Rescursive Descent, Pratt)

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
