# Bao Cao Lab VXLAN — Module 5: Multi-VNI / Tenant Isolation

---

## 1. Muc Tieu

Chung minh rang VXLAN co the phan vung nhieu **tenant doc lap** tren cung mot ha tang underlay L3:

1. **VNI 100 (Tenant A)**: h1 ↔ h2 thong, 0% packet loss
2. **VNI 200 (Tenant B)**: h3 ↔ h4 thong, 0% packet loss
3. **Cross-VNI Isolation**: h1/h2 KHONG the giao tiep voi h3/h4
4. **Same-IP Isolation**: h1 va h3 cung IP `10.0.0.1`; h2 va h4 cung IP `10.0.0.2` — ARP cache moi host chi thay MAC cua tenant minh

---

## 2. Mo Hinh Topo

```
  ╔══════════════ Tenant A — VNI 100 ══════════════╗
  ║  h1 (10.0.0.1)          h2 (10.0.0.2)          ║
  ║  MAC: 00:00:00:00:01:01  MAC: 00:00:00:00:01:02 ║
  ║       |                        |                 ║
  ║     [s1a]══ VXLAN VNI 100 ══[s2a]               ║
  ╚════════════════════════════════════════════════╝

  ╔══════════════ Tenant B — VNI 200 ══════════════╗
  ║  h3 (10.0.0.1)          h4 (10.0.0.2)          ║
  ║  MAC: 00:00:00:00:02:01  MAC: 00:00:00:00:02:02 ║
  ║       |                        |                 ║
  ║     [s1b]══ VXLAN VNI 200 ══[s2b]               ║
  ╚════════════════════════════════════════════════╝

       VTEP: 192.168.1.1           VTEP: 192.168.1.2
       (tren bridge s1a)            (tren bridge s2a)
```

| Thanh phan | Ten | IP Overlay | MAC | VNI |
|-----------|-----|-----------|-----|-----|
| Host 1 | h1 | 10.0.0.1/24 | 00:00:00:00:01:01 | 100 |
| Host 2 | h2 | 10.0.0.2/24 | 00:00:00:00:01:02 | 100 |
| Host 3 | h3 | 10.0.0.1/24 | 00:00:00:00:02:01 | 200 |
| Host 4 | h4 | 10.0.0.2/24 | 00:00:00:00:02:02 | 200 |
| Bridge VNI 100 trai | s1a | VTEP: 192.168.1.1 | — | 100 |
| Bridge VNI 100 phai | s2a | VTEP: 192.168.1.2 | — | 100 |
| Bridge VNI 200 trai | s1b | VTEP: 192.168.1.1 (chung) | — | 200 |
| Bridge VNI 200 phai | s2b | VTEP: 192.168.1.2 (chung) | — | 200 |
| Tunnel A | v100s1 / v100s2 | — | — | 100 |
| Tunnel B | v200s1 / v200s2 | — | — | 200 |

---

## 3. Moi Truong Lab

| Thanh phan | Phien ban |
|-----------|---------|
| Mininet | 2.x |
| Open vSwitch (OVS) | 3.3.4 |
| He dieu hanh | Ubuntu |
| Python | 3.x |

---

## 4. Nguyen Ly

### 4.1 VNI la gi?

**VNI (VXLAN Network Identifier)** la truong 24-bit trong VXLAN header, dong vai tro nhu VLAN ID nhung rong hon (2^24 = 16 trieu VNI vs 4096 VLAN).

```
 VXLAN Header (8 bytes):
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |R|R|R|R|I|R|R|R|            Reserved                           |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                VXLAN Network Identifier (VNI) |   Reserved    |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                              ^
                         24 bit = 16,777,216 VNI
```

### 4.2 Cach OVS phan biet tunnel theo VNI

Khi OVS nhan mot VXLAN packet tren UDP port 4789, no match theo bo (local_ip, remote_ip, VNI):

```
Packet den: src=192.168.1.2, dst=192.168.1.1, VNI=100
  -> OVS tim port co: local_ip=192.168.1.1, remote_ip=192.168.1.2, key=100
  -> Khop voi v100s1 tren bridge s1a
  -> Inner frame duoc dua vao bridge s1a -> chuyen toi h1

Packet den: src=192.168.1.2, dst=192.168.1.1, VNI=200
  -> OVS tim port co: local_ip=192.168.1.1, remote_ip=192.168.1.2, key=200
  -> Khop voi v200s1 tren bridge s1b
  -> Inner frame duoc dua vao bridge s1b -> chuyen toi h3
```

Hai VNI hoan toan doc lap, du dung chung local_ip va remote_ip.

### 4.3 Tai sao cung IP van bi cach ly?

