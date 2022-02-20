# Let's dig inside the function "compile"
# help(compile)

# c = compile('Your code in text format', 'test.py', 'exec')
c = compile(open('test.py').read(), 'test.py', 'exec')
print(c)

# the most important one is the 'co_code'
print(dir(c))

print(c.co_code)  # a str type thing, a byte code
print([b for b in c.co_code])  # check ASC2 table
print(len(c.co_code))  # 28
