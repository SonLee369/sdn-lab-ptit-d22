# Báo Cáo: Các Hướng Chủ Đề Thực Hành SDN trên Mininet

## 1. Giới thiệu

Software Defined Networking (SDN) là kiến trúc mạng tách biệt **mặt điều khiển (control plane)** khỏi **mặt chuyển tiếp dữ liệu (data plane)**, cho phép lập trình và quản lý mạng một cách linh hoạt thông qua một controller tập trung.

**Mininet** là nền tảng mô phỏng mạng nhẹ, cho phép tạo ra các topology mạng ảo với switch, host và controller thực thi trên một máy đơn, rất phù hợp để thực hành và nghiên cứu SDN.

---

## 2. Các Hướng Chủ Đề

### Hướng 1 — Xây Dựng Mạng SDN Cơ Bản với OpenFlow Controller

**Mô tả:**
Xây dựng topology mạng tùy chỉnh (Fat-Tree, Ring, Star) trên Mininet, kết hợp với controller (POX hoặc Ryu) để điều khiển quá trình chuyển tiếp gói tin qua giao thức OpenFlow.

**Nội dung thực hành:**
- Tạo topology tùy chỉnh bằng Python API của Mininet
- Kết nối controller Ryu/POX với các Open vSwitch (OVS)
- Kiểm tra bảng flow (flow table) trên switch
- Đo hiệu năng: băng thông (iperf3), độ trễ (ping), packet loss

**Kết quả kỳ vọng:**
- Hiểu cơ chế hoạt động của OpenFlow
- So sánh hành vi mạng SDN vs mạng truyền thống

**Độ khó:** Cơ bản
**Công cụ:** Mininet, Ryu/POX, iperf3, Wireshark

---

### Hướng 2 — Load Balancing với SDN Controller

**Mô tả:**
Xây dựng hệ thống cân bằng tải (load balancing) sử dụng controller SDN để phân phối traffic từ client đến nhiều server một cách thông minh, thay thế cho các giải pháp truyền thống.

**Nội dung thực hành:**
- Thiết kế topology: 1 client — 1 load balancer switch — N servers
- Lập trình controller Ryu để phân phối flow theo thuật toán Round-Robin hoặc Least Connection
- Theo dõi và trực quan hóa flow table động
- So sánh hiệu năng với giải pháp không có load balancing

**Kết quả kỳ vọng:**
- Hiểu cơ chế điều hướng traffic ở layer 2/3 bằng flow rules
- Chứng minh tính linh hoạt của SDN trong việc điều khiển luồng dữ liệu

**Độ khó:** Trung bình
**Công cụ:** Mininet, Ryu, iperf3, REST API

---

### Hướng 3 — QoS & Traffic Engineering

**Mô tả:**
Triển khai chất lượng dịch vụ (QoS) trên mạng SDN, ưu tiên các luồng traffic quan trọng (VoIP, video streaming) và giới hạn băng thông của các luồng thông thường.

**Nội dung thực hành:**
- Phân loại traffic theo địa chỉ IP/Port/Protocol
- Lập trình flow rules với priority và meter table (OpenFlow 1.3)
- Cấu hình Queue trên OVS để giới hạn tốc độ
- Đo và so sánh hiệu năng trước/sau khi áp dụng QoS

**Kết quả kỳ vọng:**
- Hiểu cơ chế meter, queue trong OpenFlow 1.3
- Chứng minh SDN có thể thực thi chính sách QoS linh hoạt hơn mạng truyền thống

**Độ khó:** Nâng cao
**Công cụ:** Mininet, Ryu, iperf3, tc (traffic control), OVS-VSCTL

---

### Hướng 4 — SDN Firewall / DDoS Mitigation

**Mô tả:**
Xây dựng tường lửa (firewall) và hệ thống phát hiện/ngăn chặn tấn công DDoS sử dụng controller SDN, tận dụng khả năng lập trình flow rules động để phản ứng real-time với các mối đe dọa.

**Nội dung thực hành:**
- Lập trình controller Ryu để phân tích packet-in và phát hiện traffic bất thường
- Tự động cài đặt drop rules khi phát hiện tấn công (theo ngưỡng PPS/BPS)
- Mô phỏng tấn công DDoS bằng hping3 hoặc scapy trong Mininet
- So sánh hiệu năng mạng trước và sau khi kích hoạt tính năng bảo vệ

**Kết quả kỳ vọng:**
- Hiểu cách SDN phản ứng linh hoạt với các mối đe dọa bảo mật
- Chứng minh lợi thế của control plane tập trung trong việc thực thi chính sách bảo mật

**Độ khó:** Nâng cao
**Công cụ:** Mininet, Ryu, hping3, Scapy, Wireshark

---

## 3. Bảng So Sánh Tổng Quan

| Tiêu chí | Hướng 1 | Hướng 2 | Hướng 3 | Hướng 4 |
|---|---|---|---|---|
| **Chủ đề** | Cơ bản SDN | Load Balancing | QoS/Traffic Eng. | Firewall/DDoS |
| **Độ khó** | Cơ bản | Trung bình | Nâng cao | Nâng cao |
| **OpenFlow** | 1.0/1.3 | 1.3 | 1.3 | 1.3 |
| **Lập trình** | Ít | Trung bình | Nhiều | Nhiều |
| **Tính ứng dụng** | Giáo dục | Thực tế cao | Thực tế cao | Thực tế cao |
| **Thời gian ước tính** | 4–6 giờ | 6–8 giờ | 8–12 giờ | 8–12 giờ |

---

## 4. Khuyến Nghị Lựa Chọn

```
Mục tiêu                          →  Hướng khuyến nghị
──────────────────────────────────────────────────────
Nắm vững kiến thức nền SDN        →  Hướng 1
Bài lab môn học (trung bình)       →  Hướng 2  ← PHỔ BIẾN NHẤT
Nghiên cứu / đồ án chuyên sâu     →  Hướng 3 hoặc 4
Quan tâm đến bảo mật mạng         →  Hướng 4
```

**Controller được khuyến nghị cho tất cả các hướng: Ryu**
- Viết bằng Python, dễ tùy chỉnh
- Hỗ trợ OpenFlow 1.3 đầy đủ
- Tích hợp REST API sẵn có
- Cộng đồng và tài liệu phong phú

---

## 5. Kết Luận

Bốn hướng chủ đề trên đều khai thác tốt sức mạnh của nền tảng SDN/Mininet. Tùy vào mục tiêu học tập và thời gian có sẵn, người thực hành có thể lựa chọn hướng phù hợp. Với bài thực hành trong môi trường học thuật, **Hướng 2 (Load Balancing)** được đánh giá là cân bằng tốt nhất giữa độ phức tạp kỹ thuật và tính minh họa trực quan của SDN.
