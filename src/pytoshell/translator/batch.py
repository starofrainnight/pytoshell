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
    NORMAL_TYPE = "PYTSV"
    INTERNAL_TYPE = "PYTSI"
    RAW_TYPE = "PYTSA"
    RET_TYPE = "PYTSR"

    def __init__(self, name, type_):
        self._name = str(name)
        self._type = type_

    @property
    def name(self):
        return self._name

    @property
    def escaped_name(self):
        return self._escape_name(self.name)

    @property
    def id_(self):
        return "%s%s" % (self.type_, self._escape_name(self.name))

    @property
    def type_(self):
        return self._type

    @classmethod
    def _escape_name(cls, name):
        name = name.replace(".", "_")
        chars = []
        for c in name:
            if c.isupper():
                chars.append("#")
            else:
                c = c.upper()
            chars.append(c)
        return ''.join(chars)

class Function(Object):
    def __init__(self, name, type_=Object.NORMAL_TYPE):
        super().__init__(name, type_)

    @property
    def id_(self):
        return ":" + super().id_

class Variant(Object):
    def __init__(self, name, type_=Object.NORMAL_TYPE):
        super().__init__(name, type_)

    @property
    def value(self):
        return "%%%s%%" % self.id_

    @property
    def id_(self):
        return "@" + super().id_

class RetVariant(Variant):
    def __init__(self):
        super().__init__("", Object.RET_TYPE)

class CommandGenerator(object):
    RET_VARIANT = "@PYTSR"
    NORMAL_PREFIX = "@PYTSV"
    INTERNAL_PREFIX = "@PYTSI"
    RAW_PREFIX = "@PYTSA"

    def __init__(self):
        self._variant_id = 0

    def _new_variant_id(self):
        self._variant_id += 1
        return self._variant_id

    def _new_raw_variant(self):
        return RawVariant(self._new_variant_id(), self.RAW_TYPE)

    @classmethod
    def _list_safe_append(cls, alist, value):
        if isinstance(value, six.string_types):
            alist.append(value)
        else:
            alist += value

    @classmethod
    def define_variant(cls, name, value, is_with_type=False):
        if is_with_type:
            value = "%s@%s" % (type(value).__name__, value)
        return 'set "%s=%s"' % (name, value)

    @classmethod
    def undefine_variant(cls, name):
        return define_variant(cls, name, "")

    @classmethod
    def get_function(cls, name):
        if not name.prefix("@"):
            name = cls.variant_from_name(name.replace(".", "_"))
        name = ":" + name[1:]
        return name

    @classmethod
    def calcuate_expr(cls, expression, variant=RetVariant()):
        return 'set /a "%s=%s" > NUL' % (variant.id_, expression)

    @classmethod
    def return_(cls, value=None):
        if value is None:
            value = RetVariant().value
        return cls.exec_all(cls.endlocal(cls), "exit /b " % value)

    @classmethod
    def begin_context(cls):
        return "setlocal"

    @classmethod
    def end_context(cls):
        return "endlocal"

    @classmethod
    def comment(cls, text):
        return "::%s" % text

    @classmethod
    def exec_all(cls, *args):
        return '&'.join(args)

    @classmethod
    def get_char(cls, variant, index):
        return '%%%s:%s,1%%' % (varaint.id_, index)

    @classmethod
    def pipe(cls, *args):
        return '|'.join(args)

    @classmethod
    def if_equal(cls, text0, text1, if_block, else_block):
        lines = []
        lines.append("if %s*==%s* (" % (text0, text1))
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
        lines.append(cls.undefine_variant(RetVariant()))
        result = ""
        result += 'for /f "tokens=1 delims=@" %%%%a "'
        result += ' in ("%s") ' % varaint.value
        result += ' do set "%s=str@%%%%a" ' % RetVariant().id_
        lines.append(result)

        return lines

    @classmethod
    def invoke(cls, function, *args):
        lines = []
        parties = function.split(".")
        variant = cls.variant_from_name(parties[0])
        del parties[0]

        static_function = Function(function)
        dynamic_function = ':%s_%s' % (
            variant.value,
            Function('.'.join(parties)).escaped_name)
        arguments = ' '.join(args)

        if_else_lines = cls.if_equal(
            variant.value, "",
            "call %s %s" % (static_function, arguments),
            "call %s %s" % (dynamic_function, arguments))

        _list_safe_append(lines, cls.get_type(variant))
        _list_safe_append(lines, if_else_lines)

        return

