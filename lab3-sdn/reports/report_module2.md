# Báo Cáo Module 2: Lập Trình Ryu Controller — L2 Learning Switch

## 1. Mục Tiêu

Module 2 xây dựng bộ não điều khiển cho hệ thống SDN, bao gồm:

- Lập trình **Ryu Application** thực hiện chức năng L2 Learning Switch
- Xử lý sự kiện **PacketIn** từ switch, học địa chỉ MAC động
- Cài đặt **flow rules** xuống switch qua thông điệp `OFPFlowMod`
- Chuyển tiếp gói tin chính xác hoặc flood khi chưa biết cổng đích

---

## 2. Cơ Sở Lý Thuyết

### 2.1 L2 Learning Switch trong SDN

Trong mạng truyền thống, switch học địa chỉ MAC tự động qua phần cứng. Trong SDN, chức năng này được **lập trình ở controller** và áp đặt xuống switch bằng flow rules.

```
Mạng truyền thống:         Mạng SDN (Module 2):
┌────────────────┐          ┌──────────────────────┐
│  Switch        │          │  Ryu Controller      │
│  (học MAC      │          │  (học MAC, quyết định│
│   bằng phần    │          │   flow rule bằng SW) │
│   cứng)        │          └──────────┬───────────┘
└────────────────┘                     │ OFPFlowMod
                                ┌──────┴──────┐
                                │  OVS Switch │
                                │  (thực thi  │
                                │  flow rule) │
                                └─────────────┘
```

### 2.2 Các Thông Điệp OpenFlow 1.3 Sử Dụng

| Thông điệp | Hướng | Chức năng |
|---|---|---|
| `OFPSwitchFeatures` | Switch → Controller | Thông báo switch đã kết nối |
| `OFPFlowMod` | Controller → Switch | Cài / sửa / xóa flow rule |
| `OFPPacketIn` | Switch → Controller | Gửi gói tin lên controller khi không khớp rule |
| `OFPPacketOut` | Controller → Switch | Yêu cầu switch gửi gói tin ra cổng |

### 2.3 Flow Table và Table-Miss

```
Gói tin vào switch
      │
      ▼
┌─────────────────────────────────────┐
│           Flow Table                │
│  ┌───────────────────────────────┐  │
│  │ priority=1: eth_src+eth_dst   │──▶ Forward ra out_port
│  │ priority=1: eth_src+eth_dst   │──▶ Forward ra out_port
│  │ ...                           │  │
│  │ priority=0: match=ALL (miss)  │──▶ Lên Controller (PacketIn)
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 3. Cấu Trúc Code `controller.py`

```
controller.py
├── Import thư viện Ryu
├── class L2LearningSwitch(RyuApp)
│   ├── OFP_VERSIONS = [OpenFlow 1.3]
│   ├── __init__(): Khởi tạo mac_to_port = {}
│   ├── switch_features_handler()  ← Sự kiện SwitchFeatures
│   │   └── Cài table-miss rule (priority=0)
│   ├── packet_in_handler()        ← Sự kiện PacketIn
│   │   ├── Parse gói Ethernet
│   │   ├── Học MAC src → port
│   │   ├── Tra cứu MAC dst → out_port
│   │   ├── Cài flow rule (nếu biết dst)
│   │   └── Gửi PacketOut
│   └── _add_flow()                ← Hàm tiện ích
│       └── Gửi OFPFlowMod xuống switch
```

---

## 4. Giải Thích Chi Tiết Từng Thành Phần

### 4.1 Khai Báo Lớp và Bảng MAC

```python
class L2LearningSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2LearningSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
```

- `OFP_VERSIONS`: Ràng buộc controller chỉ chấp nhận switch dùng **OpenFlow 1.3**
- `mac_to_port`: Bảng học MAC có cấu trúc `{dpid: {mac: port}}`
  - `dpid`: Datapath ID — định danh duy nhất của mỗi switch
  - Hỗ trợ nhiều switch cùng lúc nhờ cấu trúc lồng nhau

### 4.2 Xử Lý Kết Nối Switch — `switch_features_handler`

```python
@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
def switch_features_handler(self, ev):
    match   = parser.OFPMatch()                          # Khớp tất cả
    actions = [parser.OFPActionOutput(OFPP_CONTROLLER,
                                      OFPCML_NO_BUFFER)] # Lên controller
    self._add_flow(datapath, priority=0, match=match, actions=actions)
```

**Giải thích:**
- Decorator `@set_ev_cls(..., CONFIG_DISPATCHER)`: Hàm được gọi khi switch vừa kết nối (giai đoạn cấu hình)
- `OFPMatch()` không có tham số = khớp **tất cả** gói tin
- `OFPP_CONTROLLER`: Cổng ảo "gửi lên controller"
- `OFPCML_NO_BUFFER`: Gửi toàn bộ gói tin lên (không dùng buffer switch)
- `priority=0`: Ưu tiên thấp nhất — chỉ áp dụng khi không khớp rule nào khác (**table-miss**)

### 4.3 Xử Lý PacketIn — `packet_in_handler`

```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
```

**Decorator `MAIN_DISPATCHER`**: Hàm được gọi khi switch đã ở trạng thái hoạt động bình thường.

**Luồng xử lý 5 bước:**

```
Bước 1: Parse gói Ethernet
        pkt     = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        → Lấy src_mac, dst_mac, ethertype

