# CPython internals

Use python 3.8.x source code to understand python better
Update will be very very very slow

# Overview
Source code => complier => byte code => interpreter(what we gonna focus) => output

# Include
header files
interfaces

## 00 opcode.h
different operations



# Objects
internal IOs (for example list object)

## object.c
how things implemented



# Python
run times

## 01 ceval.c
main interpreter loop
```c
for (;;)
```



# Modules / Lib
for example import os, built in modules



# Notes
open python, type:
```
help(compile)

# Compile source into a code object that can be executed by exec() or eval().
c = compile('test.py', 'test.py', 'exec')

# output:
# <code object <module> at 0x7eff7ecc2e40, file "test.py", line 1>



# dir(c) or help(c)
c.co_code

# out: byte code
b'e\x00j\x01\x01\x00d\x00S\x00'

type(c.co_code)

[byte for byte in c.co_code]
# out: check acs2 table
# [101, 0, 106, 1, 1, 0, 100, 0, 83, 0]

# in py2:
[ord(byte) for byte in c.co_code]

```

