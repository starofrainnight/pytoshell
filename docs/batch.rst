
There are rules that use by generated batch scripts

Variants
=====================

Principle
---------------------
Variants are emulated by environment variants.

Because window's environment variant only support case insensitive name, so we have to do a little trick to the name.

If there have any upper case character, we append character '#' before it:

::

 Function Os.Path.Join ==> set "@PYTSV#OS_#PATH_#JOIN=function@Os_Path_Join"

Prefixs
---------------------

* @PYTSR, Return variant
* @PYTSU, Arguments variant
* @PYTSV, Normal Variants
* @PYTSI, Internal Variants
* @PYTSA, Raw Variants (Contained values without type)

Name
---------------------
Format : "@PYTSV(Variant Name)"
Temp Format : "@PYTSV(Number)"

Value
---------------------
Format: "(Type)@(Value)", type prefixed

Value will be converted to a normal temp environment value before using.

Type
---------------------
Only support basic types:

* NoneType
* bool
* int
* str
* float
* dict
* list
* tuple
* function
* method

Special Variants
---------------------

# @PYTSR, Return varaint
* @PYTSUCOUNT, Argument count
* @PYTSUX, Arguments, for example : @PYTSU0, @PYTSU1 ... @PYTSUX

Module
=====================

1. Module don't have directory layout, so the file name just the module name

 For example : module **pytoshell.base** will contained in "pytoshell_base.bat", all dots in module name will be converted to underscore then append ".bat".

2. site.bat is a special module that contains all internal functions

 All stuffs in site.bat will be importted automatically without import code

Functions
=====================

All manually wrote funcitons should prefixed with full module name

::

 os_path_join() if you using join() in os.path module

All Functions are late binded, so they calling a function or a method, they actually calling a environment variant and requiring it's value for the real function name.

::

 set os_path_join

Return
---------------------

Return value not using the ERRORLEVEL, use variant @PYTSR

You should backup the value immediately after called if you want to use it, it might changed during each call.

Internal Functions
---------------------

eval
`````````````````````
Emulated by inserting codes into a batch script then call it.

Feature Supported
=====================

* print()

 Only support basic syntax within only one argument : print("a string with %s" % variant)

* len()
