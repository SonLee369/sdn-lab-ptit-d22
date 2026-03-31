mininet> sh bash capture.sh

━━━ BƯỚC 1: Bắt VXLAN trên underlay interface (s1-eth2) ━━━
Lọc: UDP port 4789 (VXLAN)
Đang ping h2 (192.168.100.2) từ h1...
[OK] Gói tin đã lưu vào /tmp/vxlan_cap/underlay.pcap

━━━ BƯỚC 2: Bắt ICMP gốc trên overlay interface (h1-eth0) ━━━
Lọc: ICMP
[OK] Gói tin đã lưu vào /tmp/vxlan_cap/overlay.pcap

━━━ BƯỚC 3: Phân tích gói VXLAN trên underlay ━━━

[3a] Tóm tắt các gói bắt được (tcpdump -r):
─────────────────────────────────────────────

[3b] Chi tiết gói đầu tiên (verbose -vvv):
─────────────────────────────────────────────

━━━ BƯỚC 4: Phân tích ICMP gốc trên overlay ━━━

━━━ BƯỚC 5: So sánh kích thước — Overhead của VXLAN ━━━

Không thể đọc kích thước gói — kiểm tra file pcap

━━━ BƯỚC 6: Xác minh VNI=100 (0x000064) trong hex dump ━━━

━━━ Tổng kết ━━━

File capture đã lưu:
Underlay (VXLAN): /tmp/vxlan_cap/underlay.pcap
Overlay (ICMP) : /tmp/vxlan_cap/overlay.pcap

Mở bằng Wireshark (trên máy host):
wireshark /tmp/vxlan_cap/underlay.pcap &

Tshark phân tích chi tiết (nếu đã cài):
tshark -r /tmp/vxlan_cap/underlay.pcap -V 2>/dev/null | grep -A5 'VXLAN'

mininet> sh tshark -r /tmp/vxlan_capture.pcap -V 2>/dev/null | grep -A3 "VXLAN"
mininet>
