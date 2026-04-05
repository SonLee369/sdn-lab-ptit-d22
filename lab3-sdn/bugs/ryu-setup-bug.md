son@son-SDN-VM:~$ sudo apt install -y python3 python3-pip python3-dev libffi-dev libssl-dev gcc
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
python3 is already the newest version (3.12.3-0ubuntu2.1).
python3-pip is already the newest version (24.0+dfsg-1ubuntu1.3).
python3-dev is already the newest version (3.12.3-0ubuntu2.1).
libffi-dev is already the newest version (3.4.6-1build1).
libssl-dev is already the newest version (3.0.13-0ubuntu3.7).
gcc is already the newest version (4:13.2.0-7ubuntu1).
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.

son@son-SDN-VM:~$ pip3 install ryu
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: ryu in ./.local/lib/python3.12/site-packages (4.34)
Requirement already satisfied: eventlet==0.31.1 in ./.local/lib/python3.12/site-packages (from ryu) (0.31.1)
Requirement already satisfied: msgpack>=0.4.0 in ./.local/lib/python3.12/site-packages (from ryu) (1.1.2)
Requirement already satisfied: netaddr in /usr/lib/python3/dist-packages (from ryu) (0.8.0)
Requirement already satisfied: oslo.config>=2.5.0 in ./.local/lib/python3.12/site-packages (from ryu) (10.3.0)
Requirement already satisfied: ovs>=2.6.0 in /usr/lib/python3/dist-packages (from ryu) (3.3.4)
Requirement already satisfied: packaging==20.9 in ./.local/lib/python3.12/site-packages (from ryu) (20.9)
Requirement already satisfied: routes in /usr/lib/python3/dist-packages (from ryu) (2.5.1)
Requirement already satisfied: six>=1.4.0 in /usr/lib/python3/dist-packages (from ryu) (1.16.0)
Requirement already satisfied: tinyrpc==1.0.4 in ./.local/lib/python3.12/site-packages (from ryu) (1.0.4)
Requirement already satisfied: webob>=1.2 in /usr/lib/python3/dist-packages (from ryu) (1.8.7)
Requirement already satisfied: dnspython<2.0.0,>=1.15.0 in ./.local/lib/python3.12/site-packages (from eventlet==0.31.1->ryu) (1.16.0)
Requirement already satisfied: greenlet>=0.3 in /usr/lib/python3/dist-packages (from eventlet==0.31.1->ryu) (3.0.3)
Requirement already satisfied: pyparsing>=2.0.2 in /usr/lib/python3/dist-packages (from packaging==20.9->ryu) (3.1.1)
Requirement already satisfied: stevedore>=5.6.0 in ./.local/lib/python3.12/site-packages (from oslo.config>=2.5.0->ryu) (5.7.0)
Requirement already satisfied: oslo.i18n>=3.15.3 in ./.local/lib/python3.12/site-packages (from oslo.config>=2.5.0->ryu) (6.7.2)
Requirement already satisfied: rfc3986>=1.2.0 in ./.local/lib/python3.12/site-packages (from oslo.config>=2.5.0->ryu) (2.0.0)
Requirement already satisfied: PyYAML>=5.1 in /usr/lib/python3/dist-packages (from oslo.config>=2.5.0->ryu) (6.0.1)
Requirement already satisfied: requests>=2.18.0 in /usr/lib/python3/dist-packages (from oslo.config>=2.5.0->ryu) (2.31.0)
Requirement already satisfied: pbr>=2.0.0 in ./.local/lib/python3.12/site-packages (from oslo.i18n>=3.15.3->oslo.config>=2.5.0->ryu) (7.0.3)
Requirement already satisfied: setuptools in ./.local/lib/python3.12/site-packages (from pbr>=2.0.0->oslo.i18n>=3.15.3->oslo.config>=2.5.0->ryu) (67.6.1)

son@son-SDN-VM:~$ ryu-manager --version
ryu-manager: command not found
son@son-SDN-VM:~$
