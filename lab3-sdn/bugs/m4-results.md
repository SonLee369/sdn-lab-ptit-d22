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

mininet> pingall
**_ Ping: testing ping reachability
h1 -> h2 h3 h4
h2 -> h1 h3 h4
h3 -> h1 h2 h4
h4 -> h1 h2 h3
_** Results: 0% dropped (12/12 received)

mininet> h4 iperf3 -s -D

mininet> h1 iperf4 -c 10.0.0.4 -t 10 -i 1
bash: iperf4: command not found

mininet> h1 iperf3 -c 10.0.0.4 -t 10 -i 1
Connecting to host 10.0.0.4, port 5201
[ 5] local 10.0.0.1 port 60088 connected to 10.0.0.4 port 5201
[ ID] Interval Transfer Bitrate Retr Cwnd
[ 5] 0.00-1.00 sec 1.75 MBytes 14.7 Mbits/sec 0 175 KBytes  
[ 5] 1.00-2.00 sec 1.62 MBytes 13.6 Mbits/sec 0 235 KBytes  
[ 5] 2.00-3.00 sec 1.12 MBytes 9.43 Mbits/sec 0 293 KBytes  
[ 5] 3.00-4.00 sec 1.25 MBytes 10.5 Mbits/sec 0 351 KBytes  
[ 5] 4.00-5.00 sec 1.62 MBytes 13.6 Mbits/sec 0 409 KBytes  
[ 5] 5.00-6.00 sec 1.75 MBytes 14.7 Mbits/sec 0 468 KBytes  
[ 5] 6.00-7.00 sec 1.00 MBytes 8.38 Mbits/sec 0 526 KBytes  
[ 5] 7.00-8.00 sec 1.12 MBytes 9.44 Mbits/sec 0 584 KBytes  
[ 5] 8.00-9.00 sec 2.38 MBytes 19.9 Mbits/sec 0 643 KBytes  
[ 5] 9.00-10.00 sec 1.38 MBytes 11.5 Mbits/sec 0 701 KBytes

---

[ ID] Interval Transfer Bitrate Retr
[ 5] 0.00-10.00 sec 15.0 MBytes 12.6 Mbits/sec 0 sender
[ 5] 0.00-10.61 sec 12.0 MBytes 9.49 Mbits/sec receiver

iperf Done.

mininet> h4 iperf3 -s -D

mininet> h1 iperf3 -c 10.0.0.4 -u -b 9M -t 10 -i 1
Connecting to host 10.0.0.4, port 5201
[ 5] local 10.0.0.1 port 39857 connected to 10.0.0.4 port 5201
[ ID] Interval Transfer Bitrate Total Datagrams
[ 5] 0.00-1.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 1.00-2.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 2.00-3.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 3.00-4.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 4.00-5.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 5.00-6.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 6.00-7.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 7.00-8.00 sec 1.07 MBytes 8.99 Mbits/sec 776  
[ 5] 8.00-9.00 sec 1.07 MBytes 9.00 Mbits/sec 777  
[ 5] 9.00-10.00 sec 1.07 MBytes 8.99 Mbits/sec 777

---

[ ID] Interval Transfer Bitrate Jitter Lost/Total Datagrams
[ 5] 0.00-10.00 sec 10.7 MBytes 9.00 Mbits/sec 0.000 ms 0/7769 (0%) sender
[ 5] 0.00-10.02 sec 10.7 MBytes 8.98 Mbits/sec 0.352 ms 0/7769 (0%) receiver

iperf Done.

mininet> h4 iperf3 -s -D

mininet> h1 iperf3 -c 10.0.0.4 -t 10 -p 4
iperf3: error - unable to connect to server - server may have stopped running or use a different port, firewall issue, etc.: Connection refused

mininet> h1 iperf3 -c 10.0.0.4 -t 10 -P 4
Connecting to host 10.0.0.4, port 5201
[ 5] local 10.0.0.1 port 58766 connected to 10.0.0.4 port 5201
[ 7] local 10.0.0.1 port 58780 connected to 10.0.0.4 port 5201
[ 9] local 10.0.0.1 port 58796 connected to 10.0.0.4 port 5201
[ 11] local 10.0.0.1 port 58804 connected to 10.0.0.4 port 5201
[ ID] Interval Transfer Bitrate Retr Cwnd
[ 5] 0.00-1.00 sec 640 KBytes 5.24 Mbits/sec 0 65.0 KBytes  
[ 7] 0.00-1.00 sec 640 KBytes 5.24 Mbits/sec 0 63.6 KBytes  
[ 9] 0.00-1.00 sec 512 KBytes 4.19 Mbits/sec 0 63.6 KBytes  
[ 11] 0.00-1.00 sec 384 KBytes 3.14 Mbits/sec 0 60.8 KBytes  
[SUM] 0.00-1.00 sec 2.12 MBytes 17.8 Mbits/sec 0

---

