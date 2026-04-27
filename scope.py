from visitor  import Visitor
from luau_ast import *


class Symbol:
    def __init__(self, name, *, is_local=True, is_param=False, decl_node=None):
        self.name       = name
        self.is_local   = is_local
        self.is_param   = is_param
        self.is_upval   = False      # set True when referenced by child scope
        self.decl_node  = decl_node
        self.refs       = []         # Name nodes that read this symbol

    def __repr__(self):
        flags = []
        if self.is_local:  flags.append("local")
        if self.is_param:  flags.append("param")
        if self.is_upval:  flags.append("upval")
        tag = "|".join(flags) if flags else "global"
        return f"Symbol({self.name!r}, {tag}, refs={len(self.refs)})"


class Scope:
    _id_counter = 0

    def __init__(self, parent=None, node=None):
        Scope._id_counter += 1
        self.id       = Scope._id_counter
        self.parent   = parent
        self.node     = node      # the AST node that opened this scope (FuncDecl, etc.)
        self.children = []
        self.symbols  = {}        # name → Symbol (locals are declared here)

        if parent is not None:
            parent.children.append(self)

    def declare(self, name, *, is_local=True, is_param=False, decl_node=None):
        sym = Symbol(name, is_local=is_local, is_param=is_param, decl_node=decl_node)
        self.symbols[name] = sym
        return sym

    def lookup(self, name):
        scope = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def lookup_local(self, name):
        return self.symbols.get(name)

    def is_global(self, name):
        return self.lookup(name) is None

    def depth(self):
        d, s = 0, self
        while s.parent:
            d += 1
            s = s.parent
        return d

    def __repr__(self):
        return f"Scope(id={self.id}, depth={self.depth()}, symbols={list(self.symbols)})"


class SymbolTable:
    def __init__(self, root):
        self.root      = root
        self.scope_of  = {}   # Node → Scope (which scope a node belongs to)
        self.symbol_of = {}   # name → [Symbol, ...]  (all decls across all scopes)

    def _register(self, sym):
        self.symbol_of.setdefault(sym.name, []).append(sym)

    def all_locals(self):
        result = []
        for syms in self.symbol_of.values():
            result.extend(s for s in syms if s.is_local or s.is_param)
        return result

    def all_globals(self):
        result = []
        for syms in self.symbol_of.values():
            result.extend(s for s in syms if not s.is_local and not s.is_param)
        return result

    def __repr__(self):
        return (f"SymbolTable("
                f"scopes={Scope._id_counter}, "
                f"unique_names={len(self.symbol_of)})")


