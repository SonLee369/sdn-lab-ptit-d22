mininet> sh ovs-vsctl list interface vxlan0

\_uuid : 5a834c0a-4743-49e9-88d0-8ce30efce155
admin\*state : up
bfd : {}
bfd_status : {}
cfm_fault : []
cfm_fault_status : []
cfm_flap_count : []
cfm_health : []
cfm_mpid : []
cfm_remote_mpids : []
cfm_remote_opstate : []
duplex : []
error : []
external_ids : {}
ifindex : 5
ingress_policing_burst: 0
ingress_policing_kpkts_burst: 0
ingress_policing_kpkts_rate: 0
ingress_policing_rate: 0
lacp_current : []
link_resets : 0
link_speed : []
link_state : up
lldp : {}
mac : []
mac_in_use : "ce:3e:a0:35:b2:19"
mtu : []
mtu_request : []
name : vxlan0
ofport : 4
ofport_request : []
options : {dst_port="4789", key="100", local_ip="10.0.0.1", remote_ip="10.0.0.2"}
other_config : {}
statistics : {rx_bytes=1642031049, rx_packets=21985790, tx_bytes=1521508888, tx_packets=20268806}
status : {tunnel_egress_iface=s2, tunnel_egress_iface_carrier=up}
type : vxlan

mininet> ovs-ofctl dump-flows s1

\*\*\* Unknown command: ovs-ofctl dump-flows s1

mininet> sh ovs-ofctl dump-flows s1

cookie=0x0, duration=414.190s, table=0, n_packets=49636512, n_bytes=3751102786, priority=0 actions=NORMAL

mininet> sh ovs-ofctl dump-flows s2

cookie=0x0, duration=446.910s, table=0, n_packets=58074165, n_bytes=4422883158, priority=0 actions=NORMAL

mininet> sh ping -c 3 10.0.0.2

PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=6.06 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=2.06 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=2.04 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2018ms
rtt min/avg/max/mdev = 2.035/3.382/6.057/1.891 ms

mininet> h1 ifconfig

h1-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500
inet 192.168.100.1 netmask 255.255.255.0 broadcast 192.168.100.255
inet6 fe80::8cc9:d5ff:fe44:612f prefixlen 64 scopeid 0x20<link>
ether 8e:c9:d5:44:61:2f txqueuelen 1000 (Ethernet)
RX packets 177276152 bytes 13862132503 (13.8 GB)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 13 bytes 1006 (1.0 KB)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING> mtu 65536
inet 127.0.0.1 netmask 255.0.0.0
inet6 ::1 prefixlen 128 scopeid 0x10<host>
loop txqueuelen 1000 (Local Loopback)
RX packets 0 bytes 0 (0.0 B)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 0 bytes 0 (0.0 B)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

mininet> h2 ifconfig

h2-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500
inet 192.168.100.2 netmask 255.255.255.0 broadcast 192.168.100.255
inet6 fe80::ccff:f4ff:fe1f:565b prefixlen 64 scopeid 0x20<link>
ether ce:ff:f4:1f:56:5b txqueuelen 1000 (Ethernet)
RX packets 187870993 bytes 14690581032 (14.6 GB)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 13 bytes 1006 (1.0 KB)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING> mtu 65536
inet 127.0.0.1 netmask 255.0.0.0
inet6 ::1 prefixlen 128 scopeid 0x10<host>
loop txqueuelen 1000 (Local Loopback)
RX packets 0 bytes 0 (0.0 B)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 0 bytes 0 (0.0 B)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

mininet> h1 ping -c 5 192.168.100.2

PING 192.168.100.2 (192.168.100.2) 56(84) bytes of data.

--- 192.168.100.2 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 4108ms

mininet> h2 ping -c 3 192.168.100.1

PING 192.168.100.1 (192.168.100.1) 56(84) bytes of data.

--- 192.168.100.1 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2059ms

mininet> h1 ping -c 5 192.168.100.2

PING 192.168.100.2 (192.168.100.2) 56(84) bytes of data.

--- 192.168.100.2 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 4147ms

mininet> pingall

**_ Ping: testing ping reachability
h1 -> X
h2 -> X
_** Results: 100% dropped (0/2 received)

mininet> sh ping 10.0.0.2

PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=10.2 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=3.06 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=2.61 ms
64 bytes from 10.0.0.2: icmp_seq=4 ttl=64 time=6.28 ms
64 bytes from 10.0.0.2: icmp_seq=5 ttl=64 time=2.51 ms
64 bytes from 10.0.0.2: icmp_seq=6 ttl=64 time=2.45 ms
64 bytes from 10.0.0.2: icmp_seq=7 ttl=64 time=2.58 ms
64 bytes from 10.0.0.2: icmp_seq=8 ttl=64 time=3.04 ms
^C
--- 10.0.0.2 ping statistics ---
8 packets transmitted, 8 received, 0% packet loss, time 7015ms
rtt min/avg/max/mdev = 2.451/4.091/10.220/2.602 ms

Interrupt

mininet> sh ovs-vsctl show

68aa1f77-4cfe-4e4f-b81b-5d4e2d367764
Bridge s2
fail_mode: standalone
Port s2-eth2
Interface s2-eth2
Port vxlan1
Interface vxlan1
type: vxlan
options: {dst_port="4789", key="100", local_ip="10.0.0.2", remote_ip="10.0.0.1"}
Port s2-eth1
Interface s2-eth1
Port s2
Interface s2
type: internal
Bridge s2b
fail_mode: standalone
Port s2b-eth1
Interface s2b-eth1
error: "could not open network device s2b-eth1 (No such device)"
Port s2b
Interface s2b
type: internal
Port v200s2
Interface v200s2
type: vxlan
options: {dst_port="4789", key="200", local_ip="192.168.1.2", remote_ip="192.168.1.1"}
Bridge s1a
fail_mode: standalone
Port v100s1
Interface v100s1
type: vxlan
options: {dst_port="4789", key="100", local_ip="192.168.1.1", remote_ip="192.168.1.2"}
Port s1a
Interface s1a
type: internal
Port s1a-eth1
Interface s1a-eth1
error: "could not open network device s1a-eth1 (No such device)"
Bridge s1b
fail_mode: standalone
Port s1b-eth1
Interface s1b-eth1
error: "could not open network device s1b-eth1 (No such device)"
Port s1b
Interface s1b
type: internal
Port v200s1
Interface v200s1
type: vxlan
options: {dst_port="4789", key="200", local_ip="192.168.1.1", remote_ip="192.168.1.2"}
Bridge s1
fail_mode: standalone
Port s1-eth1
Interface s1-eth1
Port vxlan0
Interface vxlan0
type: vxlan
options: {dst_port="4789", key="100", local_ip="10.0.0.1", remote_ip="10.0.0.2"}
Port s1-eth2
Interface s1-eth2
Port s1
Interface s1
type: internal
Bridge s2a
fail_mode: standalone
Port s2a
Interface s2a
type: internal
Port s2a-eth1
Interface s2a-eth1
error: "could not open network device s2a-eth1 (No such device)"
Port v100s2
Interface v100s2
type: vxlan
options: {dst_port="4789", key="100", local_ip="192.168.1.2", remote_ip="192.168.1.1"}
ovs_version: "3.3.4"

mininet> h1 ifconfig

h1-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500
inet 192.168.100.1 netmask 255.255.255.0 broadcast 192.168.100.255
inet6 fe80::8cc9:d5ff:fe44:612f prefixlen 64 scopeid 0x20<link>
ether 8e:c9:d5:44:61:2f txqueuelen 1000 (Ethernet)
RX packets 242370113 bytes 18883001450 (18.8 GB)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 31 bytes 2350 (2.3 KB)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING> mtu 65536
inet 127.0.0.1 netmask 255.0.0.0
inet6 ::1 prefixlen 128 scopeid 0x10<host>
loop txqueuelen 1000 (Local Loopback)
RX packets 1 bytes 112 (112.0 B)
RX errors 0 dropped 0 overruns 0 frame 0
TX packets 1 bytes 112 (112.0 B)
TX errors 0 dropped 0 overruns 0 carrier 0 collisions 0

mininet> sh ovs-ofctl dump-flows s1

cookie=0x0, duration=1346.773s, table=0, n_packets=253830350, n_bytes=19661626755, priority=0 actions=NORMAL

\*mininet> sh ovs-appctl fdb/show s1
port VLAN MAC Age
4 0 92:f0:9a:7a:d5:13 0
2 0 02:41:b6:49:b6:d1 0
2 0 2a:67:1c:8a:7f:43 0
4 0 8e:c9:d5:44:61:2f 0
2 0 ce:ff:f4:1f:56:5b 0
4 0 ba:b5:1a:22:e9:41 0

mininet>
