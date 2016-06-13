import ast

class BaseGenerator(ast.NodeVisitor):
    def generate(self, node):
        raise NotImplemented("You must implement generate()!")
