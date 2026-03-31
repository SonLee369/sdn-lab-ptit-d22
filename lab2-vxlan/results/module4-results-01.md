mininet> h2 ping -c 3 10.0.0.1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
--- 10.0.0.1 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2057ms

mininet> h1 arp -n
Address HWtype HWaddress Flags Mask Iface
10.0.0.2 ether 00:00:00:00:00:02 C h1-eth0

mininet> sh tcpdump -i s1-eth2 -n udp port 4789 -c 5
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on s1-eth2, link-type EN10MB (Ethernet), snapshot length 262144 bytes
^C
0 packets captured
13680 packets received by filter
1794 packets dropped by kernel

Interrupt
mininet> sh ovs-appctl fdb/show s1
port VLAN MAC Age
3 0 00:00:00:00:00:02 0
2 0 32:1f:93:96:5b:47 0
3 0 b6:14:58:a3:da:0a 0
3 0 f6:f9:10:75:d8:4f 0
2 0 6a:47:28:8e:ca:33 0
3 0 00:00:00:00:00:01 0
mininet>