```
h1 (10.0.0.1) muon ping 10.0.0.2:
  1. h1 gui ARP broadcast "Ai la 10.0.0.2?"
  2. ARP di vao s1a -> flood toi v100s1 (VNI 100)
  3. s2a nhan, flood ra s2a-eth1 -> h2 nhan, tra loi
  4. h1 nhan duoc MAC cua h2 (00:00:00:00:01:02)
  -> h1 ping duoc h2 ✓

h3 (10.0.0.1) muon ping 10.0.0.2:
  1. h3 gui ARP broadcast "Ai la 10.0.0.2?"
  2. ARP di vao s1b -> flood toi v200s1 (VNI 200)
  3. s2b nhan, flood ra s2b-eth1 -> h4 nhan, tra loi
  4. h3 nhan duoc MAC cua h4 (00:00:00:00:02:02)
  -> h3 ping duoc h4 ✓

h1 co the ping h4 khong?
  - h4 thuoc s2b (VNI 200)
  - Khong co duong nao tu s1a (VNI 100) den s2b (VNI 200)
  - ARP cua h1 chi di qua v100s1 -> s2a -> h2 (khong den h4)
  -> h1 KHONG ping duoc h4 ✓ (isolation!)
```

### 4.4 Bang so sanh MAC — bang chung isolation

| Host | IP tra cuu | MAC nhan duoc | La ai |
|------|-----------|--------------|-------|
| h1 | 10.0.0.2 | 00:00:00:00:**01:02** | h2 (cung VNI 100) |
| h3 | 10.0.0.2 | 00:00:00:00:**02:02** | h4 (cung VNI 200) |

Cung tra cuu `10.0.0.2` nhung nhan duoc **MAC khac nhau** — day la bang chung ro rang nhat rang 2 tenant hoan toan bi cach ly.

---

## 5. Cau Hinh Chi Tiet

### 5.1 VXLAN Tunnel VNI 100 (Tenant A)

```bash
# Tren s1a
ovs-vsctl add-port s1a v100s1 \
  -- set interface v100s1 \
     type=vxlan \
     options:local_ip=192.168.1.1 \
     options:remote_ip=192.168.1.2 \
     options:key=100 \
     options:dst_port=4789

# Tren s2a
ovs-vsctl add-port s2a v100s2 \
  -- set interface v100s2 \
     type=vxlan \
     options:local_ip=192.168.1.2 \
     options:remote_ip=192.168.1.1 \
     options:key=100 \
     options:dst_port=4789
```

### 5.2 VXLAN Tunnel VNI 200 (Tenant B)

```bash
# Tren s1b
ovs-vsctl add-port s1b v200s1 \
  -- set interface v200s1 \
     type=vxlan \
     options:local_ip=192.168.1.1 \
     options:remote_ip=192.168.1.2 \
     options:key=200 \
     options:dst_port=4789

# Tren s2b
ovs-vsctl add-port s2b v200s2 \
  -- set interface v200s2 \
     type=vxlan \
     options:local_ip=192.168.1.2 \
     options:remote_ip=192.168.1.1 \
     options:key=200 \
     options:dst_port=4789
```

### 5.3 Chay script

```bash
sudo mn -c
sudo python3 scripts/module5_multivni.py
```

### 5.4 Kiem tra trong CLI

```bash
# Intra-VNI ping
mininet> h1 ping -c 3 10.0.0.2   # Tenant A: h1 -> h2
mininet> h3 ping -c 3 10.0.0.2   # Tenant B: h3 -> h4

# ARP isolation proof
mininet> h1 arp -n                # Phai thay MAC h2 (01:02)
mininet> h3 arp -n                # Phai thay MAC h4 (02:02)

# FDB isolation
mininet> sh ovs-appctl fdb/show s1a
mininet> sh ovs-appctl fdb/show s1b

# OVS config
mininet> sh ovs-vsctl show
```

---

## 6. Ket Qua Thuc Te

### 6.1 TEST 1 — Intra-VNI: h1 → h2 (VNI 100)

```
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=3.55 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.147 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.191 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2035ms
rtt min/avg/max/mdev = 0.147/1.294/3.545/1.591 ms
```

**Ket qua: PASS** — RTT cao o goi dau (ARP lookup), on dinh tu goi 2.

### 6.2 TEST 2 — Intra-VNI: h3 → h4 (VNI 200)

```
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=1.91 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=0.076 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=0.102 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2033ms
rtt min/avg/max/mdev = 0.076/0.697/1.914/0.860 ms
```

**Ket qua: PASS**

### 6.3 TEST 3 — Isolation: ARP Cache

