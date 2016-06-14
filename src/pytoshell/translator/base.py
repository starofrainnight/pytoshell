import ast
import os.path
from .. import _get_data_path

class Translator(ast.NodeVisitor):
    def get_module_path(self):
        return _get_data_path(self._module_dir)

    def translate(self, node):
        raise NotImplemented("You must implement generate()!")
