import ast
import os.path
from .. import _get_data_path

class Translator(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self._is_bootstrap=False

    @property
    def is_bootstrap(self):
        return self._is_bootstrap

    @is_bootstrap.setter
    def is_bootstrap(self, value):
        self._is_bootstrap = value

    def get_module_path(self):
        return _get_data_path(self._module_dir)

    def translate(self, node):
        raise NotImplemented("You must implement generate()!")
