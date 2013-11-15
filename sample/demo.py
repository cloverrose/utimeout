# -*- coding:utf-8 -*-
import utimeout
import datetime
import pytz
tzinfo = pytz.timezone('Asia/Tokyo')


def my_start_message(cmd, timeout, polling_time, verbose):
    return '\n'.join(['START: {0}'.format(datetime.datetime.now(tz=tzinfo)), ' '.join(cmd)])


def my_finish_message(cmd, timeout, polling_time, verbose):
    return '\n'.join(['FINISH: {0}'.format(datetime.datetime.now(tz=tzinfo))])


def my_timeout_message(cmd, timeout, polling_time, verbose):
    return '\n'.join(['TIMEOUT: {0}'.format(datetime.datetime.now(tz=tzinfo))])


if __name__ == '__main__':
    import sys
    x = sys.argv[1]
    if x == 'sleepchild':
        print 'start [python sleepchild.py]'
        utimeout.start(['python', 'sleepchild.py'], timeout=5, verbose=True, start_message=my_start_message, finish_message=my_finish_message, timeout_message=my_timeout_message)

    elif x == 'fibwrapper':
        print 'start [python fibwrapper.py 20 5]'
        utimeout.start(['python', 'fibwrapper.py', '50', '5'], timeout=10, verbose=True)

    elif x == 'fibonacci':
        print 'start [python fibonacci.py 10]'
        utimeout.start(['python', 'fibonacci.py', '10'], timeout=10, polling_time=5, verbose=True)
