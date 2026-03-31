mininet> h1 ping -c 3 10.0.0.2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.767 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.136 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.076 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2038ms
rtt min/avg/max/mdev = 0.076/0.326/0.767/0.312 ms

mininet> h2 ping -c 3 10.0.0.1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=1.42 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=0.073 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=0.095 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2063ms
rtt min/avg/max/mdev = 0.073/0.528/1.416/0.627 ms

mininet> h1 arp -n
Address HWtype HWaddress Flags Mask Iface
10.0.0.2 ether 00:00:00:00:00:02 C h1-eth0

mininet> sh ovs-appctl fdb/show s1
port VLAN MAC Age
LOCAL 0 ee:15:76:fb:99:4a 26
3 0 2e:17:6d:b4:39:4d 25
3 0 00:00:00:00:00:02 8
1 0 00:00:00:00:00:01 8

mininet> sh tcpdump -i s1-eth2 -n udp port 4789 -c 5
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on s1-eth2, link-type EN10MB (Ethernet), snapshot length 262144 bytes
^C
0 packets captured
0 packets received by filter
0 packets dropped by kernel
Interrupt

mininet>
