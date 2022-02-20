# Let's dig inside the function "compile"
import dis


TEST_FILE = 'test2.py'
print('File name: {}'.format(TEST_FILE))

# help(compile)
# c = compile('Your code in text format', 'test.py', 'exec')
c = compile(open(TEST_FILE).read(), TEST_FILE, 'exec')
print('Compiled result: {}'.format(c))


# the most important one is the 'co_code'
# print(dir(c))


print('==============================')
print('Examing the byte code')
# print(c.co_code)  # a str type thing, the raw byte code
print([b for b in c.co_code])  # check ASC2 table
print('Size of byte code: {}'.format(len(c.co_code)))


print('==============================')
print(dis.dis(open(TEST_FILE).read()))
print('==============================')
