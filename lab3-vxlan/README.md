# Lab 3 — VXLAN over SDN với Mininet + OVS

Bài lab thực hành xây dựng, cấu hình, kiểm thử và phân tích gói tin **mạng overlay VXLAN** sử dụng Open vSwitch (OVS) làm VTEP, chạy trên môi trường mô phỏng Mininet.

---

## Chúng ta làm gì?

Mô phỏng kịch bản triển khai VXLAN giữa hai datacenter hoàn toàn bằng phần mềm:

- Hai OVS bridge (`s1`, `s2`) đóng vai trò **VTEP (VXLAN Tunnel Endpoint)**
- Hai host (`h1`, `h2`) giao tiếp qua **mạng overlay Layer 2** kéo dài qua hạ tầng Layer 3 underlay
- VXLAN VNI 100 đóng gói Ethernet frame vào UDP/IP (cổng 4789)
- Bắt và phân tích gói tin để xác minh encapsulation, giá trị VNI và overhead

```
 OVERLAY (VNI 100) — 192.168.100.0/24
 ┌──────────────────────────────────────────────┐
 │  h1 (192.168.100.1)    h2 (192.168.100.2)   │
 └────────┬──────────────────────────┬──────────┘
          │                          │
     ┌────┴─────┐   VXLAN Tunnel   ┌─┴────────┐
     │  OVS s1  │==================│  OVS s2  │
     │  (VTEP)  │  UDP:4789 VNI100 │  (VTEP)  │
     └────┬─────┘                  └────┬─────┘
          └────────────┬────────────────┘
                 UNDERLAY LINK
                 10.0.0.0/24
```

---

## Cấu trúc thư mục

```
lab3-vxlan/
├── README.md                    ← file này
├── report.md                    ← báo cáo lab đầy đủ (7 module)
│
├── scripts/
│   ├── topology.py              ← script Python dựng topology Mininet
│   ├── vxlan_setup.sh           ← script cấu hình VXLAN thủ công (8 bước)
│   ├── test_module5.py          ← bộ kiểm thử tự động (28 assertions)
│   └── capture.sh               ← script bắt và phân tích gói tin (6 bước)
│
├── results/
│   ├── module4-results.md       ← output thô từ lần chạy Module 4
│   ├── module5-results.md       ← output thô từ lần chạy Module 5
│   └── test-result.md           ← output bộ test trước khi sửa lỗi
│
└── capture-module/
    ├── capture.md               ← lần thử 1 (pcap rỗng)
    ├── capture-fix.md           ← lần thử 2 (vẫn thất bại)
    ├── capture3.md              ← lần thử 3 (0 gói trên s1-eth2)
    ├── capture4.md              ← lần thử 4 (overlay rỗng)
    └── capture5.md              ← lần thử 5 — THÀNH CÔNG ✓
```

---

## Cách thực hiện

### Công cụ sử dụng

| Công cụ | Vai trò |
|---------|---------|
| Mininet | Mô phỏng mạng — host, switch, link |
| Open vSwitch (OVS) | Triển khai VTEP — tạo VXLAN tunnel port |
| tcpdump | Bắt gói tin tại underlay và overlay |
| Python 3 | Script topology và kiểm thử tự động |
| Bash | Script cấu hình và capture tự động |

### Cách cấu hình VXLAN

OVS `add-port` với `type=vxlan` tạo tunnel tự động:

```bash
ovs-vsctl add-port s1 vxlan0 \
  -- set interface vxlan0 type=vxlan \
  options:local_ip=10.0.0.1 \
  options:remote_ip=10.0.0.2 \
  options:key=100 \
  options:dst_port=4789
```

OVS xử lý encapsulation/decapsulation trong kernel datapath — không cần controller (`failMode=standalone`).

### Cách chạy bắt gói tin

```bash
# Từ Mininet CLI
mininet> sh bash scripts/capture.sh
```

Script tự động:
1. Tìm network namespace của h1 (3 phương pháp fallback)
2. Xác minh ping overlay h1 → h2
3. Bắt VXLAN trên `-i any` (UDP port 4789) → `underlay.pcap`
4. Bắt ICMP thuần trên `h1-eth0` trong namespace h1 → `overlay.pcap`
5. Hiển thị phân tích verbose, tính overhead, hex dump

---

## Những gì đã hoàn thành

### Module 1 — Lý thuyết nền tảng
- Kiến trúc VXLAN, tổng quan RFC 7348
- Khái niệm SDN, vai trò OVS làm VTEP
- Mục tiêu lab và các quyết định thiết kế

### Module 2 — Thiết kế Topology
- Topology hai VTEP kết nối điểm-điểm
- Bảng địa chỉ IP: underlay `10.0.0.0/24`, overlay `192.168.100.0/24`
- Sơ đồ luồng đóng gói VXLAN

### Module 3 — Script Topology (`topology.py`)
- Script Python Mininet đầy đủ với gán IP underlay tự động
- Tạo VXLAN port qua OVS
- Kiểm tra kết nối lúc khởi động (ping underlay)

