# Báo Cáo: So Sánh Các SDN Controller

## 1. Giới Thiệu

SDN Controller là thành phần trung tâm trong kiến trúc Software Defined Networking, đóng vai trò **"não bộ"** của toàn bộ hệ thống mạng. Controller chịu trách nhiệm:

- Duy trì **global network view** (tầm nhìn toàn cục về trạng thái mạng)
- Ra quyết định định tuyến và chuyển tiếp gói tin
- Cài đặt **flow rules** xuống các switch thông qua giao thức OpenFlow
- Cung cấp **northbound API** cho các ứng dụng mạng cấp cao

Bài báo cáo này phân tích và so sánh 4 controller phổ biến nhất trong môi trường nghiên cứu và thực hành SDN: **POX**, **Ryu**, **OpenDaylight (ODL)** và **ONOS**.

---

## 2. Tổng Quan Các Controller

### 2.1 POX

**POX** là một SDN controller mã nguồn mở được phát triển bởi nhóm nghiên cứu tại UC Berkeley, viết hoàn toàn bằng **Python 2/3**. POX được thiết kế với mục tiêu đơn giản, dễ học, phù hợp cho môi trường giáo dục và nghiên cứu ban đầu về SDN.

**Kiến trúc:**
- Single-threaded, event-driven
- Giao tiếp với switch qua OpenFlow 1.0
- Component-based: các tính năng được tổ chức thành các module độc lập

**Các tính năng nổi bật:**
- `l2_learning`: học địa chỉ MAC, hoạt động như L2 switch
- `l3_learning`: hỗ trợ định tuyến L3 cơ bản
- `firewall`: lọc gói tin theo ACL đơn giản
- `spanning_tree`: tránh vòng lặp mạng

**Ưu điểm:**
- Cú pháp Python đơn giản, dễ đọc
- Tài liệu học thuật phong phú, nhiều ví dụ mẫu
- Thời gian cài đặt và khởi động nhanh
- Phù hợp làm quen với khái niệm SDN/OpenFlow

**Hạn chế:**
- Chỉ hỗ trợ OpenFlow **1.0**
- Hiệu năng thấp do single-threaded
- Không còn được cập nhật tích cực từ năm 2013
- Không có REST API tích hợp
- Không phù hợp cho môi trường production

---

### 2.2 Ryu

**Ryu** là SDN controller mã nguồn mở được phát triển bởi **NTT Labs (Nhật Bản)**, viết bằng **Python 3** với kiến trúc event-driven dựa trên thư viện `eventlet`. Ryu được thiết kế để vừa dễ sử dụng vừa đủ mạnh cho các kịch bản thực tế.

**Kiến trúc:**
- Event-driven, cooperative multitasking (eventlet)
- Hỗ trợ OpenFlow **1.0, 1.2, 1.3, 1.4, 1.5**
- Mỗi ứng dụng SDN là một RyuApp độc lập, có thể kết hợp

**Các tính năng nổi bật:**
- `simple_switch_13`: L2 learning switch với OpenFlow 1.3
- `rest_router`: REST API để quản lý định tuyến
- `ofctl_rest`: API truy vấn và thao tác flow table
- Hỗ trợ **VLAN**, **MPLS**, **GRE tunnel**
- Tích hợp **REST API** để điều khiển từ xa

**Ưu điểm:**
- Hỗ trợ OpenFlow 1.3 đầy đủ (meter, group table, multiple table)
- REST API tích hợp sẵn, dễ tích hợp với hệ thống bên ngoài
- Vẫn được duy trì và cập nhật
- Tài liệu chi tiết, có sách hướng dẫn chính thức
- Phù hợp cả học thuật lẫn nghiên cứu chuyên sâu

**Hạn chế:**
- Hiệu năng giới hạn bởi GIL của Python
- Không phù hợp cho môi trường production quy mô lớn
- Ít được dùng trong doanh nghiệp thực tế

---

### 2.3 OpenDaylight (ODL)