[ 5] 1.00-2.00 sec 384 KBytes 3.15 Mbits/sec 0 77.8 KBytes  
[ 7] 1.00-2.00 sec 384 KBytes 3.15 Mbits/sec 0 77.8 KBytes  
[ 9] 1.00-2.00 sec 256 KBytes 2.10 Mbits/sec 0 76.4 KBytes  
[ 11] 1.00-2.00 sec 384 KBytes 3.15 Mbits/sec 0 77.8 KBytes  
[SUM] 1.00-2.00 sec 1.38 MBytes 11.5 Mbits/sec 0

---

[ 5] 2.00-3.00 sec 384 KBytes 3.15 Mbits/sec 0 94.7 KBytes  
[ 7] 2.00-3.00 sec 128 KBytes 1.05 Mbits/sec 0 90.5 KBytes  
[ 9] 2.00-3.00 sec 384 KBytes 3.15 Mbits/sec 0 93.3 KBytes  
[ 11] 2.00-3.00 sec 384 KBytes 3.15 Mbits/sec 0 90.5 KBytes  
[SUM] 2.00-3.00 sec 1.25 MBytes 10.5 Mbits/sec 0

---

[ 5] 3.00-4.00 sec 256 KBytes 2.10 Mbits/sec 0 110 KBytes  
[ 7] 3.00-4.00 sec 512 KBytes 4.19 Mbits/sec 0 105 KBytes  
[ 9] 3.00-4.00 sec 512 KBytes 4.19 Mbits/sec 0 107 KBytes  
[ 11] 3.00-4.00 sec 512 KBytes 4.19 Mbits/sec 0 105 KBytes  
[SUM] 3.00-4.00 sec 1.75 MBytes 14.7 Mbits/sec 0

---

[ 5] 4.00-5.00 sec 256 KBytes 2.10 Mbits/sec 0 122 KBytes  
[ 7] 4.00-5.00 sec 256 KBytes 2.10 Mbits/sec 0 122 KBytes  
[ 9] 4.00-5.00 sec 256 KBytes 2.10 Mbits/sec 0 122 KBytes  
[ 11] 4.00-5.00 sec 256 KBytes 2.10 Mbits/sec 0 122 KBytes  
[SUM] 4.00-5.00 sec 1.00 MBytes 8.38 Mbits/sec 0

---

[ 5] 5.00-6.00 sec 512 KBytes 4.19 Mbits/sec 0 154 KBytes  
[ 7] 5.00-6.00 sec 512 KBytes 4.19 Mbits/sec 0 140 KBytes  
[ 9] 5.00-6.00 sec 256 KBytes 2.10 Mbits/sec 0 147 KBytes  
[ 11] 5.00-6.00 sec 512 KBytes 4.19 Mbits/sec 0 143 KBytes  
[SUM] 5.00-6.00 sec 1.75 MBytes 14.7 Mbits/sec 0

---

[ 5] 6.00-7.00 sec 384 KBytes 3.15 Mbits/sec 0 201 KBytes  
[ 7] 6.00-7.00 sec 384 KBytes 3.15 Mbits/sec 0 189 KBytes  
[ 9] 6.00-7.00 sec 768 KBytes 6.29 Mbits/sec 0 204 KBytes  
[ 11] 6.00-7.00 sec 384 KBytes 3.15 Mbits/sec 0 198 KBytes  
[SUM] 6.00-7.00 sec 1.88 MBytes 15.7 Mbits/sec 0

---

[ 5] 7.00-8.00 sec 1.00 MBytes 8.39 Mbits/sec 0 272 KBytes  
[ 7] 7.00-8.00 sec 1.00 MBytes 8.39 Mbits/sec 0 284 KBytes  
[ 9] 7.00-8.00 sec 512 KBytes 4.19 Mbits/sec 0 257 KBytes  
[ 11] 7.00-8.00 sec 512 KBytes 4.19 Mbits/sec 0 245 KBytes  
[SUM] 7.00-8.00 sec 3.00 MBytes 25.2 Mbits/sec 0

---

[ 5] 8.00-9.00 sec 768 KBytes 6.30 Mbits/sec 0 351 KBytes  
[ 7] 8.00-9.00 sec 768 KBytes 6.30 Mbits/sec 0 373 KBytes  
[ 9] 8.00-9.00 sec 640 KBytes 5.25 Mbits/sec 0 331 KBytes  
[ 11] 8.00-9.00 sec 640 KBytes 5.25 Mbits/sec 0 345 KBytes  
[SUM] 8.00-9.00 sec 2.75 MBytes 23.1 Mbits/sec 0

---

[ 5] 9.00-10.00 sec 896 KBytes 7.32 Mbits/sec 0 468 KBytes  
[ 7] 9.00-10.00 sec 1.00 MBytes 8.37 Mbits/sec 0 485 KBytes  
[ 9] 9.00-10.00 sec 768 KBytes 6.28 Mbits/sec 0 437 KBytes  
[ 11] 9.00-10.00 sec 768 KBytes 6.28 Mbits/sec 0 409 KBytes  
[SUM] 9.00-10.00 sec 3.38 MBytes 28.2 Mbits/sec 0

