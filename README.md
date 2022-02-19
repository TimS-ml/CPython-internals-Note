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
You don't need to run `make install` inside python 3.7
To install packages, run `./python -m pip install`, then you can find it in `~/.local/lib/python3.7`

To execute python, simply: `./python`
To load python script in IPython, simply: 
- `./python -m pip install` then `./ipython`
- Inside ipython, run:
```python
%run ./your_script.py
```

