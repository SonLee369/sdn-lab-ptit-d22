# Bao Cao Lab VXLAN — Module 4: L2 Overlay Verification

---

## 1. Muc Tieu

Xac nhan VXLAN tunnel (VNI=100) da tao o Module 3 hoat dong dung chuc nang:

1. **ARP hoat dong qua VXLAN**: h1 phan giai duoc MAC cua h2 qua tunnel
2. **Ping thong 2 chieu**: h1 ↔ h2 thong qua L2 overlay (0% packet loss)
3. **MAC learning chinh xac**: OVS hoc MAC cua h2 tren vxlan port, MAC cua h1 tren local port
4. **Giai thich hanh vi tcpdump**: Tai sao VXLAN traffic khong xuat hien tren `s1-eth2`

---

## 2. Mo Hinh Topo

```
  h1 (10.0.0.1/24)              h2 (10.0.0.2/24)
        |                              |
     [s1]  <==== VXLAN VNI 100 ====> [s2]
VTEP: 192.168.1.1 ------------ VTEP: 192.168.1.2
  (dev s1 bridge)                (dev s2 bridge)
        |______________________________|
              s1-eth2 <-> s2-eth2
          (underlay link - KHONG trong bridge)
```

| Thanh phan | Chi tiet |
|-----------|---------|
| Overlay subnet | 10.0.0.0/24 (h1, h2) |
| Underlay subnet | 192.168.1.0/30 (VTEP) |
| VXLAN VNI | 100 |
| UDP Port | 4789 |
| VTEP s1 | 192.168.1.1 tren bridge interface `s1` |
| VTEP s2 | 192.168.1.2 tren bridge interface `s2` |
| Bridge s1 ports | s1-eth1 (h1), vxlan1 |
| Bridge s2 ports | s2-eth1 (h2), vxlan2 |

> **Diem khac so voi Module 3**: `s1-eth2` va `s2-eth2` da bi xoa khoi bridge
> de ngan switching loop. VTEP co them `options:local_ip` tuong minh.

---

## 3. Moi Truong Lab

| Thanh phan | Phien ban |
|-----------|---------|
| Mininet | 2.x |
| Open vSwitch (OVS) | 3.3.4 |
| He dieu hanh | Ubuntu |
| Python | 3.x |

---

## 4. Nguyen Ly Hoat Dong

### 4.1 Luong goi tin VXLAN (ARP + Ping)

```
h1 gui ARP "Ai la 10.0.0.2?"
  |
  v
s1 nhan tren s1-eth1
  |-- Hoc MAC h1 (00:00:00:00:00:01) tren port 1
  |-- Flood toi vxlan1 (broadcast)
  |
  v
vxlan1 dong goi:
  +-------------+-------+--------+-----------------------+
  | Outer IP    | UDP   | VXLAN  | ARP Request (inner)   |
  | src:1.1.1.1 | 4789  | VNI=100| src: 00:...:01        |
  | dst:1.1.1.2 |       |        | dst: ff:ff:ff:ff:ff:ff|
  +-------------+-------+--------+-----------------------+
  [Local delivery vi 192.168.1.2 la dia chi local cung namespace]
  |
  v
s2 nhan tren vxlan2
  |-- Hoc MAC h1 (00:00:00:00:00:01) tren vxlan2
  |-- Go bo VXLAN header
  |-- Forward ARP Request toi h2 qua s2-eth1
  |
  v
h2 nhan ARP Request, gui ARP Reply:
  |
  v
s2 nhan ARP Reply tren s2-eth1
  |-- Hoc MAC h2 (00:00:00:00:00:02) tren port s2-eth1
  |-- Tra cuu h1 MAC -> nam o vxlan2 -> gui qua vxlan2
  |
  v
s1 nhan tren vxlan1
  |-- Hoc MAC h2 (00:00:00:00:00:02) tren port vxlan1 (port 3)
  |-- Tra cuu h1 MAC -> nam o port 1 (s1-eth1) -> gui toi h1
  |
  v
h1 nhan ARP Reply: "00:00:00:00:00:02 la h2" -> ARP resolved!
  |
  v
ICMP Echo Request/Reply chay qua cung luong VXLAN
```

