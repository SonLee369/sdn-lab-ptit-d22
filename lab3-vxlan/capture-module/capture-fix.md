mininet> sh bash capture.sh

━━━ Tiền kiểm tra — Tìm namespace của h1 ━━━
[OK] Phương pháp 2: nsenter PID=16167
Kiểm tra overlay ping từ h1...
[OK] h1 → h2 ping OK — bắt đầu capture

━━━ BƯỚC 1: Bắt VXLAN trên underlay interface (s1-eth2) ━━━
Lọc: UDP port 4789 | Số gói tối đa: 20
Đang ping từ namespace h1...
[ERROR] BƯỚC 1 FAIL: underlay.pcap trống. Kiểm tra s1-eth2 và VXLAN.

mininet>
