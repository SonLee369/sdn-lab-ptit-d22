mininet> sh ip addr show dev s1
51: s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
link/ether c2:09:07:68:94:46 brd ff:ff:ff:ff:ff:ff
inet 192.168.1.1/30 scope global s1
valid_lft forever preferred_lft forever
inet6 fe80::c009:7ff:fe68:9446/64 scope link
valid_lft forever preferred_lft forever
mininet> sh ping -c 3 192.168.1.1
PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.086 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.164 ms
64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0.091 ms

--- 192.168.1.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2087ms
rtt min/avg/max/mdev = 0.086/0.113/0.164/0.035 ms
mininet> sh ovs-vsctl show
68aa1f77-4cfe-4e4f-b81b-5d4e2d367764
Bridge s1
fail_mode: standalone
Port s1-eth2
Interface s1-eth2
Port s1-eth1
Interface s1-eth1
Port s1
Interface s1
type: internal
Bridge s2
fail_mode: standalone
Port s2-eth1
Interface s2-eth1
Port s2-eth2
Interface s2-eth2
Port s2
Interface s2
type: internal
ovs_version: "3.3.4"
mininet>

**_ Adiction Cheking_**

mininet> sh ip addr show dev s2
52: s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
link/ether 12:69:16:e0:1a:45 brd ff:ff:ff:ff:ff:ff
inet 192.168.1.2/30 scope global s2
valid_lft forever preferred_lft forever
inet6 fe80::1069:16ff:fee0:1a45/64 scope link
valid_lft forever preferred_lft forever
mininet> sh ping -c 3 192.168.1.2
PING 192.168.1.2 (192.168.1.2) 56(84) bytes of data.
64 bytes from 192.168.1.2: icmp_seq=1 ttl=64 time=0.073 ms
64 bytes from 192.168.1.2: icmp_seq=2 ttl=64 time=0.571 ms
64 bytes from 192.168.1.2: icmp_seq=3 ttl=64 time=0.084 ms

--- 192.168.1.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2034ms
rtt min/avg/max/mdev = 0.073/0.242/0.571/0.232 ms
mininet>
