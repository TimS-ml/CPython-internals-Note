# CPython internals

Use python 3.7.12 and 2.7.18 source code to understand python better
- Getting the python source code here: 
  - https://www.python.org/downloads/release/python-3712/
  - https://www.python.org/downloads/release/python-2718/
  - Source code => complier => byte code => interpreter(what we gonna focus) => output

Reference:
- [CPython internals: A ten-hour codewalk through the Python interpreter source code](https://www.youtube.com/playlist?list=PLzV58Zm8FuBL6OAv1Yu6AwXZrnsFbbR0S)
- [In Chinese](https://flaggo.github.io/python3-source-code-analysis/)



# How to play around with the source code
open python, type:
```python
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
