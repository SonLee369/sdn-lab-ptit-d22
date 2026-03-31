#!/bin/bash
# ============================================================
#  Lab 3: Cấu hình VXLAN thủ công trên OVS
#  Chạy script này SAU KHI topology.py đã khởi động xong
#  (tức là Mininet đã tạo s1, s2 và gán IP underlay rồi)
#
#  Dùng lệnh từ Mininet CLI:
#    mininet> sh bash /path/to/vxlan_setup.sh
#  Hoặc từ terminal khác khi Mininet đang chạy:
#    sudo bash vxlan_setup.sh
# ============================================================

# ---------- Thông số cấu hình ----------
S1_BRIDGE="s1"
S2_BRIDGE="s2"
S1_VTEP_IP="10.0.0.1"
S2_VTEP_IP="10.0.0.2"
UNDERLAY_MASK="24"
VNI="100"
VXLAN_PORT="4789"
# OVS yêu cầu tên interface duy nhất toàn cục trên cùng instance
# => s1 và s2 KHÔNG THỂ cùng dùng "vxlan0"
S1_VXLAN_IFACE="vxlan0"
S2_VXLAN_IFACE="vxlan1"

# ---------- Màu sắc terminal ----------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_ok()   { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "        $1"; }

echo ""
echo "============================================================"
echo "  Lab 3 — Cấu hình VXLAN thủ công trên OVS"
echo "============================================================"
echo ""

# ============================================================
# BƯỚC 1: Kiểm tra điều kiện tiên quyết
# ============================================================
echo ">>> BƯỚC 1: Kiểm tra điều kiện tiên quyết"

# Kiểm tra ovs-vsctl có tồn tại không
if ! command -v ovs-vsctl &>/dev/null; then
    log_err "ovs-vsctl không tìm thấy. Hãy cài Open vSwitch."
    exit 1
fi
log_ok "ovs-vsctl tìm thấy: $(ovs-vsctl --version | head -1)"

# Kiểm tra OVS daemon đang chạy
if ! ovs-vsctl show &>/dev/null; then
    log_err "OVS daemon chưa chạy. Khởi động bằng: sudo /etc/init.d/openvswitch-switch start"
    exit 1
fi
log_ok "OVS daemon đang hoạt động"

# Kiểm tra bridge s1 và s2 tồn tại
for BR in $S1_BRIDGE $S2_BRIDGE; do
    if ovs-vsctl br-exists $BR; then
        log_ok "Bridge '$BR' tồn tại"
    else
        log_err "Bridge '$BR' không tìm thấy. Hãy chạy topology.py trước."
        exit 1
    fi
done
echo ""

# ============================================================
# BƯỚC 2: Rút underlay veth ra khỏi OVS bridge + gán VTEP IP
# ============================================================
# ROOT CAUSE FIX: s1-eth2/s2-eth2 nằm trong OVS bridge + VXLAN tunnel
# = hai đường L2 song song → OVS flood cả hai → broadcast storm → loop.
# Giải pháp: rút s1-eth2/s2-eth2 khỏi bridge, gán VTEP IP trực tiếp lên
# các veth interface thuần (kernel) — OVS sẽ không flood qua đó nữa.
echo ">>> BƯỚC 2: Rút underlay veth khỏi OVS bridge (ngăn L2 loop)"

S1_UNDERLAY_IFACE="s1-eth2"
S2_UNDERLAY_IFACE="s2-eth2"

# Rút khỏi OVS bridge (bỏ qua lỗi nếu đã rút rồi)
ovs-vsctl del-port ${S1_BRIDGE} ${S1_UNDERLAY_IFACE} 2>/dev/null && \
    log_ok "Đã rút '${S1_UNDERLAY_IFACE}' khỏi bridge ${S1_BRIDGE}" || \
    log_warn "'${S1_UNDERLAY_IFACE}' đã không còn trong bridge ${S1_BRIDGE}"

ovs-vsctl del-port ${S2_BRIDGE} ${S2_UNDERLAY_IFACE} 2>/dev/null && \
    log_ok "Đã rút '${S2_UNDERLAY_IFACE}' khỏi bridge ${S2_BRIDGE}" || \
    log_warn "'${S2_UNDERLAY_IFACE}' đã không còn trong bridge ${S2_BRIDGE}"

# Gán VTEP IP cho raw veth interface
ip addr add ${S1_VTEP_IP}/${UNDERLAY_MASK} dev ${S1_UNDERLAY_IFACE} 2>/dev/null
ip link set ${S1_UNDERLAY_IFACE} up
log_ok "s1 VTEP IP: ${S1_VTEP_IP}/${UNDERLAY_MASK} trên ${S1_UNDERLAY_IFACE}"

ip addr add ${S2_VTEP_IP}/${UNDERLAY_MASK} dev ${S2_UNDERLAY_IFACE} 2>/dev/null
ip link set ${S2_UNDERLAY_IFACE} up
log_ok "s2 VTEP IP: ${S2_VTEP_IP}/${UNDERLAY_MASK} trên ${S2_UNDERLAY_IFACE}"
echo ""

# ============================================================
# BƯỚC 3: Kiểm tra kết nối underlay
# ============================================================
echo ">>> BƯỚC 3: Kiểm tra kết nối underlay (s1 ping s2)"

# Không dùng -I (bind interface) vì OVS pipeline chặn ARP reply qua bridge interface
# Dùng ping thông thường — kernel định tuyến qua route 10.0.0.0/24
ping -c 3 -W 2 ${S2_VTEP_IP} > /tmp/ping_underlay.txt 2>&1
if grep -q "bytes from" /tmp/ping_underlay.txt; then
    log_ok "Underlay OK — ${S1_VTEP_IP} → ${S2_VTEP_IP} thành công"
    grep "packets transmitted" /tmp/ping_underlay.txt | while read line; do
        log_info "$line"
    done
