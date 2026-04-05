# Kế Hoạch Triển Khai: Xây Dựng Mạng SDN Cơ Bản với Ryu + OpenFlow 1.3

## 1. Mục Tiêu

Xây dựng và kiểm nghiệm một mạng SDN hoàn chỉnh trên Mininet sử dụng Ryu Controller với giao thức OpenFlow 1.3, bao gồm:

- Tạo topology mạng tùy chỉnh (Star)
- Lập trình controller thực hiện L2 Learning Switch
- Kiểm tra kết nối và quan sát flow table
- Đo hiệu năng mạng (băng thông, độ trễ, packet loss)
- Tổng hợp kết quả thành báo cáo

---

## 2. Môi Trường Thực Hành

| Thành phần | Phiên bản / Công cụ |
|---|---|
| Nền tảng mô phỏng | Mininet |
| SDN Controller | Ryu |
| Giao thức điều khiển | OpenFlow 1.3 |
| Switch ảo | Open vSwitch (OVS) |
| Đo băng thông | iperf3 |
| Phân tích gói tin | Wireshark / tcpdump |
| Ngôn ngữ lập trình | Python 3 |
| Định dạng báo cáo | Markdown |

---

## 3. Kiến Trúc Hệ Thống

```
                    ┌─────────────────────┐
                    │    Ryu Controller   │
                    │  (controller.py)    │
                    │   OpenFlow 1.3      │
                    └──────────┬──────────┘
                               │ TCP 6633
                               │ OpenFlow Channel
                    ┌──────────┴──────────┐
                    │    Open vSwitch     │
                    │       (s1)          │
                    └──┬────┬────┬────┬──┘
                       │    │    │    │
                     h1  h2  h3  h4
                (Star Topology — 1 Switch, 4 Hosts)
```

**Luồng hoạt động:**
1. Host gửi gói tin → Switch nhận, không có flow rule → gửi **PacketIn** lên Controller
2. Controller phân tích gói, học địa chỉ MAC → cài **flow rule** xuống Switch
3. Switch chuyển tiếp gói tin theo flow rule mà không cần hỏi Controller nữa

---

## 4. Phân Chia Module

### Module 1 — Thiết Kế Topology
**File:** `topo.py`

**Mô tả:**
Định nghĩa topology Star gồm 1 OVS switch và 4 hosts bằng Mininet Python API. Cấu hình băng thông và độ trễ cho các link để phục vụ kiểm tra hiệu năng.

**Nội dung cần triển khai:**
- Import Mininet API (`Topo`, `Mininet`, `OVSSwitch`, `RemoteController`)
- Khai báo class `StarTopo(Topo)` với 1 switch `s1` và 4 hosts `h1–h4`
- Gán thông số link: bandwidth 10 Mbps, delay 5ms
- Hàm `main()` khởi động Mininet với `RemoteController` (kết nối Ryu)
- Mở Mininet CLI để tương tác

**Kết quả kỳ vọng:**
- Topology khởi động thành công
- 4 hosts kết nối đến switch s1

---

### Module 2 — Lập Trình Ryu Controller
**File:** `controller.py`

**Mô tả:**
Lập trình Ryu Application thực hiện chức năng L2 Learning Switch: học địa chỉ MAC từ các gói tin đến, cài đặt flow rules động vào switch, và chuyển tiếp gói tin chính xác.

**Nội dung cần triển khai:**
- Import Ryu API (`RyuApp`, `OFPSwitch`, các event handler)
- Xử lý sự kiện `EventOFPSwitchFeatures`: cài flow rule mặc định (table-miss → gửi lên controller)
- Xử lý sự kiện `EventOFPPacketIn`:
  - Parse gói tin, trích xuất địa chỉ MAC nguồn/đích
  - Học MAC → Port vào bảng `mac_to_port`
  - Nếu biết cổng đích: cài flow rule `(src_mac, dst_mac) → out_port`
  - Nếu chưa biết: flood gói tin ra tất cả cổng
- Hàm `add_flow()`: helper cài flow rule với priority và idle_timeout
- Log thông tin học MAC và cài flow rule

**Kết quả kỳ vọng:**
- Controller nhận kết nối từ switch qua TCP 6633
- Tự động học MAC và cài flow rule sau lần ping đầu tiên

---

### Module 3 — Kiểm Tra Kết Nối
**Hình thức:** Hướng dẫn lệnh thực thi

**Mô tả:**
Kiểm tra hoạt động đúng đắn của hệ thống SDN sau khi khởi động Mininet và Ryu.

**Các bước kiểm tra:**

