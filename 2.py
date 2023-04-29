import ast


class ASTExplorer:
    def __init__(self):
        # task 2
        self.debug = True
        self.func_def_dict = {}  # func_name : def_node
        self.ns_stk = []  # each namespace defined_var set
        self.undefined_count = 0

    # traversal into a separate namespace: {var set} {func set}
    # (1) global namespace
    # (2) call from a statement

    def dfs_ast_ns(self, node, invoking=False, invoking_node=None, args=[], kws={}):
        if isinstance(node, ast.FunctionDef):
            if not invoking:
                # firstly meet func_def: update def node
                self.func_def_dict[node.name] = node
                return
            else:
                # in invoking routine: update namespace define set and undefine count
                argc = len(node.args.args)
                for i in range(argc):
                    if i < len(args):
                        # pass by arg
                        if args[i]:
                            self.ns_stk[-1].add(node.args.args[i].arg)
                    elif i >= len(args) and i < argc - len(node.args.defaults):
                        # pass by kw or undefine
                        if kws[node.args.args[i].arg]:
                            self.ns_stk[-1].add(node.args.args[i].arg)
                    else:
                        # pass by kw or default
                        if node.args.args[i].arg in kws.keys():
                            # pass by kw
                            if kws[node.args.args[i].arg]:
                                self.ns_stk[-1].add(node.args.args[i].arg)
                        else:
                            # pass by default
                            if isinstance(node.args.defaults[i-(argc-len(node.args.defaults))], ast.Constant)\
                                    or (isinstance(node.args.defaults[i-(argc-len(node.args.defaults))], ast.Name) and node.args.defaults[i-(argc-len(node.args.defaults))].id in self.ns_stk[-1]):
                                self.ns_stk[-1].add(child.args.args[i].arg)

        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.func_def_dict[child.name] = child
            elif isinstance(child, ast.Assign):
                right_undefined_count = self.dfs_ast_normal(child.value)
                self.undefined_count += right_undefined_count
                for left in child.targets:
                    self.dfs_ast_normal(left, (right_undefined_count != 0))
            else:
                undefined_count = self.dfs_ast_normal(child)
                self.undefined_count += undefined_count

    # traversal into normal statements
    # NOT invoked by Call Node
    def dfs_ast_normal(self, node, undefined_left=False):
        undefined_count = 0
        node_stk = list()
        node_stk.append(node)

        while node_stk:
            cur_node = node_stk.pop()

            if isinstance(cur_node, ast.Call):
                args = list()
                kws = dict()
                for arg in cur_node.args:
                    args.append(self.dfs_ast_normal(arg) == 0)

                for keyword in cur_node.keywords:
                    kws[keyword.arg] = (
                        self.dfs_ast_normal(keyword.value) == 0)
                self.ns_stk.append(set())

                # traversal in target function definition
                self.dfs_ast_ns(
                    self.func_def_dict[cur_node.func.id], True, node, args, kws)

                self.ns_stk.pop(-1)
                continue

            if isinstance(cur_node, ast.Name):
                if isinstance(cur_node.ctx, ast.Store):
                    # left
                    if not undefined_left:
                        self.ns_stk[-1].add(cur_node.id)
                    else:
                        self.ns_stk[-1].discard(cur_node.id)
                elif isinstance(cur_node.ctx, ast.Load):
                    # right
                    if not cur_node.id in self.ns_stk[-1]:
                        if self.debug:
                            print(
                                f'line {cur_node.lineno}: undefined var {cur_node.id}')
                        undefined_count += 1

            for child in ast.iter_child_nodes(cur_node):
                node_stk.append(child)

        return undefined_count


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
myExplorer.ns_stk.append(set())
myExplorer.dfs_ast_ns(parse_tree)
myExplorer.ns_stk.pop()

print(myExplorer.undefined_count)
