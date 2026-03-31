═══════════════════════════════════════════════════════
Lab 3 — Test Module 5: VXLAN Traffic Testing
═══════════════════════════════════════════════════════

Đang khởi động topology...

───────────────────────────────────────────────────────
T1: Kiểm tra VTEP IP trên underlay veth
───────────────────────────────────────────────────────

[PASS] s1-eth2 có IP 10.0.0.1/24
[PASS] s2-eth2 có IP 10.0.0.2/24
[PASS] s1-eth2 không còn trong OVS bridge s1 (không loop)
[PASS] s2-eth2 không còn trong OVS bridge s2 (không loop)

───────────────────────────────────────────────────────

T2: Kiểm tra kết nối underlay (VTEP-to-VTEP)
───────────────────────────────────────────────────────

[PASS] Underlay ping 10.0.0.1 → 10.0.0.2 (4/4 received)
4 packets transmitted, 4 received, 0% packet loss, time 3093ms

───────────────────────────────────────────────────────

T3: Kiểm tra cấu hình VXLAN tunnel trên OVS
───────────────────────────────────────────────────────
[FAIL] vxlan0 tồn tại trên s1 (type=vxlan)
[PASS] vxlan0: local_ip=10.0.0.1
[PASS] vxlan0: remote_ip=10.0.0.2
[PASS] vxlan0: VNI key=100
[PASS] vxlan0: dst_port=4789
[FAIL] vxlan1 tồn tại trên s2 (type=vxlan)
[PASS] vxlan1: local_ip=10.0.0.2
[PASS] vxlan1: remote_ip=10.0.0.1
[PASS] vxlan0 link_state=up (got: up)
[PASS] vxlan1 link_state=up (got: up)

───────────────────────────────────────────────────────

T4: Kiểm tra địa chỉ IP overlay của h1 và h2
───────────────────────────────────────────────────────
[PASS] h1 có IP 192.168.100.1/24
[PASS] h2 có IP 192.168.100.2/24

───────────────────────────────────────────────────────

T5: Overlay ping h1 → h2 (qua VXLAN tunnel)
───────────────────────────────────────────────────────

[PASS] h1 → h2 overlay ping (5/5 received)
5 packets transmitted, 5 received, 0% packet loss, time 4067ms

───────────────────────────────────────────────────────

T6: Overlay ping h2 → h1 (chiều ngược lại)
───────────────────────────────────────────────────────

[PASS] h2 → h1 overlay ping (3/3 received)
3 packets transmitted, 3 received, 0% packet loss, time 2037ms

───────────────────────────────────────────────────────

T7: Kiểm tra ARP table (h1 đã học MAC của h2)
───────────────────────────────────────────────────────

[PASS] h1 ARP table có entry cho 192.168.100.2
[PASS] ARP entry đúng MAC của h2 (86:fa:12:ca:5d:36)
Address HWtype HWaddress Flags Mask Iface
192.168.100.2 ether 86:fa:12:ca:5d:36 C h1-eth0

───────────────────────────────────────────────────────

T8: Kiểm tra MAC learning — FDB của s1
───────────────────────────────────────────────────────

[PASS] FDB s1 chứa MAC của h1 (46:a5:86:24:ec:44)
[PASS] FDB s1 chứa MAC của h2 (86:fa:12:ca:5d:36)
[PASS] MAC h1 học đúng port (không phải vxlan0) port=1, vxlan0_port=3
port VLAN MAC Age
1 0 46:a5:86:24:ec:44 1
3 0 86:fa:12:ca:5d:36 1

───────────────────────────────────────────────────────

T9: Kiểm tra flow table trên s1
───────────────────────────────────────────────────────

[PASS] Flow table s1 có entry
[PASS] Flow table dùng actions=NORMAL (standalone mode)
cookie=0x0, duration=9.949s, table=0, n_packets=26, n_bytes=2180, priority=0 actions=NORMAL

───────────────────────────────────────────────────────

T10: Kiểm tra không có broadcast storm
───────────────────────────────────────────────────────

[PASS] Không có storm trên h1 (RX delta=4 gói trong 3s ping)
[PASS] Không có storm trên h2 (RX delta=5 gói trong 3s ping)

═══════════════════════════════════════════════════════

KẾT QUẢ KIỂM TRA MODULE 5
═══════════════════════════════════════════════════════

Bài kiểm tra Kết quả
──────────────────────────────────────── ──────────

s1-eth2 có IP 10.0.0.1/24 PASS
s2-eth2 có IP 10.0.0.2/24 PASS
s1-eth2 không còn trong OVS bridge s1 PASS
s2-eth2 không còn trong OVS bridge s2 PASS
Underlay ping 10.0.0.1 → 10.0.0.2 (4/4 PASS
vxlan0 tồn tại trên s1 (type=vxlan) FAIL
vxlan0: local_ip=10.0.0.1 PASS
vxlan0: remote_ip=10.0.0.2 PASS
vxlan0: VNI key=100 PASS
vxlan0: dst_port=4789 PASS
vxlan1 tồn tại trên s2 (type=vxlan) FAIL
vxlan1: local_ip=10.0.0.2 PASS
vxlan1: remote_ip=10.0.0.1 PASS
vxlan0 link_state=up PASS (got: up)
vxlan1 link_state=up PASS (got: up)
h1 có IP 192.168.100.1/24 PASS
h2 có IP 192.168.100.2/24 PASS
h1 → h2 overlay ping (5/5 received) PASS
h2 → h1 overlay ping (3/3 received) PASS
h1 ARP table có entry cho 192.168.100. PASS
ARP entry đúng MAC của h2 (86:fa:12:ca PASS
FDB s1 chứa MAC của h1 (46:a5:86:24:ec PASS
FDB s1 chứa MAC của h2 (86:fa:12:ca:5d PASS
MAC h1 học đúng port (không phải vxlan PASS port=1, vxlan0_port=3
Flow table s1 có entry PASS
Flow table dùng actions=NORMAL (standa PASS
Không có storm trên h1 (RX delta=4 gói PASS
Không có storm trên h2 (RX delta=5 gói PASS

Tổng: 26/28 PASS | 2 FAIL
✗ Có 2 bài kiểm tra FAIL — xem chi tiết ở trên

═══════════════════════════════════════════════════════

Mở Mininet CLI để kiểm tra thêm (gõ exit để thoát)...

\*\*\* Starting CLI:
