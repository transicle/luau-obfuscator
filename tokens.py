VAR_DECLS  = ["local", "type", "export"]
SYMBOLS    = [
    "//=", "..=", "+=", "-=", "*=", "/=", "%=", "^=",
    "==", "~=", "<=", ">=", "->", "::", "..", "...", "//",
    "=", "+", "-", "*", "/", "%", "^", "#",
    "<", ">", "&", "|", "?",
    "(", ")", "{", "}", "[", "]",
    ".", ",", ";", ":", "@",
    "`",
]
TYPES      = [
    "string", "number", "boolean", "table", "function",
    "nil", "thread", "buffer", "userdata", "vector",
    "any", "never", "unknown",
    "i8", "i16", "i32", "i64",
    "u8", "u16", "u32", "u64",
    "f32", "f64",
]
KEYWORDS   = [
    "and", "break", "continue", "do", "else", "elseif", "end",
    "false", "for", "function", "if", "in", "local", "nil",
    "not", "or", "repeat", "return", "then", "true",
    "type", "typeof", "until", "while", "export",
]
BUILTINS   = [
    "print", "warn", "error", "assert", "pcall", "xpcall",
    "type", "typeof",
    "tostring", "tonumber",
    "rawget", "rawset", "rawequal", "rawlen",
    "select", "unpack", "table.unpack",
    "next", "pairs", "ipairs",
    "setmetatable", "getmetatable",
    "require", "loadstring", "dofile", "load",
    "collectgarbage",
    "newproxy",
    "math", "table", "string", "os", "io",
    "coroutine", "bit32", "utf8", "buffer",
    "_G", "_VERSION",
    "game", "workspace", "script", "plugin",
    "tick", "time", "os.clock",
    "task", "spawn", "delay", "wait",
    "shared",
]
TYPE_KEYWORDS = [
    "type", "typeof", "export",
    "keyof", "rawkeyof",
    "self",
]
ATTRIBUTES = [
    "@native", "@inline", "@noinline",
]

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
    
def make_token(type, value):
    return Token(type, value)