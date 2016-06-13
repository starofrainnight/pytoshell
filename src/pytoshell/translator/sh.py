import ast
from . import base
from .. import _get_data_path

class Translator(base.Translator):
    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def translate(self, node):
        print(ast.dump(node))
        return ""
