# -*- coding:utf-8 -*-
import subprocess
import os
import sys
import signal
import time
import os.path
import uuid
import redis


def Popen(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0):
    p = subprocess.Popen(args, bufsize, executable, stdin, stdout, stderr, preexec_fn, close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags)
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.sadd(os.getenv('redis_key'), str(p.pid))
    return p


def _get_tick():
    return os.sysconf(os.sysconf_names['SC_CLK_TCK'])


def _parse_utime(pid):
    try:
        with open('/proc/{0}/stat'.format(pid)) as f:
            return int(f.readline().strip('\n').split()[13])
    except IOError as e:
        return None


def _calc_total_usertime(r, tick, redis_key):
    running_child_usertime = 0
    remove_pids = set()
    for pid in r.smembers(redis_key):
        ipid = int(pid)
        utime = _parse_utime(ipid)
        if utime is None:
            remove_pids.add(pid)
        else:
            running_child_usertime += utime
    for pid in remove_pids:
        r.srem(redis_key, pid)
    running_child_usertime = running_child_usertime / tick
    times = os.times()
    return running_child_usertime + times[0] + times[2]


def start(cmd, timeout, polling_time=1, verbose=False):
    """
    if timeout return True,
    if finish return False.
    """
    redis_key = uuid.uuid4().hex
    os.environ['redis_key'] = redis_key

    tick = _get_tick()
    if verbose:
        sys.stderr.write('tick: {0}\n'.format(tick))
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete(redis_key)

    p = Popen(cmd, preexec_fn=os.setsid, stderr=subprocess.STDOUT)

    while p.poll() is None:
        utime = _calc_total_usertime(r, tick, redis_key)
        if verbose:
            sys.stderr.write('utime: {0}s\n'.format(utime))
        if utime > timeout:
            os.killpg(p.pid, signal.SIGTERM)
            sys.stderr.write('timeout ({0}s)\n'.format(utime))
            timeout = True
            break
        time.sleep(polling_time)
    else:
        utime = _calc_total_usertime(r, tick, redis_key)
        sys.stderr.write('finish ({0}s)\n'.format(utime))
        timeout = False
    r.delete(redis_key)
    return timeout
