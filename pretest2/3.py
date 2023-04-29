x = z =  2
x = y + 2
def foo(x):
    x = x + 1

def func(z, x, y=x):
    x = y + z
    foo(x)

func(x+1, 4, y=x+1)