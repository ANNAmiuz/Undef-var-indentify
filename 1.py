import ast

class NegateOperatorsAndRemoveUnusedFuncs(ast.NodeTransformer):
    def __init__(self):
        self.global_vars = set()
        self.used_funcs = set()

    def visit_Module(self, node):
        # Visit the children of the module node
        self.generic_visit(node)
        
        # Find all the global variables
        for item in node.body:
            if isinstance(item, ast.Global):
                self.global_vars.update(item.names)
            elif isinstance(item, ast.FunctionDef):
                # If the function definition is used, add it to the set of used functions
                if item.name in self.used_funcs:
                    continue
                # Otherwise, remove it from the list of module body nodes
                else:
                    node.body.remove(item)
        
        # Add a print statement for each global variable found
        for var in self.global_vars:
            node.body.append(ast.parse(f"print({var})").body[0])

        return node

    def visit_FunctionDef(self, node):
        # Keep track of all the function names used in the module
        self.used_funcs.add(node.name)
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
        return self.generic_visit(node)

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

    def to_source(self, node):
        return ast.unparse(node)

# Take a string input from the user
input_str = input()
input_str = "\n".join(input_str.split("\\n"))
print(input_str)

# Parse the input string into an AST
parse_tree = ast.parse(input_str)

# Negate the binary and comparison operators
transformer = NegateOperatorsAndRemoveUnusedFuncs()
negated_tree = transformer.visit(parse_tree)

# Add a print statement for each global variable found
for var in transformer.global_vars:
    negated_tree.body.insert(0, ast.parse(f"print({var})"))

# Dump the negated parse tree
# print(ast.dump(negated_tree))

# Output the modified program as a string
modified_program = transformer.to_source(negated_tree)
print(modified_program)