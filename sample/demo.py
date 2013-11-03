# -*- coding:utf-8 -*-
import utimeout


if __name__ == '__main__':
    import sys
    x = sys.argv[1]
    if x == 'sleepchild':
        print 'start [python sleepchild.py]'
        utimeout.start(['python', 'sleepchild.py'], timeout=5, verbose=True)

    elif x == 'fibwrapper':
        print 'start [python fibwrapper.py 20 5]'
        utimeout.start(['python', 'fibwrapper.py', '50', '5'], timeout=10, verbose=True)

    elif x == 'fibonacci':
        print 'start [python fibonacci.py 10]'
        utimeout.start(['python', 'fibonacci.py', '10'], timeout=10, polling_time=5, verbose=True)
