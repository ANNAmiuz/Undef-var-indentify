import ast
import sys

def generic_visit(self, node):
        # print(type(node).__name__)
        if self.root==None:
            self.root=node
        ast.NodeVisitor.generic_visit(self, node)

# Define a function for the mutation strategies
def mutate(node):
    if isinstance(node, ast.FunctionDef):
        if not any(isinstance(child_node, ast.Call) and child_node.func.id == node.name for child_node in ast.walk(tree)):
            # If the function is not called anywhere in the code, delete it
            node.body = []
    elif isinstance(node, ast.BinOp):
        # negate binary operators
        if isinstance(node.op, ast.Add):
            node.op = ast.Sub()
        elif isinstance(node.op, ast.Sub):
            node.op = ast.Add()
        elif isinstance(node.op, ast.Mult):
            node.op = ast.Div()
        elif isinstance(node.op, ast.Div):
            node.op = ast.Mult()
    elif isinstance(node, ast.Compare):
        # negate comparison operators
        if isinstance(node.ops[0], ast.Gt):
            node.ops[0] = ast.LtE()
        elif isinstance(node.ops[0], ast.Lt):
            node.ops[0] = ast.GtE()
        elif isinstance(node.ops[0], ast.GtE):
            node.ops[0] = ast.Lt()
        elif isinstance(node.ops[0], ast.LtE):
            node.ops[0] = ast.Gt()
    for child_node in ast.iter_child_nodes(node):
        mutate(child_node)



if __name__ == '__main__':
    # Get the string argument from the program to test
    code = input()
    code = "\n".join(code.split("\\n"))
    print(code)

    # Parse the string input into an AST tree
    tree = ast.parse(code)

    # Apply mutation
    mutate(tree)

    # Recompose the AST into code
    mutated_code = ast.unparse(tree)

    # Dump the AST tree structure
    print(mutated_code)