### 4.2 Tai sao tcpdump tren s1-eth2 khong thay VXLAN

Trong Mininet, tat ca OVS bridge deu chay trong **root network namespace** (cung namespace). Vi vay:

```
Binh thuong (2 may vat ly rieng biet):
  VTEP1 (192.168.1.1) --[cable]--> VTEP2 (192.168.1.2)
  tcpdump tren cable thay VXLAN packet ✓

Mininet (cung namespace):
  192.168.1.2 la LOCAL address tren bridge s2
  Kernel: "192.168.1.2 la local -> giao tuc tiep (local delivery)"
  Packet KHONG di ra s1-eth2 vat ly
  -> tcpdump -i s1-eth2 thay 0 packet (binh thuong!)
```

---

## 5. Cac Buoc Thuc Hien

### Buoc 1 — Don dep va chay script

```bash
sudo mn -c
sudo python3 scripts/module4_verify.py
```

### Buoc 2 — Cau hinh chinh (trong script)

**Xoa underlay port khoi bridge (ngan loop):**
```bash
ovs-vsctl del-port s1 s1-eth2
ovs-vsctl del-port s2 s2-eth2
```

**Gan VTEP IP len bridge interface:**
```bash
ip addr add 192.168.1.1/30 dev s1
ip addr add 192.168.1.2/30 dev s2
```

**Cau hinh VXLAN voi local_ip tuong minh:**
```bash
# Tren s1
ovs-vsctl add-port s1 vxlan1 \
  -- set interface vxlan1 \
     type=vxlan \
     options:local_ip=192.168.1.1 \
     options:remote_ip=192.168.1.2 \
     options:key=100 \
     options:dst_port=4789

# Tren s2
ovs-vsctl add-port s2 vxlan2 \
  -- set interface vxlan2 \
     type=vxlan \
     options:local_ip=192.168.1.2 \
     options:remote_ip=192.168.1.1 \
     options:key=100 \
     options:dst_port=4789
```

### Buoc 3 — Kiem tra trong Mininet CLI

```bash
# Ping 2 chieu
mininet> h1 ping -c 3 10.0.0.2
mininet> h2 ping -c 3 10.0.0.1

# Kiem tra ARP table
mininet> h1 arp -n

# Kiem tra MAC learning tren OVS
mininet> sh ovs-appctl fdb/show s1
mininet> sh ovs-appctl fdb/show s2
```

---

## 6. Ket Qua Thuc Te

### 6.1 Ping h1 → h2

```
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.767 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.136 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.076 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2038ms
rtt min/avg/max/mdev = 0.076/0.326/0.767/0.312 ms
```

### 6.2 Ping h2 → h1

```
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=1.42 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=0.073 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=0.095 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2063ms
rtt min/avg/max/mdev = 0.073/0.528/1.416/0.627 ms
```

### 6.3 ARP Table tren h1

```
Address    HWtype  HWaddress           Flags Mask  Iface
10.0.0.2   ether   00:00:00:00:00:02   C           h1-eth0
```

### 6.4 MAC Table tren s1 (FDB)

```
port  VLAN  MAC                Age
LOCAL 0     ee:15:76:fb:99:4a  26   <- bridge s1 internal MAC
3     0     2e:17:6d:b4:39:4d  25   <- s2 bridge MAC (thay qua tunnel)
3     0     00:00:00:00:00:02  8    <- h2 MAC, hoc qua vxlan1 (port 3) ✓
1     0     00:00:00:00:00:01  8    <- h1 MAC, hoc qua s1-eth1 (port 1) ✓
```

---

## 7. Loi Gap Va Qua Trinh Xu Ly

Module 4 gap **3 bug lien tiep** trong qua trinh debug:

### Bug 1 — Switching Loop (Broadcast Storm)

| Muc | Chi tiet |
|-----|---------|
| Trieu chung | 13,680 VXLAN packets bi drop, h1 MAC hoc sai tren vxlan port |
| Nguyen nhan | `s1-eth2`/`s2-eth2` con nam trong bridge -> VXLAN packet bi flood qua ca physical port lan tunnel port -> tao loop |
| Loop path | h1 broadcast → s1 flood → s1-eth2 → s2-eth2 → s2 flood → vxlan2 → vxlan1 → s1 (lap lai) |
| Cach xu ly | `ovs-vsctl del-port s1 s1-eth2` va `del-port s2 s2-eth2` |

