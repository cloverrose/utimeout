# -*- coding:utf-8 -*-
"""
calculate fibonacci many subprocess version
"""

import sys
import os
import subprocess

from utimeout import Popen


def fib(n):
    if n == 0:
        ret =  0
    elif n == 1:
        ret = 1
    else:
        p = Popen(['python', 'fibonacci.py', str(n-2)], stdout=subprocess.PIPE)
        q = Popen(['python', 'fibonacci.py', str(n-1)], stdout=subprocess.PIPE)
        p_ret, _ = p.communicate()
        q_ret, _ = q.communicate()
        ret = int(p_ret) + int(q_ret)

    sys.stdout.write('{0}'.format(ret))
    return ret


if __name__ == '__main__':
    n = int(sys.argv[1])
    print(fib(n))
