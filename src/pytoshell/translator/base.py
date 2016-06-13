import ast

class Translator(ast.NodeVisitor):
    def generate(self, node):
        raise NotImplemented("You must implement generate()!")