class ScopeAnalyser(Visitor):
    def __init__(self):
        super().__init__(order="pre")
        Scope._id_counter = 0
        root          = Scope(parent=None, node=None)
        self.table    = SymbolTable(root)
        self._scope   = root          # current scope during traversal
        self._pending_refs = []       # (Name node, scope_at_read) — resolved post-walk

    def _push(self, node):
        s = Scope(parent=self._scope, node=node)
        self._scope = s
        return s

    def _pop(self):
        self._scope = self._scope.parent

    def _declare(self, name, *, is_local=True, is_param=False, decl_node=None):
        sym = self._scope.declare(name, is_local=is_local,
                                  is_param=is_param, decl_node=decl_node)
        self.table._register(sym)
        return sym

    def visit(self, node):
        if node is None:
            return
        # Record which scope this node lives in
        self.table.scope_of[id(node)] = self._scope

        dispatch = getattr(self, f"visit_{type(node).__name__}", None)
        if dispatch:
            dispatch(node)
        else:
            super()._traverse_children(node)
    def visit_Block(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_LocalDecl(self, node):
        for expr in node.exprs:
            self.visit(expr)
        for name in node.names:
            self._declare(name, is_local=True, decl_node=node)

    def visit_Assign(self, node):
        for expr in node.exprs:
            self.visit(expr)
        for target in node.targets:
            if isinstance(target, Name):
                # global assignment if name not already in scope
                if self._scope.lookup(target.name) is None:
                    self._declare(target.name, is_local=False, decl_node=node)
            else:
                self.visit(target)

    def visit_Do(self, node):
        self._push(node)
        self.visit(node.body)
        self._pop()

    def visit_WhileLoop(self, node):
        self.visit(node.cond)
        self._push(node)
        self.visit(node.body)
        self._pop()

    def visit_RepeatLoop(self, node):
        # repeat…until: condition can see locals declared in the body
        self._push(node)
        self.visit(node.body)
        self.visit(node.cond)
        self._pop()

    def visit_IfStmt(self, node):
        for cond, body in node.clauses:
            self.visit(cond)
            self._push(body)
            self.visit(body)
            self._pop()
        if node.else_body:
            self._push(node.else_body)
            self.visit(node.else_body)
            self._pop()

    def visit_NumericFor(self, node):
        self.visit(node.start)
        self.visit(node.stop)
        if node.step:
            self.visit(node.step)
        self._push(node)
        # loop variable is local to the for-body scope
        self._declare(node.var, is_local=True, is_param=True, decl_node=node)
        self.visit(node.body)
        self._pop()

    def visit_GenericFor(self, node):
        for it in node.iters:
            self.visit(it)
        self._push(node)
        for name in node.names:
            self._declare(name, is_local=True, is_param=True, decl_node=node)
        self.visit(node.body)
        self._pop()

    def _visit_func(self, func_node, name, params, body, is_local):
        if is_local and name:
            # `local function f`, f is visible inside its own body (recursive)
            self._declare(name, is_local=True, decl_node=func_node)
        self._push(func_node)
        for p in params:
            if p != "...":
                self._declare(p, is_local=True, is_param=True, decl_node=func_node)
        self.visit(body)
        self._pop()
        if not is_local and name:
            # `function f` at statement level, f is global (or already declared)
            if self._scope.lookup(name) is None:
                self._declare(name, is_local=False, decl_node=func_node)

    def visit_FuncDecl(self, node):
        self._visit_func(node, node.name, node.params, node.body, node.is_local)

    def visit_FuncExpr(self, node):
        self._visit_func(node, None, node.params, node.body, is_local=True)

    def visit_ReturnStmt(self, node):
        for e in node.exprs:
            self.visit(e)

    def visit_CallStmt(self, node):
        self.visit(node.call_expr)

    def visit_Name(self, node):
        self._pending_refs.append((node, self._scope))

    def visit_CallExpr(self, node):
        self.visit(node.func)
        for a in node.args:
            self.visit(a)

    def visit_MethodCallExpr(self, node):
        self.visit(node.obj)
        for a in node.args:
            self.visit(a)

    def visit_FieldExpr(self, node):
        self.visit(node.obj)

    def visit_IndexExpr(self, node):
        self.visit(node.obj)
        self.visit(node.key)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnOp(self, node):
        self.visit(node.operand)

    def visit_TableConstructor(self, node):
        for key, value in node.fields:
            if isinstance(key, Node):
                self.visit(key)
            self.visit(value)

    def _resolve_refs(self):
        for name_node, read_scope in self._pending_refs:
            sym = read_scope.lookup(name_node.name)
            if sym is None:
                continue
            sym.refs.append(name_node)
            decl_scope = self._find_decl_scope(sym, read_scope)
            if decl_scope and decl_scope is not read_scope:
                sym.is_upval = True

    def _find_decl_scope(self, sym, from_scope):
        s = from_scope
        while s is not None:
            if sym.name in s.symbols and s.symbols[sym.name] is sym:
                return s
            s = s.parent
        return None


def analyse(ast):
    analyser = ScopeAnalyser()
    analyser.visit(ast)
    analyser._resolve_refs()
    return analyser.table


def format_symbol_table(table):
    def format_symbol(symbol):
        flags = []
        if symbol.is_local:
            flags.append("local")
        else:
            flags.append("global")
        if symbol.is_param:
            flags.append("param")
        if symbol.is_upval:
            flags.append("upval")
        return f"{symbol.name} [{' | '.join(flags)}] refs={len(symbol.refs)}"

    def format_scope(scope, indent=0):
        lines = []
        prefix = "  " * indent
        if scope.parent is None:
            lines.append("Scope 1 (root)")
        else:
            lines.append(f"{prefix}Scope {scope.id} (depth={scope.depth()})")

        if scope.symbols:
            for symbol in sorted(scope.symbols.values(), key=lambda item: item.name):
                lines.append(f"{prefix}  - {format_symbol(symbol)}")
        else:
            lines.append(f"{prefix}  - <no local declarations>")

        for child in scope.children:
            lines.extend(format_scope(child, indent + 1))

        return lines

    lines = [repr(table), ""]
    lines.extend(format_scope(table.root))
    return "\n".join(lines)
