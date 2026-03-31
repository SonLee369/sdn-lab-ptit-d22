mininet> sh bash capture.sh

━━━ Tiền kiểm tra — Tìm namespace của h1 ━━━
[OK] Phương pháp 2: nsenter PID=16167
Kiểm tra overlay ping từ h1...
[OK] h1 → h2 ping OK — bắt đầu capture

━━━ BƯỚC 1: Bắt VXLAN trên underlay interface (any) ━━━
Capture interface: any (bắt toàn bộ interfaces trong root namespace)
Underlay s1-eth2: UP — IP: 10.0.0.1/24
Lọc: UDP port 4789
tcpdump đã khởi động (PID=17293)
Đang ping 5 gói từ namespace h1 (interval=0.8s)...
PING 192.168.100.2 (192.168.100.2) 56(84) bytes of data.
64 bytes from 192.168.100.2: icmp_seq=1 ttl=64 time=0.897 ms
64 bytes from 192.168.100.2: icmp_seq=2 ttl=64 time=0.158 ms
64 bytes from 192.168.100.2: icmp_seq=3 ttl=64 time=0.352 ms
64 bytes from 192.168.100.2: icmp_seq=4 ttl=64 time=0.174 ms
64 bytes from 192.168.100.2: icmp_seq=5 ttl=64 time=0.114 ms

--- 192.168.100.2 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 3339ms
rtt min/avg/max/mdev = 0.114/0.339/0.897/0.290 ms
[OK] Đã bắt gói → /tmp/vxlan_cap/underlay.pcap (1724 bytes)

━━━ BƯỚC 2: Bắt ICMP gốc trên overlay interface (h1-eth0) ━━━
Lọc: ICMP | h1-eth0 ở namespace h1 → dùng h1_exec
tcpdump overlay đã khởi động (PID=17305)
[OK] Đã bắt gói → /tmp/vxlan_cap/overlay.pcap (1164 bytes)

━━━ BƯỚC 3: Phân tích gói VXLAN trên underlay ━━━

[3a] Tóm tắt (tcpdump -r):
──────────────────────────────────────────────────────
10:31:37.697828 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 1, length 64
10:31:37.698080 lo In IP 10.0.0.2.41080 > 10.0.0.1.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 1, length 64
10:31:38.540920 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 2, length 64
10:31:38.540979 lo In IP 10.0.0.2.41080 > 10.0.0.1.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 2, length 64
10:31:39.373241 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 3, length 64
10:31:39.373452 lo In IP 10.0.0.2.41080 > 10.0.0.1.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 3, length 64
10:31:40.204610 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 4, length 64
10:31:40.204678 lo In IP 10.0.0.2.41080 > 10.0.0.1.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 4, length 64
10:31:41.036452 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 5, length 64
10:31:41.036491 lo In IP 10.0.0.2.41080 > 10.0.0.1.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 5, length 64

[3b] Verbose -vvv (2 gói đầu):
──────────────────────────────────────────────────────
10:31:37.697828 lo In IP (tos 0x0, ttl 64, id 9915, offset 0, flags [DF], proto UDP (17), length 134)
10.0.0.1.41080 > 10.0.0.2.4789: [no cksum] VXLAN, flags [I] (0x08), vni 100
IP (tos 0x0, ttl 64, id 13205, offset 0, flags [DF], proto ICMP (1), length 84)
192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 1, length 64
10:31:37.698080 lo In IP (tos 0x0, ttl 64, id 28453, offset 0, flags [DF], proto UDP (17), length 134)
10.0.0.2.41080 > 10.0.0.1.4789: [no cksum] VXLAN, flags [I] (0x08), vni 100
IP (tos 0x0, ttl 64, id 10902, offset 0, flags [none], proto ICMP (1), length 84)
192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 1, length 64

━━━ BƯỚC 4: Phân tích ICMP gốc trên overlay (h1-eth0) ━━━

10:31:42.864123 IP (tos 0x0, ttl 64, id 16068, offset 0, flags [DF], proto ICMP (1), length 84)
192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 1, length 64
10:31:42.864191 IP (tos 0x0, ttl 64, id 14122, offset 0, flags [none], proto ICMP (1), length 84)
192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 1, length 64
10:31:43.724573 IP (tos 0x0, ttl 64, id 16371, offset 0, flags [DF], proto ICMP (1), length 84)
192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 2, length 64
10:31:43.724686 IP (tos 0x0, ttl 64, id 14469, offset 0, flags [none], proto ICMP (1), length 84)
192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 2, length 64
10:31:44.556657 IP (tos 0x0, ttl 64, id 16643, offset 0, flags [DF], proto ICMP (1), length 84)
192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 3, length 64
10:31:44.556728 IP (tos 0x0, ttl 64, id 14801, offset 0, flags [none], proto ICMP (1), length 84)
192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 3, length 64
10:31:45.389041 IP (tos 0x0, ttl 64, id 16679, offset 0, flags [DF], proto ICMP (1), length 84)
192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 4, length 64
10:31:45.389135 IP (tos 0x0, ttl 64, id 15313, offset 0, flags [none], proto ICMP (1), length 84)
192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 4, length 64
10:31:46.221479 IP (tos 0x0, ttl 64, id 17146, offset 0, flags [DF], proto ICMP (1), length 84)
192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 5, length 64
10:31:46.221625 IP (tos 0x0, ttl 64, id 15617, offset 0, flags [none], proto ICMP (1), length 84)
192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 5, length 64

━━━ BƯỚC 5: So sánh kích thước — Overhead VXLAN ━━━

Gói VXLAN (underlay): 154 bytes
Gói ICMP gốc (overlay): 98 bytes
Overhead VXLAN: 56 bytes

Cấu trúc overhead (lý thuyết = 50 bytes):
Outer Ethernet : 14 bytes
Outer IP : 20 bytes
Outer UDP : 8 bytes
VXLAN header : 8 bytes

━━━ BƯỚC 6: Hex dump — xác minh VNI=100 (0x000064) ━━━

Vị trí VNI: byte 46-48 (sau Outer Eth[14]+IP[20]+UDP[8]+VXLAN flags[4])

10:31:37.697828 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 1, length 64
0x0000: 0800 0000 0000 0001 0304 0006 0000 0000
0x0010: 0000 0000 4500 0086 26bb 4000 4011 ffa9
0x0020: 0a00 0001 0a00 0002 a078 12b5 0072 0000
0x0030: 0800 0000 0000 6400 7e69 bbd2 444d fe7e
0x0040: b898 a0c4 0800 4500 0054 3395 4000 4001
0x0050: bdbf c0a8 6401 c0a8 6402 0800 544c 4390
0x0060: 0001 1940 cb69 0000 0000 b2a5 0a00 0000
0x0070: 0000 1011 1213 1415 1617 1819 1a1b 1c1d
0x0080: 1e1f 2021 2223 2425 2627 2829 2a2b 2c2d
0x0090: 2e2f 3031 3233 3435 3637

━━━ Tổng kết ━━━

File đã lưu:
Underlay (VXLAN) : /tmp/vxlan_cap/underlay.pcap
Overlay (ICMP) : /tmp/vxlan_cap/overlay.pcap

Phân tích thêm:
tshark -r /tmp/vxlan_cap/underlay.pcap
tshark -r /tmp/vxlan_cap/underlay.pcap -V 2>/dev/null | grep -A5 'VXLAN'

Mở Wireshark (từ terminal host, NGOÀI Mininet CLI):
wireshark /tmp/vxlan_cap/underlay.pcap &

mininet>
