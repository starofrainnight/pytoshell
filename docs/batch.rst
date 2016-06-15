
There are rules that use by generated batch scripts

Variants
=====================

Principle
---------------------
Variants are emulated by environment variants

Prefixs
---------------------

* @PYTSR, Return variants

 - @PYTSRC, Return variants Count
 - @PYTSRV(Number), Return value variant, number range 0..X (X unlimitted)

* @PYTSV, Normal Variants

Name
---------------------
Prefix with "@PYTSV(Number)"

Value
---------------------
Type prefixed "(Type)@(Value)"

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

Functions
=====================

Module
---------------------

1. Module don't have directory layout, so the file name just the module name

 For example : module **pytoshell.base** will contained in "pytoshell_base.bat", all dots in module name will be converted to underscore then append ".bat".

2. __init__.bat is a special module that contains all internal functions

 All stuffs in __init__.bat will be importted automatically without import code

3. All manually wrote funcitons should prefixed with full module name

 os_path_join() if you using join() in os.path module

Return
---------------------

Return value not using the ERRORLEVEL

They will return multiply varaints defined by @PYTSRC and @PYTSRV(Number).

::

 @PYTSRV0, @PYTSRV1, ... @PYTSRVX

You should backup these values immediately after called if you want to use them, they might changed during each call.
