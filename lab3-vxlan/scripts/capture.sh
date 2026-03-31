#!/bin/bash
# ============================================================
#  capture.sh — Bắt gói tin VXLAN để phân tích
#
#  Chạy từ Mininet CLI sau khi topology đã khởi động:
#    mininet> sh bash capture.sh
# ============================================================

UNDERLAY_IFACE="any"
OVERLAY_IFACE="h1-eth0"
CAPTURE_DIR="/tmp/vxlan_cap"
UNDERLAY_CAP="$CAPTURE_DIR/underlay.pcap"
OVERLAY_CAP="$CAPTURE_DIR/overlay.pcap"
PING_TARGET="192.168.100.2"
PING_COUNT=5

GREEN='\033[92m'; RED='\033[91m'; CYAN='\033[96m'; BOLD='\033[1m'; RESET='\033[0m'
hdr()    { echo -e "\n${CYAN}${BOLD}━━━ $1 ━━━${RESET}"; }
log_ok() { echo -e "  ${GREEN}[OK]${RESET}    $1"; }
log_err(){ echo -e "  ${RED}[ERROR]${RESET} $1"; exit 1; }

mkdir -p "$CAPTURE_DIR"

# ── Tìm namespace của h1 — thử 3 phương pháp ─────────────
hdr "Tiền kiểm tra — Tìm namespace của h1"

h1_exec() { echo ""; }   # placeholder

# Phương pháp 1: named namespace "mn.h1" (Mininet 2.3+)
if ip netns list 2>/dev/null | grep -qE "^mn\.h1( |$)"; then
    h1_exec() { ip netns exec mn.h1 -- "$@"; }
    log_ok "Phương pháp 1: ip netns exec mn.h1"

# Phương pháp 2: nsenter qua PID của process "mininet:h1"
elif H1_PID=$(ps -eo pid,args 2>/dev/null | grep "mininet:h1" | grep -v grep \
              | awk '{print $1}' | head -1) && [ -n "$H1_PID" ]; then
    h1_exec() { nsenter --net=/proc/$H1_PID/ns/net -- "$@"; }
    log_ok "Phương pháp 2: nsenter PID=$H1_PID"

# Phương pháp 3: mnexec (Mininet built-in tool)
elif H1_PID=$(ps -eo pid,args 2>/dev/null | grep "mininet:h1" | grep -v grep \
              | awk '{print $1}' | head -1) && command -v mnexec &>/dev/null; then
    h1_exec() { mnexec -a "$H1_PID" "$@"; }
    log_ok "Phương pháp 3: mnexec PID=$H1_PID"

else
    log_err "Không tìm thấy namespace h1. Chắc chắn topology.py đang chạy."
fi

# Kiểm tra h1 có ping được h2 không
echo "  Kiểm tra overlay ping từ h1..."
if h1_exec ping -c 1 -W 2 "$PING_TARGET" &>/dev/null; then
    log_ok "h1 → h2 ping OK — bắt đầu capture"
else
    log_err "h1 không ping được h2. Kiểm tra VXLAN đã cấu hình chưa (chạy vxlan_setup.sh)."
fi

# ── BƯỚC 1: Bắt VXLAN trên underlay (s1-eth2) ────────────
hdr "BƯỚC 1: Bắt VXLAN trên underlay interface ($UNDERLAY_IFACE)"

# Kiểm tra s1-eth2 (underlay physical iface) tồn tại
if ! ip link show "s1-eth2" &>/dev/null; then
    log_err "Interface s1-eth2 không tồn tại. Chạy topology.py trước."
fi
echo "  Capture interface: $UNDERLAY_IFACE (bắt toàn bộ interfaces trong root namespace)"
echo "  Underlay s1-eth2: $(ip link show s1-eth2 | grep -oP '(?<=state )\w+') — IP: $(ip addr show s1-eth2 | grep -oP '(?<=inet )[\d./]+')"
echo "  Lọc: UDP port 4789"

