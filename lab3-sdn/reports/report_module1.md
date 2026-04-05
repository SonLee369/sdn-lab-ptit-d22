# Báo Cáo Module 1: Thiết Kế Topology Mạng SDN

## 1. Mục Tiêu

Module 1 có nhiệm vụ xây dựng nền tảng vật lý ảo cho toàn bộ hệ thống SDN, bao gồm:

- Định nghĩa topology mạng dạng **Star** sử dụng Mininet Python API
- Cấu hình các thông số chất lượng đường truyền (băng thông, độ trễ)
- Thiết lập kết nối giữa Mininet và **Ryu RemoteController** qua giao thức **OpenFlow 1.3**

---

## 2. Thiết Kế Topology

### 2.1 Sơ Đồ Mạng

```
        ┌─────────────────────────────┐
        │      Ryu Controller         │
        │    (127.0.0.1 : 6633)       │
        │      OpenFlow 1.3           │
        └──────────────┬──────────────┘
                       │ Kênh điều khiển (TCP)
              ┌────────┴────────┐
              │  OVS Switch s1  │
              │  OpenFlow 1.3   │
              └──┬───┬───┬───┬──┘
                 │   │   │   │
                h1  h2  h3  h4
```

### 2.2 Thông Số Cấu Hình

| Thành phần | Tên | Giá trị |
|---|---|---|
| Switch | s1 | OVS, OpenFlow 1.3 |
| Host 1 | h1 | IP: `10.0.0.1/24` — MAC: `00:00:00:00:00:01` |
| Host 2 | h2 | IP: `10.0.0.2/24` — MAC: `00:00:00:00:00:02` |
| Host 3 | h3 | IP: `10.0.0.3/24` — MAC: `00:00:00:00:00:03` |
| Host 4 | h4 | IP: `10.0.0.4/24` — MAC: `00:00:00:00:00:04` |
| Băng thông link | bw | 10 Mbps |
| Độ trễ link | delay | 5 ms |
| Tỷ lệ mất gói | loss | 0% |
| Hàng đợi | queue | HTB (Hierarchical Token Bucket) |
| Controller | Ryu | `127.0.0.1:6633` |

### 2.3 Lý Do Chọn Star Topology

Star topology được chọn vì:

- **Đơn giản, trực quan** — Dễ quan sát luồng dữ liệu đi qua switch trung tâm
- **Phù hợp với mục tiêu học tập** — Tập trung vào cơ chế hoạt động của OpenFlow thay vì phức tạp hóa cấu trúc mạng
- **Dễ mở rộng** — Tham số `n_hosts` cho phép thêm host linh hoạt mà không cần sửa code
- **Phù hợp thực tế** — Phản ánh cấu trúc Access Layer trong mạng doanh nghiệp

---

## 3. Cài Đặt Kỹ Thuật

### 3.1 Cấu Trúc File `topo.py`

```
topo.py
├── Import thư viện Mininet
├── class StarTopo(Topo)
│   └── build(): Tạo switch s1 và 4 hosts, kết nối bằng TCLink
└── def run()
    ├── Khởi tạo Mininet với OVSSwitch + TCLink
    ├── Thêm RemoteController (Ryu, 127.0.0.1:6633)
    ├── Ép switch dùng OpenFlow 1.3 qua ovs-vsctl
    ├── In thông tin topology
    └── Mở Mininet CLI
```

### 3.2 Giải Thích Các Thành Phần Chính

#### Lớp `StarTopo`

```python
class StarTopo(Topo):
    def build(self, n_hosts=4, bw=10, delay='5ms'):
        link_opts = dict(bw=bw, delay=delay, loss=0, use_htb=True)
        switch = self.addSwitch('s1', protocols='OpenFlow13')
        for i in range(1, n_hosts + 1):
            host = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24',
                                         mac=f'00:00:00:00:00:0{i}')
            self.addLink(host, switch, **link_opts)
```

