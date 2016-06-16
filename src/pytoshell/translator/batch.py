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

class Source(object):
    def __init__(self):
        self.front = []
        self.back = []
        self.temp_finalize = []

    def get_ret_varaint(self):
        return "@PYTSR"

    def get_variant(self, name):
        name = str(name)

        if name.startswith("@"):
            return name

        chars = []
        for c in name:
            if c.isupper():
                chars.append("#")
            else:
                c = c.upper()
            chars.append(c)

        return "@PYTSV%s" % "".join(chars)

    def create_temp_varaint(self, name):
        name = self.get_variant(name)
        self.temp_finalize.insert(0, self.gen_set_env(name))
        return name

    def append(self, other_source):
        self.front += other_source.front
        self.back = other_source.back + self.back
        self.temp_finalize = other_source.temp_finalize + self.temp_finalize

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
        self.add_initialize("ENDLOCAL")

    def start_context(self):
        return LocalContext(self._context_enter, self._context_exit)

    def start_temp_clearup(self):
        return LocalContext(self._temp_clearup_enter, self._temp_clearup_exit)

    def add_initialize(self, line):
        self.front.append(line)

    def add_finalize(self, line):
        self.back.append(line)

    def gen_set_env(self, name, value="", do_math=False):
        opt = ""
        if do_math:
            opt = "/a"

        name = self.get_variant(name)

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

    def _new_object_id(self):
        self._object_id += 1
        return self._object_id

    def _gen_call(self, node):
        if not isinstance(node, ast.Call):
            raise TypeError("node must be type of ast.Call!")

        source = Source()

        raw_function_name = node.func.id.replace(".", "_")
        batch_function_name = ":%s" % raw_function_name
        function_name = source.get_variant(raw_function_name)

        arguments = ""
        for argument in node.args:
            sub_source = self._parse_value(argument)
            source.append(sub_source)

            temp_variant = source.create_temp_varaint(self._new_object_id())
            source.set_env(temp_variant, "%%%s%%" % source.get_ret_varaint())
            arguments += " \"%%%s%%\" " % temp_variant

        source.add_initialize("IF \"%%%s%%\"==\"\" (" % function_name)
        source.add_initialize("\tCALL %s %s" % (batch_function_name, arguments))
        source.add_initialize(") ELSE (")
        source.add_initialize("\tCALL %%%s%% %s" % (function_name, arguments))
        source.add_initialize(")")
        return source

    def _parse_value(self, value):
        source = Source()
        variant_name = source.get_ret_varaint()

        if type(value) == ast.Num:
            source.set_env_object(variant_name, value.n)
        elif type(value) == ast.Str:
            source.set_env_object(variant_name, value.s)
        elif type(value) == ast.Name:
            source.set_env(variant_name, "%%%s%%" % source.get_variant(value.id))
        elif type(value) == ast.Call:
            sub_source = self._gen_call(value)
            source.append(sub_source)
        elif type(value) == ast.BinOp:

            left_source = self._parse_value(value.left)
            source.append(left_source)
            left_temp_variant = source.create_temp_varaint(self._new_object_id())
            source.set_env(left_temp_variant, "%%%s%%" % source.get_ret_varaint())

            right_source = self._parse_value(value.right)
            source.append(right_source)
            right_temp_variant = source.create_temp_varaint(self._new_object_id())
            source.set_env(right_temp_variant, "%%%s%%" % source.get_ret_varaint())

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
        source = Source()

        sub_source = self._parse_value(value)
        source.append(sub_source)
        source.set_env(name.id, "%%%s%%" % source.get_ret_varaint())

        return source

    def _parse_node(self, node):
        source = Source()

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
            with self._stack, source.start_context():
                for sub_node in node.body:
                    sub_source = self._parse_node(sub_node)
                    source.append(sub_source)
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

        print(lines)

        return "\n".join(lines)
