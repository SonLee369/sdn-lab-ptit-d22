son@son-SDN-VM:~/lab3-sdn$ sudo python3 topo.py
[sudo] password for son:
**_ Khởi tạo topology Star (1 switch, 4 hosts)
_** Kết nối Ryu RemoteController tại 127.0.0.1:6633
**_ Creating network
_** Adding hosts:
h1 h2 h3 h4
**_ Adding switches:
s1
_** Adding links:
(10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss) (h1, s1) (10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss) (h2, s1) (10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss) (h3, s1) (10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss) (h4, s1)
**_ Configuring hosts
h1 h2 h3 h4
_** Khởi động mạng
**_ Starting controller
ryu
_** Starting 1 switches
s1 ...(10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss) (10.00Mbit 5ms delay 0.00000% loss)
\*\*\* Cấu hình OVS switch: OpenFlow 1.3

=== THÔNG TIN TOPOLOGY ===
Switch : s1
Host : h1 IP=10.0.0.1 MAC=00:00:00:00:00:01
Host : h2 IP=10.0.0.2 MAC=00:00:00:00:00:02
Host : h3 IP=10.0.0.3 MAC=00:00:00:00:00:03
Host : h4 IP=10.0.0.4 MAC=00:00:00:00:00:04
==========================

**_ Mở Mininet CLI (gõ "exit" để thoát)
_** Starting CLI:
mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s1-eth3
h4 h4-eth0:s1-eth4
s1 lo: s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:h3-eth0 s1-eth4:h4-eth0
ryu
mininet> nodes
available nodes are:
h1 h2 h3 h4 ryu s1
mininet> dump
<Host h1: h1-eth0:10.0.0.1 pid=13289>
<Host h2: h2-eth0:10.0.0.2 pid=13291>
<Host h3: h3-eth0:10.0.0.3 pid=13293>
<Host h4: h4-eth0:10.0.0.4 pid=13295>
<OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None,s1-eth3:None,s1-eth4:None pid=13300>
<RemoteController ryu: 127.0.0.1:6633 pid=13454>
mininet> pingall
**_ Ping: testing ping reachability
h1 -> h2 h3 h4
h2 -> h1 h3 h4
h3 -> h1 h2 h4
h4 -> h1 h2 h3
_** Results: 0% dropped (12/12 received)
mininet> h1 ping h4 -c 10
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
From 10.0.0.1 icmp_seq=10 Destination Host Unreachable

--- 10.0.0.4 ping statistics ---
10 packets transmitted, 0 received, +1 errors, 100% packet loss, time 9211ms

mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
mininet> sh ovs-ofctl -O OpenFlow13 show s1
OFPT_FEATURES_REPLY (OF1.3) (xid=0x2): dpid:0000000000000001
n_tables:254, n_buffers:0
capabilities: FLOW_STATS TABLE_STATS PORT_STATS GROUP_STATS QUEUE_STATS
OFPST_PORT_DESC reply (OF1.3) (xid=0x3):
1(s1-eth1): addr:76:e4:60:33:05:fe
config: 0
state: LIVE
current: 10GB-FD COPPER
speed: 10000 Mbps now, 0 Mbps max
2(s1-eth2): addr:36:c6:03:70:34:d2
config: 0
state: LIVE
current: 10GB-FD COPPER
speed: 10000 Mbps now, 0 Mbps max
3(s1-eth3): addr:4e:cf:37:2e:10:37
config: 0
state: LIVE
current: 10GB-FD COPPER
speed: 10000 Mbps now, 0 Mbps max
4(s1-eth4): addr:72:e5:54:19:29:cc
config: 0
state: LIVE
current: 10GB-FD COPPER
speed: 10000 Mbps now, 0 Mbps max
LOCAL(s1): addr:ca:83:82:36:20:43
config: PORT_DOWN
state: LINK_DOWN
speed: 0 Mbps now, 0 Mbps max
OFPT_GET_CONFIG_REPLY (OF1.3) (xid=0x9): frags=normal miss_send_len=0
mininet>
