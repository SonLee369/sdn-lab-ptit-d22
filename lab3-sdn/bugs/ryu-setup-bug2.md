son@son-SDN-VM:~$ ls ~/.local/bin/ryu-manager
/home/son/.local/bin/ryu-manager

son@son-SDN-VM:~$ export PATH=$PATH:~/.local/bin

son@son-SDN-VM:~$ ryu-manager --version
Traceback (most recent call last):
File "/home/son/.local/bin/ryu-manager", line 5, in <module>
from ryu.cmd.manager import main
File "/home/son/.local/lib/python3.12/site-packages/ryu/cmd/manager.py", line 22, in <module>
from ryu.lib import hub
File "/home/son/.local/lib/python3.12/site-packages/ryu/lib/hub.py", line 30, in <module>
import eventlet
File "/home/son/.local/lib/python3.12/site-packages/eventlet/**init**.py", line 17, in <module>
from eventlet import convenience
File "/home/son/.local/lib/python3.12/site-packages/eventlet/convenience.py", line 7, in <module>
from eventlet.green import socket
File "/home/son/.local/lib/python3.12/site-packages/eventlet/green/socket.py", line 4, in <module>
**import**('eventlet.green._socket_nodns')
File "/home/son/.local/lib/python3.12/site-packages/eventlet/green/\_socket_nodns.py", line 11, in <module>
from eventlet import greenio
File "/home/son/.local/lib/python3.12/site-packages/eventlet/greenio/**init**.py", line 3, in <module>
from eventlet.greenio.base import \* # noqa
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/son/.local/lib/python3.12/site-packages/eventlet/greenio/base.py", line 32, in <module>
socket_timeout = eventlet.timeout.wrap_is_timeout(socket.timeout)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/son/.local/lib/python3.12/site-packages/eventlet/timeout.py", line 166, in wrap_is_timeout
base.is_timeout = property(lambda _: True)
^^^^^^^^^^^^^^^
TypeError: cannot set 'is_timeout' attribute of immutable type 'TimeoutError'
