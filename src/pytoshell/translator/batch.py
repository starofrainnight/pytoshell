import ast
import six
import os.path
import weakref
from . import base
from .. import _get_data_path

class LocalContext(object):
    def __init__(self, enter_func, exit_func):
        self._enter_func = enter_func
        self._exit_func = exit_func

    def __enter__(self):
        self._enter_func()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit_func(exc_type, exc_val, exc_tb)

class Object(object):
    TAG_NORMAL = "PYTSV"
    TAG_ARGUMENT = "PYTSU"
    TAG_INTERNAL = "PYTSI"
    TAG_RAW = "PYTSA"
    TAG_RET = "PYTSR"

    def __init__(self, name, tag):
        self._name = str(name)
        self._tag = tag

    @property
    def name(self):
        return self._name

    @property
    def escaped_name(self):
        return self._escape_name(self.name)

    @property
    def id_(self):
        return "%s%s" % (self.tag, self._escape_name(self.name))

    @property
    def tag(self):
        return self._tag

    @classmethod
    def _escape_name(cls, name):
        chars = []
        for c in name:
            if c.isupper():
                chars.append("#")
            else:
                c = c.upper()
            chars.append(c)
        return ''.join(chars)

    @classmethod
    def _unescape_name(cls, name):
        chars = []
        for i in range(len(name)):
            c = name[i]
            if c == "#":
                i += 1
                c = name[i].upper()
            else:
                c = c.lower()

            chars.append(c)
        return "".join(chars)

class Function(Object):
    def __init__(self, name, tag=Object.TAG_NORMAL):
        super().__init__(name, tag)

    @property
    def id_(self):
        return ":" + super().id_

class Variant(Object):
    def __init__(self, name, tag=Object.TAG_NORMAL):
        super().__init__(name, tag)

    @property
    def value(self):
        return "%%%s%%" % self.id_

    @property
    def id_(self):
        return "@" + super().id_

    @property
    def type_info(self):
        return TypeInfoVariant(self.name, self.tag)

class TypeInfoVariant(Variant):
    def __init__(self, name, tag=Object.TAG_NORMAL):
        if name.endswith("-t"):
            name = "-t"
        else:
            name += "-t"
        super().__init__(name, tag)

class ArgumentVariant(Variant):
    def __init__(self, name, tag=Object.TAG_ARGUMENT):
        super().__init__(name, tag)

    @property
    def value(self):
        return "%%%s%%" % super().value

class RetVariant(Variant):
    def __init__(self):
        super().__init__("", Object.TAG_RET)

class CommandGenerator(object):
    def __init__(self):
        self._variant_id = 0

    def _new_variant_id(self):
        self._variant_id += 1
        return self._variant_id

    def _new_raw_variant(self):
        return Variant(self._new_variant_id(), Object.TAG_RAW)

    @classmethod
    def _list_safe_append(cls, alist, value):
        if isinstance(value, six.string_types):
            alist.append(value)
        else:
            alist += value

    @classmethod
    def set_variant(cls, name, value, type_="str", is_raw=False):
        variant = None
        if isinstance(name, Variant):
            variant = name
            variant_id = variant.id_
            variant_type_id = variant.type_info.id_
        else:
            variant_id = name

        if isinstance(value, Variant):
            value_value = value.value
            is_raw = True
            value_type_info_value = value.type_info.value
        elif value is None:
            value_value = ""
            value_type_info_value = ""
        else:
            value_value = value
            if isinstance(value_value, six.string_types):
                value_value = value_value.replace("%", "%%")
            value_type_info_value = type_

        command = 'set "%s=%s"' % (variant_id, value_value)
        if not variant is None:
            command += ' & set "%s=%s"' % (variant_type_id, value_type_info_value)

        return command

    @classmethod
    def unset_variant(cls, name):
        return cls.set_variant(name, None, is_raw=True)

    @classmethod
    def calcuate_expr(cls, expression, variant=RetVariant()):
        return 'set /a "%s=%s" > NUL' % (variant.id_, expression)

    @classmethod
    def raw_return_(cls, value=None):
        if value is None:
            value = RetVariant().value
        return "exit /b %s" % value

    @classmethod
    def return_(cls, value=None):
        lines = []

        if value is None:
            value = RetVariant()

        if value.tag != Object.TAG_RET:
            cls._list_safe_append(lines, cls.set_variant(RetVariant(), value))

        cls._list_safe_append(lines, cls.exec_all(cls.end_context(), "exit /b %ERRORLEVEL%"))

        return lines

    @classmethod
    def begin_context(cls):
        return "setlocal"

    @classmethod
    def end_context(cls):
        return cls.exec_all('endlocal', 'set "@PYTSR=%@PYTSR%"', 'set "@PYTSR-T=%@PYTSR-T%"')

    @classmethod
    def comment(cls, text):
        return "::%s" % text

    @classmethod
    def exec_all(cls, *args):
        return ' & '.join(args)

    @classmethod
    def get_char(cls, variant, index):
        return '%%%s:%s,1%%' % (varaint.id_, index)

    @classmethod
    def pipe(cls, *args):
        return ' | '.join(args)

    @classmethod
    def if_equal(cls, text0, text1, if_block, else_block):
        lines = []
        lines.append("if \"%s\"==\"%s\" (" % (text0, text1))
        if isinstance(if_block, six.string_types):
            lines.append(if_block)
        else:
            lines += if_block
        lines.append(") else (")
        if isinstance(else_block, six.string_types):
          lines.append(else_block)
        else:
          lines += else_block
        lines.append(")")
        return lines

    @classmethod
    def get_type(cls, varaint):
        lines = []
        lines.append(cls.unset_variant(RetVariant()))
        result = ""
        result += 'for /f "tokens=1 delims=@" %%%%a "'
        result += ' in ("%s") ' % varaint.value
        result += ' do set "%s=str@%%%%a" ' % RetVariant().id_
        lines.append(result)

        return lines

    @classmethod
    def get_value(cls, varaint):
        if isinstance(varaint, Variant):
            return variant.value

        return "%%%s%%" % variant

    @classmethod
    def invoke(cls, afunction, *args):
        lines = []

        if not isinstance(afunction, Function):
            afunction = Function(afunction)
        arguments = ' '.join(args)

        lines.append("call %s %s" % (afunction.id_, arguments))

        return lines