```
h1 arp -n:
Address    HWtype  HWaddress           Flags  Iface
10.0.0.2   ether   00:00:00:00:01:02   C      h1-eth0   <- h2's MAC ✓

h3 arp -n:
Address    HWtype  HWaddress           Flags  Iface
10.0.0.2   ether   00:00:00:00:02:02   C      h3-eth0   <- h4's MAC ✓
```

**Ket qua: ISOLATION CONFIRMED** — Cung IP `10.0.0.2` nhung 2 host nhan 2 MAC khac nhau.

### 6.4 FDB Tables

```
s1a (VNI 100):
port  VLAN  MAC                Age
2     0     00:00:00:00:01:02  23   <- h2 (Tenant A), hoc qua vxlan tunnel
1     0     00:00:00:00:01:01  20   <- h1 (Tenant A), hoc qua s1a-eth1
2     0     02:ca:81:ff:ec:46  20   <- s2a bridge MAC (thay qua tunnel)
LOCAL 0     5e:b7:48:86:da:49  19   <- s1a internal interface

s1b (VNI 200):
port  VLAN  MAC                Age
2     0     00:00:00:00:02:02  6    <- h4 (Tenant B), hoc qua vxlan tunnel
1     0     00:00:00:00:02:01  1    <- h3 (Tenant B), hoc qua s1b-eth1
```

Moi bridge chi biet MAC cua tenant minh — khong bao gio hoc MAC cua tenant khac.

### 6.5 OVS Config Tong Quat

```
Bridge s1a
    Port s1a-eth1          <- h1
    Port v100s1            <- VXLAN VNI 100
        Interface v100s1
            type: vxlan
            options: {dst_port="4789", key="100",
                      local_ip="192.168.1.1",
                      remote_ip="192.168.1.2"}

Bridge s2a
    Port s2a-eth1          <- h2
    Port v100s2            <- VXLAN VNI 100
        Interface v100s2
            type: vxlan
            options: {dst_port="4789", key="100",
                      local_ip="192.168.1.2",
                      remote_ip="192.168.1.1"}

Bridge s1b
    Port s1b-eth1          <- h3
    Port v200s1            <- VXLAN VNI 200
        Interface v200s1
            type: vxlan
            options: {dst_port="4789", key="200",
                      local_ip="192.168.1.1",
                      remote_ip="192.168.1.2"}

Bridge s2b
    Port s2b-eth1          <- h4
    Port v200s2            <- VXLAN VNI 200
        Interface v200s2
            type: vxlan
            options: {dst_port="4789", key="200",
                      local_ip="192.168.1.2",
                      remote_ip="192.168.1.1"}
```

---

## 7. Phan Tich Ket Qua

| Tieu chi | Ket qua | Y nghia |
|---------|--------|--------|
| h1 → h2 (VNI 100) | PASS 0% loss | Tunnel VNI 100 hoat dong |
| h3 → h4 (VNI 200) | PASS 0% loss | Tunnel VNI 200 hoat dong |
| h1 ARP 10.0.0.2 → MAC h2 | PASS | ARP chi di trong VNI 100 |
| h3 ARP 10.0.0.2 → MAC h4 | PASS | ARP chi di trong VNI 200 |
| FDB s1a khong co MAC h3/h4 | PASS | Bridge VNI 100 mu voi Tenant B |
| FDB s1b khong co MAC h1/h2 | PASS | Bridge VNI 200 mu voi Tenant A |
| 2 VNI dung chung VTEP IP | OK | OVS phan biet bang VNI key |
| 4 host dung chung underlay | OK | Underlay L3 chia se hieu qua |

### So sanh voi VLAN truyen thong

| Dac diem | VLAN | VXLAN Multi-VNI |
|---------|------|----------------|
| So luong segment toi da | 4,096 | 16,777,216 |
| Pham vi | Layer 2 domain | Vuot qua L3 boundary |
| Overhead | 4 bytes | 50 bytes (IP+UDP+VXLAN) |
| Underlay chia se | Co | Co |
| MAC isolation | Co | Co |
| IP overlap giua tenant | Khong | Co ✓ |

---

## 8. Ket Luan

Module 5 hoan thanh thanh cong. Da chung minh duoc:

- **Multi-tenant isolation**: 2 tenant doc lap tren cung ha tang underlay
- **VNI phan biet traffic**: OVS dung (local_ip + remote_ip + key) de dinh tuyen chinh xac
- **Same-IP overlap**: Tenant A va Tenant B cung dung `10.0.0.x/24` nhung hoan toan cach ly
- **Bang chung ARP**: Cung tra cuu `10.0.0.2` nhung nhan MAC khac nhau — isolation ro rang

**Day la core value cua VXLAN trong datacenter**: Cho phep nhieu tenant cung tru tren cung ha tang vat ly ma khong anh huong lan nhau.

---

*Ngay thuc hien: 30/03/2026*
