
#!/usr/bin/env python

import argparse
import re
import sys
import six
import os.path
import ast
import io
import logging
import weakref
from .translator.batch import Translator as BatchTranslator
from .translator.sh import Translator as ShTranslator

class Application(object):
    def __init__(self, argv):
        description='''Wrote in python, compile to shell scripts (unix sh, windows batch)'''

        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("-t", "--type",
            help="Generate to which type of shellscript (sh, bat)",
            required=True)
        parser.add_argument("-o", "--output", help="Output file path")
        parser.add_argument("-b", "--bootstrap",
                            help="Bootstrap mode, don't import __init__ module",
                            action='store_true',
                            default=False)
        parser.add_argument("-d", "--dump",
                            help='Dump AST Tree',
                            action='store_true',
                            default=False)
        parser.add_argument("file_path", help="Input file path")

        self.__args = parser.parse_args(argv)

        # If user does not specific output path, we default it to input file
        # path
        if self.__args.output is None:
            self.__args.output ="%s.%s" %(
                os.path.splitext(self.__args.file_path)[0], self.__args.type)

        self._logger = logging.getLogger(__name__)

    def _mark_ast_tree(self, node):
        if 'body' not in node.__dict__:
            return

        prev_sibling = None
        next_sibling = None

        node.__dict__["_children"] = node.body

        for i in range(len(node.body)):
            member = node.body[i]
            if i < (len(node.body) - 1):
                next_sibling = weakref.ref(node.body[i+1])
            else:
                next_sibling = None

            if isinstance(member, ast.AST):
                member.__dict__["_parent"] = weakref.ref(node)
                member.__dict__["_prev_sibling"] = prev_sibling
                member.__dict__["_next_sibling"] = next_sibling
                member.__dict__["_children"] = []
                self._mark_ast_tree(member)

            prev_sibling = weakref.ref(member)

    def mark_ast_tree(self, node):
        node.__dict__["_parent"] = None
        node.__dict__["_prev_sibling"] = None
        node.__dict__["_next_sibling"] = None
        node.__dict__["_children"] = []
        self._mark_ast_tree(node)

    def exec_(self):
        # Register translators
        translator_classes = [ShTranslator, BatchTranslator]
        translators = {}
        for aclass in translator_classes:
            for aext in aclass.file_extensions:
                translators[aext] = aclass()
                translators[aext].is_bootstrap = self.__args.bootstrap

        translator = translators[self.__args.type]

        with io.open(self.__args.file_path) as source_file:
            ast_tree = ast.parse(source_file.read())
            self.mark_ast_tree(ast_tree)

            if self.__args.dump:
                print("=== AST TREE BEGIN ===\n%s\n=== AST TREE END ===\n" % ast.dump(ast_tree))
            script_content = translator.translate(ast_tree)

        with io.open(self.__args.output, "w") as script_file:
            script_file.write(script_content)

        return 0

def main(argv):
    a = Application(argv)
    sys.exit(a.exec_())

if __name__ == "__main__":
    # Execute only if run as a script
    main(sys.argv[1:])
