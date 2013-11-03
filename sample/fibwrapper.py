# -*- coding:utf-8 -*-
"""
calculate fibonacci in current process and subprocess.
"""

import subprocess
import os.path
import time
import fib

from utimeout import Popen


def main(n, m):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fib')
    ps = []
    for _ in range(m):
        ps.append(Popen([path, str(n)]))

    for _ in range(m):
        fib.fib(30)
        time.sleep(5)

    for p in ps:
        p.wait()


if __name__ == '__main__':
    import sys
    n = int(sys.argv[1])
    m = int(sys.argv[2])
    main(n, m)
