# Let's dig inside the function "compile"
# help(compile)

c = compile('test.py', 'test.py', 'exec')
print(c)

# the most important one is the 'co_code'
print(dir(c))

print(c.co_code)  # a str type thing, a byte code
print([b for b in c.co_code])  # check ASC table