class Source(object):
    def __init__(self, command_generator):
        self.front = []
        self.back = []
        self.temp_finalize = []
        self.definitions = []
        self._cg = command_generator

    def create_temp_varaint(self, name):
        name = Variant(name).id_
        self.temp_finalize.insert(0, self.gen_set_env(name))
        return name

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
        self.add_initialize("SETLOCAL")
        self._temp_clearup_enter()

    def _context_exit(self, exc_type, exc_val, exc_tb):
        self._temp_clearup_exit(exc_type, exc_val, exc_tb)
        self.add_initialize('ENDLOCAL & SET "@PYTSR=%@PYTSR%"')

    def start_context(self):
        return LocalContext(self._context_enter, self._context_exit)

    def start_temp_clearup(self):
        return LocalContext(self._temp_clearup_enter, self._temp_clearup_exit)

    def add_initialize(self, line):
        self.front.append(line)

    def add_finalize(self, line):
        self.back.append(line)

    def add_definition(self, source):
        if not isinstance(source, Source):
            raise TypeError("source must be Source type!")

        self.definitions.append(source)

    def gen_set_env(self, name, value="", do_math=False):
        opt = ""
        if do_math:
            opt = "/a"

        if not name.startswith("@"):
            name = Variant(name).id_

        return 'SET %s "%s=%s"' % (opt, name, value)

    def gen_set_env_object(self, name, value="", do_math=False):
        value = "%s@%s" % (type(value).__name__, value)
        return self.gen_set_env(name, value, do_math)

    def set_env(self, *args, **kwargs):
        self.add_initialize(self.gen_set_env(*args, **kwargs))

    def set_env_object(self, *args, **kwargs):
        self.add_initialize(self.gen_set_env_object(*args, **kwargs))

    def del_env(self, name):
        self.set_env(name)

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
        self._object_id = 0
        self._cg = CommandGenerator()
        self._ret_variant = RetVariant()

    def _new_object_id(self):
        self._object_id += 1
        return self._object_id

    def _gen_call(self, node):
        if not isinstance(node, ast.Call):
            raise TypeError("node must be type of ast.Call!")

        source = Source(self._cg)

        batch_function_name = Function(node.func.id).id_
        function_name = Variant(node.func.id).id_

        arguments = ""
        for argument in node.args:
            sub_source = self._parse_value(argument)
            source.append(sub_source)

            temp_variant = source.create_temp_varaint(self._new_object_id())
            source.set_env(temp_variant, self._ret_variant.value)
            arguments += " \"%%%s%%\" " % temp_variant

        source.add_initialize("IF \"%%%s%%\"==\"\" (" % function_name)
        source.add_initialize("\tCALL %s %s" % (batch_function_name, arguments))
        source.add_initialize(") ELSE (")
        source.add_initialize("\tCALL %%%s%% %s" % (function_name, arguments))
        source.add_initialize(")")
        return source

    def _parse_value(self, value):
        source = Source(self._cg)
        variant_name = self._ret_variant.name

        if type(value) == ast.Num:
            source.set_env_object(variant_name, value.n)
        elif type(value) == ast.Str:
            source.set_env_object(variant_name, value.s)
        elif type(value) == ast.Name:
            source.set_env(variant_name, Variant(value.id).value)
        elif type(value) == ast.Call:
            sub_source = self._gen_call(value)
            source.append(sub_source)
        elif type(value) == ast.BinOp:

            left_source = self._parse_value(value.left)
            source.append(left_source)
            left_temp_variant = source.create_temp_varaint(self._new_object_id())
            source.set_env(left_temp_variant, self._ret_variant.value)

            right_source = self._parse_value(value.right)
            source.append(right_source)
            right_temp_variant = source.create_temp_varaint(self._new_object_id())
            source.set_env(right_temp_variant, self._ret_variant.value)

            operators = {
                ast.Add:"+",
                ast.Sub:"-",
                ast.Mult:"*",
                ast.Div:"/",
                ast.Mod:"%",
                ast.LShift:"<<",
                ast.RShift:">>",
                ast.BitOr:"|",
                ast.BitAnd:"&",
                ast.BitXor:"^",
            }

            opt = operators[type(value.op)]

            source.set_env(
                variant_name,
                "%s%s%s" % (left_temp_variant, opt, right_temp_variant),
                do_math=True)
        return source

    def _parse_assign(self, name, value):
        source = Source(self._cg)

        sub_source = self._parse_value(value)
        source.append(sub_source)
        source.set_env(name.id, self._ret_variant.value)

        return source

    def _parse_node(self, node):
        source = Source(self._cg)

        if type(node) == ast.Assign:
            atarget = node.targets[0]
            with source.start_temp_clearup():
                if type(atarget) == ast.Name:
                    sub_source = self._parse_assign(atarget, node.value)
                    source.append(sub_source)
                elif type(atarget) == ast.Tuple:
                    for i in range(len(atarget.elts)):
                        avariable = atarget.elts[i]
                        value = node.value.elts[i]
                        sub_source = self._parse_assign(avariable, value)
                        source.append(sub_source)

        if "body" in node.__dict__:

            if isinstance(node, ast.FunctionDef):
                new_source = Source(self._cg)
                new_source.add_initialize(Function(node.name).id_)
                new_source.add_finalize("EXIT /B %ERRORLEVEL%")
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
            lines += source.front
            lines += source.back
            lines.append("EXIT /B %ERRORLEVEL%")

            for sub_source in source.definitions:
                lines += sub_source.front
                lines += sub_source.back

        print(lines)

        site_module_file = open(os.path.join(self.get_module_path(), "site.bat"), "r")
        with site_module_file:
            lines + site_module_file.readlines()

        return "\n".join(lines)
