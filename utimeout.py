# -*- coding:utf-8 -*-
import subprocess
import os
import sys
import signal
import time
import os.path
import uuid
import redis
from multiprocessing import Process, Queue


STDOUT = -2

def Popen(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0):
    p = subprocess.Popen(args, bufsize, executable, stdin, stdout, stderr, preexec_fn, close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags)
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.sadd(os.getenv('redis_key'), str(p.pid))
    return p


def _get_tick():
    return os.sysconf(os.sysconf_names['SC_CLK_TCK'])


def _parse_cputime(pid):
    try:
        with open('/proc/{0}/stat'.format(pid)) as f:
            t = f.readline().strip('\n').split()
            return int(t[13]) + int(t[14])
    except IOError as e:
        return None


def _calc_total_cputime(r, tick, redis_key):
    running_child_cputime = 0
    remove_pids = set()
    for pid in r.smembers(redis_key):
        cputime = _parse_cputime(int(pid))
        if cputime is None:
            remove_pids.add(pid)
        else:
            running_child_cputime += cputime
    for pid in remove_pids:
        r.srem(redis_key, pid)
    running_child_cputime = running_child_cputime / tick
    times = os.times()
    return running_child_cputime + times[2] + times[3]


def _start_core(cmd, timeout, polling_time, verbose, stdout, stderr):
    redis_key = uuid.uuid4().hex
    os.environ['redis_key'] = redis_key

    tick = _get_tick()
    if verbose:
        stderr.write('tick: {0}\n'.format(tick))
        stderr.flush()
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete(redis_key)

    p = Popen(cmd, preexec_fn=os.setsid, stderr=subprocess.STDOUT, stdout=stdout)

    while p.poll() is None:
        cputime = _calc_total_cputime(r, tick, redis_key)
        if verbose:
            stderr.write('cputime: {0}s\n'.format(cputime))
            stderr.flush()
        if cputime > timeout:
            os.killpg(p.pid, signal.SIGTERM)
            stderr.write('timeout ({0}s)\n'.format(cputime))
            stderr.flush()
            timeout = True
            break
        time.sleep(polling_time)
    else:
        cputime = _calc_total_cputime(r, tick, redis_key)
        stderr.write('finish ({0}s)\n'.format(cputime))
        stderr.flush()
        timeout = False
    r.delete(redis_key)
    return timeout


def _start_queue(queue, cmd, timeout, polling_time, verbose, stdout, stderr):
    timeout = _start_core(cmd, timeout, polling_time, verbose, stdout, stderr)
    queue.put(timeout)


def start(cmd, timeout, polling_time=1, verbose=False, stdout=None, stderr=None, start_message=None, finish_message=None, timeout_message=None):
    """
    if timeout return True,
    if finish return False.
    """
    out = stdout if stdout is not None else sys.stdout
    if stderr == STDOUT:
        err = out
    else:
        err = stderr if stderr is not None else sys.stderr

    queue = Queue()
    p = Process(target=_start_queue,
                args=(queue,),
                kwargs=dict(cmd=cmd,
                            timeout=timeout,
                            polling_time=polling_time,
                            verbose=verbose,
                            stdout=out,
                            stderr=err))
    if start_message:
        msg = start_message(cmd, timeout, polling_time, verbose)
        if msg != "":
            err.write(str(msg))
            err.flush()
    p.start()
    timeout = queue.get()
    p.join()
    if timeout and timeout_message:
        msg = timeout_message(cmd, timeout, polling_time, verbose)
        if msg != "":
            err.write(str(msg))
            err.flush()
    elif not timeout and finish_message:
        msg = finish_message(cmd, timeout, polling_time, verbose)
        if msg != "":
            err.write(str(msg))
            err.flush()
    return timeout
