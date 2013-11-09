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


def start(cmd, timeout, polling_time=1, verbose=False, stdout=None, stderr=None):
    """
    if timeout return True,
    if finish return False.
    """
    out = stdout if stdout is not None else sys.stdout
    if stderr == STDOUT:
        err = out
    else:
        err = stderr if stderr is not None else sys.stderr

    redis_key = uuid.uuid4().hex
    os.environ['redis_key'] = redis_key

    tick = _get_tick()
    if verbose:
        err.write('tick: {0}\n'.format(tick))
        err.flush()
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete(redis_key)

    p = Popen(cmd, preexec_fn=os.setsid, stderr=subprocess.STDOUT, stdout=out)

    while p.poll() is None:
        cputime = _calc_total_cputime(r, tick, redis_key)
        if verbose:
            err.write('cputime: {0}s\n'.format(cputime))
            err.flush()
        if cputime > timeout:
            os.killpg(p.pid, signal.SIGTERM)
            err.write('timeout ({0}s)\n'.format(cputime))
            err.flush()
            timeout = True
            break
        time.sleep(polling_time)
    else:
        cputime = _calc_total_cputime(r, tick, redis_key)
        err.write('finish ({0}s)\n'.format(cputime))
        err.flush()
        timeout = False
    r.delete(redis_key)
    return timeout


def _start_queue(queue, cmd, timeout, polling_time=1, verbose=False, stdout=None, stderr=None):
    timeout = start(cmd, timeout, polling_time, verbose, stdout, stderr)
    queue.put(timeout)


def start_process(cmd, timeout, polling_time=1, verbose=False, stdout=None, stderr=None):
    """
    Run start method in new Process.
    """
    queue = Queue()
    p = Process(target=_start_queue,
                args=(queue,),
                kwargs=dict(cmd=cmd,
                            timeout=timeout,
                            polling_time=polling_time,
                            verbose=verbose,
                            stdout=stdout,
                            stderr=stderr))
    p.start()
    timeout = queue.get()
    p.join()
    return timeout