class Constants(object):
    RET = RetVariant()
    ARGUMENT_COUNT = ArgumentVariant("count")

class Source(object):
    def __init__(self, command_generator):
        self.front = []
        self.back = []
        self.temp_finalize = []
        self.definitions = []
        self._cg = command_generator

    def create_temp_varaint(self):
        variant = self._cg._new_raw_variant()
        self.temp_finalize.insert(0, self._cg.unset_variant(variant))
        return variant

    def append(self, other_source):
        self.front += other_source.front
        self.back = other_source.back + self.back
        self.temp_finalize = other_source.temp_finalize + self.temp_finalize
        self.definitions += other_source.definitions

    def _temp_clearup_enter(self):
        pass

    def _temp_clearup_exit(self, exc_type, exc_val, exc_tb):
        self.front += self.temp_finalize
        self.temp_finalize.clear()

    def _context_enter(self):
        self.add_initialize(self._cg.begin_context())
        self._temp_clearup_enter()

    def _context_exit(self, exc_type, exc_val, exc_tb):
        self._temp_clearup_exit(exc_type, exc_val, exc_tb)
        self.add_initialize(self._cg.end_context())

    def start_context(self):
        return LocalContext(self._context_enter, self._context_exit)

    def start_temp_clearup(self):
        return LocalContext(self._temp_clearup_enter, self._temp_clearup_exit)

    def add_initialize(self, line):
        self._cg._list_safe_append(self.front, line)

    def add_finalize(self, line):
        self._cg._list_safe_append(self.back, line)

    def add_definition(self, source):
        if not isinstance(source, Source):
            raise TypeError("source must be Source type!")

        self.definitions.append(source)

class Stack(list):
    def push(self, value):
        self.append(value)

    @property
    def top(self):
        return self[len(self) - 1]

    def __enter__(self):
        self.push({})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()