### Module 4 — Cấu hình VXLAN (`vxlan_setup.sh`)
- Script cấu hình thủ công 8 bước
- Cấu hình interface underlay, tạo tunnel port
- Xác minh kết nối sau cấu hình

### Module 5 — Kiểm thử tự động (`test_module5.py`)
- 10 test case, 28 assertions
- Kiểm tra: OVS bridge tồn tại, cấu hình VXLAN port, ping underlay, ping overlay, xác minh VNI, học MAC, flow table, cô lập namespace

**Kết quả: 28/28 PASS**

### Module 6 — Bắt và phân tích gói tin (`capture.sh`)
- 6 bước bắt và phân tích tự động
- Xác minh đóng gói VXLAN từ gói tin thực tế

**Kết quả đo thực tế:**

| Chỉ số | Giá trị |
|--------|---------|
| Outer IP length | 134 bytes |
| Inner IP length | 84 bytes |
| Overhead VXLAN | **50 bytes** (đúng lý thuyết RFC 7348) |
| VNI trong hex | `0x000064` = 100 ✓ |
| UDP port | 4789 ✓ |
| VXLAN Valid flag | `0x08` ✓ |

### Module 7 — Kết luận
- So sánh lý thuyết và kết quả thực đo
- Phân tích hạn chế đặc thù của môi trường Mininet
- Đề xuất hướng mở rộng

---

## Các lỗi gặp phải và cách giải quyết

### Lỗi 1 — Xung đột tên port OVS (Module 4)

**Biểu hiện:** `ovs-vsctl add-port` thất bại trên s2 với lỗi "port already exists".

**Nguyên nhân:** Cả s1 và s2 đều tạo port tên `vxlan0`. OVS yêu cầu tên interface **duy nhất toàn cục** trên tất cả các bridge.

**Giải pháp:** Đổi tên — s1 dùng `vxlan0`, s2 dùng `vxlan1`.

---

### Lỗi 2 — Ping underlay thất bại với `-I s1` (Module 4)

**Biểu hiện:** `ping -I s1 10.0.0.2` thất bại; ARP không nhận được reply.

**Nguyên nhân:** Khi dùng interface bridge `s1` làm nguồn, ARP reply đi ngược qua OVS pipeline. Trong `standalone` mode, OVS flood frame chưa biết MAC — nhưng reply bị OVS internal processing chặn trước khi đến kernel socket.

**Giải pháp:** Dùng `ping 10.0.0.2` không có flag `-I`. Để kernel tự định tuyến qua `s1-eth2`.

---

### Lỗi 3 — L2 Broadcast Storm (Module 5)

**Biểu hiện:** h1 nhận 18.8 GB traffic ngay sau khi topology khởi động; ping overlay thất bại hoặc mất hàng phút; MAC của h1 được học sai trên port `vxlan0` thay vì `s1-eth1`.

**Nguyên nhân:** `s1-eth2` và `s2-eth2` (cặp veth underlay) vừa là **OVS port thông thường** bên trong bridge, vừa được kết nối qua VXLAN tunnel. Kết quả: có **hai đường L2** giữa s1 và s2:

```
Đường 1: s1 →[port s1-eth2]→ veth wire →[port s2-eth2]→ s2
Đường 2: s1 →[vxlan0 tunnel]→ đóng gói → mở gói →[vxlan1 tunnel]→ s2
```

OVS `standalone` mode flood broadcast frame trên cả hai đường → loop → broadcast storm.

**Giải pháp:** Xóa `s1-eth2` và `s2-eth2` khỏi OVS bridge **trước khi** gán IP VTEP:

```python
s1.cmd('ovs-vsctl del-port s1 s1-eth2')
s2.cmd('ovs-vsctl del-port s2 s2-eth2')
s1.cmd('ip addr add 10.0.0.1/24 dev s1-eth2')
s2.cmd('ip addr add 10.0.0.2/24 dev s2-eth2')
```

Lúc này `s1-eth2` là interface L3 thuần — chỉ còn VXLAN tunnel kết nối hai bridge.

---

### Lỗi 4 — test_module5.py T3 FAIL do định dạng output OVS (Module 5)

**Biểu hiện:** Test T3 (kiểm tra type VXLAN port) thất bại dù `vxlan0` đã được cấu hình đúng.

**Nguyên nhân:** `ovs-vsctl list interface` in ra `type                : vxlan` (nhiều khoảng trắng). Script kiểm tra chuỗi `'type=vxlan'` và `'type : vxlan'` — đều sai.

**Giải pháp:** Dùng regex: `re.search(r'type\s*:\s*vxlan', out)`

---

### Lỗi 5 — tcpdump bắt 0 gói trên `s1-eth2` (Module 6)

**Biểu hiện:** tcpdump báo "listening on s1-eth2, 0 packets captured" dù h1 → h2 ping thành công 5/5 gói.

