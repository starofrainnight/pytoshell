#!/usr/bin/env python

import argparse
import re
import sys
import six
import os.path

class Application(object):
    def __init__(self):
        description='''Wrote in python, compile to shell scripts (unix sh, windows batch)'''

        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("-t", "--type",
            help="Generate to which type of shellscript (sh, bat)",
            required=True)
        parser.add_argument("-o", "--output", help="Output file path")
        parser.add_argument("file_path", help="Input file path")

        self.__args = parser.parse_args()

        # If user does not specific output path, we default it to input file
        # path
        if self.__args.output is None:
            self.__args.output = self.__args.file_path

    def exec_(self):
        return 0

def main():
    a = Application()
    sys.exit(a.exec_())

if __name__ == "__main__":
    # Execute only if run as a script
    main()
