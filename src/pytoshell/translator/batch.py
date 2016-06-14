import ast
import six
import os.path
import weakref
from . import base
from .. import _get_data_path

class Source(object):
    def __init__(self):
        self.front = []
        self.back = []

    def append(self, other_source):
        self.front += other_source.front
        self.back = other_source.back + self.back

class Stack(list):
    def push(self, value):
        self.append(value)

    @property
    def top(self):
        return self[len(self) - 1]

class Translator(base.Translator):
    file_extensions = ['bat']
    _module_dir = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self):
        self._stack = Stack()
        self._object_id = 0

    def _new_object_id(self):
        self._object_id += 1
        return self._object_id

    def _get_variant_name(self, node):
        if node.id not in self._stack.top:
            self._stack.top[node.id] = self._new_object_id()

        return "__PTSO%s" % self._stack.top[node.id]

    def _get_temp_variant_name(self):
        return "__PTSTMPO%s" % self._new_object_id()

    def _gen_set_env(self, name, value="", do_math=False):
        opt = ""
        if do_math:
            opt = "/a"

        return 'set %s "%s=%s"' % (opt, name, value)

    def _parse_env(self, name, value="", do_math=False):
        source = Source()
        if not isinstance(name, six.string_types):
            name = self._get_variant_name(name)
        source.front.append(self._gen_set_env(name, value, do_math=do_math))
        source.back.insert(0, self._gen_set_env(name))
        return source

    def _parse_value(self, value):
        source = Source()
        variant_name = self._get_temp_variant_name()

        if type(value) == ast.Num:
            # Use value directly
            variant_name = value.n
        elif type(value) == ast.Str:
            # Use value directly
            variant_name = value.s
        elif type(value) == ast.Call:
            print("Not implemented call value!")
        elif type(value) == ast.BinOp:
            left_source, left_variant = self._parse_value(value.left)
            right_source, right_variant = self._parse_value(value.right)

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
            source.append(self._parse_env(
                variant_name,
                "%s%s%s" % (left_variant, opt, right_variant),
                do_math=True))

        return source, variant_name

    def _parse_assign(self, name, value):
        source = Source()

        sub_source, variant_name = self._parse_value(value)

        source.front += sub_source.front
        source.append(self._parse_env(name, variant_name))
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
            self._stack.push({})
            for sub_node in node.body:
                sub_source = self._parse_node(sub_node)
                source.append(sub_source)
            self._stack.pop()

        return source

    def _mark_ast_tree(self, node):
        if 'body' not in node.__dict__:
            return

        prev_sibling = None
        next_sibling = None

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
                self._mark_ast_tree(member)

            prev_sibling = weakref.ref(member)

    def translate(self, node):
        self._mark_ast_tree(node)
        print(ast.dump(node))

        self._stack.push({})
        source = self._parse_node(node)
        lines = []
        lines += source.front
        lines += source.back
        lines.append("EXIT /B %ERRORLEVEL%")

        return "\n".join(lines)