class Translator(base.Translator):
    file_extensions = ['bat']
    _module_dir = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self):
        self._stack = Stack()
        self._cg = CommandGenerator()
        self._ret_variant = RetVariant()

    def _gen_call(self, node):
        if not isinstance(node, ast.Call):
            raise TypeError("node must be type of ast.Call!")

        source = Source(self._cg)

        function_name = node.func.id
        batch_function = Function(function_name)

        arguments = []
        for argument in node.args:
            temp_variant = source.create_temp_varaint()

            sub_source = self._parse_value(argument, temp_variant)
            source.append(sub_source)

            arguments.append(temp_variant.id_)

        source.add_initialize(self._cg.invoke(batch_function.name, *arguments))

        return source

    def _parse_value(self, value, variant=None):
        source = Source(self._cg)

        if variant is None:
            variant = self._ret_variant

        if isinstance(value, ast.Num):
            source.add_initialize(self._cg.set_variant(variant, value.n, "int"))
        elif isinstance(value, ast.Str):
            source.add_initialize(self._cg.set_variant(variant, value.s, "str"))
        elif isinstance(value, ast.Name):
            source.add_initialize(self._cg.set_variant(variant, Variant(value.id)))
        elif isinstance(value, ast.Tuple):
            elements = []
            for new_value in value.elts:
                temp_variant = source.create_temp_varaint()
                sub_source = self._parse_value(new_value, temp_variant)
                source.append(sub_source)
                elements.append(temp_variant.id_)

            source.add_initialize(self._cg.set_variant(
                variant, '"%s"' %" ".join(elements), "tuple"))
        elif isinstance(value, ast.Call):
            sub_source = self._gen_call(value)
            source.append(sub_source)
        elif isinstance(value, ast.FunctionDef):
            source.add_initialize("") # Add a new line before function definition
            source.add_initialize(Function(value.name).id_)
            for an_arg in value.args.args:
                an_arg_variant = Variant(an_arg.arg)
                source.add_initialize('set "%s=%%%%1%%" & set "%s=%%%%1%%"' % (
                    an_arg_variant.id_, an_arg_variant.type_info.id_))
                source.add_initialize('shift')
            source.add_finalize(self._cg.raw_return_("%ERRORLEVEL%"))
        elif isinstance(value, ast.BinOp):

            left_temp_variant = source.create_temp_varaint()
            left_source = self._parse_value(value.left, left_temp_variant)
            source.append(left_source)

            right_temp_variant = source.create_temp_varaint()
            right_source = self._parse_value(value.right, right_temp_variant)
            source.append(right_source)

            operators = {
                ast.Add:["+", "__add__"],
                ast.Sub:["-", "__sub__"],
                ast.Mult:["*", "__mul__"],
                ast.Div:["/", "__truediv__"],
                ast.Mod:["%", "__mod__"],
                ast.LShift:["<<", "__lshift__"],
                ast.RShift:[">>", "__rshift__"],
                ast.BitOr:["|", "__or__"],
                ast.BitAnd:["&", "__and__"],
                ast.BitXor:["^", "__xor__"],
            }

            opt = operators[type(value.op)][0]
            opt_name = operators[type(value.op)][1]
            afunction = Function("%%%s%%.%s" % (left_temp_variant.type_info.id_.lower(), opt_name))
            source.add_initialize(self._cg.invoke(
                afunction,
                left_temp_variant.id_, right_temp_variant.id_,
            ))
            if variant.tag != Object.TAG_RET:
                source.add_initialize(self._cg.set_variant(variant, self._ret_variant))
        elif isinstance(value, ast.Return):
            if value.value is not None:
                sub_source = self._parse_value(value.value)
                source.append(sub_source)
            source.add_initialize(self._cg.return_())

        return source

    def _parse_assign(self, name, value):
        source = Source(self._cg)

        if isinstance(value, ast.Num):
            source.add_initialize(self._cg.set_variant(Variant(name.id), value.n, "int"))
        elif isinstance(value, ast.Str):
            source.add_initialize(self._cg.set_variant(Variant(name.id), value.s, "str"))
        elif isinstance(value, ast.Name):
            source.add_initialize(self._cg.set_variant(Variant(name.id), Variant(value.id)))
        elif isinstance(value, ast.NameConstant):
            constants_table = {
                True:1,
                False:0,
            }
            source.add_initialize(self._cg.set_variant(Variant(name.id), constants_table[value.value], "bool"))
        else:
            sub_source = self._parse_value(value)
            source.append(sub_source)
            source.add_initialize(self._cg.set_variant(Variant(name.id), self._ret_variant))

        return source

    def _parse_node(self, node):
        source = Source(self._cg)

        if isinstance(node, ast.Assign):
            atarget = node.targets[0]
            with source.start_temp_clearup():
                if isinstance(atarget, ast.Name):
                    sub_source = self._parse_assign(atarget, node.value)
                    source.append(sub_source)
                elif isinstance(atarget, ast.Tuple):
                    for i in range(len(atarget.elts)):
                        avariable = atarget.elts[i]
                        value = node.value.elts[i]
                        sub_source = self._parse_assign(avariable, value)
                        source.append(sub_source)
        elif isinstance(node, ast.Expr):
            with source.start_temp_clearup():
                sub_source = self._parse_value(node.value)
                source.append(sub_source)
        elif isinstance(node, ast.Return):
            with source.start_temp_clearup():
                sub_source = self._parse_value(node)
                source.append(sub_source)

        if "body" in node.__dict__:

            if isinstance(node, ast.FunctionDef):
                new_source = self._parse_value(node)
            else:
                new_source = source

            with self._stack, new_source.start_context():
                for sub_node in node.body:
                    sub_source = self._parse_node(sub_node)
                    new_source.append(sub_source)

            if new_source != source:
                source.add_definition(new_source)

        return source

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

    def translate(self, node):
        # Initialize custom members for root node of ast tree
        node.__dict__["_parent"] = None
        node.__dict__["_prev_sibling"] = None
        node.__dict__["_next_sibling"] = None
        node.__dict__["_children"] = []
        self._mark_ast_tree(node)

        print(ast.dump(node))

        with self._stack:
            source = self._parse_node(node)
            lines = []
            lines.append("@echo off")
            lines += source.front
            lines += source.back

            lines.append("del /q/s __PYTSTEMP_EXEC.BAT > NUL")
            lines.append(self._cg.raw_return_("%ERRORLEVEL%"))

            for sub_source in source.definitions:
                lines += sub_source.front
                lines += sub_source.back

        site_module_file = open(os.path.join(self.get_module_path(), "site.bat"), "r")
        with site_module_file:
            for line in site_module_file:
                lines.append(line.strip())

        return "\n".join(lines)
