# -*- coding:utf-8 -*-
import utimeout
from multiprocessing import Process
import time


if __name__ == '__main__':
    p1 = Process(target=utimeout.start,
                 args=(['time', 'python', 'fibwrapper.py', '40', '2'],),
                 kwargs={'timeout': 100, 'polling_time': 3, 'verbose': True})
    p2 = Process(target=utimeout.start,
                 args=(['time', 'python', 'fibwrapper.py', '40', '2'],),
                 kwargs={'timeout': 100, 'polling_time': 3, 'verbose': True})
    p1.start()
    time.sleep(6)
    p2.start()
    p1.join()
    p2.join()
