# CPython internals

Use python 3.7.12 and 2.7.18 source code to understand python better
- Getting the python source code here: 
  - https://www.python.org/downloads/release/python-3712/
  - https://www.python.org/downloads/release/python-2718/
  - Source code => complier => byte code => interpreter(what we gonna focus) => output

Reference:
- [CPython internals: A ten-hour codewalk through the Python interpreter source code](https://www.youtube.com/playlist?list=PLzV58Zm8FuBL6OAv1Yu6AwXZrnsFbbR0S)
- [In Chinese](https://flaggo.github.io/python3-source-code-analysis/)
- Byte code visualizer
  - https://pythontutor.com/
  - byteplay (for 2.7) or bytecode



# TODO

- [ ] Notation of `opcode.h` and `ceval.c`



# How to play around with the source code

Search **PYIMPORTANT** in source code, it will bring you to the location that crucal to read

You don't need to run `make install` inside python 3.7
After running `make -j8` or `make -j4`, copy or link `python` from ./Python-3.7.12 to project root directory
To install packages, run `./python -m pip install`, then you can find it in `~/.local/lib/python3.7`

To execute python, simply: `./python`
To load python script in IPython, simply: 
- `./python -m pip install` then `./ipython`
- Inside ipython, run:
    ```python
    %run ./your_script.py
    ```

    or

    ```python
    %run -m dis ./your_script.py
    ```



# A qick note of C

## C macros
```c
// An easy one, in `opcode.h`
// call POP_EXCEPT will return a number
#define POP_EXCEPT               89

// in `ceval.c`
// This is neat, avoiding from copying code again and again
#define JUMPTO(x)       (next_instr = first_instr + (x) / sizeof(_Py_CODEUNIT))
#define TOP()             (stack_pointer[-1])
```



# Important terms in Python interpreter

- value stack
- function stack
- frame obj vs function obj vs code obj
  - code: contains `bytecode` (bunch of 0 and 1) + extra info: constants / var name ...
  - function obj: code + env pointer
  - frame obj: code + env pointer, code at run time
  - When you call functin, it create a new frame. Example of 1 function obj and 4 frame obj:
      ```python
      def fact(n):
          if n <= 1:
              return n
          else:
              return n * fact(n-1)

      x = fact(4)
      ```


# The opcode and the main interpreter loop

- https://docs.python.org/3/whatsnew/3.6.html#cpython-bytecode-changes
- https://docs.python.org/3/library/dis.html

The output of `python -m dis ./test.py`

by the way: Check `./Python-3.7.12/Lib/dis.py` for what happened inside `python -m dis xxx.py`, you will find:
```python
code = compile(source, args.infile.name, "exec")
```

```python
  1           0 LOAD_CONST               0 (1)  # Push into a `value stack`
              2 STORE_NAME               0 (x)  # Pop value stack and put into memory

  2           4 LOAD_CONST               1 (2)
              6 STORE_NAME               1 (y)

  3           8 LOAD_NAME                0 (x)  # Load whatever x contains, push to `value stack`
                                                # One object x with two pointers to x
                                                # i.e. `refcount` = 2 now
                                                # refcount is for garbage collection
                                                # The x is in memory
             10 LOAD_NAME                1 (y)
             12 BINARY_ADD
             14 STORE_NAME               2 (z)

  4          16 LOAD_NAME                3 (print)  # print is different in python2 (`PRINT_ITEM`) 
                                                    # which was removed in python3
             18 LOAD_NAME                2 (z)
             20 CALL_FUNCTION            1
             22 POP_TOP
             24 LOAD_CONST               2 (None)
             26 RETURN_VALUE                        # Pop None. Python return None by default
```


## The meaning of byte code
```
          byte code line number                  
          also total bytes so far     var value
              |                             | 
  1           0 LOAD_CONST               0 (1)
  |                 |                    |    
line number     Instruction           var number
```


## What we can found
- Single line will match one or more specific byte code
- 2 bytes per command (1 for command, 1 for argument pointer(?))
  - `BINARY_ADD` becomes 2 bytes in python 3
- `len(c.co_code)` = 28, the python executable should be 28 bytes
- Take a look in side each byte in `c.co_code` list, this should looks familar:
    ```python
    [
        100, 0, 
        90, 0, 
        100, 1, 
        90, 1, 
        101, 0, 
        101, 1, 
    
        ...
    
        100, 2, 
        83, 0
    ]
    ```
- You can find a pre-compiled file end in `.pyc`


## `opcode.h`
In `opcode.h` we can find
```c
#define POP_TOP                   1  // no argument
#define HAVE_ARGUMENT            90  // place holder, before 90: no arg, after 90: with arg
#define LOAD_CONST              100
```


## `ceval.c`
Recall that running `01-compile.py` will return: 
- b'd\x00Z\x00d\x01Z\x01e\x00e\x01\x17\x00Z\x02e\x03e\x02\x83\x01\x01\x00d\x02S\x00'
- which equals to [100, 0, 90, 0, 100, 1, 90, 1, 101, 0, 101, 1, 23, 0, 90, 2, 101, 3, 101, 2, 131, 1, 1, 0, 100, 2, 83, 0]

This list is a compressed result, which will be executed in `ceval.c`

```c
#define TARGET(op) \
    TARGET_##op: \
    case op:

for (;;) {
  ...

  if (HAS_ARG(opcode)) {
      printf("%d: %d, %d\n",
             f->f_lasti, opcode, oparg);
  }

  ...
  
  switch (opcode){
    TARGET(XXX)
      do xxx
  
      ...
  
    TARGET(XXX)
      do xxx
  }

  if (why != WHY_NOT)
      break;
}
```

For example, `BINARY_ADD` opcode function
```c
TARGET(BINARY_ADD) {
    PyObject *right = POP();
    PyObject *left = TOP();
    PyObject *sum;
    if (PyUnicode_CheckExact(left) &&
             PyUnicode_CheckExact(right)) {
        sum = unicode_concatenate(left, right, f, next_instr);
        /* unicode_concatenate consumed the ref to left */
    }
    else {
        sum = PyNumber_Add(left, right);
        Py_DECREF(left);
    }
    Py_DECREF(right);
    SET_TOP(sum);
    if (sum == NULL)
        goto error;
    DISPATCH();
}
```

To speedup the loop, you can find a function(?) called `fast_next_code`



# Frames, function calls, and scope

- https://docs.python.org/3.7/c-api/refcounting.html#c.Py_DECREF

The output of `python -m dis ./test2.py`
```python
  1           0 LOAD_CONST               0 (10)
              2 STORE_NAME               0 (x)

  3           4 LOAD_CONST               1 (<code object foo at 0x7f601d7b6660, file "test2.py", line 3>)
              6 LOAD_CONST               2 ('foo')
              8 MAKE_FUNCTION            0
             10 STORE_NAME               1 (foo)

  7          12 LOAD_CONST               3 (<code object bar at 0x7f601d7b6780, file "test2.py", line 7>)
             14 LOAD_CONST               4 ('bar')
             16 MAKE_FUNCTION            0
             18 STORE_NAME               2 (bar)

 11          20 LOAD_NAME                1 (foo)
             22 LOAD_NAME                0 (x)
             24 CALL_FUNCTION            1
             26 STORE_NAME               3 (z)
             28 LOAD_CONST               5 (None)
             30 RETURN_VALUE

Disassembly of <code object foo at 0x7f601d7b6660, file "test2.py", line 3>:
  4           0 LOAD_FAST                0 (x)
              2 LOAD_CONST               1 (2)
              4 BINARY_MULTIPLY
              6 STORE_FAST               1 (y)

  5           8 LOAD_GLOBAL              0 (bar)
             10 LOAD_FAST                1 (y)
             12 CALL_FUNCTION            1
             14 RETURN_VALUE

Disassembly of <code object bar at 0x7f601d7b6780, file "test2.py", line 7>:
  8           0 LOAD_GLOBAL              0 (x)
              2 LOAD_CONST               1 (2)
              4 BINARY_TRUE_DIVIDE
              6 STORE_FAST               0 (y)

  9           8 LOAD_FAST                0 (y)
             10 RETURN_VALUE
```


## What we can found
- The function is unbound untile execution
- Put `print(compile(xxx))` together you can find something interesting
  - Main code: `<code object <module> at 0x7f601f451d20, file "test2.py", line 1>`
  - Function 1: `<code object foo at 0x7f601d7b6660, file "test2.py", line 3>`
  - Function 2: `<code object bar at 0x7f601d7b6780, file "test2.py", line 7>`
  - So it's samilar to individual files
    - In large code base we have folder structure like this:
        ```
        __init__.py
        Func1.py
        Func2.py
        ```
  - Also you can try this:
      ```python
      import dis
      import test2

      dis.dis(test2.foo)
      ```
- A `frame stack` for the project, check `frameobject.h`, each functions got their frame stack inside


## `object.h`
In python3 the `Py_DECREF` moved to `object.h`

```c
#define Py_DECREF(op)                                   \
    do {                                                \
        PyObject *_py_decref_tmp = (PyObject *)(op);    \
        if (_Py_DEC_REFTOTAL  _Py_REF_DEBUG_COMMA       \
        --(_py_decref_tmp)->ob_refcnt != 0)             \
            _Py_CHECK_REFCNT(_py_decref_tmp)            \
        else                                            \
            _Py_Dealloc(_py_decref_tmp);                \
    } while (0)
```


## `code.h`



# Some opcodes for compiled code

## Without Arg
### BINARY_ADD
```c
TARGET(BINARY_ADD) {
    PyObject *right = POP();
    PyObject *left = TOP();
    PyObject *sum;
    /* NOTE(haypo): Please don't try to micro-optimize int+int on
       CPython using bytecode, it is simply worthless.
       See http://bugs.python.org/issue21955 and
       http://bugs.python.org/issue10044 for the discussion. In short,
       no patch shown any impact on a realistic benchmark, only a minor
       speedup on microbenchmarks. */
    if (PyUnicode_CheckExact(left) &&
             PyUnicode_CheckExact(right)) {
        sum = unicode_concatenate(left, right, f, next_instr);
        /* unicode_concatenate consumed the ref to left */
    }
    else {
        sum = PyNumber_Add(left, right);
        Py_DECREF(left);
    }
    Py_DECREF(right);
    SET_TOP(sum);
    if (sum == NULL)
        goto error;
    DISPATCH();
}
```

## With Arg
### (Important) CALL_FUNCTION

Two types of functions
CFUNCTION is optimized for C

```c
PREDICTED(CALL_FUNCTION);
TARGET(CALL_FUNCTION) {
    PyObject **sp, *res;
    sp = stack_pointer;
    res = call_function(&sp, oparg, NULL);
    stack_pointer = sp;
    PUSH(res);
    if (res == NULL) {
        goto error;
    }
    DISPATCH();
}



Py_LOCAL_INLINE(PyObject *) _Py_HOT_FUNCTION
call_function(PyObject ***pp_stack, Py_ssize_t oparg, PyObject *kwnames)
{
  ...

  if (PyFunction_Check(func)) {
      x = _PyFunction_FastCallKeywords(func, stack, nargs, kwnames);
  }
  else {
      x = _PyObject_FastCallKeywords(func, stack, nargs, kwnames);
  }
  Py_DECREF(func);

  ...

  /* Clear the stack of the function object. */
  while ((*pp_stack) > pfunc) {
      w = EXT_POP(*pp_stack);
      Py_DECREF(w);
  }
}



_PyEval_EvalCodeWithName(PyObject *_co, PyObject *globals, PyObject *locals,
           PyObject *const *args, Py_ssize_t argcount,
           PyObject *const *kwnames, PyObject *const *kwargs,
           Py_ssize_t kwcount, int kwstep,
           PyObject *const *defs, Py_ssize_t defcount,
           PyObject *kwdefs, PyObject *closure,
           PyObject *name, PyObject *qualname)
{
  ...

  /* Create the frame */
  tstate = PyThreadState_GET();
  assert(tstate != NULL);
  f = _PyFrame_New_NoTrack(tstate, co, globals, locals);
  if (f == NULL) {
      return NULL;
  }

  // copy into new frame
  fastlocals = f->f_localsplus;
  freevars = f->f_localsplus + co->co_nlocals;
  ...

}
```

