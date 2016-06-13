import ast
from .basegenerator import BaseGenerator
from . import _get_data_path

class BatGenerator(BaseGenerator):
    def generic_visit(self, node):
        print(type(node).__name__)
        ast.NodeVisitor.generic_visit(self, node)
        
    def generate(self, node):
        self.visit(node)
        # print(node)
        print(ast.dump(node))
        return ""
