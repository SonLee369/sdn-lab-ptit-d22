# Lab VXLAN — Tong Ket Du An

> **Muc tieu**: Nghien cuu va trien khai VXLAN (Virtual eXtensible LAN) tren Mininet + Open vSwitch,
> tu nen tang underlay L3 den multi-tenant isolation.

---

## Moi Truong

| Thanh phan | Phien ban |
|-----------|---------|
| Mininet | 2.x |
| Open vSwitch (OVS) | 3.3.4 |
| He dieu hanh | Ubuntu |
| Python | 3.x |

---

## Cau Truc Thu Muc

```
lab2-vxlan/
├── README.md                    <- Tong ket du an (file nay)
├── scripts/
│   ├── module2_underlay.py      <- Topo underlay L3
│   ├── module3_vxlan.py         <- VXLAN tunnel setup
│   ├── module4_verify.py        <- L2 overlay verification
│   └── module5_multivni.py      <- Multi-VNI isolation
├── reports/
│   ├── report_module2.md        <- Bao cao Module 2
│   ├── report_module3.md        <- Bao cao Module 3
│   ├── report_module4.md        <- Bao cao Module 4
│   └── report_module5.md        <- Bao cao Module 5
└── results/
    ├── module2-results.md
    ├── module3-results.md
    ├── module4-results-03.md    <- Ket qua sau khi fix
    └── module5-results.md
```

---

## Tong Quan VXLAN

**VXLAN (Virtual eXtensible LAN)** la giao thuc overlay cho phep tao mang L2 ao tren nen tang L3:

```
 Host A                                          Host B
   |                                               |
[VTEP 1] --- Underlay IP Network (L3) --- [VTEP 2]
   |                                               |
   +------------ VXLAN Tunnel (L2 overlay) --------+

Dong goi:
┌──────────┬─────┬────────┬──────────────────────┐
│ Outer IP │ UDP │ VXLAN  │  Inner Ethernet Frame │
│ src:VTEP1│4789 │VNI=100 │  (payload goc)        │
│ dst:VTEP2│     │        │                       │
└──────────┴─────┴────────┴──────────────────────┘
```

| Dac diem | Gia tri |
|---------|--------|
| VNI (tenant ID) | 24-bit, toi da 16,777,216 VNI |
| UDP port | 4789 (chuan IANA) |
| Overhead | 50 bytes / goi (Outer ETH+IP+UDP+VXLAN) |
| Underlay | L3 (IP routing) |
| Overlay | L2 (Ethernet) |

---

## Cac Module Da Thuc Hien

### Module 2 — Underlay L3 Network

**Muc tieu**: Xay dung nen tang L3 giua 2 VTEP truoc khi trien khai VXLAN.

```
  h1 (10.0.0.1/24)              h2 (10.0.0.2/24)
        |                              |
      [s1]                           [s2]
  VTEP: 192.168.1.1/30 -------- VTEP: 192.168.1.2/30
```

**Ket qua**: 2 VTEP ping duoc nhau, 0% packet loss, RTT ~0.24 ms.

**Script**: `scripts/module2_underlay.py` | **Bao cao**: `reports/report_module2.md`

---

### Module 3 — VXLAN Tunnel Setup

**Muc tieu**: Tao VXLAN tunnel (VNI=100) giua 2 OVS switch.

```
  [s1] <====== VXLAN VNI 100, UDP 4789 ======> [s2]
  vxlan1: remote=192.168.1.2, key=100         vxlan2: remote=192.168.1.1, key=100
```

**Ket qua**: Ca 2 VXLAN port `admin_state=up`, `link_state=up`, co traffic thuc su.

**Luu y quan trong**: Ten port phai unique trong toan bo OVS instance (`vxlan1` cho s1, `vxlan2` cho s2).

**Script**: `scripts/module3_vxlan.py` | **Bao cao**: `reports/report_module3.md`

---

### Module 4 — L2 Overlay Verification

**Muc tieu**: Xac nhan h1 ↔ h2 thong qua VXLAN tunnel; phan tich ARP, ping, MAC learning.

```
  h1 (10.0.0.1) ---[s1]=====VXLAN VNI 100=====[s2]--- h2 (10.0.0.2)
```

**Ket qua**:

| Test | Ket qua |
|------|--------|
| h1 → h2 ping | PASS, 0% loss, avg 0.326 ms |
| h2 → h1 ping | PASS, 0% loss, avg 0.528 ms |
| ARP resolved | h1 biet MAC h2: `00:00:00:00:00:02` |
| MAC learning | h2 MAC tren vxlan port (port 3), h1 MAC tren local port (port 1) |

**Qua trinh debug — 3 bug da giai quyet**:

| Bug | Trieu chung | Nguyen nhan | Fix |
|-----|------------|------------|-----|
| 1 | Broadcast storm, 13,680 pkts dropped | `s1-eth2`/`s2-eth2` trong bridge tao L2 loop | `ovs-vsctl del-port s1 s1-eth2` |
| 2 | 0 VXLAN packet, ARP incomplete | VTEP IP dat sai interface (`dev s1-eth2`) | Chuyen sang `dev s1` (bridge interface) |
| 3 | ARP van incomplete | Thieu `options:local_ip` → OVS chon sai source IP | Them `options:local_ip=192.168.1.1` |

