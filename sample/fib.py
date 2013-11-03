# -*- coding:utf-8 -*-
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 2) + fib(n - 1)


if __name__ == '__main__':
    import sys
    n = int(sys.argv[1])
    print(fib(n))
