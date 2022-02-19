# Let's dig inside the function "compile"
# help(compile)

c = compile('test.py', 'test.py', 'exec')
print(c)

print(dir(c))