**Script**: `scripts/module4_verify.py` | **Bao cao**: `reports/report_module4.md`

---

### Module 5 — Multi-VNI / Tenant Isolation

**Muc tieu**: Chung minh 2 tenant doc lap tren cung underlay, ke ca khi dung trung IP.

```
  ╔══ Tenant A — VNI 100 ══╗       ╔══ Tenant B — VNI 200 ══╗
  ║ h1(10.0.0.1) h2(10.0.0.2)║     ║ h3(10.0.0.1) h4(10.0.0.2)║
  ║    [s1a]══VNI100══[s2a]  ║     ║    [s1b]══VNI200══[s2b]  ║
  ╚════════════════════════╝       ╚════════════════════════╝
         VTEP: 192.168.1.1              VTEP: 192.168.1.2
                    (chung underlay)
```

**Ket qua**:

| Test | Ket qua |
|------|--------|
| h1 → h2 (VNI 100) | PASS, 0% loss |
| h3 → h4 (VNI 200) | PASS, 0% loss |
| h1 ARP `10.0.0.2` | `00:00:00:00:01:02` (MAC h2) |
| h3 ARP `10.0.0.2` | `00:00:00:00:02:02` (MAC h4) |

**Bang chung isolation**: Cung tra cuu IP `10.0.0.2` nhung h1 va h3 nhan **2 MAC khac nhau** — 2 tenant hoan toan bi cach ly du dung chung underlay va cung subnet.

**Script**: `scripts/module5_multivni.py` | **Bao cao**: `reports/report_module5.md`

---

## Bai Hoc Ky Thuat Quan Trong

### 1. Mininet Same-Namespace — VXLAN Local Delivery

Trong Mininet, tat ca OVS bridge chay trong **root network namespace**. VTEP IP cua `s1` va `s2` deu la *local address* cua cung may. Do do, VXLAN traffic di qua **local delivery** (khong qua interface vat ly).

```
Thuc te (2 may):          Mininet (cung namespace):
  s1-eth2 --[wire]--> s2-eth2    192.168.1.2 la LOCAL address
  tcpdump thay VXLAN ✓           tcpdump -i s1-eth2 thay 0 goi
                                 tcpdump -i any thay goi ✓
```

**Chuc nang overlay van giong hoan toan** — chi khac cach goi tin di trong kernel.

### 2. options:local_ip la bat buoc

Khi khong co `local_ip`, OVS hoi kernel "source IP nao de den 192.168.1.2?" Kernel tra loi `192.168.1.2` (la local) → VXLAN gui `src=dst=192.168.1.2` → tunnel phia kia tu choi.

```bash
# SAI (thieu local_ip)
ovs-vsctl add-port s1 vxlan1 -- set interface vxlan1 \
  type=vxlan options:remote_ip=192.168.1.2 options:key=100

# DUNG
ovs-vsctl add-port s1 vxlan1 -- set interface vxlan1 \
  type=vxlan \
  options:local_ip=192.168.1.1 \     <- bat buoc trong Mininet
  options:remote_ip=192.168.1.2 \
  options:key=100
```

### 3. Underlay Port Phai Tach Khoi Bridge

Neu port underlay (`s1-eth2`) nam trong OVS bridge, VXLAN packet bi flood qua ca physical port lan tunnel port → tao L2 switching loop → broadcast storm.

```bash
# Giai phap: xoa underlay port khoi bridge
ovs-vsctl del-port s1 s1-eth2
```

### 4. Ten Port Phai Unique Trong Toan Bo OVS Instance

Ca `s1` va `s2` dung chung mot `ovsdb`. Neu dat 2 port cung ten (vi du `vxlan1`) tren 2 bridge khac nhau → conflict.

```
SAI:  s1 co vxlan1, s2 cung co vxlan1  → loi!
DUNG: s1 co vxlan1, s2 co vxlan2       → ok
```

---

## Huong Dan Chay Lai

```bash
# Don dep truoc khi chay bat ky module nao
sudo mn -c

# Module 2 — Underlay
sudo python3 scripts/module2_underlay.py

# Module 3 — VXLAN Tunnel
sudo python3 scripts/module3_vxlan.py

# Module 4 — L2 Overlay (bao gom Module 2+3)
sudo python3 scripts/module4_verify.py

# Module 5 — Multi-VNI
sudo python3 scripts/module5_multivni.py
```

---

## Trang Thai Du An

| Module | Ten | Trang thai |
|--------|-----|-----------|
| 2 | Underlay L3 Network | Done |
| 3 | VXLAN Tunnel Setup | Done |
| 4 | L2 Overlay Verification | Done |
| 5 | Multi-VNI / Tenant Isolation | Done |
| 6 | *(planned)* Static FDB / EVPN concept | Chua bat dau |

---

*Ngay cap nhat: 30/03/2026*
