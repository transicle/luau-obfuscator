from rename  import rename_vars
from encrypt import encrypt_strings
from builtin_table import obfuscate_builtins
from dead_code import inject_dead_code

__all__ = ["rename_vars", "encrypt_strings", "obfuscate_builtins", "inject_dead_code"]
