mininet> sh bash capture.sh

━━━ Tiền kiểm tra — Tìm namespace của h1 ━━━
[OK] Phương pháp 2: nsenter PID=16167
Kiểm tra overlay ping từ h1...
[OK] h1 → h2 ping OK — bắt đầu capture

━━━ BƯỚC 1: Bắt VXLAN trên underlay interface (s1-eth2) ━━━
Interface s1-eth2: UP
IP: 10.0.0.1/24
Lọc: UDP port 4789
tcpdump đã khởi động (PID=16940)
Đang ping 5 gói từ namespace h1 (interval=0.8s)...
PING 192.168.100.2 (192.168.100.2) 56(84) bytes of data.
64 bytes from 192.168.100.2: icmp_seq=1 ttl=64 time=0.080 ms
64 bytes from 192.168.100.2: icmp_seq=2 ttl=64 time=0.076 ms
64 bytes from 192.168.100.2: icmp_seq=3 ttl=64 time=0.095 ms
64 bytes from 192.168.100.2: icmp_seq=4 ttl=64 time=0.152 ms
64 bytes from 192.168.100.2: icmp_seq=5 ttl=64 time=0.086 ms

--- 192.168.100.2 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 3308ms
rtt min/avg/max/mdev = 0.076/0.097/0.152/0.027 ms
tcpdump stderr: tcpdump: listening on s1-eth2, link-type EN10MB (Ethernet), snapshot length 262144 bytes
0 packets captured
0 packets received by filter
0 packets dropped by kernel
[ERROR] BƯỚC 1 FAIL: underlay.pcap trống (24 bytes). Xem stderr ở trên.
mininet>
