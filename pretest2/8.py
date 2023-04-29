x = 1

def fun1():
    global x
    x = x + 1

def fun2():
    fun1()

def fun1():
    global x
    x = x + 2

fun2()
print(x)