**OpenDaylight** là nền tảng SDN controller mã nguồn mở được thành lập năm 2013 dưới sự bảo trợ của **Linux Foundation**, với sự đóng góp từ Cisco, Juniper, RedHat và nhiều tập đoàn lớn khác. ODL được viết bằng **Java** và có kiến trúc microservice dựa trên **OSGi (Apache Karaf)**.

**Kiến trúc:**
- Microservice, plugin-based (OSGi framework)
- Model-driven Service Abstraction Layer (MD-SAL)
- Hỗ trợ đa giao thức: OpenFlow, NETCONF, OVSDB, BGP, PCEP
- Northbound: REST API (RESTCONF/YANG), Java API

**Các tính năng nổi bật:**
- **DLUX**: giao diện web quản lý topology trực quan
- **YANG Tools**: mô hình hóa dữ liệu mạng theo chuẩn YANG
- **AAA**: xác thực và phân quyền tích hợp
- Hỗ trợ **multi-layer** (L2, L3, overlay networks)
- Khả năng **clustering** để đảm bảo HA (High Availability)

**Ưu điểm:**
- Enterprise-grade, được dùng trong môi trường production thực tế
- Hỗ trợ đa giao thức, không chỉ giới hạn OpenFlow
- Kiến trúc plugin cho phép mở rộng linh hoạt
- Cộng đồng lớn, được hỗ trợ bởi các tập đoàn lớn
- GUI dashboard trực quan (DLUX)

**Hạn chế:**
- Rất nặng: yêu cầu tối thiểu 4GB RAM, khởi động mất 2–5 phút
- Đường cong học tập dốc, cấu hình phức tạp
- Overkill cho bài lab sinh viên hoặc nghiên cứu nhỏ
- Tài liệu nhiều nhưng phức tạp và đôi khi lỗi thời

---

### 2.4 ONOS (Open Network Operating System)

**ONOS** là SDN controller mã nguồn mở được phát triển bởi **ON.Lab** (nay thuộc Open Networking Foundation - ONF), ra đời năm 2014. ONOS được thiết kế dành riêng cho **carrier-grade networks** (mạng nhà mạng viễn thông), nhấn mạnh vào khả năng mở rộng, tính sẵn sàng cao và phân tán.

**Kiến trúc:**
- Distributed, clustered (Apache Karaf + RAFT consensus)
- **Intent Framework**: lập trình mạng theo mục tiêu thay vì flow rules cụ thể
- Hỗ trợ: OpenFlow, NETCONF, P4Runtime, gRPC
- Northbound: REST API, GUI, CLI

**Các tính năng nổi bật:**
- **Intent API**: định nghĩa "ý định" kết nối thay vì viết flow rules thủ công
- **Network Configuration Service**: quản lý cấu hình toàn mạng tập trung
- **Segment Routing** hỗ trợ
- **Topo GUI**: giao diện đồ họa mạng real-time
- Clustering tự động với RAFT, chịu lỗi cao

**Ưu điểm:**
- Thiết kế cho quy mô carrier/enterprise lớn
- Intent API giúp đơn giản hóa lập trình mạng cấp cao
- Highly Available: không có single point of failure
- Hỗ trợ P4 và các công nghệ mạng tiên tiến
- GUI đẹp, trực quan

**Hạn chế:**
- Cực kỳ nặng: yêu cầu 8GB+ RAM cho cluster
- Không thực tế cho bài lab Mininet trên máy đơn
- Thời gian học và cấu hình rất dài
- Phức tạp không cần thiết cho mục đích giáo dục

---

## 3. Bảng So Sánh Chi Tiết