rm -f "$UNDERLAY_CAP"
# s1-eth2 ở root namespace — tcpdump không cần nsenter
# Bắt không giới hạn gói (-c), dừng thủ công sau khi ping xong
# Ghi stderr ra file để debug nếu cần
tcpdump -i "$UNDERLAY_IFACE" -n -s 0 -w "$UNDERLAY_CAP" \
        udp port 4789 2>/tmp/td1_err.txt &
TD1=$!

# Chờ tcpdump sẵn sàng: kiểm tra process còn chạy + file được tạo
for i in $(seq 1 10); do
    sleep 0.3
    kill -0 $TD1 2>/dev/null && [ -f "$UNDERLAY_CAP" ] && break
done
echo "  tcpdump đã khởi động (PID=$TD1)"

# Ping chậm hơn để tcpdump không bỏ sót gói
echo "  Đang ping $PING_COUNT gói từ namespace h1 (interval=0.8s)..."
h1_exec ping -c $PING_COUNT -i 0.8 "$PING_TARGET"
sleep 0.8   # chờ gói cuối đến s1-eth2 trước khi dừng

kill $TD1 2>/dev/null; wait $TD1 2>/dev/null

# Kiểm tra file size > 24 bytes (pcap header = 24 bytes, file có gói > 24 bytes)
FSIZE=$(stat -c%s "$UNDERLAY_CAP" 2>/dev/null || echo 0)
if [ "$FSIZE" -gt 24 ]; then
    PKT_COUNT=$(tcpdump -r "$UNDERLAY_CAP" 2>/dev/null | tail -1 | grep -oP '^\d+')
    log_ok "Đã bắt gói → $UNDERLAY_CAP ($FSIZE bytes)"
else
    echo "  tcpdump stderr: $(cat /tmp/td1_err.txt 2>/dev/null)"
    log_err "BƯỚC 1 FAIL: underlay.pcap trống ($FSIZE bytes). Xem stderr ở trên."
fi

# ── BƯỚC 2: Bắt ICMP gốc trên overlay (h1-eth0) ──────────
hdr "BƯỚC 2: Bắt ICMP gốc trên overlay interface ($OVERLAY_IFACE)"
echo "  Lọc: ICMP | h1-eth0 ở namespace h1 → dùng h1_exec"

rm -f "$OVERLAY_CAP"
# -c limit: mỗi ping = request + reply = 2 packet → PING_COUNT*2
# tcpdump tự thoát sau khi bắt đủ gói → không cần kill, pcap flush đúng
h1_exec tcpdump -i "$OVERLAY_IFACE" -n -s 0 \
        -c $((PING_COUNT * 2)) \
        -w "$OVERLAY_CAP" \
        icmp 2>/tmp/td2_err.txt &
TD2=$!

# Chờ tcpdump sẵn sàng: process còn sống VÀ file được tạo
for i in $(seq 1 15); do
    sleep 0.3
    kill -0 $TD2 2>/dev/null && [ -f "$OVERLAY_CAP" ] && break
done
echo "  tcpdump overlay đã khởi động (PID=$TD2)"

h1_exec ping -c $PING_COUNT -i 0.8 "$PING_TARGET" &>/dev/null

# Chờ tcpdump tự thoát sau khi bắt đủ gói (timeout 5s)
for i in $(seq 1 17); do
    sleep 0.3
    kill -0 $TD2 2>/dev/null || break
done
# Nếu vẫn còn chạy (ít hơn PING_COUNT*2 gói captured), kill bằng SIGINT để flush
kill -INT $TD2 2>/dev/null
# Kill child tcpdump process nếu nsenter wrapper còn giữ nó
pkill -INT -f "tcpdump.*$OVERLAY_IFACE" 2>/dev/null
wait $TD2 2>/dev/null

