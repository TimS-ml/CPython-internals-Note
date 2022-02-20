# CPython internals

Use python 3.7.12 and 2.7.18 source code to understand python better
- Getting the python source code here: 
  - https://www.python.org/downloads/release/python-3712/
  - https://www.python.org/downloads/release/python-2718/
  - Source code => complier => byte code => interpreter(what we gonna focus) => output

Reference:
- [CPython internals: A ten-hour codewalk through the Python interpreter source code](https://www.youtube.com/playlist?list=PLzV58Zm8FuBL6OAv1Yu6AwXZrnsFbbR0S)
- [In Chinese](https://flaggo.github.io/python3-source-code-analysis/)
- byteplay (for 2.7) or bytecode
  - https://github.com/MatthieuDartiailh/bytecode



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



# The opcode and the main interpreter loop
- https://docs.python.org/3/whatsnew/3.6.html#cpython-bytecode-changes
- https://docs.python.org/3/library/dis.html

The output of `python -m dis ./test.py`
```python
  1           0 LOAD_CONST               0 (1)
              2 STORE_NAME               0 (x)

  2           4 LOAD_CONST               1 (2)
              6 STORE_NAME               1 (y)

  3           8 LOAD_NAME                0 (x)
             10 LOAD_NAME                1 (y)
             12 BINARY_ADD
             14 STORE_NAME               2 (z)

  4          16 LOAD_NAME                3 (print)
             18 LOAD_NAME                2 (z)
             20 CALL_FUNCTION            1
             22 POP_TOP
             24 LOAD_CONST               2 (None)
             26 RETURN_VALUE
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

- Single line will match one or more specific byte code
- 2 bytes per command (1 for command, 1 for argument pointer(?))
  - BINARY_ADD becomes 2 bytes in python 3
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

## Inside `opcode.h` and `ceval.c`
### `opcode.h`
In `opcode.h` we can find
```c
#define POP_TOP                   1  // no argument
#define HAVE_ARGUMENT            90  // place holder, before 90: no arg, after 90: with arg
#define LOAD_CONST              100
```

### `ceval.c`
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

For example, `BINARY_ADD`
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

To speedup the loop, you can find a function(?) called `fast_next_code`


## Go over the byte code line by line
by the way: Check `./Python-3.7.12/Lib/dis.py` for what happened inside `python -m dis xxx.py`, you will find:
```python
code = compile(source, args.infile.name, "exec")
```

```
Line 1
0 LOAD_CONST               0 (1)
Push into a `value stack`

2 STORE_NAME               0 (x)
Pop value stack and put into memory


Line 3
8 LOAD_NAME                0 (x)
Load whatever x contains, push to `value stack`
  One object of x, two pointers to x
  `refcount` = 2 now, refcount is for garbage collection
The memory of x is still here

10 LOAD_NAME                1 (y)
12 BINARY_ADD
Pop 1 and 2, add, push 3 into value stack
Check `ceval.c`

14 STORE_NAME               2 (z)

16 LOAD_NAME                3 (print)
print is different in python2 (`PRINT_ITEM`) which was removed in python3

18 LOAD_NAME                2 (z)
20 CALL_FUNCTION            1
22 POP_TOP
24 LOAD_CONST               2 (None)
Load None

26 RETURN_VALUE
Pop None. Python return None by default
```


# Frames, function calls, and scope
