# Lab 3: VXLAN trên nền SDN với Mininet và Open vSwitch

**Môn học:** Mạng định nghĩa bằng phần mềm (Software Defined Networking)
**Công cụ:** Mininet + Open vSwitch (OVS)
**Ngày thực hiện:** 30/03/2026

---

## Mục lục

1. [Cơ sở lý thuyết](#1-cơ-sở-lý-thuyết)
2. [Thiết kế topology](#2-thiết-kế-topology)
3. [Script Mininet](#3-script-mininet)
4. [Cấu hình VXLAN](#4-cấu-hình-vxlan)
5. [Kiểm tra kết nối](#5-kiểm-tra-kết-nối)
6. [Bắt và phân tích gói tin](#6-bắt-và-phân-tích-gói-tin)
7. [Kết luận](#7-kết-luận)

---

## 1. Cơ sở lý thuyết

### 1.1 VXLAN là gì?

**VXLAN (Virtual Extensible LAN)** là công nghệ ảo hóa mạng được định nghĩa trong [RFC 7348](https://datatracker.ietf.org/doc/html/rfc7348). VXLAN đóng gói (encapsulate) các frame Ethernet Layer 2 bên trong gói tin UDP/IP, cho phép mạng Layer 2 ảo được kéo dài qua hạ tầng mạng Layer 3 (underlay).

Các đặc điểm chính:

- **VNI (VXLAN Network Identifier):** Định danh segment 24-bit (hỗ trợ ~16 triệu mạng ảo, so với 4096 của VLAN)
- **VTEP (VXLAN Tunnel Endpoint):** Thiết bị thực hiện đóng gói / mở gói VXLAN
- **Cổng UDP:** 4789 (chuẩn IANA)
- **Đóng gói:** Ethernet frame → VXLAN header → UDP → IP → Ethernet (underlay)

#### Cấu trúc gói tin VXLAN

```
+------------------+
|  Outer Ethernet  |  (Underlay L2)
+------------------+
|    Outer IP      |  (Underlay L3 — địa chỉ nguồn/đích VTEP)
+------------------+
|    Outer UDP     |  (cổng đích: 4789)
+------------------+
|  VXLAN Header    |  (8 bytes — chứa VNI 24-bit)
+------------------+
|  Inner Ethernet  |  (Frame L2 gốc — Overlay)
+------------------+
|  Inner IP/Data   |  (Payload gốc)
+------------------+
```

---

### 1.2 Tại sao dùng VXLAN?

| Hạn chế (Mạng truyền thống)       | Giải pháp VXLAN             |
| --------------------------------- | --------------------------- |
| VLAN giới hạn 4096 ID             | VNI hỗ trợ 16 triệu ID      |
| L2 bị giới hạn trong cùng miền L2 | L2 chạy trên bất kỳ mạng L3 |
| Phân tách multi-tenant kém        | Cô lập theo từng VNI        |
| STP giới hạn khả năng mở rộng     | Không dùng STP ở underlay   |

VXLAN được sử dụng rộng rãi trong **data center overlay**, **cloud networking** (AWS VPC, OpenStack Neutron) và **mở rộng L2 đa site**.

---

### 1.3 SDN là gì?

**SDN (Software Defined Networking)** tách biệt **control plane** (mặt điều khiển) khỏi **data plane** (mặt chuyển tiếp dữ liệu):

```
Mạng truyền thống:            Mạng SDN:
+------------------+          +------------------+
| Control + Data   |          |  SDN Controller  |  ← Điều khiển tập trung
| (mỗi thiết bị)   |          +--------+---------+
+------------------+                   |
                                        | OpenFlow / REST API
                              +---------+---------+
                              | Switch (Data Plane)|  ← Chỉ chuyển tiếp
                              +-------------------+
```

**Các khái niệm SDN dùng trong bài lab:**

- **OpenFlow:** Giao thức giữa controller và switch
- **OVS (Open vSwitch):** Switch phần mềm hỗ trợ OpenFlow + VXLAN
- **Flow table:** Bảng luật định nghĩa cách chuyển tiếp gói tin

---

### 1.4 Open vSwitch (OVS) và VXLAN

OVS là switch phần mềm mã nguồn mở, đa lớp, được dùng trong Mininet. OVS hỗ trợ:

- OpenFlow 1.0 – 1.5
- VXLAN tunnel interface (type `vxlan`)
- GRE, GENEVE và các giao thức overlay khác

Trong bài lab này, OVS đóng vai trò **VTEP** — tự động đóng gói và mở gói VXLAN khi được thêm tunnel port.

**Lệnh OVS quan trọng cho VXLAN:**

```bash
# Thêm VXLAN tunnel port vào bridge
ovs-vsctl add-port <bridge> <tên-port> \
  -- set interface <tên-port> type=vxlan \
  options:local_ip=<địa_chỉ_VTEP_local> \
  options:remote_ip=<địa_chỉ_VTEP_remote> \
  options:key=<VNI>
```

---

### 1.5 Tổng quan Mininet

**Mininet** mô phỏng mạng gồm host, switch, controller và liên kết trên một máy Linux duy nhất, sử dụng ảo hóa nhẹ (network namespace + veth pair).

Trong bài lab này, Mininet được dùng để:

1. Mô phỏng hai OVS switch đóng vai trò VTEP
2. Gắn host vào mỗi switch
3. Mô phỏng mạng IP underlay giữa hai switch
4. Cấu hình VXLAN overlay bên trên

---

### 1.6 Mục tiêu bài lab

Sau khi hoàn thành bài lab, sinh viên có thể:

1. Giải thích quá trình đóng gói VXLAN và vai trò của VTEP
2. Cấu hình VXLAN tunnel trên OVS bằng `ovs-vsctl`
3. Xây dựng topology Mininet có VXLAN overlay
4. Xác minh kết nối L2 qua mạng underlay L3 mô phỏng
5. Bắt và phân tích gói tin được đóng gói VXLAN

---

## 2. Thiết kế Topology

### 2.1 Tổng quan thiết kế

Bài lab sử dụng mô hình **hai VTEP**: hai OVS switch đóng vai trò VTEP, mỗi switch kết nối với một host. Hai switch được nối với nhau qua một **mạng underlay Layer 3** mô phỏng. Tunnel VXLAN với VNI 100 kéo dài một segment Layer 2 qua cả hai switch, khiến các host ở hai switch khác nhau hoạt động như ở cùng một LAN.

---

### 2.2 Sơ đồ topology

#### Topology đầy đủ (Underlay + Overlay)

```
 OVERLAY (VNI 100) — 192.168.100.0/24
 ┌─────────────────────────────────────────────────────┐
 │                                                     │
 │  h1                                             h2  │
 │  192.168.100.1/24                 192.168.100.2/24  │
 └──────┬──────────────────────────────────┬───────────┘
        │  (veth)                  (veth)  │
   ┌────┴─────┐   VXLAN Tunnel   ┌─────────┴────┐
   │   OVS    │==================│     OVS      │
   │    s1    │  UDP:4789 VNI100 │      s2      │
   │  (VTEP)  │                  │    (VTEP)    │
   └────┬─────┘                  └──────┬───────┘
        │ 10.0.0.1/24        10.0.0.2/24│
        └──────────────┬─────────────────┘
                       │
              UNDERLAY LINK
              10.0.0.0/24
```

#### Phân tầng logic

```
┌──────────────────────────────────────────────┐
│        TẦNG OVERLAY (L2 over VXLAN)          │
│   h1 ←──────────── VNI 100 ───────────→ h2  │
│   192.168.100.1                192.168.100.2  │
└──────────────────────────────────────────────┘
                    ↕ đóng gói / mở gói
┌──────────────────────────────────────────────┐
│        TẦNG UNDERLAY (mạng IP L3)            │
│   s1-VTEP (10.0.0.1) ←──→ s2-VTEP(10.0.0.2)│
└──────────────────────────────────────────────┘
```

---

### 2.3 Bảng địa chỉ IP

#### Mạng Underlay

| Thiết bị | Interface   | Địa chỉ IP  | Vai trò       |
| -------- | ----------- | ----------- | ------------- |
| s1       | s1 (bridge) | 10.0.0.1/24 | IP nguồn VTEP |
| s2       | s2 (bridge) | 10.0.0.2/24 | IP nguồn VTEP |

#### Mạng Overlay (VNI 100)

| Thiết bị | Interface | Địa chỉ IP       | MAC                |
| -------- | --------- | ---------------- | ------------------ |
| h1       | h1-eth0   | 192.168.100.1/24 | Tự gán bởi Mininet |
| h2       | h2-eth0   | 192.168.100.2/24 | Tự gán bởi Mininet |

#### Thông số VXLAN Tunnel

| Tham số     | Giá trị        |
| ----------- | -------------- |
| VNI         | 100            |
| Cổng UDP    | 4789           |
| VTEP 1 (s1) | 10.0.0.1       |
| VTEP 2 (s2) | 10.0.0.2       |
| Kiểu tunnel | Point-to-point |

---

### 2.4 Vai trò các thành phần

| Thành phần    | Loại           | Vai trò                               |
| ------------- | -------------- | ------------------------------------- |
| `h1`          | Mininet Host   | Điểm cuối overlay — sinh traffic      |
| `h2`          | Mininet Host   | Điểm cuối overlay — nhận traffic      |
| `s1`          | OVS Bridge     | VTEP — đóng gói frame từ h1 vào VXLAN |
| `s2`          | OVS Bridge     | VTEP — mở gói VXLAN và chuyển đến h2  |
| `vxlan0` (s1) | OVS VXLAN port | Tunnel port trên s1, trỏ đến s2       |
| `vxlan0` (s2) | OVS VXLAN port | Tunnel port trên s2, trỏ đến s1       |

---

### 2.5 Luồng traffic (h1 → h2)

```
Bước 1: h1 gửi Ethernet frame đến h2 (192.168.100.2)
   └─→ Frame đến s1 qua port h1-eth0

Bước 2: s1 (VTEP) tra cứu MAC đích → ánh xạ đến VXLAN tunnel port
   └─→ s1 đóng gói frame:
        [ Outer IP: 10.0.0.1→10.0.0.2 | UDP:4789 | VNI:100 | Inner Frame ]

Bước 3: Gói tin đóng gói đi qua underlay (10.0.0.0/24)
   └─→ Đến s2 tại địa chỉ 10.0.0.2

Bước 4: s2 (VTEP) nhận gói UDP:4789 → gỡ VXLAN header
   └─→ Chuyển frame Ethernet gốc đến h2
```

---

### 2.6 Quyết định thiết kế

| Quyết định     | Lựa chọn              | Lý do                                                          |
| -------------- | --------------------- | -------------------------------------------------------------- |
| Loại underlay  | Liên kết L3 trực tiếp | Đơn giản, không cần router trong Mininet                       |
| Chế độ tunnel  | Point-to-point        | Dễ cấu hình, không cần multicast                               |
| VNI            | 100                   | Tùy chọn; một segment đủ để minh họa                           |
| Subnet overlay | 192.168.100.0/24      | Dải private, tách biệt rõ với underlay                         |
| Số host/switch | 1                     | Tối giản hóa độ phức tạp trong khi vẫn minh họa được khái niệm |

---

## 3. Script Mininet

### 3.1 Tổng quan script

File `topology.py` xây dựng toàn bộ môi trường lab theo chương trình. Sau khi `net.start()`, script thực hiện bốn bước:

| Bước | Hành động                                                 |
| ---- | --------------------------------------------------------- |
| 1    | Gán IP underlay (`10.0.0.x`) cho interface của OVS bridge |
| 2    | Kiểm tra kết nối underlay bằng ping 2 gói                 |
| 3    | Thêm VXLAN tunnel port (`vxlan0`) vào cả hai bridge       |
| 4    | Mở Mininet CLI để kiểm thử                                |

---

### 3.2 Các lựa chọn thiết kế chính trong script

#### OVSBridge với `failMode='standalone'`

```python
s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
```

- `OVSBridge` tạo OVS bridge không cần controller OpenFlow bên ngoài.
- `failMode='standalone'` bật chế độ học MAC tự động — OVS flood frame khi chưa biết MAC đích và học dần từ traffic, hoạt động như switch L2 thông thường.

#### Gán IP underlay cho interface bridge

```python
s1.cmd('ip addr add 10.0.0.1/24 dev s1')
```

- Gán IP trực tiếp cho interface của OVS bridge (không phải port vật lý).
- Linux kernel dùng IP này làm **địa chỉ nguồn VTEP** khi đóng gói VXLAN.
- Cả hai VTEP cùng `/24` nên có thể liên lạc trực tiếp không qua router.

#### Cấu hình VXLAN port

```bash
ovs-vsctl add-port s1 vxlan0
  -- set interface vxlan0 type=vxlan
  options:local_ip=10.0.0.1
  options:remote_ip=10.0.0.2
  options:key=100
  options:dst_port=4789
```

- `type=vxlan`: OVS nhận diện đây là VXLAN tunnel interface.
- `local_ip` / `remote_ip`: định nghĩa cặp VTEP hai đầu tunnel.
- `key=100`: đặt giá trị VNI.
- `dst_port=4789`: cổng UDP chuẩn IANA cho VXLAN.

---

### 3.3 Script đầy đủ (`topology.py`)

```python
#!/usr/bin/env python3
"""
Lab 3: VXLAN over SDN with Mininet + OVS
Topology:
    h1 (192.168.100.1) --- s1 (VTEP: 10.0.0.1)
                               ||  VXLAN VNI 100 (UDP 4789)
    h2 (192.168.100.2) --- s2 (VTEP: 10.0.0.2)
"""

from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

UNDERLAY_S1   = '10.0.0.1'
UNDERLAY_S2   = '10.0.0.2'
UNDERLAY_MASK = '24'
OVERLAY_H1    = '192.168.100.1'
OVERLAY_H2    = '192.168.100.2'
OVERLAY_MASK  = '24'
VNI           = '100'
VXLAN_PORT    = '4789'

def add_vxlan_port(switch, port_name, local_ip, remote_ip, vni):
    switch.cmd(
        f'ovs-vsctl add-port {switch.name} {port_name}'
        f' -- set interface {port_name} type=vxlan'
        f' options:local_ip={local_ip}'
        f' options:remote_ip={remote_ip}'
        f' options:key={vni}'
        f' options:dst_port={VXLAN_PORT}'
    )

def build_topology():
    net = Mininet(controller=None, link=TCLink)

    h1 = net.addHost('h1', ip=f'{OVERLAY_H1}/{OVERLAY_MASK}')
    h2 = net.addHost('h2', ip=f'{OVERLAY_H2}/{OVERLAY_MASK}')

    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')

    net.addLink(h1, s1)   # overlay: h1 → s1
    net.addLink(h2, s2)   # overlay: h2 → s2
    net.addLink(s1, s2)   # underlay: s1 ↔ s2

    net.start()

    # Bước 1: Gán IP underlay
    s1.cmd(f'ip addr add {UNDERLAY_S1}/{UNDERLAY_MASK} dev s1')
    s2.cmd(f'ip addr add {UNDERLAY_S2}/{UNDERLAY_MASK} dev s2')
    s1.cmd('ip link set s1 up')
    s2.cmd('ip link set s2 up')

    # Bước 2: Kiểm tra underlay
    result = s1.cmd(f'ping -c 2 -W 2 {UNDERLAY_S2}')
    if '2 received' in result or '1 received' in result:
        info('[OK] Underlay có thể liên lạc\n')
    else:
        info('[WARN] Ping underlay thất bại\n')

    # Bước 3: Thêm VXLAN tunnel port
    add_vxlan_port(s1, 'vxlan0', UNDERLAY_S1, UNDERLAY_S2, VNI)
    add_vxlan_port(s2, 'vxlan0', UNDERLAY_S2, UNDERLAY_S1, VNI)

    info('\n' + '='*55 + '\n')
    info('  Topology đã sẵn sàng!\n')
    info(f'  Underlay : s1={UNDERLAY_S1}  s2={UNDERLAY_S2}\n')
    info(f'  Overlay  : h1={OVERLAY_H1}  h2={OVERLAY_H2}\n')
    info(f'  VXLAN    : VNI={VNI}  UDP={VXLAN_PORT}\n')
    info('='*55 + '\n\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
```

---

### 3.4 Cách chạy script

```bash
# Phải chạy với quyền root (Mininet yêu cầu)
sudo python3 topology.py
```

Kết quả khởi động mong đợi:

```
*** Adding hosts
*** Adding OVS bridges (VTEPs)
*** Adding links
*** Starting network
*** Assigning underlay IPs: s1=10.0.0.1, s2=10.0.0.2
*** Testing underlay connectivity (s1 → s2)
    [OK] Underlay có thể liên lạc
*** Adding VXLAN tunnel ports (VNI=100)
=======================================================
  Topology đã sẵn sàng!
  Underlay : s1=10.0.0.1  s2=10.0.0.2
  Overlay  : h1=192.168.100.1  h2=192.168.100.2
  VXLAN    : VNI=100  UDP=4789
=======================================================

mininet>
```

---

### 3.5 Các lệnh Mininet CLI hữu ích

| Lệnh                         | Mục đích                              |
| ---------------------------- | ------------------------------------- |
| `pingall`                    | Kiểm tra kết nối giữa tất cả các host |
| `h1 ping -c 3 192.168.100.2` | Ping h2 từ h1                         |
| `h1 ifconfig`                | Hiển thị interface mạng của h1        |
| `sh ovs-vsctl show`          | Xem cấu hình OVS bridge và port       |
| `sh ovs-ofctl dump-flows s1` | Xem bảng flow trên s1                 |
| `h1 arp -n`                  | Xem bảng ARP của h1                   |
| `exit`                       | Thoát CLI và dọn dẹp topology         |

---

## 4. Cấu hình VXLAN

### 4.1 Tổng quan các bước cấu hình

Cấu hình VXLAN trên OVS gồm **3 giai đoạn chính**:

```
Giai đoạn 1          Giai đoạn 2              Giai đoạn 3
─────────────        ─────────────────        ─────────────────
Gán IP underlay  →   Thêm VXLAN tunnel  →     Xác minh tunnel
cho OVS bridge        port vào bridge          và flow table
```

Trong bài lab này, các bước trên được thực hiện **tự động** bởi `topology.py`. File `vxlan_setup.sh` đóng gói lại toàn bộ các lệnh thủ công để tiện tham khảo và chạy độc lập.

---

### 4.2 Giai đoạn 1 — Tách underlay veth khỏi OVS bridge và gán VTEP IP

> **Vấn đề quan trọng — L2 Loop:** Nếu gán IP cho bridge interface (`dev s1`) trong khi `s1-eth2` vẫn nằm trong OVS bridge, thì s1 và s2 sẽ có **hai đường L2 song song**:
> - Đường vật lý: `s1-eth2 ↔ s2-eth2` (cả hai trong OVS bridge)
> - Đường tunnel: `vxlan0 ↔ vxlan1` (VXLAN over UDP)
>
> OVS ở chế độ standalone sẽ **flood ra tất cả port** khi chưa biết MAC đích → frame đi vòng lặp vô tận → **broadcast storm** → overlay ping 100% packet loss.

**Giải pháp:** Rút `s1-eth2` và `s2-eth2` ra khỏi OVS bridge, gán VTEP IP trực tiếp lên các veth interface thuần (kernel). Khi đó OVS bridge chỉ còn:
- s1: `s1-eth1` (h1) + `vxlan0` (tunnel) → không còn đường vật lý trực tiếp đến s2
- s2: `s2-eth1` (h2) + `vxlan1` (tunnel) → không còn đường vật lý trực tiếp đến s1

```bash
# Bước 1: Rút underlay veth ra khỏi OVS bridge
ovs-vsctl del-port s1 s1-eth2
ovs-vsctl del-port s2 s2-eth2

# Bước 2: Gán VTEP IP cho raw veth interface (không phải bridge interface)
ip addr add 10.0.0.1/24 dev s1-eth2
ip link set s1-eth2 up

ip addr add 10.0.0.2/24 dev s2-eth2
ip link set s2-eth2 up
```

**Giải thích:**

- `s1-eth2` và `s2-eth2` sau khi rút khỏi OVS bridge trở thành **interface kernel thuần** — được dùng chỉ cho VXLAN UDP transport.
- Linux kernel dùng IP `10.0.0.1` (trên `s1-eth2`) làm địa chỉ nguồn VTEP khi đóng gói VXLAN.
- Hai interface này kết nối trực tiếp qua veth pair → cùng `/24` → không cần routing.

**Kiểm tra ngay sau khi gán:**

```bash
# Kiểm tra IP đã gán trên veth
ip addr show s1-eth2
ip addr show s2-eth2

# Kiểm tra kết nối underlay
ping -c 3 10.0.0.2
```

Kết quả mong đợi:

```
3 packets transmitted, 3 received, 0% packet loss
```

---

### 4.3 Giai đoạn 2 — Thêm VXLAN Tunnel Port

> **Lưu ý quan trọng:** OVS yêu cầu tên interface **duy nhất toàn cục** trên cùng một OVS instance. Hai bridge s1 và s2 **không thể** cùng dùng tên `vxlan0`. Do đó s1 dùng `vxlan0`, s2 dùng `vxlan1`.

#### Thêm VXLAN port vào s1 (VTEP 1) — port tên `vxlan0`

```bash
ovs-vsctl add-port s1 vxlan0 \
    -- set interface vxlan0 \
       type=vxlan \
       options:local_ip=10.0.0.1 \
       options:remote_ip=10.0.0.2 \
       options:key=100 \
       options:dst_port=4789
```

#### Thêm VXLAN port vào s2 (VTEP 2) — port tên `vxlan1`

```bash
ovs-vsctl add-port s2 vxlan1 \
    -- set interface vxlan1 \
       type=vxlan \
       options:local_ip=10.0.0.2 \
       options:remote_ip=10.0.0.1 \
       options:key=100 \
       options:dst_port=4789
```

**Giải thích từng tham số:**

| Tham số      | Giá trị  | Ý nghĩa                                     |
| ------------ | -------- | ------------------------------------------- |
| `type=vxlan` | vxlan    | Loại tunnel — OVS xử lý đóng/mở gói tự động |
| `local_ip`   | 10.0.0.x | IP nguồn của VTEP (outer IP header)         |
| `remote_ip`  | 10.0.0.x | IP đích của VTEP đối diện                   |
| `key`        | 100      | VNI — định danh mạng overlay (24-bit)       |
| `dst_port`   | 4789     | Cổng UDP đích chuẩn IANA cho VXLAN          |

---

### 4.4 Giai đoạn 3 — Xác minh cấu hình

#### Kiểm tra toàn bộ cấu hình OVS

```bash
sh ovs-vsctl show
```

Kết quả mong đợi:

```
Bridge s1
    Port s1
        Interface s1
            type: internal
    Port h1-eth0       ← port kết nối với h1
        Interface h1-eth0
    Port s1-eth2       ← port underlay nối với s2
        Interface s1-eth2
    Port vxlan0        ← VXLAN tunnel port
        Interface vxlan0
            type: vxlan
            options: {dst_port="4789", key="100",
                      local_ip="10.0.0.1", remote_ip="10.0.0.2"}

Bridge s2
    Port s2
        Interface s2
            type: internal
    Port h2-eth0
        Interface h2-eth0
    Port s2-eth2
        Interface s2-eth2
    Port vxlan1            ← tên khác vxlan0 vì OVS yêu cầu tên duy nhất toàn cục
        Interface vxlan1
            type: vxlan
            options: {dst_port="4789", key="100",
                      local_ip="10.0.0.2", remote_ip="10.0.0.1"}
```

#### Kiểm tra trạng thái tunnel port

```bash
# Xem thông tin chi tiết interface vxlan0
sh ovs-vsctl list interface vxlan0
```

Chú ý trường `link_state`: nếu là `up` thì tunnel đang hoạt động.

#### Xem flow table

```bash
# Flow table trên s1
sh ovs-ofctl dump-flows s1

# Flow table trên s2
sh ovs-ofctl dump-flows s2
```

Trong `failMode='standalone'`, OVS tự sinh flow khi có traffic. Ban đầu bảng flow sẽ trống, sau khi ping sẽ có các entry học được.

---

### 4.5 Script `vxlan_setup.sh`

File `vxlan_setup.sh` thực hiện toàn bộ 8 bước cấu hình có kiểm tra và thông báo màu:

| Bước | Nội dung                              |
| ---- | ------------------------------------- |
| 1    | Kiểm tra `ovs-vsctl` và OVS daemon    |
| 2    | Gán IP underlay cho s1 và s2          |
| 3    | Ping kiểm tra underlay                |
| 4    | Xóa VXLAN port cũ (nếu có)            |
| 5    | Thêm VXLAN port vào s1                |
| 6    | Thêm VXLAN port vào s2                |
| 7    | Hiển thị `ovs-vsctl show` để xác minh |
| 8    | Hiển thị flow table của cả hai bridge |

**Cách chạy:**

```bash
# Chạy sau khi topology.py đã khởi động
sudo bash vxlan_setup.sh

# Hoặc từ Mininet CLI
mininet> sh bash vxlan_setup.sh
```

---

### 4.6 Xử lý lỗi thường gặp

| Triệu chứng                                              | Nguyên nhân                                                                | Cách xử lý                                           |
| -------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------- |
| `ovs-vsctl: no bridge named s1`                          | topology.py chưa chạy                                                      | Chạy `sudo python3 topology.py` trước                |
| Ping underlay thất bại                                   | IP chưa gán hoặc bridge chưa up                                            | Kiểm tra `ip addr show s1` và `ip link show s1`      |
| `cannot create port vxlan0, already exists on bridge s1` | Dùng cùng tên `vxlan0` cho cả s1 và s2 — OVS yêu cầu tên duy nhất toàn cục | Dùng tên khác nhau: `vxlan0` cho s1, `vxlan1` cho s2 |
| `interface vxlan0 already exists`                        | Port đã được thêm từ lần chạy trước                                        | Xóa bằng `ovs-vsctl del-port s1 vxlan0` rồi thêm lại |
| Ping overlay thất bại sau khi cấu hình                   | VNI không khớp giữa hai đầu                                                | Kiểm tra `options:key` phải giống nhau trên s1 và s2 |
| `link_state: down`                                       | remote_ip không truy cập được                                              | Ping underlay lại, kiểm tra IP bridge                |

---

---

## 5. Kiểm tra kết nối

### 5.1 Quy trình kiểm tra

Việc kiểm tra được thực hiện theo **3 lớp từ dưới lên**:

```
Lớp 3 — Overlay ping (h1 ↔ h2)          ← mục tiêu cuối cùng
   ↑
Lớp 2 — ARP & MAC learning trên OVS
   ↑
Lớp 1 — Underlay IP (s1 ↔ s2)           ← kiểm tra trước tiên
```

Nếu lớp dưới thất bại, lớp trên sẽ không hoạt động.

---

### 5.2 Kiểm tra Lớp 1 — Underlay IP (s1 ↔ s2)

Mục đích: xác nhận hai VTEP có thể liên lạc qua mạng underlay trước khi tunnel VXLAN hoạt động.

#### Lệnh kiểm tra

```bash
# Từ Mininet CLI — chạy lệnh trực tiếp trên host namespace
mininet> sh ping -c 3 10.0.0.2
```

#### Kết quả mong đợi

```
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.XXX ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.XXX ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.XXX ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

#### Kiểm tra bảng định tuyến underlay

```bash
mininet> sh ip route show
```

Kết quả mong đợi — phải có route đến `10.0.0.0/24`:

```
10.0.0.0/24 dev s1  proto kernel  scope link  src 10.0.0.1
10.0.0.0/24 dev s2  proto kernel  scope link  src 10.0.0.2
```

---

### 5.3 Kiểm tra Lớp 2 — Cấu hình VXLAN tunnel

Trước khi ping overlay, xác nhận VXLAN đã được cấu hình đúng.

#### Xem toàn bộ cấu hình OVS

```bash
mininet> sh ovs-vsctl show
```

Kết quả mong đợi — phải thấy `vxlan0` trên s1 và `vxlan1` trên s2:

```
Bridge s1
    Port vxlan0
        Interface vxlan0
            type: vxlan
            options: {dst_port="4789", key="100",
                      local_ip="10.0.0.1", remote_ip="10.0.0.2"}
    Port h1-s1
        Interface h1-s1
    ...
Bridge s2
    Port vxlan1
        Interface vxlan1
            type: vxlan
            options: {dst_port="4789", key="100",
                      local_ip="10.0.0.2", remote_ip="10.0.0.1"}
    Port h2-s2
        Interface h2-s2
    ...
```

#### Kiểm tra interface của h1 và h2

```bash
mininet> h1 ifconfig
mininet> h2 ifconfig
```

Xác nhận h1 có IP `192.168.100.1/24` và h2 có `192.168.100.2/24`.

---

### 5.4 Kiểm tra Lớp 3 — Overlay ping (h1 ↔ h2)

Đây là bài kiểm tra chính — xác nhận L2 overlay hoạt động qua VXLAN.

#### Test 1: Ping đơn từ h1 đến h2

```bash
mininet> h1 ping -c 5 192.168.100.2
```

Kết quả mong đợi:

```
PING 192.168.100.2 (192.168.100.2) 56(84) bytes of data.
64 bytes from 192.168.100.2: icmp_seq=1 ttl=64 time=X.XXX ms
64 bytes from 192.168.100.2: icmp_seq=2 ttl=64 time=X.XXX ms
64 bytes from 192.168.100.2: icmp_seq=3 ttl=64 time=X.XXX ms
64 bytes from 192.168.100.2: icmp_seq=4 ttl=64 time=X.XXX ms
64 bytes from 192.168.100.2: icmp_seq=5 ttl=64 time=X.XXX ms

--- 192.168.100.2 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss
```

> Gói đầu tiên (icmp_seq=1) có thể mất do ARP chưa học — đây là bình thường.

#### Test 2: Ping ngược từ h2 đến h1

```bash
mininet> h2 ping -c 3 192.168.100.1
```

#### Test 3: pingall — kiểm tra toàn bộ

```bash
mininet> pingall
```

Kết quả mong đợi:

```
*** Ping: testing ping reachability
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
```

---

### 5.5 Kiểm tra ARP và MAC Learning

Sau khi ping thành công, OVS đã học được địa chỉ MAC. Kiểm tra kết quả học:

#### Bảng ARP trên h1

```bash
mininet> h1 arp -n
```

Kết quả mong đợi:

```
Address                  HWtype  HWaddress           Flags Mask
192.168.100.2            ether   XX:XX:XX:XX:XX:XX   C
```

#### Bảng MAC (FDB) trên OVS bridge s1

```bash
mininet> sh ovs-appctl fdb/show s1
```

Kết quả mong đợi:

```
 port  VLAN  MAC                Age
    1     0  XX:XX:XX:XX:XX:XX    5   ← MAC của h1 (port h1-s1)
    3     0  XX:XX:XX:XX:XX:XX    5   ← MAC của h2 (học qua tunnel vxlan0)
```

MAC của h2 được học qua port `vxlan0` — xác nhận traffic đã đi qua VXLAN tunnel.

---

### 5.6 Kiểm tra flow table sau khi có traffic

```bash
mininet> sh ovs-ofctl dump-flows s1
mininet> sh ovs-ofctl dump-flows s2
```

Sau khi ping, OVS standalone sẽ tự sinh flow entry. Ví dụ:

```
cookie=0x0, ..., in_port=1, dl_src=XX:XX:XX:XX:XX:XX,
    dl_dst=YY:YY:YY:YY:YY:YY, actions=output:3

cookie=0x0, ..., in_port=3, dl_src=YY:YY:YY:YY:YY:YY,
    dl_dst=XX:XX:XX:XX:XX:XX, actions=output:1
```

> `in_port=1` → port của h1; `output:3` → port `vxlan0` (tunnel)

---

### 5.7 Tổng hợp kết quả kiểm tra

| Bài kiểm tra | Lệnh | Kết quả mong đợi |
|---|---|---|
| Underlay ping | `sh ping -c 3 10.0.0.2` | 0% packet loss |
| OVS config | `sh ovs-vsctl show` | Thấy vxlan0 (s1) và vxlan1 (s2) |
| h1 interface | `h1 ifconfig` | IP 192.168.100.1/24 |
| h2 interface | `h2 ifconfig` | IP 192.168.100.2/24 |
| Overlay ping h1→h2 | `h1 ping -c 5 192.168.100.2` | 0% packet loss |
| Overlay ping h2→h1 | `h2 ping -c 3 192.168.100.1` | 0% packet loss |
| Toàn mạng | `pingall` | 0% dropped (2/2 received) |
| ARP h1 | `h1 arp -n` | MAC của h2 xuất hiện |
| MAC table | `sh ovs-appctl fdb/show s1` | MAC h2 học qua port vxlan0 |

---

### 5.8 Xử lý sự cố nếu overlay ping thất bại

#### Dấu hiệu broadcast storm (lỗi nghiêm trọng nhất)

Nếu gặp tình trạng sau, nguyên nhân là **L2 forwarding loop**:
- `h1 ping 192.168.100.2` → 100% packet loss
- `h1 ifconfig` → RX packets hàng trăm triệu (GB) nhưng TX rất ít
- `sh ovs-appctl fdb/show s1` → MAC của h1 nằm trên port **vxlan0** (không phải port local)

**Nguyên nhân:** `s1-eth2` và `s2-eth2` vẫn còn trong OVS bridge, tạo thành hai đường L2 song song với VXLAN tunnel:

```
s1 ←─── s1-eth2 (physical, trong OVS) ───→ s2
s1 ←─── vxlan0/vxlan1 (VXLAN tunnel)  ───→ s2
         ↑
   OVS flood ra cả hai → vòng lặp vô tận
```

**Cách sửa:**

```bash
# Rút underlay veth ra khỏi OVS bridge
mininet> sh ovs-vsctl del-port s1 s1-eth2
mininet> sh ovs-vsctl del-port s2 s2-eth2

# Gán VTEP IP cho raw veth (không phải bridge interface)
mininet> sh ip addr add 10.0.0.1/24 dev s1-eth2
mininet> sh ip addr add 10.0.0.2/24 dev s2-eth2
mininet> sh ip link set s1-eth2 up
mininet> sh ip link set s2-eth2 up

# Thử ping lại
mininet> h1 ping -c 3 192.168.100.2
```

---

#### Quy trình debug tổng quát

```
Bước 1: sh ping 10.0.0.2              → Nếu fail: veth chưa có IP hoặc link down
   ↓
Bước 2: sh ovs-vsctl show             → Kiểm tra s1-eth2 KHÔNG có trong bridge s1
   ↓
Bước 3: sh ip addr show s1-eth2       → Kiểm tra VTEP IP 10.0.0.1/24
   ↓
Bước 4: sh ovs-appctl fdb/show s1     → MAC của h1 phải trên port local (không phải vxlan0)
   ↓
Bước 5: h1 ping -c 5 192.168.100.2   → Overlay phải thông
```

| Triệu chứng | Nguyên nhân | Giải pháp |
|---|---|---|
| 100% loss + RX hàng triệu gói trên h1 | L2 loop — s1-eth2 vẫn trong OVS bridge | `ovs-vsctl del-port s1 s1-eth2` (và s2) |
| Underlay ping fail | VTEP IP chưa gán lên s1-eth2 | `ip addr add 10.0.0.1/24 dev s1-eth2` |
| `vxlan0`/`vxlan1` không thấy | VXLAN chưa được cấu hình | Chạy lại `vxlan_setup.sh` |
| MAC của h1 trên port vxlan0 trong FDB | Dấu hiệu broadcast storm đang xảy ra | Sửa L2 loop như trên |
| VNI không khớp hai đầu | `options:key` khác nhau giữa vxlan0 và vxlan1 | Kiểm tra và đồng bộ key=100 cả hai bên |

---

## 6. Bắt và phân tích gói tin

### 6.1 Mục tiêu

Phần này sử dụng `tcpdump` để bắt gói tin tại hai vị trí khác nhau trong topology, chứng minh trực quan cơ chế đóng gói VXLAN:

| Vị trí bắt | Interface | Thấy gì |
|---|---|---|
| **Underlay** | `s1-eth2` | Gói VXLAN đã đóng gói: Outer IP + UDP:4789 + VXLAN header + Inner frame |
| **Overlay** | `h1-eth0` | ICMP gốc chưa đóng gói: chỉ thấy IP + ICMP thuần |

So sánh hai luồng giúp hiểu rõ quá trình encapsulation/decapsulation của VTEP.

---

### 6.2 Cấu trúc gói VXLAN cần phân tích

```
Gói bắt trên s1-eth2 (underlay):
┌──────────────────────────────────────────────────────┐
│ Outer Ethernet │ src: MAC(s1-eth2) → dst: MAC(s2-eth2) │ 14 bytes
├──────────────────────────────────────────────────────┤
│ Outer IP       │ src: 10.0.0.1    → dst: 10.0.0.2     │ 20 bytes
├──────────────────────────────────────────────────────┤
│ Outer UDP      │ src: ephemeral   → dst: 4789          │  8 bytes
├──────────────────────────────────────────────────────┤
│ VXLAN Header   │ Flags=0x08  VNI=100 (0x000064)        │  8 bytes
├──────────────────────────────────────────────────────┤
│ Inner Ethernet │ src: MAC(h1-eth0)→ dst: MAC(h2-eth0)  │ 14 bytes
├──────────────────────────────────────────────────────┤
│ Inner IP       │ src: 192.168.100.1→dst: 192.168.100.2 │ 20 bytes
├──────────────────────────────────────────────────────┤
│ ICMP           │ Echo Request / Echo Reply              │  8 bytes
└──────────────────────────────────────────────────────┘
Tổng overhead VXLAN: 14+20+8+8 = 50 bytes
```

---

### 6.3 Bắt gói trên underlay

> **Lưu ý triển khai thực tế:** Trong lab này, `s1-eth2` (10.0.0.1) và `s2-eth2` (10.0.0.2) đều nằm trong **root namespace** của cùng một máy Linux. Khi OVS đóng gói và gửi VXLAN đến 10.0.0.2, kernel nhận ra đây là địa chỉ local (trên `s2-eth2`) và định tuyến gói qua **loopback path nội bộ** — không phát ra ngoài `s1-eth2`. Do đó, tcpdump trên `s1-eth2` không bắt được gói. Giải pháp: dùng `-i any` để bắt trên tất cả interface, bao gồm cả loopback path.

#### Lệnh bắt gói (dùng `capture.sh`)

```bash
# Chạy script tự động từ Mininet CLI
mininet> sh bash capture.sh
```

#### Kết quả thực tế

```
━━━ BƯỚC 1: Bắt VXLAN trên underlay interface (any) ━━━
Capture interface: any (bắt toàn bộ interfaces trong root namespace)
Underlay s1-eth2: UP — IP: 10.0.0.1/24
Lọc: UDP port 4789
tcpdump đã khởi động (PID=17293)
Đang ping 5 gói từ namespace h1 (interval=0.8s)...
5 packets transmitted, 5 received, 0% packet loss
[OK] Đã bắt gói → /tmp/vxlan_cap/underlay.pcap (1724 bytes)
```

#### Nội dung bắt được (10 gói: 5 request + 5 reply)

```
10:31:37.697828 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 1, length 64
10:31:37.698080 lo In IP 10.0.0.2.41080 > 10.0.0.1.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 1, length 64
...
(tổng 10 dòng — 5 cặp request/reply)
```

**Giải thích từng trường:**

| Trường | Giá trị | Ý nghĩa |
|---|---|---|
| `10.0.0.1 > 10.0.0.2` | Outer IP | VTEP s1 → VTEP s2 (underlay) |
| `.4789` | UDP dest port | Cổng VXLAN chuẩn IANA |
| `flags [I] (0x08)` | VXLAN flag | Bit I=1: VNI hợp lệ |
| `vni 100` | VNI | Định danh overlay network |
| `192.168.100.1 > 192.168.100.2` | Inner IP | h1 → h2 (overlay) |
| `ICMP echo request` | Inner payload | Dữ liệu gốc của h1 |

---

### 6.4 Bắt gói trên overlay (`h1-eth0`)

Interface `h1-eth0` chỉ thấy frame gốc — **không có** VXLAN header. `h1-eth0` nằm trong network namespace riêng của host h1, nên phải dùng `nsenter` để vào namespace trước khi chạy tcpdump.

#### Kết quả thực tế

```
━━━ BƯỚC 2: Bắt ICMP gốc trên overlay interface (h1-eth0) ━━━
[OK] Đã bắt gói → /tmp/vxlan_cap/overlay.pcap (1164 bytes)

10:31:42.864123 IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 1, length 64
10:31:42.864191 IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 1, length 64
10:31:43.724573 IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17309, seq 2, length 64
10:31:43.724686 IP 192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17309, seq 2, length 64
...
```

Không có bất kỳ thông tin UDP/VXLAN nào — đây là frame L2 thuần như mạng LAN thông thường. VXLAN hoàn toàn **trong suốt** với host.

---

### 6.5 Phân tích chi tiết với verbose (`-vvv`)

#### Kết quả thực tế (2 gói đầu)

```
10:31:37.697828 lo In IP (tos 0x0, ttl 64, id 9915, offset 0, flags [DF], proto UDP (17), length 134)
    10.0.0.1.41080 > 10.0.0.2.4789: [no cksum] VXLAN, flags [I] (0x08), vni 100
    IP (tos 0x0, ttl 64, id 13205, offset 0, flags [DF], proto ICMP (1), length 84)
        192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 1, length 64

10:31:37.698080 lo In IP (tos 0x0, ttl 64, id 28453, offset 0, flags [DF], proto UDP (17), length 134)
    10.0.0.2.41080 > 10.0.0.1.4789: [no cksum] VXLAN, flags [I] (0x08), vni 100
    IP (tos 0x0, ttl 64, id 10902, offset 0, flags [none], proto ICMP (1), length 84)
        192.168.100.2 > 192.168.100.1: ICMP echo reply, id 17296, seq 1, length 64
```

**Phân tích các trường quan trọng:**

| Trường | Giá trị | Ý nghĩa |
|--------|---------|---------|
| `proto UDP (17)` | Outer protocol | Outer header là UDP |
| `length 134` | Outer IP length | Tổng kích thước gói underlay |
| `10.0.0.1.41080 > 10.0.0.2.4789` | VTEP src → dst | s1 VTEP gửi đến s2 VTEP, UDP port 4789 |
| `[no cksum]` | UDP checksum | OVS bỏ tính checksum (tối ưu hiệu suất) |
| `vni 100` | VNI | Đúng với cấu hình |
| `flags [I] (0x08)` | VXLAN Valid bit | Bit I=1: VNI hợp lệ |
| `length 84` | Inner IP length | Kích thước gói ICMP gốc |
| `192.168.100.1 > 192.168.100.2` | Inner IP src → dst | h1 → h2 (overlay) |

**Overhead thực tế:** `134 − 84 = 50 bytes` → đúng như lý thuyết.

---

### 6.6 Xác minh VNI trong hex dump

#### Kết quả thực tế

```
10:31:37.697828 lo In IP 10.0.0.1.41080 > 10.0.0.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 192.168.100.1 > 192.168.100.2: ICMP echo request, id 17296, seq 1, length 64
0x0000:  0800 0000 0000 0001 0304 0006 0000 0000   ← Linux SLL2 pseudo-header (16 bytes, do -i any)
0x0010:  0000 0000 4500 0086 26bb 4000 4011 ffa9   ← Outer IP: 4500=IPv4, len=0x0086=134
0x0020:  0a00 0001 0a00 0002 a078 12b5 0072 0000   ← src=10.0.0.1, dst=10.0.0.2, sport=41080, dport=0x12b5=4789
0x0030:  0800 0000 0000 6400 7e69 bbd2 444d fe7e   ← VXLAN: flags=0x08, VNI=0x000064=100 ✓
0x0040:  b898 a0c4 0800 4500 0054 3395 4000 4001   ← Inner Ethernet+IP: len=0x54=84
0x0050:  bdbf c0a8 6401 c0a8 6402 0800 544c 4390   ← Inner IP src=192.168.100.1, dst=192.168.100.2
...
```

**Vị trí VNI trong payload (tính từ sau SLL2 header 16 bytes):**
- Byte 42–45 (offset 0x2A): `0800 0000` — VXLAN flags (0x08 = Valid) + reserved
- Byte 46–48 (offset 0x2E): `0000 64` = **0x000064 = 100** → VNI = 100 ✓
- Byte 49 (offset 0x31): `00` — reserved

`0x000064` = 100 (decimal) → Xác nhận VNI = 100 đúng với cấu hình.

---

### 6.7 So sánh kích thước gói — VXLAN Overhead

#### Kết quả đo từ lab

| Chỉ số | Giá trị | Nguồn |
|--------|---------|-------|
| Outer IP length (underlay) | **134 bytes** | `length 134` trong verbose output |
| Inner IP length (overlay) | **84 bytes** | `length 84` trong verbose output |
| **Overhead VXLAN thực tế** | **50 bytes** | 134 − 84 = 50 |

#### Phân tích cấu trúc overhead (50 bytes)

| Thành phần | Kích thước | Ghi chú |
|---|---|---|
| Outer Ethernet header | 14 bytes | MAC underlay (src/dst VTEP) |
| Outer IP header | 20 bytes | IP VTEP s1 → s2 |
| Outer UDP header | 8 bytes | dst port 4789 |
| VXLAN header | 8 bytes | 4 bytes flags + 3 bytes VNI + 1 byte reserved |
| **Tổng overhead** | **50 bytes** | Đúng RFC 7348 |

#### Inner packet = 84 bytes

| Thành phần | Kích thước |
|---|---|
| Inner Ethernet | 14 bytes |
| Inner IP header | 20 bytes |
| ICMP header | 8 bytes |
| ICMP payload | 56 bytes (ping default) |
| **Tổng inner** | **84 bytes** |

> **Kết luận:** Overhead 50 bytes ≈ **60%** so với inner IP packet (84 bytes). Mỗi gói ICMP 56-byte payload phải chịu 50 bytes overhead — điển hình cho giao thức tunnel điểm-điểm.

> **Lưu ý kỹ thuật:** File pcap bắt với `-i any` chứa Linux SLL2 pseudo-header (16 bytes) thay vì Ethernet header thật. Vì vậy kích thước file record = 154 bytes (underlay) và 98 bytes (overlay), nhưng overhead VXLAN thực = `Outer IP length − Inner IP length = 134 − 84 = 50 bytes`.

---

### 6.8 Lưu và phân tích bằng file pcap

#### Lưu ra file

```bash
# Bắt và lưu vào file pcap
mininet> sh tcpdump -i s1-eth2 -n udp port 4789 -w /tmp/vxlan_capture.pcap &

# Sinh traffic
mininet> h1 ping -c 10 192.168.100.2

# Dừng bắt
mininet> sh kill %1
```

#### Phân tích bằng tshark (nếu đã cài)

```bash
# Xem tất cả gói VXLAN
tshark -r /tmp/vxlan_capture.pcap

# Lọc và hiển thị VNI
tshark -r /tmp/vxlan_capture.pcap -T fields \
    -e ip.src -e ip.dst -e udp.dstport -e vxlan.vni

# Hiển thị inner frame
tshark -r /tmp/vxlan_capture.pcap -V | grep -A 5 "VXLAN"
```

#### Mở bằng Wireshark

> **Lưu ý:** Wireshark là ứng dụng GUI — **không chạy trực tiếp từ Mininet CLI**.
> Phải dùng một trong các cách sau:

```bash
# Cách 1: Mở terminal host MỚI (ngoài Mininet), chạy lệnh này
wireshark /tmp/vxlan_capture.pcap &

# Cách 2: Từ Mininet CLI với sh prefix (yêu cầu môi trường có DISPLAY)
mininet> sh wireshark /tmp/vxlan_capture.pcap &

# Cách 3: SSH với X11 forwarding
#   Kết nối: ssh -X user@host
#   Rồi trong Mininet CLI: sh wireshark /tmp/vxlan_capture.pcap &

# Cách 4: Copy về máy Windows rồi mở (nếu lab chạy trên VM)
#   scp user@host:/tmp/vxlan_capture.pcap C:\Users\adm\Downloads\
```

**Trong Wireshark:** Filter `vxlan` để lọc, click vào packet để thấy phân tầng:
```
► Frame
  ► Ethernet II (Outer)
    ► Internet Protocol (Outer IP: 10.0.0.1 → 10.0.0.2)
      ► UDP (port 4789)
        ► Virtual eXtensible Local Area Network (VNI: 100)
          ► Ethernet II (Inner)
            ► Internet Protocol (Inner IP: 192.168.100.1 → 192.168.100.2)
              ► Internet Control Message Protocol
```

---

### 6.9 Script tự động: `capture.sh`

File `capture.sh` tự động hóa toàn bộ quá trình bắt và phân tích:

```bash
# Chạy từ Mininet CLI
mininet> sh bash capture.sh
```

Script thực hiện:

| Bước | Nội dung | Kết quả thực tế |
|---|---|---|
| 1 | Bắt VXLAN trên `-i any` (UDP port 4789) trong khi h1 ping h2 → `underlay.pcap` | 1724 bytes, 10 gói ✓ |
| 2 | Bắt ICMP trên `h1-eth0` trong h1 namespace → `overlay.pcap` | 1164 bytes, 10 gói ✓ |
| 3 | Phân tích underlay — tóm tắt và verbose `-vvv` | VNI=100, IP 10.0.0.1→10.0.0.2 ✓ |
| 4 | Phân tích overlay — ICMP gốc | Không có VXLAN header ✓ |
| 5 | So sánh kích thước — tính overhead | 134−84 = 50 bytes ✓ |
| 6 | Hex dump xác minh VNI=100 (0x000064) | `0000 6400` tại offset 0x30 ✓ |

---

## 7. Kết luận

### 7.1 Tổng kết kết quả lab

Bài lab đã triển khai thành công VXLAN overlay network trên nền tảng SDN Mininet + OVS. Tất cả mục tiêu đề ra đều đạt được:

| Mục tiêu | Kết quả |
|----------|---------|
| Xây dựng topology Mininet 2-VTEP | ✓ `topology.py` khởi động thành công |
| Cấu hình VXLAN tunnel VNI=100 trên OVS | ✓ `vxlan0`/`vxlan1` với `key=100` |
| h1 ↔ h2 ping qua overlay | ✓ 5/5 packets, 0% loss |
| Bắt và phân tích gói VXLAN | ✓ 10 gói, overhead 50 bytes đúng lý thuyết |
| Xác minh VNI trong hex dump | ✓ `0x000064` = 100 |

### 7.2 Những gì đã học được

#### VXLAN hoạt động đúng như RFC 7348

Kết quả capture xác nhận đầy đủ cơ chế VXLAN:

- **Đóng gói:** Frame Ethernet gốc (h1→h2, 192.168.100.x) được OVS đóng gói hoàn toàn vào UDP datagram. Inner packet 84 bytes + 50 bytes overhead = outer 134 bytes.
- **Trong suốt với host:** `h1-eth0` chỉ thấy ICMP thuần — không có dấu vết VXLAN. Đây là đặc tính quan trọng: host không cần biết gì về tunnel.
- **VNI là định danh segment:** VNI=100 xuất hiện nhất quán trong mọi gói bắt được, đúng với cấu hình `options:key=100`.

#### Vai trò của OVS trong VXLAN

OVS đóng vai trò VTEP hoàn toàn tự động:
1. Nhận frame từ host port (`h1-eth0` → `s1` → `s1-eth1`)
2. Tra cứu MAC đích trong flow table
3. Quyết định đưa ra tunnel port `vxlan0`
4. Tự động đóng gói: thêm Outer Ethernet + IP + UDP + VXLAN header
5. Gửi gói ra underlay interface

Toàn bộ quá trình này xảy ra trong OVS kernel datapath — **không cần controller** (standalone mode).

#### Bài học về môi trường mô phỏng

Bài lab gặp một số vấn đề thú vị đặc thù của môi trường Mininet:

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| OVS port name conflict | OVS yêu cầu tên interface global unique | Dùng `vxlan0`/`vxlan1` thay vì cùng tên |
| L2 broadcast storm | `s1-eth2`/`s2-eth2` vừa là underlay vừa là OVS port → 2 L2 path | `del-port` trước khi gán IP VTEP |
| tcpdump không bắt được trên `s1-eth2` | Cả hai VTEP trong cùng root namespace → kernel định tuyến nội bộ qua loopback | Dùng `-i any` |
| tcpdump overlay empty pcap | `kill nsenter` không forward signal đến child tcpdump | Dùng `-c N` để tcpdump tự thoát + `pkill -INT` |

### 7.3 So sánh lý thuyết và thực nghiệm

| Thông số | Lý thuyết | Thực đo | Khớp? |
|----------|-----------|---------|-------|
| UDP port | 4789 | 4789 | ✓ |
| VNI | 100 | 100 (0x000064) | ✓ |
| VXLAN overhead | 50 bytes | 50 bytes (134−84) | ✓ |
| VXLAN flags Valid bit | 0x08 | 0x08 | ✓ |
| Inner ICMP length | 84 bytes | 84 bytes | ✓ |
| Outer IP length | 134 bytes | 134 bytes | ✓ |

### 7.4 Hạn chế và hướng mở rộng

#### Hạn chế của lab hiện tại

- **Topology đơn giản:** Chỉ 2 VTEP point-to-point. Thực tế data center có hàng trăm VTEP cần multicast hoặc BGP EVPN để học MAC.
- **Không có controller:** OVS chạy ở `standalone` mode. Trong SDN thực tế, OpenFlow controller quản lý flow table và có thể tối ưu routing.
- **Single VNI:** Chỉ demo 1 segment. Khả năng multi-tenant với nhiều VNI là ưu điểm chính của VXLAN so với VLAN.

#### Hướng mở rộng

1. **Multi-VTEP:** Thêm `s3`, `h3` — demo VXLAN flooding và MAC learning trong môi trường nhiều VTEP.
2. **OpenFlow controller:** Tích hợp Ryu hoặc ONOS để quản lý flow table — demo SDN control plane thực sự.
3. **BGP EVPN:** Thay thế flooding bằng BGP EVPN (RFC 7432) để phân phối thông tin MAC/IP — như Cumulus, FRR.
4. **Inter-VNI routing:** Thêm VXLAN gateway để traffic giữa các VNI khác nhau đi qua L3 gateway.
5. **Đo hiệu năng:** So sánh throughput và latency của VXLAN vs GRE vs native L3.

### 7.5 Kết luận chung

Bài lab chứng minh thành công rằng **VXLAN cho phép mở rộng mạng L2 qua hạ tầng L3** một cách minh bạch với endpoint. OVS là một VTEP mạnh mẽ và linh hoạt, có thể cấu hình hoàn toàn bằng `ovs-vsctl` mà không cần phần cứng chuyên dụng. Sự kết hợp Mininet + OVS cung cấp môi trường học tập lý tưởng để hiểu sâu cơ chế hoạt động của VXLAN ở mức packet level.

---
