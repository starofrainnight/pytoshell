import ast
from .basegenerator import BaseGenerator

class ShGenerator(BaseGenerator):
    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def generate(self, node):
        print(ast.dump(node))
        return ""