| Tiêu chí | POX | Ryu | OpenDaylight | ONOS |
|---|---|---|---|---|
| **Ngôn ngữ** | Python | Python | Java | Java |
| **OpenFlow** | 1.0 | 1.0–1.5 | 1.0–1.5 | 1.0–1.5 + P4 |
| **Kiến trúc** | Single-thread | Event-driven | Microservice | Distributed |
| **REST API** | Không | Có | Có | Có |
| **GUI** | Không | Không | Có (DLUX) | Có |
| **RAM tối thiểu** | ~50 MB | ~100 MB | ~2–4 GB | ~4–8 GB |
| **Khởi động** | < 5 giây | < 5 giây | 2–5 phút | 3–10 phút |
| **Độ khó** | Dễ | Trung bình | Khó | Rất khó |
| **Hỗ trợ NETCONF** | Không | Không | Có | Có |
| **Clustering/HA** | Không | Không | Có | Có |
| **Tích hợp Mininet** | Tốt | Rất tốt | Được | Được |
| **Mục tiêu sử dụng** | Giáo dục | Nghiên cứu | Enterprise | Carrier-grade |
| **Trạng thái** | Ngừng phát triển | Đang duy trì | Đang duy trì | Đang duy trì |

---

## 4. So Sánh Theo Tiêu Chí Quan Trọng

### 4.1 Phù Hợp với Mininet

```
Ryu          ████████████████████  Tốt nhất
POX          ████████████████      Tốt
ODL          ████████              Chấp nhận được
ONOS         ██████                Phức tạp, tốn tài nguyên
```

### 4.2 Độ Dễ Lập Trình

```
POX          ████████████████████  Dễ nhất (Python đơn giản)
Ryu          ████████████████      Dễ (Python + framework)
ODL          ████████              Khó (Java + YANG + OSGi)
ONOS         ██████                Khó nhất (Java + Intent + Cluster)
```

### 4.3 Tính Năng và Khả Năng Mở Rộng

```
ONOS         ████████████████████  Đầy đủ nhất
ODL          ██████████████████    Đầy đủ
Ryu          ████████████          Đủ dùng
POX          ██████                Cơ bản
```

### 4.4 Phù Hợp Môi Trường Thực Tế (Production)

```
ONOS         ████████████████████  Carrier-grade
ODL          ████████████████████  Enterprise
Ryu          ████████              Nghiên cứu / SMB
POX          ██                    Không phù hợp
```

---

## 5. Khuyến Nghị Theo Mục Tiêu

| Mục tiêu | Controller Khuyến Nghị | Lý Do |
|---|---|---|
| Học SDN lần đầu | **POX** | Đơn giản, nhiều tài liệu học thuật |
| Bài lab môn học (trung bình) | **Ryu** | Cân bằng giữa dễ dùng và tính năng |
| Nghiên cứu chuyên sâu | **Ryu** hoặc **ODL** | REST API, hỗ trợ OpenFlow 1.3 |
| Đồ án / Luận văn | **ODL** hoặc **ONOS** | Tính năng đầy đủ, gần thực tế |
| Môi trường doanh nghiệp | **ODL** | Enterprise-grade, đa giao thức |
| Mạng nhà mạng viễn thông | **ONOS** | Carrier-grade, HA, phân tán |

---

## 6. Kết Luận

Việc lựa chọn SDN controller phụ thuộc chủ yếu vào **mục tiêu sử dụng** và **nguồn lực sẵn có**:

- Nếu mục tiêu là **học tập và thực hành trong môi trường Mininet**, **Ryu** là lựa chọn tối ưu nhất: dễ lập trình bằng Python, hỗ trợ OpenFlow 1.3 đầy đủ, có REST API và tài liệu phong phú.

- Nếu mục tiêu là **nghiên cứu hoặc triển khai thực tế quy mô lớn**, **OpenDaylight** hoặc **ONOS** sẽ phù hợp hơn nhờ kiến trúc enterprise-grade và khả năng mở rộng cao.

- **POX** vẫn có giá trị như một công cụ giáo dục để hiểu nguyên lý hoạt động cơ bản của SDN, nhưng không nên dùng cho các dự án yêu cầu OpenFlow 1.3 trở lên.

> **Khuyến nghị cho dự án này: Sử dụng Ryu Controller với OpenFlow 1.3**

---

*Báo cáo được thực hiện trong khuôn khổ dự án "Tạo mạng SDN trên Mininet"*
