import ast


class Scope:
    def __init__(self, scope_node):
        self.__scope_node = scope_node


class ASTExplorer:
    def __init__(self):
        self.defined_set = set()  # var name : dependent set()
        self.undefined_count = 0
        self.function_defs = {}  # name : node
        self.function_calls = {}  # calling_node : def_node
        self.calls_within_functions = {}  # function name : {nested calling node under it}
        self.global_vars = []
        self.unused_function_defs = set()
        self.func_def_nodes = set()
        self.ns_list = []  # namespace

    def dfs_ast(self, node, within_function=False, enclosing_function=None):
        if isinstance(node, ast.FunctionDef):
            within_function = True
            enclosing_function = node.name
            self.function_defs[node.name] = node
            self.calls_within_functions[node.name] = set()
            self.func_def_nodes.add(node)

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
        for func_def_node in self.func_def_nodes:
            if not any(func_def_call == func_def_node for func_def_call in self.function_calls.values()):
                self.unused_function_defs.add(func_def_node)

    # traversal through ast tree considering function namespace: {var set} {func set}
    def dfs_ast_ns(self, node, args=[], kws={}, ns_index=0, ns_root=None):
        self.ns_list[ns_index] = [set(), set()]
        undefined_vars = set()
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef):
                if child in self.unused_function_defs:
                    continue
                argc = len(child.args.args)
                for i in range(argc):
                    if i < len(args):
                        # pass by arg
                        if args[i]:
                            self.ns_list[ns_index][0].add(child.args.args[i].arg)
                        else:
                            undefined_vars.add(child.args.args[i].arg)
                    elif i >= len(args) and i < argc - len(child.args.defaults):
                        # pass by kw
                        if kws[child.args.args[i].arg]:
                            self.ns_list[ns_index][0].append(child.args.args[i].arg)
                        else:
                            undefined_vars.add(child.args.args[i].arg)
                    else:
                        # pass by kw or default
                        if child.args.args[i].arg in kws.keys():
                            # pass by kw
                            if kws[child.args.args[i].arg]:
                                self.ns_list[ns_index][0].append(child.args.args[i].arg)
                            else:
                                undefined_vars.add(child.args.args[i].arg)
                        else:
                            # pass by default
                            self.ns_list[ns_index][0].append(child.args.args[i].arg)

            elif isinstance(child, ast.Assign):
                if self.get_nested_undefined_count(child) > 0:
                    self.undefined_count += 1
                    self.defined_set.discard(child)
                    break
                else:
                    self.defined_set.add(child)

    def get_nested_undefined_count(self, node):
        undefined_count = 0
        # 这里也没想好怎么写
        return undefined_count

    def _add_nested_calling(self, enclosing_function, node):
        self.calls_within_functions[enclosing_function].add(node)
        for calling in self.calls_within_functions[node.func.id]:
            self.calls_within_functions[enclosing_function].add(calling)


# Take a string input from the user
input_str = input()
input_str = "\n".join(input_str.split("\\n"))
# print(input_str)
# print("-----------------------------------------------")

# Parse the input string into an AST
parse_tree = ast.parse(input_str)

# Dump the parse tree
print(ast.dump(parse_tree))
# print(parse_tree.body)


myExplorer = ASTExplorer()
myExplorer.dfs_ast(parse_tree)
