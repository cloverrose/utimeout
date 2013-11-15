utimeout
========

Run command with CPU time (user time + system time) sense timeout.

 - dose not kill child process when child process is sleeping.
   - ```python demo.py sleepchild```


*u* means LTL's *Until* operator.


Install
-------

utimeout use redis.

```
sudo apt-get install redis-server redis-doc
pip install redis
```


```pip install git+https://github.com/cloverrose/utimeout.git```


How to use
----------

replace ```from subprocess import Popen``` into ```from utimeout import Popen```.



Implementation
--------------

- polling /proc/pid/stat files.
  - inotify cannot use because /proc/pid/stat is pseudo file.
- use redis to store process ids.
  - store process id when process start in utimeout.Popen.
  - remove process id when /proc/pid/stat was deleted.
  - because redis_key is generated by uuid.uuid4(), you can run utimeout.start concurrently.


DEMO
----

```
cd sample
gcc fib.c -o fib
python demo.py sleepchild
python demo.py fibwrapper
python dmeo.py fibonacci
```