x = 7.5
y = x + x*5.5
def fux1():
    return
def fux2():
    fux1()
def add1(n):
    fux1()
add1(1)
def add1():
    global x
    x = x + 1
    fux2(x)
def add2(y):
    y = y + 2
    add1()
    z = y * (5.5 >= 2)
def add3(z):
    def zcySb():
        return
    zcySb()
    z = z + 3
    fux1()
add1()
add3(x)
