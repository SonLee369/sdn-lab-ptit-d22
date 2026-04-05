# Báo Cáo Module 3: Kiểm Tra Kết Nối và Quan Sát Flow Table

## 1. Mục Tiêu

Module 3 thực hiện kiểm tra toàn diện hệ thống SDN sau khi khởi động Ryu Controller và Mininet, bao gồm:

- Xác nhận topology mạng được tạo đúng
- Quan sát flow table trước và sau khi có traffic
- Kiểm tra kết nối toàn mạng bằng `pingall`
- Đo độ trễ thực tế giữa các host
- Phân tích log học MAC của Ryu Controller

---

## 2. Môi Trường Thực Nghiệm

| Thành phần | Giá trị |
|---|---|
| Controller | Ryu 4.34 — `controller.py` |
| Topology | `topo.py` — Star, 1 switch + 4 hosts |
| Giao thức | OpenFlow 1.3 |
| Switch | OVS s1 — dpid=`0x0000000000000001` |
| Hosts | h1–h4, IP `10.0.0.1–4/24` |
| Link | 10 Mbps / 5ms delay |

---

## 3. Kết Quả Thực Nghiệm

### 3.1 Bước 1 — Kiểm Tra Topology

**Lệnh:**
```
mininet> net
mininet> nodes
mininet> dump
```

**Kết quả `net`:**
```
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s1-eth3
h4 h4-eth0:s1-eth4
s1 lo: s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:h3-eth0 s1-eth4:h4-eth0
ryu
```

**Kết quả `dump`:**
```
<Host h1: h1-eth0:10.0.0.1 pid=13289>
<Host h2: h2-eth0:10.0.0.2 pid=13291>
<Host h3: h3-eth0:10.0.0.3 pid=13293>
<Host h4: h4-eth0:10.0.0.4 pid=13295>
<OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None,s1-eth3:None,s1-eth4:None pid=13300>
<RemoteController ryu: 127.0.0.1:6633 pid=13454>
```

**Nhận xét:** Topology khởi động đúng theo thiết kế — 4 hosts kết nối vào switch s1, Ryu RemoteController hoạt động tại `127.0.0.1:6633`.

---

### 3.2 Bước 2 — Flow Table TRƯỚC Khi Ping

**Lệnh:**
```
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Kết quả:**
```
cookie=0x0, duration=9.476s, table=0, n_packets=23, n_bytes=1954,
priority=0 actions=CONTROLLER:65535
```

**Phân tích:**

| Trường | Giá trị | Ý nghĩa |
|---|---|---|
| `priority=0` | Thấp nhất | Rule table-miss — áp dụng khi không khớp rule nào |
| `actions=CONTROLLER:65535` | Lên controller | Gửi toàn bộ gói tin lên Ryu |
| `n_packets=23` | 23 gói | IPv4 ARP và broadcast ban đầu khi khởi động |
| `duration=9.476s` | ~9 giây | Thời gian rule đã tồn tại |

**Nhận xét:** Đúng như thiết kế — chỉ có **1 flow rule table-miss** do controller cài khi switch kết nối. Chưa có flow rule học được nào.

---

### 3.3 Bước 3 — Kiểm Tra Kết Nối Toàn Mạng

**Lệnh:**
```
mininet> pingall
```

**Kết quả:**
```
*** Ping: testing ping reachability
h1 -> h2 h3 h4
h2 -> h1 h3 h4
h3 -> h1 h2 h4
h4 -> h1 h2 h3
*** Results: 0% dropped (12/12 received)
```

**Nhận xét:** Tất cả **12 cặp host** kết nối thành công, **0% packet loss** — hệ thống SDN hoạt động đúng đắn.

---

### 3.4 Bước 4 — Flow Table SAU Khi Ping

**Lệnh:**
```
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Kết quả:**
```
cookie=0x0, duration=18.245s, table=0, n_packets=3, n_bytes=238,
  priority=1,in_port="s1-eth2",dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01
  actions=output:"s1-eth1"

cookie=0x0, duration=18.230s, table=0, n_packets=2, n_bytes=140,
  priority=1,in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02
  actions=output:"s1-eth2"

cookie=0x0, duration=18.180s, table=0, n_packets=3, n_bytes=238,
  priority=1,in_port="s1-eth3",dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:01
  actions=output:"s1-eth1"

cookie=0x0, duration=18.165s, table=0, n_packets=2, n_bytes=140,
  priority=1,in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:03
  actions=output:"s1-eth3"

cookie=0x0, duration=18.122s, table=0, n_packets=3, n_bytes=238,
  priority=1,in_port="s1-eth4",dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01
  actions=output:"s1-eth1"

cookie=0x0, duration=18.106s, table=0, n_packets=2, n_bytes=140,
  priority=1,in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:04
  actions=output:"s1-eth4"

cookie=0x0, duration=18.029s, table=0, n_packets=3, n_bytes=238,
  priority=1,in_port="s1-eth3",dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:02
  actions=output:"s1-eth2"

cookie=0x0, duration=18.014s, table=0, n_packets=2, n_bytes=140,
  priority=1,in_port="s1-eth2",dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:03
  actions=output:"s1-eth3"

cookie=0x0, duration=17.961s, table=0, n_packets=3, n_bytes=238,
  priority=1,in_port="s1-eth4",dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:02
  actions=output:"s1-eth2"

cookie=0x0, duration=17.948s, table=0, n_packets=2, n_bytes=140,
  priority=1,in_port="s1-eth2",dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:04
  actions=output:"s1-eth4"

cookie=0x0, duration=17.845s, table=0, n_packets=3, n_bytes=238,
  priority=1,in_port="s1-eth4",dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:03
  actions=output:"s1-eth3"

cookie=0x0, duration=17.831s, table=0, n_packets=2, n_bytes=140,
  priority=1,in_port="s1-eth3",dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:04
  actions=output:"s1-eth4"

cookie=0x0, duration=41.433s, table=0, n_packets=49, n_bytes=3606,
  priority=0 actions=CONTROLLER:65535
```

