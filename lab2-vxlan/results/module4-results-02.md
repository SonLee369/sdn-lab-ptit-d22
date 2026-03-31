mininet> h2 ping -c 3 10.0.0.1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
From 10.0.0.2 icmp_seq=1 Destination Host Unreachable
From 10.0.0.2 icmp_seq=2 Destination Host Unreachable
From 10.0.0.2 icmp_seq=3 Destination Host Unreachable

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2053ms
pipe 3

mininet> h2 ping -c 3 10.0.0.1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
From 10.0.0.2 icmp_seq=1 Destination Host Unreachable
From 10.0.0.2 icmp_seq=2 Destination Host Unreachable
From 10.0.0.2 icmp_seq=3 Destination Host Unreachable

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2063ms
pipe 3
mininet> h1 arp -n
Address HWtype HWaddress Flags Mask Iface
10.0.0.2 (incomplete) h1-eth0

mininet> sh ovs-appctl fdb/show s1
port VLAN MAC Age
3 0 00:00:00:00:00:01 13

mininet> sh tcpdump -i s1-eth2 -n udp port 4789
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on s1-eth2, link-type EN10MB (Ethernet), snapshot length 262144 bytes
^C
0 packets captured
0 packets received by filter
0 packets dropped by kernel

Interrupt
mininet>
