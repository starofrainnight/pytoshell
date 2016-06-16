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
        self.ret = None

    def get_ret_varaint(self):
        return "@PYTSR"

    def get_variant(self, name):
        chars = []
        for c in name:
            if c.isupper():
                chars.append("#")
            else:
                c = c.upper()
            chars.append(c)

        return "@PYTSV%s" % "".join(chars)

    def append(self, other_source):
        self.front += other_source.front
        self.back = other_source.back + self.back

    def _context_enter(self):
        self.add_initialize("SETLOCAL")

    def _context_exit(self, exc_type, exc_val, exc_tb):
        self.add_initialize("ENDLOCAL")

    def start_context(self):
        return LocalContext(self._context_enter, self._context_exit)

    def add_initialize(self, line):
        self.front.append(line)

    def add_finalize(self, line):
        self.back.append(line)

    def set_env(self, name, value="", do_math=False):
        if not isinstance(name, six.string_types):
            raise TypeError("name must be string type!")

        opt = ""
        if do_math:
            opt = "/a"

        if not name.startswith("@"):
            name = self.get_variant(name)

        self.front.append('set %s "%s=%s"' % (opt, name, value))

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

        result = ""
        return_variant_name = self._get_temp_variant_name()
        function_name = node.func.id.replace(".", "_")
        result += function_name
        result += " %s " % return_variant_name
        for argument in node.args:
            result += " \"%%%s%%\" " % self._get_variant_name(argument)
        return result, return_variant_name

    def _parse_value(self, value):
        source = Source()
        variant_name = source.get_variant(str(self._new_object_id()))

        if type(value) == ast.Num:
            source.set_env(variant_name, value.n)
        elif type(value) == ast.Str:
            source.set_env(variant_name, value.s)
        elif type(value) == ast.Call:
            text, result_variant_name = self._gen_call(value)
            source.front.append(text)
            source.del_env(result_variant_name)
        elif type(value) == ast.BinOp:
            left_source = self._parse_value(value.left)
            right_source = self._parse_value(value.right)

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

            source.append(left_source)
            source.append(right_source)
            source.set_env(
                variant_name,
                "%s%s%s" % (left_source.ret, opt, right_source.ret),
                do_math=True)
        source.ret = variant_name
        return source

    def _parse_assign(self, name, value):
        source = Source()

        sub_source = self._parse_value(value)

        source.front += sub_source.front
        source.set_env(name.id, "%%%s%%" % sub_source.ret)
        source.front += sub_source.back

        return source

    def _parse_node(self, node):
        source = Source()

        if type(node) == ast.Assign:
            atarget = node.targets[0]
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
