x = 10

def foo(x):
    y = x * 2
    return bar(y)

def bar(y):
    y = x / 2
    return y

z = foo(x)