- `addSwitch('s1', protocols='OpenFlow13')`: Tạo OVS switch, khai báo sẵn OpenFlow 1.3
- `addHost(...)`: Gán IP và MAC tĩnh để dễ theo dõi trong thực nghiệm
- `TCLink` + `use_htb=True`: Dùng HTB (Hierarchical Token Bucket) để kiểm soát băng thông chính xác

#### Hàm `run()`

```python
net = Mininet(topo=topo, switch=OVSSwitch, controller=None, link=TCLink,
              autoSetMacs=False, autoStaticArp=False)

ryu = net.addController('ryu', controller=RemoteController,
                         ip='127.0.0.1', port=6633)
```

- `controller=None` khi khởi tạo, sau đó thêm `RemoteController` thủ công → đảm bảo Mininet không tự khởi động controller nội bộ
- `autoStaticArp=False` → Để controller SDN xử lý ARP tự nhiên, phản ánh đúng cơ chế PacketIn
- `autoSetMacs=False` → Dùng MAC đã gán thủ công trong `build()`

```python
for sw in net.switches:
    sw.cmd(f'ovs-vsctl set bridge {sw.name} protocols=OpenFlow13')
```

- Đảm bảo switch chỉ dùng OpenFlow 1.3, tránh fallback về OpenFlow 1.0

---

## 4. Luồng Khởi Động Hệ Thống

```
Bước 1: Ryu controller khởi động, lắng nghe TCP port 6633
         │
Bước 2: sudo python3 topo.py
         │
Bước 3: Mininet tạo switch s1 (OVS) và 4 namespace host
         │
Bước 4: OVS switch kết nối TCP đến Ryu (127.0.0.1:6633)
         │
Bước 5: Ryu gửi HELLO → switch phản hồi → kênh OpenFlow được thiết lập
         │
Bước 6: Ryu cài flow rule mặc định (table-miss): gửi tất cả gói lạ lên controller
         │
Bước 7: Mininet CLI sẵn sàng nhận lệnh từ người dùng
```

---

## 5. Cách Chạy Module 1

### Bước 1 — Khởi động Ryu Controller (Terminal 1)

```bash
ryu-manager controller.py
```

> Ryu sẽ in thông báo: `loading app controller.py` và lắng nghe tại port 6633

### Bước 2 — Khởi động Mininet (Terminal 2)

```bash
sudo python3 topo.py
```

> Mininet sẽ in thông tin topology và mở CLI `mininet>`

### Bước 3 — Kiểm tra nhanh trong Mininet CLI

```bash
mininet> net          # Xem cấu trúc topology
mininet> nodes        # Liệt kê các node
mininet> links        # Liệt kê các link
mininet> dump         # Thông tin chi tiết từng node
```

**Kết quả mong đợi của lệnh `net`:**
```
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s1-eth3
h4 h4-eth0:s1-eth4
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:h3-eth0 s1-eth4:h4-eth0
ryu
```

---

## 6. Kết Quả Module 1

| Hạng mục | Kết quả |
|---|---|
| File tạo ra | `topo.py` |
| Topology | Star — 1 switch (s1) + 4 hosts (h1–h4) |
| Giao thức | OpenFlow 1.3 |
| Kết nối controller | RemoteController tại `127.0.0.1:6633` |
| Thông số link | 10 Mbps / 5ms delay / 0% loss |
| Trạng thái | Hoàn thành |

---

## 7. Lưu Ý Kỹ Thuật

> **Quan trọng:** Luôn khởi động **Ryu trước**, sau đó mới chạy `topo.py`. Nếu Mininet khởi động trước khi Ryu sẵn sàng, switch sẽ không kết nối được với controller và mạng sẽ không hoạt động.

> **Dọn dẹp:** Nếu Mininet bị crash, chạy lệnh sau để dọn dẹp trạng thái cũ:
> ```bash
> sudo mn -c
> ```

---

*Module 1 hoàn thành — Tiếp theo: Module 2 — Lập trình Ryu Controller (`controller.py`)*
