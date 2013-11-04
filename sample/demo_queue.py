# -*- coding:utf-8 -*-
from tasks import start

TIMEOUT = 30

if __name__ == '__main__':
    for i in range(3):
        start.delay(['time', 'python', 'fibwrapper.py', '20', '6', 'name{0}'.format(i)], TIMEOUT)