**Phân tích flow table:**

| Chỉ số | Giá trị |
|---|---|
| Tổng số flow rule | 13 (12 learned + 1 table-miss) |
| Flow rule priority=1 | 12 — tương ứng 6 cặp host × 2 chiều |
| Flow rule priority=0 | 1 — table-miss vẫn còn |
| idle_timeout | 0s — không bao giờ tự xóa |

**Bảng flow rule theo cặp host:**

| Chiều | Match | Action |
|---|---|---|
| h2 → h1 | in=eth2, src=02, dst=01 | output: eth1 |
| h1 → h2 | in=eth1, src=01, dst=02 | output: eth2 |
| h3 → h1 | in=eth3, src=03, dst=01 | output: eth1 |
| h1 → h3 | in=eth1, src=01, dst=03 | output: eth3 |
| h4 → h1 | in=eth4, src=04, dst=01 | output: eth1 |
| h1 → h4 | in=eth1, src=01, dst=04 | output: eth4 |
| h3 → h2 | in=eth3, src=03, dst=02 | output: eth2 |
| h2 → h3 | in=eth2, src=02, dst=03 | output: eth3 |
| h4 → h2 | in=eth4, src=04, dst=02 | output: eth2 |
| h2 → h4 | in=eth2, src=02, dst=04 | output: eth4 |
| h4 → h3 | in=eth4, src=04, dst=03 | output: eth3 |
| h3 → h4 | in=eth3, src=03, dst=04 | output: eth4 |

**Nhận xét:** Controller đã học đúng địa chỉ MAC của tất cả host và cài đặt flow rule chính xác cho **tất cả 12 chiều** giao tiếp.

---

### 3.5 Bước 5 — Đo Độ Trễ h1 → h4

**Lệnh:**
```
mininet> h1 ping h4 -c 10
```

**Kết quả:**
```
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=22.6 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=21.6 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=22.9 ms
64 bytes from 10.0.0.4: icmp_seq=4 ttl=64 time=22.7 ms
64 bytes from 10.0.0.4: icmp_seq=5 ttl=64 time=22.3 ms
64 bytes from 10.0.0.4: icmp_seq=6 ttl=64 time=21.7 ms
64 bytes from 10.0.0.4: icmp_seq=7 ttl=64 time=22.0 ms
64 bytes from 10.0.0.4: icmp_seq=8 ttl=64 time=21.6 ms
64 bytes from 10.0.0.4: icmp_seq=9 ttl=64 time=22.5 ms
64 bytes from 10.0.0.4: icmp_seq=10 ttl=64 time=22.1 ms

--- 10.0.0.4 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9011ms
rtt min/avg/max/mdev = 21.641/22.215/22.910/0.445 ms
```

**Phân tích kết quả ping:**

| Chỉ số | Giá trị | Phân tích |
|---|---|---|
| Packet loss | **0%** | Kết nối ổn định hoàn toàn |
| RTT min | 21.641 ms | Gần bằng 2× link delay (2×5ms=10ms) + overhead VM |
| RTT avg | **22.215 ms** | Ổn định, ít biến động |
| RTT max | 22.910 ms | Chênh lệch min-max chỉ 1.27ms |
| mdev | **0.445 ms** | Jitter rất thấp — mạng ổn định |

**Nhận xét:** Tất cả 10 gói tin gửi thành công. RTT trung bình ~22ms bao gồm:
- 2× link delay: 2 × 5ms = 10ms (h1→s1 và s1→h4)
- Overhead xử lý tại switch và VM: ~12ms