FSIZE2=$(stat -c%s "$OVERLAY_CAP" 2>/dev/null || echo 0)
[ "$FSIZE2" -gt 24 ] && log_ok "Đã bắt gói → $OVERLAY_CAP ($FSIZE2 bytes)" \
                      || log_err "BƯỚC 2 FAIL: overlay.pcap trống. stderr: $(cat /tmp/td2_err.txt)"

# ── BƯỚC 3: Phân tích underlay ────────────────────────────
hdr "BƯỚC 3: Phân tích gói VXLAN trên underlay"
echo ""
echo "  [3a] Tóm tắt (tcpdump -r):"
echo "  ──────────────────────────────────────────────────────"
tcpdump -r "$UNDERLAY_CAP" -n 2>/dev/null | head -20

echo ""
echo "  [3b] Verbose -vvv (2 gói đầu):"
echo "  ──────────────────────────────────────────────────────"
tcpdump -r "$UNDERLAY_CAP" -n -vvv -c 2 2>/dev/null

# ── BƯỚC 4: Phân tích overlay ─────────────────────────────
hdr "BƯỚC 4: Phân tích ICMP gốc trên overlay (h1-eth0)"
echo ""
tcpdump -r "$OVERLAY_CAP" -n -v 2>/dev/null | head -20

# ── BƯỚC 5: So sánh kích thước ────────────────────────────
hdr "BƯỚC 5: So sánh kích thước — Overhead VXLAN"
echo ""

# Dùng -e để lấy đúng field length từ Ethernet header
UNDERLAY_BYTES=$(tcpdump -r "$UNDERLAY_CAP" -n -e 2>/dev/null \
    | grep -oP '(?<=length )\d+' | head -1)
OVERLAY_BYTES=$(tcpdump -r "$OVERLAY_CAP" -n -e 2>/dev/null \
    | grep -oP '(?<=length )\d+' | head -1)

if [[ -n "$UNDERLAY_BYTES" && -n "$OVERLAY_BYTES" ]]; then
    OVERHEAD=$(( UNDERLAY_BYTES - OVERLAY_BYTES ))
    printf "  %-32s %s\n" "Gói VXLAN (underlay):"   "${UNDERLAY_BYTES} bytes"
    printf "  %-32s %s\n" "Gói ICMP gốc (overlay):" "${OVERLAY_BYTES} bytes"
    printf "  %-32s %s\n" "Overhead VXLAN:"          "${OVERHEAD} bytes"
    echo ""
    echo "  Cấu trúc overhead (lý thuyết = 50 bytes):"
    echo "    Outer Ethernet : 14 bytes"
    echo "    Outer IP       : 20 bytes"
    echo "    Outer UDP      :  8 bytes"
    echo "    VXLAN header   :  8 bytes"
else
    echo "  Không đọc được kích thước — hiển thị raw:"
    tcpdump -r "$UNDERLAY_CAP" -n 2>/dev/null | head -3
fi

# ── BƯỚC 6: Hex dump — xác minh VNI=100 ──────────────────
hdr "BƯỚC 6: Hex dump — xác minh VNI=100 (0x000064)"
echo ""
echo "  Vị trí VNI: byte 46-48 (sau Outer Eth[14]+IP[20]+UDP[8]+VXLAN flags[4])"
echo ""
tcpdump -r "$UNDERLAY_CAP" -n -xx -c 1 2>/dev/null

# ── Tổng kết ──────────────────────────────────────────────
hdr "Tổng kết"
echo ""
echo "  File đã lưu:"
echo "    Underlay (VXLAN) : $UNDERLAY_CAP"
echo "    Overlay  (ICMP)  : $OVERLAY_CAP"
echo ""
echo "  Phân tích thêm:"
echo "    tshark -r $UNDERLAY_CAP"
echo "    tshark -r $UNDERLAY_CAP -V 2>/dev/null | grep -A5 'VXLAN'"
echo ""
echo "  Mở Wireshark (từ terminal host, NGOÀI Mininet CLI):"
echo "    wireshark $UNDERLAY_CAP &"
echo ""
