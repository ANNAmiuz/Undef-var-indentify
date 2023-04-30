import ast


class ASTExplorer:
    def __init__(self):
        # task 2
        self.debug = False
        self.func_def_dict = {}  # func_name : def_node
        self.func_defaultdef_dict = {} # func_name : defaults_define_dict
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
                self.func_defaultdef_dict[node.name] = dict()
                for i in range(len(node.args.defaults)):
                    if self.dfs_ast_normal(node.args.defaults[i]) == 0:
                        self.func_defaultdef_dict[node.name][i] = True
                    else:
                        self.func_defaultdef_dict[node.name][i] = False
                return
            else:
                # in invoking routine: update namespace define set and undefine count
                argc = len(node.args.args)
                undefined_vars = set()
                for i in range(argc):
                    if i < len(args):
                        # pass by arg
                        if args[i]:
                            self.ns_stk[-1].add(node.args.args[i].arg)
                        else:
                            undefined_vars.add(node.args.args[i].arg)
                    elif i >= len(args) and i < argc - len(node.args.defaults):
                        # pass by kw or undefine
                        if kws[node.args.args[i].arg]:
                            self.ns_stk[-1].add(node.args.args[i].arg)
                        else:
                            undefined_vars.add(node.args.args[i].arg)
                    else:
                        # pass by kw or default
                        if node.args.args[i].arg in kws.keys():
                            # pass by kw
                            if kws[node.args.args[i].arg]:
                                self.ns_stk[-1].add(node.args.args[i].arg)
                        else:
                            # pass by default
                            # if isinstance(node.args.defaults[i-(argc-len(node.args.defaults))], ast.Constant):
                            #     self.ns_stk[-1].add(node.args.args[i].arg)
                            # elif isinstance(node.args.defaults[i-(argc-len(node.args.defaults))], ast.Name):
                            #     if node.args.defaults[i-(argc-len(node.args.defaults))].id in self.ns_stk[-1] \
                            #             or (node.args.defaults[i-(argc-len(node.args.defaults))].id in self.ns_stk[0] and not node.args.defaults[i-(argc-len(node.args.defaults))].id in undefined_vars):
                            #         self.ns_stk[-1].add(node.args.args[i].arg)
                            # if self.dfs_ast_normal(node.args.defaults[i-(argc-len(node.args.defaults))]) == 0:
                            #     self.ns_stk[-1].add(node.args.args[i].arg)
                            if self.func_defaultdef_dict[node.name][i-(argc-len(node.args.defaults))]:
                                self.ns_stk[-1].add(node.args.args[i].arg)
                for var in self.ns_stk[0]:
                    # add global defined vars into current function namesapce
                    if not any(arg.arg == var for arg in node.args.args):
                        self.ns_stk[-1].add(var)

        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.func_def_dict[child.name] = child
                self.func_defaultdef_dict[child.name] = dict()
                for i in range(len(child.args.defaults)):
                    if self.dfs_ast_normal(child.args.defaults[i]) == 0:
                        self.func_defaultdef_dict[child.name][i] = True
                    else:
                        self.func_defaultdef_dict[child.name][i] = False
            elif isinstance(child, ast.Assign):
                right_undefined_count = self.dfs_ast_normal(child.value)
                if self.debug:
                    print(
                        f"iterate right: add {right_undefined_count} undefine count")
                self.undefined_count += right_undefined_count
                for left in child.targets:
                    self.dfs_ast_normal(left, (right_undefined_count != 0))
            else:
                undefined_count = self.dfs_ast_normal(child)
                if self.debug:
                    print(
                        f"iterate right: add {undefined_count} undefine count")
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
# print(ast.dump(parse_tree))
# print(parse_tree.body)


myExplorer = ASTExplorer()
myExplorer.ns_stk.append(set())
# myExplorer.debug = True
myExplorer.dfs_ast_ns(parse_tree)
myExplorer.ns_stk.pop()

print(myExplorer.undefined_count)
