
#!/usr/bin/env python

import argparse
import re
import sys
import six
import os.path
import ast
import io
import logging
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
        parser.add_argument("file_path", help="Input file path")

        self.__args = parser.parse_args(argv)

        # If user does not specific output path, we default it to input file
        # path
        if self.__args.output is None:
            self.__args.output ="%s.%s" %(
                os.path.splitext(self.__args.file_path)[0], self.__args.type)

        self._logger = logging.getLogger(__name__)

    def exec_(self):
        translators = {
            "sh":ShTranslator(),
            "bat":BatchTranslator(),
            }
        translator = translators[self.__args.type]
        with io.open(self.__args.file_path) as source_file:
            script_content = translator.translate(ast.parse(source_file.read()))

        with io.open(self.__args.output, "w") as script_file:
            script_file.write(script_content)

        return 0

def main(argv):
    a = Application(argv)
    sys.exit(a.exec_())

if __name__ == "__main__":
    # Execute only if run as a script
    main(sys.argv[1:])