```
Truoc fix (bridge s1):              Sau fix (bridge s1):
  s1-eth1 (h1)                        s1-eth1 (h1)
  s1-eth2 (underlay) <- GAY LOOP      [da xoa]
  vxlan1  (tunnel)                    vxlan1  (tunnel)
```

### Bug 2 — Sai Interface cho VTEP IP

| Muc | Chi tiet |
|-----|---------|
| Trieu chung | 0 VXLAN packet, ARP incomplete |
| Nguyen nhan | Sau khi del-port, VTEP IP duoc gan vao `s1-eth2`/`s2-eth2` thay vi bridge interface. Ca 2 IP (192.168.1.1 va 192.168.1.2) nam cung namespace -> tao conflict route |
| Cach xu ly | Gan IP vao bridge interface: `ip addr add 192.168.1.1/30 dev s1` |

### Bug 3 — Thieu `options:local_ip`

| Muc | Chi tiet |
|-----|---------|
| Trieu chung | ARP van incomplete du VTEP IP da dung |
| Nguyen nhan | Khong co `local_ip`, OVS hoi kernel: "source IP cho 192.168.1.2 la gi?" Kernel tra loi `192.168.1.2` (vi la local address cung namespace) -> VXLAN packet co `src=dst=192.168.1.2` -> vxlan2 tu choi vi `remote_ip=192.168.1.1` khong khop |
| Cach xu ly | Them `options:local_ip=192.168.1.1` vao vxlan1, `options:local_ip=192.168.1.2` vao vxlan2 |

```
Khong co local_ip:                  Co local_ip:
  OVS hoi kernel route              OVS dung IP da chi dinh
  Kernel: src = 192.168.1.2 (!)     src = 192.168.1.1 ✓
  vxlan2 reject (remote != src)     vxlan2 chap nhan ✓
```

---

## 8. Phan Tich Ket Qua

| Tieu chi | Ket qua | Y nghia |
|---------|--------|--------|
| h1 → h2 ping | OK (0% loss) | L2 overlay hoat dong chieu di |
| h2 → h1 ping | OK (0% loss) | L2 overlay hoat dong chieu ve |
| RTT trung binh | ~0.4 ms | Thap, phu hop Mininet |
| ARP h1 co h2 MAC | OK | ARP broadcast duoc VXLAN dong goi va chuyen thanh cong |
| FDB h1 MAC o port 1 | OK | s1-eth1 (port local) - chinh xac |
| FDB h2 MAC o port 3 | OK | vxlan1 (port tunnel) - chinh xac |
| tcpdump s1-eth2 = 0 pkt | Expected | VXLAN dung local delivery trong Mininet same-namespace |

### Ghi chu dac biet ve Mininet VXLAN

Trong moi truong Mininet thuc te (same namespace), VXLAN hoat dong nhung co diem khac voi thuc te:

| Dac diem | Mininet (same namespace) | Thuc te (2 may rieng) |
|---------|------------------------|----------------------|
| VTEP delivery | Local (kernel loopback) | Physical wire |
| tcpdump underlay | Khong thay packet | Thay day du |
| Hieu nang | Rat cao (< 1 ms) | Phu thuoc mang vat ly |
| Chuc nang overlay | Giong hoan toan | Giong hoan toan |

---

## 9. Ket Luan

Module 4 hoan thanh thanh cong. L2 overlay VXLAN (VNI=100) da duoc xac nhan:

- **ARP hoat dong**: h1 phan giai MAC cua h2 qua VXLAN tunnel
- **Ping 2 chieu**: 0% packet loss, RTT < 1 ms
- **MAC learning dung**: h2 MAC hoc tren vxlan port, h1 MAC hoc tren local port
- **3 bug da duoc giai quyet**: switching loop, sai interface IP, thieu local_ip

**San sang cho Module 5: Multi-VNI / Tenant Isolation.**

---

*Ngay thuc hien: 30/03/2026*