else
    log_warn "Ping underlay thất bại — tiếp tục cấu hình VXLAN, kiểm tra lại sau"
    grep "packet loss" /tmp/ping_underlay.txt || cat /tmp/ping_underlay.txt
fi
echo ""

# ============================================================
# BƯỚC 4: Xóa VXLAN port cũ (nếu có) để cấu hình lại sạch
# ============================================================
echo ">>> BƯỚC 4: Dọn dẹp VXLAN port cũ (nếu có)"

# Dọn từng bridge với đúng tên interface của nó
for ENTRY in "${S1_BRIDGE}:${S1_VXLAN_IFACE}" "${S2_BRIDGE}:${S2_VXLAN_IFACE}"; do
    BR="${ENTRY%%:*}"
    IFACE="${ENTRY##*:}"
    if ovs-vsctl list-ports $BR | grep -q "^${IFACE}$"; then
        ovs-vsctl del-port $BR $IFACE
        log_warn "Đã xóa port '${IFACE}' cũ trên ${BR}"
    else
        log_ok "Không có port '${IFACE}' cũ trên ${BR}"
    fi
done
echo ""

# ============================================================
# BƯỚC 5: Thêm VXLAN tunnel port vào s1
# ============================================================
echo ">>> BƯỚC 5: Thêm VXLAN tunnel port vào s1 (port: ${S1_VXLAN_IFACE})"

ovs-vsctl add-port ${S1_BRIDGE} ${S1_VXLAN_IFACE} \
    -- set interface ${S1_VXLAN_IFACE} \
       type=vxlan \
       options:local_ip=${S1_VTEP_IP} \
       options:remote_ip=${S2_VTEP_IP} \
       options:key=${VNI} \
       options:dst_port=${VXLAN_PORT}

if [ $? -eq 0 ]; then
    log_ok "VXLAN port '${S1_VXLAN_IFACE}' đã thêm vào ${S1_BRIDGE}"
    log_info "  local_ip  = ${S1_VTEP_IP}"
    log_info "  remote_ip = ${S2_VTEP_IP}"
    log_info "  VNI (key) = ${VNI}"
    log_info "  dst_port  = ${VXLAN_PORT}"
else
    log_err "Thêm VXLAN port vào ${S1_BRIDGE} thất bại"
    exit 1
fi
echo ""

# ============================================================
# BƯỚC 6: Thêm VXLAN tunnel port vào s2
# ============================================================
echo ">>> BƯỚC 6: Thêm VXLAN tunnel port vào s2 (port: ${S2_VXLAN_IFACE})"

ovs-vsctl add-port ${S2_BRIDGE} ${S2_VXLAN_IFACE} \
    -- set interface ${S2_VXLAN_IFACE} \
       type=vxlan \
       options:local_ip=${S2_VTEP_IP} \
       options:remote_ip=${S1_VTEP_IP} \
       options:key=${VNI} \
       options:dst_port=${VXLAN_PORT}

if [ $? -eq 0 ]; then
    log_ok "VXLAN port '${S2_VXLAN_IFACE}' đã thêm vào ${S2_BRIDGE}"
    log_info "  local_ip  = ${S2_VTEP_IP}"
    log_info "  remote_ip = ${S1_VTEP_IP}"
    log_info "  VNI (key) = ${VNI}"
    log_info "  dst_port  = ${VXLAN_PORT}"
else
    log_err "Thêm VXLAN port vào ${S2_BRIDGE} thất bại"
    exit 1
fi
echo ""

# ============================================================
# BƯỚC 7: Xác minh cấu hình OVS
# ============================================================
echo ">>> BƯỚC 7: Xác minh cấu hình OVS"
echo ""
echo "--- ovs-vsctl show ---"
ovs-vsctl show
echo ""

# Kiểm tra trạng thái tunnel port — dùng đúng tên interface cho từng bridge
for ENTRY in "${S1_BRIDGE}:${S1_VXLAN_IFACE}" "${S2_BRIDGE}:${S2_VXLAN_IFACE}"; do
    BR="${ENTRY%%:*}"
    IFACE="${ENTRY##*:}"
    LINK=$(ovs-vsctl get interface ${IFACE} link_state 2>/dev/null | tr -d '"')
    log_info "Tunnel '${IFACE}' trên ${BR}: link_state = ${LINK:-unknown}"
done
echo ""

# ============================================================
# BƯỚC 8: Hiển thị flow table
# ============================================================
echo ">>> BƯỚC 8: Flow table trên s1 và s2"
echo ""
echo "--- Flow table s1 ---"
ovs-ofctl dump-flows ${S1_BRIDGE}
echo ""
echo "--- Flow table s2 ---"
ovs-ofctl dump-flows ${S2_BRIDGE}
echo ""

# ============================================================
# Tổng kết
# ============================================================
echo "============================================================"
echo "  Cấu hình VXLAN hoàn tất!"
echo ""
echo "  Underlay : s1=${S1_VTEP_IP}  ←→  s2=${S2_VTEP_IP}"
echo "  Overlay  : VNI=${VNI}  UDP=${VXLAN_PORT}"
echo ""
echo "  Kiểm tra kết nối overlay:"
echo "    Trong Mininet CLI:"
echo "      mininet> h1 ping -c 3 192.168.100.2"
echo "      mininet> pingall"
echo "============================================================"
echo ""