---

### 3.6 Log Ryu Controller — Phân Tích Quá Trình Học MAC

**Log thực tế (Terminal 1):**
```
[CONNECT] Switch dpid=0x0000000000000001 đã kết nối
[FLOW]    priority=0 | match=OFPMatch(oxm_fields={}) | idle_timeout=0s

[LEARN]   MAC 00:00:00:00:00:01 → port 1
[FLOOD]   00:00:00:00:00:01 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[LEARN]   MAC 00:00:00:00:00:02 → port 2
[MATCH]   00:00:00:00:00:02 → 00:00:00:00:00:01 via port 1
[FLOW]    priority=1 | in_port=2, eth_dst=:01, eth_src=:02 | idle_timeout=0s
[MATCH]   00:00:00:00:00:01 → 00:00:00:00:00:02 via port 2
[FLOW]    priority=1 | in_port=1, eth_dst=:02, eth_src=:01 | idle_timeout=0s
...
(tương tự cho h3, h4)
```

**Chuỗi sự kiện cho mỗi cặp host:**

```
Bước 1: h1 gửi ARP broadcast
        → [LEARN] h1 MAC → port 1
        → [FLOOD] vì chưa biết MAC đích

Bước 2: h2 gửi ARP reply về h1
        → [LEARN] h2 MAC → port 2
        → [MATCH] h1 MAC đã biết → port 1
        → [FLOW]  Cài rule h2→h1 (priority=1)

Bước 3: h1 nhận ARP reply, gửi ICMP
        → [MATCH] h2 MAC đã biết → port 2
        → [FLOW]  Cài rule h1→h2 (priority=1)

Bước 4: Mọi gói tiếp theo → switch xử lý trực tiếp
        (không lên controller nữa)
```

---

## 4. Tổng Hợp Kết Quả

| Bài kiểm tra | Lệnh | Kết quả | Đánh giá |
|---|---|---|---|
| Topology | `net` / `dump` | 4 hosts + 1 switch đúng cấu hình | Đạt |
| Flow table trước ping | `dump-flows` | 1 rule table-miss | Đạt |
| Kết nối toàn mạng | `pingall` | **0% dropped (12/12)** | Đạt |
| Flow table sau ping | `dump-flows` | 12 learned rules + 1 table-miss | Đạt |
| Độ trễ h1→h4 | `ping -c 10` | **RTT avg=22.215ms, 0% loss** | Đạt |
| Học MAC | Ryu log | 4 MAC học đúng, 12 flow rules cài đúng | Đạt |

---

## 5. Lỗi Phát Sinh và Cách Sửa

### Lỗi 1 — Flow rules tự xóa sau 30 giây (`idle_timeout`)

| | Chi tiết |
|---|---|
| **Biểu hiện** | `dump-flows` trả về rỗng; `h1 ping h4` → 100% packet loss |
| **Nguyên nhân** | `idle_timeout=30s` — flow rules bị xóa khi không có traffic trong 30 giây |
| **Cách sửa** | Đổi `idle_timeout=30` thành `idle_timeout=0` trong `_add_flow()` |

### Lỗi 2 — IPv6 Multicast Flood Storm

| | Chi tiết |
|---|---|
| **Biểu hiện** | Hàng chục log `[FLOOD] → 33:33:xx:xx:xx:xx` làm nghẽn controller |
| **Nguyên nhân** | Linux kernel tự phát sinh gói MLD/Neighbor Discovery với MAC đích `33:33:xx` |
| **Cách sửa** | Thêm filter: `if dst_mac.startswith('33:33'): return` trong `packet_in_handler` |

### Lỗi 3 — NameError: `dst_mac` dùng trước khi khai báo

| | Chi tiết |
|---|---|
| **Biểu hiện** | `NameError: name 'dst_mac' is not defined` |
| **Nguyên nhân** | Filter IPv6 (`if dst_mac.startswith(...)`) đặt trước dòng `dst_mac = eth_pkt.dst` |
| **Cách sửa** | Di chuyển `src_mac / dst_mac` lên trước khối filter |

---

## 6. Kết Luận Module 3

Module 3 xác nhận hệ thống SDN hoạt động đúng đắn và đầy đủ:

- **Topology** được khởi tạo chính xác theo thiết kế Star
- **Controller** học MAC tự động và cài flow rules động
- **Kết nối** đạt 0% packet loss trên toàn mạng (12/12 cặp)
- **Độ trễ** ổn định: RTT avg = 22.215ms, jitter = 0.445ms
- **Flow table** phản ánh đúng trạng thái mạng học được

---

*Module 3 hoàn thành — Tiếp theo: Module 4 — Đo hiệu năng mạng (iperf3)*
