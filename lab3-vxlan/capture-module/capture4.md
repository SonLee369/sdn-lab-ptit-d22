mininet> sh bash capture.sh

━━━ Tiền kiểm tra — Tìm namespace của h1 ━━━
[OK] Phương pháp 2: nsenter PID=16167
Kiểm tra overlay ping từ h1...
[OK] h1 → h2 ping OK — bắt đầu capture

━━━ BƯỚC 1: Bắt VXLAN trên underlay interface (any) ━━━
Capture interface: any (bắt toàn bộ interfaces trong root namespace)
Underlay s1-eth2: UP — IP: 10.0.0.1/24
Lọc: UDP port 4789
tcpdump đã khởi động (PID=17202)
Đang ping 5 gói từ namespace h1 (interval=0.8s)...
PING 192.168.100.2 (192.168.100.2) 56(84) bytes of data.
64 bytes from 192.168.100.2: icmp_seq=1 ttl=64 time=0.261 ms
64 bytes from 192.168.100.2: icmp_seq=2 ttl=64 time=0.086 ms
64 bytes from 192.168.100.2: icmp_seq=3 ttl=64 time=0.135 ms
64 bytes from 192.168.100.2: icmp_seq=4 ttl=64 time=0.163 ms
64 bytes from 192.168.100.2: icmp_seq=5 ttl=64 time=0.158 ms

--- 192.168.100.2 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 3319ms
rtt min/avg/max/mdev = 0.086/0.160/0.261/0.057 ms
[OK] Đã bắt gói → /tmp/vxlan_cap/underlay.pcap (1724 bytes)

━━━ BƯỚC 2: Bắt ICMP gốc trên overlay interface (h1-eth0) ━━━
Lọc: ICMP | h1-eth0 ở namespace h1 → dùng h1_exec
tcpdump overlay đã khởi động (PID=17215)
[ERROR] BƯỚC 2 FAIL: overlay.pcap trống. stderr: tcpdump: listening on h1-eth0, link-type EN10MB (Ethernet), snapshot length 262144 bytes
mininet>