| Bước | Lệnh | Mục đích |
|---|---|---|
| 1 | `pingall` | Kiểm tra kết nối toàn bộ các cặp host |
| 2 | `h1 ping h4 -c 5` | Kiểm tra độ trễ cụ thể |
| 3 | `sh ovs-ofctl dump-flows s1` | Xem flow table trên switch |
| 4 | `sh ovs-ofctl show s1` | Xem thông tin switch và port |
| 5 | `net` | Kiểm tra topology đang chạy |

**Kết quả kỳ vọng:**
- `pingall` đạt 0% packet loss
- Flow table hiển thị các rule được cài sau khi ping
- Lần ping đầu độ trễ cao hơn (PacketIn lên controller), lần sau thấp hơn (khớp flow rule)

---

### Module 4 — Đo Hiệu Năng
**Hình thức:** Hướng dẫn lệnh thực thi

**Mô tả:**
Đo và so sánh các chỉ số hiệu năng mạng sử dụng iperf3 và ping để đánh giá chất lượng mạng SDN.

**Các thử nghiệm:**

#### 4.1 Đo Độ Trễ (Latency)
```
h1 ping h4 -c 20
```
- Ghi nhận: RTT min/avg/max/mdev
- So sánh lần ping đầu (qua controller) vs lần sau (khớp flow rule)

#### 4.2 Đo Băng Thông (Bandwidth) — TCP
```
h4 iperf3 -s &
h1 iperf3 -c h4_ip -t 10
```
- Ghi nhận: Throughput (Mbps), Retransmits

#### 4.3 Đo Băng Thông — UDP
```
h4 iperf3 -s &
h1 iperf3 -c h4_ip -u -b 8M -t 10
```
- Ghi nhận: Throughput, Jitter (ms), Packet Loss (%)

#### 4.4 Kiểm Tra Đa Luồng (Multi-stream)
```
h1 iperf3 -c h4_ip -t 10 -P 4
```
- Ghi nhận: Tổng throughput khi có 4 luồng song song

**Kết quả kỳ vọng:**
- Băng thông TCP đạt gần 10 Mbps (giới hạn link)
- Jitter UDP < 1ms
- Packet loss < 1%

---

### Module 5 — Báo Cáo Tổng Hợp
**File:** `bao_cao_huong1.md`

**Mô tả:**
Tổng hợp toàn bộ quá trình thực hành thành báo cáo hoàn chỉnh theo cấu trúc học thuật.

**Cấu trúc báo cáo:**

```
1. Giới thiệu
   1.1 Mục tiêu thực hành
   1.2 Công nghệ sử dụng

2. Cơ Sở Lý Thuyết
   2.1 Kiến trúc SDN
   2.2 Giao thức OpenFlow 1.3
   2.3 Ryu Controller
   2.4 L2 Learning Switch

3. Thiết Kế Hệ Thống
   3.1 Kiến trúc tổng thể
   3.2 Topology mạng
   3.3 Luồng xử lý gói tin

4. Triển Khai
   4.1 Cài đặt môi trường
   4.2 Code topology (topo.py)
   4.3 Code controller (controller.py)

5. Kết Quả Thực Nghiệm
   5.1 Kiểm tra kết nối
   5.2 Quan sát flow table
   5.3 Kết quả đo hiệu năng

6. Phân Tích và Đánh Giá
   6.1 Nhận xét kết quả
   6.2 So sánh SDN vs mạng truyền thống

7. Kết Luận
```

---

## 5. Thứ Tự Thực Hiện và Phụ Thuộc

```
Module 1 (topo.py)
    │
    ▼
Module 2 (controller.py)
    │
    ▼
Module 3 (Kiểm tra kết nối) ──── Chạy song song Mininet + Ryu
    │
    ▼
Module 4 (Đo hiệu năng)
    │
    ▼
Module 5 (Báo cáo tổng hợp)
```

---

## 6. Cấu Trúc Thư Mục

```
D:/lab3-sdn/
├── ke_hoach_trien_khai.md      ← File này
├── topo.py                      ← Module 1
├── controller.py                ← Module 2
├── huong_chu_de.md
├── so_sanh_controller.md
└── bao_cao_huong1.md            ← Module 5
```

---

## 7. Checklist Triển Khai

- [ ] Module 1: Viết và kiểm tra `topo.py`
- [ ] Module 2: Viết và kiểm tra `controller.py`
- [ ] Module 3: Chạy `pingall`, kiểm tra flow table
- [ ] Module 4: Chạy iperf3, ping và ghi nhận kết quả
- [ ] Module 5: Viết báo cáo `bao_cao_huong1.md`

---

*Kế hoạch triển khai dự án "Tạo mạng SDN trên Mininet" — Hướng 1*
