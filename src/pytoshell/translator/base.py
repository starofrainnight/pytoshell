import ast

class Translator(ast.NodeVisitor):
    def translate(self, node):
        raise NotImplemented("You must implement generate()!")
