son@son-SDN-VM:~/lab3-sdn$ sudo python3 topo.py
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

mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
cookie=0x0, duration=9.476s, table=0, n_packets=23, n_bytes=1954, priority=0 actions=CONTROLLER:65535

mininet> pingall
**_ Ping: testing ping reachability
h1 -> h2 h3 h4
h2 -> h1 h3 h4
h3 -> h1 h2 h4
h4 -> h1 h2 h3
_** Results: 0% dropped (12/12 received)

mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
cookie=0x0, duration=18.245s, table=0, n_packets=3, n_bytes=238, priority=1,in_port="s1-eth2",dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01 actions=output:"s1-eth1"
cookie=0x0, duration=18.230s, table=0, n_packets=2, n_bytes=140, priority=1,in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02 actions=output:"s1-eth2"
cookie=0x0, duration=18.180s, table=0, n_packets=3, n_bytes=238, priority=1,in_port="s1-eth3",dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:01 actions=output:"s1-eth1"
cookie=0x0, duration=18.165s, table=0, n_packets=2, n_bytes=140, priority=1,in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:03 actions=output:"s1-eth3"
cookie=0x0, duration=18.122s, table=0, n_packets=3, n_bytes=238, priority=1,in_port="s1-eth4",dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01 actions=output:"s1-eth1"
cookie=0x0, duration=18.106s, table=0, n_packets=2, n_bytes=140, priority=1,in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:04 actions=output:"s1-eth4"
cookie=0x0, duration=18.029s, table=0, n_packets=3, n_bytes=238, priority=1,in_port="s1-eth3",dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:02 actions=output:"s1-eth2"
cookie=0x0, duration=18.014s, table=0, n_packets=2, n_bytes=140, priority=1,in_port="s1-eth2",dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:03 actions=output:"s1-eth3"
cookie=0x0, duration=17.961s, table=0, n_packets=3, n_bytes=238, priority=1,in_port="s1-eth4",dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:02 actions=output:"s1-eth2"
cookie=0x0, duration=17.948s, table=0, n_packets=2, n_bytes=140, priority=1,in_port="s1-eth2",dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:04 actions=output:"s1-eth4"
cookie=0x0, duration=17.845s, table=0, n_packets=3, n_bytes=238, priority=1,in_port="s1-eth4",dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:03 actions=output:"s1-eth3"
cookie=0x0, duration=17.831s, table=0, n_packets=2, n_bytes=140, priority=1,in_port="s1-eth3",dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:04 actions=output:"s1-eth4"
cookie=0x0, duration=41.433s, table=0, n_packets=49, n_bytes=3606, priority=0 actions=CONTROLLER:65535

mininet> h1 ping h4 -c 10
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=22.6 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=21.6 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=22.9 ms
64 bytes from 10.0.0.4: icmp_seq=4 ttl=64 time=22.7 ms
64 bytes from 10.0.0.4: icmp_seq=5 ttl=64 time=22.3 ms
64 bytes from 10.0.0.4: icmp_seq=6 ttl=64 time=21.7 ms
64 bytes from 10.0.0.4: icmp_seq=7 ttl=64 time=22.0 ms
64 bytes from 10.0.0.4: icmp_seq=8 ttl=64 time=21.6 ms
64 bytes from 10.0.0.4: icmp_seq=9 ttl=64 time=22.5 ms
64 bytes from 10.0.0.4: icmp_seq=10 ttl=64 time=22.1 ms

--- 10.0.0.4 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9011ms
rtt min/avg/max/mdev = 21.641/22.215/22.910/0.445 ms
mininet>