Bước 2: Bỏ qua gói LLDP
        if eth_pkt.ethertype == ETH_TYPE_LLDP: return
        → Tránh xử lý gói link discovery không cần thiết

Bước 3: Học MAC nguồn
        self.mac_to_port[dpid][src_mac] = in_port
        → Ghi nhận: MAC này đến từ cổng nào

Bước 4: Tra cứu và quyết định cổng ra
        if dst_mac in mac_to_port[dpid]:
            out_port = mac_to_port[dpid][dst_mac]   → Unicast
        else:
            out_port = OFPP_FLOOD                    → Broadcast

Bước 5: Cài flow rule (nếu unicast) + gửi PacketOut
        _add_flow(match=(in_port, src_mac, dst_mac), action=out_port)
        datapath.send_msg(OFPPacketOut)
```

### 4.4 Hàm Cài Flow Rule — `_add_flow`

```python
def _add_flow(self, datapath, priority, match, actions,
              buffer_id=None, idle_timeout=30, hard_timeout=0):
    inst = [OFPInstructionActions(OFPIT_APPLY_ACTIONS, actions)]
    mod  = OFPFlowMod(datapath, priority=priority, match=match,
                      instructions=inst, idle_timeout=30)
    datapath.send_msg(mod)
```

**Các tham số quan trọng:**

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `priority` | 0 (table-miss) / 1 (learned) | Thứ tự ưu tiên khớp rule |
| `idle_timeout` | 30 giây | Tự xóa rule nếu không có traffic trong 30s |
| `hard_timeout` | 0 | Không giới hạn thời gian tuyệt đối |
| `OFPIT_APPLY_ACTIONS` | — | Thực thi action ngay lập tức (không qua pipeline) |

---

## 5. Luồng Hoạt Động Hoàn Chỉnh

### Lần ping đầu tiên (h1 → h4, chưa học MAC)

```
h1 gửi ARP Request "ai có IP 10.0.0.4?"
  │
  ▼
s1 nhận gói, không có rule phù hợp
  │
  ▼ PacketIn
Ryu Controller:
  ├─ [LEARN]  MAC h1 (00:00:00:00:00:01) → port 1
  ├─ [FLOOD]  MAC h4 chưa biết → flood ra port 2,3,4
  └─ PacketOut → s1 flood

h4 nhận ARP, gửi ARP Reply về h1
  │
  ▼ PacketIn
Ryu Controller:
  ├─ [LEARN]  MAC h4 (00:00:00:00:00:04) → port 4
  ├─ [MATCH]  MAC h1 đã biết → port 1
  ├─ [FLOW]   Cài rule: h4→h1 via port 1
  └─ PacketOut → s1 gửi về h1

h1 nhận ARP Reply, gửi ICMP Echo
  │
  ▼ PacketIn
Ryu Controller:
  ├─ [MATCH]  MAC h4 đã biết → port 4
  ├─ [FLOW]   Cài rule: h1→h4 via port 4
  └─ PacketOut → s1 gửi đến h4
```

### Lần ping thứ hai (h1 → h4, đã có flow rule)

```
h1 gửi ICMP Echo
  │
  ▼
s1 khớp flow rule (priority=1): h1→h4 via port 4
  │
  ▼ Chuyển tiếp trực tiếp (KHÔNG lên controller)
h4 nhận gói ← RTT thấp hơn lần đầu
```

---

## 6. Bảng MAC và Flow Table Sau Khi pingall

**Bảng `mac_to_port` trong Controller:**

```
dpid=0x000000000001 (s1):
  00:00:00:00:00:01  →  port 1  (h1)
  00:00:00:00:00:02  →  port 2  (h2)
  00:00:00:00:00:03  →  port 3  (h3)
  00:00:00:00:00:04  →  port 4  (h4)
```

**Flow Table trên switch s1 (kết quả `ovs-ofctl dump-flows s1`):**

```
priority=0  actions=CONTROLLER:65535            ← table-miss
priority=1  in_port=1,dl_src=00:01,dl_dst=00:04  actions=output:4
priority=1  in_port=4,dl_src=00:04,dl_dst=00:01  actions=output:1
priority=1  in_port=1,dl_src=00:01,dl_dst=00:02  actions=output:2
...                                              ← tất cả cặp host
```

---

## 7. Kết Quả Module 2

| Hạng mục | Kết quả |
|---|---|
| File tạo ra | `controller.py` |
| Giao thức | OpenFlow 1.3 |
| Chức năng | L2 Learning Switch |
| Sự kiện xử lý | `SwitchFeatures`, `PacketIn` |
| Cơ chế học MAC | Động — ghi nhận từ PacketIn |
| Flow rule | Table-miss (priority=0) + Learned (priority=1, idle=30s) |
| Hỗ trợ đa switch | Có — phân biệt theo `dpid` |
| Trạng thái | Hoàn thành |

---

## 8. Cách Chạy

```bash
# Terminal 1: Khởi động Ryu Controller
ryu-manager controller.py

# Log mong đợi khi switch kết nối:
# [CONNECT] Switch dpid=0x0000000000000001 đã kết nối
# [FLOW]    priority=0 | match=OFPMatch() | idle_timeout=30s

# Terminal 2: Khởi động Mininet
sudo python3 topo.py
```

---

*Module 2 hoàn thành — Tiếp theo: Module 3 — Kiểm tra kết nối và quan sát flow table*