---

[ ID] Interval Transfer Bitrate Retr
[ 5] 0.00-10.00 sec 5.38 MBytes 4.51 Mbits/sec 0 sender
[ 5] 0.00-11.55 sec 3.38 MBytes 2.45 Mbits/sec receiver
[ 7] 0.00-10.00 sec 5.50 MBytes 4.61 Mbits/sec 0 sender
[ 7] 0.00-11.55 sec 3.38 MBytes 2.45 Mbits/sec receiver
[ 9] 0.00-10.00 sec 4.75 MBytes 3.98 Mbits/sec 0 sender
[ 9] 0.00-11.55 sec 3.12 MBytes 2.27 Mbits/sec receiver
[ 11] 0.00-10.00 sec 4.62 MBytes 3.88 Mbits/sec 0 sender
[ 11] 0.00-11.55 sec 3.00 MBytes 2.18 Mbits/sec receiver
[SUM] 0.00-10.00 sec 20.2 MBytes 17.0 Mbits/sec 0 sender
[SUM] 0.00-11.55 sec 12.9 MBytes 9.35 Mbits/sec receiver

iperf Done.

mininet> h1 ping h4 -c 20 -i 0.5
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=24.5 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=22.3 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=23.1 ms
64 bytes from 10.0.0.4: icmp_seq=4 ttl=64 time=22.8 ms
64 bytes from 10.0.0.4: icmp_seq=5 ttl=64 time=22.7 ms
64 bytes from 10.0.0.4: icmp_seq=6 ttl=64 time=21.9 ms
64 bytes from 10.0.0.4: icmp_seq=7 ttl=64 time=21.9 ms
64 bytes from 10.0.0.4: icmp_seq=8 ttl=64 time=22.8 ms
64 bytes from 10.0.0.4: icmp_seq=9 ttl=64 time=22.1 ms
64 bytes from 10.0.0.4: icmp_seq=10 ttl=64 time=22.3 ms
64 bytes from 10.0.0.4: icmp_seq=11 ttl=64 time=22.7 ms
64 bytes from 10.0.0.4: icmp_seq=12 ttl=64 time=21.9 ms
64 bytes from 10.0.0.4: icmp_seq=13 ttl=64 time=22.0 ms
64 bytes from 10.0.0.4: icmp_seq=14 ttl=64 time=21.9 ms
64 bytes from 10.0.0.4: icmp_seq=15 ttl=64 time=22.6 ms
64 bytes from 10.0.0.4: icmp_seq=16 ttl=64 time=21.3 ms
64 bytes from 10.0.0.4: icmp_seq=17 ttl=64 time=21.7 ms
64 bytes from 10.0.0.4: icmp_seq=18 ttl=64 time=20.8 ms
64 bytes from 10.0.0.4: icmp_seq=19 ttl=64 time=21.7 ms
64 bytes from 10.0.0.4: icmp_seq=20 ttl=64 time=22.2 ms

--- 10.0.0.4 ping statistics ---
20 packets transmitted, 20 received, 0% packet loss, time 9529ms
rtt min/avg/max/mdev = 20.757/22.251/24.469/0.738 ms

mininet> h1 iperf3 -s -D

mininet> h4 iperf3 -c 10.0.0.1 -t 10 -i 1
Connecting to host 10.0.0.1, port 5201
[ 5] local 10.0.0.4 port 43666 connected to 10.0.0.1 port 5201
[ ID] Interval Transfer Bitrate Retr Cwnd
[ 5] 0.00-1.00 sec 1.75 MBytes 14.7 Mbits/sec 0 175 KBytes  
[ 5] 1.00-2.00 sec 1.62 MBytes 13.6 Mbits/sec 0 235 KBytes  
[ 5] 2.00-3.00 sec 1.12 MBytes 9.45 Mbits/sec 0 293 KBytes  
[ 5] 3.00-4.00 sec 1.25 MBytes 10.5 Mbits/sec 0 351 KBytes  
[ 5] 4.00-5.00 sec 1.62 MBytes 13.6 Mbits/sec 0 409 KBytes  
[ 5] 5.00-6.00 sec 1.75 MBytes 14.7 Mbits/sec 0 468 KBytes  
[ 5] 6.00-7.00 sec 1.00 MBytes 8.38 Mbits/sec 0 526 KBytes  
[ 5] 7.00-8.00 sec 1.12 MBytes 9.44 Mbits/sec 0 584 KBytes  
[ 5] 8.00-9.00 sec 2.38 MBytes 19.9 Mbits/sec 0 643 KBytes  
[ 5] 9.00-10.00 sec 1.38 MBytes 11.5 Mbits/sec 0 701 KBytes

---

[ ID] Interval Transfer Bitrate Retr
[ 5] 0.00-10.00 sec 15.0 MBytes 12.6 Mbits/sec 0 sender
[ 5] 0.00-10.61 sec 12.0 MBytes 9.49 Mbits/sec receiver

iperf Done.
mininet>
