VAR_DECLS = ["local", "_G", "getgenv()", "shared"]
SYMBOLS   = ["=", "+", "-", "*", "/", "%", "(", ")", "{", "}", "[", "]", ".", ",", ";"]

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
    
def make_token(type, value):
    return Token(type, value)