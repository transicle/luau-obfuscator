from rename  import rename_vars
from encrypt import encrypt_strings
from builtin_table import obfuscate_builtins
from dead_code import inject_dead_code
from control_flow import flatten_control_flow
from opaque import inject_opaque_predicates
from substitute import encode_numeric_literals
from expand_expr import expand_expressions
from tamper import wrap_with_tamper_guard

__all__ = [
	"rename_vars",
	"encrypt_strings",
	"obfuscate_builtins",
	"inject_dead_code",
	"flatten_control_flow",
	"inject_opaque_predicates",
	"encode_numeric_literals",
	"expand_expressions",
	"wrap_with_tamper_guard",
]
