import ast

class ShGenerator(ast.NodeVisitor):
    def generic_visit(self, node):
        pass

    def generate(self, node):
        return ""
