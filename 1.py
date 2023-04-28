import ast


class ASTExplorer:
    def __init__(self):
        self.function_defs = {}  # name : node
        self.function_calls = {}  # calling_node : def_node
        self.calls_within_functions = {}  # function name : {nested calling node under it}
        self.global_vars = []
        self.unused_function_defs = set()

    def dfs_ast(self, node, within_function=False, enclosing_function=None):
        if isinstance(node, ast.FunctionDef):
            within_function = True
            enclosing_function = node.name
            self.function_defs[node.name] = node
            self.calls_within_functions[node.name] = set()

        if isinstance(node, ast.Call):
            if within_function:
                self.calls_within_functions[enclosing_function].add(node)
                self._add_nested_calling(enclosing_function, node)
            else:
                self.function_calls[node] = self.function_defs[node.func.id]
                for calling_node in self.calls_within_functions[node.func.id]:
                    self.function_calls[calling_node] = self.function_defs[calling_node.func.id]

        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            # Check if the name is not defined within a function
            if not within_function:
                self.global_vars.append(node.id)

        for child in ast.iter_child_nodes(node):
            self.dfs_ast(child, within_function, enclosing_function)

    def get_unused_function_defs(self):
        for func_def in self.function_defs.values():
            if not any(func_def_call == func_def for func_def_call in self.function_calls.values()):
                self.unused_function_defs.add(func_def)

    def print_function_sets(self):
        print("Function definitions:")
        for name, node in self.function_defs.items():
            print(f"{name} -> {node} ")

        print("\nCalls within functions:")
        for name, calls in self.calls_within_functions.items():
            if len(calls) > 0:
                print(f"- {name}: ")
                for call in calls:
                    print(f"  - {call.func.id} ")

        print("\nFunction_calls:")
        for caller, callee in self.function_calls.items():
            print(f"{caller.func.id} {caller} -> {callee.name} {callee} ")

        print("\nGlobal variables:")
        for var in self.global_vars:
            print(f"{var}")

        print("\nUnused function defs:")
        for func_def in self.unused_function_defs:
            print(f"{func_def.name} {func_def}")

    def _add_nested_calling(self, enclosing_function, node):
        self.calls_within_functions[enclosing_function].add(node)
        for calling in self.calls_within_functions[node.func.id]:
            self.calls_within_functions[enclosing_function].add(calling)


class ASTMutator(ast.NodeTransformer):
    def __init__(self, unused_func_defs):
        super().__init__
        self.unused_func_defs = unused_func_defs

    def visit_FunctionDef(self, node):
        if node in self.unused_func_defs:
            # If the function is not used, delete it
            return None
        else:
            return node

    def visit_BinOp(self, node):
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
            elif isinstance(node.op, ast.Mult):
                node.op = ast.Div()
            elif isinstance(node.op, ast.Div):
                node.op = ast.Mult()
        return node

    def visit_Compare(self, node):
        # Negate each comparison operator in the list except Eq and NotEq
        for i, op in enumerate(node.ops):
            if isinstance(op, (ast.Gt, ast.GtE, ast.Lt, ast.LtE)):
                node.ops[i] = self._negate_operator(op)
        return node

    def _negate_operator(self, op):
        # Negate the comparison operator by returning its complement
        if isinstance(op, ast.GtE):
            return ast.Lt()
        elif isinstance(op, ast.Gt):
            return ast.LtE()
        elif isinstance(op, ast.LtE):
            return ast.Gt()
        elif isinstance(op, ast.Lt):
            return ast.GtE()
        else:
            raise ValueError(f"Invalid operator: {type(op).__name__}")


# Take a string input from the user
input_str = input()
input_str = "\n".join(input_str.split("\\n"))
# print(input_str)
# print("-----------------------------------------------")

# Parse the input string into an AST
parse_tree = ast.parse(input_str)

# Dump the parse tree
# print(ast.dump(parse_tree))
# print(parse_tree.body)
myExplorer = ASTExplorer()
myExplorer.dfs_ast(parse_tree)
myExplorer.get_unused_function_defs()
myExplorer.print_function_sets()

# Negate the binary and comparison operators
mymutator = ASTMutator(myExplorer.unused_function_defs)
mutated_tree = mymutator.visit(parse_tree)

# Add a print statement for each global variable found
for var in myExplorer.global_vars:
    print_node = ast.Expr(value=ast.Call(func=ast.Name(id="print", ctx=ast.Load()),
                                      args=[ast.Name(id=var, ctx=ast.Load())],
                                      keywords=[]))
    mutated_tree.body.append(print_node)

# Dump the negated parse tree
# print(ast.dump(negated_tree))

# Output the modified program as a string
modified_program = ast.unparse(mutated_tree)
print(modified_program)
