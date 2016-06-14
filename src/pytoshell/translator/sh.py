import ast
import os.path
from . import base
from .. import _get_data_path

class Translator(base.Translator):
    file_extensions = ['sh']
    module_dir = os.path.splitext(os.path.basename(__file__))[0]

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def translate(self, node):
        print(ast.dump(node))
        return ""
