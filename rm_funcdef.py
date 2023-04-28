import ast

class RemoveFunctions(ast.NodeTransformer):
    def __init__(self):
        super().__init__
        self.global_vars = set()  

    def visit_Module(self, node):  
        # # Find all the global variables
        # for item in node.body:
        #     if isinstance(item, ast.Global):
        #         self.global_vars.update(item.names)
        #     elif isinstance(item, ast.FunctionDef):
        #         # If the function definition is used, add it to the set of used functions
        #         if item.name in self.used_funcs:
        #             continue
        #         # Otherwise, remove it from the list of module body nodes
        #         else:
        #             node.body.remove(item)
        
        # Add a print statement for each global variable found
        for var in self.global_vars:
            node.body.append(ast.parse(f"print({var})").body[0])
        return node

    def visit_FunctionDef(self, node):
        if not any(isinstance(child_node, ast.Call) and child_node.func.id == node.name for child_node in ast.walk(tree)):
            return None
        else:
            return node

# Example usage
code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

add(1+1)
"""

tree = ast.parse(code)
transformed_tree = RemoveFunctions().visit(tree)
new_code = ast.unparse(transformed_tree)

print(new_code)
