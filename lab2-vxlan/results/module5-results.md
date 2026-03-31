mininet> h1 ping -c 3 10.0.0.2

PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=3.55 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.147 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.191 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2035ms
rtt min/avg/max/mdev = 0.147/1.294/3.545/1.591 ms

mininet> h3 ping -c 3 10.0.0.2

PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=1.91 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.076 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.102 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2033ms
rtt min/avg/max/mdev = 0.076/0.697/1.914/0.860 ms

mininet> h1 arp -n

Address HWtype HWaddress Flags Mask Iface
10.0.0.2 ether 00:00:00:00:01:02 C h1-eth0
mininet> h3 arp -n
Address HWtype HWaddress Flags Mask Iface
10.0.0.2 ether 00:00:00:00:02:02 C h3-eth0

mininet> sh ovs-appctl fdb/show s1a

port VLAN MAC Age
2 0 00:00:00:00:01:02 23
1 0 00:00:00:00:01:01 20
2 0 02:ca:81:ff:ec:46 20
LOCAL 0 5e:b7:48:86:da:49 19

mininet> sh ovs-appctl fdb/show s1b

port VLAN MAC Age
2 0 00:00:00:00:02:02 6
1 0 00:00:00:00:02:01 1
mininet>