**Nguyên nhân:** Trong Mininet, cả hai địa chỉ VTEP (`10.0.0.1` trên `s1-eth2` và `10.0.0.2` trên `s2-eth2`) đều nằm trong **root namespace** của cùng một máy Linux. Khi OVS gửi gói VXLAN đến `10.0.0.2`, kernel nhận ra đây là địa chỉ local (trên `s2-eth2`) và chuyển gói qua **đường loopback nội bộ** — gói không bao giờ đi ra ngoài `s1-eth2` dưới dạng TX. tcpdump trên `s1-eth2` không thấy gì.

**Giải pháp:** Bắt trên `-i any` thay vì `s1-eth2`. Interface ảo này capture trên tất cả interface kể cả loopback path nội bộ.

```bash
# Trước (thất bại)
tcpdump -i s1-eth2 -n udp port 4789

# Sau (thành công)
tcpdump -i any -n udp port 4789
```

---

### Lỗi 6 — overlay.pcap luôn rỗng (Module 6)

**Biểu hiện:** `overlay.pcap` chỉ có 24 bytes (chỉ pcap header, không có gói tin) dù ping hoạt động bình thường.

**Nguyên nhân:** Script chạy `h1_exec tcpdump ... &` để background tcpdump trong namespace h1, sau đó gọi `kill $TD2`. Nhưng `$TD2` là PID của tiến trình `nsenter` wrapper — kill nó **không forward signal đến tcpdump con**. tcpdump trở thành orphan process, file pcap không bao giờ được flush và đóng.

**Giải pháp:** Dùng `-c $((PING_COUNT * 2))` để tcpdump **tự thoát** sau khi bắt đủ gói (5 ping × request+reply = 10 gói). Khi thoát tự nhiên, tcpdump flush và đóng file pcap đúng cách. Thêm `pkill -INT -f "tcpdump.*h1-eth0"` làm fallback.

```bash
h1_exec tcpdump -i "$OVERLAY_IFACE" -n -s 0 \
        -c $((PING_COUNT * 2)) \
        -w "$OVERLAY_CAP" icmp &
```

---

## Hướng phát triển trong tương lai

### Ngắn hạn
- **Wireshark trực quan:** Copy `underlay.pcap` về máy Windows, mở bằng Wireshark. Filter `vxlan` để thấy phân tầng đầy đủ Outer Eth → IP → UDP → VXLAN → Inner frame.
- **tshark trích xuất field:** Xuất `vxlan.vni`, `ip.src`, `ip.dst`, `udp.dstport` ra bảng để phân tích gọn hơn.

### Trung hạn
- **Topology 3 VTEP:** Thêm `s3 + h3` để demo VXLAN flooding, học MAC trên nhiều VTEP, và xử lý traffic BUM (Broadcast, Unknown unicast, Multicast).
- **Nhiều VNI:** Cấu hình VNI 100 và VNI 200 làm hai tenant độc lập; xác minh cô lập — h1 (VNI 100) không thể đến h3 (VNI 200) mà không qua VXLAN gateway.
- **Đo hiệu năng:** Dùng `iperf3` để so sánh throughput và latency có/không có VXLAN — lượng hóa overhead encapsulation thực tế.

### Dài hạn
- **Tích hợp SDN Controller:** Thay `failMode=standalone` bằng Ryu hoặc ONOS. Cài đặt flow rule chủ động cho VXLAN forwarding — control plane SDN thực sự.
- **BGP EVPN (RFC 7432):** Thay cấu hình VTEP tĩnh bằng quảng bá MAC/IP động qua BGP EVPN với FRRouting — cách các hệ thống production VXLAN (Cumulus, Nokia, Cisco) hoạt động.
- **Định tuyến liên VNI (L3 Gateway):** Thêm VXLAN gateway để định tuyến traffic giữa VNI 100 và VNI 200 — mô phỏng distributed gateway trong môi trường cloud.

---

## Khởi động nhanh

```bash
# 1. Khởi động topology
sudo python3 scripts/topology.py

# 2. (Trong Mininet CLI) Kiểm tra kết nối overlay
mininet> h1 ping -c 3 192.168.100.2

# 3. Chạy kiểm thử tự động
mininet> sh python3 scripts/test_module5.py

# 4. Bắt và phân tích gói tin
mininet> sh bash scripts/capture.sh

# 5. Thoát
mininet> exit
```

---

## Kết luận chính

1. **VXLAN trong suốt với host** — `h1-eth0` chỉ thấy ICMP thuần; toàn bộ đóng gói xảy ra trong OVS, host không biết gì về tunnel.
2. **OVS là VTEP mạnh mẽ** — thuần phần mềm, cấu hình qua `ovs-vsctl`, không cần phần cứng chuyên dụng.
3. **Môi trường Mininet có hạn chế đặc thù** — shared root namespace, tên OVS interface global unique, và thực thi nhận thức namespace (nsenter) — đây không phải vấn đề trong triển khai thực tế nhưng cần xử lý cẩn thận trong mô phỏng.
4. **Overhead đo thực tế khớp lý thuyết** — 134 − 84 = **50 bytes** mỗi gói (14 Eth + 20 IP + 8 UDP + 8 VXLAN).
