import ast

class BatGenerator(ast.NodeVisitor):
    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def generate(self, node):
        return ""
