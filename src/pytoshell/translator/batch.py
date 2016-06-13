import ast
from . import base
from .. import _get_data_path

class Translator(base.Translator):
    def generic_visit(self, node):
        print(type(node).__name__)
        ast.NodeVisitor.generic_visit(self, node)

    def generate(self, node):
        self.visit(node)
        # print(node)
        print(ast.dump(node))
        return ""
